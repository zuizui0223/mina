#!/usr/bin/env python3
"""Reproducible exploratory isotope-proxy × local salinity association.

All user inputs must be SOURCE-AUDITED DERIVED tables produced by pinned
Youngflesh (2026) Zenodo and mina GLORYS/NSIDC original workflows.
No abundance forecast, original Stan DI posterior or causal claim.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.api as sm
from scipy.stats import t

COLS=['mean_doy_centered','mean_doy_sq','GLORYS_NovFeb_thetao_C',
      'author_SIC_150km_NovFeb_center_approx_fraction','GLORYS_NovFeb_salinity']
Y='predicted_d15N_season_day_equal'

def project_fe(x,sites,region_season):
    v=np.asarray(x,dtype=float).copy()
    s=pd.Series(np.asarray(sites))
    g=pd.Series(np.asarray(region_season))
    for _ in range(3000):
        old=v.copy()
        v-=pd.Series(v).groupby(s,sort=False).transform("mean").to_numpy()
        v-=pd.Series(v).groupby(g,sort=False).transform("mean").to_numpy()
        if np.max(np.abs(v-old))<1e-10:break
    if max(np.max(np.abs(pd.Series(v).groupby(s).mean())),
           np.max(np.abs(pd.Series(v).groupby(g).mean())))>1e-6:
        raise ValueError("Fixed effects did not converge")
    return v

def solve(d,cluster="cell",specific_region=False):
    d=d.reset_index(drop=True).copy()
    g=d.season if specific_region else d.source_region.astype(str)+"__"+d.season.astype(str)
    x=np.column_stack([project_fe(d[k],d.site_id,g) for k in COLS])
    y=project_fe(d[Y],d.site_id,g)
    if np.linalg.matrix_rank(x)<len(COLS):raise ValueError("Rank-deficient salinity test")
    z=d.source_wet_grid_y.astype(str)+":"+d.source_wet_grid_x.astype(str)
    groups={"cell":z,"site":d.site_id,"region":d.source_region,"season":d.season}[cluster]
    fit0=sm.OLS(y,x[:,:4]).fit()
    fit1=sm.OLS(y,x).fit(cov_type="cluster",cov_kwds={"groups":groups})
    beta=float(fit1.params[-1]);se=float(fit1.bse[-1]);n=int(pd.Series(groups).nunique())
    return {"n":len(d),"n_source_sites":int(d.site_id.nunique()),
            "n_source_regions":int(d.source_region.nunique()),
            "n_wet_grid_cells":int(z.nunique()),
            "cluster_type":cluster,"n_clusters":n,
            "beta_salinity":beta,"cluster_se":se,
            "normal_95ci":list(map(float,fit1.conf_int()[-1])),
            "conservative_t_gminus1_95ci":[beta-t.ppf(.975,n-1)*se,beta+t.ppf(.975,n-1)*se],
            "partial_residual_r2":float(1-np.sum(fit1.resid**2)/np.sum(fit0.resid**2))}

def main(a):
    iso=pd.read_csv(a.isotope)
    days=pd.read_csv(a.isotope_days)
    ocean=pd.read_csv(a.glorys)
    sic=pd.read_csv(a.nsidc)
    for label,d in [("proxy",iso),("daily",days),("marine",ocean),("SIC",sic)]:
        if d.duplicated(["site_id","season"]).any() and label!="daily":
            raise ValueError("Duplicate site×season in "+label)
    if (len(iso),iso.site_id.nunique())!=(860,88):
        raise ValueError("Strict original-publisher cohort must be 860 site-season / 88 sites")
    if len(ocean)!=892 or len(sic)!=892:
        raise ValueError("Publisher-matched ocean/ice cohort must retain original 892")
    days['date']=pd.to_datetime(days[["year","month","day"]])
    days['doy']=(days.date-pd.to_datetime(days.season.astype(str)+"-11-01")).dt.days+1
    if not days.doy.between(1,125).all():raise ValueError("Original capture outside Nov–Feb")
    days['doy_c']=days.doy-60
    days['doy_sq']=days.doy_c**2
    timing=days.groupby(["site_id","season"],as_index=False).agg(
        mean_doy_centered=("doy_c","mean"),mean_doy_sq=("doy_sq","mean"))
    o=ocean[["site_id","season","source_wet_grid_y","source_wet_grid_x",
             "GLORYS_NovFeb_salinity","GLORYS_NovFeb_thetao_C","all_four_original_months_valid"]]
    s=sic[["site_id","season","author_SIC_150km_NovFeb_center_approx_fraction",
           "all_four_sic_months_valid","min_n_valid_25km_source_cells"]]
    d=iso.merge(o,on=["site_id","season"],validate="one_to_one")
    d=d.merge(s,on=["site_id","season"],validate="one_to_one")
    d=d.merge(timing,on=["site_id","season"],validate="one_to_one")
    if (len(d),d.site_id.nunique())!=(860,88):
        raise ValueError("True source intersection lost matched rows")
    if not bool((d.all_four_original_months_valid & d.all_four_sic_months_valid).all()):
        raise ValueError("No imputation or missing source seasons allowed")
    if not d.min_n_valid_25km_source_cells.ge(3).all():
        raise ValueError("Insufficient native ocean pixel support")
    if not np.isfinite(d[COLS+[Y]].to_numpy(dtype=float)).all():
        raise ValueError("Invalid original sourced predictor or isotope")
    results={"status":"EXPLORATORY_ORIGINAL_SOURCE_ISOTOPE_PROXY_SALINITY_ASSOCIATION",
             "not_original_published_hierarchical_DI":True,
             "not_fish_or_krill_fraction":True,
             "not_causal_or_out_of_region_prospective":True,
             "nonindependent_years_and_cells":True,
             "season":"November–following February (both physics and isotope proxy)",
             "source_ice":"NSIDC G02202 V4 original 25km native **pixel-center** 150km circle approximation",
             "reference":"https://nsidc.org/data/user-resources/help-center/guide-nsidcs-polar-stereographic-projection"}
    results["fixed_source_primary_cell_cluster"]=solve(d,"cell")
    results["original_reporting_region_cluster"]=solve(d,"region")
    outregions=[]
    for r,q in d.groupby("source_region"):
        n=int(q.site_id.nunique())
        nwet=int(q[["source_wet_grid_x","source_wet_grid_y"]].drop_duplicates().shape[0])
        row={"region":r,"n":len(q),"n_site":n,"n_wetcell":nwet}
        if n>=3 and nwet>=3 and len(q)>=25:
            try:row|=solve(q,"cell",specific_region=True)
            except ValueError as e:row["excluded"]=str(e)
        else:row["excluded"]="insufficient independent source within-region support"
        outregions.append(row)
    results["leave_one_region_out"]=[]
    for region in sorted(d.source_region.unique()):
        try:
            fitted=solve(d[d.source_region!=region],"cell")
            results["leave_one_region_out"].append({"omitted_region":region,
                "beta_salinity":fitted["beta_salinity"],"n":fitted["n"]})
        except ValueError as e:
            results["leave_one_region_out"].append({"omitted_region":region,"error":str(e)})
    results["n_region_specific_supported"]=sum("beta_salinity" in x for x in outregions)
    a.out.mkdir(parents=True,exist_ok=True)
    d.to_csv(a.out/"matched_860_original_isotope_ocean_ice_site_seasons.csv",index=False)
    pd.DataFrame(outregions).to_csv(a.out/"region_specific_exploratory_coefficients.csv",index=False)
    (a.out/"original_source_salinity_isotope_verdict.json").write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(results,indent=2,ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for k in ["isotope","isotope_days","glorys","nsidc"]:
        ap.add_argument("--"+k.replace("_","-"),required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    main(a)
