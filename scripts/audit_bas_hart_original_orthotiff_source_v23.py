#!/usr/bin/env python3
"""V23 BAS Hart original orthotiff file-list source genealogy, no image pixels.

Verifies whether V20 original nest coordinate CSVs share original publisher
imagery folders; filename co-location alone does not verify same survey mask.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

LOCALITIES=("Ashen_Hills","Bellingshausen","Beach_Point","Hewison_Point")
EXPECTED_TIFF=132
EXPECTED_FILES=164


def inventory_original_imagery(manifest):
    if manifest["status"]!="VERIFIED_ORIGINAL_SOURCE_FILES_PUBLISHER_SUMMARY_COUNT_DISCREPANCY":
        raise ValueError("SOURCE_STOP original BAS full archive not verified")
    all_files=manifest["original_all_file_metadata_only"]
    if len(all_files)!=EXPECTED_FILES:raise ValueError("SOURCE_STOP original published file corpus changed")
    image_files=[x for x in all_files if x["original_source_file_type"] in ("tif","tiff")]
    if len(image_files)!=EXPECTED_TIFF:raise ValueError("SOURCE_STOP original TIFF layer total changed")
    groups={}
    for site in LOCALITIES:
        imgs=sorted((x for x in image_files
                     if x["top_level_source_locality_folder"]==site),
                    key=lambda z:z["original_archive_relative_path"])
        ids=[x["original_archive_relative_path"] for x in imgs]
        if not ids:
            raise ValueError("SOURCE_STOP original local nest source has no published image files")
        def classify(z):
            lower=z["original_publisher_file_name"].casefold()
            if "ortho" in lower or "mosaic" in lower:return "CANDIDATE_ORTHOMOSAIC_LABELED"
            if "tile" in lower:return "CANDIDATE_IMAGE_TILE_LABELED"
            return "UNSPECIFIED_IMAGE_FRAME_FILENAME"
        classes=Counter(classify(x) for x in imgs)
        prefixes=Counter(
            "/".join(x["original_archive_relative_path"].split("/")[:-1])
            for x in imgs)
        groups[site]={
            "original_image_count":len(imgs),
            "original_tiff_source_file_class_labels":dict(sorted(classes.items())),
            "original_nested_publisher_directory_tiff_counts":dict(sorted(prefixes.items())),
            "source_original_image_paths_and_IDs":[{
                "path":x["original_archive_relative_path"],
                "publisher_original_file_id":x["original_publisher_archive_id"],
                "file_class_from_name_only":classify(x),
            } for x in imgs],
            "all_original_species_nest_points_observed_in_one_same_UAV_footprint_verified":False,
            "actual_imagery_years_extracted":False,
            "source_original_georeferenced_TIFF_bounds_read":False,
        }
    return {
      "status":"BAS_HART_2019_20_SOURCE_IMAGERY_FRAME_METADATA_V23",
      "original_full_publisher_TIFF_n":len(image_files),
      "source_original_four_multitaxon_site_TIFF_n":sum(r["original_image_count"] for r in groups.values()),
      "site_source_imagery":groups,
      "verified_common_source_image_mask_for_all_compared_taxa":False,
      "original_UAV_image_data_pixels_loaded":False,
      "biological_nest_point_outcomes_opened":0,
      "independently_replicated_island_species_interaction_test_performed":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result={"status":"HOLD_BAS_HART_IMAGERY_SOURCE_V23"}
    try:
        source=json.loads(a.manifest.read_text(encoding="utf-8"))
        result=inventory_original_imagery(source)
        result["original_source_manifest_local_SHA256"]=hashlib.sha256(a.manifest.read_bytes()).hexdigest()
    except Exception as e:
        result["error_type"]=type(e).__name__
        result["error"]=str(e)[:600]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({**{k:v for k,v in result.items() if k!="site_source_imagery"},
        "source_four_locality_original_tiff_paths":{
            k:v["source_original_image_paths_and_IDs"][:70]
            for k,v in result.get("site_source_imagery",{}).items()}},ensure_ascii=False))
    if result["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
