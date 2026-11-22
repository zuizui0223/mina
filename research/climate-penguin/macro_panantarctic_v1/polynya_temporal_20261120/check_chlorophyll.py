"""Recompute frozen source gates and path estimates independently from saved data."""
import json
import numpy as np
import pandas as pd
from run import HERE, CONTROLS, Y
from chl_models import NAMES

s=pd.read_csv(HERE/'chlorophyll_screen_support.csv')
m=pd.read_csv(HERE/'chlorophyll_screen_monthly.csv')
daily=pd.read_csv(HERE/'chlorophyll_screen_daily.csv',parse_dates=['date'])
assert len(s)==358 and not s.duplicated(['site_id','season']).any()
assert not daily.duplicated(['site_id','season','date']).any()
for r in m.itertuples():
    q=daily[(daily.site_id==r.site_id)&(daily.season==r.season)&(daily.month==r.month)]
    valid=q[q.coverage.ge(.2)&q.chlor_a.gt(0)]
    assert len(valid)==r.n_days
    assert (len(valid)>=5 and np.where(valid.date.dt.day<=15,1,2).size>0 and len(set(np.where(valid.date.dt.day<=15,1,2)))==2)==r.passes
    if r.passes:assert np.isclose(valid.chlor_a.mean(),r.chlor_a)
for r in s.itertuples():
    q=m[(m.site_id==r.site_id)&(m.season==r.season)]
    if r.status=='ELIGIBLE':
        assert len(q)==4 and q.passes.all()
        assert np.isclose(r.C,np.log10(q.chlor_a.mean()))
    else:assert (~q.passes).any()
assert s.status.eq('ELIGIBLE').sum()==112
d=pd.read_csv(HERE/'chlorophyll_matched_analysis.csv')
cols=CONTROLS+['P0','P1']
fe=pd.concat([pd.get_dummies(d.site_id,dtype=float),pd.get_dummies(d.region_year,dtype=float)],axis=1).to_numpy()
x0=np.column_stack([d[cols],fe]);x1=np.column_stack([d[cols+['C']],fe])
a=np.linalg.lstsq(x0,d.C,rcond=None)[0][5]*.1
b0=np.linalg.lstsq(x0,d[Y],rcond=None)[0][5]*.1
f=np.linalg.lstsq(x1,d[Y],rcond=None)[0];b=f[7];b1=f[5]*.1
point=np.array([a,b,a*b,b1-b0,b0,b1])
reported=pd.read_csv(HERE/'chlorophyll_pathway_coefficients.csv')
assert reported.term.tolist()==NAMES and np.allclose(point,reported.estimate,atol=1e-8)
boot=pd.read_csv(HERE/'chlorophyll_region_bootstrap.csv')
assert len(boot)==4999 and boot.valid.sum()==4867
ci=np.quantile(boot.loc[boot.valid,NAMES],[.025,.975],axis=0)
assert np.allclose(ci[0],reported.lower) and np.allclose(ci[1],reported.upper)
assert np.allclose(boot.loc[boot.valid,'a_times_b_per10pp'],-boot.loc[boot.valid,'delta_beta_P0_per10pp'],atol=1e-7)
assert json.loads((HERE/'chlorophyll_model_verdict.json').read_text())['status']=='PATHWAY_CONSISTENCY_NOT_ESTABLISHED'
print('PASS daily/monthly/seasonal eligibility, equal-month log aggregate, explicit FE pathway fits, all fixed bootstrap quantiles; no mediation confirmation')
