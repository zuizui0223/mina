"""Synthetic no-outcome tests for RSPB island CENTROID candidate, not landmass."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_jncc_rpsb_predator_point_proximity_v35 as v


def test_centroid_nearest_and_competing_points_fixed_without_name_fuzzy():
    assert v.classify_point(50,1200,12)["candidate_lowid"]==12
    assert v.classify_point(50,1200,12)["class"].startswith("UNIQUE_NEAR")
    assert v.classify_point(251,1200,12)["candidate_lowid"] is None
    assert v.classify_point(50,200,12)["class"].startswith("AMBIGUOUS")
    assert v.classify_point(250,750,12)["class"].startswith("AMBIGUOUS")


def test_two_unnamed_candidates_not_strict_gis_physical_landmasses():
    parent=("Arctic Tern","Scotland","invented parent","AON")
    points=[(56.0,-5.0),(56.01,-5.1),(56.02,-5.2)]
    records=[({"lat":lat,"lon":lon}, {}) for lat,lon in points]
    panels={parent:records}
    matches={
       points[0]:v.classify_point(50,1000,1),
       points[1]:v.classify_point(50,1000,2),
       points[2]:v.classify_point(50,1000,2),
    }
    statuses={
       1:{"status_codes":{"American mink":"0","Brown rat":"1"}},
       2:{"status_codes":{"American mink":"1","Brown rat":"0"}},
    }
    a=v.summarize_source_panels(panels,matches,statuses)
    assert a["original_V30_structural_parents"]==1
    assert a["original_JNCC_child_records"]==3
    assert a["original_parent_source_point_support"]["parents_ALL_children_unique_and_at_least_two_distinct_centroid_ids"]==1
    assert a["candidate_mixed_parent_with_different_status_reference_labels"]["American mink"]==1
    assert a["candidate_mixed_parent_with_different_status_reference_labels"]["Brown rat"]==1
    assert a["V32_H2_strict_physical_island_test_ready"] is False
    assert a["JNCC_numeric_site_count_magnitudes_opened"]==0


def test_partial_coastal_point_match_does_not_promote_to_mixed_panel():
    parent=("Arctic Tern","Scotland","invented parent","AON")
    pts=[(50.1,-5),(50.2,-5),(50.3,-5)]
    panels={parent:[({"lat":lat,"lon":lon},{}) for lat,lon in pts]}
    mapping={
        pts[0]:v.classify_point(3,999,1),
        pts[1]:v.classify_point(30,1000,2),
        pts[2]:v.classify_point(500,900,3),
    }
    statuses={1:{"status_codes":{"American mink":"1","Brown rat":"0"}},
              2:{"status_codes":{"American mink":"0","Brown rat":"0"}}}
    result=v.summarize_source_panels(panels,mapping,statuses)
    assert result["original_parent_source_point_support"].get("parents_ALL_children_unique_and_at_least_two_distinct_centroid_ids",0)==0
    assert result["V32_H2_strict_physical_island_test_ready"] is False
