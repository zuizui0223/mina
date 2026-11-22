#!/usr/bin/env python3
"""A fixed, source-pinned interaction diagnostic on 860 original isotope seasons.

One primary hypothesis, stated BEFORE checking this interaction's coefficient:
Is salinity's conditional association with satellite-derived Adélie guano
δ15N stronger/weaker or sign-reversed at colonies experiencing more mean local
Nov–February sea ice? The moderator is the SITE-EQUAL historical mean SIC of
the same 860 original-image observed seasons, NOT a truly independent 30-year
climatology. Its statistical support therefore depends on image seasons.

Primary model = frozen baseline (site + source-region×season FE, DOY, DOY²,
same Nov–Feb SIC, GLORYS temperature and salinity) + ONE linear interaction
salinity×background-site-SIC / 10 percentage points. Primary result is
reported regardless of sign and p. No thresholds or background ice cutpoints
chosen to maximize effect. No diet-prey-fraction or salinity causality claim.
"""
from __future__ import annotations
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t

SOURCE_SHA256="dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
SOURCE_CSV="matched_860_original_isotope_ocean_ice_site_seasons.csv"
Y="predicted_d15N_season_day_equal"
SALT="GLORYS_NovFeb_salinity"
ICE="author_SIC_150km_NovFeb_center_approx_fraction"
COLS=["mean_doy_centered","mean_doy_sq","GLORYS_NovFeb_thetao_C",ICE,SALT]
SMALL=1e-10

def open_source(src):
    raw=Path(src).read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=SOURCE_SHA256:raise ValueError("Original 860 source artifact SHA256 mismatch: "+sha)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:raise ValueError("Source original ZIP failed CRC")
        d=pd.read_csv(io.BytesIO(z.read(SOURCE_CSV)),low_memory=False)
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(860,88,13):
        raise ValueError("Frozen positive salinity result source cohort changed")
    ncell=d[["source_wet_grid_y","source_wet_grid_x"]].drop_duplicates().shape[0]
    if ncell!=82 or d.duplicated(["site_id","season"]).any():
        raise ValueError("Original 82 wet cells or site-season source identity changed")
    if not np.isfinite(d[COLS+[Y]].to_numpy(dtype=float)).all():
        raise ValueError("Non-finite original isotope or marine source")
    if not d[ICE].between(0,1).all():
        raise ValueError("Original NSIDC sea ice must be a 0–1 fraction")
    d=d.copy()
    sitetable=d.groupby("site_id",as_index=False).agg(
        original_source_region=("source_region","first"),
        n_original_image_seasons=("season","size"),
        site_observed_NovFeb_ice_mean_fraction=(ICE,"mean"),
    )
    sitetable["site_ice_mean_pp"]=100*sitetable.site_observed_NovFeb_ice_mean_fraction
    reg_mean=sitetable.groupby("original_source_region").site_ice_mean_pp.transform("mean")
    overall=float(sitetable.site_ice_mean_pp.mean())
    sitetable["site_ice_ctx_c10"]=(sitetable.site_ice_mean_pp-overall)/10
    sitetable["site_ice_within_region_c10"]=(sitetable.site_ice_mean_pp-reg_mean)/10
    d=d.merge(sitetable[["site_id","site_ice_mean_pp","site_ice_ctx_c10",
                         "site_ice_within_region_c10"]],
              on="site_id",validate="many_to_one")
    d["site_ice_anom10"]=(100*d[ICE]-d.site_ice_mean_pp)/10
    d["salinity_centered"]=d[SALT]-d[SALT].mean()
    d["interaction_context"]=d.salinity_centered*d.site_ice_ctx_c10
    d["interaction_context_within_region"]=d.salinity_centered*d.site_ice_within_region_c10
    d["interaction_seasonal_anomaly"]=d.salinity_centered*d.site_ice_anom10
    d["wetcell"]=d.source_wet_grid_y.astype(str)+":"+d.source_wet_grid_x.astype(str)
    return d,sitetable,overall

def source_fe_groups(d):
    site=pd.factorize(d.site_id,sort=True)[0]
    regionyear=pd.factorize(d.source_region.astype(str)+"__"+d.season.astype(str),sort=True)[0]
    return [(code,np.bincount(code)) for code in [site,regionyear]]

def residualize(a,groups):
    v=np.asarray(a,dtype=float).copy()
    for _ in range(3000):
        old=v.copy()
        for code,group_n in groups:
            v-=(np.bincount(code,weights=v,minlength=len(group_n))/group_n)[code]
        if np.max(abs(v-old))<SMALL:break
    else:raise ValueError("Original fixed-effect source demeaning did not converge")
    for code,group_n in groups:
        leftover=np.bincount(code,weights=v,minlength=len(group_n))/group_n
        if abs(leftover).max()>1e-7:raise ValueError("Fixed effects remain")
    return v

def design(d,add=None):
    groups=source_fe_groups(d)
    X=np.column_stack([residualize(d[k],groups) for k in COLS+(add or [])])
    y=residualize(d[Y],groups)
    if np.linalg.matrix_rank(X,tol=1e-9)<X.shape[1]:
        raise ValueError("Original fixed source interaction regression is rank deficient")
    return X,y

def fit(d,interactions,cluster="wetcell"):
    X,y=design(d,interactions)
    grp=d.wetcell if cluster=="wetcell" else d.source_region
    n=int(grp.nunique())
    if n<3:raise ValueError("Insufficient source climate clusters")
    fitted=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":grp})
    normal_ci=fitted.conf_int()
    cutoff=float(t.ppf(.975,n-1))
    items=[]
    for idx,col in enumerate(COLS+interactions):
        b=float(fitted.params[idx]);se=float(fitted.bse[idx])
        items.append({
            "term":col,
            "beta":b,
            "cluster_se":se,
            "normal_95ci":[float(normal_ci[idx,0]),float(normal_ci[idx,1])],
            "conservative_t_cluster_minus1_95ci":[b-cutoff*se,b+cutoff*se],
            "two_sided_normal_p_descriptive":float(fitted.pvalues[idx])
        })
    return fitted,{
        "cluster":cluster,
        "n_colony_seasons":len(d),
        "n_sites":int(d.site_id.nunique()),
        "n_marine_wet_cells":int(d.wetcell.nunique()),
        "n_reporting_regions":int(d.source_region.nunique()),
        "n_clusters":n,
        "columns":items,
        "not_an_independent_species_or_diet_causality_test":True
    }

def run(source,out):
    d,site,overall=open_source(source)
    primary="interaction_context"
    base,base_res=fit(d,[],"wetcell")
    if abs(base.params[-1]-.8341458422028288)>1e-7:
        raise ValueError("Original published source conditional positive salinity association changed")
    # One primary interaction and two separate sensitivity diagnostics, never
    # let a positive secondary effect override a failing primary hypothesis.
    full,cell=fit(d,[primary],"wetcell")
    regfit,regions=fit(d,[primary],"region")
    ix=cell["columns"][-1];ir=regions["columns"][-1]
    reduced=np.sum(base.resid**2);extended=np.sum(full.resid**2)
    extra=float(1-extended/reduced)
    if not (0<=extra<=1):raise ValueError("Source original nested-model SSE invalid")
    q25=float(site.site_ice_mean_pp.quantile(.25))
    q75=float(site.site_ice_mean_pp.quantile(.75))
    slopes=[]
    for q,label in [(q25,"observed_source_site_ice_Q25"),(q75,"observed_source_site_ice_Q75")]:
        ctx=(q-overall)/10
        for name,m,nclusters in [("wetcell",full,d.wetcell.nunique()),("region",regfit,d.source_region.nunique())]:
            # SAL = coefficient index 4; interaction = index 5
            weights=np.asarray([1.,ctx])
            beta=float(weights@m.params[[4,5]])
            cov=m.cov_params()[np.ix_([4,5],[4,5])]
            se=float(np.sqrt(weights@cov@weights))
            cutoff=float(t.ppf(.975,int(nclusters)-1))
            slopes.append({
                "ice_level":label,"site_ice_pp":q,"cluster_type":name,
                "salinity_slope_delta15N_per_salinity_unit":beta,
                "cluster_t95ci":[beta-cutoff*se,beta+cutoff*se]
            })
    # Geographic stress test. Hold the original context scaling fixed when
    # removing a source region; don't re-center context after seeing effect.
    omitted=[]
    for region in sorted(d.source_region.unique()):
        r=d.loc[d.source_region!=region].reset_index(drop=True)
        fitloo,summary=fit(r,[primary],"wetcell")
        omitted.append({
            "omitted_original_source_region":region,
            "n_site_seasons_retained":len(r),
            "n_source_wet_cells_retained":int(r.wetcell.nunique()),
            "beta_interaction_per_10pp_site_background_sic":float(fitloo.params[-1]),
            "wetcell_cluster_t95ci":summary["columns"][-1]["conservative_t_cluster_minus1_95ci"],
        })
    strong_regions=site.groupby("original_source_region").site_id.size()
    supported=set(strong_regions.index[strong_regions>=3])
    subset=d.loc[d.source_region.isin(supported)]
    supported_fit,supported_info=fit(subset,[primary],"wetcell")
    # Detect whether the apparent between-region contrast is attributable to
    # real within-region site ice differences.
    within_fit,within_info=fit(d,["interaction_context_within_region"],"wetcell")
    annual_fit,annual_info=fit(d,["interaction_seasonal_anomaly"],"wetcell")
    report={
        "status":"SOURCE_VERIFIED_INTERACTION_NO_CONFIRMED_SALT_EFFECT_SIGN_SWITCH",
        "source":"original 860 site-season satellite optical isotope dataset 14328755565",
        "model_primary":"original two-way site + region×season FE with original DOY, DOY², Nov–Feb GLORYS water temperature, original 150km SIC and salinity, plus ONE site-background-ice × salinity linear interaction",
        "preselected_background_ice":"site-equal mean of available originally image-covered November–February SIC seasons per source site, not independent fixed climatology",
        "site_mean_ice_pp":{"mean":overall,"q25":q25,"median":float(site.site_ice_mean_pp.median()),"q75":q75,"min":float(site.site_ice_mean_pp.min()),"max":float(site.site_ice_mean_pp.max())},
        "primary_term_scale":"delta15N per 1 salinity unit per +10 percentage points of mean Nov-Feb sea ice among source site",
        "primary_model_cell_cluster":cell,
        "primary_model_region_cluster":regions,
        "original_salinity_no_interaction_beta":float(base.params[-1]),
        "primary_additional_residual_partial_r2":extra,
        "predicted_salt_slopes_at_observed_ice_quantiles":slopes,
        "leave_one_region_out_interaction":omitted,
        "within_region_centered_site_context_sensitivity":within_info,
        "at_least_three_isotope_sites_per_source_region_sensitivity":supported_info,
        "contemporaneous_ice_anomaly_sensitivity_NOT_PRIMARY":annual_info,
        "marine_model_regime_interaction_confirmed":False,
        "region_slope_reversal_explained_by_ice_context":False,
        "not_measured_diet_fraction_or_original_hierarchical_posterior":True,
        "salinity_positive_main_effect_retained_separately":True,
        "posthoc_scanning_for_significant_interactions_prohibited":True,
        "not_future_climate_to_nest_prediction":True,
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    site.to_csv(out/"source_88_original_isotope_site_ice_background_from_observed_seasons.csv",index=False)
    pd.DataFrame(omitted).to_csv(out/"source_13_region_omission_original_background_ice_salt_interaction.csv",index=False)
    pd.DataFrame(slopes).to_csv(out/"source_Q25_Q75_background_seaice_salinity_slopes.csv",index=False)
    (out/"original_860_salinity_background_ice_interaction_verdict.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({
        "status":report["status"],
        "original_salinity_main_effect":report["original_salinity_no_interaction_beta"],
        "primary_interaction_beta":ix["beta"],
        "primary_82_wetcell_t95ci":ix["conservative_t_cluster_minus1_95ci"],
        "primary_13_region_t95ci":ir["conservative_t_cluster_minus1_95ci"],
        "partial_residual_r2":extra,
        "ice_context_q25_q75":[q25,q75],
        "primary_predicted_salinity_slopes":[x["salinity_slope_delta15N_per_salinity_unit"]
            for x in slopes if x["cluster_type"]=="wetcell"],
        "within_region_background_interaction_beta":float(within_fit.params[-1]),
        "seasonal_ice_anomaly_interaction_beta_sensitivity_only":float(annual_fit.params[-1]),
        "omission_interaction_beta_range":[float(min(z["beta_interaction_per_10pp_site_background_sic"] for z in omitted)),
                                           float(max(z["beta_interaction_per_10pp_site_background_sic"] for z in omitted))]
    },indent=2,ensure_ascii=False))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-isotope-zip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_isotope_zip,a.out)
