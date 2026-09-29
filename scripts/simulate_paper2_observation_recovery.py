#!/usr/bin/env python3
"""Synthetic observation-layer recovery for Paper 2 Gate 2E-B."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

SPECIES=("ADPE","CHPE","GEPE")
WINDOW=(1980,2025)
EXPECTED_GATE0={"ADPE":57,"CHPE":46,"GEPE":49}
EXPECTED_BRIDGED={"ADPE":44,"CHPE":34,"GEPE":29}


def _thirds(start:int,end:int):
    width=end-start+1
    cut1=start+(width//3)-1
    cut2=start+(2*width//3)-1
    return (start,cut1),(cut1+1,cut2),(cut2+1,end)


def _vantage_family(value)->str:
    if pd.isna(value):
        return "unknown"
    value_text=str(value).strip().lower().replace("_"," ")
    if value_text in {"ground","aerial","offshore vessel"}:
        return "direct"
    if value_text in {"ground photo","aerial photo","uav","vhr","landsat","sentinel"}:
        return "image_based"
    raise ValueError(f"unrecognized vantage: {value}")


def _accuracy_group(value)->str:
    if pd.isna(value):
        raise ValueError("missing accuracy in frozen count record")
    code=int(float(value))
    if code==1:
        return "1"
    if 2<=code<=5:
        return "2-5"
    raise ValueError(f"invalid accuracy code: {value}")


def build_frozen_observation_metadata(obs:pd.DataFrame)->pd.DataFrame:
    """Reconstruct the frozen 107-unit record structure and discard count magnitudes."""
    required={"site_id","species_id","type","count","year","season","vantage","accuracy"}
    _require_columns(obs,required)
    nest=obs[
        obs["species_id"].isin(SPECIES)
        & obs["type"].eq("nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest["season"]=pd.to_numeric(nest["season"],errors="coerce")

    gate0=[]
    for (site,species),local in nest.dropna(subset=["year"]).groupby(
        ["site_id","species_id"]
    ):
        years=sorted({int(v) for v in local["year"]})
        if len(years)>=5 and max(years)-min(years)>=10:
            gate0.append((str(site),str(species)))
    gate0_by_species={
        sp:sum(species==sp for _,species in gate0)
        for sp in SPECIES
    }
    if gate0_by_species!=EXPECTED_GATE0:
        raise ValueError(
            f"Gate0 species drift: {gate0_by_species} != {EXPECTED_GATE0}"
        )

    grouped={
        (str(site),str(species)):local
        for (site,species),local in nest.groupby(["site_id","species_id"])
    }
    start,end=WINDOW
    first,_,last=_thirds(start,end)
    bridged=[]
    for site,species in gate0:
        local=grouped[(site,species)]
        seasons=sorted({
            int(v) for v in local["season"].dropna()
            if start<=int(v)<=end
        })
        if not seasons:
            continue
        span=max(seasons)-min(seasons)
        has_first=any(first[0]<=v<=first[1] for v in seasons)
        has_last=any(last[0]<=v<=last[1] for v in seasons)
        if len(seasons)>=5 and span>=10 and has_first and has_last:
            bridged.append((site,species))
    bridged_by_species={
        sp:sum(species==sp for _,species in bridged)
        for sp in SPECIES
    }
    if bridged_by_species!=EXPECTED_BRIDGED:
        raise ValueError(
            f"bridged species drift: {bridged_by_species} != {EXPECTED_BRIDGED}"
        )

    keys=set(bridged)
    keep_mask=nest.apply(
        lambda row:(str(row["site_id"]),str(row["species_id"])) in keys,
        axis=1,
    )
    cohort=nest[
        keep_mask
        & nest["season"].between(start,end,inclusive="both")
    ].copy()

    out=pd.DataFrame({
        "site_id":cohort["site_id"].astype(str),
        "species_id":cohort["species_id"].astype(str),
        "season":cohort["season"].astype(int),
        "vantage_family":cohort["vantage"].map(_vantage_family),
        "accuracy_group":cohort["accuracy"].map(_accuracy_group),
    })
    out["group_id"]=(
        out["site_id"]+"|"+out["species_id"]+"|"+out["season"].astype(str)
    )
    columns=[
        "group_id","site_id","species_id","season",
        "vantage_family","accuracy_group",
    ]
    return out[columns].sort_values(
        ["species_id","site_id","season","vantage_family","accuracy_group"]
    ).reset_index(drop=True)


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


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    result=pyreadr.read_r(str(path))
    if expected in result:
        frame=result[expected]
    elif len(result)==1:
        frame=next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(result)}")
    if not isinstance(frame,pd.DataFrame):
        raise TypeError(expected)
    return frame


def _metadata_support(metadata:pd.DataFrame)->dict:
    family=metadata["vantage_family"].value_counts().to_dict()
    mixed_by_species={sp:0 for sp in SPECIES}
    mixed_total=0
    repeated_groups=0
    for _,local in metadata.groupby("group_id",sort=True):
        if len(local)>=2:
            repeated_groups+=1
        families=set(local["vantage_family"].astype(str))
        if {"direct","image_based"}<=families:
            mixed_total+=1
            sp=str(local["species_id"].iloc[0])
            mixed_by_species[sp]=mixed_by_species.get(sp,0)+1
    return {
        "records":int(len(metadata)),
        "bridged_units":int(
            metadata[["site_id","species_id"]].drop_duplicates().shape[0]
        ),
        "season_groups":int(metadata["group_id"].nunique()),
        "repeated_groups":int(repeated_groups),
        "direct_records":int(family.get("direct",0)),
        "image_based_records":int(family.get("image_based",0)),
        "unknown_vantage_records":int(family.get("unknown",0)),
        "mixed_direct_image_groups":int(mixed_total),
        "mixed_direct_image_groups_by_species":{
            sp:int(mixed_by_species.get(sp,0)) for sp in SPECIES
        },
    }


def run_observation_audit(
    obs:pd.DataFrame,
    *,
    replicates:int=200,
    seed_offset:int=3000000,
)->dict:
    """Rebuild frozen metadata, verify Gate 2B support, then run synthetic recovery."""
    metadata=build_frozen_observation_metadata(obs)
    support=_metadata_support(metadata)

    expected={
        "records":2100,
        "bridged_units":107,
        "season_groups":1721,
        "repeated_groups":273,
        "direct_records":1889,
        "image_based_records":149,
        "unknown_vantage_records":62,
        "mixed_direct_image_groups":41,
        "mixed_direct_image_groups_by_species":{
            "ADPE":9,"CHPE":10,"GEPE":22,
        },
    }
    if support!=expected:
        raise ValueError(f"observation metadata drift: {support} != {expected}")

    recovery=evaluate_observation_recovery(
        metadata,
        replicates=replicates,
        seed_offset=seed_offset,
    )
    return {
        "schema_version":1,
        "audit_id":"mina-paper2-observation-recovery-v1",
        "metadata":support,
        "recovery":recovery,
        "decision":{
            "observation_layer_recoverable":bool(recovery["gate"]["passes"]),
            "no_real_demographic_magnitudes_opened":True,
        },
    }


def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--mapppdr-dir",required=True,type=Path)
    parser.add_argument("--out-json",required=True,type=Path)
    parser.add_argument("--replicates",type=int,default=200)
    args=parser.parse_args()

    obs=_load_rda(args.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    result=run_observation_audit(obs,replicates=args.replicates)
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result["decision"]["observation_layer_recoverable"]:
        raise SystemExit("observation recovery gate failed")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
