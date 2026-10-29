import importlib.util,sys
from pathlib import Path
import pytest
pytest.importorskip('numpy')
pytest.importorskip('xarray')
pytest.importorskip('pyproj')
import numpy as np
P=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/seaice_fixed_pairs_v4.py'
def mod():
    assert P.exists(), 'fixed marine exposure implementation missing'
    sys.path.insert(0,str(P.parent))
    sp=importlib.util.spec_from_file_location('marine_v4',P)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def test_ocean_quality_retains_true_zero_not_missing_or_land():
    m=mod()
    sic=np.array([10.,50.,0.,np.nan,99.,80.])
    flags=np.array([0.,8.,4.,0.,1.,2.])
    d=m.summarize_cells(sic,flags,np.arange(6))
    assert d['n_ocean']==4 and d['n_valid']==3
    assert d['sic_percent_mean'] is None
    assert d['unqualified_valid_pixel_mean']==20.
    assert d['n_open_water_filtered']==1 and d['n_landspill']==1
    sic[3]=20.
    d=m.summarize_cells(sic,flags,np.arange(6))
    assert d['sic_percent_mean']==20 and d['complete_spatial_support']

def test_fixed_prior_window_uses_both_complete_years_not_new_lag():
    m=mod()
    rows=[{'site_id':'A','start_year':'2000','end_year':'2001','prior_precedes_all_source_bounds':'True','relative_growth':'1.0'}]
    table=[{'site_id':'A','year':year,'month':mo,'sic_percent_mean':float(10*(year-1998)),'complete_spatial_support':True} for year in [1999,2000] for mo in [8,9,10,11]]
    joined=m.join_exposure(rows,table)
    assert joined[0]['delta_prior_sic_10pp']==1.
    table.pop()
    with pytest.raises(ValueError,match='missing monthly'):m.join_exposure(rows,table)
    rows[0]['prior_precedes_all_source_bounds']='False'
    with pytest.raises(ValueError,match='chronology'):m.join_exposure(rows,table)

def test_metadata_does_not_accept_wrong_version_or_month():
    m=mod()
    attrs={'product_id':'osi-450-a1','product_version':'3.1','doi':'10.15770/EUM_SAF_OSI_0023','time_coverage_start':'1993-08-01T00:00:00Z','time_coverage_end':'1993-09-01T00:00:00Z'}
    m.validate_attrs(attrs,1993,8)
    with pytest.raises(ValueError):m.validate_attrs(dict(attrs,product_version='3.0'),1993,8)
    with pytest.raises(ValueError):m.validate_attrs(attrs,1993,9)

def test_shared_marine_cells_are_not_independent_support():
    m=mod()
    d=m.overlap_report({'A':{1,2,3},'B':{1,2,3},'C':{3,4,5}})
    assert d[0]['jaccard']==1.
    assert len(d)==3
    assert next(x for x in d if x['a']=='A' and x['b']=='C')['shared_cells']==1
