#!/usr/bin/env python3
"""Post-result within-site observed-census-year sensitivity for 23 vs 17 Adélie sites.

Condition on source-observed annual counts; resample observed years with replacement
*within the same site and period*, preserving number of observed years and genuine
recorded zeros. This is NOT a population confidence interval or a climate effect.
"""
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from recompute_parent23_vs_complete17_SIC_region_sensitivity_20261121 import decompose, load

HERE = Path(__file__).resolve().parent
N_DRAWS=4999
SEED=20261121
EARLY=(1993,2000)
LATE=(2011,2020)
OUTPUT=HERE/"SIC23_VS17_SOURCE_CENSUS_YEAR_RESAMPLING_20261121.json"
DRAWS_OUTPUT=HERE/"SIC23_VS17_SOURCE_CENSUS_YEAR_RESAMPLING_DRAWS_20261121.csv"


def xorshift32(seed):
    while True:
        seed ^= (seed << 13) & 0xffffffff
        seed ^= seed >> 17
        seed ^= (seed << 5) & 0xffffffff
        seed &= 0xffffffff
        yield seed


def percentile(a,p):
    a=sorted(a)
    t=(len(a)-1)*p
    lo,hi=math.floor(t),math.ceil(t)
    if lo==hi:
        return a[lo]
    return a[lo]*(hi-t)+a[hi]*(t-lo)


def records_by_site():
    x=load(HERE/"observed_counts_used.csv")
    assert len(x)==513, "Recorded source-row count changed"
    g=defaultdict(list)
    keys=set()
    for r in x:
        assert r["species"]=="ADPE"
        k=(r["site_id"],int(r["season"]))
        assert k not in keys
        keys.add(k)
        assert float(r["observed_nest_count"])>=0
        if float(r["observed_nest_count"])==0:
            assert r["observed_zero_is_actual_source_count"]=="True"
        g[r["site_id"]].append(r)
    for site, rr in g.items():
        assert len({q["original_survey_method"] for q in rr})==1, site
    return g


def historical_pairs(roster, source):
    pairs={}
    for r in roster:
        site=r["site_id"]
        a=[]
        for (start,end) in (EARLY,LATE):
            rows=[z for z in source[site] if start<=int(z["season"])<=end]
            expected_years=r["years"+str(len(a))].split(";")
            assert sorted(expected_years)==sorted(z["season"] for z in rows),site
            assert len(rows)==int(float(r["n_years"+str(len(a))]))
            assert len(rows)>=2
            vals=[float(z["observed_nest_count"]) for z in rows]
            assert math.isclose(statistics.median(vals),float(r["n"+str(len(a))]),rel_tol=0,abs_tol=1e-9),site
            a.append(vals)
        pairs[site]=a
    return pairs


def sample_median(values, rng):
    n=len(values)
    chosen=[values[next(rng)%n] for _ in range(n)]
    return float(statistics.median(chosen))


def describe(values):
    return {
        "n":len(values),
        "q025":percentile(values,.025),
        "median":percentile(values,.5),
        "q975":percentile(values,.975),
        "positive_count":sum(x>0 for x in values),
        "positive_fraction":sum(x>0 for x in values)/len(values),
        "zero_count":sum(x==0 for x in values),
    }


def main():
    roster=[r for r in load(HERE/"matched_support.csv") if r["comparison"]=="long" and r["radius"]=="0"]
    assert len(roster)==23 and len({r["site_id"] for r in roster})==23
    completed=[r for r in roster if all(r[k] for k in ("salinity0","salinity1","sst_C0","sst_C1"))]
    assert len(completed)==17
    ids17={r["site_id"] for r in completed}
    src=records_by_site()
    pairs=historical_pairs(roster,src)
    assert pairs["PLEN"][0]==[0.0]*4
    assert statistics.median(pairs["PLEN"][1])==0.0
    assert sorted(pairs["PLEN"][1])==[0.0,0.0,0.0,0.0,1.0], "True 2017 positive source observation must not be overwritten by decade median zero"
    actual23=decompose(roster)
    actual17=decompose(completed)
    fields=("nest_reallocation_component_pp","between_region_pp","within_region_pp")
    stats={name:{field:[] for field in fields} for name in ("full23","matched17")}
    draw_rows=[]
    rng=xorshift32(SEED)
    for i in range(1,N_DRAWS+1):
        draw=[]
        for r in roster:
            row=dict(r)
            v0,v1=pairs[r["site_id"]]
            row["n0"]=sample_median(v0,rng)
            row["n1"]=sample_median(v1,rng)
            draw.append(row)
        r23=decompose(draw)
        r17=decompose([r for r in draw if r["site_id"] in ids17])
        for name,values in (("full23",r23),("matched17",r17)):
            for k in fields:
                stats[name][k].append(values[k])
        draw_rows.append({
            "draw":i,
            "parent23_R_pp":r23["nest_reallocation_component_pp"],
            "parent23_between_pp":r23["between_region_pp"],
            "parent23_within_pp":r23["within_region_pp"],
            "marine17_R_pp":r17["nest_reallocation_component_pp"],
            "marine17_between_pp":r17["between_region_pp"],
            "marine17_within_pp":r17["within_region_pp"],
        })
    with DRAWS_OUTPUT.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=draw_rows[0].keys())
        w.writeheader();w.writerows(draw_rows)
    report={
        "status":"POST_RESULT_SOURCE_YEAR_CONDITIONAL_RESAMPLING_NOT_ECOLOGICAL_CI",
        "source":"observed_counts_used.csv, matched_support.csv",
        "resampling_definition":"At each source site, draw n actually observed census seasons with replacement separately for 1993-2000 and 2011-2020; recalculate period medians; reuse exact same draw for parent23 and marine17. Actual zeros remain zeros. No extrapolation or Y-outcome model.",
        "seed":SEED,"n_draws":N_DRAWS,
        "sites_23":len(roster),"sites_17":len(completed),
        "regions_23":4,"regions_17":4,
        "original":{"full23":{key:actual23[key] for key in fields},
                    "matched17":{key:actual17[key] for key in fields}},
        "conditional_sensitivity":{
            name:{field:describe(values) for field,values in fields_dict.items()}
            for name,fields_dict in stats.items()},
        "limits":"Observed nest count data come from heterogeneous source years, methods and survey processes; replacement sampling estimates only conditional numeric instability of observed medians, not independent colonies, ecological dynamics, or true sampling-model uncertainty.",
        "not_an_ecological_randomization_test":True,
        "no_new_climate_effect_or_population_forecast":True,
    }
    # Changes in locale survey-year medians must not alter the interpretation
    # of cohort-selection/GLORYS missingness as an independent replication.
    assert report["conditional_sensitivity"]["full23"]["between_region_pp"]["n"]==N_DRAWS
    assert report["conditional_sensitivity"]["matched17"]["between_region_pp"]["n"]==N_DRAWS
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "verdict":report["status"],"draws":N_DRAWS,
        "full23":report["conditional_sensitivity"]["full23"],
        "matched17":report["conditional_sensitivity"]["matched17"],
        "source_medians_exact":True,
        "zero_PLEN_source_record_preserved":True,
        "not_an_ecological_randomization_test":True},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
