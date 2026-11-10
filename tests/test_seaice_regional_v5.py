import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'code/seaice_regional_v5.py'
if not TARGET.exists():
    TARGET=ROOT/'research/climate-penguin/work/climate_penguin/seaice_regional_v5.py'

def module():
    spec=importlib.util.spec_from_file_location('seaice_regional_v5_tests',TARGET)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def balanced():
    rows=[]
    for r in range(2):
        for i in range(3):
            for y in range(5):
                local=(i-1)*((y%3)-1)*.3
                common=2*(y-2)+(r-0.5)*((y%2)*3-1)
                x=common+local+.2*i
                outcome=1.75*local+4*r+5*i-2.4*common
                rows.append(dict(site_id=f'{r}_{i}',region=str(r),end_year=2000+y,
                                 x=x,relative_growth=outcome))
    return rows

def test_nested_partition_is_exact_and_local_slope_recovers_known_effect():
    m=module(); rows=balanced()
    assert hasattr(m,'partition'), 'Missing regional identification implementation'
    p=m.partition(rows,'x')
    assert np.isclose(p['models']['site_region_year']['coefficient'],1.75,atol=1e-10)
    parts=p['orthogonal_components']
    assert np.isclose(sum(q['x_ss'] for q in parts),p['site_residual_x_ss'],atol=1e-9)
    assert np.isclose(sum(q['xy_crossproduct'] for q in parts),p['site_residual_xy'],atol=1e-9)
    assert np.isclose(sum(q['slope_contribution'] for q in parts),p['models']['site']['coefficient'],atol=1e-9)
    assert p['maximum_cross_component_dot_abs']<1e-8

def test_region_year_adjustment_is_invariant_to_added_regional_shocks():
    m=module(); rows=balanced(); changed=[]
    for row in rows:
        z=dict(row); shock=7*int(z['region'])*(int(z['end_year'])%3)
        z['x']+=shock; z['relative_growth']+=2*shock
        changed.append(z)
    assert hasattr(m,'partition'), 'Missing regional identification implementation'
    a=m.partition(rows,'x');b=m.partition(changed,'x')
    assert np.isclose(a['models']['site_region_year']['coefficient'],b['models']['site_region_year']['coefficient'])
    assert not np.isclose(a['models']['site']['coefficient'],b['models']['site']['coefficient'])

def test_rank_exhaustion_or_no_local_weather_returns_no_interpretable_slope():
    m=module(); assert hasattr(m,'fit'), 'Missing rank-aware model'
    rows=[dict(site_id=f's{i}',region='one',end_year=2000+i,x=i,relative_growth=i*i) for i in range(4)]
    z=m.fit(rows,'x',('site_id','end_year'))
    assert z['coefficient'] is None
    assert z['status'] in {'NO_RESIDUAL_PREDICTOR','SATURATED_NO_RESIDUAL_DF'}

def test_distinct_shared_ocean_cells_are_not_double_counted():
    m=module(); assert hasattr(m,'regional_union'), 'Missing unique-cell union'
    rows=[]
    for site,values in [('A',[(1,0),(2,20)]),('B',[(2,20),(3,100)])]:
        for cell,v in values:
            rows.append(dict(site_id=site,year='2000',month='8',flat_cell_index=str(cell),
                             lat=str(-60-cell/10),lon='-60',flag='0',sic_percent=str(v)))
    series,support=m.regional_union(rows,{'A':'R','B':'R'},require_full=False)
    assert len(series)==1
    assert series[0]['n_unique_ocean_cells']==3
    assert series[0]['sic_percent_mean']==40
    assert support['regions']['R']['sites']==['A','B']

def test_conflicting_or_missing_original_ocean_values_fail_without_imputation():
    m=module(); assert hasattr(m,'regional_union'), 'Missing unique-cell union'
    a=dict(site_id='A',year='2000',month='8',flat_cell_index='1',lat='-60',lon='-60',flag='0',sic_percent='10')
    b=dict(a,site_id='B',sic_percent='11')
    with pytest.raises(ValueError,match='conflicting'):
        m.regional_union([a,b],{'A':'R','B':'R'},require_full=False)
    with pytest.raises(ValueError,match='missing'):
        m.regional_union([dict(a,sic_percent='')],{'A':'R'},require_full=False)

def test_land_flags_do_not_mean_zero_marine_ice():
    m=module(); assert hasattr(m,'regional_union'), 'Missing unique-cell union'
    a=dict(site_id='A',year='2000',month='8',flat_cell_index='1',lat='-60',lon='-60',flag='0',sic_percent='20')
    b=dict(a,flat_cell_index='2',flag='1',sic_percent='')
    rows,_=m.regional_union([a,b],{'A':'R'},require_full=False)
    assert rows[0]['n_unique_ocean_cells']==1 and rows[0]['sic_percent_mean']==20

def test_unknown_region_must_not_be_filled_by_nearest_site():
    m=module(); assert hasattr(m,'regional_union'), 'Missing unique-cell union'
    a=dict(site_id='unknown',year='2000',month='8',flat_cell_index='1',lat='-60',lon='-60',flag='0',sic_percent='20')
    with pytest.raises(ValueError,match='site'):
        m.regional_union([a],{'A':'R'},require_full=False)

def test_source_bytes_are_pinned_before_recomputing(tmp_path):
    m=module(); assert hasattr(m,'verify_source'), 'Missing source byte pin'
    for name in ('fixed44_prior_seaice_pairs.csv','original_selected_grid_cells.csv','seaice_fixed44_v4_result.json'):
        (tmp_path/name).write_text('unverified input')
    with pytest.raises(ValueError,match='SHA'):
        m.verify_source(tmp_path)
