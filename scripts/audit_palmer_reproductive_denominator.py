#!/usr/bin/env python3
"""Post-outcome denominator-semantics audit for Palmer chick production."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ISLANDS=("CHR","COR","HUM","LIT","TOR")


def finite(v):
    if v in {None,"","NA","NaN","nan"}:
        return False
    try:
        return math.isfinite(float(v))
    except (TypeError,ValueError):
        return False


def load_adults(path):
    with Path(path).open(newline="",encoding="utf-8-sig") as h:
        raw=list(csv.DictReader(h))
    out={}
    for r in raw:
        if not finite(r.get("num_breeding_pairs")):
            continue
        island=str(r.get("island_name","")).strip()
        study=str(r.get("study_name","")).strip()
        code=str(r.get("colony_code","")).strip()
        if island not in ISLANDS or not study or not code:
            continue
        key=(study,island,code)
        if key in out:
            raise ValueError(f"duplicate adult key {key}")
        out[key]=float(r["num_breeding_pairs"])
    return out


def load_chicks(path):
    with Path(path).open(newline="",encoding="utf-8-sig") as h:
        raw=list(csv.DictReader(h))
    by=defaultdict(list)
    for r in raw:
        if not finite(r.get("num_chicks")):
            continue
        island=str(r.get("island_name","")).strip()
        study=str(r.get("study_name","")).strip()
        code=str(r.get("colony_code","")).strip()
        if island not in ISLANDS or not study or not code:
            continue
        by[(study,island,code)].append(r)
    chosen={}
    for key,local in by.items():
        local=sorted(
            local,
            key=lambda r:(
                -float(r["num_chicks"]),
                str(r.get("time","")),
                str(r.get("census_time",""))
            )
        )
        chosen[key]=local[0]
    return chosen


def common_rows(adults,chicks):
    rows=[]
    for key in sorted(set(adults)&set(chicks)):
        study,island,code=key
        adult=float(adults[key])
        r=chicks[key]
        if not finite(r.get("num_breeding_pairs")):
            continue
        legacy=float(r["num_breeding_pairs"])
        chick=float(r["num_chicks"])
        if adult<=0 or legacy<=0 or chick<0:
            continue
        rows.append({
            "study_name":study,
            "island":island,
            "colony_code":code,
            "adult_pairs":adult,
            "legacy_pairs":legacy,
            "chicks":chick,
        })
    return rows


def build_groups(rows):
    grouped=defaultdict(list)
    for r in rows:
        grouped[(r["island"],r["study_name"])].append(r)
    out=[]
    for (island,study),local in sorted(grouped.items()):
        if len(local)<4:
            continue
        chicks=np.asarray([float(r["chicks"]) for r in local],float)
        if not np.allclose(chicks,np.rint(chicks),atol=1e-9):
            raise ValueError("non-integer chicks")
        chicks=np.rint(chicks).astype(np.int64)
        if int(chicks.sum())<1:
            continue
        rec={"island":island,"study_name":study,"n":len(local),"chicks":chicks}
        good=True
        for src,col in (("adult","adult_pairs"),("legacy","legacy_pairs")):
            pairs=np.asarray([float(r[col]) for r in local],float)
            xraw=np.log1p(pairs)
            sd=float(np.std(xraw,ddof=0))
            if sd<=0:
                good=False
                break
            x=(xraw-float(np.mean(xraw)))/sd
            p=pairs/float(np.sum(pairs))
            mu=float(np.sum(p*x))
            var=float(np.sum(p*(x-mu)**2))
            info=int(chicks.sum())*var
            rec[src]={
                "pairs":pairs,"x":x,"p":p,
                "score":float(np.sum(chicks*x)-int(chicks.sum())*mu),
                "information":info,
            }
        if good:
            out.append(rec)
    return out


def fit_beta(groups,src):
    beta=0.0
    info=float("nan")
    for _ in range(100):
        score=0.0
        info=0.0
        for g in groups:
            z=g[src]
            pairs=z["pairs"]; x=z["x"]; chicks=g["chicks"].astype(float)
            c=float(np.sum(chicks))
            eta=np.clip(beta*x,-30,30)
            w=pairs*np.exp(eta); p=w/float(np.sum(w))
            mu=float(np.sum(p*x)); var=float(np.sum(p*(x-mu)**2))
            score+=float(np.sum(chicks*x)-c*mu)
            info+=c*var
        if info<=0:
            raise ValueError("non-positive information")
        step=score/info
        beta+=step
        if abs(step)<1e-12:
            break
    return {
        "beta":float(beta),
        "multiplicative_per_1sd":float(math.exp(beta)),
        "naive_se":float(1/math.sqrt(info)),
    }


def score_test(groups,src,draws,seed):
    obs_score=float(sum(g[src]["score"] for g in groups))
    info=float(sum(g[src]["information"] for g in groups))
    zobs=obs_score/math.sqrt(info)
    rng=np.random.default_rng(seed)
    null=np.zeros(draws,float)
    for g in groups:
        z=g[src]
        c=int(np.sum(g["chicks"]))
        sim=rng.multinomial(c,z["p"],size=draws)
        mu=float(np.sum(z["p"]*z["x"]))
        null+=sim@z["x"]-c*mu
    nullz=null/math.sqrt(info)
    p=float((1+int(np.sum(nullz>=zobs)))/(draws+1))
    return {
        "observed_z":float(zobs),
        "null_mean":float(np.mean(nullz)),
        "null_q025":float(np.quantile(nullz,.025)),
        "null_q975":float(np.quantile(nullz,.975)),
        "one_sided_upper_p":p,
    }


def ratio_slopes(groups,rows):
    lookup=defaultdict(list)
    for r in rows:
        lookup[(r["island"],r["study_name"])].append(r)
    vals={"adult_predictor":[],"legacy_predictor":[]}
    by_island={name:{k:[] for k in vals} for name in ISLANDS}
    eligible={(g["island"],g["study_name"]) for g in groups}
    for key in sorted(eligible):
        local=lookup[key]
        y=np.asarray([float(r["chicks"])/float(r["legacy_pairs"]) for r in local],float)
        for label,col in (("adult_predictor","adult_pairs"),("legacy_predictor","legacy_pairs")):
            x=np.log1p(np.asarray([float(r[col]) for r in local],float))
            sx=float(np.std(x,ddof=1))
            if sx<=0:
                continue
            z=(x-float(np.mean(x)))/sx
            slope=float((z@y)/(z@z))
            vals[label].append(slope)
            by_island[key[0]][label].append(slope)
    return {
        "overall_mean_slope":{k:float(np.mean(v)) for k,v in vals.items()},
        "by_island_mean_slope":{
            isl:{k:(float(np.mean(v)) if v else None) for k,v in d.items()}
            for isl,d in by_island.items()
        },
        "role":"descriptive only; ratio regression is not the inferential model",
    }


def measurement(rows):
    adult=np.asarray([float(r["adult_pairs"]) for r in rows])
    legacy=np.asarray([float(r["legacy_pairs"]) for r in rows])
    chicks=np.asarray([float(r["chicks"]) for r in rows])
    exact=int(np.sum(adult==legacy))
    rel=np.abs(adult-legacy)/np.maximum(adult,1.0)
    return {
        "n_common_rows":len(rows),
        "exact_pair_match_n":exact,
        "exact_pair_match_fraction":float(exact/len(rows)),
        "median_absolute_pair_difference":float(np.median(np.abs(adult-legacy))),
        "median_relative_difference_vs_adult":float(np.median(rel)),
        "legacy_chicks_gt_2x_pairs_n":int(np.sum(chicks>2*legacy)),
        "legacy_chicks_gt_2x_pairs_fraction":float(np.mean(chicks>2*legacy)),
        "adult_chicks_gt_2x_pairs_n":int(np.sum(chicks>2*adult)),
        "adult_chicks_gt_2x_pairs_fraction":float(np.mean(chicks>2*adult)),
    }


def analyze(adult_path,chick_path,draws=100000):
    adults=load_adults(adult_path); chicks=load_chicks(chick_path)
    rows=common_rows(adults,chicks)
    groups=build_groups(rows)
    if len(groups)!=95 or sum(g["n"] for g in groups)!=727:
        raise ValueError(
            f"common-frame drift groups={len(groups)} rows={sum(g['n'] for g in groups)}"
        )
    models={}
    for src,seed in (("adult",20260930),("legacy",20260931)):
        pooled=fit_beta(groups,src)
        pooled["score_test"]=score_test(groups,src,draws,seed)
        island={}
        for isl in ISLANDS:
            local=[g for g in groups if g["island"]==isl]
            island[isl]=fit_beta(local,src)
        loo={}
        for isl in ISLANDS:
            local=[g for g in groups if g["island"]!=isl]
            loo[isl]=fit_beta(local,src)
        models[src]={
            "pooled":pooled,
            "by_island":island,
            "leave_one_island_out":loo,
        }
    adult_signs={isl:models["adult"]["by_island"][isl]["beta"]>0 for isl in ISLANDS}
    loo_positive=all(models["adult"]["leave_one_island_out"][isl]["beta"]>0 for isl in ISLANDS)
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-reproductive-denominator-audit-v1",
        "common_frame":{
            "n_groups":len(groups),
            "n_colony_rows":int(sum(g["n"] for g in groups)),
        },
        "measurement":measurement(rows),
        "conditional_count_models":models,
        "ratio_diagnostic":ratio_slopes(groups,rows),
        "decision":{
            "positive_count_space_effect_under_both_denominator_sources":bool(
                models["adult"]["pooled"]["beta"]>0
                and models["legacy"]["pooled"]["beta"]>0
                and models["adult"]["pooled"]["score_test"]["one_sided_upper_p"]<=.05
                and models["legacy"]["pooled"]["score_test"]["one_sided_upper_p"]<=.05
            ),
            "adult_denominator_island_signs":adult_signs,
            "all_adult_denominator_island_betas_positive":bool(all(adult_signs.values())),
            "all_adult_denominator_leave_one_out_betas_positive":bool(loo_positive),
            "palmer_wide_positive_density_dependence_claim_allowed":False,
        },
        "interpretation":[
            "The null same-denominator ratio slope and the positive count-space size effect are not equivalent tests.",
            "On an identical common frame, conditional chick-count allocation gives a positive pooled size effect under either pair-count source, so the sign is not created solely by choosing the independent adult denominator.",
            "The pair denominators disagree strongly in raw records and the legacy chick-table denominator has serious biological-cap violations; it is not a robustness gold standard for ratio inference.",
            "The positive pooled count-space effect is spatially heterogeneous across islands and is not robust to every leave-one-island-out fit; a common Palmer-wide small-group reproductive disadvantage is therefore not supported.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--adult",required=True,type=Path)
    p.add_argument("--chicks",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--draws",type=int,default=100000)
    a=p.parse_args()
    out=analyze(a.adult,a.chicks,a.draws)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
