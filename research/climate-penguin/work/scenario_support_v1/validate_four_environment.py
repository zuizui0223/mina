"""Independent full-design regression and saved-output checks."""
from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/four_environment_scenarios_v1'
F=['airC','ice10','salt01','waterC']
c=pd.read_csv(ROOT/'outputs/relationship_response_v1/cohort.csv')
b=pd.read_csv(OUT/'coefficients.csv');p=pd.read_csv(OUT/'site_components.csv');s=pd.read_csv(OUT/'summary.csv')
assert len(b)==12 and len(p)==3936 and len(s)==288
for r in b.to_dict('records'):
    a=c[(c.scope==r['scope'])&(c.species==r['species'])]
    z=pd.get_dummies(a.cam,dtype=float)
    if r['mode']=='site_year':z=pd.concat([z,pd.get_dummies(a.year,drop_first=True,dtype=float)],axis=1)
    fit=sm.OLS(a.y.to_numpy(),np.column_stack([z,a[F]])).fit()
    assert np.allclose(fit.params[-4:],[r[f] for f in F],atol=1e-7)
valid=p.physical_ice
assert p.loc[~valid,'index_shift'].isna().all()
assert np.allclose(p.loc[valid,'index_shift'],p.loc[valid,['component_'+f for f in F]].sum(axis=1))
keys=['scope','species','mode','source_id','member_id','experiment_id','period','transform']
for key,a in p.groupby(keys):
    row=s
    for k,v in zip(keys,key):row=row[row[k]==v]
    assert len(row)==1
    r=row.iloc[0]
    if a.physical_ice.all():assert np.isclose(a.index_shift.mean(),r.mean_index_shift)
    else:assert pd.isna(r.mean_index_shift)
    assert r.outside_hull==a.outside_four_variable_hull.sum()
# Deterministic sample checked with a different convex-feasibility algorithm.
sample=p[p['mode']=='site'].iloc[::31]
for r in sample.to_dict('records'):
    a=c[(c.scope==r['scope'])&(c.species==r['species'])][F].to_numpy()
    center=a.mean(axis=0);scale=a.std(axis=0)
    x=(a-center)/scale;v=(np.array([r[f] for f in F])-center)/scale
    result=linprog(np.zeros(len(a)),A_eq=np.vstack([x.T,np.ones(len(a))]),b_eq=np.r_[v,1],bounds=(0,None),method='highs')
    assert result.status in [0,2]
    assert (result.status==2)==r['outside_four_variable_hull']
receipt=dict(status='passed',independent_regressions=12,saved_site_rows=3936,saved_summaries=288,
             sampled_hull_checks=len(sample),hull_check_scope='every 31st site-mode row only',
             limitations='Numerical checks do not validate causal, extrapolation or future temperature proxy assumptions')
(OUT/'independent_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt)
