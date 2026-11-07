from pathlib import Path
import pandas as pd,numpy as np,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
d=pd.read_csv(OUT/'return_drift_daily_2011_2020.csv.gz',parse_dates=['date'])
assert d.date.nunique()==610 and len(d)==610*106
assert not d.duplicated(['location_id','date']).any()
d['year']=d.date.dt.year;d['month']=d.date.dt.month
d['supported']=(d.n_satellite>=3)&d.east_km_day.notna()&d.north_km_day.notna()
rows=[]
for (loc,year,month),g in d.groupby(['location_id','year','month']):
    good=g[g.supported];nominal=g[g.n_nominal>=3]
    rows.append(dict(location_id=loc,year=year,month=month,n_days=len(g),n_supported_days=len(good),coverage_fraction=len(good)/len(g),east_km_day=good.east_km_day.mean(),north_km_day=good.north_km_day.mean(),mean_satellite_cells=g.n_satellite.mean(),mean_wind_cells=g.n_wind.mean(),n_nominal_days=len(nominal),nominal_east_km_day=nominal.nominal_east_km_day.mean(),nominal_north_km_day=nominal.nominal_north_km_day.mean()))
m=pd.DataFrame(rows);m['screen_pass']=m.coverage_fraction>=.8;m.to_csv(OUT/'return_drift_monthly_support.csv',index=False)
p=pd.read_csv(OUT/'behavior_environment_coordinate_join.csv')
for month in [9,10]:
    a=m[m.month==month].drop(columns='month').rename(columns={'year':'season_start_year',**{c:f'drift_m{month}_'+c for c in m.columns if c not in ['location_id','year','month']}})
    p=p.merge(a,on=['location_id','season_start_year'],how='left',validate='many_to_one')
p['drift_both_months_screen']=p.drift_m9_screen_pass.fillna(False).astype(bool)&p.drift_m10_screen_pass.fillna(False).astype(bool)
p.to_csv(OUT/'behavior_environment_drift_join.csv',index=False)
s=[]
for species,g in p.groupby('species'):
    a=g[g.drift_both_months_screen & g.environment_join_complete]
    s.append(dict(species=species,rows_with_concentration=int(g.environment_join_complete.sum()),rows_with_both_drift_months=len(a),geographic_codes=a.cam.nunique(),code_seasons=len(a[['cam','season_start_year']].drop_duplicates())))
pd.DataFrame(s).to_csv(OUT/'behavior_drift_support.csv',index=False)
print(pd.DataFrame(s).to_string(index=False))
