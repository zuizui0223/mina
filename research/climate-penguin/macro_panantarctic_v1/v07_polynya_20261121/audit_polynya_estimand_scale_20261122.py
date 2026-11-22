#!/usr/bin/env python3
"""Frozen-input Frisch–Waugh–Lovell exposure scale audit (not a new test).

Uses exact same 439 original isotope+polynya rows, colony and region-by-season
fixed effects, original summer covariates, and unchanged M_P/M_SP slopes.
The 10-percentage-point coefficient is rescaled to the SD of *identifying*
residual polynya exposure. No new variable, model, tail, p value or claim.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import linalg
import verify_frozen_polynya_results as source

ROOT=Path(__file__).resolve().parent


def residualize(values, Q):
    a=np.asarray(values,dtype=float)
    return a-Q@(Q.T@a)


def summarize(fractions):
    z=np.asarray(fractions,dtype=float)
    return {
        "mean_pp":float(z.mean()*100),
        "sd_pop_pp":float(z.std(ddof=0)*100),
        "q10_pp":float(np.quantile(z,.1)*100),
        "q90_pp":float(np.quantile(z,.9)*100),
        "abs_ge_5pp_count":int(np.sum(abs(z)>=.05)),
        "abs_ge_10pp_count":int(np.sum(abs(z)>=.1)),
    }


def audit(root):
    iso, physical, _, _, _, _, _, receipt = source.read_sources(
        root/"frozen_archives",root/"verification_inputs/matched_temporal358.csv")
    merged=iso.merge(
        physical[source.KEYS+[source.REGION,source.POLYNYA]],on=source.KEYS,
        suffixes=("","_physical"),validate="one_to_one")
    assert (len(merged),int(merged[source.POLYNYA].notna().sum()))==(860,439)
    d=merged.loc[merged[source.POLYNYA].notna()].copy().reset_index(drop=True)
    assert (int(d.site_id.nunique()),int(d[source.REGION].nunique()))==(85,11)
    assert d[source.REGION].equals(d[source.REGION+"_physical"])
    # A fresh explicit dummy QR and standard least-squares FWL calculation.
    region_season=d[source.REGION].astype(str)+"__"+d.season.astype(str)
    D=np.column_stack([
        pd.get_dummies(d.site_id.astype(str),dtype=float).to_numpy(),
        pd.get_dummies(region_season,dtype=float).to_numpy()])
    Q,R,_=linalg.qr(D,mode="economic",pivoting=True)
    diagonal=abs(np.diag(R))
    rank=int(sum(diagonal>np.finfo(float).eps*max(D.shape)*diagonal.max()))
    Q=Q[:,:rank]
    p=residualize(d[source.POLYNYA].to_numpy(float),Q)
    y=residualize(d[source.Y_OLD].to_numpy(float),Q)
    raw=d[source.POLYNYA].to_numpy(float)
    result={}
    for name,baseline,prior in [
        ("M_P",source.BASE,-1.0031091429244874),
        ("M_SP",source.BASE+[source.SALINITY],-.9216089250042973)]:
        A=residualize(d[baseline].to_numpy(float),Q)
        xp=p-A@np.linalg.lstsq(A,p,rcond=None)[0]
        yp=y-A@np.linalg.lstsq(A,y,rcond=None)[0]
        slope=float(.1*(xp@yp)/(xp@xp))
        bfull=float(.1*np.linalg.lstsq(np.column_stack([A,p]),y,rcond=None)[0][-1])
        assert abs(slope-bfull)<1e-10
        assert abs(slope-prior)<1e-8, "STOP_FROZEN_SOURCE_ESTIMATE_DRIFT"
        sums={r:float((xp[d[source.REGION].eq(r).to_numpy()]**2).sum())
              for r in sorted(d[source.REGION].unique())}
        informative=[k for k,v in sums.items() if v>1e-16]
        mask=d[source.REGION].isin(informative).to_numpy()
        assert len(informative)==8 and sum(mask)==425
        full=summarize(xp); info=summarize(xp[mask])
        result[name]={
            "slope_per_10pp_per_mil":slope,
            "fully_residualized_439":full,"fully_residualized_425_informative":info,
            "slope_per_1sd_of_439_identifying_exposure_per_mil":float(slope*full["sd_pop_pp"]/10),
            "slope_per_1sd_of_425_identifying_exposure_per_mil":float(slope*info["sd_pop_pp"]/10),
            "ten_pp_in_439_residual_standard_deviations":float(10/full["sd_pop_pp"]),
            "same_frozen_linear_coefficient_reexpressed":True,
        }
    assert abs(result["M_P"]["fully_residualized_439"]["sd_pop_pp"]-1.601131540927318)<1e-8
    assert abs(result["M_SP"]["fully_residualized_439"]["sd_pop_pp"]-1.5879202109614812)<1e-8
    return {
        "status":"PASS_FROZEN_SOURCE_ESTIMAND_SCALE_DESCRIPTIVE_ONLY",
        "audit_date":"2026-11-22","source_commit":source.PINNED_COMMIT,
        "original_observations":439,"original_sites":85,"nominal_regions":11,
        "informative_observations":425,"informative_regions":8,
        "units":"p is a fraction; 1 percentage point corresponds to 0.01",
        "original_raw_fraction":summarize(raw),
        "site_regionseason_FE_only_residual":summarize(p),
        "frozen_slope_rescalings":result,
        "source_zip_sha256":{k:v["sha256"] for k,v in receipt.items() if k.endswith(".zip")},
        "no_new_inference_or_hypothesis":True,
        "not_a_causal_or_independent_biological_test":True,
        "note":"The source-reported 10pp coefficient is correct, but the identifying conditional residual SD is about 1.6pp; no claim about a manipulable 10pp exposure is justified.",
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result=audit(args.root)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],"n":result["original_observations"],
        "results":{k:{"slope10pp":v["slope_per_10pp_per_mil"],
                      "residual_sd_pp":v["fully_residualized_439"]["sd_pop_pp"],
                      "scaled_1sd_mil":v["slope_per_1sd_of_439_identifying_exposure_per_mil"]}
                    for k,v in result["frozen_slope_rescalings"].items()},
        "not_new_inference":True},indent=2))
