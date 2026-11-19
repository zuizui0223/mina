#!/usr/bin/env python3
"""Original AADC 2025 search-effort source inventory vs East Antarctic site atlas.

Source-first contract: inventory publisher dataset IDs, UUIDs and exact object
names/bytes. No ecological records, claimed independent colonies, A->P events,
or model fitting. The 2025 archive may overlap legacy AADC AAS_4088 sources.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import quote, urlparse
import requests

BASE="https://data.aad.gov.au"
CATALOG=BASE+"/eds/api/dataset?size=10000"
EDS_EXPECTED={
    "5959":{"metadata":"AAS_4518_Seabird_Breeding_Occupancy",
            "title_token":"breeding occupancy"},
    "4344":{"metadata":"AAS_4088_Spatial_reference_system_coastal_east_Antarctica",
            "title_token":"spatial reference"},
}
MAX_JSON=28_000_000
MAX_OBJECTS=25000
RELEVANT_TOKENS=("occup","search","presence","absence","habitat","site",
                 "spatial","reference","map","region","data")
ALLOWED=("csv","tsv","txt","xlsx","xls","zip","gpkg","shp","dbf","geojson","json")

def download_json(session,url):
    info=urlparse(url)
    if info.scheme!="https" or info.hostname!="data.aad.gov.au":
        raise ValueError("untrusted URL")
    with session.get(url,timeout=(22,95),stream=True,
                     headers={"User-Agent":"mina-original-AADC-breeding-riskset-source-20261119"}) as r:
        r.raise_for_status()
        end=urlparse(r.url)
        if end.scheme!="https" or not (end.hostname=="data.aad.gov.au"
              or end.hostname.endswith(".data.aad.gov.au")):
            raise ValueError("unexpected original-source redirect")
        chunks=bytearray()
        for block in r.iter_content(32768):
            chunks.extend(block)
            if len(chunks)>MAX_JSON:
                raise ValueError("oversized official JSON catalogue")
    raw=bytes(chunks)
    if not raw.lstrip()[:1] in (b"{",b"["):
        raise ValueError("official endpoint did not return JSON")
    return json.loads(raw),hashlib.sha256(raw).hexdigest()

def select_exact_catalog_entries(rows):
    if not isinstance(rows,list):
        raise ValueError("AADC catalog not a list")
    chosen={}
    for eds,contract in EDS_EXPECTED.items():
        matches=[x for x in rows if str(x.get("eds_id",""))==eds]
        if len(matches)!=1:
            chosen[eds]={"status":"HOLD_MISSING_OR_DUPLICATE_EDS_ID",
                         "number_of_records":len(matches)}
            continue
        r=matches[0]
        metadata=str(r.get("metadata_entry_id",""))
        title=str(r.get("dataset_name",""))
        if (contract["metadata"].lower() not in metadata.lower() and
            contract["title_token"].lower() not in title.lower()):
            chosen[eds]={"status":"HOLD_PUBLISHER_IDENTITY_MISMATCH",
                         "metadata_entry_id":metadata,"dataset_title":title}
            continue
        uuid=str(r.get("uuid",""))
        if len(uuid)!=36:
            chosen[eds]={"status":"HOLD_MISSING_DATASET_UUID",
                         "dataset_title":title,"metadata_entry_id":metadata}
            continue
        chosen[eds]={"status":"EXACT_PUBLISHER_IDENTITY","eds_id":int(eds),
                     "uuid":uuid,"dataset_title":title,
                     "metadata_entry_id":metadata,
                     "dataset_visibility_status":r.get("dataset_visibility_status")}
    return chosen

def object_manifest(raw):
    if not isinstance(raw,list) or len(raw)>MAX_OBJECTS:
        raise ValueError("Publisher objects not bounded list")
    selected=[]
    seen=set()
    extension_counts={}
    for x in raw:
        if not isinstance(x,dict):
            continue
        name=str(x.get("name","")).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        ext=name.rsplit(".",1)[-1].lower() if "." in name else ""
        extension_counts[ext]=extension_counts.get(ext,0)+1
        if ext not in ALLOWED:continue
        if len(selected)>=2500:
            raise ValueError("Too many candidate original data objects")
        selected.append({"name":name,"size":x.get("size"),"extension":ext,
                         "priority_source_object":any(t in name.lower() for t in RELEVANT_TOKENS)})
    return {"all_source_objects":len(raw),
            "total_file_extensions":dict(sorted(extension_counts.items())),
            "potential_original_data_objects":selected,
            "source_objects_eligible_for_later_schema_audit":len(selected),
            "has_firsthand_survey_negative_proof":False}

def audit():
    with requests.Session() as session:
        dataset_list,catalog_sha=download_json(session,CATALOG)
        matches=select_exact_catalog_entries(dataset_list)
        out={
            "schema_version":1,
            "status":"AADC_OFFICIAL_SOURCE_MANIFEST_ONLY",
            "time_utc":datetime.now(timezone.utc).isoformat(),
            "original_catalog_sha256":catalog_sha,
            "catalog_record_count":len(dataset_list),
            "target_original_doi":{"5959":"10.26179/5n29-r073",
                                   "4344":"10.26179/53yk-8z83"},
            "datasets":{},
            "records_of_seabird_presence_absence_opened":False,
            "geographic_site_coords_opened":False,
            "original_bird_occupancy_effect_fitted":False,
        }
        for eds,entry in matches.items():
            rec=dict(entry)
            if rec.get("status")!="EXACT_PUBLISHER_IDENTITY":
                out["datasets"][eds]=rec
                continue
            uuid=rec["uuid"]
            url=BASE+f"/eds/api/dataset/{quote(uuid)}/objects?recursive=true&removeBasePath=true"
            try:
                obj,sha=download_json(session,url)
                rec["original_object_manifest_sha256"]=sha
                rec.update(object_manifest(obj))
                rec["status"]="PUBLISHER_ORIGINAL_OBJECT_INVENTORY_VERIFIED"
            except Exception as e:
                rec["status"]="HOLD_PUBLISHER_ORIGINAL_OBJECT_INDEX"
                rec["source_error"]=f"{type(e).__name__}: {str(e)}"[:220]
            out["datasets"][eds]=rec
        out["two_dataset_original_index_gate"]=all(
            v.get("status")=="PUBLISHER_ORIGINAL_OBJECT_INVENTORY_VERIFIED"
            for v in out["datasets"].values())
        out["next_source_rule"]=(
            "Inspect SOURCE SCHEMA of likely 2025 event table and full ice-free candidate site table, "
            "then join by original geographic site ID, source season and effort. "
            "No ecological colonization inference without independently dated exposure and post-exposure visits."
        )
        return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True,type=Path)
    args=p.parse_args()
    try:
        result=audit()
    except Exception as e:
        result={"schema_version":1,"status":"HOLD_AADC_ORIGINAL_PUBLISHER_CATALOG",
                "error":f"{type(e).__name__}: {str(e)}"[:360],
                "original_bird_occupancy_effect_fitted":False}
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,indent=2,sort_keys=True,
                                          ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"datasets":{
        x:{"status":v.get("status"),"title":v.get("dataset_title"),
           "objects":v.get("all_source_objects"),
           "eligible":v.get("source_objects_eligible_for_later_schema_audit")}
        for x,v in result.get("datasets",{}).items()}},ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
