"""Synthetic-only geometric partition test, no genuine penguin polygons."""
import sys
from pathlib import Path
import pytest

pytest.importorskip("requests")
pytest.importorskip("shapely")
pytest.importorskip("shapefile")
pytest.importorskip("pyproj")

from shapely.geometry import box, GeometryCollection
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from zavodovski_jointly_corroborated_transition_v18 import evaluate, SHRINK_METERS


def fabricated():
    original_c=box(0,0,4,2)
    original_m=box(10,0,11,1)
    future_c=box(2,0,4,2)
    future_m=original_m.union(box(0,0,2,2))
    direct={
        (2011,"chinstrap"):original_c,
        (2011,"macaroni"):original_m,
        (2011,"cloud"):GeometryCollection(),
        (2016,"chinstrap"):future_c,
        (2016,"macaroni"):future_m,
        (2016,"cloud"):GeometryCollection()
    }
    historic={
        "CHPE":box(0,0,1.6,2),
        "MCPE":box(1.5,0,1.75,2),
        "MIXED":box(1,0,1.5,2)
    }
    return direct,historic


def test_original_mixed_exclusive_partition_recovers_exact_total():
    direct,hist=fabricated()
    r=evaluate(direct,hist,expected_v10_E=1)
    categories=r["exclusive_historic_category_partition_of_X"]
    assert r["mapped_M_gain_m2"] == 4
    assert r["mapped_co_location_X_m2"] == 4
    assert r["jointly_corroborated_T_m2"] == 2
    assert r["T_fraction_of_co_location_X"] == 0.5
    assert categories["A_historic_MIXED"]["area_m2"] == 1
    assert categories["B_historic_MCPE_outside_MIXED"]["area_m2"] == 0.5
    assert categories["C_jointly_CHPE_confirmed"]["area_m2"] == 2
    assert categories["D_not_in_historic_map"]["area_m2"] == 0.5
    assert round(sum(v["fraction_of_X"] for v in categories.values()),6) == 1


def test_buffered_consensus_strictly_shrinks_and_anchors_zero_margin():
    direct,hist=fabricated()
    r=evaluate(direct,hist,expected_v10_E=1)
    b=r["geometric_interior_sensitivity"]
    assert [x["margin_m"] for x in b] == list(SHRINK_METERS)
    assert b[0]["corroborated_map_area_m2"] == 2
    assert all(b[i]["corroborated_map_area_m2"] >= b[i+1]["corroborated_map_area_m2"]
               for i in range(len(b)-1))
    assert b[1]["corroborated_map_area_m2"] <= 2


def test_baseline_mismatch_causes_stop():
    direct,hist=fabricated()
    with pytest.raises(ValueError,match="REPRODUCIBILITY_STOP"):
        evaluate(direct,hist)


def test_clouded_intersection_cannot_be_counted():
    direct,hist=fabricated()
    direct[2011,"cloud"]=box(0,0,1,2)
    r=evaluate(direct,hist,expected_v10_E=1)
    assert r["jointly_corroborated_T_m2"] == 0
    assert r["exclusive_historic_category_partition_of_X"]["A_historic_MIXED"]["area_m2"] == 1
