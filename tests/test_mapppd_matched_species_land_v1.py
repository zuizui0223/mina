import importlib.util
from pathlib import Path
import math

SCRIPT=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/mapppd_matched_species_land_v1.py'

def module():
    assert SCRIPT.exists(), 'Mapped-land grouping is not implemented'
    s=importlib.util.spec_from_file_location('matched_land',SCRIPT)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def test_shared_land_is_not_independent_site_and_unmatched_not_rescued():
    m=module()
    rows=[{'site_id':'A','delta_log_ratio_b_over_a':1.},
          {'site_id':'A','delta_log_ratio_b_over_a':1.},
          {'site_id':'B','delta_log_ratio_b_over_a':3.},
          {'site_id':'C','delta_log_ratio_b_over_a':-2.},
          {'site_id':'D','delta_log_ratio_b_over_a':99.}]
    exact='EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON'
    geo={'A':{'category':exact,'original_land_fid':1},'B':{'category':exact,'original_land_fid':1},
         'C':{'category':exact,'original_land_fid':2},'D':{'category':'NEAR_ONLY_HOLD_NOT_EXACT','original_land_fid':None}}
    x=m.aggregate(rows,geo)
    assert x['retained_sites']==3 and x['retained_land_features']==2
    assert x['excluded_sites']==['D']
    assert math.isclose(x['same_sample_equal_site_mean'],2/3)
    assert x['equal_land_mean_of_site_means']==0.
    assert not x['independent_physical_islands_verified']

def test_largest_mainland_proxy_excluded_and_empty_safe():
    m=module();r=[{'site_id':'A','delta_log_ratio_b_over_a':1.}]
    g={'A':{'category':'EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON','original_land_fid':m.CONTINENT_FID}}
    x=m.aggregate(r,g)
    assert x['retained_sites']==0 and x['equal_land_mean_of_site_means'] is None
