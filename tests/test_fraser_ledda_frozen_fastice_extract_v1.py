"""Precommitted physical ice class mask, time, no-future exposure test."""
import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "fraser_frozen",
    ROOT/"scripts/extract_fraser_ledda_frozen_2011_2014_fastice_v1.py"
)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def test_classification_preserves_land_water_edge_and_nodata():
    x=np.array([[4,4,0,2],
                [4,5,6,1],
                [3,0,-127,4]])
    m=np.ones(x.shape,dtype=bool)
    r=M.summarize_mosaic(x,m)
    assert r["n_cells_spatial_mask"]==12
    assert r["n_fastice_class4"]==4
    assert r["n_edge_classes_5_or_6"]==2
    assert r["n_unknown_or_fill"]==1
    assert r["n_class_valid"]==11
    assert r["n_marine_classes_0_4_5_6"]==8
    assert r["fraction_fastice_over_valid_cells"]==4/11
    assert r["fraction_fastice_over_marine_and_edge"]==4/8


def test_freeze_before_original_negative_images():
    assert M.YEARS==(2011,2014)
    assert M.SPATIAL_RADII==(1,3,5)
    assert M.PRIMARY_RADIUS_KM==3
    assert M.EPSG=="EPSG:3412"
    assert M.FROZEN_YEAR[2011]["primary_t"]==16
    assert M.FROZEN_YEAR[2011]["primary_date_alt"]==20110829
    assert M.FROZEN_YEAR[2011]["overlap_t"]==17
    assert M.FROZEN_YEAR[2014]["primary_t"]==18
    assert M.FROZEN_YEAR[2014]["primary_date_alt"]==20140928
    assert M.FROZEN_YEAR[2014]["overlap_t"]==19
    assert M.FROZEN_YEAR[2011]["preimage_indices"]==tuple(range(8,17))
    assert M.FROZEN_YEAR[2014]["preimage_indices"]==tuple(range(8,19))
    for y in M.YEARS:
        d=M.FROZEN_YEAR[y]
        assert d["primary_t"]<d["overlap_t"]
        assert max(d["preimage_indices"])==d["primary_t"]
        assert d["overlap_t"] not in d["preimage_indices"]


def test_do_not_read_unfrozen_year():
    with pytest.raises(ValueError,match="independently frozen"):
        M.read_one_year(2016)


def test_zero_marine_cells_not_silently_interpreted_as_zero_ice():
    a=np.array([[1,2],[3,-127]])
    r=M.summarize_mosaic(a,np.ones(a.shape,dtype=bool))
    assert r["fraction_fastice_over_marine_and_edge"] is None
    assert r["n_fastice_class4"]==0


def test_empty_window_fails():
    with pytest.raises(ValueError,match="No valid grid centers"):
        M.summarize_mosaic(np.zeros((2,2),dtype=int),
                           np.zeros((2,2),dtype=bool))
