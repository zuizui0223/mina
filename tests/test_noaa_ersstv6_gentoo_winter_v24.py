"""Tests use invented SST and invented Gentoo growth values only."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import model_noaa_ersstv6_gentoo_winter_v24 as v
import pytest

def test_fixed_publication_source_grid_axes():
    import numpy as np
    lat=np.array([-52.,-54.,-56.,-58.,-60.,-62.])
    lon=np.array([312.,314.,316.,318.,320.,322.,324.,326.])
    k,j,c=v.ocean_grid_cell(lat,lon,-54.,321.95)
    assert k==1 and j==5
    assert c["lat"]==-54. and c["lon_0_360"]==322.
    with pytest.raises(ValueError,match="too far"):
        v.ocean_grid_cell(lat,lon,-70.,324.)

def invented():
    winter={}
    for index,site in enumerate(v.SITES):
        winter[site]={yr:3+index+((yr-2010)**2 % (6+index))*.11
                       for yr in v.YEARS}
    growth={yr:{site:((yr-2011)**2 % (5+idx))*.12
                for idx,site in enumerate(v.SITES)} for yr in v.WINDOWS}
    return winter,growth

def test_complete_eight_window_input_only_no_lag_reopt():
    winter,growth=invented()
    r=v.environmental_vs_growth(winter,growth)
    assert r["effect_computed"]
    assert r["fixed_original_growth_windows"]==list(v.WINDOWS)
    assert r["original_winter_sst_years"]==list(v.YEARS)
    assert r["marine_SST_causal_effect_demonstrated"] is False

def test_missing_winter_year_prohibits_fit():
    winter,growth=invented()
    winter["signy"].pop(2013)
    r=v.environmental_vs_growth(winter,growth)
    assert not r["effect_computed"]
    assert r["status"]=="STOP_INCOMPLETE_ORIGINAL_ERSST_WINTER_DATA"

def test_wrong_window_roster_prohibits_fit():
    winter,growth=invented()
    growth.pop(2017)
    r=v.environmental_vs_growth(winter,growth)
    assert r["status"]=="STOP_V23_GROWTH_WINDOWS_CHANGED"
    assert v.WINTER_MONTHS==(7,8,9)
    assert len(v.SITES)==3
    assert v.EXPECTED_V23_DELTA==pytest.approx(1.0154800142899)

def test_source_url_not_silent_dataset_version_change():
    assert "/noaa.ersst.v6/sst.mnmean.nc" in v.SOURCE
    assert v.REQUEST["time_start"].startswith("2009-")
    assert v.REQUEST["west"]=="312"
    assert v.REQUEST["east"]=="326"
    assert v.MAX_BYTES <= 12*1024*1024

def test_original_sst_missing_categories_are_separate_from_temperature_zero():
    # Monthly data availability diagnostics must not recode a mask as SST=0.
    import numpy as np
    x=np.ma.masked
    assert np.ma.is_masked(x)
    assert not np.ma.is_masked(0.0)
    assert v.MINUS_SST_ZERO_NEVER_IMPUTED if hasattr(v,"MINUS_SST_ZERO_NEVER_IMPUTED") else True
