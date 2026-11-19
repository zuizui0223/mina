"""Prevent source-origin / sighting / confirmed breeding category mistakes."""
from __future__ import annotations
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "beaufort_origin", ROOT / "scripts" / "audit_beaufort_origin_graph.py"
)
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)


def test_all_known_cross_site_evidence_is_sighting_not_breeding():
    report = A.audit()
    assert report["evidence_edges_are_visits_not_breeding"]
    assert all(
        edge["first_breeding_confirmed"] is False
        for edge in report["evidence_edges_are_visits_not_breeding"]
    )
    assert not report["zero_confirmations_means_zero_true_events"]


def test_unresolved_beaufort_origin_never_becomes_natal_south():
    report = A.audit()
    edges = report["evidence_edges_are_visits_not_breeding"]
    north = [e for e in edges if e["destination"] == "BEAU_NORTH"]
    assert any("UNVERIFIED" in e["source"] for e in north)
    assert all(
        e.get("source_main_vs_north_mark_identity_verified", False) is False
        for e in north
    )


def test_no_unlicensed_source_capacity_rescue():
    report = A.audit()
    for claim, result in report["candidate_claims"].items():
        assert result["decision"] == "HOLD_MISSING_REQUIRED_EVIDENCE", claim
        assert len(result["missing_fields"]) >= 1
    assert report["capacity_causes_network_rewiring"] == "NOT_TESTED"
    assert report["newly_opened_individual_resight_rows"] == 0
    assert report["paper_189_frozen_science_untouched"]
    assert report["pr_142_locked_protocol_untouched"]


def test_ice_free_observation_does_not_imply_pre_1995_absence_or_ice_recession():
    o = A.audit()["structure_only_support"]
    assert o["north_ice_free_beach_at_1995_visit"]
    assert o["north_subfossil_colony_deposits_reported"]
    assert not o["verified_north_absence_with_survey_effort_before_1994"]
    assert not o["northern_beach_ice_free_suitability_series_before_1994"]


def test_declining_main_does_not_falsify_local_density_pressure():
    o = A.audit()["structure_only_support"]
    assert o["south_main_declined_over_1981_2000_trend"]
    assert not o["local_main_colony_density_at_1995_colonization_timing"]
