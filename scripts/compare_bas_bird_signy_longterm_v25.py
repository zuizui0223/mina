#!/usr/bin/env python3
"""V25 long-horizon original BAS Gentoo Bird Island–Signy colony growth check.

Exploratory after observed negative 2011-2018 V23 coefficient. Never infer causation.
"""
from __future__ import annotations
import argparse
from collections import defaultdict,Counter
import json
import math
from pathlib import Path
from statistics import mean
import audit_bas_south_georgia_source_v21 as v21
import fit_bas_bird_maiviken_nests_v22 as v22
import compare_bas_gentoo_near_far_v23 as v23

FIRST=1982
LAST=2019
MIN_STRUCTURAL_WINDOWS=20
MIN_BIRD_COLONIES=5
MIN_POST_STANDARD_WINDOWS=12
MIN_PRE_STANDARD_WINDOWS=8
SHORT_EPOCH_YEARS=tuple(range(2011,2019))
V23_BIRD_SIGNY_R=-0.33420933224382615
FIXED_COLONIES=(
    "Johnson","Landing Beach","Lower Mountain Cwm",
    "Lower Natural Arch","Square Pond","Upper Mountain Cwm",
    "Upper Natural Arch"
)

def metadata_cohort(bird,signy):
    bird_rows=defaultdict(list)
    missing_bird_day=0
    for row in bird:
        sp=str(row.get("Species","")).lower()
        colony=str(row.get("Colony","")).strip()
        if "gentoo" not in sp and "pygoscelis papua" not in sp:
            continue
        if colony not in FIXED_COLONIES:
            continue
        dt=v22.parse_count_day(row.get("Date nests counted"))
        if dt is None:
            missing_bird_day+=1
            continue
        year=v22.start_year(dt)
        if FIRST<=year<=LAST:
            bird_rows[(colony,year)].append(row)
    duplicates_bird={key for key,v in bird_rows.items() if len(v)>1}
    bird_single={key:r[0] for key,r in bird_rows.items() if len(r)==1}
    signy_rows=defaultdict(list)
    bad_signy_label=0
    for row in signy:
        species=str(row.get("SPECIES","")).strip().lower()
        if "gentoo" not in species and "pygoscelis papua" not in species:
            continue
        year=v22.season_year(row.get("SEASON"))
        if year is None:
            bad_signy_label+=1
            continue
        if FIRST<=year<=LAST:
            signy_rows[year].append(row)
    duplicates_signy={yr for yr,rows in signy_rows.items() if len(rows)>1}
    signy_single={yr:rows[0] for yr,rows in signy_rows.items() if len(rows)==1}
    years=sorted(set(k[1] for k in bird_single) & set(signy_single))
    windows={}
    for yr in years:
        if yr+1 not in signy_single:
            continue
        colon0={k[0] for k in bird_single if k[1]==yr}
        colon1={k[0] for k in bird_single if k[1]==yr+1}
        common=sorted(colon0 & colon1)
        if len(common)>=MIN_BIRD_COLONIES:
            windows[yr]=common
    qa={
        "original_Bird_source_rows":len(bird),
        "original_Signy_source_rows":len(signy),
        "fixed_known_Bird_colony_roster":list(FIXED_COLONIES),
        "bird_unparseable_calendar_source_rows":missing_bird_day,
        "bird_original_duplicate_colony_season_groups_dropped":len(duplicates_bird),
        "signy_invalid_original_season_labels":bad_signy_label,
        "signy_duplicate_original_season_groups_dropped":len(duplicates_signy),
        "unambiguous_Signy_years_in_preset_period":len(signy_single),
        "bird_unique_valid_colony_years":len(bird_single),
        "eligible_candidate_adjacent_bird_signy_year_windows":len(windows),
        "eligible_annual_window_start_years":sorted(windows),
        "matched_original_colonies_by_interval":{str(y):len(s) for y,s in windows.items()},
        "no_nesting_count_magnitudes_used_before_gate":True,
    }
    return bird_single,signy_single,windows,qa

def numeric_growth(bird,signy,windows):
    result={}
    errors=Counter()
    for year,colonies in windows.items():
        s0=v22.raw_count(signy[year].get("TOTAL_NUMBER_OF_PAIRS"))
        s1=v22.raw_count(signy[year+1].get("TOTAL_NUMBER_OF_PAIRS"))
        if s0 is None or s1 is None:
            errors["unknown_original_Signy_pair_count"]+=1
            continue
        vals=[]
        for colony in colonies:
            b0=v22.raw_count(bird[(colony,year)].get("Number of nests"))
            b1=v22.raw_count(bird[(colony,year+1)].get("Number of nests"))
            if b0 is None or b1 is None:
                errors["unknown_original_Bird_colony_nests"]+=1
                continue
            vals.append(math.log1p(b1)-math.log1p(b0))
        if len(vals)<MIN_BIRD_COLONIES:
            errors["fewer_than_five_numeric_same_colonies"]+=1
            continue
        result[year]={
            "bird":float(mean(vals)),
            "signy":math.log1p(s1)-math.log1p(s0),
            "matched_colonies":len(vals)
        }
    return result,dict(errors)

def describe(growth):
    years=sorted(growth)
    if len(years)<MIN_STRUCTURAL_WINDOWS:
        return {"status":"STOP_FEWER_THAN_20_NUMERIC_GROWTH_WINDOWS",
                "effect_computed":False,"n_numeric_windows":len(years)}
    def r_of(yy):
        return v22.pearson([growth[y]["bird"] for y in yy],
                           [growth[y]["signy"] for y in yy])
    short=list(SHORT_EPOCH_YEARS)
    if not all(y in growth for y in short):
        return {"status":"STOP_V23_SHORT_YEAR_ROSTER_NOT_REPRODUCIBLE",
                "effect_computed":False,"n_numeric_windows":len(years)}
    observed_short=r_of(short)
    if observed_short is None or abs(observed_short-V23_BIRD_SIGNY_R)>1e-10:
        return {"status":"STOP_ORIGINAL_V23_SHORT_EFFECT_NOT_REPRODUCED",
                "effect_computed":False,"n_numeric_windows":len(years),
                "source_recheck_required":True}
    total=r_of(years)
    if total is None:
        return {"status":"STOP_ORIGINAL_HISTORICAL_ZERO_VARIANCE",
                "effect_computed":False,"n_numeric_windows":len(years)}
    old=[y for y in years if y<1997]
    modern=[y for y in years if y>=1997]
    oldr=r_of(old) if len(old)>=MIN_PRE_STANDARD_WINDOWS else None
    modernr=r_of(modern) if len(modern)>=MIN_POST_STANDARD_WINDOWS else None
    loo=[r_of([y for y in years if y!=excluded]) for excluded in years]
    loo=[x for x in loo if x is not None and math.isfinite(x)]
    nonzero=sum(growth[y]["bird"]!=0 and growth[y]["signy"]!=0 for y in years)
    same=sum(growth[y]["bird"]*growth[y]["signy"]>0 for y in years)
    return {
        "status":"HISTORICAL_BAS_ORIGINAL_BIRD_SIGNY_GENTOO_ANNUAL_ASSOCIATION",
        "effect_computed":True,
        "original_year_start_window_roster":years,
        "original_historical_adjacent_year_windows":len(years),
        "original_distinct_physical_islands":2,
        "full_historical_bird_signy_pearson_r":total,
        "short_V23_years":short,
        "short_V23_bird_signy_r_reproduced":observed_short,
        "pre_1997_1996p_CEMP_transition_start_year_windows":len(old),
        "pre_1997_r_if_ge8_windows":oldr,
        "post_1997_source_start_year_windows":len(modern),
        "post_1997_r_if_ge12_windows":modernr,
        "historical_leave_one_window_out_r_range":[min(loo),max(loo)] if loo else None,
        "full_history_same_growth_direction_windows":same,
        "full_history_both_nonzero_growth_windows":nonzero,
        "full_history_same_sign_fraction":same/nonzero if nonzero else None,
        "fixed_roster_Bird_colonies_not_independent_islands":True,
        "regional_climate_ice_wind_or_prey_causation_estimated":False,
        "no_biological_p_value":True,
        "scientific_decision":"EXPLORATORY_HISTORICAL_SIGNY_BIRD_SYNCHRONY_NO_CAUSAL_ISLAND_LAW"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",type=Path,required=True)
    args=p.parse_args()
    receipt={"status":"HOLD_ORIGINAL_SOURCES","effect_computed":False}
    try:
        first_spec=v21.SOURCES["bird_island_v1"]
        braw,bmeta=v21.get_raw(first_spec["url"])
        if bmeta["sha256"]!=v22.SHA_BIRD:
            raise ValueError("SOURCE_STOP Bird original V1 SHA drift")
        sraw,smeta=v21.get_raw(v23.SIGNY_URL)
        if smeta["sha256"]!=v23.SIGNY_SHA:
            raise ValueError("SOURCE_STOP Signy original SHA drift")
        birds=v22.rows_csv(braw)
        signy=v22.rows_csv(sraw)
        b,s,w,qa=metadata_cohort(birds,signy)
        valid=len(w)>=MIN_STRUCTURAL_WINDOWS
        receipt={
            "status":"V25_HISTORICAL_BAS_SOURCE_STRUCTURE_CHECKED",
            "frozen_contract":"contracts/BAS_BIRD_SIGNY_LONG_HORIZON_V25.md",
            "Bird_original_SHA256":v22.SHA_BIRD,
            "Signy_original_SHA256":v23.SIGNY_SHA,
            "original_Bird_Signy_source_metadata":qa,
            "predeclared_structural_20_window_gate":valid,
            "ecological_effect_computed":False,
            "scientific_decision":"STOP_INSUFFICIENT_HISTORICAL_ORIGINAL_SOURCE_SUPPORT" if not valid
                                  else "NUMERIC_ORIGINAL_SUPPORT_PENDING",
        }
        if valid:
            growth,problems=numeric_growth(b,s,w)
            result=describe(growth)
            receipt["source_count_eligibility_diagnostics"]=problems
            receipt["original_nesting_growth"]=result
            receipt["ecological_effect_computed"]=bool(result["effect_computed"])
            receipt["scientific_decision"]=result.get("scientific_decision",result["status"])
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:650]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_ORIGINAL_SOURCES":
        raise SystemExit(2)

if __name__=="__main__":
    main()
