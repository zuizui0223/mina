#!/usr/bin/env python3
"""Prespecified exact-date / <=14-day observation-offset sensitivity."""
from __future__ import annotations

import argparse,json
from pathlib import Path
import itertools
import numpy as np
import pandas as pd
import pyreadr

from scripts.run_paper2_real_v3_fit import (
    build_frozen_real_records,
    _filter_records,
)
from scripts.simulate_paper2_observation_recovery import (
    _vantage_family,
    _accuracy_group,
    estimate_accuracy_scales,
)
from scripts.simulate_paper2_spatial_adjusted_v3 import (
    build_v3_frames,
    fit_spatial_species,
)

SPECIES=("ADPE","CHPE","GEPE")
EXPECTED_RECORDS=2100
EXPECTED_PAIRS={0:23,14:53}


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x: return x[expected]
    if len(x)==1: return next(iter(x.values()))
    raise ValueError(expected)


def build_dated_cohort(obs:pd.DataFrame,records:pd.DataFrame)->pd.DataFrame:
    ids=set(
        records["species_id"].astype(str)+"|"+records["site_id"].astype(str)
    )
    x=obs[
        obs["species_id"].isin(SPECIES)
        & obs["type"].eq("nests")
        & obs["count"].notna()
    ].copy()
    x["season"]=pd.to_numeric(x["season"],errors="coerce")
    x["count"]=pd.to_numeric(x["count"],errors="raise")
    x["unit_id"]=x["species_id"].astype(str)+"|"+x["site_id"].astype(str)
    x=x[
        x["unit_id"].isin(ids)
        & x["season"].between(1980,2025,inclusive="both")
    ].copy()
    x["season"]=x["season"].astype(int)
    x["vantage_family"]=x["vantage"].map(_vantage_family)
    x["accuracy_group"]=x["accuracy"].map(_accuracy_group)
    x["date_parsed"]=pd.to_datetime(x["date"],errors="coerce")
    x["group_id"]=(
        x["site_id"].astype(str)+"|"+x["species_id"].astype(str)+"|"+x["season"].astype(str)
    )
    if len(x)!=EXPECTED_RECORDS:
        raise ValueError(f"dated cohort drift {len(x)} != {EXPECTED_RECORDS}")
    return x


def matched_offset(cohort:pd.DataFrame,max_days:int)->dict:
    diffs=[]
    by_species={sp:0 for sp in SPECIES}
    for (_,sp,_),local in cohort.groupby(["site_id","species_id","season"],sort=True):
        direct=local[
            local["vantage_family"].astype(str).eq("direct")
            & local["date_parsed"].notna()
        ]
        image=local[
            local["vantage_family"].astype(str).eq("image_based")
            & local["date_parsed"].notna()
        ]
        for _,d in direct.iterrows():
            for _,im in image.iterrows():
                delta=abs((d["date_parsed"]-im["date_parsed"]).days)
                if delta<=max_days:
                    diffs.append(
                        float(np.log1p(float(im["count"]))-np.log1p(float(d["count"])))
                    )
                    by_species[str(sp)]+=1
    expected=EXPECTED_PAIRS[max_days]
    if len(diffs)!=expected:
        raise ValueError(f"timing pair drift {max_days}: {len(diffs)} != {expected}")
    return {
        "pairs":int(len(diffs)),
        "pairs_by_species":{sp:int(by_species[sp]) for sp in SPECIES},
        "delta_image":float(np.mean(diffs)),
        "image_multiplicative_factor":float(np.exp(np.mean(diffs))),
        "pair_diff_sd":float(np.std(diffs,ddof=1)) if len(diffs)>1 else None,
    }


def recalibrate_accuracy(records:pd.DataFrame,delta_image:float)->dict:
    x=records.copy()
    x["log_observed"]=np.log1p(pd.to_numeric(x["count"],errors="raise").to_numpy(float))
    out=estimate_accuracy_scales(x,delta_image=float(delta_image))
    for key in ("1","2-5"):
        if out[key]["sigma"] is None:
            raise ValueError(f"accuracy scale {key} unavailable")
    return out


def fit_mode(frames,records,delta_image,accuracy)->dict:
    result={}
    for sp in SPECIES:
        ids=set(frames[sp]["unit_id"].astype(str))
        local=records.copy()
        local["unit_id"]=local["species_id"].astype(str)+"|"+local["site_id"].astype(str)
        local=local[local["unit_id"].isin(ids)].copy()
        fit=fit_spatial_species(
            frames[sp].reset_index(drop=True),
            local,
            delta_image=float(delta_image),
            sigma1=float(accuracy["1"]["sigma"]),
            sigma2plus=float(accuracy["2-5"]["sigma"]),
            truth_forcing=None,
            true_lambda=None,
        )
        ga=float(fit["gamma_a"]); gh=float(fit["gamma_h"]); gah=float(fit["gamma_ah"])
        result[sp]={
            "gamma_a":ga,
            "gamma_h":gh,
            "gamma_ah":gah,
            "low_area_H_slope":gh-gah,
            "high_area_H_slope":gh+gah,
            "crossover_classification":bool(gah<0 and (gh-gah)>=0 and (gh+gah)<0),
            "process_sd":float(fit["process_sd"]),
            "loading_residual_sd":float(fit["loading_residual_sd"]),
        }
    vals=np.asarray([result[sp]["gamma_ah"] for sp in SPECIES],float)
    return {
        "species":result,
        "cross_species_median_gamma_ah":float(np.median(vals)),
        "negative_species":int(np.sum(vals<0)),
        "crossover_species":[sp for sp in SPECIES if result[sp]["crossover_classification"]],
    }


def run(fr,fu,br,obs):
    records=build_frozen_real_records(obs)
    dated=build_dated_cohort(obs,records)
    frames=build_v3_frames(fr,fu,br)
    modes={}
    for days,label in ((0,"exact_date"),(14,"within_14_days")):
        offset=matched_offset(dated,days)
        acc=recalibrate_accuracy(records,offset["delta_image"])
        fit=fit_mode(frames,records,offset["delta_image"],acc)
        modes[label]={
            "offset":offset,
            "accuracy":{
                "sigma_1":float(acc["1"]["sigma"]),
                "sigma_2_5":float(acc["2-5"]["sigma"]),
                "repeat_groups_1":int(acc["1"]["repeat_groups"]),
                "repeat_groups_2_5":int(acc["2-5"]["repeat_groups"]),
            },
            "fit":fit,
        }
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-observation-timing-sensitivity-v1",
        "modes":modes,
        "interpretation_boundary":{
            "primary_same_season_offset_replaced":False,
            "inferential_p_values_recomputed":False,
            "descriptive_sensitivity_only":True,
        },
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-json",type=Path,required=True)
    p.add_argument("--forcing-csv",type=Path,required=True)
    p.add_argument("--breeding-csv",type=Path,required=True)
    p.add_argument("--mapppdr-dir",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text())
    fu=pd.read_csv(a.forcing_csv); br=pd.read_csv(a.breeding_csv)
    obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    out=run(fr,fu,br,obs)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
