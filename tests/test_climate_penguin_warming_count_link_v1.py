"""Synthetic and source-support tests for post-exploration ERA5 × penguin counts.

This guards the DESIGN, not climate attribution or a biological effect.
No original ERA5 exposure / penguin count slope is selected in these tests.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "research" / "climate-penguin"
SCRIPT = DIR / "work" / "climate_penguin" / "analyze_warming_count_link_v1.py"


def module():
    spec = importlib.util.spec_from_file_location("warming_count_link_v1_guard", SCRIPT)
    assert spec and spec.loader
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def sample_rows():
    """A balanced connected site × year design with known fixed effects."""
    out = []
    for site_index, site in enumerate(("A", "B", "C", "D")):
        for yr in range(2011, 2017):
            shock = (site_index - 1.5) * ((yr % 3) - 1)
            x = shock + site_index * 0.5 + (yr - 2011) * 0.25
            y = 2.5 * x + 4.0 * site_index + 3.0 * (yr - 2011)
            out.append({
                "site_id": site,
                "end_year": yr,
                "region": "Victoria Land" if site in ("A", "B") else "Other",
                "test_temp": x,
                "delta_log_count": y,
            })
    return out


def test_fixed_effect_slope_recovers_known_effect_without_pseudoreplication():
    mod = module()
    rows = sample_rows()
    assert math.isclose(mod.slope(rows, "test_temp", ["site_id", "end_year"]), 2.5, abs_tol=1e-9)
    assert not math.isclose(mod.slope(rows, "test_temp", ["site_id"]), 2.5, abs_tol=.01)
    result = mod.support_and_effect(rows, "test_temp", ["site_id", "end_year"])
    assert (result["n_intervals"], result["n_sites"], result["n_regions"]) == (24, 4, 2)
    assert result["victoria_n"] == 12
    assert math.isclose(result["beta_logN_per_1C_change"], 2.5, abs_tol=1e-8)
    assert all(math.isclose(z, 2.5, abs_tol=1e-8) for z in result["leave_one_site_out_range"])
    # Missing exposure is excluded without treating missing as zero.
    rows[0]["test_temp"] = None
    assert math.isclose(mod.slope(rows, "test_temp", ["site_id", "end_year"]), 2.5, abs_tol=1e-8)
    assert mod.support_and_effect(rows, "test_temp", ["site_id"])["n_intervals"] == 23


def write_csv(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def make_era5_fixture(tmp_path: Path):
    site_file = DIR / "outputs" / "climate_penguin" / "daily_ice_locations.csv"
    with site_file.open(newline="", encoding="utf-8") as fh:
        sites = [row["site_id"] for row in csv.DictReader(fh) if row["cohort"] == "macro_40"]
    assert len(sites) == len(set(sites)) == 40

    source = tmp_path / "synthetic-era5"
    source.mkdir()
    path = source / "era5_monthly_1991_2020.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "site_id", "year", "month", "complete_month", "air2m_mean_c"
        ])
        writer.writeheader()
        for i, site in enumerate(sites):
            for year in range(1991, 2021):
                for month in range(1, 13):
                    # Full-year trend +0.2 C/year; site-constant and
                    # month-constant offsets; all year-to-year changes=0.2.
                    writer.writerow({
                        "site_id": site, "year": year, "month": month,
                        "complete_month": "True",
                        "air2m_mean_c": -15.0 + .2 * (year - 1991)
                        + .25 * (i % 3) + .05 * month,
                    })
    return source, path


def test_full_40_site_synthetic_input_preserves_timing_gates_and_no_false_effect(tmp_path, monkeypatch):
    mod = module()
    source, _ = make_era5_fixture(tmp_path)
    output = tmp_path / "outputs"
    monkeypatch.setattr(sys, "argv", [
        str(SCRIPT), "--era5-dir", str(source), "--output", str(output),
    ])
    mod.main()
    report = json.loads((output / "count_temperature_exploratory_v1.json").read_text())
    assert report["n_count_intervals"] == 301
    assert report["n_with_era5_september"] == 301
    assert report["n_strict_post_september"] == 203
    assert report["n_strict_post_november"] == 191
    assert report["status"] == "post_outcome_exploratory_not_climate_attribution"
    assert report["effects"]["september_strict"]["site_fixed"]["n_intervals"] == 203
    assert report["effects"]["aug_nov_strict"]["site_fixed"]["n_intervals"] == 191
    # Identical Delta T within all complete site-years has zero
    # post-demeaning variation, so the model must report unidentifiable
    # rather than manufacture a climate coefficient.
    for group in ("site_fixed", "site_year_fixed"):
        for label in ("september_strict", "aug_nov_strict"):
            assert report["effects"][label][group]["beta_logN_per_1C_change"] is None
    with (output / "count_temperature_interval_join_v1.csv").open(newline="") as fh:
        joins = list(csv.DictReader(fh))
    assert len(joins) == 301
    assert all(math.isclose(float(r["delta_t_september_c"]), .2, abs_tol=1e-10)
               for r in joins)


def test_full_source_gate_rejects_partial_or_duplicate_months(tmp_path, monkeypatch):
    mod = module()
    source, path = make_era5_fixture(tmp_path)
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # An incomplete batch must not be silently treated as a complete climate panel.
    write_csv(path, rows[:-1])
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--era5-dir", str(source),
                                      "--output", str(tmp_path / "bad-output")])
    with pytest.raises(AssertionError, match="full-site source"):
        mod.main()
    # Also reject a duplicate record even with the expected total number.
    write_csv(path, rows[:-1] + [rows[0]])
    with pytest.raises(AssertionError):
        mod.main()
