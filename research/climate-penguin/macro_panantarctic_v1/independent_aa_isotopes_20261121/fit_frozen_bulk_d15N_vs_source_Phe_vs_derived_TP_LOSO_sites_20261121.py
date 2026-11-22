#!/usr/bin/env python3
"""Original Michelson 2026 USAP-DC source-backed, new-target AA measurement audit.

Frozen specification: FROZEN_AA_BULK_PHE_VS_TP_DIAGNOSTIC_20261121_JA.md.
Analyze FULL 65 complete paired feathers only as 55 Site×Year_collected
(mean of multiple specimens), grouped by 4 Region×era strata.
Compare fixed group-null, source-AA Phe, derived TP, both by true leave-one-Site-
out validation, Site-equal MSE and 4999 bootstraps of fixed site-specific losses.
Never join external polynyas/Youngflesh isotope Y, or imply climatic causality.
"""
from __future__ import annotations
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_MEMBER="usapdc_602094/Michelson_2026_Adelie_Feathers_SIA_CSIA_Data.csv"
SOURCE_MD5="f9a91c9d9bf3dba9607bf0767df8c206"
SOURCE_ZIP_SHA="185dca693aa9cef96019e379308fa999d6985e010f9ddd9358e706c69ff9b1ce"
OUTCOMES=["d15N","Phe_d15N","Glu_d15N","Trophic_position"]
SEED=20261121
BOOT=4999
MODELS={"null":[],"Phe_baseline":["Phe_d15N"],"TP_trophic":["Trophic_position"],
        "Both":["Phe_d15N","Trophic_position"]}
GROUPS=["Antarctic Peninsula|historical","Antarctic Peninsula|modern",
        "Ross Sea|historical","Ross Sea|modern"]
REFERENCE_GROUP=GROUPS[0]

def load_source(p:Path):
    p=Path(p)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=SOURCE_ZIP_SHA:
        raise ValueError("USAP-DC original user supplied exact MD5-matched ZIP changed")
    with zipfile.ZipFile(p) as z:
        if z.testzip() is not None:raise ValueError("Original native ZIP CRC fails")
        files=[m.filename for m in z.infolist() if not m.is_dir()]
        if files!=[SOURCE_MEMBER]:raise ValueError("Unexpected native USAP-DC original CSV archive members")
        raw=z.read(SOURCE_MEMBER)
    if hashlib.md5(raw).hexdigest()!=SOURCE_MD5:
        raise ValueError("Original publisher source CSV MD5 failed")
    d=pd.read_csv(io.BytesIO(raw))
    if d.shape!=(108,45) or d.Sample_ID.nunique()!=108:
        raise ValueError("Source Michelson paper original 108x45 records changed")
    for c in OUTCOMES:
        if c not in d or not pd.api.types.is_numeric_dtype(d[c]):
            raise ValueError("Source original measured isotope or TP column missing/invalid")
    if d.Genus_species.nunique()!=1 or d.Genus_species.iloc[0]!="Pygoscelis adeliae":
        raise ValueError("Original biological species changed")
    if d.Sample_type.nunique()!=1 or d.Sample_type.iloc[0]!="Breast feather":
        raise ValueError("Original sample tissue changed")
    if d.Region.isna().any() or d.Site.isna().any() or d.Year_collected.isna().any():
        raise ValueError("Missing metadata to define unit of ecological observation")
    if set(d.Region.unique())!={"Antarctic Peninsula","Ross Sea"}:
        raise ValueError("Original exact two ecological source regions changed")
    d["era"]=np.where(d.Year_collected<=1995,"historical",
              np.where(d.Year_collected>=2000,"modern","UNDEFINED"))
    if (d.era=="UNDEFINED").any():
        raise ValueError("Source publication history period definitions not disjoint")
    d["group"]=d.Region+"|"+d.era
    if set(d.group.unique())!=set(GROUPS):
        raise ValueError("All 4 predefined source region×era groups required")
    sub=d.loc[d[OUTCOMES].notna().all(axis=1)].copy()
    if len(sub)!=65:raise ValueError("Complete original 65 paired source isotope observations drift")
    if not np.isfinite(sub[OUTCOMES].to_numpy(float)).all():
        raise ValueError("Nonfinite original AA isotope or derived TP outcome")
    # Only set one ecological unit per original Site×collection year. A single
    # source site label should not belong to multiple Region names.
    if (sub.groupby("Site").Region.nunique()>1).any():
        raise ValueError("Same original site label ambiguous between two source regions")
    mean=(sub.groupby(["Region","era","group","Site","Year_collected"],as_index=False,sort=True)
            [OUTCOMES].mean())
    n=sub.groupby(["Site","Year_collected"]).size().rename("n_individuals_in_source_site_year")
    mean=mean.merge(n,how="left",on=["Site","Year_collected"],validate="one_to_one")
    if (len(mean),mean.Site.nunique())!=(55,35):
        raise ValueError("Original 65 real specimens not 55 site-years, 35 sites")
    if int(mean.n_individuals_in_source_site_year.sum())!=65:
        raise ValueError("Unexpected original individual-level grouping duplication")
    grp=mean.groupby("group").agg(siteyears=("Site","size"),sites=("Site","nunique")).to_dict(orient="index")
    expectation={GROUPS[0]:23,GROUPS[1]:6,GROUPS[2]:21,GROUPS[3]:5}
    if {k:v["siteyears"] for k,v in grp.items()}!=expectation:
        raise ValueError("Fixed Region×historical/modern sample support changed")
    return d,sub,mean,grp,hashlib.sha256(raw).hexdigest()

def design(d,predictors):
    group=pd.Categorical(d.group,categories=GROUPS)
    if np.any(pd.isna(group)):
        raise ValueError("New unmatched source region×era group")
    matrix=np.column_stack([np.ones(len(d))]+
        [(np.asarray(group)==g).astype(float) for g in GROUPS[1:]]+
        [d[x].to_numpy(dtype=float) for x in predictors])
    return matrix

def fit(train,test,preds):
    X=design(train,preds);Xt=design(test,preds)
    if np.linalg.matrix_rank(X)!=X.shape[1]:
        raise ValueError(f"Training design rank failed for predictors {preds}")
    beta=np.linalg.lstsq(X,train.d15N.to_numpy(float),rcond=None)[0]
    return Xt@beta, beta

def cv(d):
    predictions=d[["Site","Year_collected","group"]].copy()
    for k in MODELS:predictions[f"pred_{k}"]=np.nan
    for site in sorted(d.Site.unique()):
        tr=d[d.Site!=site];te=d[d.Site==site]
        if tr.group.nunique()!=4:
            raise ValueError("LOSO training missing a source group; invalid temporal/region extrapolation")
        for k,preds in MODELS.items():
            p,_=fit(tr,te,preds)
            predictions.loc[te.index,f"pred_{k}"]=p
    if predictions.filter(like="pred_").isna().any().any():
        raise ValueError("LOSO missing source site prediction")
    for k in MODELS:
        predictions[f"sqerr_{k}"]=(d.d15N.to_numpy(float)-predictions[f"pred_{k}"].to_numpy(float))**2
    site=predictions.groupby("Site",as_index=False).agg(
        n_siteyears=("Year_collected","size"),**{
          f"mean_sqerr_{k}":(f"sqerr_{k}","mean") for k in MODELS})
    m={k:float(site[f"mean_sqerr_{k}"].mean()) for k in MODELS}
    rmses={k:float(np.sqrt(v)) for k,v in m.items()}
    delta=(site["mean_sqerr_Phe_baseline"]-site["mean_sqerr_TP_trophic"]).to_numpy(float)
    if len(delta)!=35 or not np.isfinite(delta).all():
        raise ValueError("Site-equal LOSO 35 independent sites not found")
    rng=np.random.default_rng(SEED)
    picks=rng.integers(0,len(delta),size=(BOOT,len(delta)))
    boot=delta[picks].mean(axis=1)
    q=np.quantile(boot,[.025,.975])
    if q[1]<0:status="PHE_BASELINE_PROXY_LOSO_PREDICTIVE_DOMINANCE_SUPPORTED"
    elif q[0]>0:status="TP_TROPHIC_LOSO_PREDICTIVE_DOMINANCE_SUPPORTED"
    else:status="NO_CLEAR_LOSO_BASELINE_VS_TP_PREDICTIVE_DOMINANCE"
    return site,{"site_equal_mse":m,"site_equal_rmse":rmses,
      "Phe_minus_TP_paired_site_equal_MSE_delta":float(delta.mean()),
      "paired_site_bootstrap_n":BOOT,
      "paired_site_bootstrap_seed":SEED,
      "Phe_minus_TP_bootstrap_95pct":list(map(float,q)),
      "n_distinct_source_sites_in_CV":len(delta),
      "status":status}

def partial(d):
    # Full historical+modern site-year source sample, fixed region×era blocks
    y=d.d15N.to_numpy(float)
    groups={}
    for k,preds in MODELS.items():
        X=design(d,preds)
        if np.linalg.matrix_rank(X)!=X.shape[1]:
            raise ValueError("Full source group-adjusted regression rank deficient")
        _,coef=fit(d,d,preds)
        resid=y-X@coef
        groups[k]={"sse":float(resid@resid),"n_rows":len(d),
                   "df_residual":len(d)-X.shape[1],
                   "residualized_coefficients":{p:float(v) for p,v in zip(preds,coef[-len(preds):])} if preds else {}}
    sse0=groups["null"]["sse"]
    result={"same55_siteyears_region_era_adjusted_fit":groups,
      "fraction_of_within_region_era_bulk_variance_explained":{
       k:float(1-v["sse"]/sse0) for k,v in groups.items()},
      "conditional_incremental_residual_R2":{
        "add_Phe_to_TP":float(1-groups["Both"]["sse"]/groups["TP_trophic"]["sse"]),
        "add_TP_to_Phe":float(1-groups["Both"]["sse"]/groups["Phe_baseline"]["sse"])},
      "source_Phe_TP_pooled_Pearson_r":float(d.Phe_d15N.corr(d.Trophic_position)),
      "same55_group_adjusted_Phe_TP_Pearson_r":None}
    # To remove the group nuisance, re-centre both data vectors within same 4 groups.
    b=d.Phe_d15N-d.groupby("group").Phe_d15N.transform("mean")
    tp=d.Trophic_position-d.groupby("group").Trophic_position.transform("mean")
    result["same55_group_adjusted_Phe_TP_Pearson_r"]=float(b.corr(tp))
    X=design(d,["Phe_d15N","Trophic_position"])
    sdP=float(d.Phe_d15N.std(ddof=0))
    sdTP=float(d.Trophic_position.std(ddof=0))
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    result["Both_partial_effect_per_1_source_overall_SD"]={
      "Phe_d15N_per_SD_bulk_per_mille":float(coef[-2]*sdP),
      "TP_per_SD_bulk_per_mille":float(coef[-1]*sdTP),
      "Phe_source_SD":sdP,
      "TP_source_SD":sdTP}
    return result

def repeated_sites(d):
    counts=d.groupby("Site").Year_collected.nunique()
    keep=d[d.Site.isin(counts[counts>=2].index)].copy()
    if keep.Site.nunique()!=12 or len(keep)!=32:
        raise ValueError("Frozen 12 sites 32 siteyear within-site support drift")
    y=keep.d15N.to_numpy(float)
    site=keep.Site.to_numpy()
    def demean(v):
        v=np.asarray(v,dtype=float).copy()
        return v-np.asarray(pd.Series(v).groupby(site,sort=False).transform("mean"),float)
    yres=demean(y)
    effects={}
    for label,preds in (("Phe_baseline",["Phe_d15N"]),
                         ("TP_trophic",["Trophic_position"]),
                         ("Both",["Phe_d15N","Trophic_position"])):
        X=np.column_stack([demean(keep[p]) for p in preds])
        rank=int(np.linalg.matrix_rank(X))
        if rank!=len(preds):
            effects[label]={"status":"NOT_IDENTIFIABLE","rank":rank}
        else:
            b=np.linalg.lstsq(X,yres,rcond=None)[0]
            err=yres-X@b
            effects[label]={"status":"ESTIMABLE_DESCRIPTIVE_ONLY",
               "predictors":preds,"coefficient":dict(zip(preds,map(float,b))),
               "within_site_SSE":float(err@err),"n_siteyears":len(keep),
               "n_independent_sites":int(keep.Site.nunique()),
               "within_site_r_squared":float(1-(err@err)/(yres@yres))}
    return effects

def descriptive(d):
    summaries=[]
    for group,g in d.groupby("group",sort=True):
        v={"group":group,"siteyears":len(g),"sites":int(g.Site.nunique()),
           "min_collection_year":int(g.Year_collected.min()),
           "max_collection_year":int(g.Year_collected.max())}
        for c in ["d15N","Phe_d15N","Trophic_position"]:
            v[f"{c}_mean"]=float(g[c].mean())
            v[f"{c}_median"]=float(g[c].median())
        summaries.append(v)
    return summaries

def main(a):
    a.out.mkdir(parents=True,exist_ok=True)
    full,complete,d,support,raw_sha=load_source(a.source)
    sites,cv_result=cv(d)
    within=partial(d)
    sensitivity=repeated_sites(d)
    desc=descriptive(d)
    # Original RAW isotope rows and row-level Y are not distributed in repo;
    # only one observed-site crossvalidation loss per location and aggregate results.
    sites.to_csv(a.out/"USAP602094_SAME65_TO_55_GROUP_LOSO_PAIRED_SITE_MSE.csv",
                 index=False,float_format="%.12g")
    pd.DataFrame(desc).to_csv(
        a.out/"USAP602094_FOUR_ERA_REGION_GROUP_DESCRIPTIVE_MEANS.csv",
        index=False,float_format="%.12g")
    result={
      "status":"EXACT_USAP602094_REAL_AA_BULK_BASELINE_VS_TP_SITE_BLOCKED_MEASUREMENT_DIAGNOSTIC_COMPUTED",
      "source_DOI":"10.15784/602094",
      "source_published_original_csv_MD5":SOURCE_MD5,
      "source_unmodified_CSV_SHA256":raw_sha,
      "source_zip_sha256":SOURCE_ZIP_SHA,
      "source_sampling_units":{"108_original_feathers":len(full),
        "65_complete_four_values":len(complete),
        "55_independent_source_site_collection_years":len(d),
        "35_unique_original_sites":int(d.Site.nunique()),
        "region_era_group_support":support,
        "actual_feather_growth_year_unknown":True},
      "primary_leave_one_site_out":cv_result,
      "secondary_within_four_source_groups":within,
      "secondary_within_repeated_sites_12_sites_32_siteyears":sensitivity,
      "source_sample_group_descriptive":desc,
      "comparison_has_no_marine_winter_polynya_exposure":True,
      "body_tissue_breast_feather_not_summer_guano":True,
      "TP_is_derived_from_Glu_Phe_not_independent_direct_prey_composition":True,
      "isotope_baseline_Phe_is_proxy_not_direct_Nitrate":True,
      "historical_modern_different_sites_and_sample_types":True,
      "no_2013_2021_Youngflesh_L8_new_guano_Y":True,
      "not_original_Michelson2026_manuscript_reproduction":True,
      "not_independent_replication_of_past_439_negative_polynya_association":True
    }
    (a.out/"USAP602094_FROZEN_BULK_PHE_TP_SITE_LOSO_MAIN_VERDICT.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps({
      "status":result["status"],"source_support":result["source_sampling_units"],
      "primary":cv_result,"secondary_conditional_R2":
         within["fraction_of_within_region_era_bulk_variance_explained"],
      "secondary_unique_R2":within["conditional_incremental_residual_R2"],
      "within_site_sensitivity":sensitivity,
      "not_independent_polynya_retest":True},indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
