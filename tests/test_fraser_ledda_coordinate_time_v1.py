"""Coordinate/time pilot tests: no fast ice array values opened."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys

import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SPEC=importlib.util.spec_from_file_location(
    "fraser_ledda_geotime",ROOT/"scripts/probe_fraser_ledda_coordinate_time_v1.py"
)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class Dimension:
    def __init__(self,values,attrs=None):
        self.values=np.asarray(values)
        self.attrs=attrs or {}
    def __getitem__(self,key):
        return self.values[key]


class Geospatial:
    def __init__(self,which,choice):
        self.which=which
        self.choice=choice
        self.attrs={}
    def __getitem__(self,key):
        assert isinstance(key,tuple)
        return (M.SITE_LAT if self.which=="latitude" else M.SITE_LON)


class FakeH5:
    def __init__(self):
        lon,lat=M.SITE_LON,M.SITE_LAT
        PX,PY=Transformer.from_crs("EPSG:4326","EPSG:3412",always_xy=True).transform(lon,lat)
        self.vars={
            "x":Dimension(np.linspace(PX-2812000,PX+2812000,5625)),
            "y":Dimension(np.linspace(PY-2350000,PY+2349000,4700)),
            "time":Dimension(np.arange(24,dtype=np.int16),{"units":"days since 2011-03-01","calendar":"standard"}),
            "date_alt":Dimension(np.arange(24,dtype=np.int32),{"description":"Synthetic 24 composites"}),
            "latitude":Geospatial("latitude","3412"),
            "longitude":Geospatial("longitude","3412"),
        }
    def __getitem__(self,key):
        if key=="Fast_Ice_Time_series":
            raise AssertionError("Prohibited actual physical ice class access")
        return self.vars[key]


def test_coordinates_choose_predefined_projection_without_ice_values():
    d=M.examine_axis_only(FakeH5())
    assert d["coordinate_verified"]
    assert d["coordinate_candidate"]["EPSG"] in M.PROJECTIONS
    assert d["coordinate_candidate"]["geodetic_residual_km"]<0.001
    assert d["physical_ice_class_values_read"]==0
    assert len(d["time_values"])==24
    assert d["time_attrs"]["units"]=="days since 2011-03-01"


def test_geodetic_and_metadata_guards():
    assert M.haversine_km(-74.228,-130.784,-74.228,-130.784)==0
    assert M.haversine_km(-74.228,-130.784,-74.228,-130.684)>2
    assert M.safe_attr(np.array([1,2,3]))==[1,2,3]
    assert M.safe_attr(np.zeros(100))["status"]=="OMITTED_LONG_METADATA"


def test_frozen_response_scope():
    assert M.YEARS==(2011,2014)
    assert M.MAX_LOCATION_RESIDUAL_KM==3.0
    assert M.SITE_LAT==-74.228
    assert M.SITE_LON==-130.784
