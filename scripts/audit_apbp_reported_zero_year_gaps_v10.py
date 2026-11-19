#!/usr/bin/env python3
"""Post-result descriptive APBP sampling-gap audit: reported positive/zero nests.

Source-aligned site×species breeding seasons ONLY. Does NOT infer local
colonization/extinction or treat no survey as zero; not preregistered effect.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import pandas as pd

SOURCE_SHA="75c98ad9174f6ca8b88ae915adb8bb39de5d279099b45ce1ae7d1b2e25d5ba59"
SPECIES={"Pygoscelis adeliae","Pygoscelis antarcticus","Pygoscelis papua"}
KEY=("site_id_original","scientificName_accepted","breeding_start_year")
BINS=((1,1),(2,2),(3,5),(6,10),(11,20),(21,200))


def load_source(path:Path)->pd.DataFrame:
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
        raise ValueError("SOURCE_STOP original public APBP linked measurement CSV changed")
    return pd.read_csv(path,low_memory=False)


def dated_seasons(records:pd.DataFrame):
    df=records.loc[
        records.eligibility.eq("ELIGIBLE_NEST_RECORD_ONLY") &
        records.scientificName_accepted.isin(SPECIES)
    ].copy()
    # pandas.to_datetime with heterogeneous date strings can silently reject
    # many legitimate YYYY-MM dates: use a strict original ISO year-month parser.
    parts=df.event_date.fillna("").astype(str).str.extract(
        r"^(?P<year>18\d{2}|19\d{2}|20\d{2})-(?P<month>\d{2})(?:-\d{2})?$"
    )
    years=pd.to_numeric(parts["year"],errors="coerce")
    months=pd.to_numeric(parts["month"],errors="coerce")
    df=df.loc[months.isin((1,2,12)) & years.notna()].copy()
    years=years.loc[df.index].astype(int)
    months=months.loc[df.index].astype(int)
    df["breeding_start_year"]=years-months.isin((1,2)).astype(int)
    counts=pd.to_numeric(df.nest_numeric_candidate,errors="coerce")
    if (counts.isna().any() or (counts<0).any() or
        (counts!=counts.round()).any()):
        raise ValueError("SOURCE_STOP invalid measured nest count")
    df["nests"]=counts.astype("int64")
    if df["site_id_original"].isna().any():
        raise ValueError("SOURCE_STOP original site ID missing")
    sizes=df.groupby(list(KEY),dropna=False).size()
    singular=sizes[sizes.eq(1)].index
    eligible=df.set_index(list(KEY)).loc[singular].reset_index()
    return eligible.sort_values(list(KEY)),{
        "exact_season_original_nest_record_rows_including_replicates":len(df),
        "same_site_species_year_groups_with_multiple_original_surveys":int((sizes>1).sum()),
        "same_site_species_year_duplicate_rows_omitted":int(sizes[sizes>1].sum()),
        "valid_unique_site_species_season_rows":len(eligible),
        "distinct_original_source_site_ids":int(eligible.site_id_original.nunique()),
    }


def state(row_prev, row_next):
    a=int(row_prev)
    b=int(row_next)
    if a>0 and b>0:return "positive_to_positive"
    if a==0 and b==0:return "zero_to_zero"
    if a>0 and b==0:return "positive_to_reported_zero"
    if a==0 and b>0:return "reported_zero_to_positive"
    raise ValueError("OBS_STOP invalid nonnegative nest state")


def successive_observed_records(unique:pd.DataFrame):
    result=[]
    for (site,taxon),group in unique.groupby(list(KEY[:2]),sort=True):
        g=group.sort_values("breeding_start_year")
        for i in range(1,len(g)):
            old,new=g.iloc[i-1],g.iloc[i]
            gap=int(new.breeding_start_year-old.breeding_start_year)
            if gap<=0:
                raise ValueError("PANEL_STOP nonascending surveyed year")
            result.append({
                "original_siteID":site,
                "taxon":taxon,
                "previous_breeding_start_year":int(old.breeding_start_year),
                "current_breeding_start_year":int(new.breeding_start_year),
                "original_previous_reported_nests":int(old.nests),
                "original_current_reported_nests":int(new.nests),
                "unobserved_years_between":gap-1,
                "survey_year_gap":gap,
                "reported_state_change":state(old.nests,new.nests),
                "source_note":"Observations at source site only; absent from dataset is NOT a zero",
            })
    return pd.DataFrame(result)


def summarise(unique, panels, eligibility,source_sha):
    cats=("positive_to_positive","zero_to_zero",
          "positive_to_reported_zero","reported_zero_to_positive")
    exact=panels[panels.survey_year_gap.eq(1)]
    switched=panels[panels.reported_state_change.isin(cats[-2:])]
    intervals={}
    for lo,hi in BINS:
        name=f"{lo}" if lo==hi else f"{lo}-{hi}"
        group=panels.loc[panels.survey_year_gap.between(lo,hi)]
        intervals[name]={
            "original_observed_record_pairs":len(group),
            "reported_state_classes":{
                name:int(group.reported_state_change.eq(name).sum()) for name in cats
            }
        }
    distinct_histories=unique.groupby(list(KEY[:2])).size()
    return {
        "status":"DESCRIPTIVE_SOURCE_SAMPLING_GAP_AUDIT_NOT_TURNOVER_CAUSAL_TEST",
        "source_original_sha256":source_sha,
        "canonical_dataset":"APBP DwC-A v2.3; DOI 10.48361/zftxkr",
        "taxa":sorted(SPECIES),
        "eligibility":eligibility,
        "original_site_species_histories_with_two_or_more_distinct_seasons":int((distinct_histories>=2).sum()),
        "consecutive_reported_survey_pairs_all_time_gaps":len(panels),
        "exactly_one_breeding_season_behind_pairs":len(exact),
        "exact_1year_original_measured_state_transitions":{
            name:int(exact.reported_state_change.eq(name).sum()) for name in cats
        },
        "reported_positive_zero_switches_any_gap":len(switched),
        "reported_positive_zero_switches_exact_1year":int((switched.survey_year_gap==1).sum()),
        "reported_switch_gap_min":int(switched.survey_year_gap.min()) if len(switched) else None,
        "reported_switch_gap_median":float(switched.survey_year_gap.median()) if len(switched) else None,
        "reported_switch_gap_max":int(switched.survey_year_gap.max()) if len(switched) else None,
        "observed_interval_gap_table":intervals,
        "interpretation":(
            "No source-observed positive/zero switch in exactly adjacent years. "
            "Long-gap source count-state changes cannot be dated to a true local "
            "breeding extinction or recolonization event. This is known-site "
            "measurement coverage, not unbiased island occupancy monitoring."
        ),
        "ecological_parameter_or_pvalue_fitted":False,
        "novel_island_causal_mechanism_found":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--population",required=True,type=Path)
    parser.add_argument("--json",required=True,type=Path)
    parser.add_argument("--csv",required=True,type=Path)
    a=parser.parse_args()
    result={"status":"HOLD_INVALID_APBP_SOURCE"}
    try:
        records=load_source(a.population)
        source,meta=dated_seasons(records)
        observed=successive_observed_records(source)
        if observed.empty:
            raise ValueError("PANEL_STOP no source linked seasons")
        result=summarise(source,observed,meta,SOURCE_SHA)
        a.csv.parent.mkdir(parents=True,exist_ok=True)
        observed.to_csv(a.csv,index=False)
        result["observed_pair_derivative_sha256"]=hashlib.sha256(a.csv.read_bytes()).hexdigest()
    except Exception as exc:
        result.update(error_type=type(exc).__name__,error=str(exc)[:350])
    a.json.parent.mkdir(parents=True,exist_ok=True)
    a.json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
