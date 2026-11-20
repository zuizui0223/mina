#!/usr/bin/env python3
"""Separate source-only 103 ORIGINAL GUANO lab spectra -> Landsat8 OLI 6band PLSR5.
Never reads any 2013+ images or any Antarctic coastal-polynya exposures/associations.
This does NOT transfer L7 ETM+ coefficients directly to the different OLI sensor.
Original model: reconstruct_isotope_proxy.py, 103 samples, 5-component sklearn PLS,
scale=False; calibration eligibility rule frozen before fitting new L8 spectra.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from sklearn.cross_decomposition import PLSRegression
from reconstruct_isotope_proxy import WAVES, weighted_spectra, fits_and_predictions

BAND_IDS=(2,3,4,5,6,7)
BAND_NAMES=("blue","green","red","nir","swir1","swir2")
EXPECTED_CENTERS_NM=(481,560,654,864,1608,2197)
SOURCE_DESCRIPTION="EUMETSAT NWP SAF SRF: Landsat 8 OLI response derived from NASA Ball_BA_RSR.v1.1.xlsx, wavenumbers cm^-1"
MIN_ORIGINAL_LAB_SAMPLES=103
SEED_L7=20261117+7
SEED_L8=20261117+8
N_REPS=100
FROZEN_L8_MAX_CV_RMSE=2.0
EXPECTED_L7_CV_MEDIAN=1.742
# This is a lab spectral calibration gate only; no actual L8 colony pixels evaluated.

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_srf(path):
    lines=Path(path).read_text(encoding="utf-8",errors="replace").splitlines()
    rows=[]
    for line in lines:
        parts=line.split()
        if len(parts)!=2:continue
        try:wn,resp=float(parts[0]),float(parts[1])
        except ValueError:continue
        if wn>1e3 and np.isfinite(wn) and np.isfinite(resp):
            rows.append((wn,resp))
    if len(rows)<30:
        raise ValueError(f"Official L8 OLI SRF has <30 numeric wavenumber rows: {path}")
    arr=np.asarray(rows,dtype=float)
    if (arr[:,1]<-1e-9).any():
        raise ValueError("Official L8 OLI RSR contains negative response outside publisher clamp")
    lam_nm=1e7/arr[:,0]
    order=np.argsort(lam_nm)
    lam_nm=lam_nm[order];responses=np.clip(arr[:,1][order],0,None)
    if len(np.unique(lam_nm))!=len(lam_nm):
        raise ValueError("Duplicated true wavelength in L8 OLI RSR")
    weights=np.interp(WAVES,lam_nm,responses,left=0,right=0)
    if weights.sum()<=0:raise ValueError("L8 OLI source weights empty")
    center=float(np.dot(WAVES,weights)/weights.sum())
    return weights/weights.sum(),center,len(arr)

def main(a):
    root=Path(a.original_lab)
    lab=pd.read_csv(root/"SIA_spectra.csv")
    lab["d_15N"]=pd.to_numeric(lab.d_15N,errors="coerce")
    lab=lab.loc[lab.d_15N.notna()].reset_index(drop=True)
    if len(lab)!=MIN_ORIGINAL_LAB_SAMPLES:
        raise ValueError(f"Original lab isotope source changed, {len(lab)} vs 103")
    y=lab.d_15N.to_numpy(float)
    xs=lab[[f"Wave_{i}" for i in WAVES]].to_numpy(dtype=float)
    if xs.shape!=(103,2151) or not np.isfinite(xs).all():
        raise ValueError("Original lab 103 measured reflectance spectra not 350..2500 nm")
    l7=weighted_spectra(lab,root/"L7_ETM_RSR.xlsx","L7")
    checks=[]
    columns=[]
    for band,mid in zip(BAND_IDS,EXPECTED_CENTERS_NM):
        f=Path(a.l8_source_srf)/f"rtcoef_landsat_8_oli_srf_ch{band:02}.txt"
        if not f.exists():raise ValueError("Original unmodified official L8 OLI SRF file missing "+str(f))
        w,center,n=read_srf(f)
        if abs(center-mid)>14:raise ValueError(f"Official OLI band source center changed: {band} {center:.3f} vs expected {mid}")
        checks.append({"L8_band":int(band),"band_name":BAND_NAMES[BAND_IDS.index(band)],
                       "source_file":f.name,"source_sha256":sha256(f),
                       "wavenumber_sample_rows":int(n),"source_band_center_nm":center})
        columns.append(xs@w)
    l8=np.column_stack(columns)
    if not np.isfinite(l8).all() or l8.shape!=(103,6):raise ValueError("Unusable synthesized original guano lab L8 OLI bands")
    # Same 103 original samples; same six band count, five PLS components, no new imagery Y.
    score7,pred7,model7=fits_and_predictions(l7,y,l7[:1],seed=SEED_L7,nrep=N_REPS)
    score8,pred8,model8=fits_and_predictions(l8,y,l8[:1],seed=SEED_L8,nrep=N_REPS)
    m7=pd.DataFrame(score7);m8=pd.DataFrame(score8)
    summary={}
    for label,frame in (("L7_ETM_original","L7" if False else m7),("L8_OLI_new_RSR",m8)):
        summary[label]={
          "stratified_100_holdout_median_RMSE":float(frame.holdout_rmse.median()),
          "stratified_100_holdout_median_train_mean_null_RMSE":float(frame.holdout_train_mean_rmse.median()),
          "all_100_holdout_median_absolute_error_threshold_units":"delta15N per-mille"
        }
    l7_gap=abs(summary["L7_ETM_original"]["stratified_100_holdout_median_RMSE"]-EXPECTED_L7_CV_MEDIAN)
    # The original L7 rounded baseline must match same software method, not force an identical split output.
    if l7_gap>0.05:
        raise ValueError(f"Frozen source L7 PLSR calibration not reproducible: {summary['L7_ETM_original']}")
    eligible=(
       summary["L8_OLI_new_RSR"]["stratified_100_holdout_median_RMSE"]<FROZEN_L8_MAX_CV_RMSE
       and summary["L8_OLI_new_RSR"]["stratified_100_holdout_median_RMSE"]<
           summary["L8_OLI_new_RSR"]["stratified_100_holdout_median_train_mean_null_RMSE"]
    )
    frozen={
       "status":"PASS_L8_103_GUANO_LAB_SPECTRAL_CALIBRATION_GATE_SOURCE_ONLY" if eligible
                  else "NO_GO_L8_LAB_SPECTRAL_CALIBRATION_GATE",
       "l8_sensor_is_not_l7_ETM":True,
       "original_103_lab_SIA_spectra_sha256":sha256(root/"SIA_spectra.csv"),
       "original_L7_RSR_sha256":sha256(root/"L7_ETM_RSR.xlsx"),
       "original_103_sample_n":len(lab),
       "calibration_source":SOURCE_DESCRIPTION,
       "l8_RSR_source_files":checks,
       "feature_order":list(BAND_NAMES),"origin_reflectance_units":"original guano measured hyperspectral reflectance convolved with each true source RSR",
       "PLSR_components":5,"sklearn_version":sklearn.__version__,
       "PLSRegression_scale":False,"L7_seed":SEED_L7,"L8_seed":SEED_L8,
       "original_103_lab_isotope_response_already_known_not_future_2013_2021_Y":True,
       "comparison":summary,"l8_RMSE_max_frozen":FROZEN_L8_MAX_CV_RMSE,
       "no_2013_2021_L8_image_pixel_opened":True,
       "no_2013_2021_isotope_colony_proxy_computed":True,
       "no_polynya_or_environment_test":True,
       "no_L7_confirmation_claimed":True,
       "no_future_image_eligibility_before_guano_QA":True
    }
    # A fixed spectroscopic mapping to be ALLOWED only after independent guano ROI / image unit QA.
    if eligible:
        frozen["frozen_coefficients_to_use_only_after_image_QA"]={
           "PLSR_sklearn_coef_matrix":np.asarray(model8.coef_,dtype=float).tolist(),
           "PLSR_sklearn_x_mean":np.asarray(model8._x_mean,dtype=float).tolist(),
           "PLSR_sklearn_x_std":np.asarray(model8._x_std,dtype=float).tolist(),
           "PLSR_sklearn_intercept":np.asarray(model8.intercept_,dtype=float).tolist(),
           "formula":"model8.predict(new_OLI_six_bands), EXACT fitted five-components same source; new image QA prior",
        }
    a.out.mkdir(parents=True,exist_ok=True)
    pd.concat([m7.assign(sensor="L7_legacy"),m8.assign(sensor="L8_new")],ignore_index=True).to_csv(
      a.out/"LAB_ONLY_103_original_guano_L7_L8_100_fixed_fold_CV.csv",index=False)
    (a.out/"L8_OLI_ORIGINAL_103_LAB_SPECTRAL_CALIBRATION_GATE.json").write_text(json.dumps(frozen,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in frozen.items() if k!="frozen_coefficients_to_use_only_after_image_QA"},indent=2,ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-lab",type=Path,required=True)
    p.add_argument("--l8-source-srf",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
