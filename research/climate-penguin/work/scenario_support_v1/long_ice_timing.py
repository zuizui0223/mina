"""Extend the existing 15/30%, seven-day definition without imputing censoring."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'outputs/climate_penguin'
OUT=ROOT/'outputs/long_ice_timing_v1'; OUT.mkdir(exist_ok=True)
paths=[SRC/f'daily_concentration_{a}_{b}_aug_nov.csv.gz' for a,b in [(1991,2010),(2011,2020)]]
locations=pd.read_csv(SRC/'daily_ice_locations.csv'); locations=locations[locations.cohort.eq('macro_40')]
d=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
d=d[d.location_id.isin(locations.location_id)].copy()
d['date']=pd.to_datetime(d.date);d['year']=d.date.dt.year
assert not d.duplicated(['location_id','date','inner_km']).any()
rows=[]
for (loc,year,band),g in d.groupby(['location_id','year','inner_km']):
    g=g.sort_values('date');assert len(g)==122 and g.date.diff().dropna().dt.days.eq(1).all()
    assert (g.n_valid/g.n_ocean>=.8).all()
    for stop,label in [(9,'aug_sep'),(11,'aug_nov')]:
        sub=g[g.date.dt.month<=stop]; values=sub.sic_percent_mean.to_numpy()
        assert np.isfinite(values).all()
        for threshold in [15,30]:
            low=values<threshold
            starts=[i for i in range(len(low)-6) if low[i:i+7].all()]
            rolling=np.flatnonzero(np.convolve(low.astype(int),np.ones(7,dtype=int),'valid')==7)
            assert starts==rolling.tolist()
            state='no_transition_by_window_end' if not starts else ('already_low_at_window_start' if starts[0]==0 else 'observed_transition')
            onset=starts[0] if state=='observed_transition' else np.nan
            reversal=bool((~low[starts[0]+7:]).any()) if starts else None
            runs=[]; run=0
            for flag in low:
                run=run+1 if flag else 0; runs.append(run)
            rows.append(dict(location_id=loc,year=year,inner_km=band,window=label,threshold=threshold,
                 window_days=len(low),low_days=int(low.sum()),longest_low_run=max(runs),
                 return_to_high_count=int((low[:-1]&~low[1:]).sum()),status=state,
                 transition_day_from_aug1=onset,later_reversal=reversal))
features=pd.DataFrame(rows).merge(locations[['location_id','site_id']],on='location_id',validate='many_to_one')
assert len(features)==9600
features.to_csv(OUT/'seasonal_features.csv',index=False)
# Reproduce all legacy full-window statuses/dates for the 40 macro sites.
old=pd.read_csv(SRC/'daily_ice_complete_season_features.csv')
checked=0
for threshold in [15,30]:
    a=features[(features.window=='aug_nov')&(features.threshold==threshold)&(features.year>=2011)].merge(old,on=['location_id','year','inner_km'],validate='one_to_one')
    assert (a.status==a[f'low{threshold}_7day_status']).all()
    delta=(pd.to_datetime(a[f'low{threshold}_7day_date'])-pd.to_datetime(a.year.astype(str)+'-08-01')).dt.days
    assert np.allclose(a.transition_day_from_aug1,delta,equal_nan=True)
    checked+=len(a)
intervals=pd.read_csv(SRC/'historical_count_interval_timing.csv')
pieces=[]
for (window,threshold,band),f in features.groupby(['window','threshold','inner_km']):
    a=intervals.copy()
    for phase in ['start','end']:
        cols=['status','transition_day_from_aug1','low_days','longest_low_run','return_to_high_count']
        b=f[['site_id','year']+cols].rename(columns={'year':phase,**{c:phase+'_'+c for c in cols}})
        a=a.merge(b,on=['site_id',phase],validate='many_to_one',how='left')
    a['window']=window;a['threshold']=threshold;a['inner_km']=band
    a['timing_supported']=a.both_all_after_september if window=='aug_sep' else a.both_all_after_november
    a['both_observed_transitions']=a.start_status.eq('observed_transition')&a.end_status.eq('observed_transition')
    a['onset_change']=a.end_transition_day_from_aug1-a.start_transition_day_from_aug1
    a['low_days_change']=a.end_low_days-a.start_low_days
    assert a.onset_change.notna().eq(a.both_observed_transitions).all()
    pieces.append(a)
joined=pd.concat(pieces,ignore_index=True)
joined.to_csv(OUT/'count_interval_features.csv',index=False)
support=[]
for scope,a in [('all',joined),('timing_supported',joined[joined.timing_supported])]:
    for key,g in a.groupby(['window','threshold','inner_km']):
        observed=g[g.both_observed_transitions]
        support.append(dict(scope=scope,window=key[0],threshold=key[1],inner_km=key[2],intervals=len(g),
             onset_change_intervals=len(observed),onset_change_sites=observed.site_id.nunique(),
             onset_change_regions=observed.region.nunique(),onset_change_nonvictoria=int(observed.region.ne('Victoria Land').sum())))
        support[-1].update(low_days_nonzero_change_intervals=int(g.low_days_change.ne(0).sum()),
                           low_days_nonzero_change_sites=g.loc[g.low_days_change.ne(0),'site_id'].nunique())
pd.DataFrame(support).to_csv(OUT/'transition_support.csv',index=False)
features.groupby(['window','threshold','inner_km','status']).size().rename('site_years').reset_index().to_csv(OUT/'status_summary.csv',index=False)
receipt={'passed':True,'features':len(features),'legacy_status_and_date_checks':checked,'independent_run_checks':len(features),
 'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
 'definitions':'First seven consecutive days strictly below 15 or 30 percent. Same existing definitions, both retained.',
 'limitations':['Not physical melt or final retreat','No event date imputed to already-low or no-observed-event windows',
 'Last six days cannot start a confirmed seven-day episode within the window',
 'Low-day count is fully observed even when first-transition date is censored',
 'Outcome regressions not run in this support audit']}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(pd.DataFrame(support).to_string(index=False)); print('Legacy checks',checked)
