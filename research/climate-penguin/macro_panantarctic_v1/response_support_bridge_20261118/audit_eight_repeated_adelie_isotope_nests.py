#!/usr/bin/env python3
"""Original-source same site×season Adélie nest counts versus δ15N optical proxy.

This is a focused follow-up from true 70 source matches / 49 colonies;
strictly repeat-observed 8 site IDs, 29 site-seasons. It cannot identify causal
salinity→prey→breeding mediation, prey proportions, or site dispersal.
"""
import argparse,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf
from scipy.stats import t

ISO="predicted_d15N_season_day_equal"
COUNT="log1p_original_nests"
SAL="GLORYS_NovFeb_salinity"
SIC="author_SIC_150km_NovFeb_center_approx_fraction"
TMP="GLORYS_NovFeb_thetao_C"

def csvz(path,name):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError("Source ZIP checksum/integrity failed")
        return pd.read_csv(io.BytesIO(z.read(name)))

def original_29(bridge,iso,cens):
    b=csvz(bridge,"source_70_exact_Adelie_nests_isotope_overlap_observation_only.csv")
    p=csvz(iso,"matched_860_original_isotope_ocean_ice_site_seasons.csv")
    c=csvz(cens,"source_observed_2456.csv")
    if (len(b),b.site_id.nunique(),len(p),p.site_id.nunique(),len(c))!=(70,49,860,88,2456):
        raise ValueError("Original source panel denominators drifted")
    if b.duplicated(["site_id","season"]).any() or p.duplicated(["site_id","season"]).any():
        raise ValueError("Site/season duplicate in biological original")
    b=b.merge(p,on=["site_id","season"],suffixes=("","_iso"),validate="one_to_one")
    for col in [ISO,SAL]:
        if not np.allclose(b[col],b[col+"_iso"],atol=1e-9,rtol=0):
            raise ValueError("Primary isotope or salinity source value mismatch")
    z=c.query("species=='ADPE'")
    z=z[["site_id","season","observed_nest_count","original_survey_method","source_region"]]
    b=b.merge(z,on=["site_id","season"],validate="one_to_one",suffixes=("","_count"))
    if not np.all(b.observed_nest_count==b.observed_nest_count_count):
        raise ValueError("Original count is not the observed MAPPPD value")
    if not (b.source_region==b.source_region_count).all():
        raise ValueError("Original colony reporting region mismatch")
    freq=b.groupby("site_id").size()
    d=b.loc[b.site_id.isin(freq.index[freq>=2])].copy().reset_index(drop=True)
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(29,8,4):
        raise ValueError("Original repeat survey source support changed")
    if not d.groupby("site_id").original_survey_method.nunique().eq(1).all():
        raise ValueError("Within-site original census survey methods not fixed")
    if d[[ISO,SAL,SIC,TMP,"mean_doy_centered","n_source_pixels"]].isna().any().any():
        raise ValueError("Incomplete observed isotope or physical source")
    d[COUNT]=np.log1p(d.observed_nest_count)
    d["year_c"]=d.season-d.season.mean()
    d["site_equal_w"]=1/d.groupby("site_id").site_id.transform("size")
    d["marine_cell"]=d.source_wet_grid_y.astype(str)+":"+d.source_wet_grid_x.astype(str)
    return d

def estimate(d,form,site_equal=True):
    d=d.reset_index(drop=True)
    m=(smf.wls(form,data=d,weights=d.site_equal_w) if site_equal else smf.ols(form,data=d)).fit()
    n=int(d.site_id.nunique())
    c=m.get_robustcov_results(cov_type="cluster",groups=d.site_id,use_correction=True)
    i=list(m.params.index).index(ISO)
    b=float(m.params[ISO]);se=float(c.bse[i])
    cut=float(t.ppf(.975,n-1))
    return {"n":len(d),"sites":n,"beta":b,"site_cluster95ci":[b-cut*se,b+cut*se],
            "cluster_se":se,"algebraic_df":float(m.df_resid),"site_equal":site_equal}

def difference(d):
    result=[]
    for site,a in d.groupby("site_id"):
        a=a.sort_values("season")
        for i in range(1,len(a)):
            old,new=a.iloc[i-1],a.iloc[i]
            gap=int(new.season-old.season)
            if gap<=0:raise ValueError("Not real ascending observed seasons")
            result.append({"site_id":site,"source_region":new.source_region,
                           "from_season":int(old.season),"to_season":int(new.season),"gap_years":gap,
                           "delta_log_nests":float(new[COUNT]-old[COUNT]),
                           "delta_optical_d15N":float(new[ISO]-old[ISO]),
                           "delta_NovFeb_salinity":float(new[SAL]-old[SAL]),
                           "delta_NovFeb_SIC":float(new[SIC]-old[SIC]),
                           "same_sign":bool((new[COUNT]-old[COUNT])*(new[ISO]-old[ISO])>0)})
    out=pd.DataFrame(result)
    if len(out)!=21:raise ValueError("Original observed transitions changed")
    return out

def run(a):
    d=original_29(a.bridge,a.isotope,a.counts)
    simple=f"{COUNT} ~ C(site_id) + {ISO}"
    time=simple+" + year_c"
    physics=time+f" + {SIC} + {TMP} + {SAL}"
    image=physics+" + mean_doy_centered + np.log1p(n_source_pixels)"
    result={"status":"EXPLORATORY_TRUE_OBSERVED_EIGHT_SITE_ADPE_COUNT_ISOTOPE_BRIDGE",
            "original_overlap_any_adpe_site_seasons":70,
            "observed_repeated_site_seasons":len(d),
            "observed_repeated_sites":int(d.site_id.nunique()),
            "observed_reporting_regions":int(d.source_region.nunique()),
            "distinct_source_marine_wet_grid_cells":int(d.marine_cell.nunique()),
            "site_counts":d.groupby("site_id").size().astype(int).to_dict(),
            "source_methods_sites":d.groupby("original_survey_method").site_id.nunique().astype(int).to_dict(),
            "site_equal_models":{"site_fixed":estimate(d,simple),
                                 "site_and_calendar_time":estimate(d,time),
                                 "site_time_novfeb_sic_temperature_salinity":estimate(d,physics),
                                 "site_time_marine_and_image_support":estimate(d,image)},
            "one_record_one_weight_physics_sensitivity":estimate(d,physics,False),
            "not_original_author_diet_posterior":True,
            "not_true_prey_fraction_or_isotope_baseline":True,
            "not_climate_causality_or_demographic_predictor":True}
    base=smf.wls(physics.replace(" + "+ISO,""),data=d,weights=d.site_equal_w).fit()
    full=smf.wls(physics,data=d,weights=d.site_equal_w).fit()
    result["exploratory_partial_residual_r2_iso_after_marine"]=float(
        1-sum(d.site_equal_w*full.resid**2)/sum(d.site_equal_w*base.resid**2))
    om=[]
    for site in sorted(d.site_id.unique()):
        q=d[d.site_id!=site].copy()
        om.append({"omitted_site_id":site,"beta":estimate(q,physics)["beta"]})
    result["leave_one_source_site_out"]=om
    regions=[]
    for region in sorted(d.source_region.unique()):
        q=d[d.source_region!=region]
        if q.site_id.nunique()<3:continue
        try:
            b=estimate(q,physics)
            regions.append({"omitted_region":region,"n":len(q),"sites":int(q.site_id.nunique()),"beta":b["beta"],"algebraic_df":b["algebraic_df"]})
        except Exception as e:
            regions.append({"omitted_region":region,"error":type(e).__name__+":"+str(e)[:180]})
    result["leave_one_source_region_out"]=regions
    freq=d.groupby("site_id").size()
    only3=d[d.site_id.isin(freq.index[freq>=3])]
    result["at_least_three_actual_census_years_per_site_sensitivity"]=estimate(only3,physics)
    changes=difference(d)
    result["observed_intervals"]={"n":len(changes),
        "actual_consecutive_year_intervals":int((changes.gap_years==1).sum()),
        "median_gap_years":float(changes.gap_years.median()),
        "max_gap_years":int(changes.gap_years.max()),
        "same_direction_raw_changes":int(changes.same_sign.sum()),
        "not_independent_population_replicates":True}
    result["most_repeated_site_share"]=float(freq.max()/len(d))
    result["interpretation"]="Isotope association sign positive in fitted 8-site observational models; source-site and source-region intervals include zero or attenuate; no demonstrated universal nest response or salinity→food→breeding link."
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    d.to_csv(out/"original_29_Adelie_nests_optical_isotope_and_marine_site_seasons.csv",index=False)
    changes.to_csv(out/"original_21_within_colony_actual_survey_intervals.csv",index=False)
    (out/"original_eight_site_isotope_nesting_bridge_receipt.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for n in ["bridge","isotope","counts","out"]:p.add_argument("--"+n,required=True)
    run(p.parse_args())
