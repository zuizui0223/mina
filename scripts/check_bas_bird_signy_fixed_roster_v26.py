#!/usr/bin/env python3
"""V26: BAS original fixed-baseline Bird colony subset and observational-stage QA.

Post-result sampling-roster diagnostic. Does not identify a sea-ice or island mechanism.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
from pathlib import Path
from statistics import mean,median
import audit_bas_south_georgia_source_v21 as v21
import fit_bas_bird_maiviken_nests_v22 as v22
import compare_bas_gentoo_near_far_v23 as v23
import compare_bas_bird_signy_longterm_v25 as v25

EXPECTED_V25_ALL=0.165616495725728
EXPECTED_V25_SHORT=-0.33420933224382615
MIN_WINDOWS=24
MIN_EARLY=8
MIN_MODERN=12
SPLIT_YEAR=1997

def frozen_baseline_roster(windows):
    first=min(windows) if windows else None
    if first!=1982:
        raise ValueError("SOURCE_STOP historical 1982 first monitoring interval missing")
    baseline=tuple(sorted(windows[first]))
    if len(baseline)<v25.MIN_BIRD_COLONIES:
        raise ValueError("SOURCE_STOP initial original roster has fewer than 5 colonies")
    if not set(baseline).issubset(set(v25.FIXED_COLONIES)):
        raise ValueError("SOURCE_STOP source colony not part of original V25 candidate roster")
    return baseline

def candidate_fixed_windows(bird,signy,windows,baseline):
    """Source row identities ONLY; no biological outcome columns read."""
    good={}
    for year in sorted(windows):
        if year not in signy or year+1 not in signy:
            continue
        if all((c,year) in bird and (c,year+1) in bird for c in baseline):
            good[year]=list(baseline)
    qa={
        "baseline_years":[1982,1983],
        "fixed_original_bird_colonies":list(baseline),
        "baseline_colony_count":len(baseline),
        "eligible_fixed_roster_metadata_windows":len(good),
        "metadata_start_years":sorted(good),
        "metadata_pre_1997_windows":sum(y<SPLIT_YEAR for y in good),
        "metadata_at_after_1997_windows":sum(y>=SPLIT_YEAR for y in good),
        "original_Bird_nest_or_Signy_pair_count_values_read":False,
    }
    return good,qa

def stage_date_diagnostics(bird,signy,window_years,baseline):
    """Source exact census dates: not used to choose effect windows."""
    by_period={"earlier":{"parsed":0,"unparseable_or_missing":0,"gaps":[]},
               "modern":{"parsed":0,"unparseable_or_missing":0,"gaps":[]}}
    for year in sorted(window_years):
        if year not in signy:
            continue
        period="earlier" if year<SPLIT_YEAR else "modern"
        original_signy_day=v22.parse_count_day(signy[year].get("DATE_PAIR_COUNT"))
        original_bird_days=[
            v22.parse_count_day(bird[(c,year)].get("Date nests counted"))
            for c in baseline if (c,year) in bird
        ]
        if (original_signy_day is None or not original_bird_days
                or any(day is None for day in original_bird_days)):
            by_period[period]["unparseable_or_missing"]+=1
            continue
        bird_phases=[v22.phase(d) for d in original_bird_days]
        signy_phase=v22.phase(original_signy_day)
        if signy_phase is None or any(x is None for x in bird_phases):
            by_period[period]["unparseable_or_missing"]+=1
            continue
        gap=abs(float(median(bird_phases))-float(signy_phase))
        by_period[period]["parsed"]+=1
        by_period[period]["gaps"].append(gap)
    output={}
    for group,vals in by_period.items():
        gaps=vals.pop("gaps")
        output[group]={
            "parseable_years_with_count_dates":vals["parsed"],
            "unparseable_or_missing_years":vals["unparseable_or_missing"],
            "median_absolute_source_count_phase_day_difference":median(gaps) if gaps else None,
            "years_with_source_phase_day_gap_ge30":sum(g>=30 for g in gaps),
            "years_with_source_phase_day_gap_ge60":sum(g>=60 for g in gaps),
        }
    return {
        "source_original_Signy_column":"DATE_PAIR_COUNT",
        "original_Bird_column":"Date nests counted",
        "no_source_dates_used_as_outcome_selection":True,
        "original_date_comparability_by_period":output,
    }

def numeric_fixed_roster(bird,signy,fixed,baseline):
    """Call only after *metadata* cohort passes fixed eligibility."""
    observations={}
    errors=Counter()
    for year in sorted(fixed):
        signy0=v22.raw_count(signy[year].get("TOTAL_NUMBER_OF_PAIRS"))
        signy1=v22.raw_count(signy[year+1].get("TOTAL_NUMBER_OF_PAIRS"))
        if signy0 is None or signy1 is None:
            errors["unknown_Signy_original_pair_count"]+=1
            continue
        bvalues=[]
        for colony in baseline:
            n0=v22.raw_count(bird[(colony,year)].get("Number of nests"))
            n1=v22.raw_count(bird[(colony,year+1)].get("Number of nests"))
            if n0 is None or n1 is None:
                errors["unknown_Bird_baseline_colony_original_nest_count"]+=1
                bvalues=[]
                break
            bvalues.append(math.log1p(n1)-math.log1p(n0))
        if len(bvalues)!=len(baseline):
            continue
        observations[year]={
            "bird":float(mean(bvalues)),
            "signy":math.log1p(signy1)-math.log1p(signy0),
        }
    return observations,dict(errors)

def describe(observations):
    years=sorted(observations)
    earlier=[year for year in years if year<SPLIT_YEAR]
    modern=[year for year in years if year>=SPLIT_YEAR]
    overview={
        "n_numeric_windows":len(years),
        "original_window_start_years":years,
        "n_earlier_windows":len(earlier),
        "n_modern_windows":len(modern),
        "frozen_minimum_windows":MIN_WINDOWS,
        "frozen_minimum_earlier":MIN_EARLY,
        "frozen_minimum_modern":MIN_MODERN,
    }
    if len(years)<MIN_WINDOWS or len(earlier)<MIN_EARLY or len(modern)<MIN_MODERN:
        return {**overview,"status":"HOLD_INSUFFICIENT_FIXED_ROSTER_NUMERIC_SUPPORT",
                "effect_computed":False}
    def one_group(source_years):
        x=[observations[y]["bird"] for y in source_years]
        z=[observations[y]["signy"] for y in source_years]
        r=v22.pearson(x,z)
        if r is None:
            return {"n_windows":len(source_years),"pearson_r":None}
        loo=[]
        for k in range(len(source_years)):
            a=v22.pearson(x[:k]+x[k+1:],z[:k]+z[k+1:])
            if a is not None:loo.append(a)
        nnonzero=sum(a!=0 and b!=0 for a,b in zip(x,z))
        nsign=sum(a*b>0 for a,b in zip(x,z))
        return {"n_windows":len(source_years),"pearson_r":r,
                "leave_one_window_out_min_max":[min(loo),max(loo)] if loo else None,
                "same_direction_windows":nsign,
                "both_nonzero_windows":nnonzero,
                "same_direction_fraction":nsign/nnonzero if nnonzero else None}
    results={"full_source_history":one_group(years),
             "source_start_before_1997":one_group(earlier),
             "source_start_at_or_after_1997":one_group(modern)}
    old=results["source_start_before_1997"]["pearson_r"]
    new=results["source_start_at_or_after_1997"]["pearson_r"]
    if old is None or new is None:
        return {**overview,"status":"HOLD_FIXED_ROSTER_ZERO_VARIANCE",
                "effect_computed":False,"descriptive_statistics":results}
    return {
        **overview,
        "status":"V26_ORIGINAL_BASELINE_COLONY_PANEL_ASSOCIATION",
        "effect_computed":True,
        "descriptive_statistics":results,
        "earlier_minus_modern_correlation_difference":old-new,
        "old_positive_new_negative_same_sign_pattern":bool(old>0 and new<0),
        "source_islands":2,
        "phase_difference_is_necessarily_ecological":False,
        "contribution_of_changing_colony_roster_fully_isolated":False,
        "biotic_or_climatic_causal_effect_identified":False,
        "no_biological_p_value":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",type=Path,required=True)
    a=p.parse_args()
    result={"status":"HOLD_ORIGINAL_SOURCE","effect_computed":False}
    try:
        rawbird,metadata=v21.get_raw(v21.SOURCES["bird_island_v1"]["url"])
        if metadata["sha256"]!=v22.SHA_BIRD:
            raise ValueError("SOURCE_STOP Bird historical V1 raw SHA drift")
        rawsigny,metadata=v21.get_raw(v23.SIGNY_URL)
        if metadata["sha256"]!=v23.SIGNY_SHA:
            raise ValueError("SOURCE_STOP Signy original raw SHA drift")
        b,s,w,qa=v25.metadata_cohort(v22.rows_csv(rawbird),v22.rows_csv(rawsigny))
        if len(w)<v25.MIN_STRUCTURAL_WINDOWS:
            raise ValueError("SOURCE_STOP original V25 source structure insufficient")
        growth,invalid=v25.numeric_growth(b,s,w)
        original=v25.describe(growth)
        if (not original.get("effect_computed")
            or abs(original["full_historical_bird_signy_pearson_r"]-EXPECTED_V25_ALL)>1e-10
            or abs(original["short_V23_bird_signy_r_reproduced"]-EXPECTED_V25_SHORT)>1e-10):
            raise ValueError("SOURCE_STOP original V25 numerical receipt not reproduced exactly")
        baseline=frozen_baseline_roster(w)
        fixed,fixedqa=candidate_fixed_windows(b,s,w,baseline)
        metadata_gate=(fixedqa["eligible_fixed_roster_metadata_windows"]>=MIN_WINDOWS
            and fixedqa["metadata_pre_1997_windows"]>=MIN_EARLY
            and fixedqa["metadata_at_after_1997_windows"]>=MIN_MODERN)
        dates=stage_date_diagnostics(b,s,list(w),baseline)
        result={
            "status":"V26_BASELINE_COLONY_SOURCE_SUPPORT_COMPLETED",
            "source_sha256":{"BirdIsland_V1":v22.SHA_BIRD,"Signy":v23.SIGNY_SHA},
            "frozen_contract":"contracts/BAS_BIRD_SIGNY_FIXED_ROSTER_V26.md",
            "original_V25_reproduced_full_33window_r":original["full_historical_bird_signy_pearson_r"],
            "original_V23_reproduced_short_8window_r":original["short_V23_bird_signy_r_reproduced"],
            "original_V25_numeric_windows":len(growth),
            "fixed_roster_source_metadata":fixedqa,
            "monitoring_date_only_diagnostics":dates,
            "source_metadata_gate_pass":metadata_gate,
            "effect_computed":False,
            "scientific_decision":("HOLD_FIXED_SOURCE_BASELINE_ROSTER_SUPPORT"
                                   if not metadata_gate else "ORIGINAL_COUNT_CHECK_PENDING")
        }
        if metadata_gate:
            obs,exclusions=numeric_fixed_roster(b,s,fixed,baseline)
            output=describe(obs)
            result["source_numeric_diagnostics"]=exclusions
            result["fixed_roster_effect"]=output
            result["effect_computed"]=bool(output["effect_computed"])
            result["scientific_decision"]=(
                "EXPLORATORY_FIXED_ROSTER_PERIOD_ASSOCIATION_CAUSAL_HOLD"
                if output["effect_computed"] else output["status"])
    except Exception as exc:
        result["status"]="HOLD_ORIGINAL_SOURCE"
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:850]
    a.json.parent.mkdir(parents=True,exist_ok=True)
    a.json.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]=="HOLD_ORIGINAL_SOURCE":
        raise SystemExit(2)

if __name__=="__main__":
    main()
