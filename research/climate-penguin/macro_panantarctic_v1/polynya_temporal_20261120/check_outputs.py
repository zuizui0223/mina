"""Independent real-data reconstruction; no alternative biological hypothesis."""
import json
import numpy as np
import pandas as pd
from scipy.stats import t
from run import HERE, Y, CONTROLS

d=pd.read_csv(HERE/'matched_analysis.csv');a=pd.read_csv(HERE/'annual_polynya.csv');r=pd.read_csv(HERE/'coefficients.csv')
assert len(d)==358 and d.site_id.nunique()==85 and d.source_region.nunique()==11
env=a.set_index(['site_id','year']).fraction
for row in d.itertuples():
    assert np.isclose(row.P0,env.loc[row.site_id,row.season])
    assert np.isclose(row.P1,env.loc[row.site_id,row.season+1])
days=pd.read_csv(HERE/'image_date_audit.csv',parse_dates=['date','winter_end','summer_end','lead_start'])
assert (days.date>days.winter_end).all() and (days.date<days.summer_end).all() and (days.date<days.lead_start).all()
assert (days.lead_start-days.date).dt.days.min()==93
days['doy_c']=(days.date-pd.to_datetime(days.season.astype(str)+'-11-01')).dt.days+1-60
days['doy_sq']=days.doy_c**2
timing=days.groupby(['site_id','season']).agg(mean_doy_centered=('doy_c','mean'),mean_doy_sq=('doy_sq','mean'))
for c in ['mean_doy_centered','mean_doy_sq']:
    assert np.allclose(d[c],timing.loc[list(zip(d.site_id,d.season)),c])
for name,features in [('Mnow',['P0']),('Mlead',['P1']),('Mjoint',['P0','P1'])]:
    cols=CONTROLS+features
    nuisance=pd.concat([pd.get_dummies(d.site_id,dtype=float),pd.get_dummies(d.region_year,dtype=float)],axis=1).to_numpy()
    z=d[cols].to_numpy();x=z-nuisance@np.linalg.lstsq(nuisance,z,rcond=None)[0]
    y=d[Y].to_numpy();y-=nuisance@np.linalg.lstsq(nuisance,y,rcond=None)[0]
    b=np.linalg.lstsq(x,y,rcond=None)[0];error=y-x@b
    scores=np.array([x[d.source_region.eq(g)].T@error[d.source_region.eq(g)] for g in d.source_region.unique()])
    n,k=x.shape;g=len(scores);bread=np.linalg.inv(x.T@x)
    cov=bread@scores.T@scores@bread*g/(g-1)*(n-1)/(n-k)
    for row in r[r.model.eq(name)].itertuples():
        v=np.zeros(k)
        if row.term=='P0_minus_P1':v[-2:]=[.1,-.1]
        else:v[cols.index(row.term)]=.1
        beta=v@b;se=np.sqrt(v@cov@v);ci=beta+np.array([-1,1])*t.ppf(.975,g-1)*se
        assert np.allclose([beta,se,*ci],[row.beta_per_10pp,row.se,row.lower,row.upper],atol=1e-8)
loo=pd.read_csv(HERE/'region_omissions.csv')
assert len(loo)==33 and loo[loo.term.isin(['P0','P0_minus_P1'])].beta_per_10pp.lt(0).all()
assert json.loads((HERE/'verdict.json').read_text())['verdict']=='TIME_SPECIFICITY_SUPPORTED'
print('PASS source winter pairing, all image dates/DOY, independent FE projection and covariance for every reported coefficient/contrast, all omission signs')
