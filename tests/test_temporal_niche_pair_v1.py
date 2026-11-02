"""Frozen source-support and exact-permutation guards for temporal niche audit."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/climate-penguin/work/temporal_niche_pair_v1/analyze.py"
spec = importlib.util.spec_from_file_location("temporal_niche_pair_v1", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_primary_source_support_and_result(tmp_path):
    result = mod.run(out=tmp_path)
    assert result["source_rows"] == 288
    assert result["exact_camera_pair_counts"] == {
        "Adelie-Chinstrap": 5, "Adelie-Gentoo": 7, "Chinstrap-Gentoo": 3}
    assert result["site_year_pair_counts"]["all_source_labels"] == {
        "Adelie-Chinstrap": 6, "Adelie-Gentoo": 18, "Chinstrap-Gentoo": 8}
    assert result["site_year_pair_counts"]["appendix_consistent"] == {
        "Adelie-Chinstrap": 5, "Adelie-Gentoo": 11, "Chinstrap-Gentoo": 4}
    signy = result["signc_adelie_chinstrap"]
    assert signy["seasons"] == [2016, 2017, 2018, 2019, 2020]
    assert signy["winter_sic_slope_days_per_10pp"] == pytest.approx(-1.5430814391596281)
    assert signy["permutation_two_sided_p"] == pytest.approx(28 / 120)
    assert result["site_year_within_site_slope_days_per_10pp"]["all_source_labels"]["Adelie-Gentoo"] == pytest.approx(-1.8448201593912967)
    assert result["site_year_within_site_slope_days_per_10pp"]["appendix_consistent"]["Adelie-Gentoo"] == pytest.approx(2.229226418134566)
    assert (tmp_path / "exact_camera_pairs.csv").exists()
    assert (tmp_path / "site_year_september_pairs.csv").exists()
    assert (tmp_path / "result.json").exists()
    assert result["no_climate_causal_or_future_breeding_claim"] is True


def test_exact_permutation_has_no_fake_precision():
    rows = [{"ice10": 1.0, "gap_days": 2.0},
            {"ice10": 2.0, "gap_days": 3.0},
            {"ice10": 3.0, "gap_days": 4.0}]
    assert mod.slope(rows, "ice10", "gap_days") == pytest.approx(1.0)
    assert mod.exact_two_sided_permutation(rows, "ice10", "gap_days") == pytest.approx(2 / 6)


def test_duplicate_same_camera_species_is_rejected():
    row = dict(source_row_1based="1", colname3="S", season_start_year="2020",
               species="Adelie", lat="-60", long="-45", mdn_veintewin="30",
               tmean_9="-2", settlement="100")
    other = dict(row, source_row_1based="2")
    with pytest.raises(ValueError, match="duplicate species"):
        mod.exact_camera_pairs([row, other])
