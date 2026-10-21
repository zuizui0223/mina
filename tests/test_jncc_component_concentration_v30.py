"""Synthetic only, JNCC comparative count outcomes not used in fixture."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import model_jncc_component_concentration_v30 as v
import pytest

def test_exact_finite_thinning_correction_and_temporal_turnover():
    got=v.component_effect([5,5,0],[9,1,0],[2000]*3,[2018]*3)
    assert got["late_null_expected_simpson"]==pytest.approx(.55)
    assert got["recent_simpson"]==pytest.approx(.82)
    assert got["finite_count_corrected_excess_concentration"]==pytest.approx(.27)
    assert got["declined"] is False
    assert got["site_share_total_variation"]==pytest.approx(.4)
    z=v.component_effect([10,0,0],[0,10,0],[2000]*3,[2018]*3)
    assert z["site_share_total_variation"]==pytest.approx(1.)
    assert z["finite_count_corrected_excess_concentration"]==pytest.approx(0)

def test_fractional_adjusted_counts_are_never_rounded():
    assert v.exact_count("0")==0
    assert v.exact_count("100.0")==100
    assert v.exact_count("100.5") is None
    assert v.exact_count("1.0e2")==100
    assert v.exact_count("") is None
    assert v.exact_count("NA") is None
    assert v.exact_count("-3") is None

def test_low_positive_total_stops_only_that_panel():
    assert v.component_effect([10,0,0],[0,1,0],[2000]*3,[2020]*3) is None

def test_source_overlap_parent_named_component_normalization():
    assert v.normalize_name("  Skomer   Island  ")=="skomer island"
    assert v.MIN_STRUCT_PANELS==100
    assert v.MIN_DECLINE_SPECIES==6

def test_early_zero_is_not_imputed_and_proportional_null_not_raw_change():
    d=v.component_effect([90,10,0],[5,5,0],[2000]*3,[2018]*3)
    assert d["declined"]
    assert d["finite_count_corrected_excess_concentration"]<0
    assert d["effective_components_recent"]>d["effective_components_early"]
