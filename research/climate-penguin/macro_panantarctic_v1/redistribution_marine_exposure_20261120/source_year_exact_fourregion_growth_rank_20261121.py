#!/usr/bin/env python3
"""Frozen conditional source-census-year sensitivity of four-region ranks.

Post-result: source median rank 2/24 (23-site), 3/24 (17-site) already known.
Not a randomized ecological experiment, population confidence interval,
climate-driven adaptation test, or independent replicate.
"""
import csv
import itertools
import json
import math
import statistics
from pathlib import Path
from collections import defaultdict

from recompute_parent23_vs_complete17_SIC_region_sensitivity_20261121 import load, decompose, close
from resample_source_census_years_SIC23_vs17_20261121 import (
    xorshift32, records_by_site, historical_pairs, sample_median
)
from exact_four_region_growth_alignment_20261121 import REGIONS, quantile

HERE=Path(__file__).resolve().parent
INPUT=HERE/"matched_support.csv"
FROZEN=HERE/"FROZEN_FOUR_REGION_RANK_CENSUS_YEAR_SENSITIVITY_20261121_JA.md"
EXACT=HERE/"FOUR_REGION_GROWTH_ASSIGNMENT_EXACT24_20261121.json"
N=4999
SEED=20261121
OUT=HERE/"FOUR_REGION_RANK_SOURCE_YEAR_SENSITIVITY_20261121.json"
DRAWS=HERE/"FOUR_REGION_RANK_SOURCE_YEAR_SENSITIVITY_20261121.csv"
PERMS=list(itertools.permutations(range(4)))


def build_geometry(roster):
    data={}
    for reg in REGIONS:
        rs=[r for r in roster if r["source_region"]==reg]
        assert rs
        data[reg]=rs
    assert sum(len(rs) for rs in data.values())==len(roster)
    return data


def alignment_B(rows):
    """Return 24 B assignments using exact symmetric regional decomposition."""
    groups=build_geometry(rows)
    n0=[];g=[];e=[]
    for reg in REGIONS:
        group=groups[reg]
        N0=sum(float(x["n0"]) for x in group)
        N1=sum(float(x["n1"]) for x in group)
        assert N0>0 and N1>0
        ev=0
        for x in group:
            p0=float(x["n0"])/N0
            p1=float(x["n1"])/N1
            mid=(float(x["sic_pp0"])+float(x["sic_pp1"]))/2
            ev+=.5*(p0+p1)*mid
        n0.append(N0);g.append(N1/N0);e.append(ev)
    N0=sum(n0)
    values=[]
    for perm in PERMS:
        late=[n0[i]*g[perm[i]] for i in range(4)]
        N1=sum(late)
        B=sum((late[i]/N1 - n0[i]/N0)*e[i] for i in range(4))
        values.append(B)
    # tuple identity first in itertools.permutations(range(4))
    assert PERMS[0]==(0,1,2,3)
    return values


def summarize(values):
    a=sorted(values)
    return {
       "n":len(a),
       "q025":quantile(a,.025),"median":quantile(a,.5),
       "q975":quantile(a,.975),
       "mean":sum(a)/len(a),
       "min":a[0],"max":a[-1],
    }


def one_panel(rows):
    Bs=alignment_B(rows)
    observed=Bs[0]
    rank=1+sum(x>observed+1e-10 for x in Bs)
    greater_equal=sum(x>=observed-1e-10 for x in Bs)
    # Identical regional growth draws may create exact ties; keep the best rank
    # and the inclusive upper-tail count as distinct descriptive quantities.
    assert len(Bs)==24 and 1<=rank<=greater_equal<=24
    return {
       "between_observed_pp":observed,
       "rank_highest_1":rank,
       "greater_equal_count_24":greater_equal,
       "positive_observed_between":observed>0,
    }


def main():
    assert FROZEN.is_file()
    exact=json.loads(EXACT.read_text(encoding="utf8"))
    roster=[r for r in load(INPUT) if r["comparison"]=="long" and r["radius"]=="0"]
    assert len(roster)==23
    sub=[r for r in roster if all(r[k] for k in ("salinity0","salinity1","sst_C0","sst_C1"))]
    assert len(sub)==17
    sub_ids={r["site_id"] for r in sub}
    obs23=one_panel(roster)
    obs17=one_panel(sub)
    close(obs23["between_observed_pp"],exact["parent23"]["original_observed"]["between_region_pp"],"baseline23")
    close(obs17["between_observed_pp"],exact["complete17"]["original_observed"]["between_region_pp"],"baseline17")
    assert obs23["rank_highest_1"]==exact["parent23"]["between_rank_from_highest_with_ties"]
    assert obs17["rank_highest_1"]==exact["complete17"]["between_rank_from_highest_with_ties"]

    histories=historical_pairs(roster,records_by_site())
    rng=xorshift32(SEED)
    out=[]
    for num in range(1,N+1):
        sampled=[]
        for r in roster:
            r2=dict(r)
            early,late=histories[r["site_id"]]
            r2["n0"]=sample_median(early,rng)
            r2["n1"]=sample_median(late,rng)
            sampled.append(r2)
        p=one_panel(sampled)
        q=one_panel([x for x in sampled if x["site_id"] in sub_ids])
        out.append({
           "draw":num,
           "parent23_rank_24":p["rank_highest_1"],
           "parent23_B_pp":p["between_observed_pp"],
           "parent23_top2":p["rank_highest_1"]<=2,
           "complete17_rank_24":q["rank_highest_1"],
           "complete17_B_pp":q["between_observed_pp"],
           "complete17_top2":q["rank_highest_1"]<=2,
           "complete17_top3":q["rank_highest_1"]<=3,
        })
    with DRAWS.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=out[0].keys())
        w.writeheader()
        w.writerows(out)
    r23=[x["parent23_rank_24"] for x in out]
    r17=[x["complete17_rank_24"] for x in out]
    b23=[x["parent23_B_pp"] for x in out]
    b17=[x["complete17_B_pp"] for x in out]
    obj={
      "status":"FROZEN_POST_RESULT_CENSUS_YEAR_RANK_STABILITY_NO_CAUSAL_INFERENCE",
      "seed":SEED,"draws":N,
      "frozen_design":str(FROZEN.name),
      "original_exact24_rank":{"parent23":obs23,"complete17":obs17},
      "parent23":{
         "rank_distribution":summarize(r23),
         "top2_count":sum(r<=2 for r in r23),
         "top2_fraction":sum(r<=2 for r in r23)/N,
         "between_positive_fraction":sum(x>0 for x in b23)/N,
         "between_distribution_pp":summarize(b23),
      },
      "complete17":{
         "rank_distribution":summarize(r17),
         "top2_count":sum(r<=2 for r in r17),
         "top2_fraction":sum(r<=2 for r in r17)/N,
         "top3_count":sum(r<=3 for r in r17),
         "top3_fraction":sum(r<=3 for r in r17)/N,
         "between_positive_fraction":sum(x>0 for x in b17)/N,
         "between_distribution_pp":summarize(b17),
      },
      "both_top2_fraction":sum(x["parent23_top2"] and x["complete17_top2"] for x in out)/N,
      "same_rank_fraction":sum(x["parent23_rank_24"]==x["complete17_rank_24"] for x in out)/N,
      "sensitivity_not_population_confidence_interval":True,
      "permutation_rank_not_p_value":True,
      "post_result_frozen":True,
      "no_causal_climate_or_migration_inference":True,
    }
    OUT.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps({
       "status":obj["status"],
       "N":N,
       "parent23":obj["parent23"],
       "complete17":obj["complete17"],
       "both_top2_fraction":obj["both_top2_fraction"],
       "same_rank_fraction":obj["same_rank_fraction"],
       "not_causal":True,
    },indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
