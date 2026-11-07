"""Year-label diagnostic using source environmental covariates, never outcomes."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
raw=pd.read_csv(OUT/'extended_analysis_cohort.csv')
cols=['mn_veinteoct','mdn_veinteoct','mn_cincooct','mdn_cincooct']
# Same coordinate-year can occur for multiple species/cameras. Check before reducing.
conflicts=raw.groupby(['location_id','season_start_year'])[cols].nunique().max()
assert conflicts.max()<=1,conflicts.to_dict()
base=raw.groupby(['location_id','cam','season_start_year'])[cols].first().reset_index()
d=pd.read_csv(OUT/'daily_concentration_2011_2020_aug_nov.csv.gz')
d['date']=pd.to_datetime(d.date)
d=d[d.inner_km.eq(0)&d.date.dt.month.eq(10)].copy();d['environment_year']=d.date.dt.year
env=d.groupby(['location_id','environment_year']).agg(osi_oct_mean=('sic_percent_mean','mean'),osi_oct_median=('sic_percent_mean','median'),n_days=('date','size')).reset_index()
assert env.n_days.eq(31).all()
merged=base.copy()
for shift in [-1,0,1]:
    e=env.copy();e['season_start_year']=e.environment_year-shift
    e=e.rename(columns={v:f'{v}_shift{shift}' for v in ['osi_oct_mean','osi_oct_median']})
    merged=merged.merge(e.drop(columns=['environment_year','n_days']),on=['location_id','season_start_year'],how='left',validate='many_to_one')
rows=[];points=[]
for source in cols:
    stat='mean' if source.startswith('mn_') else 'median'
    target=[f'osi_oct_{stat}_shift{i}' for i in [-1,0,1]]
    a=merged.dropna(subset=[source]+target).copy()
    for shift,targetcol in zip([-1,0,1],target):
        # Equal weight per geographic code-season, not per camera/species.
        g=a.groupby(['cam','season_start_year']).agg(x=(source,'mean'),y=(targetcol,'mean'),coordinates=('location_id','nunique')).reset_index()
        repeated=g[g.cam.isin(g.groupby('cam').size().loc[lambda s:s>=2].index)]
        r=repeated[['x','y']]-repeated.groupby('cam')[['x','y']].transform('mean')
        rows.append(dict(source_variable=source,comparison_statistic=stat,environment_year_shift=shift,code_seasons=len(g),geographic_codes=g.cam.nunique(),repeated_code_seasons=len(repeated),pooled_r=g.x.corr(g.y),within_code_r=r.x.corr(r.y)))
        g['source_variable']=source;g['environment_year_shift']=shift;points.append(g)
result=pd.DataFrame(rows);result.to_csv(OUT/'environment_year_alignment_diagnostic.csv',index=False)
pd.concat(points).to_csv(OUT/'environment_year_alignment_points.csv',index=False)
checks=dict(environment_days_per_october=31,source_within_coordinate_year_conflict_max=int(conflicts.max()),automatic_year_correction=False,calendar_reconciled=False,
 source_sha256={f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in ['extended_analysis_cohort.csv','daily_concentration_2011_2020_aug_nov.csv.gz']})
(OUT/'environment_year_alignment_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(result.to_string(index=False))
