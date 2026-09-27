"""Mechanism test: regional sea ice and island breeding-habitat moderation."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

from .lter import ISLANDS, island_year_totals, load_colony_rows

HABITAT_PERCENT={
    "LIT":89.5,
    "COR":63.0,
    "CHR":46.8,
    "TOR":44.3,
    "HUM":44.2,
}
PRIMARY_METRIC="SIDuration"
ROBUSTNESS_METRIC="IceDays"
EXPECTED_YEARS=tuple(range(1992,2018))


def _ols(x: np.ndarray,y: np.ndarray) -> np.ndarray:
    beta,_,rank,_=np.linalg.lstsq(x,y,rcond=None)
    if rank!=x.shape[1]:
        raise ValueError("rank-deficient mechanism design")
    return beta


def _island_design(
    islands: list[str],
    levels: tuple[str, ...],
) -> np.ndarray:
    x=np.zeros((len(islands),len(levels)),dtype=float)
    lookup={v:i for i,v in enumerate(levels)}
    for r,island in enumerate(islands):
        if island not in lookup:
            raise ValueError(f"unexpected island for active design: {island}")
        x[r,lookup[island]]=1.0
    return x


def load_seaice(path: str|Path) -> dict[int,dict[str,float]]:
    with Path(path).open("r",encoding="utf-8-sig",newline="") as h:
        rows=list(csv.DictReader(h))
    out={}
    for row in rows:
        try:
            year=int(float(row["Year"]))
        except (KeyError,TypeError,ValueError):
            continue
        values={}
        for name in (PRIMARY_METRIC,ROBUSTNESS_METRIC,"SIRetreat"):
            try:
                value=float(row[name])
            except (KeyError,TypeError,ValueError):
                value=float("nan")
            values[name]=value
        out[year]=values
    missing=[y for y in EXPECTED_YEARS if y not in out or not math.isfinite(out[y][PRIMARY_METRIC])]
    if missing:
        raise ValueError(f"missing primary sea-ice years: {missing}")
    return out


def growth_rows(census_path: str|Path) -> list[dict[str,object]]:
    totals=island_year_totals(load_colony_rows(census_path))
    lookup={(int(r["year"]),str(r["island"])):float(r["breeding_pairs"]) for r in totals}
    rows=[]
    for year in EXPECTED_YEARS:
        for island in ISLANDS:
            if (year-1,island) not in lookup or (year,island) not in lookup:
                raise ValueError(f"missing census transition {island} {year-1}->{year}")
            before=lookup[(year-1,island)]
            after=lookup[(year,island)]
            rows.append({
                "year":year,
                "island":island,
                "before":before,
                "after":after,
                "growth":math.log1p(after)-math.log1p(before),
            })
    return rows


def _standardize_train(values: np.ndarray,train: np.ndarray,test: np.ndarray) -> tuple[np.ndarray,np.ndarray,float,float]:
    mean=float(np.mean(values[train]))
    sd=float(np.std(values[train],ddof=1))
    if sd<=0:
        raise ValueError("zero predictor variance")
    return (values[train]-mean)/sd,(values[test]-mean)/sd,mean,sd


def _habitat_z(islands: list[str]) -> np.ndarray:
    raw=np.asarray([HABITAT_PERCENT[x] for x in islands],dtype=float)
    all_raw=np.asarray([HABITAT_PERCENT[x] for x in ISLANDS],dtype=float)
    return (raw-float(np.mean(all_raw)))/float(np.std(all_raw,ddof=1))


def _design(
    islands: list[str],
    sea_z: np.ndarray,
    model: str,
    levels: tuple[str, ...],
) -> np.ndarray:
    base=_island_design(islands,levels)
    if model=="M0":
        return base
    if model=="M1":
        return np.column_stack([base,sea_z])
    if model=="M2":
        hz=_habitat_z(islands)
        return np.column_stack([base,sea_z,sea_z*hz])
    raise ValueError(model)


def loyo(rows: list[dict[str,object]],seaice: dict[int,dict[str,float]],metric: str,
         allowed_islands: tuple[str,...]=ISLANDS,exclude_lit_after_zero: bool=False) -> dict[str,object]:
    local=[
        r for r in rows
        if r["island"] in allowed_islands
        and not (exclude_lit_after_zero and r["island"]=="LIT" and int(r["year"])>=2007)
    ]
    years=sorted({int(r["year"]) for r in local})
    levels=tuple(island for island in ISLANDS if island in {str(r["island"]) for r in local})
    values=np.asarray([seaice[int(r["year"])][metric] for r in local],dtype=float)
    y=np.asarray([float(r["growth"]) for r in local],dtype=float)
    islands=[str(r["island"]) for r in local]
    year_arr=np.asarray([int(r["year"]) for r in local],dtype=int)

    sq={m:[] for m in ("M0","M1","M2")}
    fold=[]
    for year in years:
        test=year_arr==year
        train=~test
        ztr,zte,_,_=_standardize_train(values,train,test)
        rec={"year":year,"n_test":int(np.sum(test))}
        for model in ("M0","M1","M2"):
            xtr=_design([islands[i] for i in np.where(train)[0]],ztr,model,levels)
            xte=_design([islands[i] for i in np.where(test)[0]],zte,model,levels)
            beta=_ols(xtr,y[train])
            err=y[test]-xte@beta
            mse=float(np.mean(err**2))
            sq[model].extend((err**2).tolist())
            rec[f"{model}_mse"]=mse
        fold.append(rec)
    mse={m:float(np.mean(v)) for m,v in sq.items()}
    return {
        "n_rows":len(local),
        "n_years":len(years),
        "years":years,
        "mse":mse,
        "primary_mse_gain_M0_minus_M1":mse["M0"]-mse["M1"],
        "secondary_mse_gain_M1_minus_M2":mse["M1"]-mse["M2"],
        "folds":fold,
    }


def full_coefficients(rows: list[dict[str,object]],seaice: dict[int,dict[str,float]],metric: str,
                      allowed_islands: tuple[str,...]=ISLANDS,exclude_lit_after_zero: bool=False) -> dict[str,float]:
    local=[
        r for r in rows
        if r["island"] in allowed_islands
        and not (exclude_lit_after_zero and r["island"]=="LIT" and int(r["year"])>=2007)
    ]
    islands=[str(r["island"]) for r in local]
    y=np.asarray([float(r["growth"]) for r in local],dtype=float)
    sea=np.asarray([seaice[int(r["year"])][metric] for r in local],dtype=float)
    sea=(sea-float(np.mean(sea)))/float(np.std(sea,ddof=1))
    levels=tuple(island for island in ISLANDS if island in set(islands))
    b1=_ols(_design(islands,sea,"M1",levels),y)
    b2=_ols(_design(islands,sea,"M2",levels),y)
    return {
        "regional_beta_M1":float(b1[-1]),
        "regional_beta_M2":float(b2[-2]),
        "interaction_beta_M2":float(b2[-1]),
    }


def bootstrap_coefficients(rows: list[dict[str,object]],seaice: dict[int,dict[str,float]],
                           metric: str,draws: int=10000,seed: int=20260927) -> dict[str,object]:
    years=np.asarray(EXPECTED_YEARS,dtype=int)
    by_year={y:[r for r in rows if int(r["year"])==y] for y in years}
    rng=np.random.default_rng(seed)
    regional=[]
    interaction=[]
    for _ in range(draws):
        sampled=rng.choice(years,size=len(years),replace=True)
        boot=[]
        for y in sampled:
            # Give duplicated year clusters unique pseudo-years while retaining
            # their original predictor value.
            boot.extend(by_year[int(y)])
        islands=[str(r["island"]) for r in boot]
        yy=np.asarray([float(r["growth"]) for r in boot],dtype=float)
        sea=np.asarray([seaice[int(r["year"])][metric] for r in boot],dtype=float)
        sd=float(np.std(sea,ddof=1))
        if sd<=0:
            continue
        sea=(sea-float(np.mean(sea)))/sd
        try:
            b1=_ols(_design(islands,sea,"M1",ISLANDS),yy)
            b2=_ols(_design(islands,sea,"M2",ISLANDS),yy)
        except ValueError:
            continue
        regional.append(float(b1[-1]))
        interaction.append(float(b2[-1]))
    def summary(x: list[float]) -> dict[str,float]:
        a=np.asarray(x,dtype=float)
        return {
            "draws":int(a.size),
            "median":float(np.median(a)),
            "lower_2_5":float(np.quantile(a,0.025)),
            "upper_97_5":float(np.quantile(a,0.975)),
        }
    return {"regional_beta_M1":summary(regional),"interaction_beta_M2":summary(interaction)}


def analyze(census_path: str|Path,seaice_path: str|Path) -> dict[str,object]:
    rows=growth_rows(census_path)
    seaice=load_seaice(seaice_path)
    primary=loyo(rows,seaice,PRIMARY_METRIC)
    coef=full_coefficients(rows,seaice,PRIMARY_METRIC)
    bootstrap=bootstrap_coefficients(rows,seaice,PRIMARY_METRIC)
    four=loyo(rows,seaice,PRIMARY_METRIC,allowed_islands=("CHR","COR","HUM","TOR"))
    no_post=loyo(rows,seaice,PRIMARY_METRIC,exclude_lit_after_zero=True)
    ice_days=loyo(rows,seaice,ROBUSTNESS_METRIC)
    regional_support=bool(primary["primary_mse_gain_M0_minus_M1"]>0 and coef["regional_beta_M1"]>0)
    moderation_support=bool(primary["secondary_mse_gain_M1_minus_M2"]>0)
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-seaice-habitat-mechanism-v1",
        "primary_metric":PRIMARY_METRIC,
        "growth_row_count":len(rows),
        "seaice_years":list(EXPECTED_YEARS),
        "primary_loyo":primary,
        "full_coefficients":coef,
        "year_cluster_bootstrap":bootstrap,
        "decision":{
            "regional_support":regional_support,
            "habitat_moderation_support":moderation_support,
        },
        "sensitivity":{
            "four_persistently_extant_islands":four,
            "exclude_litchfield_post_extinction":no_post,
            "actual_ice_days":ice_days,
        },
        "physical_habitat_prior":{
            "suboptimal_percent":HABITAT_PERCENT,
            "status":"published prior, not fresh independent habitat-decline evidence",
        },
        "interpretation_boundary":{
            "predictive_not_causal":True,
            "habitat_prior_not_independent_replication":True,
            "residual_not_competition":True,
        },
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--census",required=True,type=Path)
    p.add_argument("--seaice",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=analyze(args.census,args.seaice)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
