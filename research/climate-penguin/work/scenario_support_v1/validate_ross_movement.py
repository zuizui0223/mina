"""Independently self-join raw within-run rows for three retained pairs."""
from pathlib import Path
import io,json
import numpy as np
import pandas as pd
from pyproj import Geod
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'ross_movement_pairs_v1'
manifest=json.loads((root/'pointblue_full_positions_v1/acquisition_manifest.json').read_text())
b=(Path('../pointblue_full_positions')/manifest['blocks'][0]['file']).read_bytes()
raw=pd.read_csv(io.BytesIO(b'\n'.join(b.splitlines()[:-1])))
s=pd.read_csv(out/'interval_movement.csv.gz')
s=s[(s.bird_fn==raw.bird_fn.iloc[0])&(s.season==raw.season.iloc[0])]
s=s[s.target==s.target.iloc[0]].sort_values('time1')
targets=pd.read_csv(root/'ice_asymmetry/adelie_macro_support_1980_2024.csv').set_index('site_id')
geod=Geod(ellps='WGS84');checks=[]
for r in s.iloc[[0,len(s)//2,len(s)-1]].itertuples():
    first=raw[(raw.bird_fn==r.bird_fn)&(raw.season==r.season)&(raw.time1==r.time1)&(raw.time2==r.time2)]
    second=raw[(raw.bird_fn==r.bird_fn)&(raw.season==r.season)&(raw.time1==r.next_time1)&(raw.time2==r.next_time2)]
    pairs=first.merge(second,on=['bird_fn','season','run'],suffixes=('_a','_b'),validate='one_to_one')
    assert len(pairs)==r.draws==500 and pairs.time2_a.eq(pairs.time1_b).all()
    t=targets.loc[r.target];dist=[]
    for q in pairs.itertuples():
        _,_,before=geod.inv(q.lon_a,q.lat_a,t.longitude,t.latitude)
        _,_,after=geod.inv(q.lon_b,q.lat_b,t.longitude,t.latitude)
        dt=(pd.Timestamp(q.time2_b)-pd.Timestamp(q.time1_a)).total_seconds()/2/86400
        assert np.isclose(dt,r.duration_days)
        dist.append((before-after)/1000/dt)
    assert np.isclose(np.mean(dist),r.mean_radial_km_day,atol=1e-9)
    assert np.isclose(np.std(dist),r.sd_radial_km_day,atol=1e-9)
    checks.append(dict(time1=r.time1,draws=len(pairs),mean=float(np.mean(dist))))
result=dict(passed=True,scope='3 full raw pair ensembles self-joined by run, scalar geodesics; shared WGS84 library',checks=checks)
(out/'independent_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
