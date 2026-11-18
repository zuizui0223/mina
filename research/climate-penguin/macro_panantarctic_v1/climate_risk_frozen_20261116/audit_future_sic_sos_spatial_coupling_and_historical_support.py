#!/usr/bin/env python3
"""Original-source Antarctic CMIP6 SIC/SOS spatial coupling vs historical local reliability.

No biological forecasts. Every correlation is among known source-site
physical scenario differences, not climate responses of observed penguins.
We report three geographic grains: all site IDs, within-reporting-region site
contrast and one source model native SOS cell per region (to limit repeated
nearshore colony climate pixels). All chosen before inspecting associations.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd

SOURCE_CMIP_SHA="c91e3a1126bdb9af2345fe08bcb201b3c21e802cbd2fcfe21db99faa2163c4d0"
SOURCE_COUNTS_SHA="add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a"
SOURCE_HIST_SHA="fad723674b15b09b6423e2052f31300cbd28ac6b79f609c91bf1ab3128e76aeb"
CMIP_PREFIX="source_root/outputs/cmip6_projection_v1/"
MODELS={"ACCESS-CM2","BCC-CSM2-MR","CESM2"}
PERIODS={"2041-2060","2081-2100"}
SSPS={"ssp245","ssp585"}
VARIABLES={"sos","siconc","tas"}
PAIR_COLS=["source_id","site_id","experiment_id","period"]

def read_archive(path,sha):
    raw=Path(path).read_bytes()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=sha:
        raise ValueError(f"Original pinned source ZIP digest differs: {actual}")
    z=zipfile.ZipFile(io.BytesIO(raw))
    if z.testzip() is not None:raise ValueError("Original GitHub source ZIP failed CRC")
    return z

def readcsv(arc,path):
    return pd.read_csv(io.BytesIO(arc.read(path)),low_memory=False)

def region_demean_corr(data,x,y,region):
    d=data[[x,y,region]].copy()
    for variable in [x,y]:
        d[variable]=d[variable]-d.groupby(region)[variable].transform("mean")
    if d[x].std()<1e-12 or d[y].std()<1e-12:
        raise ValueError("Insufficient within-region original physical source variance")
    return float(d[x].corr(d[y]))

def site_and_cell_future(g):
    # Only original model SOS cells are used as the physical grain for its
    # salt/ice response pair, not colony site IDs assigned the same grid point.
    g=g.reset_index(drop=True)
    independent=g.groupby(["source_region","original_model_sos_grid_cell"],as_index=False).agg(
        siconc=("siconc","mean"),sos=("sos","mean"),n_source_colonies=("site_id","nunique"))
    if not independent.n_source_colonies.ge(1).all():
        raise ValueError("Unexpected original cell/region site denominator")
    raw_site=float(g.siconc.corr(g.sos))
    within_site=region_demean_corr(g,"siconc","sos","source_region")
    raw_cell=float(independent.siconc.corr(independent.sos))
    within_cell=region_demean_corr(independent,"siconc","sos","source_region")
    deleted=[]
    for region in sorted(g.source_region.unique()):
        keep=g[g.source_region!=region]
        deleted.append(region_demean_corr(keep,"siconc","sos","source_region"))
    if len(deleted)!=18:raise ValueError("18 original source regions required")
    return {
        "n_original_site_ids":len(g),
        "n_model_sos_grid_cells":int(g.original_model_sos_grid_cell.nunique()),
        "n_model_sos_cell_region_grains":len(independent),
        "n_source_regions":int(g.source_region.nunique()),
        "site_equal_raw_corr_delta_sic_delta_sos":raw_site,
        "site_equal_within_region_corr_delta_sic_delta_sos":within_site,
        "model_cell_region_equal_raw_corr_delta_sic_delta_sos":raw_cell,
        "model_cell_region_equal_within_region_corr_delta_sic_delta_sos":within_cell,
        "site_equal_within_region_leave_one_region_min":float(min(deleted)),
        "site_equal_within_region_leave_one_region_max":float(max(deleted)),
        "n_18_omit_region_same_corr_sign":int(sum(np.sign(t)==np.sign(within_site) for t in deleted)),
        "n_original_site_model_cell_pseudo_replicates":int(len(g)-g.original_model_sos_grid_cell.nunique()),
    }

def historical_cohort(h):
    rows=[]
    for model,g in sorted(h.groupby("source_id")):
        g=g.copy()
        g["wet_cell"]=(g.observed_reanalysis_wet_grid_y.astype(str)
                       +":"+g.observed_reanalysis_wet_grid_x.astype(str))
        if (len(g),g.wet_cell.nunique(),g.original_source_region.nunique())!=(588,378,18):
            raise ValueError("Original GLORYS historical support changed")
        wet=g.groupby(["original_source_region","wet_cell"],as_index=False).agg(
            sos=("sos","mean"),
            observed_sos=("observed_aug_nov_glorys_surface_salinity","mean"),
            siconc=("siconc","mean"), observed_ice=("observed_aug_nov_sic_pp","mean"),
            n_sites=("site_id","nunique"))
        if len(wet)!=378:
            raise ValueError("Real GLORYS source wet cells shared across reporting regions")
        metrics={"source_model":model,"n_source_sites":len(g),
            "n_source_reanalysis_wet_cells":len(wet),
            "n_source_regions":18}
        for name,sim,obs in [
            ("sos","sos","observed_aug_nov_glorys_surface_salinity"),
            ("sic","siconc","observed_aug_nov_sic_pp")]:
            obs_cell=("observed_sos" if name=="sos" else "observed_ice")
            metrics[f"r_site_raw_{name}"]=float(g[sim].corr(g[obs]))
            metrics[f"r_site_region_centered_{name}"]=region_demean_corr(
                g,sim,obs,"original_source_region")
            metrics[f"r_original_wetcell_region_centered_{name}"]=region_demean_corr(
                wet,sim,obs_cell,"original_source_region")
            metrics[f"model_minus_observed_site_mean_{name}"]=float((g[sim]-g[obs]).mean())
            metrics[f"site_rmse_{name}"]=float(np.sqrt(np.mean((g[sim]-g[obs])**2)))
        metrics["site_region_centered_SIC_advantage_in_r"]=(
            metrics["r_site_region_centered_sic"]-metrics["r_site_region_centered_sos"])
        metrics["wetcell_region_centered_SIC_advantage_in_r"]=(
            metrics["r_original_wetcell_region_centered_sic"]-
            metrics["r_original_wetcell_region_centered_sos"])
        # The observed pattern is source-average geography, not year-specific CMIP6
        # correspondence or an independent ability to predict future salinity changes.
        metrics["not_temporal_prediction_skill"]=True
        rows.append(metrics)
    return pd.DataFrame(rows)

def run(cmip,counts,historical,out):
    with read_archive(cmip,SOURCE_CMIP_SHA) as z:
        c=readcsv(z,CMIP_PREFIX+"site_model_changes.csv")
        meta=json.loads(z.read(CMIP_PREFIX+"manifest.json"))
    with read_archive(counts,SOURCE_COUNTS_SHA) as z:
        atlas=readcsv(z,"panantarctic_595_site_inventory.csv")
    with read_archive(historical,SOURCE_HIST_SHA) as z:
        past=readcsv(z,"source_588_sites_CMIP6_historical_sos_sic_vs_GLORYS_OSISAF.csv")
    if meta.get("n_stores_read")!=27 or meta.get("status")!="complete":
        raise ValueError("Original CMIP6 27-store model source incomplete")
    if len(c)!=21420 or c.site_id.nunique()!=595 or atlas.site_id.nunique()!=595:
        raise ValueError("Source original 595×3 model×3 variable×4 scenario rows changed")
    if set(c.source_id)!=MODELS or set(c.variable_id)!=VARIABLES:
        raise ValueError("Original 3 model and 3 source variables differ")
    if set(c.experiment_id)!=SSPS or set(c.period)!=PERIODS:
        raise ValueError("Original future source scenarios changed")
    if (len(past),past.site_id.nunique(),past.source_id.nunique())!=(1764,588,3):
        raise ValueError("Same-source historical 1995–2014 GLORYS comparison archive changed")
    if c.duplicated(PAIR_COLS+["variable_id"]).any():
        raise ValueError("Duplicate raw original CMIP6 model site")
    if c.complete_years.ne(20).any():
        raise ValueError("Original future model completeness changed")
    if c.change.isna().any():
        raise ValueError("Missing original physical CMIP6 change")
    if set(c.site_id)!=set(atlas.site_id):
        raise ValueError("MAPPPD original 595 source atlas codes changed")
    chosen=c.loc[c.variable_id.isin(["siconc","sos"])]
    pairs=chosen.pivot(index=PAIR_COLS,columns="variable_id",values="change").reset_index()
    sosmap=chosen.loc[chosen.variable_id=="sos",PAIR_COLS+["grid_cell_id"]].rename(
        columns={"grid_cell_id":"original_model_sos_grid_cell"})
    pairs=pairs.merge(sosmap,on=PAIR_COLS,validate="one_to_one")
    pairs=pairs.merge(atlas[["site_id","source_region"]],on="site_id",validate="many_to_one")
    if len(pairs)!=7140 or pairs[PAIR_COLS].duplicated().any():
        raise ValueError("Original paired model SIC/SOS rows not 7140")
    results=[]
    for (source,ssp,period),g in pairs.groupby(["source_id","experiment_id","period"],sort=True):
        if len(g)!=595 or g.site_id.nunique()!=595:
            raise ValueError("Incomplete original 595 model site geography")
        r=site_and_cell_future(g)
        results.append({"source_model":source,"scenario":ssp,"period":period,**r})
    future=pd.DataFrame(results)
    hist=historical_cohort(past)
    if (len(future),len(hist))!=(12,3):
        raise ValueError("Missing source 12 projection or 3 baseline consistency rows")
    full=future.query("scenario=='ssp585' and period=='2081-2100'").set_index("source_model")
    expected={"ACCESS-CM2":(.743,.709,.494,.404,103),
              "BCC-CSM2-MR":(-.296,-.332,-.207,-.178,87),
              "CESM2":(-.333,-.079,-.219,-.350,98)}
    for model,(a,b,c,d,n) in expected.items():
        x=full.loc[model]
        got=(x.site_equal_raw_corr_delta_sic_delta_sos,
             x.site_equal_within_region_corr_delta_sic_delta_sos,
             x.model_cell_region_equal_raw_corr_delta_sic_delta_sos,
             x.model_cell_region_equal_within_region_corr_delta_sic_delta_sos)
        if any(abs(u-v)>.001 for u,v in zip(got,(a,b,c,d))) or x.n_model_sos_grid_cells!=n:
            raise ValueError("Original late-century source-grid correlation changed: "+model)
        if x.n_18_omit_region_same_corr_sign!=18:
            raise ValueError("Physical coupling model sign sensitive to removing source regions")
    hist=hist.set_index("source_model").sort_index()
    expected_hist={"ACCESS-CM2":(.3839,.2036,.1776,.7166,.6758,.6733),
                   "BCC-CSM2-MR":(.6785,.2084,.1943,.8291,.3672,.3462),
                   "CESM2":(.5224,.2478,.2579,.7066,.6098,.5954)}
    for model, vals in expected_hist.items():
        h=hist.loc[model]
        got=(h.r_site_raw_sos,h.r_site_region_centered_sos,
             h.r_original_wetcell_region_centered_sos,
             h.r_site_raw_sic,h.r_site_region_centered_sic,
             h.r_original_wetcell_region_centered_sic)
        if any(abs(u-v)>.0002 for u,v in zip(got,vals)):
            raise ValueError("Historical original source site / GLORYS wet-cell geography drift "+model)
        if h.site_region_centered_SIC_advantage_in_r<=0:
            raise ValueError("Source pattern trend model claim SIC > SOS not reproduced")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    future.to_csv(out/"original_12_CMIP6_model_SIC_SOS_future_spatial_coupling.csv",index=False)
    hist.reset_index().to_csv(out/"original_3_CMIP6_model_historical_local_SOS_vs_SIC_support.csv",index=False)
    report={
        "status":"PASS_SOURCE_PINNED_CMIP6_SIC_SOS_FUTURE_COUPLING_AND_HISTORICAL_SPATIAL_SUPPORT",
        "source_full_595_site_ids":595,"source_original_18_reporting_regions":18,
        "source_CMIP6_future_model_scenario_rows":7140,
        "source_CMIP6_original_future_site_variable_records":21420,
        "source_CMIP6_original_stores":27,
        "source_historical_original_matched_sites":588,
        "source_historical_real_wet_ocean_cells":378,
        "source_selected_model_names":list(sorted(MODELS)),
        "all_12_scenario_model_spatial_support":True,
        "late_century_SSP585_3models_have_different_SIC_SOS_spatial_coupling_signs":True,
        "same_source_original_data_and_no_model_selection_by_fit":True,
        "regional_demeaning_is_not_true_local_foraging_exposure":True,
        "not_ensemble_probability_or_future_forecast_skill":True,
        "models_do_not_provide_population_or_d15N_predictions":True,
        "GLORYS_is_reanalysis_not_an_in_situ_independent_validation":True,
        "different_model_monthly_grid_and_observation_source_support":True,
        "original_source_archive_sha256":{
            "futureCMIP6":SOURCE_CMIP_SHA,
            "historical_comparability":SOURCE_HIST_SHA,
            "source_nests595":SOURCE_COUNTS_SHA
        },
    }
    (out/"source_CMIP6_future_coupling_and_historical_local_coverage_verdict.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print(future[["source_model","scenario","period",
                  "site_equal_within_region_corr_delta_sic_delta_sos",
                  "model_cell_region_equal_within_region_corr_delta_sic_delta_sos"]].to_string(index=False))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--cmip6-zip",required=True)
    p.add_argument("--source-counts-zip",required=True)
    p.add_argument("--historical-zip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.cmip6_zip,a.source_counts_zip,a.historical_zip,a.out)
