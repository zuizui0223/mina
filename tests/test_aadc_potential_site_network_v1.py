"""Deterministic original potential-site graph tests, no bird outcomes."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))

from build_aadc_potential_site_network_v1 import site_point_network


def sample():
    return [
        {"site_id":"A","source_class":"island","x":0.0,"y":0.0},
        {"site_id":"B","source_class":"island","x":1000.0,"y":0.0},
        {"site_id":"C","source_class":"continent","x":10000.0,"y":0.0},
        {"site_id":"D","source_class":"continent","x":60000.0,"y":0.0},
    ]


def test_radius_counts_and_source_class_do_not_mean_same_island():
    rows,report=site_point_network(sample(),{"A","C"})
    d={r["geog_site_id"]:r for r in rows}
    assert report["author_original_geographic_site_total"]==4
    assert report["source_geographic_site_classes"]=={"island":2,"continent":2}
    assert report["reported_nearest_same_class_is_within_same_physical_island"] is False
    assert d["A"]["nearest_any_other_source_site_point_m"]==pytest.approx(1000)
    assert d["A"]["nearest_same_author_class_site_point_m"]==pytest.approx(1000)
    assert d["A"]["nearest_other_author_class_site_point_m"]==pytest.approx(10000)
    assert d["B"]["nearest_other_author_class_site_point_m"]==pytest.approx(9000)
    assert d["C"]["nearest_same_author_class_site_point_m"]==pytest.approx(50000)
    assert d["C"]["nearest_other_author_class_site_point_m"]==pytest.approx(9000)
    assert d["A"]["other_original_potential_site_centres_within_2km"]==1
    assert d["A"]["other_original_potential_site_centres_within_10km"]==2
    assert d["B"]["other_original_potential_site_centres_within_10km"]==2
    assert d["D"]["other_original_potential_site_centres_within_50km"]==1
    assert report["network_descriptive_summaries"]["2021_2025_shared_site_ids"]["unique_original_site_ids"]==2
    assert report["P_A_NR_or_breeding_count_outcomes_opened"]==0


def test_one_site_has_null_neighbors_not_zero_distance():
    rows,report=site_point_network(
        [{"site_id":"Z","source_class":"island","x":0.0,"y":0.0}],set())
    assert rows[0]["nearest_any_other_source_site_point_m"] is None
    assert rows[0]["nearest_same_author_class_site_point_m"] is None
    assert rows[0]["nearest_other_author_class_site_point_m"] is None
    assert rows[0]["other_original_potential_site_centres_within_50km"]==0
    assert report["network_descriptive_summaries"]["all_2025"]["nearest_other_potential_site_point_distance_m"] is None


def test_class_and_ID_errors_stop():
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        site_point_network(sample()+[sample()[0]],set())
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        site_point_network([{"site_id":"X","source_class":"unknown","x":0,"y":0}],set())
