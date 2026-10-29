"""Post-exploration two-way cluster inference; not confirmatory analysis."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups
from statsmodels.stats.multitest import multipletests
from scipy.stats import t
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
sources={
 'extended_analysis_cohort.csv':['spgmedian','near_sic_mean_month9','far_sic_mean_month9','edge_distance_km','drift_m9_east_km_day','drift_m9_north_km_day'],
 'behavior_ocean_join.csv':['ocean_m9_surface_salinity','ocean_m9_surface_potential_temperature_c','ocean_m9_mixed_layer_depth_m'],
 'behavior_seasonal_ice_join.csv':['augsep_sic_mean','augsep_sic_sd','augsep_absolute_daily_change','augsep_low15_days','augsep_low30_days','augsep_low15_upcrossings','augsep_low30_upcrossings','low15_transition_day_from_aug1','low30_transition_day_from_aug1']}
rows=[];points=[];hashes={};manual_checks=0
for filename,variables in sources.items():
    p=pd.read_csv(OUT/filename);hashes[filename]=hashlib.sha256((OUT/filename).read_bytes()).hexdigest()
    if 'drift_m9_screen_pass' in p:
        for v in ['drift_m9_east_km_day','drift_m9_north_km_day']:
            p.loc[~p.drift_m9_screen_pass.eq(True),v]=np.nan
    for cohort in ['csv_labels','appendix_range_consistent']:
        sub=p if cohort=='csv_labels' else p[p.appendix_range_consistent.eq(True)]
        for species,g in sub.groupby('species'):
            for variable in variables:
                a=g.dropna(subset=[variable,'settlement']).groupby(['cam','season_start_year']).agg(x=(variable,'mean'),y=('settlement','mean'),camera_rows=('settlement','size')).reset_index()
                a=a[a.cam.isin(a.groupby('cam').size().loc[lambda x:x>=2].index)].copy()
                a['cohort']=cohort;a['species']=species;a['predictor']=variable;points.append(a)
                site=pd.factorize(a.cam)[0];year=pd.factorize(a.season_start_year)[0]
                ns=a.cam.nunique();ny=a.season_start_year.nunique();n=len(a)
                for mode in ['site','site_year']:
                    row=dict(cohort=cohort,species=species,predictor=variable,time_mode=mode,code_seasons=n,sites=ns,years=ny,camera_rows=int(a.camera_rows.sum()),status='pending',p=np.nan,small_cluster_warning=min(ns,ny)<20)
                    z=np.column_stack([np.ones(n),pd.get_dummies(a.cam,drop_first=True,dtype=float)])
                    if mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.season_start_year,drop_first=True,dtype=float)])
                    x=a.x.to_numpy();y=a.y.to_numpy();xr=x-z@np.linalg.lstsq(z,x,rcond=None)[0];yr=y-z@np.linalg.lstsq(z,y,rcond=None)[0]
                    X=np.column_stack([z,x]);rank=np.linalg.matrix_rank(X);df=n-rank
                    row.update(residual_df=df,cluster_t_df=min(ns,ny)-1)
                    if df<=2 or min(ns,ny)<3 or np.std(xr)<1e-9 or rank<X.shape[1]:
                        row['status']='insufficient_support_or_rank';rows.append(row);continue
                    fit=sm.OLS(y,X).fit();coef=float(fit.params[-1]);cov,cov_site,cov_year=cov_cluster_2groups(fit,site,year,use_correction=True)
                    # Independent sandwich reconstruction for every estimable model.
                    scores=X*fit.resid[:,None];bread=np.linalg.inv(X.T@X)
                    def vc(groups):
                        _,inv=np.unique(groups,axis=0,return_inverse=True)
                        sums=np.zeros((inv.max()+1,X.shape[1]));np.add.at(sums,inv,scores)
                        G=len(sums);return bread@(sums.T@sums)@bread*(G/(G-1))*((n-1)/(n-X.shape[1]))
                    manual=vc(site)+vc(year)-vc(np.column_stack([site,year]))
                    assert np.isclose(manual[-1,-1],cov[-1,-1],rtol=1e-5,atol=1e-7)
                    assert np.isclose(coef,(xr@yr)/(xr@xr),rtol=1e-6,atol=1e-7)
                    manual_checks+=1
                    for label,onecov,G in [('site',cov_site,ns),('year',cov_year,ny)]:
                        var=float(onecov[-1,-1]);se_one=np.sqrt(var) if var>0 else np.nan
                        row['se_'+label]=float(se_one)
                        row['p_'+label]=float(2*t.sf(abs(coef/se_one),G-1)) if var>0 else np.nan
                    row.update(coefficient=coef,adjusted_r=float(np.corrcoef(xr,yr)[0,1]),variance=float(cov[-1,-1]))
                    if not np.isfinite(cov[-1,-1]) or cov[-1,-1]<=0:
                        row['status']='nonpositive_cluster_variance';rows.append(row);continue
                    se=np.sqrt(cov[-1,-1]);tdf=min(ns,ny)-1;critical=t.ppf(.975,tdf)
                    row.update(status='approximate_test',se=float(se),ci_low=coef-critical*se,ci_high=coef+critical*se,p=float(2*t.sf(abs(coef/se),tdf)))
                    rows.append(row)
r=pd.DataFrame(rows);assert len(r)==216
for name,method in [('q_bh','fdr_bh'),('q_by','fdr_by')]:
    r[name]=multipletests(r.p.fillna(1).to_numpy(),method=method)[1]
    r.loc[r.p.isna(),name]=np.nan
r['p_covariance_sensitivity_max']=r[['p','p_site','p_year']].max(axis=1,skipna=False)
r['q_by_covariance_sensitivity']=multipletests(r.p_covariance_sensitivity_max.fillna(1),method='fdr_by')[1]
r.loc[r.p_covariance_sensitivity_max.isna(),'q_by_covariance_sensitivity']=np.nan
r['exploratory_by_below_05']=r.q_by.lt(.05)
r.to_csv(OUT/'exploratory_significance_results.csv',index=False)
pd.concat(points,ignore_index=True).to_csv(OUT/'exploratory_significance_points.csv',index=False)
checks=dict(source_sha256=hashes,family_size=len(r),estimable_manual_covariance_checks=manual_checks,status_counts=r.status.value_counts().to_dict(),raw_p_below_05=int(r.p.lt(.05).sum()),bh_below_05=int(r.q_bh.lt(.05).sum()),by_below_05=int(r.q_by.lt(.05).sum()),all_tests_post_exploration=True,calendar_reconciled=False)
(OUT/'exploratory_significance_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2));print(r.sort_values('p').head(12).to_string(index=False))
