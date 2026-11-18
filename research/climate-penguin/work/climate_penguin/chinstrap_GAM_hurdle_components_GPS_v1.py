"""Separate original Freer krill-GAM *occurrence* vs positive-density fields
at BAS Chinstrap GPS visited versus same-distance native raster backgrounds.

This is a component decomposition of ONE ALREADY TRAINED historical GAM,
not an independent source of prey biomass, food intake, salinity/ice effects,
or demographic prediction. Full 308 source tracks, two model years per
breeding season, seven island-years, three same-species matched comparisons.
Source data: BAS GPS Version2 DOI 10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92
and Freer BAS DOI 10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from collections import defaultdict
import numpy as np
import south_orkney_chinstrap_island_krill_v1 as island
import chinstrap_krill_geographic_vs_GPS_direction_v1 as radial
import freer_krill_signy_v2 as freer

COMPS=("prob","density_positive","combined")
PERIODS=("preseason","same_summer")
PAIRS=island.PAIRS
EXPECTED_RATIO={(2011,"LI"):1.7299767895093023,
                (2013,"PI"):4.0400136696919375,
                (2015,"MI"):2.9649677228535887}
SPECIES="Chinstrap"

def partition(observed,background):
    """Exact arithmetic mean-product log identity, NOT causal attribution.

    Combined is E[p*q], *not* E[p]*E[q]; the residual is the required
    mathematical within-unit aggregation covariance/composition term.
    """
    vals=[observed[c] for c in COMPS]+[background[c] for c in COMPS]
    if any(not math.isfinite(v) or v<=0 for v in vals):
        raise ValueError("Cannot decompose zero/nonfinite source probabilities or densities")
    result={
      "log_combined_GAM_visited_over_background":math.log(observed["combined"]/background["combined"]),
      "log_occurrence_probability_ratio":math.log(observed["prob"]/background["prob"]),
      "log_conditional_positive_density_ratio":math.log(observed["density_positive"]/background["density_positive"])
    }
    result["log_aggregation_interaction_residual"]=(
      result["log_combined_GAM_visited_over_background"]
      -result["log_occurrence_probability_ratio"]
      -result["log_conditional_positive_density_ratio"])
    if not math.isclose(result["log_combined_GAM_visited_over_background"],sum(
        result[k] for k in ("log_occurrence_probability_ratio",
          "log_conditional_positive_density_ratio",
          "log_aggregation_interaction_residual")),abs_tol=1e-12):
        raise ValueError("component identity failed")
    return result

def run(original_gps,original_gam):
    tracks,gps_audit=island.read_all_chinstrap(original_gps)
    centers=island.island_source_centers(tracks)
    models,model_audit,source_zipsha=freer.raster_fields(original_gam)
    if len(tracks)!=308 or len(centers)!=7 or len(models)!=10:
        raise ValueError("Original source cohort changed: 308 tracks/7 site-years/10 model-years")
    grids={}
    for (site,season),center in centers.items():
        for period in PERIODS:
            year=season+(period=="same_summer")
            fld=models[year]
            tr=fld["_transform"]
            for c in COMPS:
                _,rings,bins=radial.grid_reference(
                    fld[c],tr,center["center_lat"],center["center_lon"])
                grids[site,season,period,c]=(rings,bins)
    tags=[]
    unique_native_cells=defaultdict(set)
    for tag in tracks:
        site,season=tag["island"],tag["season"]
        center=centers[site,season]
        row={"island":site,"season_start":season,"deployment":tag["deployment"],
             "source_member_sha256":tag["source_sha256"],
             "n_original_GPS_positions":tag["raw_positions"],
             "measured_capture_or_dive_events":False,
             "model_source_trained_with_original_acoustic_ice_salinity":True}
        for period in PERIODS:
            year=season+(period=="same_summer")
            fld=models[year]
            hours,cells=radial.source_selected_unique_cells(
                 tag,center,fld["combined"],fld["_transform"])
            row[period+"_model_year"]=year
            row[period+"_qualifies"]=(bool(cells) and hours>=radial.N_VALID_HOURS)
            row[period+"_unique_model_cells"]=len(cells) if cells else 0
            row[period+"_original_hourly_positions_in_window"]=hours
            for c in COMPS:
                row[period+"_"+c+"_visit"]=None
                row[period+"_"+c+"_distance_background"]=None
                if not cells:continue
                rings,bins=grids[site,season,period,c]
                arr=fld[c]
                values=[float(arr[r,k]) for r,k in cells]
                if any(not math.isfinite(v) for v in values):
                    raise ValueError("component missing at originally valid combined-model GPS cell")
                bg=[rings[int(bins[r,k])] for r,k in cells]
                row[period+"_"+c+"_visit"]=float(statistics.mean(values))
                row[period+"_"+c+"_distance_background"]=float(statistics.mean(bg))
            if cells:
                unique_native_cells[site,season,period].update(cells)
                if not math.isclose(row[period+"_combined_visit"],float(
                    statistics.mean(fld["combined"][r,k] for r,k in cells)),abs_tol=1e-11):
                    raise ValueError("GPS component source cell mean mismatch")
        tags.append(row)
    if len(tags)!=308 or len({r["deployment"] for r in tags})!=308:
        raise ValueError("GPS duplicate source-IDs erroneously introduced")
    annual=[]
    for (site,season),center in sorted(centers.items()):
        for period in PERIODS:
            selected=[r for r in tags if r["island"]==site and r["season_start"]==season
                     and r[period+"_qualifies"]]
            if not selected:raise ValueError("GPS source model field missing for island-year")
            visit={c:float(statistics.mean(r[period+"_"+c+"_visit"] for r in selected))
                   for c in COMPS}
            bg={c:float(statistics.mean(r[period+"_"+c+"_distance_background"] for r in selected))
                   for c in COMPS}
            part=partition(visit,bg)
            entry={"island":site,"season_start":season,"model_period":period,
                   "model_year":season+(period=="same_summer"),
                   "source_deployments_all":sum(t["island"]==site and t["season_start"]==season for t in tags),
                   "source_deployments_qualified":len(selected),
                   "one_gam_source_krill_model_not_new_acoustic_data":True,
                   **part}
            for c in COMPS:
                entry[c+"_visited_GAM_mean"]=visit[c]
                entry[c+"_same_distance_GAM_background"]=bg[c]
                entry[c+"_visited_div_background"]=visit[c]/bg[c]
                entry[c+"_source_units"]= "dimensionless_probability" if c=="prob" else "g_per_m2"
            annual.append(entry)
    idx={(r["island"],r["season_start"],r["model_period"]):r for r in annual}
    pair_results=[]
    for yr,other in PAIRS:
        for period in PERIODS:
            a=idx["SI",yr,period]
            b=idx[other,yr,period]
            vals={"season_start":yr,"other_island":other,"reference_island":"SI",
                  "model_year":yr+(period=="same_summer"),
                  "model_period":period,
                  "qualified_other_source_deployments":b["source_deployments_qualified"],
                  "qualified_Signy_source_deployments":a["source_deployments_qualified"]}
            for c in COMPS:
                vals[c+"_original_GAM_visited_other_div_Signy"]=(b[c+"_visited_GAM_mean"]/
                    a[c+"_visited_GAM_mean"])
                vals[c+"_distance_background_other_div_Signy"]=(b[c+"_same_distance_GAM_background"]/
                    a[c+"_same_distance_GAM_background"])
                vals[c+"_radial_adjusted_ratio"]=(b[c+"_visited_div_background"]/
                    a[c+"_visited_div_background"])
            logs=("log_combined_GAM_visited_over_background",
                  "log_occurrence_probability_ratio","log_conditional_positive_density_ratio",
                  "log_aggregation_interaction_residual")
            for key in logs:
                vals["other_minus_Signy_"+key]=b[key]-a[key]
            comp=math.log(vals["combined_radial_adjusted_ratio"])
            if not math.isclose(sum(vals["other_minus_Signy_"+k] for k in
                   logs[1:]),comp,abs_tol=1e-11):
                raise ValueError("matched island exact log component attribution identity failed")
            vals["mathematical_log_decomposition_exact"]=True
            pair_results.append(vals)
            if period=="preseason":
                if not math.isclose(vals["combined_radial_adjusted_ratio"],
                                     EXPECTED_RATIO[yr,other],rel_tol=1e-10,abs_tol=1e-10):
                    raise ValueError("source-original Freer combined-model island ratio drift")
    if len(annual)!=14 or len(pair_results)!=6:
        raise ValueError("source period/matched-island counts changed")
    gate={"status":"POSTHOC_PUBLISHED_KRILL_GAM_HURDLE_COMPONENT_DECOMPOSITION",
          "source_GPS_original_DOI":"10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92",
          "source_GAM_original_DOI":"10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32",
          "GAM_member_source_checks":model_audit,
          "source_original_ZIP_SHA256":source_zipsha,
          "source_original_GPS_digest":gps_audit["source_original_313_csv_sha256"],
          "source_native_GPS_n":len(tags),
          "source_island_year_n":len(centers),"source_matched_pair_n":len(PAIRS),
          "GAM_occurrence_probability_and_positive_density_are_model_components":True,
          "GAM_ice_salinity_and_original_acoustics_used_for_training":True,
          "source_reference":"10km distance-matched GAM-valid raster cells, NOT verified accessible ocean or actual prey",
          "temporal_exposure":"T is preceding Jan-Feb but GAM trained on full decade; T+1 can follow tagged bird observation, not a forecast",
          "exact_log_decomposition":"ln(E[p*q]_visit/E[p*q]_background) equals ln(E[p]_visit/E[p]_background) + ln(E[q]_visit/E[q]_background) + aggregation interaction residual; E[p*q] != E[p]*E[q]",
          "published_original_GAM_not_independent_prey_or_krill_capture":True,
          "no_2050_2100_forecast":True,
          "source_island_year_results":annual,
          "matched_preseason_results":[r for r in pair_results if r["model_period"]=="preseason"],
          "limitations":[
             "The positive-density GAM is conditional on modelled krill occurrence, not independently observed food captured by tagged penguins.",
             "This is arithmetic within one trained model, not causal mediation of sea-ice or salinity effects.",
             "Spatial covariance/aggregation interaction must be shown; separate component means do not multiply into the combined mean.",
             "Model-valid cells are not independently surveyed traversable marine habitats; headings/azimuth constraints unvalidated.",
             "Source GPS not dive-confirmed/capture; variable tag sample and only one other island per year.",
             "No effective independent regional or year heldout, no evidence of climate-driven future recruitment, nests, N_eff or greening."
          ]}
    pixel_annual,pixel_pairs=independent_pixel_weighting_for_components(
        unique_native_cells,centers,models,grids)
    gate["native_pixel_union_preseason"]=[r for r in pixel_pairs if r["model_period"]=="preseason"]
    return tags,annual,pair_results,gate,pixel_annual,pixel_pairs

def independent_pixel_weighting_for_components(unions,centers,models,grids):
    """One vote per native GAM cell, rather than repeated source GPS tags.

    Native cells are spatially autocorrelated and do not represent
    independent marine prey observations or habitat availability.
    """
    annual=[]
    for (site,season),center in sorted(centers.items()):
        for period in PERIODS:
            cells=sorted(unions[site,season,period])
            if not cells:raise ValueError("original native pixel union is empty")
            year=season+(period=="same_summer")
            fld=models[year]
            observed={}
            background={}
            for c in COMPS:
                arr=fld[c]
                rings,bins=grids[site,season,period,c]
                observed[c]=float(statistics.mean(float(arr[r,k]) for r,k in cells))
                background[c]=float(statistics.mean(rings[int(bins[r,k])] for r,k in cells))
            parts=partition(observed,background)
            row={"island":site,"season_start":season,"model_period":period,
                 "model_year":year,"n_native_unique_model_pixels":len(cells),
                 "pixels_not_independent_ocean_observations":True,**parts}
            for c in COMPS:
                row[c+"_visited_GAM_mean"]=observed[c]
                row[c+"_same_distance_GAM_background"]=background[c]
                row[c+"_visited_div_background"]=observed[c]/background[c]
            annual.append(row)
    idx={(r["island"],r["season_start"],r["model_period"]):r for r in annual}
    paired=[]
    previously_verified={(2011,"LI"):1.6418902195131548,
                         (2013,"PI"):4.5112838741401875,
                         (2015,"MI"):3.239683825849412}
    for yr,other in PAIRS:
        for period in PERIODS:
            a=idx["SI",yr,period]
            b=idx[other,yr,period]
            row={"season_start":yr,"other_island":other,"model_period":period,
                 "n_native_pixels_other":b["n_native_unique_model_pixels"],
                 "n_native_pixels_Signy":a["n_native_unique_model_pixels"]}
            for c in COMPS:
                row[c+"_radial_adjusted_ratio"]=b[c+"_visited_div_background"]/a[c+"_visited_div_background"]
            for k in ("log_occurrence_probability_ratio",
                      "log_conditional_positive_density_ratio",
                      "log_aggregation_interaction_residual"):
                row["other_minus_Signy_"+k]=b[k]-a[k]
            terms=sum(row["other_minus_Signy_"+k] for k in (
                    "log_occurrence_probability_ratio",
                    "log_conditional_positive_density_ratio",
                    "log_aggregation_interaction_residual"))
            if not math.isclose(terms,math.log(row["combined_radial_adjusted_ratio"]),abs_tol=1e-11):
                raise ValueError("native pixel exact log partition drift")
            if period=="preseason" and not math.isclose(row["combined_radial_adjusted_ratio"],
                       previously_verified[yr,other],abs_tol=1e-10):
                raise ValueError("independent source-native pixel union receipt changed")
            row["same_published_GAM_not_independent_ocean_data"]=True
            paired.append(row)
    if len(annual)!=14 or len(paired)!=6:
        raise ValueError("14 original island-year periods and 6 pairs required")
    return annual,paired

def save(path,rows):
    if not rows:raise ValueError("empty source result")
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gps-zip",required=True,type=Path)
    p.add_argument("--model-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    arg=p.parse_args()
    tags,annual,pairs,receipt,pixel_annual,pixel_pairs=run(arg.gps_zip,arg.model_zip)
    if arg.check:
        if len(tags)!=308 or len(annual)!=14 or len(pairs)!=6:
            raise ValueError("known cohort shape changed")
        if {(z["island"],z["season_start"],z["model_period"])
           for z in annual if z["island"]=="SI"}!={("SI",y,t) for y in (2011,2013,2015,2018) for t in PERIODS}:
            raise ValueError("original Signy four-year support unexpectedly changed")
    arg.out.mkdir(parents=True,exist_ok=True)
    save(arg.out/"308_source_GPS_hurdle_components.csv",tags)
    save(arg.out/"14_island_year_hurdle_components.csv",annual)
    save(arg.out/"6_matched_island_hurdle_log_decomposition.csv",pairs)
    save(arg.out/"14_island_year_native_pixel_hurdle_components.csv",pixel_annual)
    save(arg.out/"6_matched_island_native_pixel_hurdle_decomposition.csv",pixel_pairs)
    (arg.out/"decision.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":receipt["status"],"source_tags":len(tags),"source_island_years":len(annual),
        "matched_preseason":[{k:r[k] for k in (
            "season_start","other_island","combined_radial_adjusted_ratio",
            "prob_radial_adjusted_ratio","density_positive_radial_adjusted_ratio",
            "other_minus_Signy_log_occurrence_probability_ratio",
            "other_minus_Signy_log_conditional_positive_density_ratio",
            "other_minus_Signy_log_aggregation_interaction_residual")}
            for r in receipt["matched_preseason_results"]],
        "native_pixel_union_preseason":[{k:r[k] for k in (
          "season_start","other_island","prob_radial_adjusted_ratio",
          "density_positive_radial_adjusted_ratio","combined_radial_adjusted_ratio",
          "other_minus_Signy_log_occurrence_probability_ratio",
          "other_minus_Signy_log_conditional_positive_density_ratio",
          "other_minus_Signy_log_aggregation_interaction_residual")}
           for r in pixel_pairs if r["model_period"]=="preseason"],
        "check":arg.check
    },ensure_ascii=False))
if __name__=="__main__":main()
