"""Exact 5-island source comparison; no pollution with causal claims."""
import importlib.util
import math
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/audit_palmer_aspa113_island_context_v1.py"

def load():
    spec=importlib.util.spec_from_file_location("aspa113_context",SCRIPT)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_official_vs_palmer_source_lineage_and_zeros():
    m=load()
    x=m.audit()
    assert x["palmer_count_roster_1991_2017"]=={"sites":5,"years":27,"records":135}
    assert x["litchfield_official_overlap_1991_2012"]["matched"]==20
    assert [d["year"] for d in x["litchfield_official_overlap_1991_2012"]["discrepancies"]]==[1998,1999]
    assert x["palmer_LIT_explicit_zero_2007_2017"] is True
    assert x["palmer_comparison_islands_2017_positive"]==4
    assert [z["four_other_islands_sum"] for z in x["selected_count_years"]]==[6192,913,847,451,140]
    assert x["design_stop"]["island_mediator_or_diD_identifiable"] is False
    assert x["point_buffer_geometry"]["point_buffers_are_not_island_polygons"] is True

def test_overlapping_vegetation_buffers_are_not_independent_islands():
    m=load()
    x=m.audit()
    d={(z["site_a"],z["site_b"]):z for z in x["point_buffer_geometry"]["distance_rows"]}
    assert d["HUMB","LITC"]["distance_km"]<1.0
    assert d["LITC","TORG"]["distance_km"]<1.0
    assert d["HUMB","LITC"]["overlap_500m_point_buffers"]
    assert d["LITC","TORG"]["overlap_500m_point_buffers"]
    assert x["point_buffer_geometry"]["500m_overlapping_pairs"]>=2
    habitats={z["source_site_id"]:z for z in x["static_map_context"]}
    assert habitats["LITC"]["500m_vegetation_features"]==27
    assert habitats["LITC"]["2000m_vegetation_features"]==104
    assert all(z["500m_vegetation_features"]>=0 for z in habitats.values())
