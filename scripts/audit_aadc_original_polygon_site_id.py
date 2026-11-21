#!/usr/bin/env python3
"""AADC official geographic SITE polygon source-ID eligibility for 14 observed A/P sites.

Two independently published SHP+DBF archives are inspected:
AADC 2016 coastal ice-free potential habitat site layer and AADC 2025
continental geographic sites. Only schema/ID matches and source CRS/size.
No nest patch, historical rock exposure or ecological effect is inferred.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import quote,urlparse
import requests
import shapefile

URL="https://data.aad.gov.au/eds/api/dataset"
SOURCES={
 "2016_icefree_potential_habitat":{
  "uuid":"3F139A80-800D-46BD-A7C0-D29734DAE090",
  "path":"Potential habitat/shapefile/islands_and_continental_rock_by_subgroup8",
  "expected_shp_bytes":12534616,"expected_dbf_bytes":356443
 },
 "2025_continental_sites":{
  "uuid":"b766a3e4-ae94-40c0-b340-9e544d8f5dc3",
  "path":"1_Continental spatial reference system/data/Continental geographic sites_30E_to_150E",
  "expected_shp_bytes":4470820,"expected_dbf_bytes":1461918
 }
}
FROZEN_EVENTS=16
FROZEN_SITES=14
SOURCE_A_P_RUN=44530909415
MAX_OBJECT=20_000_000
TARGET_ID_LOOKUP_LIMIT=20

def original_get(session,url,max_bytes=MAX_OBJECT):
    if urlparse(url).hostname!="data.aad.gov.au":raise ValueError("nonpublisher requested URL")
    with session.get(url,stream=True,timeout=(20,110)) as resp:
        resp.raise_for_status()
        host=urlparse(resp.url).hostname
        if not host or not (
          host=="data.aad.gov.au" or host.endswith(".data.aad.gov.au")
          or host.endswith(".amazonaws.com")
        ):raise ValueError("unexpected publisher redirect")
        out=bytearray()
        for ch in resp.iter_content(65536):
            out.extend(ch)
            if len(out)>max_bytes:raise ValueError("source file exceeds configured size")
    return bytes(out),hashlib.sha256(out).hexdigest()

def original_file(session,uuid,name):
    url=f"{URL}/{quote(uuid)}/object/download?prefix={quote(name,safe='')}"
    return original_get(session,url)

def original_event_roster(json_path):
    obj=json.loads(json_path.read_text(encoding="utf-8"))
    if obj.get("status")!="AADC_EIGHT_SPECIES_VERIFIED_DETECTION_QUALITY_SOURCE_GATE":
        raise ValueError("not original expert screened event source receipt")
    events=obj["strict_all_expert_Y_and_high_A_certainty_support"]["AP_event_source_rows"]
    ids=sorted({str(e["geog_site_id"]) for e in events})
    if len(events)!=FROZEN_EVENTS or len(ids)!=FROZEN_SITES:
        raise ValueError("source original 16 A-to-P / 14 site roster drift")
    return ids

def scan_polygon_dbf(session,src,targets):
    base=src["path"]
    raw={}
    receipts={}
    for ext in (".shp",".shx",".dbf",".prj"):
        blob,sha=original_file(session,src["uuid"],base+ext)
        if ext==".shp" and len(blob)!=src["expected_shp_bytes"]:
            raise ValueError(f"Original SHP byte-size drift {len(blob)}")
        if ext==".dbf" and len(blob)!=src["expected_dbf_bytes"]:
            raise ValueError(f"Original DBF byte-size drift {len(blob)}")
        raw[ext]=blob
        receipts[ext]={"bytes":len(blob),"sha256":sha}
    prj=raw[".prj"].decode("utf-8",errors="replace")
    reader=shapefile.Reader(shp=io.BytesIO(raw[".shp"]),
                           shx=io.BytesIO(raw[".shx"]),
                           dbf=io.BytesIO(raw[".dbf"]),
                           encoding="latin1")
    try:
        fields=[str(x[0]) for x in reader.fields[1:]]
        names=[x.lower() for x in fields]
        hits=Counter()
        actual_matched={}
        for rec in reader.iterRecords():
            for ix,v in enumerate(rec):
                st=str(v).strip()
                if st in targets:
                    hits[fields[ix]]+=1
                    actual_matched.setdefault(fields[ix],set()).add(st)
        n=reader.numRecords
        geom_type=reader.shapeTypeName
    finally:reader.close()
    if n<=0:raise ValueError("original shape file has no records")
    # Do not infer physical nest-patch identity from a geographic source polygon.
    matched_columns=sorted(k for k,v in actual_matched.items() if v)
    return {
       "status":"ORIGINAL_PUBLISHER_GIS_SCHEMA_AND_ID_SCAN_COMPLETE",
       "geographic_source":base,"dataset_uuid":src["uuid"],
       "file_checksums":receipts,"original_crs_wkt_excerpt":prj[:300],
       "original_shapefile_type":geom_type,
       "original_shape_records":n,
       "original_dbf_field_names":fields,
       "exact_source_event_id_match_counts_by_field":dict(hits),
       "exact_source_event_ids_matched_by_field":{k:sorted(v) for k,v in actual_matched.items()},
       "exact_original_14_site_codes_matched_by_any_field":len(
           set().union(*(v for v in actual_matched.values())) if actual_matched else set()),
       "any_unique_exact_geog_identifier_field":len(matched_columns)==1,
       "source_polygon_is_true_past_ice_exposure":False,
       "source_polygon_is_verifiably_nested_nest_site":False,
    }

def run(event_json):
    ids=original_event_roster(event_json)
    output={
      "status":"AADC_SOURCE_GEOGRAPHIC_POLYGON_ID_GATE",
      "input_original_events":16,
      "input_distinct_geog_ids":14,
      "original_event_source_workflow":SOURCE_A_P_RUN,
      "original_geog_site_codes":ids,
      "publisher_polygons":{},
      "actual_nesting_patch_identity_verified":False,
      "new_ice_free_rock_verified":False,
      "ecological_effect_fitted":False,
    }
    with requests.Session() as session:
        for key,src in SOURCES.items():
            try:
                output["publisher_polygons"][key]=scan_polygon_dbf(session,src,set(ids))
            except Exception as e:
                output["publisher_polygons"][key]={
                  "status":"HOLD_ORIGINAL_SHAPE_COMPONENT_OR_ID",
                  "exception_class":type(e).__name__,
                  "message":str(e)[:250]}
    output["site_geographic_polygon_lookup_supported"]=any(
      d.get("any_unique_exact_geog_identifier_field") and
      d.get("exact_original_14_site_codes_matched_by_any_field",0)>0
      for d in output["publisher_polygons"].values()
    )
    output["note"]="Same geog site ID within SHP does not establish nest footprint, historic image exposure or occupation before/after."
    return output

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-event-json",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()
    try:result=run(a.original_event_json)
    except Exception as e:
        result={"status":"HOLD_ORIGINAL_AADC_GEO_EVENT_SOURCE",
                "reason":f"{type(e).__name__}: {str(e)}"[:250],
                "ecological_effect_fitted":False}
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":result["status"],
      "sources":{k:{"status":v.get("status"),"match":v.get("exact_original_14_site_codes_matched_by_any_field")}
                 for k,v in result.get("publisher_polygons",{}).items()}},sort_keys=True))

if __name__=="__main__":main()
