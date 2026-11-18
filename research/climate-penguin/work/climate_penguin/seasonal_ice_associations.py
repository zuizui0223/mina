"""Descriptive seasonal timing and variability, with censoring retained."""
from pathlib import Path
import hashlib,json
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
src=OUT/'daily_concentration_2011_2020_aug_nov.csv.gz'
d=pd.read_csv(src);d=d[d.inner_km.eq(0)].copy()
d['date']=pd.to_datetime(d.date);d['year']=d.date.dt.year
assert not d.duplicated(['location_id','date']).any()
rows=[]
for (loc,year),g in d.groupby(['location_id','year']):
    g=g.sort_values('date')
    assert len(g)==122 and (g.date.diff().dropna().dt.days==1).all()
    assert (g.n_valid/g.n_ocean>=.8).all()
    a=g[g.date.dt.month.le(9)].sic_percent_mean.to_numpy()
    r=dict(location_id=loc,season_start_year=year,
           augsep_sic_mean=float(a.mean()),augsep_sic_sd=float(a.std(ddof=1)),
           augsep_absolute_daily_change=float(np.abs(np.diff(a)).mean()))
    for threshold in [15,30]:
        low=a<threshold
        r[f'augsep_low{threshold}_days']=int(low.sum())
        r[f'augsep_low{threshold}_upcrossings']=int((low[:-1]&~low[1:]).sum())
    rows.append(r)
features=pd.DataFrame(rows)
s=pd.read_csv(OUT/'daily_ice_complete_season_features.csv')
s=s[s.inner_km.eq(0)].rename(columns={'year':'season_start_year'})
eventcols=[x for x in s if x.startswith('low')]
features=features.merge(s[['location_id','season_start_year']+eventcols],validate='one_to_one')
for t in [15,30]:
    # Day from Aug 1 avoids leap-year offsets. No imputation for censored events.
    date=pd.to_datetime(features[f'low{t}_7day_date'])
    start=pd.to_datetime(features.season_start_year.astype(str)+'-08-01')
    features[f'low{t}_transition_day_from_aug1']=(date-start).dt.days
    assert features.loc[features[f'low{t}_7day_status'].ne('observed_transition'),f'low{t}_transition_day_from_aug1'].isna().all()
features.to_csv(OUT/'seasonal_ice_variability_features.csv',index=False)
p=pd.read_csv(OUT/'extended_analysis_cohort.csv')
joined=p.merge(features,on=['location_id','season_start_year'],how='left',validate='many_to_one')
assert len(joined)==len(p)
joined.to_csv(OUT/'behavior_seasonal_ice_join.csv',index=False)
joined[joined.appendix_range_consistent.eq(True)].to_csv(OUT/'behavior_seasonal_ice_appendix_join.csv',index=False)
code_support=[]
for t in [15,30]:
    col=f'low{t}_7day_status'
    a=joined.dropna(subset=[col]).groupby(['species','cam','season_start_year'])[col].agg(lambda x:'|'.join(sorted(set(x))))
    z=a.reset_index().groupby(['species',col]).size().reset_index(name='code_seasons')
    z=z.rename(columns={col:'status_set'});z['threshold']=t;code_support.append(z)
pd.concat(code_support).to_csv(OUT/'seasonal_ice_transition_code_support.csv',index=False)
support=[]
for t in [15,30]:
    a=joined.dropna(subset=[f'low{t}_7day_status']).drop_duplicates(['species','cam','season_start_year','location_id'])
    a=a.groupby(['species',f'low{t}_7day_status']).agg(coordinate_code_seasons=('cam','size'),geographic_codes=('cam','nunique')).reset_index()
    a=a.rename(columns={f'low{t}_7day_status':'status'});a['threshold']=t;support.append(a)
pd.concat(support).to_csv(OUT/'seasonal_ice_transition_support.csv',index=False)
(OUT/'seasonal_ice_checks.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),environment_windows=len(features),joined_camera_rows=len(joined),imputed_event_dates=0,source_calendar_reconciled=False,chronological_precedence_verified=False),indent=2),encoding='utf-8')
print(pd.concat(support).to_string(index=False))
