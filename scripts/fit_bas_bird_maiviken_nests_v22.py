#!/usr/bin/env python3
"""V22 — original BAS Bird Island and main-South-Georgia Maiviken year pairing.

Hard metadata support gate before reading any bird count magnitudes. One
physical offshore island and one site on South Georgia's much larger main island.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, date
import hashlib
import io
import json
import math
from pathlib import Path
import re
from statistics import median, mean
from itertools import combinations
import audit_bas_south_georgia_source_v21 as v21

SHA_BIRD="b1abc3c3adacee3f277d481217aabe4206c7b592a81f1f0eb1a0ec20a64450d3"
SHA_MAIN="8eef8ba06b0f1e666041be38415cfcc70d16cdb07e72ca6db805d8b70631dc85"
YEAR_START=2009
YEAR_STOP=2019
MAX_DAY_DIFF=30
MIN_BIRD=3
MIN_META_YEARS=8
MIN_YEAR_WINDOWS=6

def rows_csv(raw):
    try:
        text=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text=raw.decode("latin-1")
    return list(csv.DictReader(io.StringIO(text,newline="")))

def parse_count_day(val):
    val=str(val or "").strip()
    for fmt in ("%d/%m/%Y","%Y-%m-%d","%d %b %Y","%d %B %Y","%Y/%m/%d"):
        try:
            return datetime.strptime(val,fmt).date()
        except ValueError:
            continue
    return None

def start_year(day):
    return day.year if day.month>=7 else day.year-1

def season_year(s):
    s=str(s or "").strip()
    if re.fullmatch(r"(?:19|20)\d{2}",s):
        return int(s)
    m=re.fullmatch(r"((?:19|20)\d{2})\s*[-/]\s*(\d{2}|\d{4})",s)
    if m and (int(m.group(2))==(int(m.group(1))+1)%100 or
              int(m.group(2))==int(m.group(1))+1):
        return int(m.group(1))
    return None

def phase(day):
    # July 1 = day zero; ISO zero length calendar aligned to austral season.
    try:
        ref=date(2000 if day.month>=7 else 2001,day.month,day.day)
        return (ref-date(2000,7,1)).days
    except ValueError:
        return None

def source_metadata_only(bird,maiviken):
    """Never inspect any numeric Number column before passing this stage."""
    # Source-only raw time-field diagnostics, including the source's actual
    # calendar lexical format. No bird, nest or chick Count field is read.
    original_bird_dates=[str(x.get("Date nests counted","")).strip() for x in bird
                         if str(x.get("Date nests counted","")).strip()]
    original_main_dates=[str(x.get("Date of nest count","")).strip() for x in maiviken
                         if str(x.get("Date of nest count","")).strip()]
    original_main_seasons=[str(x.get("Season","")).strip() for x in maiviken]
    source_date_diagnostics={
        "bird_first_calendar_labels":original_bird_dates[:6],
        "bird_last_calendar_labels":original_bird_dates[-6:],
        "bird_calendar_labels_parseable_all_years":sum(parse_count_day(x) is not None
                                                        for x in original_bird_dates),
        "maiviken_first_season_day_labels":list(zip(original_main_seasons,original_main_dates))[:8],
        "maiviken_calendar_labels_parseable":sum(parse_count_day(x) is not None
                                                   for x in original_main_dates),
        "maiviken_season_labels_parseable":sum(season_year(x) is not None
                                                for x in original_main_seasons),
        "no_biological_count_fields_inspected":True,
    }
    bird_rows=defaultdict(list)
    unknown_species=0
    for r in bird:
        sp=str(r.get("Species","")).lower().strip()
        if not ("gentoo" in sp or sp=="pygoscelis papua"):
            unknown_species+=1
            continue
        colony=str(r.get("Colony","")).strip()
        day=parse_count_day(r.get("Date nests counted"))
        if not colony or day is None:
            continue
        year=start_year(day)
        if YEAR_START<=year<=YEAR_STOP:
            bird_rows[(colony,year)].append((day,r))
    duplicates={k for k,vals in bird_rows.items() if len(vals)>1}
    bird_ok={k:v[0] for k,v in bird_rows.items() if len(v)==1}
    maiv_rows=defaultdict(list)
    for r in maiviken:
        year=season_year(r.get("Season"))
        d=parse_count_day(r.get("Date of nest count"))
        if year is not None and d is not None and year==start_year(d) and YEAR_START<=year<=YEAR_STOP:
            maiv_rows[year].append((d,r))
    main_dup={year for year,vals in maiv_rows.items() if len(vals)>1}
    main_ok={year:vals[0] for year,vals in maiv_rows.items() if len(vals)==1}
    candidate={}
    phase_missing=0
    stage_off=0
    for year,(main_day,mainrow) in main_ok.items():
        colonies={name:(d,r) for (name,y),(d,r) in bird_ok.items() if y==year}
        if len(colonies)<MIN_BIRD:
            continue
        phases=[phase(d) for d,_ in colonies.values()]
        mainphase=phase(main_day)
        if mainphase is None or any(p is None for p in phases):
            phase_missing+=1
            continue
        if abs(median(phases)-mainphase)>MAX_DAY_DIFF:
            stage_off+=1
            continue
        candidate[year]={"bird":colonies,"main":(main_day,mainrow)}
    windows=[]
    for y in sorted(candidate):
        if y+1 not in candidate:
            continue
        shared=sorted(set(candidate[y]["bird"]) & set(candidate[y+1]["bird"]))
        if len(shared)>=MIN_BIRD:
            windows.append((y,shared))
    qa={
        "bird_source_rows":len(bird),
        "maiviken_source_rows":len(maiviken),
        "bird_original_species_unrecognized_rows":unknown_species,
        "bird_original_duplicate_colony_year_groups_excluded":len(duplicates),
        "maiviken_original_duplicate_year_groups_excluded":len(main_dup),
        "bird_distinct_colonies_in_valid_source_metadata":len({n for n,y in bird_ok}),
        "maiviken_unambiguous_original_years":len(main_ok),
        "eligible_same_year_seasons":len(candidate),
        "eligible_same_year_start_years":sorted(candidate),
        "original_years_excluded_due_phase_gt30_days":stage_off,
        "original_years_excluded_due_invalid_phase":phase_missing,
        "eligible_consecutive_year_colonymatched_windows":len(windows),
        "windows_start_years":[y for y,_ in windows],
        "shared_bird_colonies_per_window":{str(y):len(names) for y,names in windows},
        "original_count_magnitudes_read":0,
        "original_source_calendar_lexical_diagnostics":source_date_diagnostics,
    }
    return candidate,windows,qa

def nested_support_pass(qa):
    return qa["eligible_same_year_seasons"]>=MIN_META_YEARS and qa["eligible_consecutive_year_colonymatched_windows"]>=MIN_YEAR_WINDOWS

def raw_count(s):
    """Only called *after* the metadata gate. Zero allowed; missing not zero."""
    x=str(s if s is not None else "").strip().replace(",","")
    if not re.fullmatch(r"\d+(?:\.\d+)?",x):
        return None
    f=float(x)
    return f if math.isfinite(f) and f>=0 else None

def pearson(xs,ys):
    if len(xs)!=len(ys) or len(xs)<3:
        return None
    dx=[x-mean(xs) for x in xs]
    dy=[y-mean(ys) for y in ys]
    sx=sum(x*x for x in dx)
    sy=sum(y*y for y in dy)
    if sx<=1e-12 or sy<=1e-12:
        return None
    return sum(x*y for x,y in zip(dx,dy))/math.sqrt(sx*sy)

def analyze_counts(candidate,windows):
    # Candidate metadata fixed. Read only the already selected, source-original
    # colony nest-count cells for years in the frozen source cohort.
    numeric={}
    errors=Counter()
    for year,value in candidate.items():
        maincount=raw_count(value["main"][1].get("Number of incubating nests"))
        if maincount is None:
            errors["maiviken_missing_or_text_count"]+=1
            continue
        b={}
        for colony,(_,r) in value["bird"].items():
            c=raw_count(r.get("Number of nests"))
            if c is not None:
                b[colony]=c
            else:
                errors["bird_missing_or_text_count"]+=1
        if len(b)>=MIN_BIRD:
            numeric[year]={"bird":b,"main":maincount}
    out=[]
    colony_growths=defaultdict(dict)
    for year,_ in windows:
        if year not in numeric or year+1 not in numeric:
            continue
        shared=sorted(set(numeric[year]["bird"]) & set(numeric[year+1]["bird"]))
        if len(shared)<MIN_BIRD:
            continue
        g=[math.log1p(numeric[year+1]["bird"][c])-math.log1p(numeric[year]["bird"][c]) for c in shared]
        for colony,change in zip(shared,g):
            colony_growths[colony][year]=change
        out.append({"year":year,"bird":mean(g),
                    "main":math.log1p(numeric[year+1]["main"])-math.log1p(numeric[year]["main"]),
                    "colonies":len(shared)})
    support={
        "original_common_years_numeric_valid":len(numeric),
        "original_matched_yearly_growth_windows_numeric_valid":len(out),
        "nested_Bird_colony_count_values_not_independent_islands":True,
        "missing_source_count_diagnostics":dict(errors),
    }
    if len(numeric)<MIN_META_YEARS or len(out)<MIN_YEAR_WINDOWS:
        return {"status":"HOLD_NUMERIC_COMMON_YEAR_SUPPORT","ecological_effect_fitted":False,**support}
    xs=[r["bird"] for r in out]
    ys=[r["main"] for r in out]
    r=pearson(xs,ys)
    loo=[pearson(xs[:i]+xs[i+1:],ys[:i]+ys[i+1:]) for i in range(len(xs))]
    loo=[v for v in loo if v is not None]
    concordant=sum(x*y>0 for x,y in zip(xs,ys))
    nonzero=sum(x!=0 and y!=0 for x,y in zip(xs,ys))
    within=[]
    for a,b in combinations(sorted(colony_growths),2):
        years=sorted(set(colony_growths[a]) & set(colony_growths[b]))
        if len(years)>=MIN_YEAR_WINDOWS:
            z=pearson([colony_growths[a][yr] for yr in years],
                      [colony_growths[b][yr] for yr in years])
            if z is not None:within.append(z)
    return {
        "status":"DESCRIPTIVE_BAS_ISLAND_MAIN_ISLAND_NEST_GROWTH_ASSOCIATION",
        "ecological_effect_fitted":True,
        **support,
        "source_matched_growth_years":[r["year"] for r in out],
        "original_within_Bird_colony_roster":sorted(colony_growths),
        "coastal_small_island_vs_large_main_island_growth_pearson_r":r,
        "leave_one_year_out_r_range":[min(loo),max(loo)] if loo else None,
        "same_direction_annual_growth_windows":concordant,
        "nonzero_both_change_windows":nonzero,
        "proportion_same_direction_given_nonzero":concordant/nonzero if nonzero else None,
        "within_Bird_colony_pair_r_median":median(within) if within else None,
        "within_Bird_colony_pairs_with_ge6_common_years":len(within),
        "comparison_is_single_island_boundary":True,
        "regional_wind_ice_prey_mechanism_estimated":False,
        "ecology_generalized_to_other_islands":False,
        "no_biological_p_value":True,
        "scientific_decision":"DESCRIPTIVE_SINGLE_ISLAND_BOUNDARY_ASSOCIATION_CAUSAL_HOLD",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report={"status":"SOURCE_HOLD","ecological_effect_fitted":False}
    try:
        orig={}
        for key,spec in v21.SOURCES.items():
            data,receipt=v21.get_raw(spec["url"])
            expected={"bird_island_v1":SHA_BIRD,"south_georgia_maiviken":SHA_MAIN}[key]
            if receipt["sha256"]!=expected:
                raise ValueError("SOURCE_STOP original BAS SHA drift "+key)
            orig[key]=rows_csv(data)
        candidate,windows,qa=source_metadata_only(orig["bird_island_v1"],orig["south_georgia_maiviken"])
        ok=nested_support_pass(qa)
        report={"status":"V22_METADATA_SUPPORT_COMPLETED",
                "bird_original_sha256":SHA_BIRD,
                "maiviken_original_sha256":SHA_MAIN,
                "original_metadata_support":qa,
                "metadata_support_gate_pass":bool(ok),
                "ecological_effect_fitted":False,
                "scientific_decision":"STOP_INSUFFICIENT_SOURCE_PHASE_AND_COLONY_YEAR_SUPPORT" if not ok else "HOLD_COUNT_VALUES_UNTIL_VERIFIED",
               }
        if ok:
            effect=analyze_counts(candidate,windows)
            report["descriptive_model"]=effect
            report["ecological_effect_fitted"]=bool(effect["ecological_effect_fitted"])
            report["scientific_decision"]=effect.get("scientific_decision",effect["status"])
    except Exception as exc:
        report["status"]="SOURCE_HOLD"
        report["error_type"]=type(exc).__name__
        report["error"]=str(exc)[:500]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"]=="SOURCE_HOLD":
        raise SystemExit(2)
if __name__=="__main__":
    main()
