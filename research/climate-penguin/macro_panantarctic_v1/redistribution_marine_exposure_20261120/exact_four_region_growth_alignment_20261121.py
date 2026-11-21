#!/usr/bin/env python3
"""Exhaustive 24 assignments of four observed reporting-region growth ratios.

Frozen diagnostic in FROZEN_FOUR_REGION_GROWTH_ALIGNMENT_DIAGNOSTIC_20261121_JA.md.
NOT a causal permutation p value: the regions are not exchangeable.
Only original 23 SIC-complete vs nested 17 three-variable-complete sites.
"""
import csv
import itertools
import json
import math
from pathlib import Path

from recompute_parent23_vs_complete17_SIC_region_sensitivity_20261121 import (
    load, decompose, close,
)

HERE = Path(__file__).resolve().parent
INPUT = HERE / "matched_support.csv"
OLD17 = HERE / "REGIONAL_SORTING_NULL_RESULT_20261121.json"
OLD23 = HERE / "parent_roster_support_diagnostic.csv"
OUT = HERE / "FOUR_REGION_GROWTH_ASSIGNMENT_EXACT24_20261121.json"
TABLE = HERE / "FOUR_REGION_GROWTH_ASSIGNMENT_EXACT24_20261121.csv"
FIELDS = ("nest_reallocation_component_pp", "between_region_pp", "within_region_pp")
REGIONS = (
    "Adelie Land", "Central-west Antarctic Peninsula",
    "South Shetland Islands", "Victoria Land",
)


def quantile(v,p):
    a=sorted(v)
    i=(len(a)-1)*p
    lo,hi=math.floor(i),math.ceil(i)
    if lo==hi:
        return a[lo]
    return a[lo]*(hi-i)+a[hi]*(i-lo)


def exact_assignments(cohort, label):
    groups = {reg:[x for x in cohort if x["source_region"]==reg] for reg in REGIONS}
    assert sorted({x["source_region"] for x in cohort})==list(REGIONS)
    assert all(len(v) for v in groups.values())
    totals={}
    for reg,rs in groups.items():
        n0=sum(float(x["n0"]) for x in rs)
        n1=sum(float(x["n1"]) for x in rs)
        assert n0>0 and n1>0
        totals[reg]={"n0":n0,"n1":n1,"g":n1/n0,"sites":len(rs)}
    original=decompose(cohort)
    assignments=[]
    for perm in itertools.permutations(REGIONS):
        altered=[]
        for idx,reg in enumerate(REGIONS):
            late_total = totals[reg]["n0"]*totals[perm[idx]]["g"]
            for x in groups[reg]:
                rr=dict(x)
                rr["n1"]=late_total * float(x["n1"])/totals[reg]["n1"]
                altered.append(rr)
        d=decompose(altered)
        close(d["nest_reallocation_component_pp"],
              d["between_region_pp"]+d["within_region_pp"],"every exact 4! accounting")
        assignments.append({
            "cohort":label,
            "assignment": " | ".join(perm),
            "identity":perm==REGIONS,
            "R_pp":d["nest_reallocation_component_pp"],
            "between_region_pp":d["between_region_pp"],
            "within_region_pp":d["within_region_pp"],
        })
    assert len(assignments)==24
    identity=[x for x in assignments if x["identity"]]
    assert len(identity)==1
    for k,c in [("R_pp","nest_reallocation_component_pp"),
                ("between_region_pp","between_region_pp"),
                ("within_region_pp","within_region_pp")]:
        close(identity[0][k],original[c],"observed 4region identity="+k)
    b=[x["between_region_pp"] for x in assignments]
    b_obs=identity[0]["between_region_pp"]
    median=quantile(b,.5)
    n_ge=sum(x>=b_obs-1e-10 for x in b)
    n_gt=sum(x>b_obs+1e-10 for x in b)
    stat={
        "original_observed":{k:original[k] for k in FIELDS},
        "source_region_totals":totals,
        "permutation_count":24,
        "positive_between_count":sum(x>0 for x in b),
        "positive_between_fraction":sum(x>0 for x in b)/24,
        "between_ge_observed_count_including_identity":n_ge,
        "between_ge_observed_fraction_not_p_value":n_ge/24,
        "between_rank_from_highest_with_ties":n_gt+1,
        "between_values":{
            "min":min(b),"q025":quantile(b,.025),"median":median,
            "q975":quantile(b,.975),"max":max(b),
        },
        "between_median_centered_abs_tail_fraction_not_p_value":
            sum(abs(x-median)>=abs(b_obs-median)-1e-10 for x in b)/24,
        "conditional_desc":"Fixed original baseline sites, exposure, region; only the four regional growth-rate labels were permuted. This is not a probability under an ecological randomization design.",
        "all24":assignments,
    }
    for k in ("R_pp","within_region_pp"):
        v=[x[k] for x in assignments]
        stat[k+"_range"]={"min":min(v),"median":quantile(v,.5),"max":max(v)}
    return stat


def main():
    raw=[x for x in load(INPUT) if x["comparison"]=="long" and x["radius"]=="0"]
    assert len(raw)==23 and len(set(x["site_id"] for x in raw))==23
    assert {x["site_id"] for x in raw if float(x["n0"])==0.0}=={"PLEN"}
    assert float(next(x for x in raw if x["site_id"]=="PLEN")["n1"])==0.0
    complete=[x for x in raw if all(x[k] for k in ("salinity0","salinity1","sst_C0","sst_C1"))]
    assert len(complete)==17
    parent=exact_assignments(raw,"parent23_sic_only")
    m17=exact_assignments(complete,"complete17_glorys")

    old23=[x for x in load(OLD23) if x["comparison"]=="long" and x["radius"]=="0" and x["variable"]=="sic_pp"]
    assert len(old23)==1
    close(parent["original_observed"]["nest_reallocation_component_pp"],
          float(old23[0]["redistribution"]),"original parent source R")
    old17=json.loads(OLD17.read_text(encoding="utf8"))["results"]["sic_pp"]["observed"]
    for k,name in [("nest_reallocation_component_pp","total"),
                   ("between_region_pp","between"),
                   ("within_region_pp","within")]:
        close(m17["original_observed"][k],old17[name],"original17:"+k)

    rows=parent.pop("all24")+m17.pop("all24")
    with TABLE.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["cohort","assignment","identity","R_pp","between_region_pp","within_region_pp"])
        w.writeheader()
        w.writerows(rows)
    report={
        "status":"FOUR_REGION_GROWTH_LABEL_ENUMERATION_CONDITIONAL_NOT_CAUSAL",
        "freeze":"FROZEN_FOUR_REGION_GROWTH_ALIGNMENT_DIAGNOSTIC_20261121_JA.md",
        "source":"matched_support.csv; parent_roster_support_diagnostic.csv; REGIONAL_SORTING_NULL_RESULT_20261121.json",
        "periods":["1993–2000","2011–2020"],
        "source_regions_alphabetical":list(REGIONS),
        "parent23":parent,"complete17":m17,
        "not_an_inferential_p_value":True,
        "post_outcome_frozen":True,
        "no_adaptive_tracking_or_warming_causation":True,
    }
    assert parent["between_rank_from_highest_with_ties"]>=1
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps({
        "status":report["status"],
        "parent23":{
            "observed_between":parent["original_observed"]["between_region_pp"],
            "rank_high":parent["between_rank_from_highest_with_ties"],
            "tail_count":parent["between_ge_observed_count_including_identity"],
            "n_perms":24,
            "positive_between_count":parent["positive_between_count"],
            "range":parent["between_values"],
        },
        "complete17":{
            "observed_between":m17["original_observed"]["between_region_pp"],
            "rank_high":m17["between_rank_from_highest_with_ties"],
            "tail_count":m17["between_ge_observed_count_including_identity"],
            "n_perms":24,
            "positive_between_count":m17["positive_between_count"],
            "range":m17["between_values"],
        },
        "not_an_inferential_p_value":True,
        "post_result":True,
    },ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
