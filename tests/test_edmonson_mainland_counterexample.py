"""Reproduce published Edmonson pair counts and detect inconsistent percentage."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "edmonson_control",
    ROOT / "scripts" / "audit_edmonson_mainland_counterexample.py",
)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def test_table_1_absolute_counts_and_mass_balance():
    r = M.audit()
    assert r["2017_total"] == 2547
    assert r["2019_total"] == 2506
    assert r["coastal_absolute_change"] == -108
    assert r["higher_absolute_change"] == 67
    assert r["total_absolute_change"] == -41
    assert r["coastal_absolute_change"] + r["higher_absolute_change"] == -41


def test_table_1_hill_growth_percent_denominator_error():
    r = M.audit()
    assert abs(r["higher_fraction_change_start_denominator"] - 67 / 576) < 1e-12
    assert abs(r["higher_fraction_change_start_denominator"] - .11631944444444) < 1e-11
    assert r["published_hill_percent_mismatch"]
    assert r["published_hill_percent_matches_final_denominator"]


def test_island_crossing_and_individual_movement_not_inferred():
    r = M.audit()
    assert r["location_class"] == "continental_antarctic_coastal_headland_not_island"
    assert r["inferences"]["same_individuals_moved_coastal_to_hill"] == "NOT_OBSERVED"
    assert r["inferences"]["cross_island_emigration_effect"] == "NOT_IDENTIFIED"
    assert r["inferences"]["island_vs_continent_effect"] == "NOT_IDENTIFIED"
    assert r["status"].endswith("DESCRIPTIVE_CONTROL_ONLY")


def test_concentration_direction_and_compensation_not_transfers():
    r = M.audit()
    assert abs(r["higher_gain_over_coastal_loss"] - 67 / 108) < 1e-12
    assert r["inverse_simpson_E2_2019"] > r["inverse_simpson_E2_2017"]
    assert r["coastal_share_2019"] < r["coastal_share_2017"]
