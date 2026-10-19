"""Invented monthly ocean fields; no penguin count effects."""
import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pytest
pytest.importorskip("netCDF4")
pytest.importorskip("requests")
pytest.importorskip("pyproj")
from netCDF4 import Dataset,date2num
from pyproj import Transformer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import derive_nsidc_seaice_siteyear_v5 as v


def test_offshore_annulus_does_not_touch_land_center():
    to_grid=Transformer.from_crs(4326,3412,always_xy=True)
    px,py=to_grid.transform(-57,-63)
    x=px+np.arange(-8,9)*25000
    y=py+np.arange(-8,9)*25000
    w=v.offshore_windows({"fictional":[{"lon":-57,"lat":-63}]},x,y)
    close=w["fictional"]["25_75km"]
    far=w["fictional"]["75_150km"]
    assert len(close[0])>4
    assert len(far[0])>4
    assert not any((i==8 and j==8) for i,j in zip(*close))
    assert not any((i==8 and j==8) for i,j in zip(*far))
    assert not set(zip(*close))&set(zip(*far))


def test_sea_ice_zero_is_valid_ocean_data_but_nan_land_is_not_zero():
    x=np.ma.array(np.zeros((3,3)),mask=np.array([
        [False,False,True],[False,True,True],[False,False,True]
    ]))
    a=v.monthly_slice(x)
    assert np.isnan(a[0,2])
    assert np.isnan(a[1,1])
    assert a[0,0]==0
    ok=v.site_month_stat(a,(np.array([0,0,1,2]),np.array([0,1,0,0])))
    assert ok["sic"]==0 and ok["valid_cells"]==4
    no=v.site_month_stat(a,(np.array([0,0,1]),np.array([0,1,0])))
    assert no["sic"] is None


def test_unscaled_or_out_of_range_values_are_hard_stop():
    with pytest.raises(ValueError,match="0–1"):
        v.monthly_slice(np.array([[0,1.5]]))
    with pytest.raises(ValueError,match="0–1"):
        v.monthly_slice(np.array([[251,0]]))


def test_climatology_threshold_is_frozen_at_20_years():
    band="25_75km"
    seasons={
        1981+y:{band:(0.2+0.01*y,8,8)} for y in range(30)
    }
    out=v.climatology({"fake":seasons})["fake"][band]
    assert out[1]==30
    assert abs(out[0]-0.345)<1e-10
    # Climate baselines with insufficient years must not be zero-filled.
    sample={1981+y:{band:(0.2,8,8)} for y in range(19)}
    missing=v.climatology({"fake":sample})["fake"][band]
    assert missing==(None,19)


def test_2018_oct_nov_source_CF_and_projection_without_biological_data(tmp_path):
    path=tmp_path/"synthetic_monthly.nc"
    with Dataset(path,"w") as nc:
        nc.createDimension("time",2)
        nc.createDimension("y",332)
        nc.createDimension("x",316)
        x=nc.createVariable("xgrid","f8",("x",))
        y=nc.createVariable("ygrid","f8",("y",))
        x.units="meters";y.units="meters"
        x[:]=np.arange(316)*25000-3937500
        y[:]=4337500-np.arange(332)*25000
        times=nc.createVariable("time","f8",("time",))
        times.units="days since 1601-01-01 00:00:00"
        times.calendar="standard"
        times[:]=date2num([dt.datetime(2018,10,15),dt.datetime(2018,11,15)],units=times.units,calendar=times.calendar)
        ice=nc.createVariable(v.VAR,"f4",("time","y","x"),fill_value=np.float32(-999))
        ice.units="1"
        ice[:]=0.45
    with Dataset(path) as src:
        xx,yy,field,dates,md=v.netcdf_schema(src)
        assert (2018,10) in dates and (2018,11) in dates
        assert len(xx)==316 and len(yy)==332
        assert md["projection_grid"].startswith("EPSG:3412")
        sample=v.monthly_slice(field[0,:,:])
        assert abs(float(np.mean(sample))-0.45)<1e-6


def test_only_frozen_months_and_years_no_bird_outcomes():
    assert v.YEARS[0]==1979 and v.YEARS[-1]==2022
    assert v.BASELINE_YEARS[0]==1981 and v.BASELINE_YEARS[-1]==2010
    assert v.RADII==((25000,75000),(75000,150000))
    assert v.MIN_CELLS==4
