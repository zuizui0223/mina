"""Original observed seasons are neither interpolated years nor independent islands."""
import importlib.util
import math
from pathlib import Path
import pytest

P=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/matched_observed_intervals_v6.py'
spec=importlib.util.spec_from_file_location('observed_v6',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
S={'A':{'site_id':'A','site_name':'Site A','region':'R1'}}

def rec(i,sp,year,n=10,source='ref',method='ground',presence='1',site='A'):
    return dict(id=str(i),site_id=site,species_id=sp,season=str(year),
                type='nests',count=str(n),presence=presence,citekey=source,
                vantage=method,year=str(year),month='',day='',date='')

def joint(year,aid=1,n_a=10,n_b=10,**kw):
    return [rec(aid,'ADPE',year,n_a,**kw),rec(aid+1,'GEPE',year,n_b,**kw)]

def test_exact_elapsed_rate_and_no_fabricated_annual_records():
    r=joint(2000)+joint(2003,3,n_a=20,n_b=80)
    out,_=m.build_intervals(r,S,'ADPE','GEPE')
    assert len(out)==1 and out[0]['gap']==3
    assert math.isclose(out[0]['annualized_log_ratio_change'], math.log(4)/3)
    assert out[0]['source_a_start']=='1' and out[0]['source_b_end']=='4'
    assert out[0]['start']==2000 and out[0]['end']==2003

def test_only_adjacent_observed_joint_endpoints_not_all_combinations():
    r=joint(2000)+joint(2003,3)+joint(2005,5)
    out,_=m.build_intervals(r,S,'ADPE','GEPE')
    assert [(x['start'],x['end']) for x in out]==[(2000,2003),(2003,2005)]

@pytest.mark.parametrize('middle',[
    rec(8,'ADPE',2002,0,presence='0'),
    rec(8,'ADPE',2002,0),
    rec(8,'ADPE',2002,'bad'),
    rec(8,'ADPE',2002,10,source='other'),
    rec(8,'ADPE',2002,10,method='aerial')])
def test_intervening_conflicts_block_instead_of_hiding_disappearance(middle):
    out,audit=m.build_intervals(joint(2000)+[middle]+joint(2003,3),S,'ADPE','GEPE')
    assert out==[] and audit['intervening_conflict']==1

def test_single_positive_same_source_visit_is_not_an_absence():
    out,_=m.build_intervals(joint(2000)+[rec(8,'ADPE',2002,20)]+joint(2003,3),S,'ADPE','GEPE')
    assert len(out)==1 and out[0]['gap']==3

def test_duplicate_endpoint_or_intermediate_is_not_silently_deduplicated():
    r=joint(2000)+joint(2003,3)+[rec(9,'ADPE',2003)]+joint(2005,5)
    out,audit=m.build_intervals(r,S,'ADPE','GEPE')
    assert out==[] and audit['intervening_conflict']==1

def test_cross_species_or_temporal_source_mismatch_not_matched():
    r=joint(2000)+joint(2003,3,source='other')
    out,audit=m.build_intervals(r,S,'ADPE','GEPE')
    assert out==[] and audit['endpoint_context_change']==1
    r=joint(2000)+[rec(3,'ADPE',2003),rec(4,'GEPE',2003,source='other')]
    assert m.build_intervals(r,S,'ADPE','GEPE')[0]==[]

def test_duplicate_original_ID_is_a_hard_error():
    r=joint(2000)+joint(2003,1)
    with pytest.raises(ValueError,match='duplicate observation'):
        m.build_intervals(r,S,'ADPE','GEPE')

def simple(site,start,end,total,region='R1'):
    return dict(site_id=site,start=start,end=end,gap=end-start,region=region,
                log_ratio_change=total,annualized_log_ratio_change=total/(end-start))

def test_duration_weighting_is_not_annual_interpolation_or_equal_gap_weighting():
    rr=[simple('A',2000,2001,1),simple('A',2001,2010,0),simple('B',2000,2001,.3)]
    x=m.summarize(rr)
    assert math.isclose(x['equal_site_mean_annualized_rate'],.2)
    assert math.isclose(x['equal_site_mean_of_interval_rates'],.4)
    assert x['n_intervals']==3 and x['observed_gap_sum_site_seasons']==11

def test_land_aggregation_holds_nearby_points_and_mainland_out():
    rr=[simple(s,2000,2002,x) for s,x in [('A',.4),('B',.8),('C',1.2),('D',99),('E',99)]]
    geo={s:dict(category='EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON',original_land_fid=f)
         for s,f in [('A',10),('B',10),('C',11),('D',17692),('E',12)]}
    geo['E']['category']='NEAR_ONLY_HOLD_NOT_EXACT'
    x=m.summarize(rr,geo)
    assert x['n_sites']==3 and x['n_mapped_land_units']==2
    assert math.isclose(x['equal_land_mean_annualized_rate'],.45)
    assert x['excluded_sites']==['D','E']

def test_source_identity_is_exact_not_whitespace_normalized():
    r=joint(2000)+joint(2003,3,source='ref ')
    out,audit=m.build_intervals(r,S,'ADPE','GEPE')
    assert out==[] and audit['endpoint_context_change']==1
