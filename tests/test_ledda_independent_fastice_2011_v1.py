"""Synthetic tests only: never infer actual 2011 biology from fixtures."""
import importlib.util
from datetime import date
from pathlib import Path

import numpy as np
import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/audit_ledda_independent_fastice_2011_v1.py"
spec = importlib.util.spec_from_file_location("ledda_ice", PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_fixed_original_observation_and_dimensions():
    assert (m.LAT, m.LON, m.TARGET_DATE.isoformat()) == (-74.272, -131.243, "2011-09-23")
    assert m.RADII_KM == (1, 3, 5)
    assert m.ICE_CODES == {4, 5, 6}


def test_frozen_physical_classes_no_biological_labels():
    arr = np.array([[0, 4, 5], [6, 1, 2], [3, 0, 4]], dtype=int)
    d = np.zeros_like(arr, dtype=float)
    s = m.summarize_pixels(arr, d, 1)
    assert s["pixel_total"] == 9
    assert s["class_counts"]["0"] == 2
    assert s["fast_ice_4_5_6_pixels"] == 4
    assert s["fast_ice_4_5_6_fraction_all_pixels"] == pytest.approx(4/9)
    assert s["ocean_or_pack_or_fill_0_is_not_verified_open_water"] is True


def test_no_radius_cherry_picking():
    arr = np.array([[4, 4, 4], [0, 4, 0], [4, 4, 4]])
    dist = np.array([[3000., 2000., 3000.], [2000., 0., 2000.], [3000., 2000., 3000.]])
    assert m.summarize_pixels(arr, dist, 1)["pixel_total"] == 1
    assert m.summarize_pixels(arr, dist, 3)["pixel_total"] == 9


def test_invalid_ice_codes_and_grid_fail_closed():
    with pytest.raises(ValueError):
        m.summarize_pixels(np.array([[9]]), np.array([[0.]]), 1)
    with pytest.raises(ValueError):
        m.validate_axis([1, 2, 1, 4], "x")
    with pytest.raises(ValueError):
        m.validate_axis([0, 100, 200, 300], "x")
    assert m.validate_axis([0, 1000, 2000, 3000], "x") == 1000


def test_time_labels_do_not_prove_preimage_exposure():
    days = [date(2011, 9, 15), date(2011, 9, 30), date(2011, 10, 15)]
    result = m.bracket_dates(days, date(2011, 9, 23))
    assert result["latest_label_on_or_before_image"] == "2011-09-15"
    assert result["first_label_after_image"] == "2011-09-30"
    assert result["time_bounds_known"] is False
    assert result["time_label_not_proof_of_strict_pre_observation_ice_exposure"] is True


def test_orientation_for_both_netcdf_orders():
    class Var:
        def __init__(self, dims):
            self.dimensions = dims
            self.data = np.arange(2 * 3 * 4).reshape(2, 3, 4) if dims == ("y", "x", "time") else np.arange(3 * 2 * 4).reshape(3, 2, 4)
        def __getitem__(self, key):
            return self.data[key]
    yx = m.decode_map(Var(("y", "x", "time")), 0, slice(None), slice(None))
    xy = m.decode_map(Var(("x", "y", "time")), 0, slice(None), slice(None))
    assert yx.shape == xy.shape == (2, 3)
