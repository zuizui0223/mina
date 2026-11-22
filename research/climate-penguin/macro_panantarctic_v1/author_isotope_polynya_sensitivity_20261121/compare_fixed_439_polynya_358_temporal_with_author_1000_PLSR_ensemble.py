#!/usr/bin/env python3
"""Fixed historical source, same 439 and 358 site-season rows.

Replace original single-Python PLSR5 optical isotope proxy Y with AUTHOR-style
R pls::oscorespls 1,000 65%-train five-component ensemble per original
L4/L5/L7 sensor, reconstructed from original previously guano-selected RDS.

NOT an independent post-2013 test. NO novel guano label, no current L8 pixel,
no causal climate-foodweb inference. This code must only run after prefreeze
FROZEN_AUTHOR_1000_PLSR_MEASUREMENT_SENSITIVITY_BEFORE_NEW_Y.md.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import t
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parent
OLD_ISOTOPE_ZIP_SHA="dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
OLD_PHY_ZIP_SHA="702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96"
OLD_L7_R1000_ZIP_SHA="ac1199ad312df63173f7be73452ccbb5e01b7c55f29d3413ede63e1a1b665669"
P="direct_DEEPAA_coastal_polynya_fraction"
SAL="GLORYS_NovFeb_salinity"
Y_OLD="predicted_d15N_season_day_equal"
Y_NEW="author_R1000_delta15N_season_day_equal"
BASE=["mean_doy_centered","mean_doy_sq","GLORYS_NovFeb_thetao_C",
      "author_SIC_150km_NovFeb_center_approx_fraction"]
TEMPERATURE_TIME_BASE=BASE+[SAL]
SENSORS=[4,5,7]
BANDS=["blue","green","red","nir","swir1","swir2"]
COEFS=["intercept","B1","B2","B3","B4","B5","B7"]
PIXEL_KEYS=["site_id","season","year","month","day"]
FE_TOL=1e-10
NENSEMBLE=1000

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def from_zip(path,expected,filename):
    if sha(path)!=expected:raise ValueError(f"Frozen source artifact SHA drift for {filename}")
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError("Old GitHub results ZIP native CRC failed")
        matches=[n for n in z.namelist() if n==filename or n.endswith("/"+filename)]
        if len(matches)!=1:raise ValueError("Missing/duplicate source member "+filename)
        return pd.read_csv(io.BytesIO(z.read(matches[0])),low_memory=False)

def source(a):
    if not (ROOT/"FROZEN_AUTHOR_1000_PLSR_MEASUREMENT_SENSITIVITY_BEFORE_NEW_Y.md").is_file():
        raise ValueError("Pre-frozen method sensitivity spec missing")
    iso=from_zip(a.old_isotope_zip,OLD_ISOTOPE_ZIP_SHA,
        "matched_860_original_isotope_ocean_ice_site_seasons.csv")
    ph=from_zip(a.old_physical_zip,OLD_PHY_ZIP_SHA,
        "source_original_860_site_seasons_true_DEEPAA100km_no_optical_Y.csv")
    if (len(iso),iso.site_id.nunique(),iso.source_region.nunique())!=(860,88,13):
        raise ValueError("Original merged 860 site-seasons, 88 sites 13 regions drift")
    if not (len(ph)==860 and ph.site_id.nunique()==88 and ph.source_region.nunique()==13):
        raise ValueError("Original independent physical 860 support drift")
    if iso.duplicated(["site_id","season"]).any() or ph.duplicated(["site_id","season"]).any():
        raise ValueError("Duplicated source site/season")
    old=iso.merge(ph[["site_id","season","source_region",P]],on=["site_id","season"],
        suffixes=("","_source"),validate="one_to_one")
    if len(old)!=860 or not old.source_region.eq(old.source_region_source).all():
        raise ValueError("Physical exposure source vs frozen old isotope region support drift")
    old=old.drop(columns=["source_region_source"])
    if (old[P].notna().sum(), old.loc[old[P].notna()].site_id.nunique(),
       old.loc[old[P].notna()].source_region.nunique())!=(439,85,11):
        raise ValueError("Original exact 439/85/11 physical sample changed")
    pix=pd.read_csv(a.original_pixels,low_memory=False)
    need=PIXEL_KEYS+["satellite","cell"]+BANDS
    if set(need)-set(pix.columns):raise ValueError("Missing source old real pixel band/date columns")
    if len(pix)!=131014:
        raise ValueError(f"Original exact 860 site×season old selected rows must be 131014, got {len(pix)}")
    if not pix.satellite.isin(SENSORS).all() or not pix.month.isin([1,2,11,12]).all():
        raise ValueError("Old original imagery sensor or season outside source")
    if not np.isfinite(pix[BANDS].to_numpy(dtype=float)).all():
        raise ValueError("Old source selected reflectance missing; no imputation")
    membership=old[["site_id","season","n_source_pixels","n_observed_days"]].copy()
    actual=pix.groupby(["site_id","season"],as_index=False).size()
    test=membership.merge(actual,on=["site_id","season"],validate="one_to_one")
    if len(test)!=860 or not test.n_source_pixels.eq(test["size"]).all():
        raise ValueError("Original source 860 raw selected pixels not exactly the originally fitted response")
    if not set(tuple(x) for x in actual[["site_id","season"]].itertuples(index=False,name=None))==set(
        tuple(x) for x in old[["site_id","season"]].itertuples(index=False,name=None)):
        raise ValueError("RDS original pixels source key support not equal old 860")
    return old,pix

def coeffs(a):
    out=[]
    for s in SENSORS:
        if s==7:
            frame=from_zip(a.original_l7_coefficients_zip,OLD_L7_R1000_ZIP_SHA,
                "L7_1000_author_style_5component_PLSR_CV_ensemble_coefficients.csv")
        else:
            frame=pd.read_csv(a.coefficients_dir /
                f"L{s}_1000_author_style_5component_PLSR_CV_ensemble_coefficients.csv")
        if len(frame)!=NENSEMBLE or not frame.sensor.eq(f"L{s}").all() or not frame.iteration.eq(np.arange(1,NENSEMBLE+1)).all():
            raise ValueError("Original author 1000 coefficient identities/iteration order drift")
        if not set(COEFS).issubset(frame.columns) or not np.isfinite(frame[COEFS].to_numpy(float)).all():
            raise ValueError("Original author source 7 coeffs not all finite")
        out.append(frame[COEFS].to_numpy(dtype=float).T)  # 7×1000, x3
    return np.vstack(out)  # 21×1000

def pixel_to_season_linear_source(pix,ref):
    # Fractional sensor intercept feature and sensor-specific six mean band values
    # within each original site×actual acquisition day. This reproduces the exact
    # PLSR prediction mean over original same-day pixels, EVEN if mixed sensors.
    day_frame=pix[PIXEL_KEYS].drop_duplicates().reset_index(drop=True)
    idx=pd.MultiIndex.from_frame(pix[PIXEL_KEYS])
    unique=pd.MultiIndex.from_frame(day_frame[PIXEL_KEYS])
    codes=unique.get_indexer(idx)
    if (codes<0).any():raise ValueError("Original old raw date not uniquely matched")
    counts=np.bincount(codes,minlength=len(day_frame))
    if not (len(day_frame)==int(ref.n_observed_days.sum())==2659 and
            int(counts.sum())==131014 and (counts>0).all()):
        raise ValueError("Frozen 860 actual original site calendar days mismatch")
    a=np.zeros((len(day_frame),21))
    for i,sensor in enumerate(SENSORS):
        m=pix.satellite.eq(sensor).to_numpy()
        base=i*7
        a[:,base]=np.bincount(codes[m],minlength=len(day_frame))/counts
        for j,band in enumerate(BANDS):
            a[:,base+1+j]=np.bincount(codes[m],
                weights=pix.loc[m,band].to_numpy(float),minlength=len(day_frame))/counts
    if np.max(np.abs(a[:,[0,7,14]].sum(axis=1)-1))>1e-12:
        raise ValueError("Original daily sensor contributions do not sum to 1")
    columns=[f"L{s}_{v}" for s in SENSORS for v in COEFS]
    daily=day_frame.join(pd.DataFrame(a,columns=columns))
    aggregated=daily.groupby(["site_id","season"],as_index=False)[columns].mean()
    days=daily.groupby(["site_id","season"],as_index=False).size()
    agg=ref[["site_id","season","n_observed_days","n_source_pixels"]].merge(
        aggregated,on=["site_id","season"],validate="one_to_one")
    agg=agg.merge(days,on=["site_id","season"],validate="one_to_one")
    if len(agg)!=860 or not agg.n_observed_days.eq(agg["size"]).all():
        raise ValueError("Reconstructed original actual day-equal 860 source Y membership drift")
    return agg,columns

def demean_two_fe(v,data):
    x=np.asarray(v,dtype=float)
    if x.ndim==1:x=x[:,None]
    x=x.copy()
    if not np.isfinite(x).all():raise ValueError("Source isotope outcome or fixed exposure invalid")
    site=data.site_id.to_numpy()
    group=data.region_year.to_numpy()
    for _ in range(3000):
        before=x.copy()
        x-=pd.DataFrame(x).groupby(site,sort=False).transform("mean").to_numpy()
        x-=pd.DataFrame(x).groupby(group,sort=False).transform("mean").to_numpy()
        if np.max(np.abs(x-before))<FE_TOL:break
    else:raise ValueError("Same original site+region×season FE did not converge")
    # Original FE are only absorbed, never used in temporal forecasts.
    return x

def fixed_fit(data,features,zcols,z,c,contrast=None):
    data=data.copy().reset_index(drop=True)
    x=demean_two_fe(data[features].to_numpy(float),data)
    r=np.linalg.matrix_rank(x)
    if r!=len(features):raise ValueError(f"Fixed model rank {r} not {len(features)}")
    zres=demean_two_fe(z,data)
    yold=demean_two_fe(data[Y_OLD].to_numpy(),data).ravel()
    ynew=zres@c.mean(axis=1)
    cluster=data.source_region.to_numpy()
    oldfit=sm.OLS(yold,x).fit(cov_type="cluster",cov_kwds={"groups":cluster})
    newfit=sm.OLS(ynew,x).fit(cov_type="cluster",cov_kwds={"groups":cluster})
    # Algebraic projection of 1000 calibration-only coefficient vectors through
    # the SAME fixed model; not resampling 1000 biological observations.
    slope_full=(np.linalg.lstsq(x,zres,rcond=None)[0] @ c)
    results={}
    g=int(pd.Series(cluster).nunique())
    for name,vector in [*[(v,np.eye(len(features))[j]) for j,v in enumerate(features)],
                        *([("P0_minus_P1",np.eye(len(features))[-2]-np.eye(len(features))[-1])] if contrast else [])]:
        if name not in [P,"P0","P1","P0_minus_P1"]:continue
        beta_old=float(vector@oldfit.params*.1)
        beta_new=float(vector@newfit.params*.1)
        se_old=float(np.sqrt(vector@oldfit.cov_params()@vector)*.1)
        se_new=float(np.sqrt(vector@newfit.cov_params()@vector)*.1)
        crit=t.ppf(.975,g-1)
        slopes=np.asarray(vector@slope_full*.1)
        if abs(np.mean(slopes)-beta_new)>1e-7:
            raise ValueError("Author 1000 ensemble linear aggregation != fixed model mean slope")
        results[name]={
           "old_single_PLSR_beta_per_10pp":beta_old,
           "old_region_cluster_t95":[beta_old-crit*se_old,beta_old+crit*se_old],
           "author_R1000_PLSR_beta_per_10pp":beta_new,
           "author_region_cluster_t95":[beta_new-crit*se_new,beta_new+crit*se_new],
           "author_plsr_calibration_only_beta_median":float(np.median(slopes)),
           "author_plsr_calibration_only_beta_2p5_97p5":np.quantile(slopes,[.025,.975]).tolist(),
           "author_plsr_calibration_only_fraction_negative":float(np.mean(slopes<0)),
           "author_minus_old_beta":beta_new-beta_old,
           "calibration_partitions_reuse_original103_lab_not_independent":True}
    return results,newfit,x,zres

def looregion(data,z,c,features,contrast=False):
    out=[]
    for reg in sorted(data.source_region.unique()):
        ix=data.source_region.ne(reg).to_numpy()
        subset=data.loc[ix].copy().reset_index(drop=True)
        sub_z=z[ix]
        try:
            r,_,_,_=fixed_fit(subset,features,None,sub_z,c,contrast)
            out.append({"omitted_region":reg,
                "rows_remaining":len(subset),
                "site_count":int(subset.site_id.nunique()),
                "P_new":r[P if not contrast else "P0"]["author_R1000_PLSR_beta_per_10pp"],
                "contrast_new":r.get("P0_minus_P1",{}).get("author_R1000_PLSR_beta_per_10pp")})
        except (ValueError,np.linalg.LinAlgError) as e:
            out.append({"omitted_region":reg,"error":str(e)})
    return out

def main(a):
    old,pix=source(a)
    c=coeffs(a)
    features,columns=pixel_to_season_linear_source(pix,old)
    z=features[columns].to_numpy(float)
    predicted=z@c.mean(axis=1)
    if not np.isfinite(predicted).all():raise ValueError("Author original 860 source outcome not finite")
    if (len(predicted),len(old))!=(860,860):raise ValueError("Author new source Y support drift")
    comp=old.merge(features[["site_id","season"]+columns],
        on=["site_id","season"],validate="one_to_one")
    comp[Y_NEW]=comp[columns].to_numpy(float) @ c.mean(axis=1)
    if not (len(comp)==860 and comp[Y_NEW].notna().all()):raise ValueError("Author ensemble source 860 not exact")
    d=comp.loc[comp[P].notna()].copy().reset_index(drop=True)
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(439,85,11):
        raise ValueError("Fixed historical 439/85/11 sample drift")
    d["region_year"]=d.source_region+"__"+d.season.astype(str)
    z439=d[columns].to_numpy(float)
    main_p,_,_,_=fixed_fit(d,BASE+[P],None,z439,c)
    main_sp,_,_,_=fixed_fit(d,BASE+[SAL,P],None,z439,c)
    # Reproduce pre-existing observed same 439 baseline *BEFORE* interpretation.
    if abs(main_p[P]["old_single_PLSR_beta_per_10pp"]-(-1.0031091429244865))>1e-7:
        raise ValueError("Old frozen 439 M_P regression does not reproduce existing source")
    if abs(main_sp[P]["old_single_PLSR_beta_per_10pp"]-(-.9216089250042961))>1e-7:
        raise ValueError("Old frozen 439 M_SP regression does not reproduce existing source")
    lo439p=looregion(d,z439,c,BASE+[P])
    lo439sp=looregion(d,z439,c,BASE+[SAL,P])
    if any("error" in z for z in lo439p+lo439sp):
        raise ValueError("Old original eleven-region omission model not evaluable")
    temporal=pd.read_csv(a.temporal_fixed_358,low_memory=False)
    if (len(temporal),temporal.site_id.nunique(),temporal.source_region.nunique(),
         temporal.season.nunique())!=(358,85,11,6):
        raise ValueError("Frozen prior/next winter 358/85/11/6 source support changed")
    if temporal.duplicated(["site_id","season"]).any():raise ValueError("Temporal original duplicate site-season")
    d358=temporal.merge(features[["site_id","season"]+columns],on=["site_id","season"],validate="one_to_one")
    if len(d358)!=358:raise ValueError("Frozen 358 original temporal full site-year support changed")
    if not np.allclose(d358[Y_OLD],temporal[Y_OLD],rtol=0,atol=0):
        raise ValueError("Old 358 source Y unexpectedly changed before reproject")
    d358["region_year"]=d358.source_region+"__"+d358.season.astype(str)
    z358=d358[columns].to_numpy(float)
    time_fit,_,_,_=fixed_fit(d358,TEMPERATURE_TIME_BASE+["P0","P1"],None,z358,c,contrast=True)
    if abs(time_fit["P0_minus_P1"]["old_single_PLSR_beta_per_10pp"]-(-.687702))>.001:
        raise ValueError("Old fixed 358 time-placebo contrast does not reproduce existing source")
    lo358=looregion(d358,z358,c,TEMPERATURE_TIME_BASE+["P0","P1"],contrast=True)
    if any("error" in z for z in lo358):
        raise ValueError("Original eleven-region placebo omission unsupported")
    # Informative region sensitivity uses pre-established zero residualized
    # covariate support, NOT the replacement optical Y.
    xfull=demean_two_fe(d358[TEMPERATURE_TIME_BASE+["P0","P1"]],d358)
    info={str(r):float(np.linalg.norm(xfull[d358.source_region.eq(r).to_numpy(),:]))
        for r in sorted(d358.source_region.unique())}
    regions=[k for k,v in info.items() if v>1e-8]
    if len(regions)!=8:raise ValueError("Original 8 informative region threshold/support drift")
    idx=d358.source_region.isin(regions).to_numpy()
    reduced=d358.loc[idx].copy().reset_index(drop=True)
    time_info,_,_,_=fixed_fit(reduced,TEMPERATURE_TIME_BASE+["P0","P1"],
        None,z358[idx],c,contrast=True)
    a.out.mkdir(parents=True,exist_ok=True)
    comp[["site_id","season","source_region","n_source_pixels","n_observed_days",Y_OLD,Y_NEW]].to_csv(
        a.out/"original_860_same_source_old_single_vs_author_R1000_PLSR_optical_Y.csv",index=False)
    pd.DataFrame(lo439p).to_csv(a.out/"original_439_M_P_author_ensemble_leave_region_out.csv",index=False)
    pd.DataFrame(lo439sp).to_csv(a.out/"original_439_M_SP_author_ensemble_leave_region_out.csv",index=False)
    pd.DataFrame(lo358).to_csv(a.out/"original_358_temporal_author_ensemble_leave_region_out.csv",index=False)
    true_y_diff=comp[Y_NEW].to_numpy()-comp[Y_OLD].to_numpy()
    report={
       "status":"HISTORICAL_ONLY_AUTHOR_PLSR1000_MEASUREMENT_SENSITIVITY_COMPLETED",
       "source_support":{"original_old_site_seasons":860,"old_original_sites":88,
          "old_observed_calendar_days":int(old.n_observed_days.sum()),
          "old_source_selected_pixels":int(old.n_source_pixels.sum()),
          "old_original_used_sensors":[4,5,7],
          "original_cohort_main":{"rows":len(d),"sites":int(d.site_id.nunique()),
            "regions":int(d.source_region.nunique())},
          "original_cohort_temporal":{"rows":len(d358),"sites":int(d358.site_id.nunique()),
            "regions":int(d358.source_region.nunique()),"informative_regions":regions}},
       "source_input_receipts":{"old_iso_zip_sha256":OLD_ISOTOPE_ZIP_SHA,
          "physical_zip_sha256":OLD_PHY_ZIP_SHA,"old_L7_1000_R_pls_zip_sha256":OLD_L7_R1000_ZIP_SHA,
          "historical_RDS_selected_pixel_CSV_SHA256":sha(a.original_pixels),
          "L4_L5_original_lab_coefficients_sha256":{str(i):sha(a.coefficients_dir/
              f"L{i}_1000_author_style_5component_PLSR_CV_ensemble_coefficients.csv") for i in (4,5)}},
       "source_Y_difference_author_minus_single":{"mean":float(np.mean(true_y_diff)),
          "median":float(np.median(true_y_diff)),
          "RMSE":float(np.sqrt(np.mean(true_y_diff**2))),
          "old_new_correlation":float(np.corrcoef(comp[Y_OLD],comp[Y_NEW])[0,1])},
       "original439_M_P":main_p[P],
       "original439_M_SP":main_sp[P],
       "original358_P0_joint":time_fit["P0"],
       "original358_P1_joint":time_fit["P1"],
       "original358_P0_minus_P1":time_fit["P0_minus_P1"],
       "original358_informative_8region_P0_minus_P1":time_info["P0_minus_P1"],
       "original_informative_region_effective_covariate_norms":info,
       "original439_M_P_all_11_leave_region_out_new_negative":all(z["P_new"]<0 for z in lo439p),
       "original439_M_SP_all_11_leave_region_out_new_negative":all(z["P_new"]<0 for z in lo439sp),
       "original358_all_11_leave_region_out_new_contrasts_negative":all(z["contrast_new"]<0 for z in lo358),
       "independent_post2013_external_replicate":False,
       "2013_2021_new_L8_guano_classifier_validated":False,
       "new_post2013_optical_Y_opened":False,
       "real_prey_fraction_measured":False,
       "author_hierarchical_Stan_isotope_DI_posterior_reproduced":False,
       "1000_calibration_folds_are_not_1000_independent_ecological_samples":True,
       "source_old_Y_439_and_358_baseline_regressions_reproduced":True,
       "new_exploratory_polynya_window_or_model_selected":False
    }
    (a.out/"AUTHOR_R1000_PLSR_ORIGINAL439_358_FIXED_MEASUREMENT_VERDICT.json").write_text(
       json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":report["status"],
      "source_only":report["source_support"],"original439_M_P":main_p[P],
      "original439_M_SP":main_sp[P],
      "original358_P0_minus_P1":time_fit["P0_minus_P1"],
      "original358_info8_P0_minus_P1":time_info["P0_minus_P1"],
      "region_omissions_negative":[report["original439_M_P_all_11_leave_region_out_new_negative"],
        report["original439_M_SP_all_11_leave_region_out_new_negative"],
        report["original358_all_11_leave_region_out_new_contrasts_negative"]],
      "not_independent_time_replicate":True},indent=2,ensure_ascii=False),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--old-isotope-zip",type=Path,required=True)
    p.add_argument("--old-physical-zip",type=Path,required=True)
    p.add_argument("--original-l7-coefficients-zip",type=Path,required=True)
    p.add_argument("--original-pixels",type=Path,required=True)
    p.add_argument("--coefficients-dir",type=Path,required=True)
    p.add_argument("--temporal-fixed-358",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
