#!/usr/bin/env python3
"""V30 original OBIS/GBIF-IPT historical Antarctic penguin census DwC-A audit.

First-party exact 2018 public archive (2787 published records). No trained
island / habitat ecology model and NO inference of absence from missing rows.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import PurePosixPath,Path
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import zipfile

import requests

ORIGINAL_ARCHIVE="https://ipt.obis.org/nonode/archive.do?r=iasb&v=1.0"
ORIGINAL_RESOURCE="https://ipt.obis.org/nonode/resource?r=iasb"
LIMIT_BYTES=2_000_000
LIMIT_UNCOMPRESSED=15_000_000
MAX_ORIGINAL_ROWS=200_000
EXPECTED_ORIGINAL_OCCURRENCE_RECORDS=2787
IMPORTANT_FIELDS=(
    "occurrenceID","eventID","scientificName","species","locality",
    "decimalLatitude","decimalLongitude","coordinateUncertaintyInMeters",
    "eventDate","year","individualCount","organismQuantity",
    "organismQuantityType","occurrenceStatus","recordedBy","basisOfRecord",
    "associatedReferences","bibliographicCitation","verbatimLocality",
    "dynamicProperties","measurementType","measurementValue"
)


def source_zip_from_publisher(session):
    with session.get(ORIGINAL_ARCHIVE,timeout=(20,110),stream=True,headers={
        "User-Agent":"mina-original-penguin-island-historic-IPT-source-v30/1.0"}) as response:
        response.raise_for_status()
        loc=urlparse(response.url)
        if loc.scheme!="https" or loc.hostname!="ipt.obis.org":
            raise ValueError("SOURCE_STOP first-party archive redirected outside IPT")
        chunks=bytearray()
        for buf in response.iter_content(chunk_size=16384):
            chunks.extend(buf)
            if len(chunks)>LIMIT_BYTES:
                raise ValueError("SOURCE_STOP original IPT archived DWCA exceeds max 2 MiB")
    raw=bytes(chunks)
    if not raw.startswith(b"PK\x03\x04"):
        raise ValueError("SOURCE_STOP original Antarctic penguin archive not a ZIP")
    return raw


def safe_archive_files(raw:bytes):
    source_hash=hashlib.sha256(raw).hexdigest()
    with zipfile.ZipFile(io.BytesIO(raw)) as f:
        entries=f.infolist()
        if not entries or len(entries)>100:
            raise ValueError("SOURCE_STOP original IPT archive file count unexpected")
        if sum(x.file_size for x in entries)>LIMIT_UNCOMPRESSED:
            raise ValueError("SOURCE_STOP IPT archive uncompressed payload above 15 MiB")
        if f.testzip() is not None:
            raise ValueError("SOURCE_STOP first-party original archive CRC mismatch")
        files={}
        for entry in entries:
            parts=PurePosixPath(entry.filename)
            if parts.is_absolute() or ".." in parts.parts or len(parts.parts)>5:
                raise ValueError("SOURCE_STOP original archive unsafe path")
            if entry.is_dir():continue
            if entry.filename in files:
                raise ValueError("SOURCE_STOP duplicated original archive member")
            files[entry.filename]=f.read(entry)
    if not any(x.lower()=="meta.xml" or x.lower().endswith("/meta.xml") for x in files):
        raise ValueError("SOURCE_STOP original DwC-A does not contain meta.xml")
    return files,source_hash


def local_tag(node):
    return node.tag.rsplit("}",1)[-1]


def xml_child(parent,name):
    for x in parent:
        if local_tag(x)==name:return x
    return None


def original_dwc_core(files):
    metas=[(name,blob) for name,blob in files.items() if name.lower().endswith("meta.xml")]
    if len(metas)!=1:
        raise ValueError("SOURCE_STOP original archive contains ambiguous meta XML")
    try:
        root=ET.fromstring(metas[0][1])
    except ET.ParseError as exc:
        raise ValueError("SCHEMA_STOP original DwC XML invalid") from exc
    core=xml_child(root,"core")
    if core is None:
        raise ValueError("SCHEMA_STOP IPT Darwin Core Archive has no original occurrence core")
    rowtype=str(core.get("rowType",""))
    if "Occurrence" not in rowtype and "Event" not in rowtype:
        raise ValueError("SCHEMA_STOP unexpected source DwC-A core data type: "+rowtype)
    container=xml_child(core,"files")
    if container is None:
        raise ValueError("SCHEMA_STOP original DwC core file descriptor missing")
    locations=[x.text.strip() for x in container if local_tag(x)=="location" and x.text]
    if len(locations)!=1:
        raise ValueError("SCHEMA_STOP original IPT core location ambiguous")
    loc=locations[0]
    if loc not in files:
        raise ValueError("SOURCE_STOP occurrence core not in source archive ZIP")
    id_field=xml_child(core,"id")
    fields={}
    for node in core:
        if local_tag(node)!="field":continue
        idx=node.get("index")
        term=node.get("term","").rsplit("/",1)[-1]
        if idx is None or not str(idx).isdecimal() or not term:
            raise ValueError("SCHEMA_STOP original DwC occurrence field missing term/index")
        if int(idx) in fields:
            raise ValueError("SCHEMA_STOP duplicate field index in original IPT")
        fields[int(idx)]=term
    if not fields:
        raise ValueError("SCHEMA_STOP original IPT core lacks fields")
    rawsep=core.get("fieldsTerminatedBy",r"\t")
    rawquote=core.get("fieldsEnclosedBy","")
    sep=rawsep.replace(r"\t","\t").replace(r"\n","\n")
    quote=rawquote.replace(r"\"","\"")
    if len(sep)!=1:
        raise ValueError("SCHEMA_STOP original DwC primary delimiter unexpected")
    if quote not in ("","\"","'"):
        raise ValueError("SCHEMA_STOP original DwC quote char unexpected")
    header_n=int(core.get("ignoreHeaderLines","0"))
    if header_n not in (0,1):
        raise ValueError("SCHEMA_STOP original IPT header rows not in {0,1}")
    source=files[loc]
    try:
        text=source.decode(core.get("encoding","utf-8-sig"))
    except (UnicodeError,LookupError) as e:
        raise ValueError("SOURCE_STOP original DwC source encoding invalid") from e
    reader=csv.reader(io.StringIO(text,newline=""),
                      delimiter=sep,quotechar=quote if quote else "\"",
                      quoting=csv.QUOTE_MINIMAL if quote else csv.QUOTE_NONE)
    for i in range(header_n):
        next(reader,None)
    actual=[]
    all_columns=max(fields)+1
    for i,row in enumerate(reader,1):
        if not any(row):continue
        if len(row)<all_columns:
            raise ValueError("SCHEMA_STOP original IPT occurrence core has short row "+str(i))
        if i>MAX_ORIGINAL_ROWS:
            raise ValueError("SOURCE_STOP original source unexpectedly >200000 core rows")
        actual.append({name:row[idx].strip() for idx,name in sorted(fields.items())})
    receipt={
        "source_original_core_member_path":loc,
        "source_original_core_member_SHA256":hashlib.sha256(source).hexdigest(),
        "source_original_meta_xml_SHA256":hashlib.sha256(metas[0][1]).hexdigest(),
        "source_original_DwC_rowType":rowtype,
        "source_original_DwC_term_name_indices":fields,
        "source_original_core_delimiter":repr(sep),
        "source_original_core_headerlines":header_n,
        "source_original_core_record_n":len(actual),
        "source_original_archive_member_SHA256":{
            k:hashlib.sha256(v).hexdigest() for k,v in sorted(files.items())
        },
    }
    return actual,receipt


def describe_original_census(rows:list):
    if not rows:
        raise ValueError("SAMPLE_STOP original penguin source DwC occurrence file empty")
    columns=set(rows[0])
    field_receipts={}
    for name in IMPORTANT_FIELDS:
        if name not in columns:continue
        values=[x.get(name,"") for x in rows]
        nonblank=[v for v in values if v]
        field_receipts[name]={
            "original_nonempty_row_n":len(nonblank),
            "unique_distinct_values":len(set(nonblank)),
            "source_first_n_literal_examples":list(dict.fromkeys(nonblank))[:8],
        }
    species=Counter(x.get("scientificName") or x.get("species") or "UNSPECIFIED"
                    for x in rows)
    sourceyears=Counter()
    for x in rows:
        year=x.get("year","").strip()
        if not year:
            m=re.search(r"\b(1[89]\d{2}|20\d{2})\b",x.get("eventDate",""))
            year=m.group(1) if m else ""
        if year and re.fullmatch(r"\d{4}",year):
            sourceyears[year]+=1
        else:
            sourceyears["MISSING_OR_INVALID_YEAR"]+=1
    numeric_fields={}
    for name in ("individualCount","organismQuantity"):
        if name not in columns:continue
        v=[x.get(name,"") for x in rows]
        n=[]
        for a in v:
            if not a:continue
            try:
                value=float(a)
                if math.isfinite(value) and value>=0:n.append(value)
            except ValueError:pass
        numeric_fields[name]={
            "original_rows_with_finite_nonnegative_numeric_value":len(n),
            "original_numeric_nonzero_count":sum(z>0 for z in n),
            "source_numeric_value_min":min(n) if n else None,
            "source_numeric_value_max":max(n) if n else None,
            "record_quantity_is_valid_independently_surveyed_nests":False
        }
    latn=0
    lat_problem=0
    for r in rows:
        try:
            lat=float(r.get("decimalLatitude",""))
            lon=float(r.get("decimalLongitude",""))
            if math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180:
                latn+=1
                if lat>0:lat_problem+=1
        except ValueError:pass
    originalids=[r.get("occurrenceID","") for r in rows if r.get("occurrenceID","")]
    id_dups=len(originalids)-len(set(originalids))
    return {
        "status":"IPT_OBIS_ANTARCTIC_HISTORICAL_PENGUIN_ORIGINAL_CORE_V30",
        "original_dwca_occurrence_core_rows":len(rows),
        "published_resource_expected_original_occurrence_rows":EXPECTED_ORIGINAL_OCCURRENCE_RECORDS,
        "source_core_matches_expected_reported_2018_row_number":len(rows)==EXPECTED_ORIGINAL_OCCURRENCE_RECORDS,
        "source_taxon_literal_counts":dict(sorted(species.items())),
        "original_source_year_literal_counts":dict(sorted(sourceyears.items())),
        "source_original_field_eligibility_and_examples":field_receipts,
        "source_quantity_field_observational_numeric_support":numeric_fields,
        "valid_lat_lon_number":latn,
        "valid_numeric_but_northern_latitude_row_n":lat_problem,
        "source_nonempty_occurrence_identifier_n":len(originalids),
        "source_duplicate_occurrenceID_n":id_dups,
        "source_coordinate_or_locality_is_original_field_nest_GPS":False,
        "original_1900_1996_penguin_census_is_independent_of_2026_MAPPPD":False,
        "original_uncited_occurrence_as_verified_surveyed_absence":False,
        "original_field_unvisited_site_recoded_to_zero":False,
        "new_species_island_biological_effects_fitted":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report={"status":"HOLD_ORIGINAL_IPT_PENGUIN_SOURCE_V30","new_ecological_effect_fitted":False}
    try:
        with requests.Session() as s:
            raw=source_zip_from_publisher(s)
        files,hashval=safe_archive_files(raw)
        rows,source=original_dwc_core(files)
        report=describe_original_census(rows)
        report["original_source_publisher_url"]=ORIGINAL_ARCHIVE
        report["source_original_archive_zipped_SHA256"]=hashval
        report["source_original_archive_bytes"]=len(raw)
        report["original_source_core_manifest_receipt"]=source
        report["original_historical_geographic_census_may_contain_gazetteer_coordinates"]=True
    except Exception as e:
        report["error_type"]=type(e).__name__
        report["error"]=str(e)[:1500]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # Print schema-only short digest to GitHub workflow stdout.
    out={
        "status":report["status"],
        "source_archive_SHA256":report.get("source_original_archive_zipped_SHA256"),
        "core_fields":report.get("original_source_core_manifest_receipt",{}).get(
            "source_original_DwC_term_name_indices"),
        "source_record_count":report.get("original_dwca_occurrence_core_rows"),
        "quantity_observational_support":report.get("source_quantity_field_observational_numeric_support"),
        "species":report.get("source_taxon_literal_counts"),
        "year_min_max":(
            min(report.get("original_source_year_literal_counts",{}),default=None),
            max(report.get("original_source_year_literal_counts",{}),default=None)),
        "error_type":report.get("error_type"),
        "error":report.get("error"),
    }
    print(json.dumps(out,ensure_ascii=False))
    if report["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
