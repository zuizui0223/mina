from pathlib import Path
import json,hashlib
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
raw=pd.read_csv(OUT/'behavior_ocean_join.csv')
mapping={'ice10':'near_sic_mean_month9','salt01':'ocean_m9_surface_salinity','airC':'spgmedian','waterC':'ocean_m9_surface_potential_temperature_c'}
scales={'ice10':10.,'salt01':.1,'airC':1.,'waterC':1.}
models={'I':['airC','ice10'],'O':['airC','waterC','salt01'],'J':['airC','waterC','salt01','ice10']}
coeff=[];cohorts=[];bootrows=[];rng=np.random.default_rng(20261029)
def residual_fit(z,x,y,weights=None):
    w=np.ones(len(y)) if weights is None else np.sqrt(weights)
    zw=z*w[:,None];xw=x*w[:,None];yw=y*w
    xr=xw-zw@np.linalg.lstsq(zw,xw,rcond=None)[0]
    yr=yw-zw@np.linalg.lstsq(zw,yw,rcond=None)[0]
    if np.linalg.matrix_rank(xr)<x.shape[1]:return None,xr,yr
    return np.linalg.lstsq(xr,yr,rcond=None)[0],xr,yr
for cohort in ['csv_labels','appendix_range_consistent']:
    p=raw.copy()
    if cohort!='csv_labels':p=p[p.appendix_range_consistent]
    p=p.dropna(subset=list(mapping.values())+['settlement'])
    for species,g in p.groupby('species'):
        a=g.groupby(['cam','season_start_year']).agg(**{k:(v,'mean') for k,v in mapping.items()},y=('settlement','mean'),camera_rows=('settlement','size')).reset_index()
        a['cohort']=cohort;a['species']=species;cohorts.append(a.copy())
        for k in mapping:a[k]/=scales[k]
        for time_mode in ['none','linear','categorical']:
            z=np.column_stack([np.ones(len(a)),pd.get_dummies(a.cam,drop_first=True,dtype=float).to_numpy()])
            if time_mode=='linear':z=np.column_stack([z,a.season_start_year-a.season_start_year.mean()])
            if time_mode=='categorical':z=np.column_stack([z,pd.get_dummies(a.season_start_year,drop_first=True,dtype=float).to_numpy()])
            y=a.y.to_numpy()
            for model,cols in models.items():
                x=a[cols].to_numpy();beta,xr,yr=residual_fit(z,x,y)
                assert beta is not None
                rank=np.linalg.matrix_rank(np.column_stack([z,x]));df=len(a)-rank
                for j,v in enumerate(cols):
                    others=np.delete(xr,j,axis=1);e=xr[:,j]-others@np.linalg.lstsq(others,xr[:,j],rcond=None)[0]
                    vif=float(np.sum(xr[:,j]**2)/np.sum(e**2))
                    coeff.append(dict(cohort=cohort,species=species,time_mode=time_mode,model=model,variable=v,coefficient=float(beta[j]),vif=vif,code_seasons=len(a),geographic_codes=a.cam.nunique(),residual_df=df))
                if model=='J' and time_mode=='categorical':
                    codes,inv=np.unique(a.cam.to_numpy(),return_inverse=True);samples=[]
                    for _ in range(1000):
                        weights=np.bincount(rng.integers(0,len(codes),len(codes)),minlength=len(codes))[inv]
                        b,_,_=residual_fit(z,x,y,weights)
                        if b is not None:samples.append(b)
                    samples=np.asarray(samples)
                    for j,v in enumerate(cols):
                        bootrows.append(dict(cohort=cohort,species=species,variable=v,estimate=float(beta[j]),resample_low=float(np.quantile(samples[:,j],.025)),resample_high=float(np.quantile(samples[:,j],.975)),valid_resamples=len(samples),requested_resamples=1000))
pd.concat(cohorts,ignore_index=True).to_csv(OUT/'joint_association_cohorts.csv',index=False)
c=pd.DataFrame(coeff);c.to_csv(OUT/'joint_association_coefficients.csv',index=False)
b=pd.DataFrame(bootrows);b.to_csv(OUT/'joint_association_resampling.csv',index=False)
(OUT/'joint_association_checks.json').write_text(json.dumps({'source_sha256':hashlib.sha256((OUT/'behavior_ocean_join.csv').read_bytes()).hexdigest(),'models':models,'scales':scales,'source_calendar_reconciled':False,'causal':False,'model_fits':int(c[['cohort','species','time_mode','model']].drop_duplicates().shape[0])},indent=2))
print(c[(c.cohort=='csv_labels')&(c.model=='J')].to_string(index=False));print(b[(b.cohort=='csv_labels')&b.variable.isin(['ice10','salt01'])].to_string(index=False))
