"""Check monthly-derived endpoints against direct averages of daily source rows."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]/'outputs'
OUT=ROOT/'low_days_mean_separation_v1'
files=[ROOT/'climate_penguin'/f'daily_concentration_{a}_{b}_aug_nov.csv.gz'
       for a,b in [(1991,2010),(2011,2020)]]
locations=ROOT/'climate_penguin/daily_ice_locations.csv'
loc=pd.read_csv(locations);loc=loc[loc.cohort=='macro_40']
raw=pd.concat([pd.read_csv(p) for p in files],ignore_index=True)
raw=raw.merge(loc[['location_id','site_id']],on='location_id',validate='many_to_one')
raw['date']=pd.to_datetime(raw.date);raw['year']=raw.date.dt.year
assert not raw.duplicated(['site_id','date','inner_km']).any()
paired=pd.read_csv(OUT/'paired_features.csv')
checks=0
for window,stop in [('aug_sep',9),('aug_nov',11)]:
    a=raw[raw.date.dt.month<=stop]
    groups=a.groupby(['site_id','year','inner_km']).sic_percent_mean
    assert groups.count().eq(61 if stop==9 else 122).all()
    direct=groups.mean()
    for r in paired[paired.window==window].itertuples():
        for endpoint in ['start','end']:
            np.testing.assert_allclose(getattr(r,endpoint+'_sic'),
                direct.loc[(r.site_id,getattr(r,endpoint),r.inner_km)],atol=1e-10)
            checks+=1
assert checks==4816
receipt=dict(passed=True,direct_daily_endpoint_checks=checks,
    inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files+[locations,OUT/'paired_features.csv']})
(OUT/'daily_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'passed':True,'direct_daily_endpoint_checks':checks}))
