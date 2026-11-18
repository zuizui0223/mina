"""Real numerical/source behavior; no remote requests or fabricated ecological outcomes."""
import importlib.util
import math
from pathlib import Path
import pytest

P=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/ardley_dependence_v8.py'
def module():
    spec=importlib.util.spec_from_file_location('ardley_v8_test',P)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def row(site,x,a,b,start=2000,gap=1,cite='s'):
    return dict(site_id=site,start=start,end=start+gap,gap=gap,x_ice_rate=x,
        annualized_a_growth=a,annualized_b_growth=b,
        annualized_log_ratio_change=b-a,original_citekey=cite,original_vantage='ground')

def test_exact_site_cross_products_and_species_difference():
    m=module();rs=[row('A',0,0,0),row('A',2,0,4,start=2001),
                  row('B',0,0,0),row('B',2,0,-2,start=2001)]
    r=m.partition(rs)
    assert math.isclose(r['baseline']['beta']['relative'],.5)
    assert r['baseline']['D']==4
    assert r['baseline']['C']['relative']==2
    assert r['sites']['A']['D']==2
    assert r['sites']['A']['C']['relative']==4
    assert r['sites']['B']['C']['relative']==-2
    for v in [r['baseline'],*r['sites'].values()]:
        assert math.isclose(v['beta']['relative'],v['beta']['gentoo']-v['beta']['chinstrap'])

def test_duration_weighting_matches_centered_sums():
    m=module();rs=[row('A',0,0,1,gap=1),row('A',2,1,5,start=2002,gap=3)]
    r=m.partition(rs)['baseline']
    assert math.isclose(r['D'],3)
    assert math.isclose(r['beta']['gentoo'],2)
    assert math.isclose(r['beta']['chinstrap'],.5)

def test_single_record_site_adds_zero_slope_information():
    m=module();rs=[row('A',0,0,0),row('A',2,0,4,start=2001),row('B',900,50,-99)]
    r=m.partition(rs)
    assert r['sites']['B']['beta']['relative'] is None
    assert r['sites']['B']['D']==0
    assert r['baseline']['beta']['relative']==2

def test_source_partition_exactly_reconstructs_site_covariance():
    m=module();rs=[row('A',0,0,0,cite='old'),row('A',2,1,4,start=2001,cite='old'),
                  row('A',10,5,8,start=2010,cite='new'),row('A',12,6,6,start=2011,cite='new')]
    r=m.partition(rs)
    for k in ('chinstrap','gentoo','relative'):
        assert math.isclose(r['baseline']['C'][k],r['within_source']['C'][k]+r['between_source']['C'][k],abs_tol=1e-12)
    assert math.isclose(r['baseline']['D'],r['within_source']['D']+r['between_source']['D'])
    assert r['within_source']['beta']['gentoo']==.5

def test_duplicate_original_interval_never_inflates_support():
    m=module();a=row('A',0,0,1)
    with pytest.raises(ValueError,match='duplicate'):
        m.partition([a,a])

def test_growth_identity_cannot_change_silently():
    m=module();r=row('A',0,0,1);r['annualized_log_ratio_change']=.4
    with pytest.raises(ValueError,match='species'):
        m.partition([r])

def test_metadata_nearest_neighbor_does_not_use_response_direction():
    m=module();rs=[]
    for s in ['A','B','C']:
        for y in range(2000,2003):rs.append(row(s,y,0,99 if s=='B' else -99,start=y))
    meta={s:{'latitude':-62,'longitude':lon} for s,lon in [('A',-58),('B',-58.1),('C',-59)]}
    r=m.nearest_matched(rs,meta,'A',min_pairs=3)
    assert r['selected_site']=='B' and r['n_exact_intervals']==3
    for z in rs:z['annualized_b_growth']=-float(z['annualized_b_growth'])
    assert m.nearest_matched(rs,meta,'A',min_pairs=3)['selected_site']=='B'

def test_nonoverlapping_calendar_keys_are_not_nearby_year_match():
    m=module();rs=[row('A',1,0,1,start=2000,gap=3),row('B',1,0,1,start=2001,gap=3)]
    meta={'A':{'latitude':-62,'longitude':-58},'B':{'latitude':-62,'longitude':-58.01}}
    assert m.nearest_matched(rs,meta,'A',min_pairs=1)['selected_site'] is None

def test_one_nest_sensitivity_is_math_not_assumed_error():
    m=module();assert math.isclose(m.one_nest_log_step(9),math.log(10/9))
    assert m.one_nest_log_step(9)>m.one_nest_log_step(4635)
    with pytest.raises(ValueError):m.one_nest_log_step(0)

def test_constant_ice_has_no_estimable_slope():
    m=module();r=m.partition([row('A',1,2,5),row('A',1,-2,10,start=2001)])
    assert r['baseline']['beta']['relative'] is None

def test_official_primary_lineage_does_not_equate_compilation_to_one_survey():
    m=module()
    assert m.primary_lineage(1984,'CHPE')!=m.primary_lineage(1984,'GEPE')
    assert m.primary_lineage(1981,'CHPE')!=m.primary_lineage(1983,'CHPE')
    assert m.primary_lineage(1996,'CHPE')==m.primary_lineage(1996,'GEPE')=='INACH_Valencia_project'
    assert m.primary_lineage(1986,'CHPE') is None
    assert m.primary_lineage(2020,'CHPE') is None

def test_official_same_project_subset_uses_lineage_not_count_direction():
    m=module();a=row('ARDL',1,0,5,start=1983,cite='meeting2009management150')
    b=row('ARDL',-2,9,-1,start=1994,cite='meeting2009management150')
    assert not m.same_primary_project(a)
    assert m.same_primary_project(b)
