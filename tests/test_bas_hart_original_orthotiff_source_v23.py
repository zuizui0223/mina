"""Original Hart orthotiff file inventory is not an imagery survey footprint."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))

from audit_bas_hart_original_orthotiff_source_v23 import inventory_original_imagery,LOCALITIES


def records():
    files=[]
    # Preserve published exact total across 132 TIFF and 32 CSV.
    for k,name in enumerate(LOCALITIES):
        for j in range(30):
            fn=f"{name}_{j}.tif"
            files.append({
                "original_source_file_type":"tif",
                "top_level_source_locality_folder":name,
                "original_archive_relative_path":f"{name}/images/{fn}",
                "original_publisher_file_name":fn,
                "original_publisher_archive_id":f"{k}-{j}"
            })
    for j in range(12):
        files.append({
            "original_source_file_type":"tif",
            "top_level_source_locality_folder":"Zavodovski",
            "original_archive_relative_path":f"Zavodovski/tiles/z{j}.tif",
            "original_publisher_file_name":f"z{j}.tif",
            "original_publisher_archive_id":f"z-{j}"
        })
    for j in range(32):
        files.append({
            "original_source_file_type":"csv",
            "top_level_source_locality_folder":"Zavodovski",
            "original_archive_relative_path":f"Zavodovski/x{j}.csv",
            "original_publisher_file_name":f"x{j}.csv",
            "original_publisher_archive_id":f"c-{j}"
        })
    assert len(files)==164
    return {
        "status":"VERIFIED_ORIGINAL_SOURCE_FILES_PUBLISHER_SUMMARY_COUNT_DISCREPANCY",
        "original_all_file_metadata_only":files
    }


def test_fixed_original_four_sites_do_not_become_verified_shared_imagery():
    r=inventory_original_imagery(records())
    assert r["original_full_publisher_TIFF_n"]==132
    assert r["source_original_four_multitaxon_site_TIFF_n"]==120
    assert set(r["site_source_imagery"])==set(LOCALITIES)
    assert r["verified_common_source_image_mask_for_all_compared_taxa"] is False
    assert r["original_UAV_image_data_pixels_loaded"] is False


def test_missing_one_original_source_file_stops_not_as_species_absence():
    bad=records()
    bad["original_all_file_metadata_only"].pop()
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        inventory_original_imagery(bad)
