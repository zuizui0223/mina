"""Observed low-ice duration changes, without imputing censored retreat dates."""
from pathlib import Path
import hashlib,json,itertools
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups
from statsmodels.stats.multitest import multipletests
from scipy.stats import t as student
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'low_ice_days_count_v1';out.mkdir(exist_ok=True)
src=root/'long_ice_timing_v1/count_interval_features.csv';d=pd.read_csv(src)
assert len(d)==301*8 and d.gap.eq(1).all() and d.same_known_method.all()
assert (d[['n_start','n_end']]>0).all().all()
assert np.array_equal(d.low_days_change.to_numpy(),(d.end_low_days-d.start_low_days).to_numpy())
d['log_growth']=np.log(d.n_end/d.n_start);d['low_days_change10']=d.low_days_change/10
rows=[];support=[];rng=np.random.default_rng(20261030)
for (window,threshold,band),g in d.groupby(['window','threshold','inner_km']):
    for scope in ['all_annual','timing_supported','timing_supported_without_victoria']:
        a=g.copy()
        if scope!='all_annual':a=a[a.timing_supported]
        if scope.endswith('without_victoria'):a=a[a.region!='Victoria Land']
        for region,q in a.groupby('region'):
            support.append(dict(window=window,threshold=threshold,inner_km=band,scope=scope,region=region,
                n=len(q),nonzero_changes=int(q.low_days_change.ne(0).sum()),sites=q.site_id.nunique()))
        for mode in ['site','site_year']:
            z=pd.get_dummies(a.site_id,dtype=float).to_numpy()
            if mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.end,drop_first=True,dtype=float)])
            u,_,_=np.linalg.svd(z,full_matrices=False);z=u[:,:np.linalg.matrix_rank(z)]
            x=a.low_days_change10.to_numpy();y=a.log_growth.to_numpy()
            rx=x-z@(z.T@x);ry=y-z@(z.T@y);design=np.column_stack([z,x])
            df=len(a)-np.linalg.matrix_rank(design)
            r=dict(window=window,threshold=threshold,inner_km=band,scope=scope,mode=mode,n=len(a),
                sites=a.site_id.nunique(),years=a.end.nunique(),regions=a.region.nunique(),
                nonzero_changes=int(a.low_days_change.ne(0).sum()),nonzero_change_sites=a.loc[a.low_days_change.ne(0),'site_id'].nunique(),
                residual_df=df,status='not_identified',partial_r=np.nan,beta_per_10days=np.nan,p=np.nan,ci_low=np.nan,ci_high=np.nan)
            if rx@rx>1e-12 and ry@ry>1e-12 and df>0:
                fit=sm.OLS(y,design).fit();beta=rx@ry/(rx@rx)
                assert np.isclose(beta,fit.params[-1],atol=1e-8)
                r.update(status='estimated',partial_r=rx@ry/np.sqrt((rx@rx)*(ry@ry)),beta_per_10days=beta)
                site_information=pd.Series(rx**2).groupby(a.site_id.to_numpy()).sum()
                r['effective_sites_after_residualization']=int((site_information>1e-8*(rx@rx)).sum())
                score=rx/np.sqrt(rx@rx);stat=(score@ry)**2
                for name,cluster in [('site',a.site_id),('year',a.end)]:
                    _,inv=np.unique(cluster,return_inverse=True);G=len(np.unique(inv))
                    exact=G<=12
                    signs=np.array(list(itertools.product([-1.,1.],repeat=G))) if exact else rng.choice([-1.,1.],size=(9999,G))
                    pseudo=ry[:,None]*signs[:,inv].T;stats=(score@pseudo)**2
                    count=int((stats>=stat-1e-10).sum())
                    r[name+'_sign_p']=count/len(stats) if exact else (count+1)/(len(stats)+1)
                    yp=z@(z.T@y)+pseudo[:,0]
                    er0=yp-z@np.linalg.lstsq(z,yp,rcond=None)[0];er1=yp-design@np.linalg.lstsq(design,yp,rcond=None)[0]
                    assert np.isclose(er0@er0-er1@er1,stats[0],atol=1e-7)
                r['sensitivity_max_p']=max(r['site_sign_p'],r['year_sign_p'])
                if min(r['sites'],r['years'])>1:
                    cov,cov_site,cov_year=cov_cluster_2groups(fit,pd.factorize(a.site_id)[0],pd.factorize(a.end)[0],use_correction=True)
                    variance=cov[-1,-1];cdf=min(r['sites'],r['years'])-1
                    r.update(cluster_variance=variance,inference_df=cdf)
                    scale=max(abs(cov_site[-1,-1]),abs(cov_year[-1,-1]),np.finfo(float).tiny)
                    if variance>0 and variance>100*np.finfo(float).eps*scale and r['effective_sites_after_residualization']>1:
                        se=np.sqrt(variance);crit=student.ppf(.975,cdf)
                        r.update(p=2*student.sf(abs(beta/se),cdf),ci_low=beta-crit*se,ci_high=beta+crit*se)
                    else:r['status']='estimated_degenerate_cluster_inference'
            rows.append(r)
result=pd.DataFrame(rows);assert len(result)==48
for method in ['fdr_bh','fdr_by']:result[method]=multipletests(result.p.fillna(1),method=method)[1]
for method in ['fdr_bh','fdr_by']:result['sign_'+method]=multipletests(result.sensitivity_max_p.fillna(1),method=method)[1]
result.to_csv(out/'associations.csv',index=False);pd.DataFrame(support).to_csv(out/'region_support.csv',index=False)
v=dict(status='observed_duration_association_not_retreat_date_or_transport',family_size=48,
    finite_p=int(result.p.notna().sum()),bh_below_005=int(result.fdr_bh.lt(.05).sum()),by_below_005=int(result.fdr_by.lt(.05).sum()),
    sign_bh_below_005=int(result.sign_fdr_bh.lt(.05).sum()),sign_by_below_005=int(result.sign_fdr_by.lt(.05).sum()),
    input_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
    limitations=['CR1 two-way site/end-year t approximation; few informative sites can invalidate apparent precision',
                'Observed days below threshold, not imputed event dates or final retreat',
                'All-annual includes uncertain temporal ordering; timing-supported is primary',
                '48 exploratory comparisons do not replace previous wider test families',
                'Separate site/year restricted sign flips are sensitivity diagnostics, not calibrated two-way inference'])
(out/'validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
print(result[(result.scope=='timing_supported')&(result['mode']=='site_year')][['window','threshold','inner_km','n','nonzero_changes','nonzero_change_sites','partial_r','p','fdr_bh']].to_string(index=False))
