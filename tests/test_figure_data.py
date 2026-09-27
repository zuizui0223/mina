import json
from pathlib import Path

from mina.figure_data import _figure3_mechanisms


def _receipt(name):
    root=Path(__file__).resolve().parents[1]/"results"
    return json.loads((root/name).read_text())


def test_mechanism_audit_preserves_frozen_directions():
    r={
        "seaice":_receipt("PALMER_SEAICE_HABITAT_MECHANISM_RESULT_V1.json"),
        "timescale":_receipt("PALMER_SEAICE_TIMESCALE_SEPARATION_RESULT_V1.json"),
        "weather":_receipt("PALMER_WEATHER_X_HABITAT_MECHANISM_RESULT_V2.json"),
        "colony":_receipt("PALMER_COLONY_NETWORK_EROSION_RESULT_V1.json"),
        "large":_receipt("PALMER_LARGE_BREEDING_GROUP_THRESHOLD_RESULT_V1.json"),
        "neff_perm":_receipt("PALMER_NEFF_YEAR_BLOCK_PERMUTATION_RESULT_V1.json"),
    }
    rows=_figure3_mechanisms(r)
    by={row["test"]:row for row in rows}
    assert by["Annual sea-ice duration"]["direction_matches"] is False
    assert by["Five-year sea-ice duration"]["relative_error_reduction"] < 0
    assert by["October snowfall x habitat"]["direction_matches"] is False
    assert by["Effective colony number"]["direction_matches"] is True
    assert by["Effective colony number"]["relative_error_reduction"] > 0
    assert by["Effective colony number"]["decision_supported"] is False
    assert abs(by["Effective colony number"]["permutation_p"]-0.2622368881555922)<1e-12
    assert by[">50-pair group count"]["direction_matches"] is False
    assert by[">50-pair group count"]["relative_error_reduction"] > 0


def test_synthesis_v4_includes_spatial_boundary():
    from mina.synthesis import build
    root=Path(__file__).resolve().parents[1]/"results"
    x=build(root)
    spatial=x["local_colony_state"]["external_spatial_triangulation"]
    assert x["synthesis_id"].endswith("-v4")
    assert spatial["phenomenon_level_convergence"] is True
    assert spatial["identifier_level_validation"] is False


def test_synthesis_v4_locks_structured_neff_nulls():
    from mina.synthesis import build
    root=Path(__file__).resolve().parents[1]/"results"
    x=build(root)
    n=x["local_colony_state"]["effective_colony_number"]
    assert n["predictive_supported_after_uncertainty"] is False
    assert abs(n["predictive_gain_permutation_p"]-0.2622368881555922)<1e-12
    assert n["circular_shift"]["retained_against_both"] is True
    assert n["circular_shift"]["independent_island_p"]<1e-4
    assert abs(n["circular_shift"]["joint_persistent_islands_exact_p"]-(1/416))<1e-12
    assert max(
        n["circular_coupling"]["poisson_p_ge_observed"],
        n["circular_coupling"]["gamma_poisson_cv10_p_ge_observed"],
        n["circular_coupling"]["gamma_poisson_cv20_p_ge_observed"],
    )<0.01
