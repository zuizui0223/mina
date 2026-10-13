"""Fictitious geometry only; tests of the post-outcome sensitivity functions."""
import importlib.util
from pathlib import Path
import sys
import pytest
pytest.importorskip("requests")
pytest.importorskip("shapely")
pytest.importorskip("shapefile")
pytest.importorskip("pyproj")
from shapely.geometry import box
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import reproduce_zavodovski_overlap_sensitivity_v11 as m

def test_overlap_translation_in_artificial_square():
    g, c, s = box(0, 0, 10, 10), box(0, 0, 10, 10), box(-50, -50, 60, 60)
    x = m.positional_sensitivity(g, c, s, 2)
    assert x["n_offsets"] == 8
    assert 0 < x["min"] < 1
    assert x["min"] <= x["median"] <= x["max"]
    assert x["max"] < 1

def test_core_erodes_fringes_and_zero_denominator():
    x = m.patch_core_sensitivity(box(0, 0, 10, 10), box(1, 1, 9, 9), 1)
    assert 0 <= x["core_E"] <= 1
    assert m.patch_core_sensitivity(box(0, 0, 2, 2), box(0, 0, 2, 2), 2)["core_E"] is None
