#!/usr/bin/env python3
"""Independently check four GAM output tables and fixed original source cohorts.

The observation support, arbitrary ecological availability, and unequal cluster
counts are reported; not a second fit or a search for significant responses.
"""
from __future__ import annotations
from collections import defaultdict
import csv,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"

def rows(filename):
    with (OUT/filename).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def mean(a):return sum(a)/len(a)
def corr(x,y):
    xm=mean(x);ym=mean(y)
    a=sum((v-xm)*(w-ym) for v,w in zip(x,y))
    b=sum((v-xm)**2 for v in x);c=sum((w-ym)**2 for w in y)
    return a/math.sqrt(b*c) if b*c>0 else None

def main():
    support=json.loads((OUT/"source_coverage.json").read_text())
    marine=rows("marine_observed_site_species_year_661.csv")
    land=rows("contemporary_vegetation_site_species_197.csv")
    fits=rows("four_fixed_GAM_fit_metrics.csv")
    smooth=rows("fixed_GAM_approximate_smooths.csv")
    assert len(marine)==661 and len(land)==197 and len(fits)==4
    assert len({(r["site_id"],r["species"],r["year"]) for r in marine})==661
    assert len({(r["site_id"],r["species"]) for r in land})==197
    assert sum(int(r["observed_nest_count"])==0 for r in marine)==44
    assert len({r["site_id"] for r in marine})==40
    assert len({r["site_species"] for r in marine})==56
    assert len({r["region"] for r in marine})==6
    for row in land:
        assert float(row["static_mapped_vegetation_2km_m2"])>0
        assert row["one_composite_2017to2023_not_yearly_ndvi"]=="True"
    for row in marine:
        assert int(row["observed_nest_count"])>=0
        assert int(row["year"]) in range(1991,2021)
        assert row["record_is_an_actual_original_count"]=="True"
        assert math.isclose(float(row["sic_AugNov_0to100km_pct"]),
            float(row["sic_30y_site_mean_pct"])+
            10*float(row["sic_site_anomaly_per10pp"]),abs_tol=1e-10)
    keys={x["model"]:x for x in fits}
    if set(keys)!={"marine_without_sic","marine_with_sic","land_without_mapped_veg","land_with_mapped_veg"}:
        raise ValueError("Unexpected model selection")
    for name,r in keys.items():
        if int(r["n"])!=(661 if name.startswith("marine") else 197):
            raise ValueError("Model observed source grain diverged")
        if not math.isfinite(float(r["AIC"])) or not math.isfinite(float(r["adj_r2"])):
            raise ValueError("Non-finite model fit diagnostics")
        if r["is_presence_absence_or_unobserved_site_SDM"].lower() not in ("false","0"):
            raise ValueError("False occupancy/suitability claim in model outputs")
    if len([r for r in smooth if "sic_site_anomaly" in r["term"]])!=3:
        raise ValueError("Missing species-specific marine ice GAM smooth")
    if len([r for r in smooth if "static_vegetation_area" in r["term"]])!=3:
        raise ValueError("Missing species-specific terrestrial vegetation GAM smooth")
    for r in smooth:
        if r["p_is_spatial_cluster_or_project_fdr"]!="False":
            raise ValueError("Nominal p mislabeled as spatial or project-wide adjusted p")

    group=defaultdict(list)
    for z in marine:group[z["species"]].append(z)
    correlations={}
    for sp,rr in group.items():
        subset=defaultdict(list)
        for z in rr:subset[z["site_id"]].append(z)
        y=[];x=[]
        for vv in subset.values():
            xs=[float(z["sic_site_anomaly_per10pp"]) for z in vv]
            ys=[float(z["log1p_nests"]) for z in vv]
            x.extend(z-mean(xs) for z in xs)
            y.extend(z-mean(ys) for z in ys)
        correlations[sp]={"n_obs":len(rr),"n_sites":len(subset),
                         "raw_demeaned_site_correlation_no_year_adjustment":corr(x,y),
                         "no_p_value":True}
    summary={
      "status":"ORIGINAL_SOURCE_GAM_DIAGNOSTIC_PASS_MODEL_FITS_ARE_EXPLORATORY",
      "landscape_estimand":"Observed positive-colony nest counts / cross-sectional median counts, NOT occupancy or true absences",
      "n_original_ice_source_rows":support["n_original_ice_monthly"],
      "n_original_observed_census_rows":support["n_original_unambiguous_site_species_season"],
      "n_historical_observations":len(marine),
      "n_historical_unique_site_species":56,
      "n_historical_known_sites":40,
      "n_historical_observed_zeros":44,
      "n_modern_positive_vegetation_site_species":len(land),
      "n_fit_models":len(fits),
      "within_site_raw_demeaned_ice_vs_logcount":correlations,
      "model_diagnostics":{k:{"AIC":float(z["AIC"]),"adj_r2":float(z["adj_r2"]),
                             "deviance_explained":float(z["deviance_explained"]),
                             "delta_AIC_from_base":float(z["delta_AIC_to_matching_base"])
                               if z["delta_AIC_to_matching_base"] else None}
                             for k,z in keys.items()},
      "environment_smooths":[{
        "model":z["model"],"term":z["term"],"edf":float(z["edf"]),
        "p_approximate_unadjusted":float(z["p_mgcv_approximate"])}
        for z in smooth if "sic_site_anomaly" in z["term"] or "static_vegetation_area" in z["term"]],
      "inference_notice":"The same sites repeatedly sampled, 26/40 in Victoria Land; factor-smooth p values are NOT robust independent-region p and no multiple-search correction. In-sample AIC is not verified future colony prediction.",
      "land_data_notice":"Static 2017-2023 mapped vegetation signal is measured after some original 1991–2020 marine count years; separate cross-sectional target only. Mapped zero is unknown non-detection, not established biological vegetation absence.",
      "source_inclusion":"No unobserved species-site-year or outside-background pseudoabsence was introduced."
    }
    (OUT/"post_result_model_interpretation.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("NONMAXENT_GAM_VERDICT="+json.dumps(summary),flush=True)

if __name__=="__main__":
    main()
