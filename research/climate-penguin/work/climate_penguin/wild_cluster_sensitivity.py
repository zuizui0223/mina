"""Null-imposed Rademacher wild cluster bootstrap, one-way sensitivities."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster
from statsmodels.stats.multitest import multipletests
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
points=pd.read_csv(OUT/'exploratory_significance_points.csv')
tests=pd.read_csv(OUT/'exploratory_significance_results.csv')
rng=np.random.default_rng(2026102907);rows=[];verified=0
keys=['cohort','species','predictor']
groups={k:g for k,g in points.groupby(keys,sort=False)}
for it,row in tests.iterrows():
    a=groups[tuple(row[k] for k in keys)]
    n=len(a);z=np.column_stack([np.ones(n),pd.get_dummies(a.cam,drop_first=True,dtype=float)])
    if row.time_mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.season_start_year,drop_first=True,dtype=float)])
    X=np.column_stack([z,a.x]);y=a.y.to_numpy();k=X.shape[1]
    out={c:row[c] for c in keys+['time_mode','code_seasons','sites','years']}
    if n-np.linalg.matrix_rank(X)<=2 or np.linalg.matrix_rank(X)<k or min(row.sites,row.years)<3:
        out['status']='insufficient_support';rows.append(out);continue
    pinv=np.linalg.pinv(X);coef=pinv@y;resid=y-X@coef
    assert np.isclose(coef[-1],row.coefficient,atol=1e-7,rtol=1e-6)
    nullfit=z@np.linalg.lstsq(z,y,rcond=None)[0];nullres=y-nullfit
    out['coefficient']=float(coef[-1]);out['status']='computed'
    for label,column in [('site','cam'),('year','season_start_year')]:
        codes,inv=np.unique(a[column],return_inverse=True);G=len(codes)
        H=np.eye(G)[inv].T;factor=G/(G-1)*(n-1)/(n-k)
        v=pinv[-1];obsse=np.sqrt(factor*np.sum((H@(v*resid))**2));observed=abs(coef[-1]/obsse)
        full=G<=12
        weights=2*((np.arange(2**G)[:,None]>>np.arange(G))&1)-1 if full else rng.choice([-1.,1.],size=(9999,G))
        # Vectorized refits; each column is one complete cluster-weight draw.
        Y=nullfit[:,None]+nullres[:,None]*weights[:,inv].T
        B=pinv@Y;E=Y-X@B
        se=np.sqrt(factor*np.sum((H@(v[:,None]*E))**2,axis=0))
        valid=np.isfinite(se)&(se>1e-12)
        first=sm.OLS(Y[:,0],X).fit();vc=cov_cluster(first,inv,use_correction=True)
        assert np.isclose(B[-1,0],first.params[-1],atol=1e-7,rtol=1e-6)
        assert np.isclose(se[0]**2,vc[-1,-1],atol=1e-9,rtol=1e-6)
        verified+=1
        exceed=int((np.abs(B[-1,valid]/se[valid])>=observed-1e-10).sum())
        p=exceed/len(weights) if full else (exceed+1)/(len(weights)+1)
        out.update({f'p_wild_{label}':p if valid.all() else np.nan,f'weights_{label}':len(weights),f'valid_weights_{label}':int(valid.sum()),f'enumerated_{label}':full,f'observed_abs_t_{label}':float(observed)})
    rows.append(out)
    if it%40==0:print('completed',it+1,flush=True)
r=pd.DataFrame(rows);assert len(r)==216
r['p_wild_max']=r[['p_wild_site','p_wild_year']].max(axis=1,skipna=False)
for suffix in ['site','year','max']:
    for name,method in [('bh','fdr_bh'),('by','fdr_by')]:
        col=f'p_wild_{suffix}';q=f'q_wild_{suffix}_{name}'
        r[q]=multipletests(r[col].fillna(1),method=method)[1];r.loc[r[col].isna(),q]=np.nan
r.to_csv(OUT/'wild_cluster_sensitivity_results.csv',index=False)
checks=dict(family_size=len(r),verified_bootstrap_refits=verified,seed=2026102907,
    nominal_p_below_05={s:int(r[f'p_wild_{s}'].lt(.05).sum()) for s in ['site','year','max']},
    bh_below_05={s:int(r[f'q_wild_{s}_bh'].lt(.05).sum()) for s in ['site','year','max']},
    by_below_05={s:int(r[f'q_wild_{s}_by'].lt(.05).sum()) for s in ['site','year','max']},
    source_sha256={f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in ['exploratory_significance_points.csv','exploratory_significance_results.csv']},
    exact_randomization_test=False,multiway_dependence_solved=False)
(OUT/'wild_cluster_sensitivity_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2));print(r.sort_values('p_wild_max').head(8).to_string(index=False))
