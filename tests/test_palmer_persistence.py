from __future__ import annotations

import json
from pathlib import Path

import pytest

from mina.palmer import STRUCTURAL, nearest_centroid_loyo
from mina.palmer_persistence import (
    leave_one_year_out,
    persistence_summary,
    within_year_leave_one_out,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "PALMER_PHENOTYPE_REASSEMBLY_PAPER_V1.json"


def _rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    islands = ("Biscoe", "Dream", "Torgersen")
    years = ("PAL0708", "PAL0809", "PAL0910")
    sexes = ("FEMALE", "MALE")
    for year_index, year in enumerate(years):
        for island_index, island in enumerate(islands):
            for sex_index, sex in enumerate(sexes):
                for replicate in range(4):
                    base = 10.0 * island_index
                    # Make within-year clusters clear but shift their positions
                    # between years so the persistence test is nontrivial.
                    shift = 4.0 * year_index * ((island_index % 2) - 0.5)
                    rows.append(
                        {
                            "Species": "Adelie Penguin (Pygoscelis adeliae)",
                            "Island": island,
                            "studyName": year,
                            "Sex": sex,
                            "Culmen Length (mm)": str(
                                40.0 + base + shift + 2.0 * sex_index + 0.1 * replicate
                            ),
                            "Culmen Depth (mm)": str(
                                16.0 + 0.5 * base - shift + sex_index + 0.05 * replicate
                            ),
                            "Flipper Length (mm)": str(
                                180.0 + 1.5 * base + shift + 3.0 * sex_index + 0.2 * replicate
                            ),
                            "Body Mass (g)": str(3500 + 100 * island_index),
                            "Delta 15 N (o/oo)": str(8.0 + island_index + 0.1 * year_index),
                            "Delta 13 C (o/oo)": str(-25.0 + island_index - 0.1 * year_index),
                        }
                    )
    return rows


def test_contract_freezes_independent_ecological_lane_without_touching_paper1_or_paper2():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert contract["status"] == (
        "post_outcome_extension_frozen_before_within_year_transfer_analysis"
    )
    assert contract["relationship_to_mina_program"]["paper1_ecosphere_v1_modified"] is False
    assert contract["relationship_to_mina_program"]["paper2_macroecology_modified"] is False
    assert contract["new_extension"]["classifier"] == (
        "nearest centroid after training-only sex centering and training-only feature scaling"
    )
    assert contract["new_extension"]["no_model_tuning"] is True
    assert contract["new_extension"]["no_alternate_classifier_after_result"] is True
    assert contract["new_extension"]["no_trait_subset_search"] is True


def test_cross_year_implementation_matches_existing_frozen_nearest_centroid_definition():
    rows = _rows()

    old = nearest_centroid_loyo(rows, STRUCTURAL)
    new = leave_one_year_out(rows, STRUCTURAL)

    assert len(old["folds"]) == len(new) == 3
    for previous, current in zip(old["folds"], new):
        assert current["heldout_year"] == previous["heldout_year"]
        assert current["n"] == previous["n"]
        assert current["balanced_accuracy"] == pytest.approx(
            previous["balanced_accuracy"],
            abs=1e-15,
        )


def test_within_year_leave_one_out_is_deterministic_and_complete():
    rows = _rows()
    first = within_year_leave_one_out(rows, STRUCTURAL)
    second = within_year_leave_one_out(rows, STRUCTURAL)

    assert first == second
    assert len(first) == 3
    assert all(row["n"] == 24 for row in first)
    assert all(0.0 <= row["balanced_accuracy"] <= 1.0 for row in first)


def test_persistence_summary_reports_same_metric_and_positive_gap_on_fixture():
    summary = persistence_summary(_rows(), STRUCTURAL)

    assert summary.n_complete == 72
    assert summary.chance_balanced_accuracy == pytest.approx(1.0 / 3.0)
    assert 0.0 <= summary.mean_within_year_balanced_accuracy <= 1.0
    assert 0.0 <= summary.mean_cross_year_balanced_accuracy <= 1.0
    assert summary.persistence_gap == pytest.approx(
        summary.mean_within_year_balanced_accuracy
        - summary.mean_cross_year_balanced_accuracy
    )
