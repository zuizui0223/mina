from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results" / "PALMER_PHENOTYPE_REASSEMBLY_RESULT_V1.json"


def _read() -> dict[str, object]:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_palmer_reassembly_result_is_bound_to_single_execution():
    result = _read()
    execution = result["execution"]

    assert result["contract_id"] == "mina-palmer-phenotype-reassembly-v1"
    assert result["contract_merge_sha"] == (
        "7b7e96d29938aa08581f2da814e07bf66e2c16a1"
    )
    assert execution["workflow_run_id"] == 36535873528
    assert execution["run_attempt"] == 1
    assert execution["artifact_id"] == 11018646322
    assert execution["artifact_digest"] == (
        "sha256:537d0c626bb182dcbafb4554c9371d6b75e71777ec74291d03051795b6a22cd9"
    )
    assert execution["result_sha256"] == (
        "852f3280b2b5116b63952355343de6b1c4eda12beeb683a5317cd34ea8df2367"
    )


def test_assemblage_scale_island_signal_is_compositional():
    assemblage = _read()["assemblage_scale"]

    assert assemblage["naive_pooled_morphology_gain"] > 0
    assert assemblage["species_layer_gain"] > assemblage["naive_pooled_morphology_gain"]
    assert assemblage["species_conditioned_morphology_gain"] < 0


def test_structural_morphology_is_more_detectable_within_year_than_across_years():
    structural = _read()["structural_morphology_persistence"]

    assert structural["chance_balanced_accuracy"] == 1.0 / 3.0
    assert structural["mean_within_year_balanced_accuracy"] == 0.44823749187784273
    assert structural["mean_cross_year_balanced_accuracy"] == 0.34237329434697855
    assert structural["persistence_gap"] == 0.10586419753086418
    assert (
        structural["mean_within_year_balanced_accuracy"]
        > structural["mean_cross_year_balanced_accuracy"]
    )
    assert (
        abs(
            structural["mean_cross_year_balanced_accuracy"]
            - structural["chance_balanced_accuracy"]
        )
        < 0.02
    )


def test_pairwise_structural_island_contrasts_reverse_across_years():
    reversals = _read()["within_adelie_existing"]["pairwise_island_sign_reversals"]

    assert reversals["bill_length"] == "3/3"
    assert reversals["bill_depth"] == "3/3"
    assert reversals["flipper_length"] == "2/3"


def test_isotopes_remain_secondary_and_show_little_persistence_gap():
    isotopes = _read()["isotopic_niche_sensitivity"]

    assert isotopes["role"].startswith("secondary sensitivity")
    assert isotopes["persistence_gap"] < 0.03
    assert abs(
        isotopes["mean_cross_year_balanced_accuracy"]
        - isotopes["chance_balanced_accuracy"]
    ) < 0.02


def test_ecological_result_does_not_claim_adaptation_or_mechanism():
    result = _read()
    unsupported = result["ecological_interpretation"]["not_supported"]
    position = result["manuscript_position"]

    assert "local adaptation to individual Palmer islands" in unsupported
    assert "individual phenotypic plasticity" in unsupported
    assert "a causal snow, habitat, competition, or foraging mechanism" in unsupported
    assert position["ecological_paper_supported"] is True
    assert position["method_paper_positioning"] is False
    assert position["paper1_ecosphere_modified"] is False
    assert position["paper2_macroecology_modified"] is False
