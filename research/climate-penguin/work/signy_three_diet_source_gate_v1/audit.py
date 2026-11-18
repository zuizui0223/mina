"""Source-first, outcome-blind inventory of three official BAS Signy diet ZIPs.

No ecological relationships are computed. An archive, file, and row inventory
helps distinguish animal samples, prey measurements, and auxiliary dictionaries
before linking diet, phenology, and breeding-stage measurements.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

SOURCES={
 "Adelie":{"doi":"10.5285/eb421e6d-b93b-4174-904b-9a7b0b401403","entry_id":"eb421e6d-b93b-4174-904b-9a7b0b401403","period":"1997-2020"},
 "Chinstrap":{"doi":"10.5285/95e38251-797c-495a-abc0-40a613599759","entry_id":"95e38251-797c-495a-abc0-40a613599759","period":"1997-2020"},
 "Gentoo":{"doi":"10.5285/fb9bd975-e6fe-406c-84be-01e57d612b5e","entry_id":"fb9bd975-e6fe-406c-84be-01e57d612b5e","period":"1998-2010"}
}
MAX_ONE_CSV=25*1024*1024
MAX_ARCHIVE_TOTAL=100*1024*1024

def discover_years(rows,heads):
    result={}
    for i,h in enumerate(heads):
        k=re.sub("[^a-z0-9]+","",h.lower())
        if not any(s in k for s in ("date","year","season","sample")):
            continue
        observed=set()
        for row in rows:
            if i>=len(row):continue
            match=re.search(r"(19[7-9]\d|20[0-3]\d)",row[i])
            if match:observed.add(int(match.group(1)))
        if observed:
            result[h]={"min":min(observed),"max":max(observed),"n_unique_year_tokens":len(observed)}
    return result

def inspect_archive(path):
    archive=Path(path)
    raw=archive.read_bytes()
    if len(raw)>MAX_ARCHIVE_TOTAL:raise ValueError("archive too large")
    out={"zip_sha256":hashlib.sha256(raw).hexdigest(),"zip_bytes":len(raw),"files":[]}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files=z.infolist()
        names=[f.filename for f in files]
        if len(names)!=len(set(names)):raise ValueError("Duplicate ZIP members")
        if sum(f.file_size for f in files)>MAX_ARCHIVE_TOTAL:raise ValueError("Uncompressed archive too large")
        for f in files:
            if f.is_dir() or f.filename.startswith("__MACOSX/"):continue
            if f.filename.startswith("/") or ".." in Path(f.filename).parts:raise ValueError("Unsafe path")
            if not f.filename.lower().endswith(".csv"):continue
            if f.file_size>MAX_ONE_CSV:raise ValueError("CSV too large")
            content=z.read(f)
            decoded=None
            for enc in ("utf-8-sig","cp1252"):
                try:decoded=content.decode(enc);encoding=enc;break
                except UnicodeDecodeError:continue
            if decoded is None:raise ValueError("Unsupported text encoding")
            parsed=list(csv.reader(io.StringIO(decoded)))
            if not parsed:raise ValueError("Empty source CSV")
            headers=parsed[0]
            rows=[r for r in parsed[1:] if r and any(x.strip() for x in r)]
            widths={len(row) for row in rows}
            out["files"].append({
               "path":f.filename,"sha256":hashlib.sha256(content).hexdigest(),
               "bytes":len(content),"encoding":encoding,"columns":headers,
               "n_columns":len(headers),"n_nonempty_rows":len(rows),
               "n_inconsistent_width_rows":sum(len(row)!=len(headers) for row in rows),
               "candidate_year_columns":discover_years(rows,headers),
               "data_grain_assigned":False
            })
    if not out["files"]:raise ValueError("No CSV sources")
    return out

def run(source_dir,out):
    source_dir=Path(source_dir); out=Path(out)
    summary={"status":"source_inventory_not_analyzed_diet","study":"Signy multi-axis niche source support",
             "source_dois":SOURCES,"by_species":{},"joined_niche_rows":None,
             "phenology_source":"BAS 00340 chronology data must be requested from PDC (not publicly downloadable from catalog)",
             "breeding_stage_existing_source":"mina Signy source-stage data already original-SHA-audited",
             "no_trophic_or_causal_claim":True}
    for species,info in SOURCES.items():
        file=source_dir/(species.lower()+".zip")
        if not file.is_file():raise FileNotFoundError(file)
        entry=inspect_archive(file)
        entry["source_doi"]=info["doi"]
        entry["source_entry_id"]=info["entry_id"]
        summary["by_species"][species]=entry
    out.mkdir(parents=True,exist_ok=True)
    (out/"source_inventory.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    print(json.dumps(run(args.source_dir,args.out),ensure_ascii=False,indent=2))
