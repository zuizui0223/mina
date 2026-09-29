#!/usr/bin/env python3
"""Outcome-blind temporal-overlap audit for Paper 2 candidate series."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr

MAPPPDR_COMMIT="88c73a507e0921b2541c218c71eaf16721bc6502"
SPECIES=("ADPE","CHPE","GEPE")
WINDOWS=((1980,2025),(1990,2025),(2000,2025),(2010,2025))
EXPECTED={"ADPE":57,"CHPE":46,"GEPE":49}


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


def candidate_units(root:Path):
    data=root/"data"
    sites=load_rda(data/"sites.rda","sites")
    obs=load_rda(data/"penguin_obs.rda","penguin_obs")
    nest=obs[
        obs["species_id"].isin(SPECIES)
        & (obs["type"]=="nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest=nest.dropna(subset=["year"])
    nest["year"]=nest["year"].astype(int)

    candidates=[]
    for (site_id,species_id),local in nest.groupby(["site_id","species_id"]):
        years=sorted(set(int(v) for v in local["year"]))
        if len(years)>=5 and max(years)-min(years)>=10:
            candidates.append((str(site_id),str(species_id)))
    if len(candidates)!=152:
        raise ValueError(f"candidate unit drift: {len(candidates)} != 152")
    by_species=pd.Series([sp for _,sp in candidates]).value_counts().to_dict()
    if {k:int(by_species.get(k,0)) for k in SPECIES}!=EXPECTED:
        raise ValueError(f"species candidate drift: {by_species}")

    meta=sites.set_index("site_id")[["site_name","region","ccamlr_id","latitude","longitude"]]
    return nest,candidates,meta


def thirds(start:int,end:int):
    width=end-start+1
    cut1=start+(width//3)-1
    cut2=start+(2*width//3)-1
    return (start,cut1),(cut1+1,cut2),(cut2+1,end)


def summarize(root:Path):
    nest,candidates,meta=candidate_units(root)
    records=[]
    window_summaries={}

    grouped={
        (str(site),str(sp)):local
        for (site,sp),local in nest.groupby(["site_id","species_id"])
    }

    for start,end in WINDOWS:
        key=f"{start}-{end}"
        first,_,last=thirds(start,end)
        for site_id,species_id in candidates:
            local=grouped[(site_id,species_id)]
            years=sorted(set(
                int(y) for y in local.loc[
                    (local["year"]>=start)&(local["year"]<=end),"year"
                ]
            ))
            n=len(years)
            span=(max(years)-min(years)) if years else 0
            basic=bool(n>=5 and span>=10)
            has_first=any(first[0]<=y<=first[1] for y in years)
            has_last=any(last[0]<=y<=last[1] for y in years)
            bridged=bool(basic and has_first and has_last)
            m=meta.loc[site_id]
            records.append({
                "window":key,
                "window_start":start,
                "window_end":end,
                "site_id":site_id,
                "species_id":species_id,
                "site_name":str(m["site_name"]),
                "region":str(m["region"]),
                "ccamlr_id":None if pd.isna(m["ccamlr_id"]) else str(m["ccamlr_id"]),
                "n_distinct_years":n,
                "observed_span_years":span,
                "first_observed_year":min(years) if years else None,
                "last_observed_year":max(years) if years else None,
                "has_first_third":has_first,
                "has_last_third":has_last,
                "basic_eligible":basic,
                "bridged_eligible":bridged,
            })

    frame=pd.DataFrame(records)
    for start,end in WINDOWS:
        key=f"{start}-{end}"
        sub=frame[frame["window"]==key]
        sp_summary={}
        for sp in SPECIES:
            s=sub[sub["species_id"]==sp]
            bridged=s[s["bridged_eligible"]]
            sp_summary[sp]={
                "gate0_candidate_units":EXPECTED[sp],
                "basic_eligible_units":int(s["basic_eligible"].sum()),
                "bridged_eligible_units":int(s["bridged_eligible"].sum()),
                "bridged_fraction_of_gate0":float(s["bridged_eligible"].mean()),
                "bridged_regions":int(bridged["region"].nunique()) if len(bridged) else 0,
                "median_distinct_years":float(s["n_distinct_years"].median()),
                "median_observed_span_years":float(s["observed_span_years"].median()),
            }
        qualifies=all(
            sp_summary[sp]["bridged_fraction_of_gate0"]>=0.50
            for sp in SPECIES
        )
        window_summaries[key]={
            "start_year":start,
            "end_year":end,
            "basic_eligible_units":int(sub["basic_eligible"].sum()),
            "bridged_eligible_units":int(sub["bridged_eligible"].sum()),
            "bridged_fraction_of_gate0":float(sub["bridged_eligible"].mean()),
            "species":sp_summary,
            "qualifies_primary_window_rule":bool(qualifies),
        }

    selected=None
    for start,end in WINDOWS:
        key=f"{start}-{end}"
        if window_summaries[key]["qualifies_primary_window_rule"]:
            selected=[start,end]
            break

    return {
        "schema_version":1,
        "audit_id":"mina-paper2-temporal-overlap-audit-v1",
        "mapppdr_commit":MAPPPDR_COMMIT,
        "candidate_site_species_units":152,
        "candidate_windows":[list(w) for w in WINDOWS],
        "window_summaries":window_summaries,
        "selected_primary_window":selected,
        "common_window_trend_endpoint_available":selected is not None,
        "selection_rule":"longest candidate window with >=50% bridged coverage within each Pygoscelis species",
        "unit_table":records,
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    a=p.parse_args()
    result=summarize(a.mapppdr_dir)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    pd.DataFrame(result["unit_table"]).to_csv(a.out_csv,index=False)
    brief={k:v for k,v in result.items() if k!="unit_table"}
    print(json.dumps(brief,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
