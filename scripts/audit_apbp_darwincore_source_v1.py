#!/usr/bin/env python3
"""Audit official 2023 Antarctic Penguin Biogeography Project DwC-A v2.3.

Structural counts + measurement coverage ONLY: no ecological effect models,
no outcomes, no island geometry classification and no inferred species absences.
The complete original downloaded data are not written into GitHub results.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import PurePosixPath,Path
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import zipfile

import requests

SOURCE_URL = "https://ipt.biodiversity.aq/archive.do?r=mapppd_count_data&v=2.3"
SOURCE_DOI = "10.48361/zftxkr"
EXPECTED_ROW_COUNTS = {
    "Event": 4055, "Occurrence": 4768, "ExtendedMeasurementOrFact": 4750
}
MAX_DOWNLOAD = 15_000_000
MAX_UNCOMPRESSED = 50_000_000
TAXON_CANONICAL = {
    "Pygoscelis adeliae": "Pygoscelis adeliae",
    "Pygoscelis antarctica": "Pygoscelis antarcticus",  # documented source synonym
    "Pygoscelis antarcticus": "Pygoscelis antarcticus",
    "Pygoscelis papua": "Pygoscelis papua",
    "Eudyptes chrysolophus": "Eudyptes chrysolophus",
    "Aptenodytes patagonicus": "Aptenodytes patagonicus",
    "Aptenodytes forsteri": "Aptenodytes forsteri",
}
TAXA = set(TAXON_CANONICAL.values())
DWC_URI = "http://rs.tdwg.org/dwc/terms/"


def safe_zip(raw: bytes):
    if not raw.startswith(b"PK"):
        raise ValueError("SOURCE_STOP official download is not ZIP")
    if len(raw)>MAX_DOWNLOAD:
        raise ValueError("SOURCE_STOP ZIP exceeds bounded original source size")
    z=zipfile.ZipFile(io.BytesIO(raw))
    if len(z.namelist())>60 or z.testzip() is not None:
        raise ValueError("SOURCE_STOP invalid ZIP or too many members")
    total=0
    for member in z.infolist():
        p=PurePosixPath(member.filename)
        if p.is_absolute() or ".." in p.parts or member.filename.startswith("\\"):
            raise ValueError("SOURCE_STOP unsafe ZIP member path")
        total+=member.file_size
        if total>MAX_UNCOMPRESSED:
            raise ValueError("SOURCE_STOP decompressed data exceeds bound")
    if "meta.xml" not in z.namelist():
        raise ValueError("SCHEMA_STOP DwC-A lacks meta.xml")
    return z


def _decode_sep(value,default="\t"):
    if value is None:
        return default
    return (value.replace(r"\t","\t").replace(r"\n","\n")
            .replace(r"\r","\r").replace(r'\"','"'))


def _field_name(term):
    return term.split("#")[-1].rsplit("/",1)[-1]


def _sheet_metadata(root,element):
    tag=element.tag.split("}")[-1]
    if tag not in {"core","extension"}:
        raise ValueError("SCHEMA_STOP XML table must be core or extension")
    table_file=element.find("{*}files/{*}location")
    if table_file is None or not table_file.text:
        raise ValueError("SCHEMA_STOP metadata lacks table file location")
    path=table_file.text.strip()
    return {
        "kind":tag,
        "rowtype":_field_name(element.attrib.get("rowType","UNKNOWN")),
        "path":path,
        "separator":_decode_sep(element.attrib.get("fieldsTerminatedBy"),"\t"),
        "enclosure":_decode_sep(element.attrib.get("fieldsEnclosedBy"),""),
        "ignore_header_lines":int(element.attrib.get("ignoreHeaderLines","0")),
        "encoding":element.attrib.get("encoding","UTF-8"),
        "id_idx":next((int(node.attrib["index"]) for node in element.findall("{*}id")),None),
        "coreid_idx":next((int(node.attrib["index"]) for node in element.findall("{*}coreid")),None),
        "fields": {
            int(node.attrib["index"]):_field_name(node.attrib.get("term",""))
            for node in element.findall("{*}field")
        },
    }


def metadata(z):
    root=ET.fromstring(z.read("meta.xml"))
    core=root.find("{*}core")
    if core is None:
        raise ValueError("SCHEMA_STOP missing Event core")
    tables=[_sheet_metadata(root,core)]+[
        _sheet_metadata(root,x) for x in root.findall("{*}extension")]
    names=[t["rowtype"] for t in tables]
    if names.count("Event")!=1 or names.count("Occurrence")!=1 or names.count("ExtendedMeasurementOrFact")!=1:
        raise ValueError("SCHEMA_STOP expects Event/Occurrence/eMoF links")
    if tables[0]["id_idx"] is None or any(t["coreid_idx"] is None for t in tables[1:]):
        raise ValueError("SCHEMA_STOP missing DwC core ID linking keys")
    if any(not t["fields"] or max(t["fields"])>150 or t["ignore_header_lines"]>3 for t in tables):
        raise ValueError("SCHEMA_STOP implausible field schema")
    return tables


def rows_for(z,table):
    name=table["path"]
    if name not in z.namelist():
        raise ValueError("SCHEMA_STOP declared file absent: "+name)
    raw=z.read(name)
    try:
        stream=io.StringIO(raw.decode(table["encoding"].replace("UTF8","UTF-8")))
    except (UnicodeError,LookupError) as exc:
        raise ValueError("SCHEMA_STOP cannot decode publisher table: "+name) from exc
    delimiter=table["separator"]
    if len(delimiter)!=1:
        raise ValueError("SCHEMA_STOP unsupported delimiter")
    if table["enclosure"] and len(table["enclosure"])!=1:
        raise ValueError("SCHEMA_STOP unsupported quote char")
    reader=csv.reader(stream,delimiter=delimiter,
                      quotechar=table["enclosure"] or '"',
                      quoting=csv.QUOTE_MINIMAL if table["enclosure"] else csv.QUOTE_NONE)
    for _ in range(table["ignore_header_lines"]):
        next(reader,None)
    expected=max([*table["fields"].keys(),
                  *(x for x in (table["id_idx"],table["coreid_idx"]) if x is not None)])+1
    for index,parts in enumerate(reader,1):
        if not parts or not any(p.strip() for p in parts):
            continue
        if len(parts)<expected:
            raise ValueError("SCHEMA_STOP row lacks declared columns in "+name)
        values={value_name:parts[ix] for ix,value_name in table["fields"].items()}
        objid=parts[table["id_idx"]] if table["id_idx"] is not None else None
        coreid=parts[table["coreid_idx"]] if table["coreid_idx"] is not None else None
        yield objid,coreid,values


def event_year(text):
    m=re.match(r"^(18\d{2}|19\d{2}|20\d{2})(?:-|$)",str(text or "").strip())
    return int(m.group(1)) if m else None


def audited_schema(raw,expected_counts=EXPECTED_ROW_COUNTS):
    with safe_zip(raw) as z:
        tables=metadata(z)
        records={}
        event_map={}
        event_keys=set()
        duplicate_events=0
        source_rows={}
        for table in tables:
            result=list(rows_for(z,table))
            kind=table["rowtype"]
            records[kind]=result
            source_rows[kind]={
                "rows":len(result),
                "column_names":sorted(set(table["fields"].values())),
                "raw_publisher_file":table["path"],
                "row_type":kind,
                "declared_original_fields":len(table["fields"]),
            }
            if kind=="Event":
                for key,ref,values in result:
                    if key in event_map:
                        duplicate_events+=1
                    else:
                        event_map[key]=values
                    if key: event_keys.add(key)
        if not event_keys or duplicate_events:
            raise ValueError("SOURCE_STOP duplicate or missing original DwC Event primary keys")
        if any(len(records[k])!=v for k,v in expected_counts.items()):
            raise ValueError("SOURCE_VERSION_STOP pinned v2.3 publisher row counts changed: "+
                             str({k:len(records[k]) for k in expected_counts}))
        orphan={}
        for kind in ("Occurrence","ExtendedMeasurementOrFact"):
            orphan[kind]=sum(1 for _,key,values in records[kind] if key not in event_keys)
        if any(orphan.values()):
            raise ValueError("SCHEMA_STOP occurrence/eMoF foreign event keys unlinked")

        event_years=Counter()
        distinct_sites=set()
        sites_by_year=defaultdict(set)
        methods=Counter()
        for _,_,record in records["Event"]:
            site=record.get("locationID","").strip() or record.get("locality","").strip()
            year=event_year(record.get("eventDate") or record.get("year"))
            if year:
                event_years[year]+=1
                if site:
                    sites_by_year[site].add(year)
            if site: distinct_sites.add(site)
            method=record.get("samplingProtocol","").strip()
            if method:
                methods[method[:80]]+=1

        counts_per_species=Counter()
        species_labels=Counter()
        occ_fields={}
        for _,key,obj in records["Occurrence"]:
            s=obj.get("scientificName","").strip() or obj.get("acceptedNameUsage","").strip()
            species_labels[s or "UNKNOWN"]+=1
            if s in TAXON_CANONICAL:
                counts_per_species[TAXON_CANONICAL[s]]+=1
        measures=Counter()
        measure_units=Counter()
        emof=obj if False else None
        for _,key,obj in records["ExtendedMeasurementOrFact"]:
            kind=obj.get("measurementType","").strip()
            measures[kind or "UNKNOWN"]+=1
            measure_units[(kind or "UNKNOWN",obj.get("measurementUnit","").strip())]+=1

        result={
            "status":"SOURCE_LOCKED_SCHEMA_ONLY_NO_ECOLOGICAL_EFFECT",
            "source":{"publisher":"SCAR - AntOBIS",
                      "dataset":"Antarctic Penguin Biogeography Project",
                      "version":"2.3",
                      "doi":SOURCE_DOI,
                      "url":SOURCE_URL,
                      "license":"CC BY 4.0",
                      "source_zip_sha256":hashlib.sha256(raw).hexdigest(),
                      "source_zip_bytes":len(raw),
                      "zip_members":z.namelist()},
            "tables":source_rows,
            "linkage":{"event_primary_key_count":len(event_keys),
                       "duplicate_event_primary_keys":duplicate_events,
                       "unmatched_extension_event_keys":orphan},
            "coverage_metadata":{
                "distinct_original_site_identifiers":len(distinct_sites),
                "original_events_with_parsed_year":sum(event_years.values()),
                "year_min":min(event_years) if event_years else None,
                "year_max":max(event_years) if event_years else None,
                "surveyed_site_ids_with_at_least_2_distinct_years":
                    sum(len(y)>=2 for y in sites_by_year.values()),
                "surveyed_site_ids_with_at_least_5_distinct_years":
                    sum(len(y)>=5 for y in sites_by_year.values()),
                "occurrence_rows_by_exact_species_label":dict(sorted(species_labels.items())),
                "known_six_species_occurrence_rows":dict(sorted(counts_per_species.items())),
                "original_measurement_type_counts":dict(measures.most_common(40)),
                "top_survey_protocol_counts":dict(methods.most_common(12)),
            },
            "no_nest_count_unit_assumed":True,
            "no_site_equals_island_assumption":True,
            "no_missing_year_as_zero":True,
            "eco_models_fitted":0,
            "marine_or_island_environment_joined":False,
            "interpretation":"Stage 1 official schema/observation coverage only; no population trend, island effect or species × environment inference."
        }
        return result


def fetch_original():
    with requests.get(SOURCE_URL,timeout=(20,75),stream=True,
                      headers={"User-Agent":"mina-ant-island-macro-source-audit/1.0"}) as r:
        r.raise_for_status()
        final=urlparse(r.url)
        if final.scheme!="https" or final.hostname!="ipt.biodiversity.aq":
            raise ValueError("SOURCE_STOP unexpected publisher redirect")
        raw=bytearray()
        for part in r.iter_content(chunk_size=65536):
            raw.extend(part)
            if len(raw)>MAX_DOWNLOAD:
                raise ValueError("SOURCE_STOP exceeded original download cap")
        return bytes(raw)


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",required=True)
    args=a.parse_args()
    try:
        result=audited_schema(fetch_original())
    except Exception as exc:
        result={"status":"HOLD_SOURCE_OR_MEASUREMENT","source_doi":SOURCE_DOI,
                "error_type":type(exc).__name__,
                "error":str(exc)[:380],
                "eco_models_fitted":0}
    dest=Path(args.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
