#!/usr/bin/env python3
"""Existing annual satellite vegetation coverage only, no new NDVI effect test.

Do not interpret Sentinel-2 land/snow spectral detections as verified vegetation
growth or export repeat static vegetation composites as annual habitat data.
"""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict,Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
INPUT=HERE/"joint_support_outputs"
OUT=HERE/"joint_support_outputs"

ORIGINAL={
  "annual_ndvi_sites":("outputs/vegetation_annual_ndvi_v1/annual_support.csv",
          "c2a18832d2ef5551b070eddb96e0c4ce52b0b47d"),
  "same_pixel_ndvi_changes":("outputs/vegetation_annual_ndvi_v1/same_pixel_changes.csv",
          "995275f7457c8dab4d90ea8ace736b5d3b997f31"),
  "season_count_annual_pixels":("outputs/vegetation_annual_pixels_v1/same_season_count_support.csv",
          "ffa7d5af5af28e490616e67e4ddcd270588d0320")
}
def get(name):
    path,sha=ORIGINAL[name]
    data=(ROOT/path).read_bytes()
    got=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if sha!=got:raise ValueError(f"Annual source Git SHA changed {name}: {got}")
    with (ROOT/path).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def local(name):
    with (INPUT/name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def write(name,rows):
    with (OUT/name).open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)

def main():
    original=local("site_25_environmental_context.csv")
    joined=local("matched_63_observed_rows.csv")
    if len(original)!=25 or len(joined)!=63:raise ValueError("Original joint-support inputs drift")
    sites={r["site_id"] for r in original}
    annual=get("annual_ndvi_sites")
    changes=get("same_pixel_ndvi_changes")
    direct=get("season_count_annual_pixels")
    annual_window=[r for r in annual if r["site_id"] in sites and 2017<=int(r["image_year"])<=2020]
    annual_sites={r["site_id"] for r in annual_window}
    annual_genuine={r["site_id"] for r in annual_window if int(r["pixels_two_dates"])>=1 and int(r["successful_scenes"])>0}
    annual_multiple=[r for r in changes if r["site_id"] in sites and
       2017<=int(r["first_year"])<=2020 and 2017<=int(r["last_year"])<=2020 and int(r["common_pixels"])>=1]
    # A source January scene in the same austral season is not automatically
    # an annual vegetation map, and may postdate the December count.
    census={ (r["site_id"],r["species"],int(r["actual_census_year"])) for r in joined}
    direct_matched=[r for r in direct if (r["site_id"],r["species_id"],int(r["season"])) in census]
    direct_valid=[r for r in direct_matched if int(r["read_success"])>0]
    land_twice=[r for r in direct_valid if int(r["land_twice_pixels"])>=1]
    month_known=[r for r in direct_valid if r["month_known"]=="True"]
    outrows=[]
    annual_by=defaultdict(list)
    for z in annual_window:annual_by[z["site_id"]].append(z)
    direct_by=defaultdict(list)
    for z in direct_matched:direct_by[z["site_id"]].append(z)
    for r in original:
        site=r["site_id"]
        annuals=annual_by[site]
        dr=direct_by[site]
        outrows.append({
           "site_id":site,"region":r["region"],
           "n_actual_2017to2020_ice_count_years":r["n_actually_surveyed_site_years"],
           "n_2017to2020_original_annual_ndvi_years":len({z["image_year"] for z in annuals}),
           "annual_ndvi_image_years":";".join(sorted({z["image_year"] for z in annuals})),
           "n_annual_source_years_with_repeated_pixel_dates":sum(int(z["pixels_two_dates"])>=1 for z in annuals),
           "n_2017to2020_annual_ndvi_year_pairs_same_pixel":sum(z["site_id"]==site for z in annual_multiple),
           "n_matched_original_colony_count_annual_pixel_candidate_records":len(dr),
           "n_matched_candidate_count_records_with_successful_scenes":sum(int(z["read_success"])>0 for z in dr),
           "n_matched_candidate_records_with_land_twice_pixel":sum(int(z["land_twice_pixels"])>0 for z in dr),
           "n_matched_candidate_records_month_known":sum(z["month_known"]=="True" for z in dr),
           "source_land_twice_is_vegetation_specific":False
        })
    if len(outrows)!=25:raise ValueError("Site-level output changed")
    summary={
      "status":"ORIGINAL_2017_2020_ANNUAL_NDVI_SOURCE_SUPPORT_AUDITED",
      "stage":"source coverage only, no phenology, climate niche or vegetation change p-values",
      "original_source_blobs":{n:v[1] for n,v in ORIGINAL.items()},
      "n_co_located_ice_census_veg_sites":len(sites),
      "n_exact_observed_census_site_species_years":len(joined),
      "n_sites_with_any_2017to2020_annual_ndvi_product":len(annual_sites),
      "n_sites_with_source_annual_repeated_pixel_dates":len(annual_genuine),
      "n_site_image_years_from_existing_annual_ndvi_product":len(annual_window),
      "original_annual_ndvi_image_year_distribution":dict(sorted(Counter(int(r["image_year"]) for r in annual_window).items())),
      "n_sites_with_pair_2017to2020_original_annual_NDVI_common_pixels":len({r["site_id"] for r in annual_multiple}),
      "n_annual_NDVI_cross_year_pairs_2017to2020":len(annual_multiple),
      "n_original_census_annual_pixel_records_matching_63":len(direct_matched),
      "n_matching_annual_pixel_records_successful_scene":len(direct_valid),
      "n_matching_annual_pixel_records_land_twice_1plus":len(land_twice),
      "n_matching_annual_pixel_records_month_known":len(month_known),
      "validation":"All 3 source annual product receipts are Git blob matched; original 25-site overlap is unchanged.",
      "limits":[
         "Annual NDVI source across years is not guaranteed to represent the same vegetation pixels.",
         "Land-twice pixel classification from satellite may be barren ground/rock, not botanical vegetation.",
         "A successful January satellite scene may be after December penguin census, so not proof of antecedent habitat.",
         "Existing image data do not by themselves establish greening, vegetation productivity, or marine–land niche shift.",
         "Unobserved years are missing, not zero vegetation."
      ]}
    write("existing_annual_vegetation_support_at_25_sites.csv",outrows)
    (OUT/"existing_annual_vegetation_coverage.json").write_text(
      json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("ORIGINAL_ANNUAL_VEGETATION_COVERAGE="+json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=="__main__":
    main()
