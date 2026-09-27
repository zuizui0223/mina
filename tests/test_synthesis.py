from pathlib import Path

from mina.synthesis import build


def test_frozen_synthesis_matches_postdiagnostic_receipts():
    root = Path(__file__).resolve().parents[1] / "results"
    x = build(root)

    assert x["synthesis_id"] == "mina-palmer-island-ecology-synthesis-v3"
    assert abs(
        x["five_island_decline"]["pc1_variance_fraction"]
        - 0.9640284642946518
    ) < 1e-12

    mechanisms = x["prospective_mechanism_tests"]
    assert mechanisms["annual_seaice_duration"]["supported"] is False
    assert mechanisms["five_year_seaice_duration"]["supported"] is False
    assert mechanisms["october_snow_x_habitat"]["supported"] is False

    neff = x["local_colony_state"]["effective_colony_number"]
    assert neff["beta"] > 0
    assert neff["robust_predictive_gain"] is False
    assert neff["conditional_association_survives_fixed_diagnostics"] is True
    assert abs(
        neff["year_block_permutation"]["gain_p"]
        - 0.2622368881555922
    ) < 1e-12
    assert neff["year_block_permutation"]["coefficient_p"] < 0.001
    assert all(
        p < 0.01
        for p in neff["mechanical_coupling"]["coupled_beta_p"].values()
    )

    assert (
        x["local_colony_state"]["external_gt50_group_count"][
            "directional_supported"
        ]
        is False
    )
    assert (
        x["local_colony_state"]["external_spatial_triangulation"][
            "identifier_level_validation"
        ]
        is False
    )
    assert x["submission_status"]["jae"] == "hold"
