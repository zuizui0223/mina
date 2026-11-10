import importlib.util
from datetime import date
from pathlib import Path
import pytest
np = pytest.importorskip("numpy")

SCRIPT=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/lagged_climate_v3.py'
def module():
    assert SCRIPT.exists(), 'lagged chronology implementation not yet written'
    spec=importlib.util.spec_from_file_location('lagged_climate_v3_test',SCRIPT)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_year_only_is_interval_not_invented_january_survey():
    m=module();x=m.census_bounds({'year':'2007','month':'','day':'','date':''})
    assert x == (date(2007,1,1),date(2007,12,31),'year')
    assert m.window_before({'year':'2007'},2006,11) is True
    assert m.window_before({'year':'2007'},2007,11) is False

def test_month_boundaries_and_conflicting_calendar_fields():
    m=module()
    assert m.census_bounds({'year':'2008','month':'2'}) == (date(2008,2,1),date(2008,2,29),'month')
    assert m.window_before({'year':'2007','month':'11','day':'4'},2007,11) is False
    assert m.window_before({'year':'2007','month':'12'},2007,11) is True
    with pytest.raises(ValueError,match='conflict'):
        m.census_bounds({'year':'2007','date':'2008-01-04'})
    with pytest.raises(ValueError): m.census_bounds({'season':'2007'})
    with pytest.raises(ValueError): m.census_bounds({'year':'2007','month':'2','day':'30'})
    assert m.census_bounds({'date':'2007-11-04'})==(date(2007,11,4),date(2007,11,4),'day')

def synthetic_rows():
    rows=[]
    for i in range(5):
        for year in range(2001,2009):
            x=(i-2)*((year%3)-1)*.2+.1*(year-2001)
            rows.append({'site_id':str(i),'end_year':year,'land_fid':str(i//2),
                         'x':x,'relative_growth':2.3*x+4*i+1.1*(year-2001)})
    return rows

def test_fixed_effects_recover_known_slope_and_do_not_interpret_saturation():
    m=module();rows=synthetic_rows()
    a=m.fit(rows,'x',True)
    assert abs(a['coefficient']-2.3)<1e-10
    assert a['residual_df']>0
    rows=[dict(site_id='one',end_year=2001+i,land_fid='one',x=float(i),relative_growth=2*i) for i in range(5)]
    a=m.fit(rows,'x',True)
    assert a['coefficient'] is None
    assert a['status'] in ('CLIMATE_COLLINEAR','SATURATED_NO_RESIDUAL_DF')

def test_land_weights_sum_equally_and_nonfinite_input_rejected():
    m=module();rows=synthetic_rows();w=m.equal_land_weights(rows)
    total={fid:sum(v for r,v in zip(rows,w) if r['land_fid']==fid) for fid in {r['land_fid'] for r in rows}}
    assert all(abs(v-1)<1e-12 for v in total.values())
    rows[0]['x']=float('nan')
    with pytest.raises(ValueError,match='nonfinite'):m.fit(rows,'x',False)

def test_monthly_source_duplicates_fail_and_missing_month_is_not_zero():
    m=module()
    def row(mon): return {'site_id':'A','year':'2006','month':str(mon),'complete_month':'True','air2m_mean_c':'-4',
                        'returned_grid_latitude':'-64.75','returned_grid_longitude':'-64.0'}
    a=[row(k) for k in (8,9,10,11)]
    lookup=m.monthly_index(a)
    assert m.seasonal_temp(lookup,'A',2006)==-4
    with pytest.raises(ValueError,match='duplicate'):m.monthly_index(a+[a[0]])
    assert m.seasonal_temp(m.monthly_index(a[:-1]),'A',2006) is None


def test_missing_year_is_not_replaced_by_season_and_lag_is_fixed():
    m=module()
    with pytest.raises(ValueError,match='year absent'):
        m.census_bounds({'season':'2011','month':'12'})
    assert m.MONTHS == (8,9,10,11)
    assert m.PRIMARY == ('ADPE','GEPE')
    assert m.TERMS == ('delta_concurrent_AugNov_C','delta_prior_AugNov_C')
    assert m.window_before({'year':'2011'},2010,11)
    assert not m.window_before({'year':'2011'},2011,11)


def test_duplicate_year_or_changed_grid_is_not_hidden_in_monthly_source():
    m=module()
    rows=[dict(site_id='A',year='2001',month=str(mm),complete_month='True',
      air2m_mean_c='-4',returned_grid_latitude='-64.75',returned_grid_longitude='-64.0')
      for mm in (8,9)]
    rows[1]['returned_grid_longitude']='-65.0'
    with pytest.raises(ValueError,match='grid changed'):
        m.monthly_index(rows)
