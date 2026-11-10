"""Conditional scenario for original significant candidates, censoring preserved."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]/'outputs';SRC=ROOT/'daily_future_ice_v1'
OUT=ROOT/'daily_ice_candidate_scenarios_v1';OUT.mkdir(exist_ok=True)
rows=[]
for experiment in ['historical','ssp245','ssp585']:
    with np.load(SRC/f'daily_{experiment}.npz') as a:
        dates=pd.to_datetime(a['dates']);values=a['values'];locations=a['location_ids']
    for year in sorted(dates.year.unique()):
        mask=dates.year==year;v=values[mask];days=dates[mask]
        assert len(v)==122 and (np.diff(days.values)==np.timedelta64(1,'D')).all()
        for i,loc in enumerate(locations):
            seq=v[:,i]<15;starts=np.flatnonzero(np.convolve(seq.astype(int),np.ones(7,dtype=int),'valid')==7)
            status='already_low' if seq[:7].all() else ('observed_transition' if len(starts) else 'no_observed_transition')
            rows.append(dict(experiment_id=experiment,year=year,location_id=loc,
                augsep_low30_days=int((v[days.month<=9,i]<30).sum()),
                transition_status=status,low15_transition_day_from_aug1=float(starts[0]) if status=='observed_transition' else np.nan))
features=pd.DataFrame(rows);features.to_csv(OUT/'annual_features.csv',index=False)
rawpath=ROOT/'climate_penguin/extended_analysis_cohort.csv'
pointpath=ROOT/'climate_penguin/exploratory_significance_points.csv'
coefpath=ROOT/'climate_penguin/exploratory_significance_results.csv'
raw=pd.read_csv(rawpath);points=pd.read_csv(pointpath);coef=pd.read_csv(coefpath)
support=[];forecasts=[]
for sp,feature in [('Chinstrap','augsep_low30_days'),('Gentoo','low15_transition_day_from_aug1')]:
    obs=points[(points.species==sp)&(points.predictor==feature)&(points.cohort=='csv_labels')]
    b=coef[(coef.species==sp)&(coef.predictor==feature)&(coef.cohort=='csv_labels')&(coef.time_mode=='site_year')].iloc[0]
    for scenario in ['ssp245','ssp585']:
        base=features[(features.experiment_id=='historical')|((features.experiment_id==scenario)&features.year.le(2020))]
        eligible=raw[raw.species==sp].merge(obs[['cam','season_start_year','x']],on=['cam','season_start_year'],validate='many_to_one')
        matched=eligible.merge(base[['location_id','year',feature]],left_on=['location_id','season_start_year'],right_on=['location_id','year'],validate='many_to_one')
        assert len(matched)==len(eligible)
        for cam,a in matched.groupby('cam'):
            model_base=a.groupby('season_start_year')[feature].agg(lambda x:x.mean() if x.notna().all() else np.nan)
            observed=obs[obs.cam==cam].x.mean()
            assert len(model_base)==len(obs[obs.cam==cam])
            supported=model_base.notna().all()
            baseline=model_base.mean() if supported else np.nan
            support.append(dict(species=sp,predictor=feature,cam=cam,scenario=scenario,observed_years=len(model_base),supported_model_years=int(model_base.notna().sum()),observed_mean=observed,model_baseline=baseline,model_minus_observed=baseline-observed,source_locations=a.location_id.nunique()))
            # Fixed location weights: average cameras within year, then years.
            weights=a.groupby(['season_start_year','location_id']).size().rename('n').reset_index()
            weights['weight']=weights.n/weights.groupby('season_start_year').n.transform('sum')/len(model_base)
            w=weights.groupby('location_id').weight.sum();assert np.isclose(w.sum(),1)
            for lo,hi in [(2041,2060),(2081,2100)]:
                f=features[(features.experiment_id==scenario)&features.year.between(lo,hi)&features.location_id.isin(w.index)]
                matrix=f.pivot(index='year',columns='location_id',values=feature).reindex(index=range(lo,hi+1),columns=w.index)
                valid=matrix.notna().all(axis=1)
                future=np.nan
                if valid.all():future=float((matrix.to_numpy()@w.to_numpy()).mean())
                delta=future-baseline
                # Do not convert an out-of-range additive count into an actual future count.
                implied=observed+delta
                physical=bool(np.isfinite(implied) and 0<=implied<=(61 if feature=='augsep_low30_days' else 115))
                rec=dict(species=sp,predictor=feature,cam=cam,scenario=scenario,period=f'{lo}-{hi}',observed_mean=observed,model_baseline=baseline,model_future=future,valid_future_years=int(valid.sum()),delta_environment=delta,implied_observed_scale=implied,physical_additive=physical,days_shift=b.coefficient*delta if physical else np.nan,approximate_coefficient=b.coefficient,approximate_by=b.q_by)
                bounds=sorted([b.ci_low*delta,b.ci_high*delta]) if physical else [np.nan,np.nan]
                rec['coefficient_interval_low']=bounds[0];rec['coefficient_interval_high']=bounds[1];forecasts.append(rec)
pd.DataFrame(support).to_csv(OUT/'baseline_support.csv',index=False)
t=pd.DataFrame(forecasts);t.to_csv(OUT/'site_scenarios.csv',index=False)
summaries=[]
for key,a in t.groupby(['species','predictor','scenario','period']):
    full=a.days_shift.notna().all()
    summaries.append(dict(zip(['species','predictor','scenario','period'],key),sites=len(a),supported_sites=int(a.days_shift.notna().sum()),complete_support=bool(full),mean_days_shift=a.days_shift.mean() if full else np.nan,coefficient_interval_low=a.coefficient_interval_low.mean() if full else np.nan,coefficient_interval_high=a.coefficient_interval_high.mean() if full else np.nan))
s=pd.DataFrame(summaries);s.to_csv(OUT/'summary.csv',index=False)
(OUT/'validation.json').write_text(json.dumps(dict(passed=True,annual_location_features=len(features),candidate_site_scenarios=len(t),summary_rows=len(s),inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [rawpath,pointpath,coefpath]+list(SRC.glob('daily_*.npz'))},limits=['One coarse GFDL-CM4 member, not coastal-buffer resolution','Uncorrected model distributions; baseline biases reported','Censored transition dates not imputed; incomplete sites not silently dropped','Approximate coefficient intervals are not full prediction intervals; bootstrap significance was not retained']),indent=2)+'\n')
print(s.to_string(index=False));print(pd.DataFrame(support).groupby('species')[['observed_mean','model_baseline','model_minus_observed']].agg(['min','max']).to_string())
