#!/usr/bin/env python3
"""One preregistered direct-DEEPAA coastal polynya vs Youngflesh optical isotope proxy test.
SCIENTIFIC STOP: Never call if real source-only >=30-site/6-region/4-winter/3x3 region gate fails.
See DIRECT_POLYNYA_OPTICAL_ISOTOPE_MODEL_FROZEN_20261119_JA.md
"""
from __future__ import annotations
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t
import statsmodels.api as sm

ISO_SHA="dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
SOURCE_CSV="matched_860_original_isotope_ocean_ice_site_seasons.csv"
PHY_CSV="source_original_860_site_seasons_true_DEEPAA100km_no_optical_Y.csv"
PHY_REC="DEEPAA_ACTUAL_860_SOURCE_GEO_TIME_GATE.json"
Y="predicted_d15N_season_day_equal"
S="GLORYS_NovFeb_salinity"
P="direct_DEEPAA_coastal_polynya_fraction"
BASE=["mean_doy_centered","mean_doy_sq","GLORYS_NovFeb_thetao_C","author_SIC_150km_NovFeb_center_approx_fraction"]
MODEL={"M0":[],"M_S":[S],"M_P":[P],"M_SP":[S,P]}
SEED=20261119
BOOT=2000

def load(a):
    h=hashlib.sha256(Path(a.isotope_zip).read_bytes()).hexdigest()
    if h!=ISO_SHA:raise ValueError("Original 860 source SHA mismatch")
    with zipfile.ZipFile(a.isotope_zip) as z:
        if z.testzip():raise ValueError("Original ZIP CRC failure")
        iso=pd.read_csv(io.BytesIO(z.read(SOURCE_CSV)),low_memory=False)
    with zipfile.ZipFile(a.polynya_source_zip) as z:
        if z.testzip():raise ValueError("Original DEEP-AA original source derived ZIP CRC failure")
        def read(name):
            options=[n for n in z.namelist() if n==name or n.endswith("/"+name)]
            if len(options)!=1:raise ValueError("Expected exactly one source-derived member "+name)
            return z.read(options[0])
        r=json.loads(read(PHY_REC))
        ph=pd.read_csv(io.BytesIO(read(PHY_CSV)),low_memory=False)
    if r["status"]!="PASS_DIRECT_POLYNYA_MACRO_SUPPORT_SOURCE_ONLY_NO_Y_FIT":
        raise ValueError("NO_GO_DIRECT_POLYNYA_MACRO_SUPPORT: forbid outcome opened/fit")
    if not all(r["frozen_gate_checks"].values()) or not r["no_outcome_opened_or_fitted"]:
        raise ValueError("Native 100km source stage did not pass every frozen criterion")
    if (len(iso),iso.site_id.nunique(),iso.source_region.nunique())!=(860,88,13):
        raise ValueError("Original source isotope population drift")
    if (len(ph),ph.site_id.nunique(),ph.source_region.nunique())!=(860,88,13):
        raise ValueError("Direct source population drift")
    for df in (iso,ph):
        df["site_id"]=df.site_id.astype(str)
        df["season"]=df.season.astype(int)
        if df.duplicated(["site_id","season"]).any():
            raise ValueError("Original site×season duplicated")
    joint=iso.merge(ph[["site_id","season","source_region",P,
       "source_native_distinct_coastal_polynya_pixels_over_winter"]],on=["site_id","season"],how="inner",
       validate="one_to_one",suffixes=("","_source"))
    if len(joint)!=860:
        raise ValueError("Original full 860 primary source mapping lost")
    if not joint.source_region.eq(joint.source_region_source).all():
        raise ValueError("Source region mismatch")
    valid=joint[P].notna()
    sample=joint.loc[valid].copy().reset_index(drop=True)
    if len(sample)!=r["real_complete_100km_observations"]:
        raise ValueError("Underlying source coverage vs actually opened optical outcome differs")
    if (sample.site_id.nunique()!=r["real_complete_100km_original_sites"]
          or sample.source_region.nunique()!=r["real_complete_100km_source_regions"]):
        raise ValueError("Opened source sample population unsupported")
    if not np.isfinite(sample[[Y,P,S]+BASE].to_numpy(dtype=float)).all():
        raise ValueError("Native observed source target/predictor missingness not allowed")
    sample["original_wetcell"]=(sample.source_wet_grid_y.astype(str)+":"+sample.source_wet_grid_x.astype(str))
    sample["region_year"]=(sample.source_region.astype(str)+"__"+sample.season.astype(str))
    return sample,r

def project_two_fe(v,site,region_year):
    x=np.asarray(v,dtype=float).copy()
    ids=pd.Series(site).reset_index(drop=True)
    groups=pd.Series(region_year).reset_index(drop=True)
    for k in range(3000):
        before=x.copy()
        x-=pd.Series(x).groupby(ids,sort=False).transform("mean").to_numpy()
        x-=pd.Series(x).groupby(groups,sort=False).transform("mean").to_numpy()
        if np.max(np.abs(x-before))<1e-10:break
    if (np.max(np.abs(pd.Series(x).groupby(ids).mean()))>1e-7 or
       np.max(np.abs(pd.Series(x).groupby(groups).mean()))>1e-7):
        raise ValueError("Original site FE / region×season FE projection nonconvergence")
    return x

def association(d,model,cluster):
    xs=BASE+MODEL[model]
    X=np.column_stack([project_two_fe(d[c],d.site_id,d.region_year) for c in xs])
    y=project_two_fe(d[Y],d.site_id,d.region_year)
    if np.linalg.matrix_rank(X)<len(xs):
        raise ValueError(f"No independent polynya covariate under source FE design: {model}")
    if np.linalg.norm(X[:,xs.index(P)])<1e-8 if P in xs else False:
        raise ValueError("Direct coastal polynya perfectly absorbed by regional and site FE")
    groups=d.source_region if cluster=="region" else d.original_wetcell
    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":groups})
    k=int(pd.Series(groups).nunique())
    out={"model":model,"cluster":cluster,"rows":len(d),"sites":int(d.site_id.nunique()),
         "regions":int(d.source_region.nunique()),"cells":int(d.original_wetcell.nunique()),
         "sse":float(np.sum(fit.resid**2)),
         "aic_relative_no_FE":float(len(d)*np.log(np.mean(fit.resid**2))+2*len(xs)),
         "coefficients":[]}
    for i,v in enumerate(xs):
        beta=float(fit.params[i]); se=float(fit.bse[i])
        out["coefficients"].append({"feature":v,"native_beta":beta,"se":se,
           "original_feature_std":float(d[v].std(ddof=0)),
           "group_n":k,"conservative_t_df":k-1,
           "t95ci":[float(beta-t.ppf(.975,k-1)*se),float(beta+t.ppf(.975,k-1)*se)]})
    return out

def extract_feature(result,var):
    for c in result["coefficients"]:
        if c["feature"]==var:return c
    raise ValueError("Fitted model lacks declared feature "+var)

def heldout_predict(train,test,extras):
    columns=BASE+extras
    sites=sorted(train.site_id.unique())
    enc={site:i for i,site in enumerate(sites)}
    m=train[columns].mean().to_numpy(float)
    std=train[columns].std(ddof=0).to_numpy(float)
    if not np.isfinite(std).all() or (std<1e-10).any():
        raise ValueError("Predeclared 2004-06 training predictor unsupported")
    def design(df):
        if not df.site_id.isin(enc).all():raise ValueError("Test has unseen site without training intercept")
        X=np.zeros((len(df),len(sites)+len(columns)))
        X[np.arange(len(df)),df.site_id.map(enc).to_numpy(int)]=1.
        X[:,len(sites):]=(df[columns].to_numpy(float)-m)/std
        return X
    X=design(train)
    if np.linalg.matrix_rank(X)<X.shape[1]:
        raise ValueError("Predeclared 2004-06 model rank deficient")
    beta=np.linalg.lstsq(X,train[Y].to_numpy(float),rcond=None)[0]
    return design(test)@beta

def holdout(d):
    train=d.loc[d.season.between(2004,2006)].copy()
    future=d.loc[d.season.between(2007,2010)].copy()
    test=future.loc[future.site_id.isin(set(train.site_id))].copy()
    support={"train_n":len(train),"test_n":len(test),
       "train_sites":int(train.site_id.nunique()),"test_sites":int(test.site_id.nunique()),
       "train_regions":int(train.source_region.nunique()),"test_regions":int(test.source_region.nunique()),
       "n_future_new_site_excluded":len(future)-len(test),
       "no_future_region_year_effects_used":True}
    if (train.site_id.nunique()<30 or test.site_id.nunique()<30
       or train.source_region.nunique()<6 or test.source_region.nunique()<6):
        return {"status":"NOT_IDENTIFIABLE_IN_THIS_HISTORICAL_SPLIT","support":support},None
    try:
        preds={name:heldout_predict(train,test,extra) for name,extra in MODEL.items()}
    except ValueError as e:
        return {"status":"NOT_IDENTIFIABLE_IN_THIS_HISTORICAL_SPLIT","support":support,
               "diagnostic":str(e)},None
    frame=test[["site_id","season","source_region","original_wetcell"]].copy()
    frame["observed_optical_delta15N"]=test[Y].to_numpy()
    for name,v in preds.items():frame["pred_"+name]=v
    site_loss=frame[["site_id","source_region"]].copy()
    for name,p in preds.items():site_loss[name]=(test[Y].to_numpy()-p)**2
    site_loss=site_loss.groupby(["site_id","source_region"],as_index=False).mean(numeric_only=True)
    rmse={k:float(np.sqrt(site_loss[k].mean())) for k in preds}
    baseline=site_loss.source_region.to_numpy()
    regions=np.unique(baseline)
    partitions=[np.flatnonzero(baseline==rg) for rg in regions]
    seed=np.random.default_rng(SEED)
    comparisons={}
    for cand,ref in [("M_P","M0"),("M_P","M_S"),("M_SP","M0"),("M_SP","M_S")]:
        delta=(site_loss[cand]-site_loss[ref]).to_numpy()
        boot=np.empty(BOOT,dtype=float)
        for b in range(BOOT):
            ix=np.concatenate([partitions[j] for j in seed.choice(len(regions),size=len(regions),replace=True)])
            boot[b]=delta[ix].mean()
        comparisons[cand+"_minus_"+ref]={"paired_site_equal_MSE_diff":float(delta.mean()),
              "cluster_region_boot_95CI":[float(x) for x in np.quantile(boot,[.025,.975])]}
    return {"status":"HISTORICAL_SPLIT_VALIDATED_NO_REGION_YEAR_LEAKAGE","support":support,
        "site_equal_RMSE":rmse,"region_cluster_bootstrap_2000_paired_MSE_deltas":comparisons,
        "prediction_improves_M0_and_M_S":bool(rmse["M_P"]<rmse["M0"] and rmse["M_P"]<rmse["M_S"]
              and comparisons["M_P_minus_M0"]["cluster_region_boot_95CI"][1]<0
              and comparisons["M_P_minus_M_S"]["cluster_region_boot_95CI"][1]<0)},frame

def main(a):
    d,gate=load(a)
    rows={}
    for m in MODEL:
        region=association(d,m,"region")
        cell=association(d,m,"cell")
        rows[m]={"region":region,"cell":cell}
    sse0=rows["M0"]["region"]["sse"]
    for name,r in rows.items():r["additional_M0_residual_fraction"]=1-r["region"]["sse"]/sse0
    additional_vs_s=1-rows["M_SP"]["region"]["sse"]/rows["M_S"]["region"]["sse"]
    leaves=[]
    for omit in sorted(d.source_region.unique()):
        sub=d.loc[d.source_region.ne(omit)].copy().reset_index(drop=True)
        for name in ("M_P","M_SP"):
            try:
                x=extract_feature(association(sub,name,"region"),P)
                leaves.append({"omitted_original_region":str(omit),"model":name,"polynya_beta":x["native_beta"]})
            except (ValueError,np.linalg.LinAlgError) as e:
                leaves.append({"omitted_original_region":str(omit),"model":name,"error":str(e)})
    stable=all(("error" not in x and x["polynya_beta"]>0) for x in leaves)
    positive=all(extract_feature(rows[n]["region"],P)["native_beta"]>0
           and extract_feature(rows[n]["region"],P)["t95ci"][0]>0
           for n in ("M_P","M_SP"))
    eligible=bool(positive and stable)
    forecast,forecast_frame=holdout(d)
    status=("PASS_DIRECT_POLYNYA_EXPLORATORY_ASSOCIATION_NOT_CAUSAL"
            if eligible else "NO_GO_DIRECT_POLYNYA_ASSOCIATION")
    result={"status":status,"frozen_preregistered_file":
      "DIRECT_POLYNYA_OPTICAL_ISOTOPE_MODEL_FROZEN_20261119_JA.md",
      "source_outcome_gate_was_passed_before_Y_open":True,
      "same_observations_all_four_comparisons":len(d),
      "same_original_sites_all_four":int(d.site_id.nunique()),
      "source_regions":int(d.source_region.nunique()),
      "source_regions_and_winter_support_original":gate["real_complete_100km_distinct_winters"],
      "response_measures_satellite_optical_delta15N_proxy_NOT_fish_fraction":True,
      "source_real_coastal_polynya_fraction_100km_not_winter_salinity_proxy":True,
      "models":rows,"M_SP_incremental_residual_fraction_vs_M_S":additional_vs_s,
      "leave_original_region_out":leaves,
      "region_CI_positive_M_P_and_M_SP":bool(positive),
      "leave_original_region_out_positive_in_both":bool(stable),
      "heldout":forecast,"cannot_claim_direct_diet_baseline_or_causality":True,
      "no_anthropogenic_warming_or_2100_future_penguin_population_prediction":True}
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"DEEPAA100km_FROZEN_DIRECT_COASTAL_POLYNYA_OPTICAL_ISOTOPE_VERDICT.json").write_text(
       json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    pd.DataFrame(leaves).to_csv(a.out/"DEEPAA100km_leave_one_original_region_out.csv",index=False)
    if forecast_frame is not None:
        forecast_frame.to_csv(a.out/"DEEPAA100km_frozen_2004_2006_train_2007_2010_test.csv",index=False)
    print(json.dumps({"status":status,"source_eligible_observations":len(d),
      "source_regions":int(d.source_region.nunique()),
      "M_P_beta":extract_feature(rows["M_P"]["region"],P),
      "M_SP_beta":extract_feature(rows["M_SP"]["region"],P),
      "incremental_R2_vs_M0":{k:v["additional_M0_residual_fraction"] for k,v in rows.items()},
      "M_SP_extra_vs_M_S":additional_vs_s,
      "stable_leave_region_out":bool(stable),
      "heldout":forecast},indent=2,ensure_ascii=False))
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--isotope-zip",type=Path,required=True)
    parser.add_argument("--polynya-source-zip",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    main(parser.parse_args())
