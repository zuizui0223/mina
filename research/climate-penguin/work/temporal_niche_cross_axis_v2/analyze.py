"""Exploratory exact-camera temporal niche audit; NOT a penguin forecast.

Reanalyses audited v1 exact-camera rows and a source-gated same-site breeding
count comparison. Source winter 20-km SIC is NOT September or CMIP6 Aug-Nov SIC.
"""
from __future__ import annotations
import argparse
import csv
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "outputs/temporal_niche_pair_v1/exact_camera_pairs.csv"
LAND = ROOT / "outputs/warming_species_breeding_v1/matched_species_breeding_change.csv"
OUT = ROOT / "outputs/temporal_niche_cross_axis_v2/result.json"

def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def centered(v):
    mean = sum(v) / len(v)
    return [x-mean for x in v]

def pearson(x,y):
    a,b=centered(x),centered(y)
    return sum(u*v for u,v in zip(a,b))/math.sqrt(sum(u*u for u in a)*sum(v*v for v in b))

def covariance_and_denom(rows):
    x=centered([float(r["winter_sic_20km_pct"]) for r in rows])
    y=centered([float(r["gap_days"]) for r in rows])
    denominator=sum(v*v for v in x)
    if denominator <= 1e-12:
        raise ValueError("No within-camera ice variation")
    return x,y,sum(a*b for a,b in zip(x,y)),denominator

def slope_10(rows):
    _,_,num,den=covariance_and_denom(rows)
    return 10*num/den

def exact_within_camera(rows):
    x,y,num,den=covariance_and_denom(rows)
    total=0
    extreme=0
    for permutation in itertools.permutations(y):
        total+=1
        extreme+=abs(sum(a*b for a,b in zip(x,permutation)))+1e-10 >= abs(num)
    loo=[slope_10(rows[:i]+rows[i+1:]) for i in range(len(rows))]
    return {"n":len(rows),"years":sorted(int(r["year"]) for r in rows),
            "pearson_r":pearson([float(r["winter_sic_20km_pct"]) for r in rows],
                                 [float(r["gap_days"]) for r in rows]),
            "slope_days_per_10pp":10*num/den,"permutation_two_sided_p":extreme/total,
            "permutation_extreme":extreme,"permutation_total":total,
            "leave_one_season_out_slope_range_days_per_10pp":[min(loo),max(loo)]}

def pooled_exact(groups):
    if len(groups)!=2:
        raise ValueError("Requires two supported exact-camera pairs")
    xy=[covariance_and_denom(g) for g in groups]
    num=sum(p[2] for p in xy)
    den=sum(p[3] for p in xy)
    pa=[sum(a*b for a,b in zip(xy[0][0],p)) for p in itertools.permutations(xy[0][1])]
    pb=[sum(a*b for a,b in zip(xy[1][0],p)) for p in itertools.permutations(xy[1][1])]
    extreme=sum(abs(a+b)+1e-10>=abs(num) for a in pa for b in pb)
    total=len(pa)*len(pb)
    loo=[]
    for i in range(len(groups)):
        for j in range(len(groups[i])):
            modified=[list(g) for g in groups]
            modified[i].pop(j)
            parts=[covariance_and_denom(g) for g in modified]
            loo.append(10*sum(z[2] for z in parts)/sum(z[3] for z in parts))
    return {"n":sum(map(len,groups)),"camera_count":len(groups),
            "slope_days_per_10pp":10*num/den,"permutation_two_sided_p":extreme/total,
            "permutation_extreme":extreme,"permutation_total":total,
            "leave_one_season_out_slope_range_days_per_10pp":[min(loo),max(loo)],
            "exchangeable_years_assumption":"unverified; descriptive test only",
            "selection_posthoc":True,"causal_or_future_response_calibrated":False}

def cross_axis_support(selected,land_rows):
    labels={"Chinstrap":"CHPE","Gentoo":"GEPE"}
    out={}
    for (pair,camera),rs in selected.items():
        other=pair.split("-")[1]
        site=camera[:4]
        land=[r for r in land_rows if r["site_id"]==site and
              r["reference_species"]=="ADPE" and r["compared_species"]==labels[other]]
        if len(land)>1:
            raise ValueError("Repeated land source pair")
        camera_years={int(r["year"]) for r in rs}
        count_years={int(s) for s in land[0]["common_years"].split(";") if s} if land else set()
        out[pair+"/"+camera]={"land_site_code":site,"land_candidate_found":bool(land),
            "matched_site_years":sorted(camera_years&count_years),
            "n_matched_site_years":len(camera_years&count_years),
            "same_nest_camera_footprint_verified":False}
    return out

def run(input_path=INPUT,land_path=LAND,output=OUT):
    rows=read_csv(input_path)
    land=read_csv(land_path)
    if len(rows)!=15 or len(land)!=13:
        raise ValueError("Source support row count changed")
    groups=defaultdict(list)
    seen=set()
    for r in rows:
        key=(r["pair"],r["camera"],r["year"])
        if key in seen:
            raise ValueError("Duplicate pair x exact-camera x season")
        seen.add(key)
        if r["pair"].startswith("Adelie-"):
            groups[(r["pair"],r["camera"])].append(r)
    chosen=dict(sorted((k,sorted(rs,key=lambda r:int(r["year"]))) for k,rs in groups.items() if len(rs)>=5))
    if set(chosen)!={("Adelie-Chinstrap","SIGNc"),("Adelie-Gentoo","PETEe")}:
        raise ValueError("Strict same-camera support set changed")
    detail={p+"/"+c:exact_within_camera(rs) for (p,c),rs in chosen.items()}
    pooled=pooled_exact(list(chosen.values()))
    bridge=cross_axis_support(chosen,land)
    result={"analysis":"posthoc exact-camera two-pair temporal niche audit 2026-11-02",
        "inputs":{"same_camera_rows":len(rows),"land_source_pair_rows":len(land)},
        "selection":"Adelie reference, same exact camera, >=5 seasons; after inspecting data",
        "estimand":"paired settlement date gap versus source winter 20km SIC",
        "camera_pair_results":detail,"pooled_camera_pair_fixed_effects":pooled,
        "temporal_land_support":bridge,
        "temporal_land_matched_site_years_total":sum(v["n_matched_site_years"] for v in bridge.values()),
        "unverified":["independent replication","exchangeable years","same nest camera footprint",
                      "actual overlap of breeding stages","species competition",
                      "warming causal response","CMIP6 seasonal predictor equivalence"]}
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--camera-pairs",type=Path,default=INPUT)
    p.add_argument("--land-pairs",type=Path,default=LAND)
    p.add_argument("--out",type=Path,default=OUT)
    a=p.parse_args()
    result=run(a.camera_pairs,a.land_pairs,a.out)
    print(json.dumps({"pooled":result["pooled_camera_pair_fixed_effects"],
                      "bridge":result["temporal_land_support"]},ensure_ascii=False,indent=2))
