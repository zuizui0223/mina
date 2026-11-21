#!/usr/bin/env python3
"""Purely mathematical 30m Landsat pixel-size upper bound from independently
verified 44 real 2013–18 guano positive polygons at Ardley (Adelie, gentoo).

Uses EXISTING successful geospatial source audit artifact 14599603634 SHA256
95289f3dad6e8604f8116e60e230616b36b167874623951be6fee95dac8e75c4.
No additional Zenodo request. NO photo or new Landsat8 reflectance; NO isotope,
no winter polynya effect. Data provider responded 429 when a follow-on attempt
repeated the same 44 ZIP64 range requests: do not hammer provider again.

For each date+species, any 30m projected pixel can have at MOST min(900, A)
square metres of this *source-mapped* guano, where A is entire positive-polygon
union area on that date for that species, regardless of pixel grid phase.
If A < 0.8*900 (720m2), an >=80%-guano-pure 30m pixel is mathematically
impossible. Conversely A>720 DOES NOT guarantee a pure pixel because patches
may be fragmented and none fall together in one pixel.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_ARTIFACT_SHA256="95289f3dad6e8604f8116e60e230616b36b167874623951be6fee95dac8e75c4"
SOURCE_RECEIPT="ARDLEY_NATIVE_44_GUANO_SHAPEFILE_ACTUAL_GEOGRAPHIC_GATE.json"
AREA_PER_30M_UTM_CELL_M2=900.
PREDECLARED_PURITY_LEVELS=(0.25,0.50,0.80,0.95)
SOURCE_PROVIDER_DOI="10.5281/zenodo.14503437"
NO_REPEAT_SOURCE_RATE_LIMIT="429 observed at second repeated source ZIP range request; use previously archived audit"

def main(a):
    raw=Path(a.old_source_audit_zip).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_ARTIFACT_SHA256:
        raise ValueError("Actual 44 original guano source audit SHA256 changed")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip():raise ValueError("Source audit artifact ZIP CRC error")
        names=[n for n in z.namelist() if n==SOURCE_RECEIPT or n.endswith("/"+SOURCE_RECEIPT)]
        if len(names)!=1:raise ValueError("Real source geospatial JSON receipt missing")
        source=json.loads(z.read(names[0]))
    if source["status"]!="ALL_44_ACTUAL_DATED_ARDLEY_GUANO_SHAPEFILES_GEOGRAPHICALLY_VALIDATED":
        raise ValueError("Original 44 real shapefile geography was not fully verified")
    d=pd.DataFrame(source["real_guano_geographic_metadata"])
    if len(d)!=44 or not d.source_WKT_CRS_EPSG.eq(32721).all():
        raise ValueError("Original 44 geo-polygons source or native EPSG32721 drift")
    if d.invalid_source_geometries.sum()!=0 or d.n_native_guano_polygons.min()<1:
        raise ValueError("True guano geometry not valid")
    d["species"]=d.path.str.extract(r"_(adelie|gentoo)\.shp$")[0]
    d["original_mask_day"]=pd.to_datetime(d.path.str.extract(r"Ardley_(\d{8})_")[0],format="%Y%m%d").dt.date.astype(str)
    if len(set(d.species))!=2 or d.original_mask_day.nunique()!=22:
        raise ValueError("Original actual 22 × 2 dated guano source population changed")
    if d.duplicated(["original_mask_day","species"]).any():
        raise ValueError("Original shapefile species and date duplicate")
    a.out.mkdir(parents=True,exist_ok=True)
    upper=[]
    for r in d.itertuples():
        area=float(r.dissolved_union_footprint_m2)
        if not np.isfinite(area) or area<=0:raise ValueError("Not actual source area")
        v={"original_mask_day":r.original_mask_day,
            "source_species":r.species,
            "original_annotated_guano_positive_polygon_area_m2":area,
            "original_annotated_polygon_objects":int(r.n_native_guano_polygons),
            "source_polygon_total_area_divided_by_nominal30m_pixel_area":area/AREA_PER_30M_UTM_CELL_M2,
            "upper_bound_guano_fraction_of_any_one_nominal_30m_pixel":min(1.,area/AREA_PER_30M_UTM_CELL_M2),
            "cannot_prove_some_grid_pixel_exceeds_bound":True}
        for threshold in PREDECLARED_PURITY_LEVELS:
            v["30m_purity_ge_"+str(int(round(threshold*100)))+"pct_mathematically_impossible"] = bool(
                area<AREA_PER_30M_UTM_CELL_M2*threshold)
        upper.append(v)
    u=pd.DataFrame(upper).sort_values(["source_species","original_mask_day"])
    u.to_csv(a.out/"ARDLEY_ORIGINAL_44_REAL_GUANO_SHAPEFILES_30M_PROVABLE_AREA_BOUNDS.csv",index=False)
    out=[]
    for species,g in u.groupby("source_species",sort=True):
        out.append({
            "species":species,
            "n_actual_source_shapefile_dates":len(g),
            "source_total_annotated_guano_area_min_median_max_m2":[float(g.original_annotated_guano_positive_polygon_area_m2.min()),
                float(g.original_annotated_guano_positive_polygon_area_m2.median()),
                float(g.original_annotated_guano_positive_polygon_area_m2.max())],
            "polygon_object_sum":int(g.original_annotated_polygon_objects.sum()),
            "n_dates_mathematically_impossible_at_least_80pct_pure_30m_pixel":int(
                g["30m_purity_ge_80pct_mathematically_impossible"].sum()),
            "n_dates_mathematically_impossible_at_least_50pct_pure_30m_pixel":int(
                g["30m_purity_ge_50pct_mathematically_impossible"].sum()),
            "n_dates_with_enough_area_in_principle_for_80pct":int(
                (~g["30m_purity_ge_80pct_mathematically_impossible"]).sum()),
            "minimum_maximum_guano_fraction_across_source_mask_days":[float(g.upper_bound_guano_fraction_of_any_one_nominal_30m_pixel.min()),
                float(g.upper_bound_guano_fraction_of_any_one_nominal_30m_pixel.max())],
        })
    if out[0]["species"]!="adelie" or out[0]["n_dates_mathematically_impossible_at_least_80pct_pure_30m_pixel"]!=22:
        raise ValueError("Mathematical area bound check differs from expected true source Adélie limitation")
    rec={"status":"ALL_44_SOURCE_VERIFIED_30M_PIXEL_PURITY_MATHEMATICAL_UPPER_BOUNDS",
         "source_polygon_verification_origin":"GitHub Actions #44671441478 SUCCESS",
         "source_original_44_geo_audit_artifact_id":14599603634,
         "source_exact_artifact_SHA256":SOURCE_ARTIFACT_SHA256,
         "source_original_publication":"Pfeifer et al. 2025, Ecological Indicators, Guano native drone shapefile dataset",
         "source_Zenodo":SOURCE_PROVIDER_DOI,
         "n_independent_source_mask_dates":22,
         "n_original_real_species_and_date_shapefiles":44,
         "L8_nominal_projected_cell_side_m":30,
         "L8_nominal_cell_m2":AREA_PER_30M_UTM_CELL_M2,
         "purity_bounds_are_rigorous_regardless_30m_grid_phase":True,
         "source_UTM_EPSG":32721,
         "source_label_is_annotated_guano_only_not_actual_L8_30m_true_positive_and_true_negative_pixel_classifier":True,
         "source_Ardley_not_in_original_88_sites":True,
         "mathematical_upper_bounds_by_species":out,
         "frozen_30m_levels":list(PREDECLARED_PURITY_LEVELS),
         "grid_mixing_above_source_area_bound_not_possible":True,
         "grid_pure_pixels_cannot_be_inferred_from_source_area_if_area_ge_threshold":True,
         "actual_native_L8_grid_alignment_not_evaluated":True,
         "independent_rock_snow_ice_pixel_truth_not_available":True,
         "reason_no_repeated_4GB_source_range_fetch":NO_REPEAT_SOURCE_RATE_LIMIT,
         "new_2013_2021_L8_spectral_isotope_outcomes_not_opened":True,
         "no_new_polynya_association_fitted":True}
    (a.out/"ARDLEY_44_GUANO_SHAPEFILE_MATHEMATICAL_30M_PURITY_UPPER_BOUND_RESULT.json").write_text(
        json.dumps(rec,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(rec,indent=2,ensure_ascii=False),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--old-source-audit-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
