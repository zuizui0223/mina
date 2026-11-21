#!/usr/bin/env python3
"""Reconstruct Youngflesh-2026 Landsat-derived delta15N proxy from MD5-verified
publisher inputs. This is a transparent PLSR replication attempt, not the
authors' missing Stan DI posterior or a diet/sea-ice/salinity effect analysis.
"""
import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error

BANDS = ["blue", "green", "red", "nir", "swir1", "swir2"]
WAVES = np.arange(350, 2501)
SENSORS = {
    4: ("L4_TM_RSR.xlsx", "L4 TM"),
    5: ("L5_TM_RSR.xlsx", "L5 TM"),
    7: ("L7_ETM_RSR.xlsx", "L7"),
}

def weighted_spectra(sia, xlsx, suffix):
    wavecols = [f"Wave_{v}" for v in WAVES]
    if not all(n in sia.columns for n in wavecols):
        raise ValueError("Missing original SIA spectral wavelength columns")
    spectra = sia[wavecols].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    factors = []
    for b in ("Blue", "Green", "Red", "NIR", "SWIR(5)", "SWIR(7)"):
        sheet = f"{b}-{suffix}"
        tab = pd.read_excel(xlsx, sheet_name=sheet)
        if "Wavelength" not in tab.columns or len(tab.columns) < 2:
            raise ValueError(f"Missing original RSR wavelength / band in {sheet}")
        t = tab.iloc[:, :2].copy()
        t.columns = ["Wavelength", "response"]
        t["Wavelength"] = pd.to_numeric(t["Wavelength"], errors="raise")
        t["response"] = pd.to_numeric(t["response"], errors="raise")
        if t.Wavelength.duplicated().any():
            raise ValueError(f"Duplicate wavelengths: {sheet}")
        weights = t.set_index("Wavelength")["response"].reindex(WAVES).fillna(0).to_numpy(dtype=float)
        if not np.isfinite(weights).all() or weights.sum() <= 0:
            raise ValueError(f"Invalid response weights: {sheet}")
        factors.append(weights / weights.sum())
    x = spectra @ np.stack(factors, axis=1)
    if not np.isfinite(x).all():
        raise ValueError("Nonfinite lab spectra / band-response")
    return x

def fits_and_predictions(x, y, px, seed=20261117, nrep=100):
    if len(y) < 12 or len(np.unique(y)) < 8:
        raise ValueError("Insufficient original isotope calibration support")
    if not (np.isfinite(x).all() and np.isfinite(y).all() and np.isfinite(px).all()):
        raise ValueError("Nonfinite calibration or image reflectances")
    if x.shape[1] != 6 or px.shape[1] != 6:
        raise ValueError("Six Landsat bands required")
    rng = np.random.default_rng(seed)
    edges = np.unique(np.quantile(y, [0, .2, .4, .6, .8, 1]))
    if len(edges) < 4:
        raise ValueError("Cannot form stable isotope stratification bins")
    bins = np.digitize(y, edges[1:-1], right=False)
    rows=[]
    for k in range(nrep):
        train=[]
        for b in np.unique(bins):
            idx=np.flatnonzero(bins==b)
            if len(idx) < 2:
                raise ValueError("Isotope stratum with fewer than 2 originals")
            n=max(1,min(len(idx)-1,int(np.floor(.65*len(idx)))))
            train.extend(rng.choice(idx,size=n,replace=False).tolist())
        train=np.array(sorted(set(train)),dtype=int)
        test=np.setdiff1d(np.arange(len(y)),train)
        if len(train)<=6 or len(test)<3:
            raise ValueError("Insufficient CV samples")
        m=PLSRegression(n_components=5,scale=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",category=UserWarning)
            m.fit(x[train],y[train])
            yp=m.predict(x[test]).ravel()
        rows.append({"replicate":k,"n_train":int(len(train)),"n_test":int(len(test)),
                     "holdout_rmse":float(np.sqrt(mean_squared_error(y[test],yp))),
                     "holdout_train_mean_rmse":float(np.sqrt(mean_squared_error(y[test],np.full(len(test),np.mean(y[train])))))})
    full=PLSRegression(n_components=5,scale=False).fit(x,y)
    pred=full.predict(px).ravel()
    return rows,pred,full

def reconstruct(root, output, nrep=100):
    root=Path(root);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    lab=pd.read_csv(root/"SIA_spectra.csv")
    lab["d_15N"]=pd.to_numeric(lab["d_15N"],errors="raise")
    lab=lab.loc[lab.d_15N.notna()].reset_index(drop=True)
    px=pd.read_csv(root/"original_landsat_pixels.csv")
    require=["site_id","season","satellite","year","month","day","cell"]+BANDS
    if not set(require).issubset(px):
        raise ValueError(f"Missing Landsat columns: {set(require)-set(px)}")
    for name in BANDS:
        px[name]=pd.to_numeric(px[name],errors="coerce")
    px["season"]=pd.to_numeric(px.season,errors="raise").astype(int)
    px["satellite"]=pd.to_numeric(px.satellite,errors="raise").astype(int)
    px["month"]=pd.to_numeric(px.month,errors="raise").astype(int)
    px["day"]=pd.to_numeric(px.day,errors="raise").astype(int)
    if not px.month.isin([11,12,1,2]).all():
        raise ValueError("Landsat archive has images outside published Nov-Feb season")
    if not px.satellite.isin(list(SENSORS)).all():
        raise ValueError("Unsupported Landsat sensor in original RDS")
    if not np.isfinite(px[BANDS].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite source image reflectances: diagnose selection before fit")
    metrics=[]
    px["predicted_d15N_plsr5"]=np.nan
    for sensor,(file,suffix) in SENSORS.items():
        a=px.satellite==sensor
        if a.sum()==0:continue
        x=weighted_spectra(lab,root/file,suffix)
        yy=lab.d_15N.to_numpy(dtype=float)
        scores,pred,m=fits_and_predictions(x,yy,px.loc[a,BANDS].to_numpy(dtype=float),seed=20261117+sensor,nrep=nrep)
        px.loc[a,"predicted_d15N_plsr5"]=pred
        mdf=pd.DataFrame(scores)
        mdf["sensor"]=sensor
        metrics.append(mdf)
    if not np.isfinite(px.predicted_d15N_plsr5).all():
        raise ValueError("Missing source-derived isotope predictions")
    metrics=pd.concat(metrics,ignore_index=True)
    metrics.to_csv(output/"plsr5_stratified_random_holdout_scores.csv",index=False)
    day_keys=["site_id","season","year","month","day"]
    daily=px.groupby(day_keys,dropna=False).agg(
        n_original_pixels=("predicted_d15N_plsr5","size"),
        predicted_d15N_daily_mean=("predicted_d15N_plsr5","mean"),
        predicted_d15N_daily_sd=("predicted_d15N_plsr5","std"),
        n_sensors=("satellite","nunique"),
    ).reset_index()
    daily.to_csv(output/"source_d15N_proxy_site_season_day.csv",index=False)
    # Default is day-equal. Pixel-equal shown solely as multiplicity sensitivity.
    sea=daily.groupby(["site_id","season"],dropna=False).agg(
        n_observed_days=("predicted_d15N_daily_mean","size"),
        n_source_pixels=("n_original_pixels","sum"),
        predicted_d15N_season_day_equal=("predicted_d15N_daily_mean","mean"),
        sd_across_observed_days=("predicted_d15N_daily_mean","std"),
    ).reset_index()
    pc=px.groupby(["site_id","season"],dropna=False)["predicted_d15N_plsr5"].mean().rename("predicted_d15N_season_pixel_equal")
    sea=sea.merge(pc,left_on=["site_id","season"],right_index=True,validate="one_to_one")
    sea.to_csv(output/"source_d15N_proxy_site_season.csv",index=False)
    cv=metrics.groupby("sensor").agg(n_replicates=("replicate","size"),
                                    median_holdout_rmse=("holdout_rmse","median"),
                                    median_mean_null_rmse=("holdout_train_mean_rmse","median")).reset_index()
    receipt={
        "status":"SOURCE_LAB_SPECTRA_TO_LANDSAT_DELTA15N_PROXY_RECONSTRUCTED_NOT_ORIGINAL_DI",
        "calibration_isotope_n":int(len(lab)), "source_landsat_pixel_rows":int(len(px)),
        "source_landsat_sites":int(px.site_id.nunique()),"source_seasons":int(sea.shape[0]),
        "source_site_days":int(daily.shape[0]),"n_repeats_per_sensor":int(nrep),
        "sensors":cv.to_dict(orient="records"),"observed_season_year_min":int(sea.season.min()),"observed_season_year_max":int(sea.season.max()),
        "main_outcome":"predicted delta15N isotope proxy. NOT author's hierarchical posterior DI and NOT a measured prey fraction.",
        "uncertainty":"random calibration holdout; NO validated independent site/region or dietary composition calibration",
        "forward_diet_salinity_effect":"NOT TESTED",
    }
    (output/"source_plsr5_d15N_proxy_receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(receipt,indent=2,ensure_ascii=False))
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root")
    p.add_argument("--out")
    p.add_argument("--nrep",type=int,default=100)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        rng=np.random.default_rng(1)
        X=rng.normal(size=(60,6)); y=10+X[:,0]*2-X[:,1]+rng.normal(size=60)*.1
        rows,pred,model=fits_and_predictions(X,y,X[:9],nrep=4)
        assert len(rows)==4 and len(pred)==9 and np.isfinite(pred).all()
        print("PASS synthetic PLSR5 holdout and six-band inference")
    else:
        if not a.root or not a.out: p.error("--root/--out required")
        reconstruct(a.root,a.out,nrep=a.nrep)
