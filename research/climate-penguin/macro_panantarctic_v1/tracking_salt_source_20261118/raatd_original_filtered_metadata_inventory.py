#!/usr/bin/env python3
"""Read the FULL source-publisher-checksummed SCAR RAATD filtered archive,
publish only metadata *aggregates* for a strict source overlap audit.

Source: RAATD 2020 Zenodo 3722948 filtered-noTMB (not 993 MB TMB objects).
The archive may have license/attribution conditions and sensitive individual
deployment records. Keep original archive and raw metadata in the CI workspace,
publish aggregate counts/schema and source source provenance ONLY.
"""
from __future__ import annotations
import argparse,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
from collections import Counter
import pandas as pd
URL="https://zenodo.org/api/records/3722948"
PUBLISHER_MD5="168e5b9b5c4ed20bb84dd00145acb0a5"
PUBLISHER_FILE="SCAR_EGBAMM_RAATD-filtered-noTMB.zip"
MAX_ARCHIVE=450_000_000
UA={"User-Agent":"mina-RAATD-publisher-original-provenance/1.0 (https://github.com/zuizui0223/mina)"}

def original_archive(output):
    with urllib.request.urlopen(urllib.request.Request(URL,headers=UA),timeout=90) as r:
        record=json.load(r)
    if record.get("id")!=3722948:raise ValueError("RAATD Zenodo record changed")
    fil=next((i for i in record.get("files",[]) if i.get("key")==PUBLISHER_FILE),None)
    if not fil:raise ValueError("Original RAATD filtered-noTMB original file missing")
    ck=fil.get("checksum")
    if ck!="md5:"+PUBLISHER_MD5:raise ValueError("Publisher RAATD original MD5 changed")
    if fil.get("size",0)>MAX_ARCHIVE or fil.get("size",0)<100_000_000:
        raise ValueError("Unverified or unexpectedly large RAATD file")
    link=fil["links"].get("content") or fil["links"].get("self")
    dest=Path(output)/"original_Raatd_full_filtered_noTMB_source.zip"
    h=hashlib.md5();sha=hashlib.sha256();n=0
    with urllib.request.urlopen(urllib.request.Request(link,headers=UA),timeout=180) as response, dest.open("wb") as dst:
        while True:
            c=response.read(2**20)
            if not c:break
            n+=len(c)
            if n>MAX_ARCHIVE:raise ValueError("Too much data from publisher")
            h.update(c);sha.update(c);dst.write(c)
    if n!=fil["size"] or h.hexdigest()!=PUBLISHER_MD5:
        raise ValueError(f"Original RAATD source bytes or publisher MD5 mismatch {n} {h.hexdigest()}")
    return dest,{"zenodo_id":3722948,"source_archive":PUBLISHER_FILE,"original_archive_bytes":n,
            "original_archive_md5":h.hexdigest(),"original_archive_sha256":sha.hexdigest(),
            "source_record_url":"https://zenodo.org/records/3722948",
            "original_source_date_period":"1991–2016, not a current tracked-animal survey"}

def inspect_metadata(z):
    members=[x for x in z.infolist() if not x.is_dir()]
    # Do not read original large animal position series. First inventory names.
    archive=[{"name":x.filename,"bytes":x.file_size,"compressed_bytes":x.compress_size}
             for x in members]
    candidates=[x for x in members if x.filename.lower().endswith(".csv") and
                any(t in x.filename.lower() for t in ("meta","deploy")) and x.file_size<=30_000_000]
    if not candidates:
        return {"status":"ORIGINAL_RAATD_NO_SMALL_METADATA_CSV_FOUND",
                "archive_members":archive,"metadata_candidates":[]},None
    # A metadata table is one row per animal, NOT millions of position fixes.
    candidates.sort(key=lambda x:("metadata" not in x.filename.lower(),x.file_size))
    assessments=[]
    valid=None
    for x in candidates:
        with z.open(x) as raw:
            d=pd.read_csv(raw,low_memory=False)
        desc={"name":x.filename,"rows":len(d),"cols":len(d.columns),
              "columns":[str(x) for x in d.columns],
              "scientific_names":sorted(map(str,d["scientific_name"].dropna().unique()))
                  if "scientific_name" in d else []}
        assessments.append(desc)
        if 100<=len(d)<=30_000 and "individual_id" in d.columns and "scientific_name" in d.columns:
            valid=(x.filename,d)
            break
    if valid is None:
        return {"status":"METADATA_GRAIN_NOT_AUTHOR_CONFIRMED",
                "archive_members":archive,"metadata_candidates":assessments},None
    name,d=valid
    if d.individual_id.duplicated().sum():
        # Could have multiple deployments per individual! Be explicit.
        original_id_dupes=int(d.individual_id.duplicated().sum())
    else:original_id_dupes=0
    species=(d.scientific_name.fillna("NA").astype(str).value_counts().to_dict())
    summary={"status":"ORIGINAL_RAATD_INDIVIDUAL_METADATA_EXTRACTED",
             "archive_members":archive,
             "metadata_candidates":assessments,
             "source_metadata_member":name,
             "metadata_total_rows":len(d),
             "metadata_distinct_individual_ids":int(d.individual_id.nunique()),
             "metadata_duplicate_individual_ids":original_id_dupes,
             "metadata_taxa_counts":{str(k):int(v) for k,v in species.items()},
             "Adelie_original_metadata_rows":int(
                d.scientific_name.fillna("").astype(str).str.lower().eq("pygoscelis adeliae").sum()),
             "columns":list(d.columns),
             "meta_csv_downloaded_but_not_republished":True}
    return summary,d

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    p.add_argument("--work",required=True)
    a=p.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    work=Path(a.work);work.mkdir(parents=True,exist_ok=True)
    archive,pin=original_archive(work)
    with zipfile.ZipFile(archive) as z:
        # z.testzip decompresses 1GB of RDS, avoid; verify per metadata via ZIP CRC open.
        original,metadata=inspect_metadata(z)
    if metadata is not None:
        raw=work/"raitd_original_deployment_metadata_DO_NOT_PUBLISH.csv"
        metadata.to_csv(raw,index=False)
        pin["original_metadata_extracted_under_workspace_only"]=str(raw)
    # NEVER publish path of local sensitive original metadata from the receipt.
    pin.pop("original_metadata_extracted_under_workspace_only",None)
    rec={**pin,**original,"not_original_diet_or_prey_capture":True,
         "location_tracks_not_yet_used":True,
         "original_animal_metadata_not_uploaded":True,
         "raw_publisher_zip_not_uploaded":True,
         "author_data_collection_ended_2016":True}
    (out/"raatd_source_2020_publisher_metadata_inventory.json").write_text(
        json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in rec.items() if k not in ("archive_members","metadata_candidates")},
                     ensure_ascii=False,indent=2))
    return rec
if __name__=="__main__":main()
