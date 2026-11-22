#!/usr/bin/env python3
"""Historical-absolute-state source comparability for future CMIP6 SOS and SIC.

Compare identical colony site IDs and Aug–Nov 1995–2014 calendar span:
historical CMIP6 source model baseline vs GLORYS ocean surface salinity
and OSI SAF 100 km site buffered sea ice. Source-space differences are not
independent causal attribution or validation of the future physical trend.
"""
from __future__ import annotations
import argparse,io,hashlib,json,zipfile
from pathlib import Path
import pandas as pd,numpy as np
CMIP_HASH="c91e3a1126bdb9af2345fe08bcb201b3c21e802cbd2fcfe21db99faa2163c4d0"
MARINE_HASH="30c311ef8312e8424919bec0230c72eec7ab0a9db40997275fccfde0fa7e95c8"
COUNTS_HASH="add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a"
PREFIX="source_root/outputs/cmip6_projection_v1/"
CMIP={"ACCESS-CM2","BCC-CSM2-MR","CESM2"}

def zipped(path,pinned):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pinned:raise ValueError("Original archived source SHA256 mismatch "+str(path))
    z=zipfile.ZipFile(io.BytesIO(raw))
    if z.testzip() is not None:raise ValueError("Original archived source ZIP corrupt")
    return z

def frame(z,key):
    return pd.read_csv(io.BytesIO(z.read(key)),low_memory=False)

def run(cmip,marine,counts,out):
    with zipped(cmip,CMIP_HASH) as z:
        source=frame(z,PREFIX+"site_model_changes.csv")
        support=frame(z,PREFIX+"coastal_grid_support.csv")
    with zipped(marine,MARINE_HASH) as z:
        observed=frame(z,"all_original_18region_1993_2020_real_joint_marine_3var_site_year.csv")
    with zipped(counts,COUNTS_HASH) as z:
        census=frame(z,"source_observed_2456.csv")
    if (len(source),len(support),len(observed),len(census))!=(21420,5355,16464,2456):
        raise ValueError("Original 3-source frozen row scope changed")
    if (observed.site_id.nunique(),observed.source_region.nunique(),observed.year.nunique())!=(588,18,28):
        raise ValueError("Original GLORYS/OSI-SAF marine source denominators changed")
    if not set(source.source_id)==CMIP or source.site_id.nunique()!=595:
        raise ValueError("Original three selected CMIP6 physical model identity drift")
    if source.duplicated(["site_id","source_id","variable_id","experiment_id","period"]).any():
        raise ValueError("Original model site variable future results duplicated")
    means=source.groupby(["site_id","source_id","variable_id"]).baseline_1995_2014.agg(["mean","min","max"]).reset_index()
    if len(means)!=595*3*3 or np.max(abs(means["max"]-means["min"]))>1e-12:
        raise ValueError("Original historical baseline differs across SSPs or future periods")
    hist=means.pivot(index=["site_id","source_id"],columns="variable_id",values="mean").reset_index()
    actual=observed.loc[observed.year.between(1995,2014)]
    if len(actual)!=588*20 or not actual.groupby("site_id").year.nunique().eq(20).all():
        raise ValueError("Original 1995–2014 GLORYS/SIC source years not complete")
    actual=actual.groupby("site_id",as_index=False).agg(
        observed_aug_nov_sic_pp=("SIC_pp","mean"),
        observed_aug_nov_glorys_surface_salinity=("GLORYS_salinity","mean"),
        observed_reanalysis_wet_grid_x=("source_original_wet_grid_x","first"),
        observed_reanalysis_wet_grid_y=("source_original_wet_grid_y","first"),
        original_source_region=("source_region","first"))
    cross=hist.merge(actual,on="site_id",how="inner",validate="many_to_one")
    if (len(cross),cross.site_id.nunique(),cross.original_source_region.nunique())!=(588*3,588,18):
        raise ValueError("Not all 588 real marine sites cross into all three original model historical baselines")
    ocean=support[support.variable_id.isin(["sos","siconc"])]
    dist=ocean.groupby("site_id").agg(n_model_sea_cells=("grid_cell_id","size"),
        max_model_sea_cell_distance_km=("distance_km","max"))
    cross=cross.join(dist,on="site_id",validate="many_to_one")
    cross["all_models_original_ocean50"]=(cross.n_model_sea_cells==6)&(cross.max_model_sea_cell_distance_km<=50)
    if cross.loc[cross.all_models_original_ocean50,"site_id"].nunique()!=367:
        raise ValueError("Source original marine 50km QA denominator drift")
    counted=set(census.loc[census.season.between(2011,2020),"site_id"])
    if len(counted)!=271:
        raise ValueError("Original recent count site support changed")
    cross["source_has_2011_2020_observed_nests"]=cross.site_id.isin(counted)
    if cross.loc[cross.source_has_2011_2020_observed_nests,"site_id"].nunique()!=265:
        raise ValueError("Original 271 census sites matched only 265 GLORYS source sites")
    cross["model_sos_minus_reanalysis_salinity"]=(cross.sos-cross.observed_aug_nov_glorys_surface_salinity)
    cross["model_siconc_minus_satellite_sic_pp"]=(cross.siconc-cross.observed_aug_nov_sic_pp)
    summaries=[];regional=[]
    for mod,d in cross.groupby("source_id"):
        for label,part in [
            ("all_588_site_equal",d),
            ("observed_census_265_site_equal",d.loc[d.source_has_2011_2020_observed_nests]),
            ("original_367_model_wetgrid50",d.loc[d.all_models_original_ocean50])]:
            if len(part)!={"all_588_site_equal":588,"observed_census_265_site_equal":265,
                            "original_367_model_wetgrid50":367}[label]:
                raise ValueError("Source historical calibration cohort unexpectedly changed")
            summaries.append({
                "model":mod,"source_cohort":label,"n_source_colonies":len(part),
                "n_original_GLORYS_wet_cells":int(part[["observed_reanalysis_wet_grid_y","observed_reanalysis_wet_grid_x"]].drop_duplicates().shape[0]),
                "mean_source_sos_minus_GLORYS":float(part.model_sos_minus_reanalysis_salinity.mean()),
                "rmse_source_sos_vs_GLORYS":float(np.sqrt(np.mean(part.model_sos_minus_reanalysis_salinity**2))),
                "source_site_correlation_sos_GLORYS":float(part.sos.corr(part.observed_aug_nov_glorys_surface_salinity)),
                "mean_source_sic_minus_OSISAF_pp":float(part.model_siconc_minus_satellite_sic_pp.mean()),
                "rmse_source_sic_vs_OSISAF_pp":float(np.sqrt(np.mean(part.model_siconc_minus_satellite_sic_pp**2))),
                "source_site_correlation_sic_OSISAF":float(part.siconc.corr(part.observed_aug_nov_sic_pp)),
                "not_in_situ_validation":True,
            })
        for region,part in d.groupby("original_source_region"):
            regional.append({
                "model":mod,"source_region":region,"source_sites":len(part),
                "source_original_GLORYS_wet_cells":int(part[["observed_reanalysis_wet_grid_y","observed_reanalysis_wet_grid_x"]].drop_duplicates().shape[0]),
                "mean_model_minus_GLORYS_sos":float(part.model_sos_minus_reanalysis_salinity.mean()),
                "mean_model_minus_sic_OSISAF_pp":float(part.model_siconc_minus_satellite_sic_pp.mean()),
            })
    result=pd.DataFrame(summaries)
    reg=pd.DataFrame(regional)
    all_=result.query("source_cohort=='all_588_site_equal'").set_index("model")
    if not (
        np.isclose(all_.loc["ACCESS-CM2","mean_source_sos_minus_GLORYS"],+.0756,atol=5e-4)
        and np.isclose(all_.loc["BCC-CSM2-MR","mean_source_sos_minus_GLORYS"],-.0590,atol=5e-4)
        and np.isclose(all_.loc["CESM2","mean_source_sos_minus_GLORYS"],-.4403,atol=5e-4)
        and np.isclose(all_.loc["ACCESS-CM2","rmse_source_sos_vs_GLORYS"],.2570,atol=5e-4)
        and np.isclose(all_.loc["BCC-CSM2-MR","rmse_source_sos_vs_GLORYS"],.1983,atol=5e-4)
        and np.isclose(all_.loc["CESM2","rmse_source_sos_vs_GLORYS"],.5074,atol=5e-4)):
        raise ValueError("Source historical model-GLORYS comparison changed unexpectedly")
    if len(result)!=9 or len(reg)!=54:
        raise ValueError("Unexpected 3 model×3 source support and 3 model×18 region diagnostics")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    cross.to_csv(out/"source_588_sites_CMIP6_historical_sos_sic_vs_GLORYS_OSISAF.csv",index=False)
    result.to_csv(out/"source_3model_historical_1995_2014_sos_sic_comparability.csv",index=False)
    reg.to_csv(out/"source_18region_3model_historical_physical_comparability.csv",index=False)
    verdict={
        "status":"PASS_REAL_SOURCE_HISTORICAL_GLORYS_VS_CMIP6_COMPARABILITY_ONLY",
        "source_original_595_model_known_colony_sites":595,
        "source_original_588_GLORYS_sites":588,
        "source_original_378_unique_GLORYS_wet_cells":378,
        "source_coincident_20years_1995_2014":20,
        "source_original_sic_data":"OSI SAF source 100km nearshore buffer, Aug–Nov 4-month",
        "source_GLORYS_data":"GLORYS12V1 reanalysis source nearest wet cell ≤25km, Aug–Nov",
        "CMIP6_source_data":"three selected model native coarse sea grid cell / original historical model, Aug–Nov",
        "GLORYS_is_reanalysis_not_in_situ_ground_truth":True,
        "different_model_grid_vs_original_observed_grid_and_month_weights":True,
        "source_counted_recent_sites_with_reference":265,
        "source_wetgrid_quality_sites_with_reference":367,
        "source_models":list(sorted(CMIP)),
        "historical_mean_bias_is_not_future_delta_skill":True,
        "future_sos_from_model_not_calibrated_GLORYS_or_optical_isotope":True,
        "no_biology_response_or_causal_future_prediction":True,
    }
    (out/"source_CMIP6_GLORYS_historical_comparability_verdict.json").write_text(
        json.dumps(verdict,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(verdict,indent=2,ensure_ascii=False))
    print(result.to_string(index=False))
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--cmip6-zip",required=True)
    p.add_argument("--glorys-zip",required=True)
    p.add_argument("--counts-zip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.cmip6_zip,a.glorys_zip,a.counts_zip,a.out)
