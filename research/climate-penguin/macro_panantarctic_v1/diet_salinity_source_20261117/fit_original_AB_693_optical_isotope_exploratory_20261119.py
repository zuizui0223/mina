#!/usr/bin/env python3
"""Source-locked exploratory winter-salinity(A) vs stratification(B) comparison.

Read MECHANISM_AB_EXPLORATORY_MODEL_FROZEN_20261119_JA.md FIRST.
No habitat-change prediction, no fish fraction inference, no A/B/C full test.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t

ISOTOPE_SHA = "dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
PHYSICAL_SHA = "a300e588c85256c060ffffa14717378fc9198a75a0ef583669e6e94e2236255f"
ISOTOPE_NAME = "matched_860_original_isotope_ocean_ice_site_seasons.csv"
PHYSICAL_NAME = "source_860_site_seasons_A_B_physics_only_NO_OUTCOME.csv"

Y = "predicted_d15N_season_day_equal"
OTHER = ["mean_doy_centered", "mean_doy_sq",
         "GLORYS_NovFeb_thetao_C", "author_SIC_150km_NovFeb_center_approx_fraction"]
S = "GLORYS_NovFeb_salinity"
A = "winter_JunOct_surface_so"
B = "summer_NovFeb_sigma0_50m_minus_0m"

EXTRAS = {
    "M0": [],
    "M_S": [S],
    "M_A": [A],
    "M_B": [B],
    "M_SA": [S, A],
    "M_SB": [S, B],
    "M_AB": [A, B],
    "M_SAB": [S, A, B],
}
FORECAST_MODELS = ["M0", "M_S", "M_A", "M_B", "M_AB", "M_SAB"]
SEED = 20261119
BOOT = 2000


def verify_zip(path, expected):
    b = Path(path).read_bytes()
    got = hashlib.sha256(b).hexdigest()
    if got != expected:
        raise ValueError(f"Pinned input ZIP SHA256 mismatch: {got}; expected {expected}")
    z = zipfile.ZipFile(io.BytesIO(b))
    if z.testzip() is not None:
        raise ValueError("Archive original artifact ZIP CRC failed")
    return z


def read_and_merge(isotope_zip, physical_zip):
    with verify_zip(isotope_zip, ISOTOPE_SHA) as z:
        source = pd.read_csv(io.BytesIO(z.read(ISOTOPE_NAME)), low_memory=False)
    with verify_zip(physical_zip, PHYSICAL_SHA) as z:
        physical = pd.read_csv(io.BytesIO(z.read(PHYSICAL_NAME)), low_memory=False)
    if (len(source), source.site_id.nunique(), source.source_region.nunique()) != (860, 88, 13):
        raise ValueError("Original isotope 860/88/13 source denominator changed")
    if (len(physical), physical.site_id.nunique()) != (860,88):
        raise ValueError("A/B ocean physical source 860/88 denominator changed")
    keys=["site_id","season"]
    if source.duplicated(keys).any() or physical.duplicated(keys).any():
        raise ValueError("Duplicated original isotope or physical site×season")
    phys_cols=keys+["source_wet_grid_x","source_wet_grid_y",
                    "winter_JunOct_surface_so","summer_NovFeb_surface_so",
                    B,"B_complete_TEOS10_density"]
    d = source.merge(physical[phys_cols], on=keys, how="inner",
                     suffixes=("_iso", "_phys"), validate="one_to_one")
    if len(d)!=860:
        raise ValueError("Original matched site×season changed")
    for label in ("source_wet_grid_x","source_wet_grid_y"):
        if not d[label+"_iso"].equals(d[label+"_phys"]):
            raise ValueError("Fixed original wetcell index mismatch: "+label)
        d[label] = d[label+"_iso"]
    delta=(d[S]-d["summer_NovFeb_surface_so"]).abs()
    if not delta.notna().all() or float(delta.max())>1e-4:
        raise ValueError("GLORYS NovFeb source salinity cross-verification failed")
    good=d[B].notna() & d[A].notna() & d[S].notna()
    s=d.loc[good].copy().reset_index(drop=True)
    if len(s)!=693 or int(s[[ "source_wet_grid_x","source_wet_grid_y"]].drop_duplicates().shape[0])!=68:
        raise ValueError("Predetermined complete physical source must be 693 and 68 distinct original wetcells")
    needed=[Y,*OTHER,S,A,B]
    if not np.isfinite(s[needed].to_numpy(dtype=float)).all():
        raise ValueError("Unresolved original biological or physical missingness")
    s["original_wetcell"]=(s.source_wet_grid_y.astype(str)+":"+
                            s.source_wet_grid_x.astype(str))
    s["region_year"]=(s.source_region.astype(str)+"__"+s.season.astype(str))
    return s, {"original_n":len(d),"original_site_n":int(d.site_id.nunique()),
               "source_identical_summer_so_max_abs_diff":float(delta.max()),
               "complete_B_n":len(s),"complete_B_sites":int(s.site_id.nunique()),
               "complete_B_wetcells":int(s.original_wetcell.nunique()),
               "complete_B_regions":int(s.source_region.nunique()),
               "complete_B_seasons":sorted([int(y) for y in s.season.unique()])}


def fe_project(vec, site, regyear):
    x=np.asarray(vec,dtype=float).copy()
    s=pd.Series(np.asarray(site)).reset_index(drop=True)
    g=pd.Series(np.asarray(regyear)).reset_index(drop=True)
    for _ in range(3000):
        prev=x.copy()
        x-=pd.Series(x).groupby(s,sort=False).transform("mean").to_numpy()
        x-=pd.Series(x).groupby(g,sort=False).transform("mean").to_numpy()
        if np.max(np.abs(x-prev)) < 1e-10:
            break
    if max(np.max(np.abs(pd.Series(x).groupby(s).mean())),
           np.max(np.abs(pd.Series(x).groupby(g).mean())))>1e-7:
        raise ValueError("Source site and region×season FE projection did not converge")
    return x


def association(d, model, cluster="cell"):
    xs=OTHER+EXTRAS[model]
    rows=[fe_project(d[c],d.site_id,d.region_year) for c in xs]
    X=np.column_stack(rows)
    y=fe_project(d[Y],d.site_id,d.region_year)
    if np.linalg.matrix_rank(X) < len(xs):
        raise ValueError("Exact original FE residual predictors rank-deficient: "+model)
    groups=d.original_wetcell if cluster=="cell" else d.source_region
    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":groups})
    out={"model":model,"n_rows":len(d),
         "n_cells":int(d.original_wetcell.nunique()),
         "n_regions":int(d.source_region.nunique()),
         "residual_sse":float(np.sum(fit.resid**2)),
         "aic_relative_same_693_FE":float(len(d)*np.log(np.mean(fit.resid**2))+2*len(xs)),
         "source_columns":xs}
    coef=[]
    groups_n=int(pd.Series(groups).nunique())
    for i, col in enumerate(xs):
        sd=float(d[col].std(ddof=0))
        beta=float(fit.params[i]); se=float(fit.bse[i])
        coef.append({"variable":col,"beta_per_native_unit":beta,
                     "beta_per_one_source_SD":beta*sd,
                     "original_unit_sd":sd,"cluster_type":cluster,
                     "cluster_n":groups_n,"se":se,
                     "t_group_m1_CI":[beta-t.ppf(.975,groups_n-1)*se,
                                      beta+t.ppf(.975,groups_n-1)*se]})
    out["coefficients"]=coef
    return out


def group_omissions(d):
    vals=[]
    for omitted in sorted(d.source_region.unique()):
        sub=d.loc[d.source_region.ne(omitted)].copy().reset_index(drop=True)
        for model,feature in [("M_A",A),("M_B",B),("M_S",S)]:
            try:
                res=association(sub,model,"cell")
                r=next(t for t in res["coefficients"] if t["variable"]==feature)
                vals.append({"omitted_region":str(omitted),"model":model,
                             "native_beta":r["beta_per_native_unit"],
                             "n_observations":len(sub)})
            except (ValueError,np.linalg.LinAlgError) as e:
                vals.append({"omitted_region":str(omitted),"model":model,
                             "error":str(e),"n_observations":len(sub)})
    return pd.DataFrame(vals)


def heldout_split(d):
    tr=d.loc[d.season<=2004].copy()
    later=d.loc[d.season.between(2005,2012)].copy()
    te=later.loc[later.site_id.isin(set(tr.site_id))].copy()
    new=later.loc[~later.site_id.isin(set(tr.site_id))].copy()
    if tr.empty or te.empty or tr.season.max()>=te.season.min():
        raise ValueError("Historical freeze cohort lost independent chronological support")
    if te.site_id.nunique()<40 or te.source_region.nunique()<7:
        raise ValueError("MODEL_SUPPORT_NO_GO fewer than 40 test sites or 7 test regions")
    return tr,te,new


def hindcast_predict(train,test,extras):
    columns=OTHER+extras
    sites=sorted(train.site_id.unique())
    lookup={v:i for i,v in enumerate(sites)}
    mu=train[columns].mean().to_numpy(dtype=float)
    sd=train[columns].std(ddof=0).to_numpy(dtype=float)
    if np.any(sd<1e-10) or not np.isfinite(sd).all():
        raise ValueError("TRAIN only numeric covariate SD degenerate")
    def build(df):
        if not df.site_id.isin(lookup).all():
            raise ValueError("Never invent intercept for not-yet-observed source site")
        X=np.zeros((len(df),len(sites)+len(columns)),dtype=float)
        X[np.arange(len(df)),df.site_id.map(lookup).to_numpy(dtype=int)]=1.0
        X[:,len(sites):]=(df[columns].to_numpy(dtype=float)-mu)/sd
        return X
    X=build(train);Z=build(test)
    if np.linalg.matrix_rank(X)<X.shape[1]:
        raise ValueError("Original training site-effect + predictor matrix rank deficient")
    p=np.linalg.lstsq(X,train[Y].to_numpy(dtype=float),rcond=None)[0]
    return Z@p


def site_equal_loss_frame(y,preds,sites,regions):
    d=pd.DataFrame({"site_id":sites.to_numpy(),"source_region":regions.to_numpy()})
    for model,p in preds.items():
        d[model+"_squared_loss"]=(y-p)**2
        d[model+"_abs_loss"]=np.abs(y-p)
    # Region should be stable for a single fixed original site.
    if d.groupby("site_id").source_region.nunique().gt(1).any():
        raise ValueError("Source site belongs to multiple report regions")
    val=d.groupby(["site_id","source_region"],as_index=False).mean(numeric_only=True)
    return val


def paired_region_boot(site_loss,a,b,rng):
    # Equal source site one vote. Repeated group bootstrap samples
    # complete region-as-clusters and its genuinely observed sites.
    delta=(site_loss[a+"_squared_loss"]-site_loss[b+"_squared_loss"]).to_numpy(dtype=float)
    region=site_loss.source_region.to_numpy()
    levels=np.unique(region)
    sample=np.arange(len(levels))
    ranges=[np.flatnonzero(region==x) for x in levels]
    out=np.empty(BOOT,dtype=float)
    for k in range(BOOT):
        chosen=rng.choice(sample,size=len(sample),replace=True)
        ix=np.concatenate([ranges[t] for t in chosen])
        out[k]=float(np.mean(delta[ix]))
    return {"difference_MSE_site_equal":float(np.mean(delta)),
            "source_region_cluster_bootstrap_95CI":[float(x) for x in np.quantile(out,[.025,.975])],
            "regions":int(len(levels)),"bootstrap_draws":BOOT}


def main(a):
    d,support=read_and_merge(a.isotope_zip,a.physical_zip)
    orig_base=association(d,"M0","cell")
    base_sse=orig_base["residual_sse"]
    assoc=[]
    for name in EXTRAS:
        results=association(d,name,"cell")
        region=association(d,name,"region")
        results["SSE_reduction_vs_M0"]=float(1-results["residual_sse"]/base_sse)
        results["region_cluster"]=region["coefficients"]
        assoc.append(results)
    omissions=group_omissions(d)
    train,test,unseen=heldout_split(d)
    predictions={m:hindcast_predict(train,test,EXTRAS[m]) for m in FORECAST_MODELS}
    y=test[Y].to_numpy(dtype=float)
    site_losses=site_equal_loss_frame(y,predictions,test.site_id,test.source_region)
    diagnostics={}
    for m in FORECAST_MODELS:
        diagnostics[m]={
            "RMSE_site_equal":float(np.sqrt(site_losses[m+"_squared_loss"].mean())),
            "MAE_site_equal":float(site_losses[m+"_abs_loss"].mean()),
            "RMSE_season_equal":float(np.sqrt(np.mean((y-predictions[m])**2))),
            "MAE_season_equal":float(np.mean(np.abs(y-predictions[m]))),
        }
    rng=np.random.default_rng(SEED)
    paired={}
    for model in ("M_A","M_B"):
        paired[model]={}
        for competitor in ("M0","M_S",("M_B" if model=="M_A" else "M_A")):
            paired[model][competitor]=paired_region_boot(site_losses,model,competitor,rng)
    winner=[]
    for model in ("M_A","M_B"):
        thresholds=all(
            diagnostics[model]["RMSE_site_equal"]<diagnostics[competitor]["RMSE_site_equal"]
            and paired[model][competitor]["source_region_cluster_bootstrap_95CI"][1]<0
            for competitor in paired[model])
        if thresholds: winner.append(model)
    result={
        "status":"PROVISIONAL_PREDICTIVE_PROXY_ONLY_NO_MECHANISM_CAUSAL_IDENTIFICATION"
                 if len(winner)==1 else "NO_GO_AB_MECHANISM_WINNER",
        "method_pre_frozen_file":"MECHANISM_AB_EXPLORATORY_MODEL_FROZEN_20261119_JA.md",
        "not_independent_confirmatory_experiment":True,
        "original_optical_isotope_proxy_not_prey_guild":True,
        "no_full_ABC_equal_support":True,
        "no_future_isotope_or_breeding_forecast":True,
        "isotope_archive_sha256":ISOTOPE_SHA,"A_B_physical_archive_sha256":PHYSICAL_SHA,
        "original_observational_support":support,
        "train":{"rows":len(train),"sites":int(train.site_id.nunique()),
                 "regions":int(train.source_region.nunique()),
                 "max_source_season":int(train.season.max())},
        "test":{"rows":len(test),"sites":int(test.site_id.nunique()),
                "regions":int(test.source_region.nunique()),
                "min_source_season":int(test.season.min())},
        "new_unseen_site_source_rows_excluded":len(unseen),
        "in_sample_identical_support_m0_sse":base_sse,
        "in_sample_models":assoc,
        "heldout_model_loss":diagnostics,
        "heldout_source_region_cluster_paired_mse_differences":paired,
        "conditionally_preferred_proxy":winner,
        "no_inference_that_winter_salt_is_polynya_or_sigma0_is_glacial_meltwater":True,
    }
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"same_693_original_source_AB_isotope_association.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    pd.DataFrame([
        {"model":x["model"],"n_rows":x["n_rows"],
         "SSE_reduction_vs_M0":x["SSE_reduction_vs_M0"],
         "AIC_relative":x["aic_relative_same_693_FE"]}
        for x in assoc
    ]).to_csv(a.out/"same_693_in_sample_model_descriptive_score.csv",index=False)
    omissions.to_csv(a.out/"AB_leave_one_original_region_out_beta.csv",index=False)
    p=test[["site_id","source_region","season","original_wetcell"]].copy()
    p["optical_d15N_proxy"]=y
    for k,v in predictions.items():
        p["predict_"+k]=v
    p.to_csv(a.out/"AB_frozen_known_site_holdout_predictions.csv",index=False)
    site_losses.to_csv(a.out/"AB_site_equal_heldout_paired_losses.csv",index=False)
    print(json.dumps({
        "status":result["status"],
        "physical_complete_support":support,
        "train":result["train"],"test":result["test"],
        "out_of_sample_new_sites_excluded":len(unseen),
        "rmse_site_equal":{k:round(v["RMSE_site_equal"],7) for k,v in diagnostics.items()},
        "paired_region_CIs":paired,
        "exploratory_in_sample_partial_R2":{
            x["model"]:round(x["SSE_reduction_vs_M0"],7) for x in assoc},
    },indent=2,ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--isotope-zip",type=Path,required=True)
    ap.add_argument("--physical-zip",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    main(ap.parse_args())
