#!/usr/bin/env python3
"""Schema/chain-of-custody gate for two original Ross penguin CSV files.

Use only provider-authorized original downloads; do not bypass the USAP-DC
download CAPTCHA. This script checks original MD5, schema support and
aggregate coverage without exposing band IDs, linking individuals,
selecting outcome years, or inferring actual breeding dispersal.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from collections import Counter
from pathlib import Path

FILES={
 "banding":{"basename":"band_inv_1994-2021.csv",
            "md5":"3da33defa4decc82b6e317c7fa9f9044",
            "doi":"10.15784/601443"},
 "resighting":{"basename":"band_resighting_1997-2021.csv",
               "md5":"aaae6ddad6d12081b5a68466794438a2",
               "doi":"10.15784/601444"}
}
MAX_MISSING_ROWS=0 # report, do not filter
def norm(s):
    return re.sub(r"[^a-z0-9]+","_",s.strip().lower()).strip("_")
def candidates(column):
    n=norm(column)
    types=[]
    if any(z in n for z in ("band","individual","bird_id","penguin_id","flipper_id","tag_id")):
        types.append("potential_animal_id")
    if any(z in n for z in ("date","year","season","observation_time","event_time")):
        types.append("potential_time")
    if any(z in n for z in ("site","colony","location","island","loc_code","place")):
        types.append("potential_location")
    if any(z in n for z in ("breed","nest","egg","chick","reproduct","adult","incubat")):
        types.append("potential_breeding_status")
    return types
def inspect(path,role):
    p=Path(path)
    if not p.is_file():raise FileNotFoundError(str(p))
    md5=hashlib.md5();sha=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            md5.update(block);sha.update(block)
    wanted=FILES[role]
    info={"source_role":role,"source_doi":wanted["doi"],
          "actual_filename":p.name,"bytes":p.stat().st_size,
          "expected_publisher_MD5":wanted["md5"],"measured_MD5":md5.hexdigest(),
          "SHA256":sha.hexdigest(),
          "publisher_checksum_matched":md5.hexdigest()==wanted["md5"]}
    if not info["publisher_checksum_matched"]:
        info["schema_status"]="SOURCE_HASH_MISMATCH_STOP"
        return info
    with p.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        columns=list(reader.fieldnames or [])
        if len(columns)!=len(set(columns)) or not columns:
            raise ValueError("Original CSV column header duplicate or missing")
        info["original_columns"]=columns
        classification={c:candidates(c) for c in columns}
        info["candidate_semantic_fields"]={
          kind:[col for col,v in classification.items() if kind in v]
          for kind in ("potential_animal_id","potential_time","potential_location","potential_breeding_status")}
        n=0
        empty=Counter()
        distinct={}
        for c in columns:
            if any(x in classification[c] for x in ("potential_location","potential_breeding_status")):
                distinct[c]=set()
        for row in reader:
            n+=1
            for c in columns:
                value=(row[c] or "").strip()
                if not value:empty[c]+=1
                if c in distinct and value and len(distinct[c])<=80:
                    distinct[c].add(value)
        info["n_original_rows"]=n
        info["missing_count_by_original_column"]={c:empty[c] for c in columns}
        info["low_cardinality_location_or_breeding_categories"]={
          c:sorted(v) if len(v)<=80 else ["HIGH_CARDINALITY_VALUES_NOT_LISTED"]
          for c,v in distinct.items()}
    # Header heuristics are not sufficient to establish semantic meaning.
    fields=info["candidate_semantic_fields"]
    essential=["potential_animal_id","potential_time","potential_location"]
    if not all(fields[z] for z in essential):
        info["schema_status"]="SCHEMA_INCOMPLETE_ID_OR_YEAR_OR_SITE"
    elif role=="resighting" and not fields["potential_breeding_status"]:
        info["schema_status"]="PROVISIONAL_RESIGHT_ONLY_NO_BREEDING_STATUS"
    else:
        info["schema_status"]="CANDIDATE_SCHEMA_AWAIT_SEMANTIC_MANUAL_AUDIT"
    return info
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--banding",required=True,type=Path)
    a.add_argument("--resighting",required=True,type=Path)
    a.add_argument("--out",type=Path,default=Path("build/ross_band_schema_audit"))
    args=a.parse_args()
    args.out.mkdir(exist_ok=True,parents=True)
    band=inspect(args.banding,"banding")
    res=inspect(args.resighting,"resighting")
    status=("SOURCE_ORIGINAL_MD5_VERIFIED_POSSIBLE_MOVEMENT_SOURCE"
        if band["publisher_checksum_matched"] and res["publisher_checksum_matched"] else
        "SOURCE_HASH_VERIFICATION_FAILED")
    summary={"status":status,"source_files":[band,res],
      "actual_breeding_dispersal_test_done":False,
      "did_not_commit_raw_individual_band_ids":True,
      "claim_boundary":"Original row count and header are source QA, NOT direct proof of natal or adult breeding dispersal.",
      "next_step":"Confirm band ID semantics, season and colony codes, true breeding event status, detection effort and longitudinal join without guessing fields."}
    (args.out/"source_schema_gate.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("ROSS_BAND_CSV_SCHEMA_GATE="+json.dumps({
      "status":status,
      "source_original_row_counts":{r["source_role"]:r.get("n_original_rows") for r in (band,res)},
      "publisher_md5_matched":{r["source_role"]:r["publisher_checksum_matched"] for r in (band,res)},
      "schema_status":{r["source_role"]:r["schema_status"] for r in (band,res)}},ensure_ascii=False),flush=True)
    if status!="SOURCE_ORIGINAL_MD5_VERIFIED_POSSIBLE_MOVEMENT_SOURCE":
        raise SystemExit(2)
if __name__=="__main__":
    main()
