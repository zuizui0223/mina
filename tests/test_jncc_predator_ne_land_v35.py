"""Synthetic original coordinate-only geographic eligibility tests for V35."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_jncc_predator_ne_land_v35 as a

def test_unique_small_landmass_bridge_never_uses_large_island_as_predator_point():
    labels={
      10:{"status":"INTERIOR","physical_id":0},
      11:{"status":"INTERIOR","physical_id":1},
      12:{"status":"INTERIOR","physical_id":2},
      13:{"status":"COAST_SNAPPED","physical_id":0},
    }
    bridge,s=a.strict_RSPB_landmass_bridge(labels,[1.0,100.0,50000.0])
    assert bridge=={0:10,1:11}
    assert s["large_landmasses_NEVER_as_RSPB_island_status"]
    assert s["RSPB_source_island_point_states"]["COAST_SNAPPED"]==1

def test_ambiguous_two_RSPB_islands_inside_same_coarse_polygon_are_held():
    labels={
      10:{"status":"INTERIOR","physical_id":0},
      11:{"status":"INTERIOR","physical_id":0},
    }
    bridge,s=a.strict_RSPB_landmass_bridge(labels,[11.0])
    assert bridge=={}
    assert s["small_polygons_with_multiple_source_RSPB_lowids_HOLD"]==1

def test_mixed_predator_labels_need_actual_separate_child_landmass_sites():
    parent=("Common Tern","Scotland","A","AON")
    children=[({
      "species":parent[0],"country":parent[1],"master":parent[2],
      "unit":parent[3],"site_id":i
    },{}) for i in [1,2,3]]
    site_states={
      ("Common Tern","Scotland","A","AON",1):{"status":"INTERIOR","physical_id":0},
      ("Common Tern","Scotland","A","AON",2):{"status":"INTERIOR","physical_id":0},
      ("Common Tern","Scotland","A","AON",3):{"status":"INTERIOR","physical_id":1},
    }
    esm={
      10:{"statuses":{"American mink":"1","Brown rat":"1"}},
      11:{"statuses":{"American mink":"0","Brown rat":"0"}},
    }
    s=a.panel_support({parent:children},site_states,{0:10,1:11},esm)
    assert s["mixed_source_island_parent_count"]==1
    assert s["parent_support_categories"]["MIXED_REPORTED_AMERICAN_MINK"]==1
    assert not s["predeclared_within_parent_mixed_island_support_pass"]
    assert s["NO_JNCC_count_magnitudes_opened"]

def test_unresolved_child_blocks_mixed_parent_inference():
    parent=("Atlantic Puffin","Scotland","B","AOB")
    children=[({
      "species":parent[0],"country":parent[1],"master":parent[2],
      "unit":parent[3],"site_id":i
    },{}) for i in [1,2,3]]
    states={
      ("Atlantic Puffin","Scotland","B","AOB",1):{"status":"INTERIOR","physical_id":0},
      ("Atlantic Puffin","Scotland","B","AOB",2):{"status":"INTERIOR","physical_id":1},
      ("Atlantic Puffin","Scotland","B","AOB",3):{"status":"COAST_SNAPPED","physical_id":1},
    }
    esm={
      10:{"statuses":{"American mink":"1","Brown rat":"1"}},
      11:{"statuses":{"American mink":"0","Brown rat":"0"}},
    }
    s=a.panel_support({parent:children},states,{0:10,1:11},esm)
    assert s["parent_support_categories"]["INCOMPLETE_STRICT_SOURCE_CHILD_ISLAND_GEOGRAPHY"]==1
    assert s["mixed_source_island_parent_count"]==0
