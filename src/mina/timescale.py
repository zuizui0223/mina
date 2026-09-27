"""Fresh post-negative test of low-frequency sea-ice timescale separation."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from .lter import ISLANDS, island_year_totals, load_colony_rows
from .mechanism import PRIMARY_METRIC, load_seaice

CENSUS_YEARS=tuple(range(1991,2018))


def _ols(x: np.ndarray,y: np.ndarray) -> np.ndarray:
    beta,_,rank,_=np.linalg.lstsq(x,y,rcond=None)
    if rank!=x.shape[1]:
        raise ValueError("rank-deficient timescale design")
    return beta


def total_counts(census_path: str|Path, islands: tuple[str,...]=ISLANDS) -> dict[int,float]:
    totals=island_year_totals(load_colony_rows(census_path))
    lookup={(int(r["year"]),str(r["island"])):float(r["breeding_pairs"]) for r in totals}
    out={}
    for year in CENSUS_YEARS:
        missing=[island for island in islands if (year,island) not in lookup]
        if missing:
            raise ValueError(f"missing census values in {year}: {missing}")
        out[year]=sum(lookup[(year,island)] for island in islands)
    return out


def windows(
    census_path: str|Path,
    seaice_path: str|Path,
    k: int,
    islands: tuple[str,...]=ISLANDS,
) -> list[dict[str,float|int]]:
    if k<2:
        raise ValueError("K must be >=2")
    counts=total_counts(census_path,islands)
    sea=load_seaice(seaice_path)
    rows=[]
    for end in range(CENSUS_YEARS[0]+k,CENSUS_YEARS[-1]+1):
        start=end-k
        ice_years=list(range(start+1,end+1))
        vals=[sea[y][PRIMARY_METRIC] for y in ice_years]
        if not all(math.isfinite(v) for v in vals):
            raise ValueError(f"missing sea ice in window ending {end}")
        rows.append({
            "start":start,
            "end":end,
            "midpoint":0.5*(start+end),
            "growth":(math.log1p(counts[end])-math.log1p(counts[start]))/k,
            "seaice_mean":float(np.mean(vals)),
        })
    return rows


def _scales(rows: list[dict[str,float|int]]) -> dict[str,float]:
    t=np.asarray([float(r["midpoint"]) for r in rows])
    s=np.asarray([float(r["seaice_mean"]) for r in rows])
    tsd=float(np.std(t,ddof=1)); ssd=float(np.std(s,ddof=1))
    if tsd<=0 or ssd<=0:
        raise ValueError("zero timescale predictor variance")
    return {
        "time_mean":float(np.mean(t)),"time_sd":tsd,
        "sea_mean":float(np.mean(s)),"sea_sd":ssd,
    }


def _design(
    rows: list[dict[str,float|int]],
    model: str,
    scales: dict[str,float],
) -> np.ndarray:
    tz=np.asarray([
        (float(r["midpoint"])-scales["time_mean"])/scales["time_sd"]
        for r in rows
    ])
    x=np.column_stack([np.ones(len(rows)),tz])
    if model=="T0":
        return x
    if model=="T1":
        sz=np.asarray([
            (float(r["seaice_mean"])-scales["sea_mean"])/scales["sea_sd"]
            for r in rows
        ])
        return np.column_stack([x,sz])
    raise ValueError(model)


def _overlap(a: dict[str,float|int],b: dict[str,float|int]) -> bool:
    # Inclusive endpoints: sharing a census endpoint is enough to purge.
    return not (int(a["end"]) < int(b["start"]) or int(a["start"]) > int(b["end"]))


def purged_validation(rows: list[dict[str,float|int]]) -> dict[str,object]:
    errors={"T0":[],"T1":[]}
    fold_sizes=[]
    for test in rows:
        train=[r for r in rows if r is not test and not _overlap(r,test)]
        if len(train)<5:
            raise ValueError(f"too few purged training windows for end={test['end']}: {len(train)}")
        scales=_scales(train)
        ytr=np.asarray([float(r["growth"]) for r in train])
        yte=float(test["growth"])
        local={}
        for model in ("T0","T1"):
            beta=_ols(_design(train,model,scales),ytr)
            pred=float(_design([test],model,scales)[0]@beta)
            err=yte-pred
            errors[model].append(err)
            local[model]=err
        fold_sizes.append({
            "end_year":int(test["end"]),
            "n_train":len(train),
            "squared_error_T0":local["T0"]**2,
            "squared_error_T1":local["T1"]**2,
        })
    mse={m:float(np.mean(np.square(v))) for m,v in errors.items()}
    return {
        "mse":mse,
        "gain_T0_minus_T1":mse["T0"]-mse["T1"],
        "folds":fold_sizes,
        "min_train_windows":min(x["n_train"] for x in fold_sizes),
    }


def full_fit(rows: list[dict[str,float|int]]) -> dict[str,float]:
    scales=_scales(rows)
    y=np.asarray([float(r["growth"]) for r in rows])
    beta0=_ols(_design(rows,"T0",scales),y)
    beta1=_ols(_design(rows,"T1",scales),y)
    t=np.asarray([float(r["midpoint"]) for r in rows])
    s=np.asarray([float(r["seaice_mean"]) for r in rows])
    corr=float(np.corrcoef(t,s)[0,1])
    return {
        "time_beta_T0":float(beta0[-1]),
        "time_beta_T1":float(beta1[-2]),
        "seaice_beta_T1":float(beta1[-1]),
        "time_seaice_correlation":corr,
    }


def phase_coefficients(rows: list[dict[str,float|int]],k: int) -> dict[str,object]:
    first=int(rows[0]["end"])
    out={}
    positive=0
    finite=0
    for phase in range(k):
        local=[r for r in rows if (int(r["end"])-first)%k==phase]
        if len(local)<3:
            out[str(phase)]={"n":len(local),"seaice_beta":None}
            continue
        try:
            beta=full_fit(local)["seaice_beta_T1"]
        except ValueError:
            beta=None
        out[str(phase)]={"n":len(local),"seaice_beta":beta}
        if beta is not None and math.isfinite(beta):
            finite+=1
            positive+=int(beta>0)
    return {"phases":out,"positive_phase_count":positive,"finite_phase_count":finite}


def run_scale(
    census_path: str|Path,
    seaice_path: str|Path,
    k: int,
    islands: tuple[str,...]=ISLANDS,
) -> dict[str,object]:
    rows=windows(census_path,seaice_path,k,islands)
    cv=purged_validation(rows)
    fit=full_fit(rows)
    return {
        "K":k,
        "islands":list(islands),
        "n_windows":len(rows),
        "validation":cv,
        "full_fit":fit,
        "phase_diagnostic":phase_coefficients(rows,k),
    }


def analyze(census_path: str|Path,seaice_path: str|Path) -> dict[str,object]:
    primary=run_scale(census_path,seaice_path,5)
    k3=run_scale(census_path,seaice_path,3)
    k7=run_scale(census_path,seaice_path,7)
    four=run_scale(census_path,seaice_path,5,("CHR","COR","HUM","TOR"))
    gain=float(primary["validation"]["gain_T0_minus_T1"])
    beta=float(primary["full_fit"]["seaice_beta_T1"])
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-seaice-timescale-separation-v1",
        "hypothesis_status":"fresh_post_negative_frozen_before_smoothed_values",
        "primary":primary,
        "robustness":{"K3":k3,"K7":k7,"four_islands_K5":four},
        "decision":{
            "timescale_separation_supported":bool(gain>0 and beta>0),
            "primary_predictive_gain_positive":bool(gain>0),
            "primary_direction_positive":bool(beta>0),
        },
        "interpretation_boundary":{
            "causal_claim":False,
            "time_trend_baseline_included":True,
            "overlapping_windows_purged_from_training":True,
            "window_length_tuned_after_outcome":False,
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
