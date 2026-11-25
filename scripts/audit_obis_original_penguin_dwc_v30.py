#!/usr/bin/env python3
"""Original published IPT/OBIS 1900–1996 penguin colony DwC-A source audit V30.

Read original publisher version 1.0 ZIP, verify bounded ZIP and Darwin Core
meta.xml, and inspect original occurrence schema/grain/lineage. No ecological
model or inferred absence is fitted. Same underlying source may enter MAPPPD.
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

SOURCE_URL="https://ipt.obis.org/nonode/archive.do?r=iasb&v=1.0"
SOURCE_PAGE="https://ipt.obis.org/nonode/resource?r=iasb"
MAX_SOURCE_ZIP_BYTES=2_000_000
MAX_SOURCE_UNCOMPRESSED_BYTES=15_000_000
EXPECTED_PUBLISHER_OCCURRENCES=2787
ALLOWED_HOSTS={"ipt.obis.org","ipt.iobis.org"}
CANON_PREFIX="http://rs.tdwg.org/dwc/terms/"
COUNT_FIELDS=("individualCount","organismQuantity","organismQuantityType","abundance",
              "count","numberOfIndividuals","populationCount","verbatimIndividualCount")
SOURCE_SEMANTIC_FIELDS=(
    "scientificName","taxonID","scientificNameID","vernacularName",
    "eventDate","year","month","day","samplingProtocol",
    "occurrenceID","occurrenceStatus","basisOfRecord",
    "individualCount","organismQuantity","organismQuantityType",
    "locationID","locality","verbatimLocality","island","islandGroup",
    "decimalLatitude","decimalLongitude","coordinateUncertaintyInMeters",
    "georeferenceSources","georeferenceProtocol","georeferencedBy",
    "recordedBy","identifiedBy","references","associatedReferences",
    "datasetName","eventID","fieldNumber"
)


def sha(data:bytes):return hashlib.sha256(data).hexdigest()


def download_source():
    with requests.Session() as session:
        with session.get(SOURCE_URL,timeout=(20,100),stream=True,headers={
            "User-Agent":"mina-antarctic-original-OBIS-FAUNA-PENGUIN-COLONY-audit-v30/1.0"
        },allow_redirects=True) as response:
            for hop in [*response.history,response]:
                u=urlparse(hop.url)
                if u.scheme!="https" or u.hostname not in ALLOWED_HOSTS:
                    raise ValueError("SOURCE_STOP original IPT redirects outside original OBIS publisher")
            response.raise_for_status()
            b=bytearray()
            for part in response.iter_content(chunk_size=16384):
                b.extend(part)
                if len(b)>MAX_SOURCE_ZIP_BYTES:
                    raise ValueError("SOURCE_STOP IPT original archive unexpectedly exceeds 2MiB bound")
    data=bytes(b)
    if not data.startswith(b"PK\x03\x04"):
        raise ValueError("SOURCE_STOP publisher returned HTML/other content, not original ZIP")
    return data


def safe_source_zip(blob:bytes):
    if not blob.startswith(b"PK") or len(blob)>MAX_SOURCE_ZIP_BYTES:
        raise ValueError("SOURCE_STOP original IPT ZIP unexpected")
    z=zipfile.ZipFile(io.BytesIO(blob),"r")
    infos=z.infolist()
    if not 2<=len(infos)<=100 or sum(x.file_size for x in infos)>MAX_SOURCE_UNCOMPRESSED_BYTES:
        raise ValueError("SOURCE_STOP original ZIP expanded size or file list beyond source gate")
    if z.testzip() is not None:
        raise ValueError("SOURCE_STOP original ZIP CRC verification failed")
    names=[]
    for member in infos:
        p=PurePosixPath(member.filename)
        if p.is_absolute() or ".." in p.parts or len(p.parts)>5:
            raise ValueError("SOURCE_STOP original publisher ZIP entry path unsafe")
        names.append(str(p))
    return z,{"original_zip_total_compressed_bytes":len(blob),
              "original_zip_SHA256":sha(blob),
              "publisher_archive_files":sorted(names),
              "original_zip_entry_count":len(names),
              "uncompressed_total_bytes":sum(x.file_size for x in infos)}


def symbol(s):
    if s is None:return ""
    if s in ("\\t","\\r","\\n","\\\"","\\'"):
        return {"\\t":"\t","\\r":"\r","\\n":"\n","\\\"":'"',"\\'":"'"}[s]
    return s


def short_field(term):
    term=str(term or "")
    return term.rsplit("/",1)[-1].rsplit("#",1)[-1] if term else ""


def parse_dwc_core(z):
    names=z.namelist()
    metas=[p for p in names if p.endswith("meta.xml")]
    if len(metas)!=1:
        raise ValueError("SCHEMA_STOP original IPT archive meta.xml missing or ambiguous")
    meta=z.read(metas[0])
    try:root=ET.fromstring(meta)
    except ET.ParseError as exc:raise ValueError("SCHEMA_STOP DwC meta.xml invalid") from exc
    cores=[x for x in root.iter() if x.tag.rsplit("}",1)[-1]=="core"]
    if len(cores)!=1:
        raise ValueError("SCHEMA_STOP IPT DwC requires exactly one occurrence core")
    core=cores[0]
    rowtype=str(core.get("rowType") or "")
    files=[x for x in core.iter() if x.tag.rsplit("}",1)[-1]=="location"]
    if len(files)!=1 or not (files[0].text or "").strip():
        raise ValueError("SCHEMA_STOP original DwC occurrence source file location missing")
    corepath=(files[0].text or "").strip()
    if corepath not in names:
        raise ValueError("SOURCE_STOP original meta.xml core path not in verified ZIP")
    raw=z.read(corepath)
    sep=symbol(core.get("fieldsTerminatedBy","\\t")) or "\t"
    enclosed=symbol(core.get("fieldsEnclosedBy",'"')) or '"'
    if len(sep)!=1 or len(enclosed)!=1:
        raise ValueError("SCHEMA_STOP source meta.xml delimiter or quote not supported")
    skip=int(core.get("ignoreHeaderLines","0"))
    fields={}
    for col in core:
        kind=col.tag.rsplit("}",1)[-1]
        if kind=="field":
            idx=int(col.get("index","-1"))
            name=short_field(col.get("term"))
            if idx<0 or not name or idx in fields:
                raise ValueError("SCHEMA_STOP original DwC occurrence core indices invalid")
            fields[idx]=name
        elif kind=="id":
            idx=int(col.get("index","-1"))
            if idx<0 or idx in fields:raise ValueError("SCHEMA_STOP original DwC ID index invalid")
            fields[idx]="core_id"
    if not fields:raise ValueError("SCHEMA_STOP no Darwin Core fields in source meta.xml")
    used=list(fields.values())
    if len(used)!=len(set(used)):
        raise ValueError("SCHEMA_STOP original DwC fields collide by short name")
    width=max(fields)+1
    with io.StringIO(raw.decode("utf-8-sig"),newline="") as stream:
        rd=csv.reader(stream,delimiter=sep,quotechar=enclosed)
        for _ in range(skip):next(rd,None)
        rows=[]
        for line in rd:
            if not any(x.strip() for x in line):continue
            if len(line)!=width:
                raise ValueError("SCHEMA_STOP original IPT core row width "+
                                 str(len(line))+" != meta.xml "+str(width))
            rows.append({fields.get(i,"unmapped_col_"+str(i)):v.strip()
                         for i,v in enumerate(line)})
    return rows,{
        "source_DwC_meta_XML_SHA256":sha(meta),
        "source_original_DwC_core_path":corepath,
        "source_original_DwC_core_SHA256":sha(raw),
        "source_original_DwC_core_bytes":len(raw),
        "source_DwC_core_row_type":rowtype,
        "source_DwC_index_to_literal_term":dict(sorted(fields.items())),
        "source_DwC_core_ignore_header_lines":skip,
        "source_original_core_column_count":width,
        "source_original_meta_file":metas[0],
        "source_XML_field_delimiter":"TAB" if sep=="\t" else sep,
    }


def field_summary(rows,field):
    x=[str(r.get(field,"") or "").strip() for r in rows]
    nonempty=[s for s in x if s]
    c=Counter(nonempty)
    return {
        "nonempty_original_rows":len(nonempty),
        "original_missing_rows":len(rows)-len(nonempty),
        "distinct_literal_values":len(c),
        "top_original_literal_values":[{"literal":k[:180],"n":v}
                                        for k,v in c.most_common(12)]
    }


def summarize_original_rows(rows,receipt):
    if not rows:raise ValueError("SAMPLE_STOP original source has zero actual records")
    keys=list(rows[0])
    has_count=[k for k in keys if k in COUNT_FIELDS]
    numeric={}
    for key in has_count:
        raw=[str(x.get(key,"") or "") for x in rows]
        values=[]
        invalid=0
        for v in raw:
            if not v:continue
            try:
                n=float(v.replace(",",""))
                if math.isfinite(n) and n>=0:values.append(n)
                else:invalid+=1
            except ValueError:invalid+=1
        numeric[key]={
            "count_nonmissing_numeric_nonnegative":len(values),
            "nonnumeric_or_invalid_rows":invalid,
            "zero_count_original_rows":sum(x==0 for x in values),
            "strictly_positive_original_rows":sum(x>0 for x in values),
            "integer_nonnegative_values":sum(abs(x-round(x))<1e-9 for x in values),
            "median":float(sorted(values)[len(values)//2]) if values else None,
            "max":max(values) if values else None,
        }

    timekey="year" if "year" in keys else "eventDate" if "eventDate" in keys else None
    years=[]
    for r in rows:
        value=str(r.get(timekey,"")) if timekey else ""
        m=re.search(r"(?:18|19|20)\d{2}",value)
        if m:years.append(int(m.group()))
    event_key=next((k for k in ("eventID","occurrenceID","core_id") if k in keys),None)
    site_key=next((k for k in ("locationID","locality","verbatimLocality") if k in keys),None)
    group_names=("scientificName","eventDate","year","individualCount",
                 "organismQuantity","occurrenceStatus","basisOfRecord",
                 "locality","locationID","coordinateUncertaintyInMeters",
                 "references","samplingProtocol")
    allfields={k:field_summary(rows,k) for k in group_names if k in keys}
    valid_geo=invalid_geo=0
    geo_dupes=Counter()
    if "decimalLatitude" in keys and "decimalLongitude" in keys:
        for r in rows:
            try:
                lat=float(r["decimalLatitude"]);lon=float(r["decimalLongitude"])
                if math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=-50 and -180<=lon<=180:
                    valid_geo+=1
                    geo_dupes[(lat,lon)]+=1
                else:invalid_geo+=1
            except (ValueError,TypeError):invalid_geo+=1
    original_ids=[r.get(event_key,"") for r in rows] if event_key else []
    replicated_events=sum(v-1 for v in Counter(original_ids).values() if v>1 and v!="")
    sites_year_species=Counter()
    if site_key and "scientificName" in keys and timekey:
        for r in rows:
            sites_year_species[(
                r.get(site_key,""),r.get(timekey,""),r.get("scientificName",""))]+=1
    repeated_site_species_year=sum(v>1 for v in sites_year_species.values())
    original_all_sources=set()
    for x in rows:
        for k in ("references","associatedReferences","datasetName"):
            value=x.get(k,"")
            if value:original_all_sources.add(str(value)[:400])
    return {
        "status":"OBIS_ORIGINAL_1900_1996_PENGUIN_CORE_SOURCE_AUDIT_V30",
        "original_archive_row_count":len(rows),
        "publisher_expected_original_row_count":EXPECTED_PUBLISHER_OCCURRENCES,
        "row_count_matches_publisher_listing":len(rows)==EXPECTED_PUBLISHER_OCCURRENCES,
        "original_source_DwC_columns":keys,
        "original_source_column_literal_summaries":allfields,
        "original_source_numeric_breeding_or_count_fields":numeric,
        "original_source_year_n":len(years),
        "original_source_year_min":min(years) if years else None,
        "original_source_year_max":max(years) if years else None,
        "original_source_years_by_count":dict(sorted(Counter(years).items())),
        "original_source_event_or_occurrence_id_key":event_key,
        "original_source_duplicate_publisher_nonblank_ID_records":replicated_events,
        "original_source_site_identifier_key":site_key,
        "original_source_distinct_site_year_species_cells":len(sites_year_species),
        "source_site_year_species_cells_with_multiple_original_records":repeated_site_species_year,
        "original_source_decimal_coordinate_rows_valid":valid_geo,
        "original_source_decimal_coordinate_rows_invalid_missing":invalid_geo,
        "original_source_coordinate_pairs_used_by_multiple_rows":sum(v>1 for v in geo_dupes.values()),
        "original_source_citation_reference_distinct_n":len(original_all_sources),
        "original_source_citation_reference_sample":sorted(original_all_sources)[:30],
        "source_presence_record_missingness_is_surveyed_breeding_absence":False,
        "original_source_locality_coordinates_are_verified_nest_GPS":False,
        "original_DwC_published_count_is_field_breeding_pair_count_verified":False,
        "original_2018_IPT_core_is_independent_from_MAPPPD_source_citation":False,
        "new_ecological_island_effect_fitted":False,
        **receipt
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result={"status":"HOLD_ORIGINAL_OBIS_HISTORICAL_ANTARCTIC_SOURCE_V30",
            "new_ecological_island_effect_fitted":False}
    try:
        raw=download_source()
        z,receipt=safe_source_zip(raw)
        with z:
            rows,meta=parse_dwc_core(z)
        result=summarize_original_rows(rows,{**receipt,**meta})
        result["original_publisher_resource_page"]=SOURCE_PAGE
        result["original_publisher_download_url"]=SOURCE_URL
        if not result["row_count_matches_publisher_listing"]:
            result["source_row_count_warning"]="PUBLISHER_LISTING_ROW_COUNT_DIFFERS_FROM_ORIGINAL_VERSION"
    except Exception as e:
        result["error_type"]=type(e).__name__
        result["error"]=str(e)[:1500]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Metadata is small, source records not copied into CI log.
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):raise SystemExit(2)

if __name__=="__main__":
    main()
