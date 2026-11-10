#!/usr/bin/env python3
"""Strict within-December QA on the already fixed original 150 Landsat8 scenes.

This is a post-result QUALITY sensitivity, NOT a new ecological model or a search
for significant greening. It reads an already generated Actions artifact zip
(or a local original-COG source output folder), and does NOT fetch/select new
scenes or reassign site/date/physical sample locations.

Each year needs >=2 December original source scene dates with QA-clear
nonwater/nonsnow unsaturated red & NIR at each of >=6 identical polar-grid points.
No biological abundance or plant-cover truth is inferred.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,statistics,zipfile
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path

CAT="landsat_original_outputs/original_landsat_catalog_50_siteyears.csv"
SCENES="landsat_original_outputs/original_L8_scene_QA_receipts.csv"
POINTS="landsat_original_outputs/original_geo_point_scene_NDVI_quality.csv"

def csv_from_bytes(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"),newline="")))

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--artifact",required=True,type=Path)
    arg.add_argument("--output",required=True,type=Path)
    a=arg.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.artifact) as z:
        names=set(z.namelist())
        if not {CAT,SCENES,POINTS}<=names:
            raise ValueError("Original Landsat QA source artifact incomplete")
        cat=csv_from_bytes(z.read(CAT))
        scenes=csv_from_bytes(z.read(SCENES))
        points=csv_from_bytes(z.read(POINTS))
    if len(cat)!=50 or len(scenes)!=150 or len(points)!=11550:
        raise ValueError("Original source counts changed or data corrupted")
    if len({z["original_item_id"] for z in scenes})!=64:
        raise ValueError("Original source site×scene reuse and independent scene identity changed")
    if Counter(z["catalog_status"] for z in cat)!={"ok":50} or Counter(z["retrieval_status"] for z in scenes)!={"ok":150}:
        raise ValueError("Catalog/asset errors in supposedly successful raw Landsat scenes")
    status=Counter(p["qa_status"] for p in points)
    if status!={"cloud_snow_water_or_fill_QA":10531,
               "qa_clear_land_non_snow":983,
               "invalid_surface_reflectance":36}:
        raise ValueError("Source QA outcome signature changed")
    # Site×breeding year×fixed physical point; no duplication among scene dates.
    by=defaultdict(dict)
    for p in points:
        if p["qa_status"]!="qa_clear_land_non_snow":
            continue
        key=(p["site_id"],int(p["survey_season"]),int(p["point_id"]))
        date=p["original_scene_date"]
        if date in by[key]:
            raise ValueError("Multiple original source scenes on the same calendar day for a fixed sample point")
        by[key][date]=float(p["ndvi"])
    source_years=defaultdict(list)
    for z in cat:
        source_years[z["site_id"]].append(int(z["survey_season"]))
    if len(source_years)!=25:raise ValueError("Fixed 25 source site list changed")
    summary_rows=[]
    for site in sorted(source_years):
        years=sorted(source_years[site])
        for year_a,year_b in combinations(years,2):
            valid_all=[]
            valid_dec=[]
            diff_all=[]
            diff_dec=[]
            for pt in range(77):
                src_a=by.get((site,year_a,pt),{})
                src_b=by.get((site,year_b,pt),{})
                if len(src_a)>=2 and len(src_b)>=2:
                    valid_all.append(pt)
                    diff_all.append(statistics.median(src_b.values())-statistics.median(src_a.values()))
                # Frozen season-start December, independent of source spectral
                # values. January/February are not compared to December.
                dec_a=[v for date,v in src_a.items() if date[5:7]=="12" and int(date[:4])==year_a]
                dec_b=[v for date,v in src_b.items() if date[5:7]=="12" and int(date[:4])==year_b]
                if len(dec_a)>=2 and len(dec_b)>=2:
                    valid_dec.append(pt)
                    diff_dec.append(statistics.median(dec_b)-statistics.median(dec_a))
            summary_rows.append({
                "site_id":site,"first_breeding_season":year_a,
                "second_breeding_season":year_b,
                "n_all_DecFeb_same_geo_points_at_least_2dates_both":len(valid_all),
                "DecFeb_median_NDVI_delta_if_n6":statistics.median(diff_all) if len(valid_all)>=6 else "",
                "n_Dec_only_same_geo_points_at_least_2dates_both":len(valid_dec),
                "December_median_NDVI_delta_if_n6":statistics.median(diff_dec) if len(valid_dec)>=6 else "",
                "monthly_comparison_pass_n6":len(valid_dec)>=6,
                "is_vegetation_or_climate_causal_effect":False
            })
    if len(summary_rows)!=33:
        raise ValueError("Expected 33 potential true census-year pairs, not artificial years")
    summer=[r for r in summary_rows if r["n_all_DecFeb_same_geo_points_at_least_2dates_both"]>=6]
    dec=[r for r in summary_rows if r["n_Dec_only_same_geo_points_at_least_2dates_both"]>=6]
    def sitekeys(v):
        return {(r["site_id"],r["first_breeding_season"],r["second_breeding_season"])
                for r in v}
    if sitekeys(summer)!={("CRZW",2017,2018),("CRZW",2018,2019),("INEX",2018,2019)}:
        raise ValueError("Full summer QA strict scene cohort changed")
    if sitekeys(dec)!={("INEX",2018,2019)} or dec[0]["n_Dec_only_same_geo_points_at_least_2dates_both"]!=13:
        raise ValueError("Strict December matched cohort drift")
    observed_delta=float(dec[0]["December_median_NDVI_delta_if_n6"])
    if abs(observed_delta+0.029688455834549293)>1e-10:
        raise ValueError("Original strict December median spectral delta drift")
    with (a.output/"strict_December_source_month_pair_33.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(summary_rows[0]))
        w.writeheader()
        w.writerows(summary_rows)
    status={
      "status":"MONTH_MATCHED_ORIGINAL_SOURCE_QA_COMPLETE_NO_BOTANICAL_INFERENCE",
      "original_source_artifact_sha256":hashlib.sha256(a.artifact.read_bytes()).hexdigest(),
      "n_eligible_original_census_siteyears":len(cat),
      "n_original_Landsat8_QA_and_reflectance_scenes":len(scenes),
      "n_unique_original_Landsat8_scene_ids":len({z["original_item_id"] for z in scenes}),
      "n_site_scene_source_reads_not_independent_images":len(scenes),
      "n_original_fixed_sample_pixel_scenes":len(points),
      "n_QA_valid_spectral_points":status["qa_clear_land_non_snow"],
      "n_potential_census_site_yearpairs":len(summary_rows),
      "n_broad_DecFeb_spectral_pairs_n6":len(summer),
      "n_month_aligned_December_spectral_pairs_n6":len(dec),
      "strict_December_support":[{
         "site":r["site_id"],"seasons":[r["first_breeding_season"],r["second_breeding_season"]],
         "common_source_spectral_points":r["n_Dec_only_same_geo_points_at_least_2dates_both"],
         "NDVI_median_spectral_difference_not_plant_area":r["December_median_NDVI_delta_if_n6"]}
         for r in dec],
      "full_DecFeb_source_support":[{
         "site":r["site_id"],"seasons":[r["first_breeding_season"],r["second_breeding_season"]],
         "common_source_spectral_points":r["n_all_DecFeb_same_geo_points_at_least_2dates_both"],
         "NDVI_median_spectral_difference_not_plant_area":r["DecFeb_median_NDVI_delta_if_n6"]}
         for r in summer],
      "conclusion":"Summer-wide annual differences are sensitive to acquisition month; December-only source supports one site pair and is not botanical vegetation cover or warming-caused greening.",
      "note":"This is a POST-RESULT strict source QA test; source IDs and selected 3 scenes per site-year were not modified after reading NDVI."
    }
    (a.output/"strict_December_source_month_gate.json").write_text(
        json.dumps(status,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("LANDSAT_SOURCE_FIXED_MONTH_QA="+json.dumps(status,ensure_ascii=False))
if __name__=="__main__":
    main()
