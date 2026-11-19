#!/usr/bin/env python3
"""V17 strict ASI independent dated adjacent-season cross-guild support and conditional analysis."""
import argparse
from collections import Counter,defaultdict
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import audit_asi_2013_original_cosurvey_v16 as a

MIN_TRANSITIONS=20
MIN_SITES=10
MIN_REGIONS=3
MAX_DOY_DIFF=21

def phase_day(iso):
    y,m,d=[int(x) for x in iso.split("-")]
    try:
        # Canonical austral July1 -> next June30, leap issue guarded.
        ref=date(2000 if m>=7 else 2001,m,d)
        return (ref-date(2000,7,1)).days
    except ValueError:
        return None

def original_temporal_pairs(rows):
    # Only structural metadata used until predeclared support gates pass.
    groups=defaultdict(list)
    site_regions=defaultdict(set)
    for r in rows:
        v=a.eligible_metadata(r)
        if v is None:
            continue
        site,region,sp,season,day=v
        site_regions[site].add(region)
        groups[(site,region,season,day,sp)].append(r)
    ambiguous={s for s,regions in site_regions.items() if len(regions)>1}
    byevent=defaultdict(dict)
    for (site,region,season,day,sp),objects in groups.items():
        if site in ambiguous or len(objects)!=1:
            continue
        byevent[(site,region,season,day)][sp]=objects[0]
    pair_seasons=defaultdict(list)
    for (site,region,season,day),species in byevent.items():
        for p in sorted(a.PENGUINS & species.keys()):
            for f in sorted(a.FLYING & species.keys()):
                pair_seasons[(site,region,p,f,season)].append((day,species[p],species[f]))
    # Cannot pick the most favourable survey day within season.
    unique={k:items[0] for k,items in pair_seasons.items() if len(items)==1}
    transitions=[]
    gap_held=0
    for (site,region,p,f,year), (day,x,y) in unique.items():
        following=unique.get((site,region,p,f,year+1))
        if following is None:
            continue
        next_day,px,fy=following
        a_day=phase_day(day); b_day=phase_day(next_day)
        if a_day is None or b_day is None or abs(a_day-b_day)>MAX_DOY_DIFF:
            gap_held+=1
            continue
        transitions.append({"site":site,"region":region,"penguin":p,"flying":f,
                            "season":year,"source":(x,y,px,fy)})
    return transitions,{
        "original_source_rows":len(rows),
        "region_ambiguous_source_sites_excluded":len(ambiguous),
        "one_pair_season_co_survey_units":len(unique),
        "pair_season_multiple_original_days_removed":sum(len(v) for v in pair_seasons.values() if len(v)>1),
        "consecutive_season_pairings_but_date_off_by_more_than_21d":gap_held,
        "eligible_consecutive_same_site_species_pairs":len(transitions),
        "eligible_distinct_original_sites":len({z["site"] for z in transitions}),
        "eligible_original_regions":len({z["region"] for z in transitions}),
        "site_pair_transitions_by_region":dict(Counter(z["region"] for z in transitions)),
        "flying_partner_transitions":dict(Counter(z["flying"] for z in transitions)),
        "penguin_partner_transitions":dict(Counter(z["penguin"] for z in transitions)),
    }

def gate(meta):
    return (meta["eligible_consecutive_same_site_species_pairs"]>=MIN_TRANSITIONS and
            meta["eligible_distinct_original_sites"]>=MIN_SITES and
            meta["eligible_original_regions"]>=MIN_REGIONS)

def count_nests(raw):
    x=str(raw).strip().replace(",","")
    if not x or not x.replace(".","",1).isdigit():
        raise ValueError("invalid original source count text")
    n=float(x)
    if not math.isfinite(n) or n<0:
        raise ValueError("invalid original original nesting count magnitude")
    return n

def weighted_corr(rows, group="site"):
    if len(rows)<3:
        return None
    sizes=Counter(z[group] for z in rows)
    weights=[1/sizes[z[group]] for z in rows]
    scale=sum(weights)
    ax=sum(w*z["penguin_growth"] for w,z in zip(weights,rows))/scale
    ay=sum(w*z["flying_growth"] for w,z in zip(weights,rows))/scale
    varx=sum(w*(z["penguin_growth"]-ax)**2 for w,z in zip(weights,rows))
    vary=sum(w*(z["flying_growth"]-ay)**2 for w,z in zip(weights,rows))
    if varx<=1e-10 or vary<=1e-10:
        return None
    cov=sum(w*(z["penguin_growth"]-ax)*(z["flying_growth"]-ay) for w,z in zip(weights,rows))
    return float(cov/math.sqrt(varx*vary))

def measure(original_transitions):
    d=[]
    invalid=0
    for v in original_transitions:
        try:
            pp,ff,nextpp,nextff=[count_nests(r["Count"]) for r in v["source"]]
        except (ValueError,TypeError):
            invalid+=1
            continue
        d.append({k:v[k] for k in ("site","region","penguin","flying","season")} |
                 {"penguin_growth":math.log1p(nextpp)-math.log1p(pp),
                  "flying_growth":math.log1p(nextff)-math.log1p(ff)})
    support={"numeric_count_transitions":len(d),
             "invalid_original_nest_count_transitions_excluded":invalid,
             "numeric_valid_distinct_sites":len({z["site"] for z in d}),
             "numeric_valid_distinct_regions":len({z["region"] for z in d})}
    if not (len(d)>=MIN_TRANSITIONS and support["numeric_valid_distinct_sites"]>=MIN_SITES
            and support["numeric_valid_distinct_regions"]>=MIN_REGIONS):
        return {**support,"status":"HOLD_NUMERIC_NEST_SUPPORT", "ecological_effect_fitted":False}
    sites=sorted({z["site"] for z in d})
    bysite={s:[x for x in d if x["site"]==s] for s in sites}
    rng=random.Random(20261020)
    boots=[]
    for _ in range(300):
        records=[]
        for i in range(len(sites)):
            source=rng.choice(sites)
            records.extend({**z,"boot_site":str(i)} for z in bysite[source])
        val=weighted_corr(records,"boot_site")
        if val is not None:
            boots.append(val)
    boots.sort()
    def quantile(x,q):
        if not x:return None
        return x[max(0,min(len(x)-1,int(q*(len(x)-1))))]
    regions=sorted({z["region"] for z in d})
    nsign=sum(z["penguin_growth"]*z["flying_growth"]>0 for z in d)
    nonzero=sum(z["penguin_growth"]!=0 and z["flying_growth"]!=0 for z in d)
    return {
        **support,
        "status":"EXPLORATORY_ASI_CONDITIONAL_CROSSGUILD_COVARIATION",
        "ecological_effect_fitted":True,
        "equal_original_site_weighted_growth_correlation":weighted_corr(d),
        "bootstrap_90pct_interval":[quantile(boots,.05),quantile(boots,.95)],
        "bootstrap_finite_replicates":len(boots),
        "omit_one_region_out_correlation":{
            region:weighted_corr([z for z in d if z["region"]!=region]) for region in regions},
        "positive_same_sign_growth_pairs":nsign,
        "nonzero_growth_in_both_taxa_pairs":nonzero,
        "same_sign_given_both_nonzero":nsign/nonzero if nonzero else None,
        "causal_marine_or_island_mechanism_identified":False,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    receipt={"status":"HOLD_ORIGINAL_SOURCE","ecological_effect_fitted":False}
    try:
        original,canonical=a.fetch_original()
        transitions,meta=original_temporal_pairs(a.parse_original(original))
        passed=gate(meta)
        receipt={"status":"V17_TEMPORAL_SUPPORT_CHECKED",
                 "original_publisher_md5":a.MD5,
                 "original_sha256":hashlib.sha256(original).hexdigest(),
                 "source_url":canonical,
                 "predeclared_support_gate_pass":bool(passed),
                 "structure":meta,
                 "model_gate":{ "min_transitions":MIN_TRANSITIONS,"min_site_IDs":MIN_SITES,
                                "min_regions":MIN_REGIONS,"max_survey_day_difference":MAX_DOY_DIFF},
                 "actual_island_boundary_independently_verified":False,
                 "independent_MAPPPD_population_replication":False,
                 "ecological_effect_fitted":False,
                 "scientific_decision":("STOP_NO_GENERALIZABLE_CROSSGUILD_ANNUAL_SUPPORT"
                                        if not passed else "EXPLORE_ASSOCIATION_ONLY"),
                }
        if passed:
            effect=measure(transitions)
            receipt["measure"]=effect
            receipt["ecological_effect_fitted"]=effect["ecological_effect_fitted"]
            if not effect["ecological_effect_fitted"]:
                receipt["scientific_decision"]="HOLD_INVALID_OR_SPARSE_ORIGINAL_COUNT_VALUES"
    except Exception as exc:
        receipt["status"]="HOLD_ORIGINAL_SOURCE"
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:700]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_ORIGINAL_SOURCE":
        raise SystemExit(2)
if __name__=="__main__":
    main()
