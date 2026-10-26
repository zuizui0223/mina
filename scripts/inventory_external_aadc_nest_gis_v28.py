#!/usr/bin/env python3
"""V28 first-party AADC original Antarctic bird nest spatial archive discovery.

Only exact fixed original metadata IDs, official current EDS dataset UUID
and source object file manifests. NO bird nest values/geometry/counts fetched.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import quote

import requests
from audit_aadc_original_workbook_headers_v11 import (
    HOST,LIST_API,trusted_response_get
)

SOURCE_IDS=(
    "windmill_flyingbirds_gis160",
    "bech_nest_locations",
    "AAS_4518_Cape_Petrel_population_estimates_VestfoldIslands",
    "AAS_4112_Nest_Colony_Locations",
)
SOURCE_THEMES={
    SOURCE_IDS[0]:"WINDMILL_1998_99_PENGUIN_COLONY_FLYING_NESTS",
    SOURCE_IDS[1]:"BECHERVAISE_2000_2002_ADELIE_NEST_GPS",
    SOURCE_IDS[2]:"VESTFOLD_CAPE_PETREL_1970S_2017",
    SOURCE_IDS[3]:"MACQUARIE_FLYING_BIRD_2012_13_SUBANTARCTIC",
}
MAX_SOURCE_INDEX=30_000_000
MAX_SOURCE_OBJECTS=5000
SPATIAL_TYPES={".shp",".shx",".dbf",".prj",".gpkg",".geojson",".zip",".kml",".gdb",".csv",".tif",".tiff"}


def exact_registry(records:list):
    if not isinstance(records,list):
        raise ValueError("SOURCE_STOP official AADC registry not an array")
    lookup={}
    for item in records:
        if not isinstance(item,dict):
            continue
        k=str(item.get("metadata_entry_id","")).casefold()
        if k in {s.casefold() for s in SOURCE_IDS}:
            lookup.setdefault(k,[]).append(item)
    return {name:lookup.get(name.casefold(),[]) for name in SOURCE_IDS}


def original_source_object_index(session,entry):
    uuid=str(entry.get("uuid","")).strip()
    if not re.fullmatch(r"[0-9a-fA-F-]{36}",uuid):
        raise ValueError("SOURCE_STOP original AADC source UUID not a valid literal")
    url=(f"https://{HOST}/eds/api/dataset/{quote(uuid)}"
         "/objects?recursive=true&removeBasePath=true")
    raw,receipt=trusted_response_get(session,url,MAX_SOURCE_INDEX,True)
    objects=json.loads(raw)
    if not isinstance(objects,list) or len(objects)>MAX_SOURCE_OBJECTS:
        raise ValueError("SOURCE_STOP original AADC object index shape/count changed")
    files=[x for x in objects if isinstance(x,dict) and x.get("name")]
    names=[str(x["name"]) for x in files]
    if len(names)!=len(set(names)):
        raise ValueError("SOURCE_STOP repeated original full path in source manifest")
    counts=Counter(Path(n).suffix.casefold() for n in names)
    spatial=[{"original_publisher_file_path":str(z["name"]),
              "publisher_source_declared_bytes":z.get("size"),
              "original_EDS_dataset_uuid":uuid} for z in files
              if Path(str(z["name"])).suffix.casefold() in SPATIAL_TYPES]
    return {
        "status":"ORIGINAL_AADC_PUBLIC_OBJECT_INDEX",
        "original_dataset_EDS_UUID":uuid,
        "official_file_index_SHA256":receipt["source_sha256"],
        "original_files_total":len(files),
        "source_object_extensions":dict(sorted(counts.items())),
        "spatial_candidate_file_paths_metadata_only":spatial,
        "original_bird_nest_or_polygon_row_values_loaded":0,
        "named_islands_from_source_filenames_are_independent_land_polygons":False,
    }


def inspect_index(session):
    raw,index=trusted_response_get(session,LIST_API,MAX_SOURCE_INDEX,True)
    records=json.loads(raw)
    matches=exact_registry(records)
    statuses={}
    for source in SOURCE_IDS:
        items=matches[source]
        if not items:
            statuses[source]={
                "source_theme":SOURCE_THEMES[source],
                "status":"HOLD_EXACT_SOURCE_NOT_IN_CURRENT_PUBLIC_EDS_REGISTRY",
                "original_metadata_page":"https://data.aad.gov.au/metadata/records/"+source,
                "original_source_bird_rows_loaded":0,
            }
            continue
        readings=[]
        for item in items:
            try:
                result=original_source_object_index(session,item)
                readings.append({
                    "original_metadata_id":source,
                    "original_source_theme":SOURCE_THEMES[source],
                    "metadata_EDS_id":item.get("eds_id"),
                    "metadata_current_dataset_name":item.get("dataset_name"),
                    **result,
                })
            except Exception as e:
                readings.append({
                    "original_metadata_id":source,
                    "status":"HOLD_OFFICIAL_SOURCE_FILE_OBJECT_INDEX",
                    "original_EDS_dataset_uuid":str(item.get("uuid","")),
                    "error_type":type(e).__name__,"error":str(e)[:300],
                    "original_bird_nest_or_polygon_row_values_loaded":0,
                })
        statuses[source]={
            "source_theme":SOURCE_THEMES[source],
            "source_metadata_registry_matches":len(items),
            "source_object_index_success_n":sum(x["status"]=="ORIGINAL_AADC_PUBLIC_OBJECT_INDEX" for x in readings),
            "source_EDS_version_manifest_receipts":readings,
            "status":"OFFICIAL_SOURCE_INDEX_AVAILABLE"
                if any(x["status"]=="ORIGINAL_AADC_PUBLIC_OBJECT_INDEX" for x in readings)
                else "HOLD_OFFICIAL_ORIGINAL_SOURCE_METADATA_OR_FILE_ACCESS",
        }
    return {
        "status":"AADC_FOUR_ORIGINAL_MULTITAXON_POLAR_NEST_GIS_SOURCE_V28",
        "original_AADC_registry_SHA256":index["source_sha256"],
        "source_original_registry_total_count":len(records),
        "source_original_exact_metadata_id_count":len(SOURCE_IDS),
        "original_AADC_source_field_GIS_candidate_inventory":statuses,
        "source_metadata_records_verified_without_nest_data":True,
        "new_original_nest_coordinates_or_species_presence_observations_loaded":0,
        "new_species_species_island_population_effect_fitted":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result={"status":"HOLD_AADC_EXTERNAL_ANTARCTIC_FIELD_GIS_V28",
            "new_species_species_island_population_effect_fitted":False}
    try:
        with requests.Session() as session:
            result=inspect_index(session)
    except Exception as ex:
        result["error_type"]=type(ex).__name__
        result["error"]=str(ex)[:900]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    concise={**result}
    if "original_AADC_source_field_GIS_candidate_inventory" in concise:
        concise["original_AADC_source_field_GIS_candidate_inventory"]={
            k:{"status":v["status"],
               "version_matches":v.get("source_metadata_registry_matches"),
               "original_file_index_success":v.get("source_object_index_success_n"),
               "metadata_sample":v.get("source_EDS_version_manifest_receipts",[{}])[0].get(
                   "spatial_candidate_file_paths_metadata_only",[])[:12]
              } for k,v in result["original_AADC_source_field_GIS_candidate_inventory"].items()
        }
    print(json.dumps(concise,ensure_ascii=False))
    if result["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
