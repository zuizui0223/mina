"""Guard post-exploration climate×count trend design without source outcome tuning."""
from __future__ import annotations

import csv
import importlib.util
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "research/climate-penguin"
SCRIPT = FOLDER / "work/climate_penguin/analyze_long_term_warming_count_trends_v1.py"


def mod():
    spec = importlib.util.spec_from_file_location("long_term_warming_v1", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_numerical_trends_and_structural_independence():
    m = mod()
    assert math.isclose(m.linear_slope([2000, 2005, 2010], [3, 4, 5]), 2)
    assert math.isclose(m.pearson([1, 2, 3], [5, 3, 1]), -1)
    assert m.pearson([1, 1, 1], [1, 2, 3]) is None
    d = []
    for index, (g, t, v) in enumerate([
        ("g0", 1, 1), ("g0", 1, 3), ("g1", 2, 2),
        ("g2", 3, 4), ("g3", 4, 6), ("g4", 5, 7),
    ]):
        d.append({
            "site_id": f"s{index}", "era5_grid_id": g,
            "temperature_c_slope_per_decade": t,
            "count_log_slope_per_decade": v,
            "region": "A" if index < 4 else "B",
        })
    report = m.association(d)
    assert report["n_sites"] == 6
    assert report["n_era5_grids"] == 5
    assert report["regions"] == {"A": 4, "B": 2}
    assert report["macro_generalization_gate"]["pass"] is False
    assert report["leave_one_grid_out_r_range"] is not None
    assert math.isclose(report["equal_grid_pearson_r"],
        m.pearson([1, 2, 3, 4, 5], [2, 2, 4, 6, 7]), abs_tol=1e-12)
    assert report["by_region_pearson_r"]["B"] is None  # n=2
    # Switching the climate window must NOT silently switch the count roster.
    for j, record in enumerate(d):
        record["fixed_1991_2020_temperature_c_slope_per_decade"] = -2 * j
    fixed = m.association(d, "fixed_1991_2020_temperature_c_slope_per_decade")
    assert fixed["n_sites"] == report["n_sites"]
    assert fixed["n_era5_grids"] == report["n_era5_grids"]
    assert fixed["climate_exposure_key"] == "fixed_1991_2020_temperature_c_slope_per_decade"
    assert fixed["site_pearson_r"] != report["site_pearson_r"]


def test_count_support_gate_frozen_independent_of_trend_direction():
    m = mod()
    counts = m.read_csv(FOLDER / "outputs/climate_penguin/historical_count_season_timing.csv")
    assert len(counts) == 516
    a = m.source_count_eligibility(counts, "all_after_september")
    b = m.source_count_eligibility(counts, "all_after_november")
    assert len(a) == 16 and len(b) == 15
    assert {z[0]["region"] for z in a.values()} == {
        "Central-west Antarctic Peninsula", "Victoria Land"}
    for obj, expected in ((a, 14), (b, 14)):
        assert sum(x[0]["region"] == "Victoria Land" for x in obj.values()) == expected
        assert all(len({r["method"] for r in part}) == 1 for part in obj.values())
        assert all(len(part) >= 8 and
                   max(int(r["season"]) for r in part) - min(int(r["season"]) for r in part) >= 12
                   for part in obj.values())


def test_monthly_real_support_metadata_and_none_handling():
    m = mod()
    records = []
    # A small synthetic subset cannot masquerade as the 40×30×12 source.
    for index, sid in enumerate(["a", "b"]):
        for year in range(1991, 2021):
            for month in range(1, 13):
                records.append({
                    "site_id": sid, "year": str(year), "month": str(month),
                    "complete_month": "True", "air2m_mean_c": str(1 + (year-1991)*.1),
                    "returned_grid_latitude": "-75.0", "returned_grid_longitude": str(110+index),
                })
    try:
        m.load_era5(records)
        raise AssertionError("partial source must fail")
    except AssertionError as ex:
        assert "incomplete" in str(ex)
