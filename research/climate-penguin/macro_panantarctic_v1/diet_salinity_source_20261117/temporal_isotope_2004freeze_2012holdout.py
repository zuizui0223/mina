#!/usr/bin/env python3
"""Frozen held-out-time source test of salinity's incremental isotope-proxy skill.

Scientific contract FIRST committed:
FROZEN_TEMPORAL_TRANSFER_AND_TWO_AXIS_TEST_20261118_JA.md

Training ONLY source colony-seasons 1996 / 1999–2004 (<=2004).
Test only source colony-seasons 2005–2012 already seen by end 2004.
Never condition validation-year outcomes on future region×season fixed effects.
Evaluate one frozen salinity additional term against site-persistence, site
historical-mean and no-salt contemporaneous ice/temperature baselines.
Actual 2005+ ocean conditions are available to this retrospective hindcast:
this is not SSP projected δ15N or prey fraction.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import statsmodels.api as sm

SOURCE_SHA256="dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
SOURCE_CSV="matched_860_original_isotope_ocean_ice_site_seasons.csv"
Y="predicted_d15N_season_day_equal"
SALT="GLORYS_NovFeb_salinity"
ICE="author_SIC_150km_NovFeb_center_approx_fraction"
TEMP="GLORYS_NovFeb_thetao_C"
TIMING=["mean_doy_centered","mean_doy_sq"]
OTHER=[*TIMING,TEMP,ICE]
MODELS=["PERSIST","SITE_MEAN","ICE_THERMAL","ICE_THERMAL_SALT"]
TRAIN_LAST=2004
TEST_START=2005
TEST_END=2012
NBOOT=2000
SEED=20261118

def load_source(src):
    raw=Path(src).read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=SOURCE_SHA256:
        raise ValueError(f"Frozen original 860 isotope source SHA256 mismatch: {sha}")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise ValueError("Source originally published zip CRC failure")
        df=pd.read_csv(io.BytesIO(z.read(SOURCE_CSV)),low_memory=False)
    if (len(df),df.site_id.nunique(),df.source_region.nunique())!=(860,88,13):
        raise ValueError("Original entire isotope source support drift")
    if df.duplicated(["site_id","season"]).any():
        raise ValueError("Duplicate original site/season")
    need=[Y,*OTHER,SALT,"site_id","season","source_region",
          "source_wet_grid_x","source_wet_grid_y"]
    if not set(need).issubset(df):
        raise ValueError("Original source input schema changed: "+str(set(need)-set(df)))
    if not np.isfinite(df[[Y,*OTHER,SALT]].to_numpy(dtype=float)).all():
        raise ValueError("Original source missing phenotype or marine physics")
    df["source_wet_cell"]=(df.source_wet_grid_y.astype(str)+":"+
                           df.source_wet_grid_x.astype(str))
    df=df.sort_values(["season","site_id"]).reset_index(drop=True)
    return df,sha

def frozen_split(df):
    train=df.loc[df.season<=TRAIN_LAST].copy()
    later=df.loc[df.season.between(TEST_START,TEST_END)].copy()
    recognized=set(train.site_id)
    test=later.loc[later.site_id.isin(recognized)].copy()
    rejected=later.loc[~later.site_id.isin(recognized)].copy()
    if (len(train),len(later),len(test),len(rejected))!=(304,556,541,15):
        raise ValueError("Frozen source temporal split changed")
    if (train.site_id.nunique(),later.site_id.nunique(),test.site_id.nunique())!=(83,87,82):
        raise ValueError("Frozen site generalization gate drift")
    if (train.source_region.nunique(),test.source_region.nunique())!=(12,11):
        raise ValueError("Frozen original reporting-region support changed")
    if not (train.season.max()<test.season.min()):
        raise ValueError("Train/test isotope target time leakage")
    if len(set(test.site_id)-set(train.site_id))>0:
        raise ValueError("Cannot predict new site with frozen site effects")
    return train,test,rejected

def design(train,test,add_salt):
    names=OTHER+([SALT] if add_salt else [])
    sites=sorted(train.site_id.unique())
    lookup={k:i for i,k in enumerate(sites)}
    def site_effect(rows):
        if not rows.site_id.isin(lookup).all():
            raise ValueError("Unseen target site has no fitted intercept")
        mat=np.zeros((len(rows),len(sites)))
        mat[np.arange(len(rows)),rows.site_id.map(lookup).to_numpy(dtype=int)]=1.
        return mat
    mu=train[names].mean().to_numpy(dtype=float)
    sd=train[names].std(ddof=0).to_numpy(dtype=float)
    if not np.isfinite(sd).all() or min(sd)<1e-8:
        raise ValueError("Frozen marine predictor has insufficient training variation")
    def get(rows):
        scalar=(rows[names].to_numpy(dtype=float)-mu)/sd
        return np.column_stack([site_effect(rows),scalar])
    x=get(train)
    xt=get(test)
    if np.linalg.matrix_rank(x)!=x.shape[1]:
        raise ValueError("Training original site effects and climate design rank deficient")
    return x,xt,sites,names,mu,sd

def frozen_fit(train,test,include_salt):
    x,xt,sites,names,mu,sd=design(train,test,include_salt)
    y=train[Y].to_numpy(dtype=float)
    fitted=sm.OLS(y,x).fit()
    values=fitted.predict(xt)
    if not np.isfinite(values).all():
        raise ValueError("Train-only physical model generated nonfinite validation predictions")
    infer={}
    for ctype,clusters in [
        ("wet_ocean_cell",train.source_wet_cell),
        ("source_site",train.site_id),
        ("source_region",train.source_region),
    ]:
        cr=fitted.get_robustcov_results(cov_type="cluster",groups=clusters,use_correction=True)
        inc={}
        for pname in [TEMP,ICE]+([SALT] if include_salt else []):
            index=len(sites)+names.index(pname)
            beta=float(fitted.params[index]/sd[names.index(pname)])
            se=float(cr.bse[index]/sd[names.index(pname)])
            # Conservative normal cluster coefficient interval and an explicit
            # reminder that region groups are sparse.
            inc[pname]={"beta_in_native_physical_units":beta,
                        "cluster_se_in_native_physical_units":se,
                        "cluster_normal_95ci":[beta-1.96*se,beta+1.96*se],
                        "n_source_clusters":int(pd.Series(clusters).nunique())}
        infer[ctype]=inc
    report={
        "training_original_rows":len(train),
        "training_original_sites":int(train.site_id.nunique()),
        "train_only_site_effects":True,
        "train_region_season_effects_used":False,
        "training_R2_in_sample_not_forecast":float(fitted.rsquared),
        "training_source_coefficients":infer,
        "explanatory_numeric_columns":names,
        "original_training_feature_mean":dict(zip(names,map(float,mu))),
        "original_training_feature_SD":dict(zip(names,map(float,sd))),
        "n_estimated_OLS_coefficients":int(x.shape[1]),
        "n_training_algebraic_residual_df":int(fitted.df_resid),
        "train_outcome_year_last":int(train.season.max()),
    }
    return values,report

def metrics(pred,y,w=None):
    pred=np.asarray(pred,dtype=float)
    y=np.asarray(y,dtype=float)
    if w is None:w=np.ones(len(y),dtype=float)
    w=np.asarray(w,dtype=float)
    if len(pred)!=len(y) or min(w)<0 or w.sum()<=0:
        raise ValueError("Invalid original heldout loss denominator")
    diff=pred-y
    return {
        "RMSE":float(np.sqrt(np.average(diff**2,weights=w))),
        "MAE":float(np.average(abs(diff),weights=w)),
        "source_rows":len(y)
    }

def bootstrap_diff_site_region(test,model,baseline,nboot,seed):
    # Signed source-site loss: one biological site one vote.
    bysite=test.groupby(["site_id","source_region"],as_index=False).apply(
        lambda d: pd.Series({"d_sq":float(np.mean((d[model]-d[Y])**2
                      -(d[baseline]-d[Y])**2)),
                             "d_abs":float(np.mean(abs(d[model]-d[Y])
                      -abs(d[baseline]-d[Y])))}),include_groups=False)
    if len(bysite)!=82:raise ValueError("Frozen source-site loss support changed")
    rnames=sorted(bysite.source_region.unique())
    if len(rnames)!=11:raise ValueError("11 matched future source regions required")
    byreg={r:bysite.loc[bysite.source_region==r,["d_sq","d_abs"]].to_numpy()
           for r in rnames}
    rng=np.random.default_rng(seed)
    draws=np.zeros((nboot,2),dtype=float)
    for k in range(nboot):
        chosen=rng.integers(0,len(rnames),size=len(rnames))
        # Each bootstrap region draw contributes its underlying actual source
        # sites; repeated regions are counted with multiplicity.
        pool=np.concatenate([byreg[rnames[j]] for j in chosen],axis=0)
        draws[k]=pool.mean(axis=0)
    lo,hi=np.quantile(draws,[.025,.975],axis=0)
    estimates=bysite[["d_sq","d_abs"]].mean().to_numpy()
    return {
        "comparison":f"{model}_minus_{baseline}",
        "observed_site_equal_delta_MSE":float(estimates[0]),
        "region_bootstrap_delta_MSE_95_percentiles":[float(lo[0]),float(hi[0])],
        "observed_site_equal_delta_MAE":float(estimates[1]),
        "region_bootstrap_delta_MAE_95_percentiles":[float(lo[1]),float(hi[1])],
        "model_beats_comparison_RMSE_and_MAE":bool(estimates[0]<0 and estimates[1]<0),
        "region_bootstrap_MSE_upper_below_zero":bool(hi[0]<0),
        "n_source_sites":len(bysite),
        "n_source_regions":len(rnames),
        "n_resamples":nboot,
        "seed":seed,
        "interpretation":"post-selection region-block sensitivity, not an independent climate trial or prospective experiment"
    }

def predictions(train,test):
    test=test.sort_values(["season","site_id"]).reset_index(drop=True).copy()
    t=train.sort_values(["season","site_id"])
    last=t.groupby("site_id").tail(1).set_index("site_id")
    avg=t.groupby("site_id")[Y].mean()
    test["PERSIST"]=test.site_id.map(last[Y])
    test["SITE_MEAN"]=test.site_id.map(avg)
    test["last_training_season"]=test.site_id.map(last.season).astype(int)
    test["gap_years_since_last_pre2005_observation"]=test.season-test.last_training_season
    test["ICE_THERMAL"],no_salt=frozen_fit(train,test,False)
    test["ICE_THERMAL_SALT"],with_salt=frozen_fit(train,test,True)
    # Independent temporal-persistence comparator: previous available source
    # isotope value strictly before target season, including previous held-out
    # observations. Never used in any of the above four frozen-2004 forecasts.
    past=pd.concat([train,test],ignore_index=True).sort_values(["site_id","season"])
    prior=past.groupby("site_id")[[Y,"season"]].shift(1)
    past["LAST_REAL_PREVIOUS_ISOTOPE_OBS"] = prior[Y]
    past["LAST_REAL_PREVIOUS_YEAR"] = prior["season"]
    past=past.loc[past.season.between(TEST_START,TEST_END)]
    prev=past[["site_id","season","LAST_REAL_PREVIOUS_ISOTOPE_OBS",
               "LAST_REAL_PREVIOUS_YEAR"]]
    test=test.merge(prev,on=["site_id","season"],validate="one_to_one")
    if test["LAST_REAL_PREVIOUS_ISOTOPE_OBS"].isna().any():
        raise ValueError("All known-source test sites should have preceding original observations")
    test["PREVIOUS_OBS_YEAR_GAP"]=test.season-test.LAST_REAL_PREVIOUS_YEAR
    if not (test.PREVIOUS_OBS_YEAR_GAP>=1).all():
        raise ValueError("Prior outcome baseline used same or future observations")
    return test,no_salt,with_salt

def run(source,out):
    df,sha=load_source(source)
    train,test,excluded=frozen_split(df)
    predictions_all,mdl_ice,mdl_salt=predictions(train,test)
    if len(predictions_all)!=541:
        raise ValueError("Held-out same-site source numerator changed")
    test=predictions_all
    counts=test.groupby("site_id").site_id.transform("size").to_numpy(dtype=float)
    site_equal_w=1/counts
    row_result={}
    for m in MODELS+["LAST_REAL_PREVIOUS_ISOTOPE_OBS"]:
        row_result[m]={"site_equal":metrics(test[m],test[Y],site_equal_w),
                       "row_equal":metrics(test[m],test[Y])}
    comps={}
    for k,b in enumerate(["PERSIST","SITE_MEAN","ICE_THERMAL"]):
        comps[b]=bootstrap_diff_site_region(
            test,"ICE_THERMAL_SALT",b,NBOOT,SEED+11*k)
    beta=mdl_salt["training_source_coefficients"]["source_region"][SALT]["beta_in_native_physical_units"]
    coeff_signs=[]
    # Robustness of source-trained salinity sign under removing one *training*
    # region. For fair held-out prediction no retraining on test biological Y.
    for reg in sorted(train.source_region.unique()):
        reduced=train.loc[train.source_region!=reg]
        use=test.loc[test.site_id.isin(reduced.site_id)]
        _,report=frozen_fit(reduced,use,True)
        coeff_signs.append({
            "omitted_source_train_region":reg,
            "n_source_train_sites_remaining":int(reduced.site_id.nunique()),
            "n_source_test_sites_with_trained_intercept":int(use.site_id.nunique()),
            "training_salinity_beta_per_unit":float(
                report["training_source_coefficients"]["source_region"][SALT]["beta_in_native_physical_units"])
        })
    yearly=[]
    for year,g in test.groupby("season"):
        if not 2005<=year<=2012:raise ValueError("Unrecognized test year")
        w=1/g.groupby("site_id").site_id.transform("size")
        for model in MODELS:
            z=metrics(g[model],g[Y],w)
            yearly.append({"year":int(year),"model":model,"n_source_sites":int(g.site_id.nunique()),
                           "RMSE":z["RMSE"],"MAE":z["MAE"]})
    region_rows=[]
    for region,g in test.groupby("source_region"):
        for model in MODELS:
            z=metrics(g[model],g[Y],1/g.groupby("site_id").site_id.transform("size"))
            region_rows.append({"source_region":region,"model":model,
                                "n_site_seasons":len(g),"n_sites":int(g.site_id.nunique()),
                                "RMSE":z["RMSE"],"MAE":z["MAE"]})
    joint=[]
    for key,g in test.groupby("source_wet_cell"):
        for model in MODELS:
            mse=np.mean((g[model]-g[Y])**2)
            joint.append({"source_wet_cell":key,"model":model,"n_original_site_seasons":len(g),
                          "wetcell_equal_mean_squared_error":float(mse)})
    perwet=pd.DataFrame(joint)
    cellmean=perwet.groupby("model").wetcell_equal_mean_squared_error.mean()
    model_skill=float(1-row_result["ICE_THERMAL_SALT"]["site_equal"]["RMSE"]**2/
                       row_result["ICE_THERMAL"]["site_equal"]["RMSE"]**2)
    passes=(
        all(comps[b]["model_beats_comparison_RMSE_and_MAE"] and
            comps[b]["region_bootstrap_MSE_upper_below_zero"]
            for b in ["PERSIST","SITE_MEAN","ICE_THERMAL"])
        and beta>0
        and all(q["training_salinity_beta_per_unit"]>0 for q in coeff_signs)
    )
    summary={
        "status":"GO_OBSERVED_COVARIATE_ISOTOPE_TEMPORAL_HINDCAST_ONLY" if passes else
                 "NO_GO_FUTURE_ISOTOPE_PROJECTION",
        "source_archive_sha256":sha,
        "contract":"FROZEN_TEMPORAL_TRANSFER_AND_TWO_AXIS_TEST_20261118_JA.md",
        "original_source_n_all":len(df),"original_source_all_sites":df.site_id.nunique(),
        "training":{"n_rows":len(train),"sites":int(train.site_id.nunique()),
                    "first_year":int(train.season.min()),"last_year":int(train.season.max()),
                    "actual_source_seasons":sorted(map(int,train.season.unique().tolist())),
                    "regions":int(train.source_region.nunique())},
        "heldout_known_site":{"n_rows":len(test),"sites":int(test.site_id.nunique()),
                              "wet_ocean_cells":int(test.source_wet_cell.nunique()),
                              "regions":int(test.source_region.nunique()),
                              "first_year":int(test.season.min()),"last_year":int(test.season.max()),
                              "test_site_year_rows_with_exact_previous_year_optical_observation":int(
                                  (test.PREVIOUS_OBS_YEAR_GAP==1).sum())},
        "heldout_new_untrained_sites_rejected":{"n_rows":len(excluded),
                                                "sites":int(excluded.site_id.nunique()),
                                                "source_regions":int(excluded.source_region.nunique())},
        "models":row_result,
        "trained_ICE_THERMAL":mdl_ice,
        "trained_ICE_THERMAL_SALT":mdl_salt,
        "training_salt_beta_leave_source_region_out":coeff_signs,
        "paired_region_loss_bootstrap_against_no_salt_and_naives":comps,
        "incremental_salt_heldout_site_equal_MSE_reduction_fraction_vs_no_salt":model_skill,
        "wetcell_equal_rmse_sensitivity":{name:float(np.sqrt(x)) for name,x in cellmean.items()},
        "time_heldout_primary_gate_all_three_loss_and_CI_and_training_sign":bool(passes),
        "known_observed_contemporaneous_marine_predictors_not_future_CMIP6":True,
        "future_region_by_season_fixed_effects_never_fit_or_inferred_from_test_outcome":True,
        "image_to_isotope_optical_calibration_not_year_independent":True,
        "outcome_is_satellite_reconstructed_optical_d15N_not_fish_krill_fraction":True,
        "cannot_use_original_860_region_by_season_slope_0p834_for_forecast":True,
        "scenario_delta_approx_negative0p27_is_unvalidated_algebra_not_forecast":True,
        "no_population_response_or_double_dissociation_proved":True,
    }
    direct={
        "status":"TWO_AXIS_ISOTOPE_COLUMN_ONLY_SAME_TRAIN_DENOMINATOR",
        "training_isotope_same_site_fe_physical_coefficients":{
           "SIC":mdl_salt["training_source_coefficients"]["source_region"][ICE],
           "temperature":mdl_salt["training_source_coefficients"]["source_region"][TEMP],
           "salinity":mdl_salt["training_source_coefficients"]["source_region"][SALT]},
        "heldout_isotope_model_ICE_THERMAL":row_result["ICE_THERMAL"]["site_equal"],
        "heldout_isotope_model_ICE_THERMAL_SALT":row_result["ICE_THERMAL_SALT"]["site_equal"],
        "salinity_added_true_out_of_time_error_reduction":model_skill,
        "ADPE_nest_counts_PC1_minus0p80_confirmed":False,
        "ADPE_nest_counts_PC1_minus0p80_source":"unverified 265-series; old 2456-count cohort produces 159 not 265; cannot use as established dual-dissociation quadrant",
        "85_actual_census_series_absence_of_salt_effect_confirmed":False,
        "85_series_zero_crossing_does_not_establish_equivalence":True,
        "same_site_year_isotope_vs_two_species_nest_pair_overlaps":0,
        "no_joint_two_outcome_prospective_test":True,
        "not_causal_double_dissociation":True
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    test[["site_id","season","source_region","source_wet_cell",Y,*OTHER,SALT,
          "PERSIST","SITE_MEAN","ICE_THERMAL","ICE_THERMAL_SALT",
          "LAST_REAL_PREVIOUS_ISOTOPE_OBS","LAST_REAL_PREVIOUS_YEAR",
          "PREVIOUS_OBS_YEAR_GAP","last_training_season",
          "gap_years_since_last_pre2005_observation"]].to_csv(
        out/"frozen_541_holdout_predictions.csv",index=False)
    pd.DataFrame(yearly).to_csv(out/"holdout_year_by_model_source_loss.csv",index=False)
    pd.DataFrame(region_rows).to_csv(out/"holdout_region_by_model_source_loss.csv",index=False)
    pd.DataFrame(coeff_signs).to_csv(out/"training_salt_beta_omit_each_source_region.csv",index=False)
    pd.DataFrame([
        {"site_id":site,"source_region":g.source_region.iloc[0],
         "n_pre_2005":len(g),"train_last_observed_year":int(g.season.max())}
        for site,g in train.groupby("site_id")
    ]).to_csv(out/"source_site_observation_support.csv",index=False)
    (out/"frozen_temporal_transfer_result.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    (out/"double_dissociation_evidence_gate.json").write_text(
        json.dumps(direct,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({
       "status":summary["status"],
       "n_train":len(train),"n_eval":len(test),"n_sites":int(test.site_id.nunique()),
       "RMSE_site_equal":{m:row_result[m]["site_equal"]["RMSE"] for m in MODELS+["LAST_REAL_PREVIOUS_ISOTOPE_OBS"]},
       "MAE_site_equal":{m:row_result[m]["site_equal"]["MAE"] for m in MODELS},
       "train_salt_beta":beta,
       "train_ice_beta_per_10pp":mdl_salt["training_source_coefficients"]["source_region"][ICE]["beta_in_native_physical_units"]*.1,
       "test_salt_additional_MSE_reduction_vs_M0":model_skill,
       "primary_bootstrap_comparisons":comps,
       "tminus1_real_observed_exact_rows":summary["heldout_known_site"]["test_site_year_rows_with_exact_previous_year_optical_observation"]
    },ensure_ascii=False,indent=2))
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-isotope-zip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_isotope_zip,a.out)
