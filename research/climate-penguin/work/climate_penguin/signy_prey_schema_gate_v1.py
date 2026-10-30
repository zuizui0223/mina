"""Outcome-blind BAS Signy three-species diet source structure audit v1.

Inspect first-party, openly accessible original BAS RAMADDA ZIP tree members.
Do NOT compute dietary outcomes, species differences, sample mass or proxy
coefficients until schemas, units and temporal grain are explicitly frozen.
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
    "Adelie": ("eb421e6d-b93b-4174-904b-9a7b0b401403",1997,2020),
    "Chinstrap": ("95e38251-797c-495a-abc0-40a613599759",1997,2020),
    "Gentoo": ("fb9bd975-e6fe-406c-84be-01e57d612b5e",1998,2010)
}
def columns(raw):
    text=None
    for encoding in ("utf-8-sig","utf-8","cp1252"):
        try:
            text=raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise ValueError("no supported text encoding")
    records=list(csv.reader(io.StringIO(text)))
    if not records:
        return {"empty_file":True}
    header=[str(x).strip() for x in records[0]]
    data=[r for r in records[1:] if any(s.strip() for s in r)]
    normalized={re.sub(r"[^a-z0-9]+","",c.lower()):c for c in header}
    candidates={kind:[c for c in header if re.search(regex,c,flags=re.I)]
                for kind,regex in {
                    "date":r"date|sample|season|year|time",
                    "wet_mass":r"(wet|total|sample|mass|weight).*(mass|weight)|(mass|weight).*(wet|total)",
                    "krill_mass":r"krill|euphausia|crustac",
                    "fish_mass":r"fish|otolith",
                    "cephalopod":r"cephalopod|squid",
                    "identifiers":r"bird|individual|sample.*id|tag|sample.*number",
                    "units":r"unit|gram|milligram|kg|percent|fraction|proportion"
                }.items()}
    return {
        "header":header,"row_count":len(data),
        "widths":[{"width":n,"n":sum(len(z)==n for z in data)}
                  for n in sorted(set(len(z) for z in data))],
        "candidate_column_categories":candidates,
        "has_time_label":bool(candidates["date"]),
        "has_weight_candidate":bool(candidates["wet_mass"]),
        "has_krill_candidate":bool(candidates["krill_mass"]),
        "has_fish_candidate":bool(candidates["fish_mass"]),
        "sample_uniqueness_confirmed":False,
        "date_to_breeding_season_confirmed":False,
        "outcome_values_opened":False
    }

def audit(root):
    out={}
    for species,(entry,lo,hi) in SOURCES.items():
        path=Path(root)/(species.lower()+".zip")
        if not zipfile.is_zipfile(path):
            raise ValueError("Original diet archive not ZIP: "+str(path))
        groups=[]
        with zipfile.ZipFile(path) as zipf:
            for name in sorted(zipf.namelist()):
                if not name.lower().endswith(".csv"):
                    continue
                buf=zipf.read(name)
                meta=columns(buf)
                groups.append({
                    "publisher_path":name,
                    "original_sha256":hashlib.sha256(buf).hexdigest(),
                    "original_bytes":len(buf),
                    **meta
                })
        if len(groups)<1:
            raise ValueError("No diet CSV members for "+species)
        out[species]={
            "source_entry_id":entry,
            "doi":"10.5285/"+entry,
            "catalogue_time_range_years":[lo,hi],
            "original_zip_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "original_zip_bytes":path.stat().st_size,
            "csv_member_count":len(groups),
            "csv_members":groups,
            "no_numeric_diet_values_inspected":True
        }
    return {
        "status":"SOURCE_HEADERS_ONLY_NEEDS_UNIT_AND_SEASON_GRAIN_FREEZE",
        "date":"2026-10-30",
        "species":out,
        "outcome_statistics_computed":False,
        "next_required_gate":[
            "Choose specific primary sample-mass/krill fields from authentic source members, with explicit units",
            "Preserve multiple samples within breeding season and sampling date, never treat stomachs as independent climate observations",
            "Resolve breeding-season label from dates and source semantics rather than assuming calendar January year",
            "Calculate annual diet covariates then match same-source Signy fledgling output at species-year grain",
            "Evaluate temporal / regional validation before interpreting food/ice/salinity pathways"
        ]
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source-dir",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    args=a.parse_args()
    result=audit(args.source_dir)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],
        "csv_members":{k:[{
            "name":z["publisher_path"],
            "n":z.get("row_count"),
            "headers":z.get("header",[]),
            "sha":z["original_sha256"]
        } for z in v["csv_members"]] for k,v in result["species"].items()}
    },ensure_ascii=False))

if __name__=="__main__":
    main()
