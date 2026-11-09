#!/usr/bin/env python3
"""Check source-pinned native integer-count NB sensitivity; do not tune after p."""
from __future__ import annotations
import csv, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"nb_outputs"
SRC=ROOT/"outputs"
def rows(path):
    with path.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def main():
    source=json.loads((SRC/"source_coverage.json").read_text(encoding="utf-8"))
    panel=rows(SRC/"marine_observed_site_species_year_661.csv")
    fit=rows(OUT/"fixed_nb_fit_metrics.csv")
    smooth=rows(OUT/"fixed_nb_approximate_smooths.csv")
    assert len(panel)==661 and len({(r["site_id"],r["species"],r["year"]) for r in panel})==661
    assert sum(int(r["observed_nest_count"])==0 for r in panel)==44
    assert len({r["site_id"] for r in panel})==40
    keys={r["model"]:r for r in fit}
    if len(fit)!=3 or set(keys)!={"nb_no_sic","nb_with_sic","nb_sic_without_Victoria_Land"}:
        raise ValueError("Altered model family or number of post-result tests")
    for name,row in keys.items():
        if row["family"]!="negative_binomial_native_integer_counts" or row["converged"]!="TRUE":
            # R write.csv logical prints TRUE; reject false/ambiguous
            raise ValueError("Model distribution or convergence changed: "+name)
        if row["post_result_exploratory"]!="TRUE" or row["unobserved_sites_or_years_imputed"]!="FALSE":
            raise ValueError("Model is mislabelled as confirmatory or added pseudoabsences")
        if (int(row["n"]),int(row["n_unique_sites"]))!=((353,14) if name.endswith("Victoria_Land") else (661,40)):
            raise ValueError("Site/year support changed: "+name)
        if not all(math.isfinite(float(row[z])) for z in ("estimated_theta","AIC","explained_deviance")):
            raise ValueError("Invalid NB model metrics: "+name)
        if float(row["estimated_theta"])<=0:
            raise ValueError("Invalid NB theta: "+name)
    d=float(keys["nb_with_sic"]["AIC"])-float(keys["nb_no_sic"]["AIC"])
    reported=float(keys["nb_with_sic"]["delta_AIC_vs_fixed_no_sic"])
    if not math.isclose(d,reported,rel_tol=1e-8,abs_tol=1e-5):
        raise ValueError("NB baseline and SIC AIC difference inconsistent")
    ice=[r for r in smooth if "sic_site_anomaly_per10pp" in r["term"]]
    if len(ice)!=6:
        raise ValueError("Expected 3 species-specific SIC smooth terms in both sensitivity fits")
    p_by_model={}
    for r in ice:
        if r["robust_colony_or_region_cluster_p"]!="FALSE" or r["project_wide_multiplicity_adjusted_p"]!="FALSE":
            raise ValueError("Nominal p improperly claimed as region independent")
        p=float(r["approximate_unadjusted_p"])
        if not 0<=p<=1:
            raise ValueError("Invalid mgcv approximate NB p-value")
        p_by_model.setdefault(r["model"],{})[r["term"]]={
            "edf":float(r["edf"]),"p_nominal":p
        }
    for name in ("nb_with_sic","nb_sic_without_Victoria_Land"):
        if len(p_by_model.get(name,{}))!=3:raise ValueError("Missing species-specific ice smooth: "+name)
    verdict={
      "status":"ORIGINAL_INTEGER_COUNT_NEGATIVE_BINOMIAL_GAM_SENSITIVITY_VERIFIED",
      "analysis_design":"post-result, fixed NB distribution check after Gaussian log1p-nests nominal association",
      "source_original_site_species_year_records":len(panel),
      "original_observed_zeros":44,
      "original_census_sources_git_blobs":source["original_git_blobs"],
      "nb_models":{
         name:{"n":int(r["n"]),"sites":int(r["n_unique_sites"]),
               "theta":float(r["estimated_theta"]),"AIC":float(r["AIC"]),
               "deviance_explained":float(r["explained_deviance"])}
         for name,r in keys.items()},
      "full_data_delta_AIC_SIC_vs_null":d,
      "nominal_mgcv_ice_smooths":p_by_model,
      "limits":[
        "Observed colony count GAM, not occupancy or detection-adjusted SDM at unobserved sites",
        "No independent source replication; regional correlation and nonrandom survey coverage remain",
        "No season-year-matched vegetation product for this historical 1991-2020 count panel",
        "Individual nominal mgcv p-values are not region-block tests or project-wide multiple-testing adjusted"
      ]
    }
    (OUT/"nb_sensitivity_verified_summary.json").write_text(json.dumps(verdict,indent=2)+"\n")
    print("NB_GAM_LIKELIHOOD_AUDIT_VERDICT="+json.dumps(verdict))
if __name__=="__main__":main()
