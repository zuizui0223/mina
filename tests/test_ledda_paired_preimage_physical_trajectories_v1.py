"""Synthetic-only trajectory tests: no true colony habitat, survival or recruitment."""
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).resolve().parents[1] / "scripts/audit_ledda_paired_preimage_physical_trajectories_v1.py"
spec=importlib.util.spec_from_file_location("paired_physical",PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def row(t,p,q):
    return {
        "time_index":t,
        "composite_start_yyyymmdd":20110101+15*t,
        "original_any_class4":p,
        "alternative_any_class4":q,
        "original_class4_fraction":float(p),
        "alternative_class4_fraction":float(q),
    }


def test_trajectories_are_paired_same_time_and_not_a_causal_effect():
    t=list(m.primary.FROZEN_YEAR[2011]["preimage_indices"])
    a=[False,True,True,False,False,True,False,False,False]
    b=[True,True,False,False,True,True,False,False,True]
    assert len(t)==len(a)==9
    d=m.trajectory_readout(2011,[row(i,p,q) for i,p,q in zip(t,a,b)])
    assert d["temporal_state_counts"]=={
        "both_class4_any":2,
        "only_original_class4_any":1,
        "only_alternative_class4_any":3,
        "neither_class4_any":3
    }
    assert d["original_site"]["number_composites_any_class4"]==3
    assert d["alternative_site"]["number_composites_any_class4"]==5
    assert d["original_site"]["longest_consecutive_class4_composites"]==2
    assert d["original_site"]["trailing_consecutive_no_class4_composites"]==3
    assert d["alternative_site"]["trailing_consecutive_no_class4_composites"]==0
    assert d["original_site"]["last_preimage_class4_detected"] is False
    assert d["alternative_site"]["last_preimage_class4_detected"] is True
    assert d["temporal_any_ice_jaccard"] == pytest.approx(2/6)
    assert not d["causal_penguin_conclusion_available"]


def test_no_ice_both_sites_jaccard_undefined():
    t=list(m.primary.FROZEN_YEAR[2014]["preimage_indices"])
    d=m.trajectory_readout(2014,[row(i,False,False) for i in t])
    assert d["temporal_any_ice_jaccard"] is None
    assert d["original_site"]["trailing_consecutive_no_class4_composites"]==11
    assert d["alternative_site"]["trailing_consecutive_no_class4_composites"]==11


def test_mismatched_time_indices_fail_closed():
    y=2011
    t=list(m.primary.FROZEN_YEAR[y]["preimage_indices"])
    def fake(year,omit=None):
        ids=t + [m.primary.FROZEN_YEAR[year]["overlap_t"]]
        if omit is not None: ids.remove(omit)
        return {"year":year,"composite_records":[{
            "time_index":i,"composite_start_yyyymmdd":20110101+15*i,
            "radius_summaries_km":{"3":{"n_class_valid":10,"n_cells_spatial_mask":10,
                                         "n_fastice_class4":0,
                                         "fraction_fastice_over_valid_cells":0.0,
                                         "n_edge_classes_5_or_6":0}}
        } for i in ids]}
    with pytest.raises(ValueError,match="missing"):
        m.summaries_for_radius(y,fake(y),fake(y,omit=t[0]),3)


def test_published_centroid_and_year_gate_immutable():
    assert m.secondary.is_frozen_plan()
    assert m.YEARS == (2011,2014)
    assert m.RADII == (1,3,5)
    with pytest.raises(ValueError):
        m.compare_year(2010,{}, {})
