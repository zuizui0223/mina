"""Complete-month macro-site SIC summaries, retaining observed-day quality."""
from pathlib import Path
import argparse,json
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=1991);ap.add_argument('--end',type=int,default=2020);args=ap.parse_args()
assert 1991<=args.start<=args.end<=2020
manifests=[]
for lo,hi,name in [(1991,2010,'daily_concentration_1991_2010_manifest.json'),(2011,2020,'daily_concentration_manifest.json')]:
    if args.start<=hi and args.end>=lo:
        entries=json.loads((OUT/name).read_text());assert len(entries)==122*(hi-lo+1),'Acquisition incomplete: '+name
        manifests.extend(entries)
wanted={str(d.date()) for y in range(args.start,args.end+1) for d in pd.date_range(f'{y}-08-01',f'{y}-11-30')}
entries=[e for e in manifests if e['date'] in wanted]
assert len(entries)==len(wanted) and {e['date'] for e in entries}==wanted
assert all(e['ok'] for e in entries),'Failed acquisition dates must be resolved or explicitly modeled'
loc=pd.read_csv(OUT/'daily_ice_locations.csv');loc=loc[loc.cohort.eq('macro_40')]
frames=[]
for e in entries:
    p=ROOT/'work/climate_penguin/osi_concentration/extracted'/(e['date']+'.csv')
    a=pd.read_csv(p);frames.append(a[a.location_id.isin(loc.location_id)])
d=pd.concat(frames,ignore_index=True);assert not d.duplicated(['location_id','date','inner_km']).any()
d['date']=pd.to_datetime(d.date);d['year']=d.date.dt.year;d['month']=d.date.dt.month
d['supported']=(d.n_valid/d.n_ocean.replace(0,np.nan)>=.8)&d.sic_percent_mean.notna()
r=d.groupby(['location_id','year','month','inner_km']).agg(days=('date','size'),supported_days=('supported','sum'),sic_mean=('sic_percent_mean','mean'),sic_sd=('sic_percent_mean','std')).reset_index()
r['expected_days']=pd.to_datetime(dict(year=r.year,month=r.month,day=1)).dt.days_in_month
r['complete_month']=r.days.eq(r.expected_days)&r.supported_days.eq(r.expected_days)
r.loc[~r.complete_month,['sic_mean','sic_sd']]=np.nan
r=r.merge(loc[['location_id','site_id']],on='location_id',validate='many_to_one')
assert len(r)==40*(args.end-args.start+1)*4*2
r.to_csv(OUT/f'macro_monthly_seaice_{args.start}_{args.end}.csv',index=False)
old=pd.read_csv(OUT/'daily_ice_complete_season_features.csv');checked=0
for month in [8,9,10,11]:
    a=r[r.month.eq(month)].merge(old[['location_id','year','inner_km',f'sic_mean_month{month}']],on=['location_id','year','inner_km'],validate='one_to_one')
    assert np.allclose(a.sic_mean,a[f'sic_mean_month{month}'],equal_nan=True,atol=1e-10);checked+=len(a)
checks=dict(start=args.start,end=args.end,days=len(wanted),macro_sites=40,monthly_windows=len(r),complete_months=int(r.complete_month.sum()),existing_monthly_values_verified=checked)
(OUT/f'macro_monthly_seaice_{args.start}_{args.end}_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(checks)
