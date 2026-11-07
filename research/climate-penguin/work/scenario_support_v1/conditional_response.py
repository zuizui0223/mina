"""Conditional index shifts, retaining climate-model and transformation choices.

No absolute settlement date, causal effect, or calibrated biological forecast.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/relationship_response_v1'))
from analyze import fe_fit
OUT=ROOT/'outputs/conditional_response_v1';OUT.mkdir(exist_ok=True)
paths=[ROOT/'outputs/relationship_response_v1/cohort.csv',ROOT/'outputs/scenario_support_v1/observed_range_audit.csv',ROOT/'outputs/scenario_support_v1/recent_comparison/overlap_site_levels.csv']
cohort=pd.read_csv(paths[0]);future=pd.read_csv(paths[1]);baseline=pd.read_csv(paths[2])
baseline=baseline.rename(columns={'scenario_branch':'experiment_id','model_mean':'matched_model_baseline'})
keys=['scope','species','cam','source_id','member_id','variable_id','experiment_id']
j=future.merge(baseline[keys+['matched_model_baseline']],on=keys,validate='many_to_one')
assert len(j)==len(future)
j=j[j.variable_id.isin(['tas','siconc'])].copy()
# Identity-preserving bounded fractional change. Decreases scale the ice
# fraction; increases scale the remaining open-water fraction. No eps/clipping.
def bounded(observed,base,target):
    assert 0<=observed<=100 and 0<=base<=100 and 0<=target<=100
    if target==base:return observed
    if target<base:return observed*target/base
    return observed+(100-observed)*(target-base)/(100-base)
for obs in [0.,10.,70.,100.]:
    for base in [0.,20.,100.]:
        assert bounded(obs,base,base)==obs
        for target in [0.,10.,100.]:assert 0<=bounded(obs,base,target)<=100
j['additive_future']=j.observed_mean+j.future_model_mean-j.matched_model_baseline
j['bounded_future']=[bounded(r.observed_mean,r.matched_model_baseline,r.future_model_mean) if r.variable_id=='siconc' else r.additive_future for r in j.itertuples()]
j.to_csv(OUT/'climate_transformations.csv',index=False)
index=['scope','species','cam','source_id','member_id','experiment_id','period']
rows=[];coef=[];summary=[];rng=np.random.default_rng(20261030)
for (scope,species),a in cohort.groupby(['scope','species']):
    for mode in ['site','site_year']:
        beta,info=fe_fit(a,['airC','ice10'],mode)
        assert beta is not None
        boot={}
        for cluster in ['cam','year']:
            groups,inv=np.unique(a[cluster],return_inverse=True);samples=[]
            for _ in range(999):
                weights=np.bincount(rng.integers(len(groups),size=len(groups)),minlength=len(groups))[inv]
                b,_=fe_fit(a,['airC','ice10'],mode,weights)
                if b is not None:samples.append(b)
            boot[cluster]=np.asarray(samples)
        coef.append(dict(scope=scope,species=species,mode=mode,n=len(a),sites=a.cam.nunique(),air_coefficient=beta[0],ice10_coefficient=beta[1],cam_boot_valid=len(boot['cam']),year_boot_valid=len(boot['year'])))
        f=j[(j.scope==scope)&(j.species==species)]
        for transform in ['additive','bounded']:
            p=f.pivot(index=index,columns='variable_id',values=transform+'_future').reset_index()
            observed=f.pivot(index=index,columns='variable_id',values='observed_mean').reset_index()
            assert p[index].equals(observed[index])
            p['delta_air']=p.tas-observed.tas;p['delta_ice10']=(p.siconc-observed.siconc)/10
            p['physical_ice']=p.siconc.between(0,100)
            p['index_shift']=p.delta_air*beta[0]+p.delta_ice10*beta[1]
            p.loc[~p.physical_ice,'index_shift']=np.nan
            p['mode']=mode;p['transform']=transform
            p['outside_air_ice_marginal_range']=~(p.tas.between(a.airC.min(),a.airC.max())&p.siconc.between(a.ice10.min()*10,a.ice10.max()*10))
            rows.append(p)
            for key,g in p.groupby(['source_id','experiment_id','period']):
                complete=bool(g.physical_ice.all())
                rec=dict(scope=scope,species=species,mode=mode,transform=transform,source_id=key[0],experiment_id=key[1],period=key[2],species_sites=len(g),invalid_ice=int((~g.physical_ice).sum()),outside_marginal_range=int(g.outside_air_ice_marginal_range.sum()),all_sites_physical=complete,mean_index_shift=np.nan)
                # Do not silently drop impossible sites and change the target.
                if complete:
                    change=g[['delta_air','delta_ice10']].mean().to_numpy()
                    rec['mean_index_shift']=float(change@beta)
                    for cluster in ['cam','year']:
                        values=boot[cluster]@change
                        rec[cluster+'_resample_low'],rec[cluster+'_resample_high']=np.quantile(values,[.025,.975])
                summary.append(rec)
pd.concat(rows,ignore_index=True).to_csv(OUT/'site_index_shifts.csv',index=False)
pd.DataFrame(coef).to_csv(OUT/'coefficients.csv',index=False)
summary=pd.DataFrame(summary);summary.to_csv(OUT/'conditional_summary.csv',index=False)
receipt={'status':'conditional_sensitivity_not_calibrated_forecast','regressions':len(coef),'scenario_summaries':len(summary),'resamples_per_cluster':999,'seed':20261030,
 'inputs':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
 'limitations':['Response is an index change, not a calendar date or absolute breeding date',
 'Two-environment reduced model omits ocean temperature, salinity, drift, snow and vegetation',
 'Mean future environment conditional scenario excludes projected site/year effects and internal variability',
 'Bounded fractional transformation is unvalidated; physical plausibility does not establish statistical calibration',
 'Site/year resampling intervals separately reflect coefficient sensitivity, not full forecast uncertainty',
 'No p value, effect selection or causal interpretation; all models and both transformations retained',
 'Same-century model reference uses the actual observed years for each site; this is not a uniform climatological baseline']}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(summary[(summary.scope=='all_source_labels')&(summary['mode']=='site')&(summary['transform']=='bounded')&(summary.period=='2081-2100')&(summary.experiment_id=='ssp585')].to_string(index=False))
