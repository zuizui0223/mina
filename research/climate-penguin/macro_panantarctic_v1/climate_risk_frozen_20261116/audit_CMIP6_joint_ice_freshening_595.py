#!/usr/bin/env python3
"""Three model×two SSP×two period joint sea-ice and surface-salinity exposure.

Published frozen CMIP6 595 Antarctic *known* colony source artifact, true
2011–2020 MAPPPD source counts (not assumed absent otherwise). The outcome
is model PHYSICAL change and sign-concordance. Absolutely no extrapolation
of experimental optical δ15N–salinity association into future isotope, prey
fractions, observed nests, survival or future occupancy.

Source models were selected by availability, not a probabilistic CMIP6 ensemble.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd

CMIP_SHA256="c91e3a1126bdb9af2345fe08bcb201b3c21e802cbd2fcfe21db99faa2163c4d0"
COUNTS_SHA256="add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a"
CMIP_DIR="source_root/outputs/cmip6_projection_v1/"
MODELS={"ACCESS-CM2","BCC-CSM2-MR","CESM2"}
VARS={"siconc","sos","tas"}
SCENARIOS={"ssp245","ssp585"}
PERIODS={"2041-2060","2081-2100"}
SOURCE_SEASON="August–November"
REFERENCE="CMIP6 historical 1995–2014 source-model seasonal reference (not observed GLORYS)"
TOL=1e-9

def pinned_zip(source,expected):
    p=Path(source)
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    if sha!=expected:
        raise ValueError(f"Frozen workflow artifact digest mismatch {p.name} actual {sha}, expected {expected}")
    z=zipfile.ZipFile(p)
    if z.testzip() is not None:raise ValueError("Original source archive ZIP CRC failed")
    return z

def csv(z,name):
    return pd.read_csv(io.BytesIO(z.read(name)),low_memory=False)

def originals(cmip_zip,counts_zip):
    with pinned_zip(cmip_zip,CMIP_SHA256) as z:
        d=csv(z,CMIP_DIR+"site_model_changes.csv")
        e=csv(z,CMIP_DIR+"site_model_ensemble.csv")
        support=csv(z,CMIP_DIR+"coastal_grid_support.csv")
        receipt=json.loads(z.read(CMIP_DIR+"manifest.json"))
    with pinned_zip(counts_zip,COUNTS_SHA256) as z:
        c=csv(z,"source_observed_2456.csv")
        a=csv(z,"panantarctic_595_site_inventory.csv")
    if receipt["status"]!="complete" or receipt["n_stores_read"]!=27 or receipt["failures"]:
        raise ValueError("Missing exact original 27-store CMIP6 source")
    if (len(d),len(e),len(support),len(c),len(a))!=(21420,7140,5355,2456,595):
        raise ValueError("Original source denominator changed")
    if (d.site_id.nunique(),e.site_id.nunique(),c.site_id.nunique(),a.site_id.nunique())!=(595,595,595,595):
        raise ValueError("Original colony identity set changed")
    if not (set(d.source_id)==MODELS and set(d.variable_id)==VARS
        and set(d.experiment_id)==SCENARIOS and set(d.period)==PERIODS):
        raise ValueError("Original physical model/variable/scenario scope changed")
    if not d.complete_years.eq(20).all() or not e.n_models.eq(3).all():
        raise ValueError("Incomplete source 20-year CMIP6 model periods")
    if d.duplicated(["source_id","site_id","variable_id","experiment_id","period"]).any():
        raise ValueError("Duplicated source site-model variable")
    if e.duplicated(["site_id","variable_id","experiment_id","period"]).any():
        raise ValueError("Duplicated source ensemble site variable")
    if not (
       set(d[d.variable_id=="siconc"].change_units)=={"percentage_points"} and
       set(d[d.variable_id=="sos"].change_units)=={"0.001"} and
       set(d[d.variable_id=="tas"].change_units)=={"degC"}):
        raise ValueError("Original source native model units changed")
    if d["change"].isna().any() or e["change_mean"].isna().any():
        raise ValueError("Original model physical scenario has missing values")
    obs=c[c.season.between(2011,2020)].groupby(["site_id","species"],as_index=False).agg(
        source_species_median_nests=("observed_nest_count","median"),
        observed_years=("season","nunique"))
    if len(obs)!=331 or obs.site_id.nunique()!=271 or set(obs.species)!={"ADPE","CHPE","GEPE"}:
        raise ValueError("Original observed 2011–2020 source census cohort changed")
    if not obs.source_species_median_nests.ge(0).all():
        raise ValueError("Original source observed actual nesting negative")
    weight=obs.groupby("site_id",as_index=False).source_species_median_nests.sum()
    weight=weight.rename(columns={"source_species_median_nests":"nest_proxy"})
    weight=weight.merge(a[["site_id","source_region","polar_250km_fixed_grid_block"]],
                        on="site_id",validate="one_to_one")
    if not np.isclose(weight.nest_proxy.sum(),2848329.5) or weight.source_region.nunique()!=16:
        raise ValueError("Original observed nest-median weight denominator drift")
    sal= support.loc[support.variable_id.isin(["sos","siconc"])]
    marine=sal.groupby("site_id",as_index=False).agg(
        original_model_ocean_max_cell_dist_km=("distance_km","max"),
        n_original_model_ocean_cells=("grid_cell_id","size"))
    strict=set(marine.loc[(marine.original_model_ocean_max_cell_dist_km<=50)&
                          (marine.n_original_model_ocean_cells==6)].site_id)
    if len(strict)!=372:
        raise ValueError("Original all-model ocean <=50km marine grid gate changed")
    strictw=weight.loc[weight.site_id.isin(strict)]
    if len(strictw)!=158 or not np.isclose(strictw.nest_proxy.sum()/weight.nest_proxy.sum(),.8020989144689896,atol=1e-9):
        raise ValueError("Original 158 count-site 50km support gate changed")
    # Independently source-check ensemble site means before any climate novelty inference.
    mean=d.groupby(["site_id","variable_id","experiment_id","period"]).change.mean().rename("check").reset_index()
    tmp=e.merge(mean,on=["site_id","variable_id","experiment_id","period"],validate="one_to_one")
    if len(tmp)!=7140 or np.max(abs(tmp.change_mean-tmp.check))>TOL:
        raise ValueError("Original physical ensemble mean failed independent 21k-row rebuild")
    return d,e,support,c,a,obs,weight,marine,strict,receipt

def weighted_avg(values,weights):
    return float(np.average(np.asarray(values,dtype=float),weights=np.asarray(weights,dtype=float)))

def summarize_scenario(d,e,weight,strict,ssp,period):
    target=d.loc[d.experiment_id.eq(ssp)&d.period.eq(period)]
    raw=target.pivot(index=["site_id","source_id"],columns="variable_id",values="change").reset_index()
    if len(raw)!=1785 or not all(raw.groupby("site_id").source_id.nunique()==3):
        raise ValueError("Not exactly 595 sites×3 models in scenario")
    raw["joint_both_negative"]=(raw.siconc<0)&(raw.sos<0)
    sign=raw.groupby("site_id").agg(
        all_three_sos_freshen=("sos",lambda x:bool((x<0).all())),
        all_three_siconc_decline=("siconc",lambda x:bool((x<0).all())),
        all_three_joint=("joint_both_negative","all"),
        any_one_sos_increase=("sos",lambda x:bool((x>0).any())),
    )
    signed=raw.pivot(index="site_id",columns="source_id",values="sos")
    sign["n_models_sos_freshen"]=(signed<0).sum(axis=1).astype(int)
    site=e.loc[e.experiment_id.eq(ssp)&e.period.eq(period)].pivot(
        index="site_id",columns="variable_id",values="change_mean")
    if len(site)!=595 or site.isna().any().any():
        raise ValueError("Model mean for all original 595 sites missing")
    site=site.join(sign,validate="one_to_one")
    site=site.join(weight.set_index("site_id")[["nest_proxy","source_region",
                                                "polar_250km_fixed_grid_block"]],how="left")
    site["count_source_2011_2020"]=site.nest_proxy.notna()
    site["all_models_marine_wet_cell_50km"]=site.index.isin(strict)
    site["modelmean_sos_decrease"]=site.sos<0
    site["modelmean_siconc_decrease"]=site.siconc<0
    site["modelmean_joint_decrease"]=site.modelmean_sos_decrease&site.modelmean_siconc_decrease
    summary=[]
    for name,part in [
        ("595_known_colonies_equal_site",site),
        ("271_source_counted_colonies_equal_site",site.loc[site.count_source_2011_2020]),
        ("271_source_counted_colonies_nest_proxy_weight",site.loc[site.count_source_2011_2020]),
        ("158_source_counted_wet50_nest_proxy_weight",site.loc[site.count_source_2011_2020&
                                                               site.all_models_marine_wet_cell_50km])]:
        isweight="nest_proxy_weight" in name
        w=part.nest_proxy.to_numpy(dtype=float) if isweight else np.ones(len(part))
        if not len(part):raise ValueError("Empty original site denominator")
        summary.append({
            "scenario":ssp,"period":period,"weight_cohort":name,
            "n_source_site_ids":len(part),
            "n_source_250km_blocks":int(part.polar_250km_fixed_grid_block.nunique()) if name!="595_known_colonies_equal_site" else None,
            "n_source_reporting_regions":int(part.source_region.nunique()) if name!="595_known_colonies_equal_site" else 18,
            "original_fixed_nest_proxy_weight_sum":float(part.nest_proxy.sum()) if isweight else None,
            "mean_delta_sic_pp":weighted_avg(part.siconc,w),
            "mean_delta_sos_native_0p001":weighted_avg(part.sos,w),
            "mean_delta_air_temperature_degC":weighted_avg(part.tas,w),
            "three_modelmean_sos_freshen_weight_fraction":weighted_avg(part.modelmean_sos_decrease,w),
            "three_modelmean_sic_decline_weight_fraction":weighted_avg(part.modelmean_siconc_decrease,w),
            "three_modelmean_both_weight_fraction":weighted_avg(part.modelmean_joint_decrease,w),
            "all_three_sos_freshen_weight_fraction":weighted_avg(part.all_three_sos_freshen,w),
            "all_three_sic_decline_weight_fraction":weighted_avg(part.all_three_siconc_decline,w),
            "all_three_joint_ice_loss_and_freshening_weight_fraction":weighted_avg(part.all_three_joint,w),
            "n_site_all_three_sos_freshen":int(part.all_three_sos_freshen.sum()),
            "n_site_all_three_joint":int(part.all_three_joint.sum()),
            "n_source_models":3,
            "model_member_range_not_probability":True
        })
    # Model weights from actual site changes, not model mean masks.
    models=[]
    for model,part in raw.groupby("source_id"):
        w=part.set_index("site_id").join(weight.set_index("site_id")[["nest_proxy"]])
        w=w.loc[w.nest_proxy.notna()]
        if len(w)!=271:raise ValueError("True 271 count support lost under source model")
        models.append({
            "scenario":ssp,"period":period,"source_model":model,
            "count_sites":len(w),
            "source_nest_proxy_weight_sum":float(w.nest_proxy.sum()),
            "siconc_change_nest_weight_pp":weighted_avg(w.siconc,w.nest_proxy),
            "sos_change_nest_weight_native_0p001":weighted_avg(w.sos,w.nest_proxy),
            "tas_change_nest_weight_degC":weighted_avg(w.tas,w.nest_proxy),
            "n_source_sites_sos_freshen":int((w.sos<0).sum()),
            "source_nest_fraction_sos_freshen":weighted_avg(w.sos<0,w.nest_proxy),
            "source_nest_fraction_sic_declines":weighted_avg(w.siconc<0,w.nest_proxy),
            "source_nest_fraction_both":weighted_avg(w.joint_both_negative,w.nest_proxy),
        })
    return site,summary,models

def run(args):
    d,e,support,c,atlas,obs,weight,marine,strict,manifest=originals(args.cmip6_zip,args.counts_zip)
    scenarios=[];model_rows=[];regional=[];species=[];cohort=[]
    for ssp in sorted(SCENARIOS):
        for period in sorted(PERIODS):
            site,sums,models=summarize_scenario(d,e,weight,strict,ssp,period)
            scenarios.extend(sums)
            model_rows.extend(models)
            # Derived source exactly one row per site, scenario, period, not replicate sites.
            cols=["siconc","sos","tas","all_three_sos_freshen","all_three_siconc_decline",
                  "all_three_joint","n_models_sos_freshen","modelmean_sos_decrease",
                  "modelmean_siconc_decrease","modelmean_joint_decrease",
                  "count_source_2011_2020","nest_proxy","source_region",
                  "polar_250km_fixed_grid_block","all_models_marine_wet_cell_50km"]
            v=site[cols].reset_index().rename(columns={"siconc":"CMIP6_delta_sic_pp",
                "sos":"CMIP6_delta_sos_native_0p001","tas":"CMIP6_delta_tas_degC"})
            v["scenario"]=ssp;v["period"]=period
            cohort.append(v)
            counted=site.loc[site.count_source_2011_2020]
            for region,group in counted.groupby("source_region"):
                wt=group.nest_proxy.to_numpy()
                regional.append({"scenario":ssp,"period":period,"region":region,
                    "n_source_counted_colonies":len(group),
                    "nest_proxy_fraction_all_counted":float(wt.sum()/weight.nest_proxy.sum()),
                    "n_source_250km_blocks":int(group.polar_250km_fixed_grid_block.nunique()),
                    "nestweighted_sic_delta_pp":weighted_avg(group.siconc,wt),
                    "nestweighted_sos_delta_native_0p001":weighted_avg(group.sos,wt),
                    "n_site_all_models_sos_freshen":int(group.all_three_sos_freshen.sum()),
                    "n_site_all_models_joint":int(group.all_three_joint.sum()),
                    "nest_fraction_all_models_sos_freshen":weighted_avg(group.all_three_sos_freshen,wt),
                    "nest_fraction_all_models_joint":weighted_avg(group.all_three_joint,wt)})
            sp=obs.merge(site[["siconc","sos","tas","all_three_sos_freshen",
                               "all_three_siconc_decline","all_three_joint"]],
                          left_on="site_id",right_index=True,validate="many_to_one")
            for species_name,group in sp.groupby("species"):
                wt=group.source_species_median_nests
                species.append({"scenario":ssp,"period":period,"species":species_name,
                    "n_source_colonies":len(group),"observed_species_site_median_weight":float(wt.sum()),
                    "nestweighted_sic_delta_pp":weighted_avg(group.siconc,wt),
                    "nestweighted_sos_delta_native_0p001":weighted_avg(group.sos,wt),
                    "nest_fraction_all_models_sos_freshen":weighted_avg(group.all_three_sos_freshen,wt),
                    "nest_fraction_all_models_joint":weighted_avg(group.all_three_joint,wt),
                    "not_species_specific_climate_niche_or_fate":True})
    s=pd.DataFrame(scenarios)
    md=pd.DataFrame(model_rows)
    region=pd.DataFrame(regional)
    sp=pd.DataFrame(species)
    source_cohort=pd.concat(cohort,ignore_index=True)
    primary=s[(s.scenario=="ssp585")&(s.period=="2081-2100")]
    focus=primary.set_index("weight_cohort")
    counted=focus.loc["271_source_counted_colonies_nest_proxy_weight"]
    sites=focus.loc["595_known_colonies_equal_site"]
    if not (np.isclose(float(counted.mean_delta_sic_pp),-13.276240917274329,atol=1e-8)
        and np.isclose(float(counted.mean_delta_sos_native_0p001),-0.2572497134152925,atol=1e-8)
        and np.isclose(float(sites.mean_delta_sic_pp),-21.442,atol=1e-3)
        and int(sites.n_site_all_three_sos_freshen)==464
        and int(sites.n_site_all_three_joint)==384
        and int(counted.n_site_all_three_sos_freshen)==179
        and int(counted.n_site_all_three_joint)==152
        and np.isclose(float(counted.all_three_sos_freshen_weight_fraction),.9348,atol=.001)
        and np.isclose(float(counted.all_three_joint_ice_loss_and_freshening_weight_fraction),.591,atol=.002)):
        raise ValueError("Source independently recomputed primary physical results drift")
    if len(s)!=16 or len(md)!=12 or len(region)!=64 or len(sp)!=12 or len(source_cohort)!=2380:
        raise ValueError("Source scenarios, model or geography output denominators drift")
    report={
        "status":"PASS_REAL_595_CMIP6_THREE_MODEL_ICE_AND_SALINITY_JOINT_PHYSICAL_EXPOSURE",
        "source_original_27_zarr_stores":27,
        "source_M595_model_grid":595,
        "source_original_actual_nest_count_records":2456,
        "source_censused_2011_2020_site_medians":271,
        "original_nest_proxy_medians_site_species":331,
        "original_nest_proxy_weight_total":2848329.5,
        "source_frozen_cmip6_zip_sha256":CMIP_SHA256,
        "source_frozen_counts_zip_sha256":COUNTS_SHA256,
        "source_models":["ACCESS-CM2","BCC-CSM2-MR","CESM2"],
        "original_months":[8,9,10,11],
        "historical_baseline":"1995-2014",
        "future_source_4_scenarios":sorted({f"{x}-{y}" for x,y in zip(s.scenario,s.period)}),
        "physical_SSS_sos_vs_observed_GLORYS_salinity":"DIFFERENT PRODUCTS and model nearshore grid supports",
        "tas_is_near_surface_AIR_temperature_not_GLORYS_sea_temperature":True,
        "do_not_reconstruct_original_3var_PCA_in_future_using_tas":True,
        "three_models_selected_by_available_source_not_probabilistic":True,
        "same_ocean_grid_cell_many_colonies_not_independent":True,
        "no_direct_fish_krill_or_d15N_future_prediction":True,
        "no_future_population_or_breeding_forecast":True,
        "primary_ssp585_2081_2100":{
            "595_sites_3_model_mean_sos_negative":int((source_cohort.query("scenario=='ssp585' and period=='2081-2100'")
                                                       .CMIP6_delta_sos_native_0p001<0).sum()),
            "595_sites_all3_sos_decrease":int(sites.n_site_all_three_sos_freshen),
            "595_sites_all3_joint_ice_and_sos_decrease":int(sites.n_site_all_three_joint),
            "271_actual_census_sites_all3_sos_decrease":int(counted.n_site_all_three_sos_freshen),
            "271_actual_census_sites_all3_joint_decrease":int(counted.n_site_all_three_joint),
            "nest_proxy_fraction_all3_sos_decrease":float(counted.all_three_sos_freshen_weight_fraction),
            "nest_proxy_fraction_all3_joint_decrease":float(counted.all_three_joint_ice_loss_and_freshening_weight_fraction),
        }
    }
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    s.to_csv(out/"original_595_CMIP6_4scenario_joint_ice_sos_main_summary.csv",index=False)
    md.to_csv(out/"original_271_CMIP6_3model_freshening_disagreement.csv",index=False)
    region.to_csv(out/"original_271_CMIP6_joint_exposure_16region.csv",index=False)
    sp.to_csv(out/"original_331_species_median_3model_ice_sos_exposure.csv",index=False)
    source_cohort.to_csv(out/"original_595_four_scenario_site_source_model_sign_concordance.csv",index=False)
    (out/"original_joint_ice_sos_source_audit_verdict.json").write_text(
         json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--cmip6-zip",required=True)
    p.add_argument("--counts-zip",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    run(args)
