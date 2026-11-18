"""V7 physical units and source rules, with synthetic outcomes only."""
import importlib.util
import math
from pathlib import Path
import numpy as np
import pytest
FILE=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/observed_interval_seaice_v7.py'

def mod():
    spec=importlib.util.spec_from_file_location('intervalseaice7',FILE)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert callable(getattr(m,'fit',None)), 'V7 interval-aware fitting is not implemented'
    return m

def synthetic():
    rows=[]
    for i in range(5):
        for j in range(7):
            start=1991+j; gap=1+j%3; end=start+gap
            x=(i-2)*(j%3-1)*.3+(j%2)*.1
            annual_a=-.03+.01*i+.12*x
            annual_b=.04+.01*i-.08*x
            rows.append(dict(site_id=f'S{i}',region='R0' if i<3 else 'R1',
                start=start,end=end,gap=gap,land_fid=i//2,
                x_ice_rate=x,annualized_a_growth=annual_a,
                annualized_b_growth=annual_b,annualized_log_ratio_change=annual_b-annual_a))
    return rows

def test_fit_recovers_separate_and_relative_coefficients():
    m=mod();z=m.fit(synthetic(),'site')
    assert z['status']=='DESCRIPTIVE_ONLY'
    assert abs(z['coefficients']['chinstrap']-.12)<1e-10
    assert abs(z['coefficients']['gentoo']+.08)<1e-10
    assert abs(z['coefficients']['relative']+.20)<1e-10
    assert abs(z['decomposition_error'])<1e-10
    assert z['p_values'] is None and z['confidence_intervals'] is None

def test_total_change_model_equivalent_to_duration_weighted_rates():
    m=mod();rows=synthetic();z=m.fit(rows,'site')
    g=np.array([r['gap'] for r in rows]);x=np.array([r['x_ice_rate']*r['gap'] for r in rows])
    y=np.array([r['annualized_log_ratio_change']*r['gap'] for r in rows])
    D=np.array([[r['gap']*float(r['site_id']==s) for s in sorted({r['site_id'] for r in rows})] for r in rows])
    X=np.column_stack((D,x))/np.sqrt(g[:,None]);Y=y/np.sqrt(g)
    b=np.linalg.lstsq(X,Y,rcond=None)[0][-1]
    assert abs(z['coefficients']['relative']-b)<1e-10

def test_region_endpoint_year_controls_not_endyear_only():
    m=mod();rows=synthetic()
    for r in rows:
        g=r['gap'];a=r['start'];b=r['end'];k=1 if r['region']=='R0' else -2
        change=k*(math.sin(b)-math.sin(a))/g
        r['annualized_b_growth']+=change
        r['annualized_log_ratio_change']+=change
    z=m.fit(rows,'region_endpoint_year')
    assert z['status']=='DESCRIPTIVE_ONLY'
    assert abs(z['coefficients']['relative']+.2)<1e-9

def test_singleton_site_carries_no_within_site_climate_information():
    m=mod();rows=synthetic();rows.append(dict(rows[0],site_id='single',x_ice_rate=40.,annualized_a_growth=200.,annualized_b_growth=-500.,annualized_log_ratio_change=-700.))
    z=m.fit(rows,'site')
    assert abs(z['coefficients']['relative']+.2)<1e-9
    assert z['x_information_by_site']['single']<1e-15

def test_zero_residual_df_hides_algebraic_coefficient():
    m=mod();rows=[dict(r,site_id='s') for r in synthetic()[:2]]
    rows[0]['x_ice_rate']=0.;rows[1]['x_ice_rate']=1.
    z=m.fit(rows,'site')
    assert z['status']=='SATURATED_NO_RESIDUAL_DF'
    assert z['coefficients']['relative'] is None

def test_constant_exposure_returns_collinear_not_zero_effect():
    m=mod();rows=synthetic()
    for r in rows:r['x_ice_rate']=2.
    z=m.fit(rows,'site')
    assert z['status']=='CLIMATE_COLLINEAR'
    assert z['coefficients']['relative'] is None

def test_equal_land_weights_preserve_total_weight_one_per_land():
    m=mod();rows=synthetic();w=m.weights(rows,'equal_land')
    for f in {r['land_fid'] for r in rows}:
        assert abs(sum(v for r,v in zip(rows,w) if r['land_fid']==f)-1)<1e-12
    with pytest.raises(ValueError):m.weights([dict(rows[0],land_fid=None)],'equal_land')

def test_false_string_month_support_is_not_true_and_missing_not_zero():
    m=mod()
    row=dict(site_id='X',start=2000,end=2003,gap=3,annualized_log_ratio_change=.1)
    monthly=[dict(site_id='X',year=y,month=mo,complete_spatial_support=True,sic_percent_mean=50 if y==1999 else 20) for y in (1999,2002) for mo in (8,9,10,11)]
    a=m.join_monthly([row],monthly)[0]
    assert a['x_ice_rate']==pytest.approx(-1.)
    monthly[0]['complete_spatial_support']='False'
    with pytest.raises(ValueError,match='support'):m.join_monthly([row],monthly)

def test_published_year_bounds_not_imputed_month():
    m=mod()
    assert m.prior_before({'year':'2000','month':'','day':'','date':''},1999)
    assert not m.prior_before({'year':'1999','month':'11','day':'','date':''},1999)
    with pytest.raises(ValueError):m.prior_before({'year':'','month':'','day':'','date':''},1999)

def test_wrong_interval_and_nonfinite_weights_rejected():
    m=mod();rows=synthetic();rows[0]['gap']=0
    with pytest.raises(ValueError):m.fit(rows,'site')
