#!/usr/bin/env python3
"""Outcome-blind audit of MAPPPD observation-method metadata."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd
import pyreadr

PRIMARY_SPECIES=("ADPE","CHPE","GEPE")


def load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        frame=x[expected]
    elif len(x)==1:
        frame=next(iter(x.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(x)}")
    if not isinstance(frame,pd.DataFrame):
        raise TypeError(expected)
    return frame


def candidate_units(obs:pd.DataFrame):
    nest=obs[
        obs["species_id"].isin(PRIMARY_SPECIES)
        & (obs["type"]=="nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest=nest.dropna(subset=["year"])
    units=[]
    for (site_id,species_id),local in nest.groupby(["site_id","species_id"]):
        years=sorted(set(int(y) for y in local["year"]))
        if len(years)>=5 and max(years)-min(years)>=10:
            units.append((str(site_id),str(species_id)))
    if len(units)!=152:
        raise ValueError(f"candidate unit drift: {len(units)} != 152")
    return set(units),nest


def norm(v):
    if pd.isna(v):
        return "NA"
    s=str(v).strip()
    return s if s else "NA"


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()

    obs=load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    units,nest=candidate_units(obs)

    local=nest[
        nest.apply(lambda r:(str(r["site_id"]),str(r["species_id"])) in units,axis=1)
    ][["site_id","species_id","year","accuracy","vantage"]].copy()
    local["vantage_norm"]=local["vantage"].map(norm)
    local["accuracy_norm"]=local["accuracy"].map(norm)

    unit_rows=[]
    for (site_id,species_id),g in local.groupby(["site_id","species_id"]):
        vantage=[x for x in g["vantage_norm"] if x!="NA"]
        accuracy=[x for x in g["accuracy_norm"] if x!="NA"]
        by_year=g.groupby("year")["vantage_norm"].agg(
            lambda s: sorted(set(x for x in s if x!="NA"))
        )
        mixed_years=[int(y) for y,vals in by_year.items() if len(vals)>1]
        distinct=sorted(set(vantage))
        unit_rows.append({
            "site_id":str(site_id),
            "species_id":str(species_id),
            "record_count":int(len(g)),
            "year_count":int(g["year"].nunique()),
            "vantage_categories":distinct,
            "vantage_category_count":len(distinct),
            "ground_only":bool(distinct==["ground"]),
            "contains_remote_imagery":bool(any(v in {"aerial","aerial photo","landsat","sentinel","uav","vhr"} for v in distinct)),
            "contains_offshore_vessel":bool("offshore vessel" in distinct),
            "missing_vantage_records":int((g["vantage_norm"]=="NA").sum()),
            "accuracy_categories":sorted(set(accuracy)),
            "missing_accuracy_records":int((g["accuracy_norm"]=="NA").sum()),
            "mixed_vantage_years":mixed_years,
            "has_same_year_mixed_vantage":bool(mixed_years),
        })

    units_df=pd.DataFrame(unit_rows)
    species_summary={}
    for species_id,g in units_df.groupby("species_id"):
        species_summary[str(species_id)]={
            "units":int(len(g)),
            "single_vantage_units":int((g["vantage_category_count"]<=1).sum()),
            "multi_vantage_units":int((g["vantage_category_count"]>1).sum()),
            "ground_only_units":int(g["ground_only"].sum()),
            "units_with_remote_imagery":int(g["contains_remote_imagery"].sum()),
            "units_with_same_year_mixed_vantage":int(g["has_same_year_mixed_vantage"].sum()),
            "units_with_any_missing_accuracy":int((g["missing_accuracy_records"]>0).sum()),
        }

    vantage_counts=Counter(local["vantage_norm"])
    accuracy_counts=Counter(local["accuracy_norm"])

    result={
        "schema_version":1,
        "audit_id":"mina-mapppd-observation-method-audit-v1",
        "candidate_site_species_units":152,
        "candidate_nest_records":int(len(local)),
        "record_vantage_counts":dict(sorted(vantage_counts.items())),
        "record_accuracy_counts":dict(sorted(accuracy_counts.items())),
        "unit_summary":{
            "single_vantage_units":int((units_df["vantage_category_count"]<=1).sum()),
            "multi_vantage_units":int((units_df["vantage_category_count"]>1).sum()),
            "ground_only_units":int(units_df["ground_only"].sum()),
            "units_with_remote_imagery":int(units_df["contains_remote_imagery"].sum()),
            "units_with_same_year_mixed_vantage":int(units_df["has_same_year_mixed_vantage"].sum()),
            "units_with_any_missing_accuracy":int((units_df["missing_accuracy_records"]>0).sum()),
            "units_with_any_missing_vantage":int((units_df["missing_vantage_records"]>0).sum()),
        },
        "species_summary":species_summary,
        "unit_details":unit_rows,
        "outcome_blind":true,
        "boundary":"Counts were used only to establish pre-frozen temporal eligibility; count values were not inspected or summarized in this audit."
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="unit_details"},indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
