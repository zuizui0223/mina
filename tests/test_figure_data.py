import json
from pathlib import Path

from mina.figure_data import _figure3_count_error, _figure3_hierarchy, _figure3_mechanisms


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


def test_hierarchy_figure_data_matches_frozen_receipts():
    h=_receipt("PALMER_HIERARCHICAL_VARIABILITY_RESULT_V1.json")
    a=_receipt("PALMER_HIERARCHY_COMPONENT_COUNT_AUDIT_RESULT_V1.json")
    raw,pairwise=_figure3_hierarchy(h,a)
    primary=raw[0]
    assert abs(primary["beta_within"]-1.0737035331938372)<1e-12
    assert abs(primary["beta_among"]-1.0112310830110414)<1e-12
    assert abs(primary["beta_total"]-1.0857623867043855)<1e-12
    assert abs(primary["within_log_beta_share"]-0.8642664462053955)<1e-12
    assert all(row["beta_within"]>row["beta_among"] for row in raw)

    labels={
        "Raw abundance": "raw_abundance",
        "Detrended log1p": "linear_detrended_log1p",
        "Annual log1p growth": "annual_log1p_growth",
    }
    for row in pairwise:
        frozen=a["pairwise_mean_correlation"][labels[row["analysis"]]]
        assert abs(row["among_islands"]-frozen["among_islands"])<1e-12
        for island in ("COR","HUM","LIT"):
            assert abs(row[island]-frozen[island])<1e-12
            assert row[island] < row["among_islands"]



def test_hierarchy_count_error_figure_data_matches_receipt():
    r=_receipt("PALMER_HIERARCHY_COUNT_ERROR_NULL_RESULT_V1.json")
    rows=_figure3_count_error(r)
    assert len(rows)==3
    by={row["error_model"]:row for row in rows}
    assert abs(by["poisson"]["one_sided_p"]-9.99990000099999e-06)<1e-15
    assert abs(by["gamma_poisson_cv10"]["one_sided_p"]-9.99990000099999e-06)<1e-15
    assert abs(by["gamma_poisson_cv20"]["one_sided_p"]-0.44753552464475355)<1e-12
    assert by["gamma_poisson_cv20"]["null_mean_beta_within"] > by["gamma_poisson_cv20"]["observed_beta_within"]
    assert by["gamma_poisson_cv10"]["null_q975_log_beta_contrast"] < by["gamma_poisson_cv10"]["observed_log_beta_contrast"]
