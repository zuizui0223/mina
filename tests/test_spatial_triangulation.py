from mina.spatial_triangulation import build


def test_external_spatial_triangulation_is_bounded():
    x=build(
        "results/PALMER_COLONY_NETWORK_EROSION_RESULT_V1.json",
        "external/TORGERSEN_SPATIAL_EVIDENCE_V1.json",
    )
    assert x["decision"]["phenomenon_level_spatial_convergence"] is True
    assert x["decision"]["identifier_level_validation"] is False
    assert x["decision"]["causal_fragmentation_validated"] is False
    assert x["external_torgersen_spatial"]["active_footprint_fraction"] < 0.25
    assert x["external_torgersen_spatial"]["south_extinction_fraction"] > x["external_torgersen_spatial"]["north_extinction_fraction"]
    assert x["internal_colony_network"]["effective_colony_beta"] > 0
    assert x["internal_colony_network"]["heldout_mse_gain"] > 0
