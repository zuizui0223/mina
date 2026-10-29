"""V53 synthetic original 3-island coastal source point mismatch QA."""
from pathlib import Path
import sys
import numpy as np
import pytest
from shapely.geometry import box
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_paper2_original_coast_disagreement_v53 as a


def test_frozen_original_COAST_ZIP_SHA_and_no_gate_redefinition():
    assert a.COAST_ZIP_SHA=="27b4cd2085b9c845abf7928c336cf82f0d37492bbe2c21522ac4c670750f6cff"
    assert a.GRID_M==30
    assert a.EXPECTED["Hewison_Point"]==(22424,19203)
    assert a.EXPECTED["Ashen_Hills"]==(75255,72903)
    assert a.v51.MIN_INSIDE_SOURCE==.95


def test_outside_points_own_coastline_distances_exact_and_no_snapping():
    land=box(0,0,100,100)
    original=np.array([[50,50],[10,10],[-2,50],[101,25],[110,10]],dtype=float)
    result=a.source_disagreement(original,land)
    assert result["original_unique_original_source_points_n"]==5
    assert result["strict_original_source_on_land_n"]==2
    assert result["strict_original_source_outside_land_n"]==3
    d=result["original_outside_distance_to_own_island_coast_m"]
    assert d["median_m"]==2
    assert d["max_m"]==10
    assert d["le5m"]==2
    assert d["le10m"]==3
    assert d["gt100m"]==0
    assert result["no_original_points_snapped_or_reprojected_to_land"]


def test_20m_original_cartography_discrepancy_not_fit_as_animal_effect():
    original=np.array([[-1,2],[-40,20],[500,500],[20,20]],dtype=float)
    r=a.source_disagreement(original,box(0,0,100,100))
    d=r["original_outside_distance_to_own_island_coast_m"]
    assert d["le5m"]==1
    assert d["le30m"]==1
    assert d["gt100m"]==1
    assert d["distinct_30m_grid_cells_outside_original_land"]==3


def test_all_inside_is_not_imputed_predator_free_or_new_habitat():
    r=a.source_disagreement(np.array([[20.,20.],[30.,30.]]),
                           box(0,0,100,100))
    assert r["original_outside_distance_to_own_island_coast_m"]["source_outside_point_n"]==0
    assert r["original_outside_distance_to_own_island_coast_m"]["median_m"] is None


def test_invalid_original_xy_must_fail_before_source_distance():
    with pytest.raises(ValueError,match="XY_NOT_VALID"):
        a.source_disagreement(np.array([[float("nan"),1.]]),
                             box(0,0,100,100))
