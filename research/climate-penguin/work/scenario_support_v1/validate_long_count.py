"""Independent dummy regression and manually summed two-way cluster scores."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import t
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/long_count_seaice_v1'
d=pd.read_csv(OUT/'intervals.csv'); results=pd.read_csv(OUT/'associations.csv')
checked=0
for r in results.itertuples():
    a=d.copy()
    if r.scope!='all_annual': a=a[a.both_all_after_september]
    if r.scope=='timing_supported_without_victoria': a=a[a.region!='Victoria Land']
    cols=['site_id']+(['end'] if r.fixed_effects=='site_year' else [])
    controls=pd.get_dummies(a[cols].astype(str),drop_first=True,dtype=float).to_numpy()
    X=np.column_stack([np.ones(len(a)),controls,a[r.feature]])
    k=np.linalg.matrix_rank(X)
    if not np.isfinite(r.coefficient):
        assert len(a)-k<=0 or np.linalg.matrix_rank(X[:,:-1])==k
        continue
    beta=np.linalg.lstsq(X,a.log_growth,rcond=None)[0]
    assert np.isclose(beta[-1],r.coefficient,atol=1e-9)
    residual=a.log_growth.to_numpy()-X@beta
    rx=X[:,-1]-X[:,:-1]@np.linalg.lstsq(X[:,:-1],X[:,-1],rcond=None)[0]
    score=rx*residual
    pieces=[]
    for group in [a.site_id,a.end,a.site_id.astype(str)+'|'+a.end.astype(str)]:
        sums=pd.DataFrame({'group':group.to_numpy(),'score':score}).groupby('group').score.sum()
        g=len(sums)
        pieces.append(float((sums**2).sum())*g/(g-1)*(len(a)-1)/(len(a)-k))
    variance=(pieces[0]+pieces[1]-pieces[2])/(rx@rx)**2
    assert np.isclose(variance,r.cluster_variance,atol=1e-10)
    if variance>0:
        p=2*t.sf(abs(beta[-1]/np.sqrt(variance)),min(a.site_id.nunique(),a.end.nunique())-1)
        assert np.isclose(p,r.p,atol=1e-9)
    checked+=1
result={'passed':True,'coefficient_variance_p_checks':checked,'non_estimable_specs':len(results)-checked}
(OUT/'independent_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
