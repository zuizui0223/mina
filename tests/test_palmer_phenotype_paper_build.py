from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.build_palmer_phenotype_paper_v0_1 import build, manuscript_text, _read_result


def test_manuscript_uses_frozen_ecological_result_without_method_reframing():
    text = manuscript_text(_read_result())

    assert "Species sorting creates transient island phenotypes" in text
    assert "+0.38946" in text
    assert "+0.53601" in text
    assert "-0.08375" in text
    assert "0.448" in text
    assert "0.342" in text
    assert "species-sorting and temporal-reassembly interpretation" in text
    assert "methods novelty" not in text.lower()
    assert "ODSP framework" not in text


def test_builder_emits_three_receipt_backed_figure_tables_and_manuscript(tmp_path: Path):
    manifest = build(tmp_path)

    assert manifest["source_result_id"] == "mina-palmer-phenotype-reassembly-result-v1"
    assert manifest["figure_data_files"] == [
        "figure1_assemblage_decomposition.csv",
        "figure2_within_adelie_reassembly.csv",
        "figure3_temporal_persistence.csv",
    ]
    assert manifest["paper1_ecosphere_modified"] is False
    assert manifest["paper2_macroecology_modified"] is False
    assert manifest["method_paper_positioning"] is False

    manuscript = tmp_path / "PALMER_PHENOTYPE_REASSEMBLY_MANUSCRIPT_V0_1.md"
    assert manuscript.is_file()
    assert manifest["manuscript_word_count"] > 1500
    assert manifest["abstract_word_count"] < 300


def test_figure1_separates_species_sorting_from_within_species_morphology(tmp_path: Path):
    build(tmp_path)
    with (tmp_path / "figure1_assemblage_decomposition.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))

    values = {row["contrast"]: float(row["gain"]) for row in rows}
    assert values["morphology_vs_pooled"] == 0.3894565006712757
    assert values["species_vs_pooled"] == 0.5360132625954789
    assert values["morphology_beyond_species"] == -0.08374806363025576


def test_figure2_preserves_small_fixed_effects_and_sign_reversals(tmp_path: Path):
    build(tmp_path)
    with (tmp_path / "figure2_within_adelie_reassembly.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))

    by_trait = {row["trait"]: row for row in rows}
    assert float(by_trait["Bill length"]["fixed_island_partial_r2"]) < 0.02
    assert float(by_trait["Bill depth"]["fixed_island_partial_r2"]) < 0.02
    assert float(by_trait["Flipper length"]["fixed_island_partial_r2"]) < 0.05
    assert int(by_trait["Bill length"]["reversed_pair_count"]) == 3
    assert int(by_trait["Bill depth"]["reversed_pair_count"]) == 3
    assert int(by_trait["Flipper length"]["reversed_pair_count"]) == 2


def test_figure3_preserves_temporal_persistence_gap(tmp_path: Path):
    build(tmp_path)
    with (tmp_path / "figure3_temporal_persistence.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))

    structural = [
        row for row in rows if row["domain"] == "structural_morphology"
    ]
    within = [
        float(row["balanced_accuracy"])
        for row in structural
        if row["validation"] == "within_year_leave_one_out"
    ]
    cross = [
        float(row["balanced_accuracy"])
        for row in structural
        if row["validation"] == "leave_one_year_out"
    ]

    assert len(within) == len(cross) == 3
    assert sum(within) / 3 == 0.44823749187784273
    assert sum(cross) / 3 == 0.34237329434697855
    assert sum(within) / 3 - sum(cross) / 3 == 0.10586419753086418
