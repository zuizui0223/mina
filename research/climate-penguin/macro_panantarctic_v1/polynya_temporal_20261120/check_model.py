"""Model algebra tests independent of biological outcomes."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t
from run import CONTROLS, Y, fit, residualize

rng=np.random.default_rng(20261120)
d=pd.DataFrame([(f'r{r}',f'r{r}s{s}',y) for r in range(8) for s in range(4) for y in range(6)],columns=['source_region','site_id','season'])
d['region_year']=d.source_region+'_'+d.season.astype(str)
for c in CONTROLS:d[c]=rng.normal(size=len(d))
d['P0']=rng.uniform(0,.2,len(d));d['P1']=.5*d.P0+rng.uniform(0,.1,len(d))
site={s:rng.normal() for s in d.site_id.unique()};ry={s:rng.normal() for s in d.region_year.unique()}
d[Y]=-5*d.P0-d.P1+d[CONTROLS].to_numpy()@np.arange(1,6)+d.site_id.map(site)+d.region_year.map(ry)+rng.normal(0,.02,len(d))
rows,x,f=fit(d,['P0','P1'])
explicit=np.column_stack([d[CONTROLS+['P0','P1']],pd.get_dummies(d.site_id,dtype=float),pd.get_dummies(d.region_year,dtype=float)])
b=np.linalg.lstsq(explicit,d[Y],rcond=None)[0][:7]
assert np.allclose(b,f.params,atol=1e-9)
assert abs(rows[0]['beta_per_10pp']+.5)<.02
assert abs(rows[1]['beta_per_10pp']+.1)<.02
# Direct cluster-score sandwich, including the original model's finite correction.
scores=[]
for region in d.source_region.unique():
    mask=d.source_region.eq(region).to_numpy();scores.append(x[mask].T@f.resid[mask])
scores=np.asarray(scores);bread=np.linalg.inv(x.T@x);n,k=x.shape;g=len(scores)
cov=bread@scores.T@scores@bread*(g/(g-1))*((n-1)/(n-k))
v=np.array([0.]*5+[.1,-.1]);se=np.sqrt(v@cov@v)
assert np.isclose(rows[-1]['se'],se)
assert np.isclose(rows[-1]['upper'],v@b+t.ppf(.975,g-1)*se)
rr=residualize(d[['P0','P1']],d)
assert np.max(abs(pd.DataFrame(rr).groupby(d.site_id).mean().to_numpy()))<1e-8
assert np.max(abs(pd.DataFrame(rr).groupby(d.region_year).mean().to_numpy()))<1e-8
shuffled=d.sample(frac=1,random_state=5).reset_index(drop=True)
other,_,_=fit(shuffled,['P0','P1'])
assert np.allclose([r['beta_per_10pp'] for r in rows],[r['beta_per_10pp'] for r in other])
print('PASS explicit fixed effects, full covariance contrast, cluster t interval, projection, row-order invariance')
