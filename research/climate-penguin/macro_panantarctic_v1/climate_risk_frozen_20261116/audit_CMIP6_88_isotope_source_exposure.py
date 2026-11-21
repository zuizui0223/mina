#!/usr/bin/env python3
"""Source overlap ONLY: previously published Adélie δ15N optical-proxy observation
sites versus 3-model CMIP6 projected SIC/sos/tas physical deltas.

No salinity-to-future-isotope coefficient transfer: isotope was observed in Nov-Feb
1996–2012 with nearshore GLORYS and 150km NSIDC SIC; CMIP6 is Aug-Nov at
coarse different model grid cells in 2041–2100, historical 1995–2014.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import pandas as pd,numpy as np

PHYS_SHA="4cf7c2324f029d9951b4fe22502f650205f8a8c711646f7645427e747fe0240a"
ISO_SHA="dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
SCENARIO=[("ssp245","2041-2060"),("ssp245","2081-2100"),("ssp585","2041-2060"),("ssp585","2081-2100")]

def content(source,sha,key):
    blob=Path(source).read_bytes()
    if hashlib.sha256(blob).hexdigest()!=sha:
        raise ValueError("Original completed-GitHub-Action derived archive SHA changed")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        if z.testzip() is not None:raise ValueError("Original archive corrupt")
        return pd.read_csv(z.open(key))

def run(physical,isotope,out):
    p=content(physical,PHYS_SHA,"original_595_four_scenario_site_source_model_sign_concordance.csv")
    i=content(isotope,ISO_SHA,"matched_860_original_isotope_ocean_ice_site_seasons.csv")
    if (len(p),p.site_id.nunique(),len(i),i.site_id.nunique())!=(2380,595,860,88):
        raise ValueError("Source denominator drift or upload was not original 595/860")
    if i.duplicated(["site_id","season"]).any():raise ValueError("Duplicate original isotope site season")
    if p.duplicated(["site_id","scenario","period"]).any():raise ValueError("CMIP6 source duplicate")
    d=i.groupby("site_id",as_index=False).agg(
        source_region=("source_region","first"),
        n_observed_isotope_site_seasons=("season","size"),
        first_observed_isotope_season=("season","min"),
        last_observed_isotope_season=("season","max"))
    if d.n_observed_isotope_site_seasons.sum()!=860 or d.source_region.nunique()!=13:
        raise ValueError("Original 88 source region support drift")
    merged=p.merge(d,on="site_id",how="inner",suffixes=("","_original_isotope"),validate="many_to_one")
    if len(merged)!=88*4 or merged.source_region_original_isotope.isna().any():
        raise ValueError("Source 88 original image locations not complete in future projection")
    cohort=[]
    by_region=[]
    for (ssp,period),q in merged.groupby(["scenario","period"],sort=True):
        for name,v in [("all_88_original_isotope_sites",q),
                       ("wet50_46_original_isotope_sites",q.loc[q.all_models_marine_wet_cell_50km])]:
            if len(v)!=(88 if name.startswith("all") else 46):
                raise ValueError("Original isotope site CMIP6 ocean source quality gate changed")
            cohort.append({
                "scenario":ssp,"period":period,"source_cohort":name,
                "n_isotope_source_sites":len(v),
                "n_isotope_source_regions":int(v.source_region_original_isotope.nunique()),
                "original_isotope_site_seasons_supported_in_these_sites":int(v.n_observed_isotope_site_seasons.sum()),
                "modelmean_SIC_loss_mean_pp":float(v.CMIP6_delta_sic_pp.mean()),
                "modelmean_sos_mean_0p001":float(v.CMIP6_delta_sos_native_0p001.mean()),
                "sites_modelmean_sos_negative":int(v.modelmean_sos_decrease.sum()),
                "sites_all3_models_sos_negative":int(v.all_three_sos_freshen.sum()),
                "sites_all3_models_both_sos_ice_negative":int(v.all_three_joint.sum()),
                "all_source_sites_historical_isotope_observations_exist":True,
                "future_isotope_proxy_or_prey_predicted":False})
        for region,g in q.groupby("source_region_original_isotope"):
            by_region.append({"scenario":ssp,"period":period,"isotope_source_region":region,
                "n_original_isotope_sites":len(g),
                "n_original_isotope_site_seasons":int(g.n_observed_isotope_site_seasons.sum()),
                "mean_model_sos_change_0p001":float(g.CMIP6_delta_sos_native_0p001.mean()),
                "model_agreed_sos_freshen_sites":int(g.all_three_sos_freshen.sum()),
                "model_agreed_joint_sites":int(g.all_three_joint.sum())})
    main=pd.DataFrame(cohort)
    regions=pd.DataFrame(by_region)
    primary=main.query("scenario=='ssp585' and period=='2081-2100'").set_index("source_cohort")
    a=primary.loc["all_88_original_isotope_sites"]
    b=primary.loc["wet50_46_original_isotope_sites"]
    if not (a.n_isotope_source_sites==88 and a.sites_modelmean_sos_negative==88
        and a.sites_all3_models_sos_negative==80
        and a.sites_all3_models_both_sos_ice_negative==43
        and np.isclose(a.modelmean_sos_mean_0p001,-.3277224324025498,atol=1e-10)
        and b.n_isotope_source_sites==46 and b.sites_all3_models_sos_negative==40
        and b.sites_all3_models_both_sos_ice_negative==17):
        raise ValueError("CMIP6 scenario projection on 88 original isotope sites drift")
    if len(main)!=8 or len(regions)!=52:
        raise ValueError("Different source result expected: 4 scenarios×2 cohorts and 13 source regions")
    summary={
        "status":"PASS_88_SOURCE_PENGUIN_ISOTOPE_SITE_FUTURE_PHYSICAL_OVERLAP_ONLY",
        "source_image_isotope_site_seasons":860,
        "source_image_sites":88,"source_original_reporting_regions":13,
        "source_CMIP6_all_three_models_wetgrid_within50_sites":46,
        "source_historical_isotope_observation_period":"1996–2012 start season; November–following February",
        "source_future_CMIP6_physical_periods":["2041-2060","2081-2100"],
        "source_CMIP6_physical_season":"August–November",
        "different_glorys_vs_cmip6_grid_and_tas_vs_thetao":True,
        "do_not_multiply_0p834_isotope_slope_by_future_sos":True,
        "no_true_future_trophic_or_nesting_projection":True,
        "primary_ssp585_late":a.to_dict(),
        "quality_50km_sensitivity":b.to_dict()
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    main.to_csv(out/"original_88_isotope_sites_four_CMIP6_scenario_exposure.csv",index=False)
    regions.to_csv(out/"original_88_isotope_sites_CMIP6_13region_exposure.csv",index=False)
    merged.to_csv(out/"original_88_isotope_sites_source_model_physical_scenarios_only.csv",index=False)
    (out/"original_88_isotope_site_CMIP6_physical_only_verdict.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return summary
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--physical-zip",required=True)
    p.add_argument("--isotope-zip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.physical_zip,a.isotope_zip,a.out)
