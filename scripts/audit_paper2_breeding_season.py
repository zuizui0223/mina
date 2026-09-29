#!/usr/bin/env python3
"""Outcome-blind calendar-year versus breeding-season audit for Paper 2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr

MAPPPDR_COMMIT="88c73a507e0921b2541c218c71eaf16721bc6502"
SPECIES=("ADPE","CHPE","GEPE")
EXPECTED={"ADPE":57,"CHPE":46,"GEPE":49}
WINDOWS=((1980,2025),(1990,2025),(2000,2025),(2010,2025))


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


def frozen_cohort(obs:pd.DataFrame):
    nest=obs[
        obs["species_id"].isin(SPECIES)
        & (obs["type"]=="nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest["season"]=pd.to_numeric(nest["season"],errors="coerce")

    units=[]
    for (site_id,species_id),local in nest.dropna(subset=["year"]).groupby(["site_id","species_id"]):
        years=sorted(set(int(y) for y in local["year"]))
        if len(years)>=5 and max(years)-min(years)>=10:
            units.append((str(site_id),str(species_id)))
    if len(units)!=152:
        raise ValueError(f"Gate0 cohort drift: {len(units)} != 152")
    counts=pd.Series([sp for _,sp in units]).value_counts().to_dict()
    if {sp:int(counts.get(sp,0)) for sp in SPECIES}!=EXPECTED:
        raise ValueError(f"Gate0 species drift: {counts}")
    keys=set(units)
    cohort=nest[
        nest.apply(lambda r:(str(r["site_id"]),str(r["species_id"])) in keys,axis=1)
    ].copy()
    return units,cohort


def thirds(start:int,end:int):
    width=end-start+1
    cut1=start+(width//3)-1
    cut2=start+(2*width//3)-1
    return (start,cut1),(cut1+1,cut2),(cut2+1,end)


def window_summary(cohort:pd.DataFrame,units:list[tuple[str,str]],field:str):
    grouped={
        (str(site),str(sp)):local
        for (site,sp),local in cohort.groupby(["site_id","species_id"])
    }
    summaries={}
    unit_rows=[]
    for start,end in WINDOWS:
        first,_,last=thirds(start,end)
        key=f"{start}-{end}"
        species_summary={}
        for site_id,species_id in units:
            local=grouped[(site_id,species_id)]
            vals=pd.to_numeric(local[field],errors="coerce").dropna()
            times=sorted(set(int(v) for v in vals if start<=int(v)<=end))
            n=len(times)
            span=(max(times)-min(times)) if times else 0
            basic=bool(n>=5 and span>=10)
            has_first=any(first[0]<=v<=first[1] for v in times)
            has_last=any(last[0]<=v<=last[1] for v in times)
            bridged=bool(basic and has_first and has_last)
            unit_rows.append({
                "time_field":field,
                "window":key,
                "site_id":site_id,
                "species_id":species_id,
                "n_distinct_time_units":n,
                "span":span,
                "first_observed":min(times) if times else None,
                "last_observed":max(times) if times else None,
                "bridged_eligible":bridged,
            })
        frame=pd.DataFrame([r for r in unit_rows if r["time_field"]==field and r["window"]==key])
        for sp in SPECIES:
            s=frame[frame["species_id"]==sp]
            species_summary[sp]={
                "gate0_units":EXPECTED[sp],
                "bridged_units":int(s["bridged_eligible"].sum()),
                "bridged_fraction":float(s["bridged_eligible"].mean())
            }
        qualifies=all(species_summary[sp]["bridged_fraction"]>=0.50 for sp in SPECIES)
        summaries[key]={
            "start":start,
            "end":end,
            "bridged_units":int(frame["bridged_eligible"].sum()),
            "bridged_fraction":float(frame["bridged_eligible"].mean()),
            "species":species_summary,
            "qualifies":bool(qualifies)
        }
    selected=None
    for start,end in WINDOWS:
        key=f"{start}-{end}"
        if summaries[key]["qualifies"]:
            selected=[start,end]
            break
    return summaries,selected,unit_rows


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    a=p.parse_args()

    obs=load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    units,cohort=frozen_cohort(obs)

    n=len(cohort)
    season_nonmissing=int(cohort["season"].notna().sum())
    season_fraction=season_nonmissing/n if n else 0.0

    both=cohort.dropna(subset=["year","season"]).copy()
    both["year_i"]=both["year"].astype(int)
    both["season_i"]=both["season"].astype(int)
    mismatch=both[both["year_i"]!=both["season_i"]].copy()

    month_counts={
        str(int(k)):int(v)
        for k,v in mismatch["month"].dropna().astype(int).value_counts().sort_index().items()
    }
    species_mismatch={}
    for sp in SPECIES:
        s=both[both["species_id"]==sp]
        species_mismatch[sp]={
            "records_with_both":int(len(s)),
            "mismatch_records":int((s["year_i"]!=s["season_i"]).sum()),
            "mismatch_fraction":float((s["year_i"]!=s["season_i"]).mean()) if len(s) else None
        }

    chosen_field="season" if season_fraction>=0.95 else "year"
    year_sum,year_sel,year_rows=window_summary(cohort,units,"year")
    season_sum,season_sel,season_rows=window_summary(cohort,units,"season")
    selected=season_sel if chosen_field=="season" else year_sel

    result={
        "schema_version":1,
        "audit_id":"mina-paper2-breeding-season-audit-v1",
        "mapppdr_commit":MAPPPDR_COMMIT,
        "frozen_gate0_units":152,
        "candidate_nest_records":n,
        "season_nonmissing_records":season_nonmissing,
        "season_nonmissing_fraction":season_fraction,
        "records_with_year_and_season":int(len(both)),
        "year_season_mismatch_records":int(len(mismatch)),
        "year_season_mismatch_fraction":float(len(mismatch)/len(both)) if len(both) else None,
        "mismatch_month_counts":month_counts,
        "species_mismatch":species_mismatch,
        "decision_rule":"use season if >=95% nonmissing in frozen cohort; otherwise year",
        "selected_primary_time_field":chosen_field,
        "calendar_year_windows":year_sum,
        "breeding_season_windows":season_sum,
        "calendar_year_selected_window":year_sel,
        "breeding_season_selected_window":season_sel,
        "selected_primary_window":selected,
        "no_count_magnitudes_opened":True,
        "unit_table":year_rows+season_rows,
    }

    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    pd.DataFrame(result["unit_table"]).to_csv(a.out_csv,index=False)
    print(json.dumps({k:v for k,v in result.items() if k!="unit_table"},indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
