#!/usr/bin/env python3
"""Synthetic observation-layer recovery for Paper 2 Gate 2E-B."""
from __future__ import annotations

import numpy as np
import pandas as pd

DELTA_IMAGE_TRUTH=float(np.log(1.15))
SIGMA_1_TRUTH=float(np.log(1.05))
SIGMA_2PLUS_TRUTH=float(np.log(1.25))


def _require_columns(frame:pd.DataFrame,columns:set[str])->None:
    missing=columns-set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")


def simulate_observation_records(
    metadata:pd.DataFrame,
    *,
    delta_image:float,
    sigma1:float,
    sigma2plus:float,
    seed:int,
)->pd.DataFrame:
    """Generate synthetic log observations on the frozen record structure."""
    _require_columns(
        metadata,
        {"group_id","species_id","vantage_family","accuracy_group"},
    )
    local=metadata.reset_index(drop=True).copy()
    rng=np.random.default_rng(seed)
    group_ids=sorted(local["group_id"].astype(str).unique())
    latent={
        group:float(rng.normal(8.0,1.0))
        for group in group_ids
    }

    values=[]
    for row in local.to_dict(orient="records"):
        family=str(row["vantage_family"])
        accuracy=str(row["accuracy_group"])
        if accuracy=="1":
            sigma=float(sigma1)
        elif accuracy=="2-5":
            sigma=float(sigma2plus)
        else:
            raise ValueError(f"unsupported accuracy group: {accuracy}")
        offset=float(delta_image) if family=="image_based" else 0.0
        values.append(
            latent[str(row["group_id"])]
            +offset
            +float(rng.normal(0.0,sigma))
        )
    local["log_observed"]=values
    return local


def estimate_method_offset(frame:pd.DataFrame)->dict:
    """Estimate one shared image offset from within-season mixed-family contrasts."""
    _require_columns(
        frame,
        {"group_id","species_id","vantage_family","log_observed"},
    )
    known=frame[
        frame["vantage_family"].isin(["direct","image_based"])
    ].copy()
    differences=[]
    species_differences:dict[str,list[float]]={}
    for _,local in known.groupby("group_id",sort=True):
        direct=local.loc[
            local["vantage_family"].eq("direct"),"log_observed"
        ]
        image=local.loc[
            local["vantage_family"].eq("image_based"),"log_observed"
        ]
        if len(direct)==0 or len(image)==0:
            continue
        diff=float(image.mean()-direct.mean())
        differences.append(diff)
        species=str(local["species_id"].iloc[0])
        species_differences.setdefault(species,[]).append(diff)

    if not differences:
        raise ValueError("no mixed direct-image groups")
    return {
        "delta_image":float(np.mean(differences)),
        "mixed_groups":int(len(differences)),
        "group_differences":differences,
        "by_species":{
            sp:{
                "mixed_groups":len(values),
                "delta_image":float(np.mean(values)),
            }
            for sp,values in sorted(species_differences.items())
        },
    }


def estimate_accuracy_scales(
    frame:pd.DataFrame,
    *,
    delta_image:float,
)->dict:
    """Estimate collapsed accuracy scales from repeated within-season records."""
    _require_columns(
        frame,
        {"group_id","vantage_family","accuracy_group","log_observed"},
    )
    known=frame[
        frame["vantage_family"].isin(["direct","image_based"])
    ].copy()
    known["corrected"]=(
        pd.to_numeric(known["log_observed"],errors="coerce")
        -float(delta_image)*known["vantage_family"].eq("image_based").astype(float)
    )
    out={}
    for accuracy in ("1","2-5"):
        sse=0.0
        df=0
        repeat_groups=0
        subset=known[known["accuracy_group"].astype(str).eq(accuracy)]
        for _,local in subset.groupby("group_id",sort=True):
            values=local["corrected"].dropna().to_numpy(dtype=float)
            if len(values)<2:
                continue
            repeat_groups+=1
            mean=float(values.mean())
            sse+=float(np.square(values-mean).sum())
            df+=len(values)-1
        if df<=0:
            raise ValueError(f"no repeated groups for accuracy {accuracy}")
        out[accuracy]={
            "sigma":float(np.sqrt(sse/df)),
            "repeat_groups":int(repeat_groups),
            "residual_df":int(df),
        }
    return out


def fit_observation_calibration(frame:pd.DataFrame)->dict:
    method=estimate_method_offset(frame)
    accuracy=estimate_accuracy_scales(
        frame,
        delta_image=method["delta_image"],
    )
    return {
        "delta_image":method["delta_image"],
        "mixed_groups":method["mixed_groups"],
        "by_species":method["by_species"],
        "accuracy":accuracy,
    }


def _q(values:list[float],q:float)->float:
    arr=np.asarray(values,dtype=float)
    if arr.size==0:
        raise ValueError("empty summary vector")
    return float(np.quantile(arr,q))


def evaluate_observation_recovery(
    metadata:pd.DataFrame,
    *,
    replicates:int=200,
    seed_offset:int=0,
)->dict:
    """Run the frozen method-offset and accuracy-scale recovery experiment."""
    if replicates<2:
        raise ValueError("replicates must be >=2")

    offset_hats=[]
    null_hats=[]
    sigma1_hats=[]
    sigma2_hats=[]
    by_species:dict[str,list[float]]={}
    finite=0

    for rep in range(replicates):
        sim=simulate_observation_records(
            metadata,
            delta_image=DELTA_IMAGE_TRUTH,
            sigma1=SIGMA_1_TRUTH,
            sigma2plus=SIGMA_2PLUS_TRUTH,
            seed=seed_offset+rep,
        )
        fit=fit_observation_calibration(sim)
        offset_hats.append(float(fit["delta_image"]))
        sigma1_hats.append(float(fit["accuracy"]["1"]["sigma"]))
        sigma2_hats.append(float(fit["accuracy"]["2-5"]["sigma"]))
        for sp,meta in fit["by_species"].items():
            by_species.setdefault(sp,[]).append(float(meta["delta_image"]))

        null_sim=simulate_observation_records(
            metadata,
            delta_image=0.0,
            sigma1=SIGMA_1_TRUTH,
            sigma2plus=SIGMA_2PLUS_TRUTH,
            seed=seed_offset+100000+rep,
        )
        null_fit=fit_observation_calibration(null_sim)
        null_hats.append(float(null_fit["delta_image"]))

        vals=[
            fit["delta_image"],
            fit["accuracy"]["1"]["sigma"],
            fit["accuracy"]["2-5"]["sigma"],
            null_fit["delta_image"],
        ]
        if all(np.isfinite(float(v)) for v in vals):
            finite+=1

    med_offset=_q(offset_hats,0.5)
    med_sigma1=_q(sigma1_hats,0.5)
    med_sigma2=_q(sigma2_hats,0.5)
    med_null=_q(null_hats,0.5)

    first_fit=fit_observation_calibration(
        simulate_observation_records(
            metadata,
            delta_image=DELTA_IMAGE_TRUTH,
            sigma1=SIGMA_1_TRUTH,
            sigma2plus=SIGMA_2PLUS_TRUTH,
            seed=seed_offset+999999,
        )
    )

    summary={
        "replicates":int(replicates),
        "truth":{
            "delta_image":DELTA_IMAGE_TRUTH,
            "sigma_1":SIGMA_1_TRUTH,
            "sigma_2_5":SIGMA_2PLUS_TRUTH,
        },
        "support":{
            "mixed_direct_image_groups":int(first_fit["mixed_groups"]),
            "accuracy_1_repeat_groups":int(
                first_fit["accuracy"]["1"]["repeat_groups"]
            ),
            "accuracy_2_5_repeat_groups":int(
                first_fit["accuracy"]["2-5"]["repeat_groups"]
            ),
            "accuracy_1_residual_df":int(
                first_fit["accuracy"]["1"]["residual_df"]
            ),
            "accuracy_2_5_residual_df":int(
                first_fit["accuracy"]["2-5"]["residual_df"]
            ),
        },
        "offset":{
            "truth":DELTA_IMAGE_TRUTH,
            "median":med_offset,
            "bias":float(med_offset-DELTA_IMAGE_TRUTH),
            "q05":_q(offset_hats,0.05),
            "q95":_q(offset_hats,0.95),
            "correct_sign_fraction":float(
                np.mean(np.asarray(offset_hats)>0.0)
            ),
            "by_species":{
                sp:{
                    "median":_q(values,0.5),
                    "q05":_q(values,0.05),
                    "q95":_q(values,0.95),
                }
                for sp,values in sorted(by_species.items())
            },
        },
        "null_offset":{
            "median":med_null,
            "q05":_q(null_hats,0.05),
            "q95":_q(null_hats,0.95),
        },
        "accuracy":{
            "1":{
                "truth":SIGMA_1_TRUTH,
                "median":med_sigma1,
                "relative_bias":float(
                    (med_sigma1-SIGMA_1_TRUTH)/SIGMA_1_TRUTH
                ),
            },
            "2-5":{
                "truth":SIGMA_2PLUS_TRUTH,
                "median":med_sigma2,
                "relative_bias":float(
                    (med_sigma2-SIGMA_2PLUS_TRUTH)/SIGMA_2PLUS_TRUTH
                ),
            },
        },
        "finite_estimate_fraction":float(finite/replicates),
    }
    checks={
        "offset_bias":abs(summary["offset"]["bias"])<=0.03,
        "offset_sign":summary["offset"]["correct_sign_fraction"]>=0.95,
        "null_center":abs(summary["null_offset"]["median"])<=0.02,
        "null_contains_zero":(
            summary["null_offset"]["q05"]<=0.0<=summary["null_offset"]["q95"]
        ),
        "accuracy_1_bias":abs(
            summary["accuracy"]["1"]["relative_bias"]
        )<=0.15,
        "accuracy_2_5_bias":abs(
            summary["accuracy"]["2-5"]["relative_bias"]
        )<=0.30,
        "finite":summary["finite_estimate_fraction"]>=1.0,
    }
    summary["gate"]={"passes":bool(all(checks.values())),"checks":checks}
    return summary
