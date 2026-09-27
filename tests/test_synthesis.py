from pathlib import Path
from mina.synthesis import build


def test_frozen_synthesis_matches_receipts():
    root=Path(__file__).resolve().parents[1]/"results"
    x=build(root)
    assert x["synthesis_id"].endswith("-v3")
    assert abs(x["five_island_decline"]["pc1_variance_fraction"]-0.9640284642946518)<1e-12
    assert x["prospective_mechanism_tests"]["annual_seaice_duration"]["supported"] is False
    assert x["prospective_mechanism_tests"]["five_year_seaice_duration"]["supported"] is False
    assert x["prospective_mechanism_tests"]["october_snow_x_habitat"]["supported"] is False

    neff=x["local_colony_state"]["effective_colony_number"]
    assert neff["predictive_supported_after_uncertainty"] is False
    assert abs(neff["predictive_gain_permutation_p"]-0.2622368881555922)<1e-12
    assert neff["association_retained"] is True
    assert neff["beta"]>0
    assert neff["coupling"]["poisson_p_ge_observed"]<0.01
    assert neff["coupling"]["gamma_poisson_cv10_p_ge_observed"]<0.01
    assert neff["coupling"]["gamma_poisson_cv20_p_ge_observed"]<0.01

    assert x["local_colony_state"]["external_gt50_group_count"]["directional_supported"] is False
    assert x["local_colony_state"]["external_spatial_triangulation"]["phenomenon_level_convergence"] is True
    assert x["local_colony_state"]["external_spatial_triangulation"]["identifier_level_validation"] is False
    assert x["journal_position"]["jae_submission_ready"] is False
