"""Secondary Ledda coordinate sensitivity: fixtures never represent Antarctic ice."""
import importlib.util
from pathlib import Path

PATH=Path(__file__).resolve().parents[1] / "scripts/extract_ledda_fretwell_secondary_centroid_fastice_v1.py"
spec=importlib.util.spec_from_file_location("secondary_ledda",PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_same_frozen_years_radii_and_15day_windows():
    assert m.is_frozen_plan()
    assert m.YEARS==(2011,2014)
    assert m.RADII==(1,3,5)
    assert m.primary.FROZEN_YEAR[2011]["primary_t"]==16
    assert m.primary.FROZEN_YEAR[2014]["primary_t"]==18


def test_second_published_centroid_far_beyond_both_5km_buffers():
    d=m.primary.haversine_km(m.PRIMARY_LAT,m.PRIMARY_LON,m.ALT_LAT,m.ALT_LON)
    assert 14<d<16
    assert d>2*max(m.RADII)


def test_any_fixed_year_or_coordinate_drift_stops(monkeypatch):
    assert m.is_frozen_plan()
    monkeypatch.setattr(m,"ALT_LON", -130.784)
    assert not m.is_frozen_plan()
    import pytest
    with pytest.raises(ValueError, match="frozen"):
        m.read_one_year(2011)


def test_unknown_year_stopped_before_network():
    import pytest
    with pytest.raises(ValueError):
        m.read_one_year(2010)
