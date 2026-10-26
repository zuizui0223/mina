"""Original publisher nest coordinate QA, no model outcomes."""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from validate_bas_hart_original_multiisland_nest_points_v20 import (
    source_csv_points, select_original_files, EXACT_SOURCE_FILES
)


def test_independent_bird_nest_point_csv_coordinates_are_valid_utm_and_real_ids():
    raw=b"nest_number,lat,lon\n1,-58.2,-26.5\n2,-58.2001,-26.5001\n"
    xy,qa=source_csv_points(raw,{"source_original_locality":"Ashen_Hills","taxon":"ADELIE"})
    assert qa["original_row_count"]==2
    assert qa["unique_original_nest_number_label_count"]==2
    assert qa["source_original_crs"] if "source_original_crs" in qa else qa["original_SSI_coord_reference"]=="EPSG:4326"
    assert qa["source_projected_coordinate_reference"]=="EPSG:32726"
    assert qa["source_exact_duplicate_projected_coordinates_within_file_n"]==0
    assert np.isfinite(xy).all()
    assert 100000<xy[0,0]<900000


def test_duplicate_original_ID_or_outside_SSI_is_a_source_stop_not_pseudo_data():
    raw=b"nest_number,lat,lon\n1,-58,-26\n1,-58.001,-26.001\n"
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        source_csv_points(raw,{"taxon":"ADELIE"})
    bad=b"nest_number,lat,lon\n1,-77,150\n"
    with pytest.raises(ValueError,match="GEOMETRY_STOP"):
        source_csv_points(bad,{"taxon":"ADELIE"})


def test_coordinate_duplicates_are_audited_not_silently_reassigned():
    raw=b"nest_number,lat,lon\n1,-58,-26\n2,-58,-26\n3,-58.0001,-26.0001\n"
    pts,qa=source_csv_points(raw,{"taxon":"ADELIE"})
    assert qa["source_exact_duplicate_projected_coordinates_within_file_n"]==1
    assert len(pts)==3


def test_locked_ten_publisher_file_paths_are_not_outcome_selected():
    from validate_bas_hart_original_multiisland_nest_points_v20 import MANIFEST_STATUS
    manifest=[]
    for locality,names in EXACT_SOURCE_FILES.items():
        for name in names:
            manifest.append({
                "top_level_source_locality_folder":locality,
                "original_archive_relative_path":f"{locality}/coordinates/{name}",
                "original_publisher_file_name":name,
                "original_source_file_type":"csv",
                "source_file_url_https":
                     "https://ramadda.data.bas.ac.uk/repository/entry/get/"+name+"?entryid=original",
            })
    for i in range(154):
        manifest.append({
            "top_level_source_locality_folder":"Zavodovski",
            "original_archive_relative_path":f"Zavodovski/files/{i}.tif",
            "original_publisher_file_name":f"{i}.tif",
            "original_source_file_type":"tif",
        })
    m={"status":MANIFEST_STATUS,"original_filename_inventory_total":164,
       "original_all_file_metadata_only":manifest}
    selected=select_original_files(m)
    assert len(selected)==10
    assert len({x["source_original_locality"] for x in selected})==4
    assert not any("ZAVO_2022_Chinstrap" in x["original_archive_relative_path"] for x in selected)
