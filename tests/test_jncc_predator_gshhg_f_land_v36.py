"""V36 GSHHG full-resolution source-only geometry and no-bird-outcome gate tests."""
from __future__ import annotations
from pathlib import Path
import sys, io, zipfile
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_jncc_predator_gshhg_f_land_v36 as v36
import audit_jncc_predator_ne_land_v35 as v35

def test_gshhg_source_is_full_resolution_and_hash_pinned():
    assert v36.STEM=="GSHHS_f_L1"
    assert "2.3.7/gshhg-shp-2.3.7.zip" in v36.SOURCE_URL
    assert v36.SOURCE_SHA256=="8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41"
    assert v36.MAX_DOWNLOAD_BYTES<=200_000_000

def test_original_archive_missing_full_resolution_is_stopped():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w") as z:
        z.writestr("GSHHS_l_L1.shp",b"not real shapefile")
    with pytest.raises(ValueError,match="GSHHG_ORIGINAL_F_L1_FILE_MISSING"):
        v36.shapefile_source(buf.getvalue())

def test_geo_bridge_holds_multiple_source_points_per_polygon():
    labels={
      "a":{"status":"INTERIOR","physical_id":0},
      "b":{"status":"INTERIOR","physical_id":0},
      "c":{"status":"INTERIOR","physical_id":1},
      "d":{"status":"COAST_SNAPPED","physical_id":2},
      "e":{"status":"INTERIOR","physical_id":2},
    }
    mapping,qa=v35.strict_RSPB_landmass_bridge(labels,[20.0,10.0,60000.0])
    assert mapping=={1:"c"}
    assert qa["small_polygons_with_multiple_source_RSPB_lowids_HOLD"]==1
    assert qa["large_landmasses_NEVER_as_RSPB_island_status"]

def test_single_same_island_cannot_identify_predator_refuge():
    parent=("Arctic Tern","Scotland","X","AON")
    children=[({"species":parent[0],"country":parent[1],"master":parent[2],"unit":parent[3],"site_id":i}, {}) for i in (1,2,3)]
    keys={(parent[0],parent[1],parent[2],parent[3],i):{"status":"INTERIOR","physical_id":7} for i in (1,2,3)}
    esm={15:{"statuses":{"American mink":"1","Brown rat":"0"}}}
    qa=v35.panel_support({parent:children},keys,{7:15},esm)
    assert qa["mixed_source_island_parent_count"]==0
    assert qa["parent_support_categories"]["ALL_CHILDREN_ONE_RSPB_ISLAND"]==1
    assert qa["NO_JNCC_count_magnitudes_opened"]
