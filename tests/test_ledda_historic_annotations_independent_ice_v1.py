"""Frozen historical Ledda dates and physical-only synthetic validators."""
from datetime import date, timedelta
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).resolve().parents[1] / "scripts/audit_ledda_historic_annotations_independent_ice_v1.py"
spec=importlib.util.spec_from_file_location("historic_ledda",PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def dates_of_year(y):
    start=date(y,1,1)
    return [start+timedelta(days=15*i) for i in range(24)]


def test_event_dates_and_known_states_are_not_redefined():
    assert list(m.EVENTS)==[2009,2010,2012,2013]
    assert m.EVENTS[2009]["image_date"]=="2009-10-27"
    assert m.EVENTS[2010]["bird_code"]=="yes"
    assert m.EVENTS[2012]["annotator_ice"]=="ice_absent"
    assert m.EVENTS[2013]["image_date"]=="2013-11-30"
    assert m.RADII==(1,3,5)


def test_never_allow_overlapping_15day_image_composite_into_prior_exposure():
    for year in m.EVENTS:
        dates=dates_of_year(year)
        ix=m.choose_preimage_indices(year,dates)
        img=date.fromisoformat(m.EVENTS[year]["image_date"])
        assert len(ix)>4
        assert dates[ix[-1]]+timedelta(days=14) < img
        assert ix == list(range(ix[0],ix[-1]+1))
        for j in range(ix[-1]+1,len(dates)):
            if dates[j] >= date(year,5,1):
                assert dates[j]+timedelta(days=14) >= img


def test_never_extrapolate_to_unapproved_or_year_mixed_ice_files():
    with pytest.raises(ValueError):
        m.choose_preimage_indices(2011,dates_of_year(2011))
    with pytest.raises(ValueError):
        m.choose_preimage_indices(2012,dates_of_year(2013))


def test_seasonal_persistence_and_gap_from_synthetic_only():
    v=[{"class4_pixels":k,"valid_pixels":10} for k in [0,3,3,0,0,1,0,0]]
    r=m.metrics(v)
    assert r["n_preimage_15day_composites"]==8
    assert r["n_composites_with_any_class4"]==3
    assert r["longest_consecutive_composites_any_class4"]==2
    assert r["trailing_composites_no_class4"]==2
    assert r["physical_spatial_context_not_confirmed_nest_habitat"]
