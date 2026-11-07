"""Contiguous within-path positions; midpoint-based radial movement proxy."""
from pathlib import Path
import argparse,io,json,hashlib,time
import pandas as pd
import numpy as np
from pyproj import Geod
from pointblue_stream import Blocks
p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'ross_movement_pairs_v1';out.mkdir(exist_ok=True)
source=root/'ross_ensemble_ice_v1/interval_support.csv.gz'
s=pd.read_csv(source);keys=['bird_fn','season','time1','time2']
meta=pd.read_csv(root/'pointblue_full_positions_v1/trip_support.csv')
s=s.merge(meta[['bird_fn','season','br_col']],on=['bird_fn','season'],validate='many_to_one')
target=pd.read_csv(root/'ice_asymmetry/adelie_macro_support_1980_2024.csv').set_index('site_id')
membership=set(map(tuple,s[keys].itertuples(index=False,name=None)))
m=json.loads((root/'pointblue_full_positions_v1/acquisition_manifest.json').read_text())
for b in m['blocks']:
    f=a.cache/b['file'];assert f.stat().st_size==b['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==b['sha256']
geod=Geod(ellps='WGS84');carry=None;pieces=[];read=0;start=time.monotonic()
def process(d):
    nxt=d.shift(-1).add_prefix('next_');q=pd.concat([d,nxt],axis=1).iloc[:-1]
    q=q[(q.bird_fn==q.next_bird_fn)&(q.season==q.next_season)&(q.run==q.next_run)&(q.time2==q.next_time1)]
    q=q.merge(s[keys+['br_col']],on=keys,validate='many_to_one')
    keep=[(r.bird_fn,r.season,r.next_time1,r.next_time2) in membership for r in q.itertuples()]
    q=q.loc[keep]
    q=q[(~q.inserted)&(q.next_inserted==False)&np.isfinite(q.lon)&np.isfinite(q.lat)&np.isfinite(q.next_lon)&np.isfinite(q.next_lat)]
    q=q[q.lon.between(-180,360)&q.next_lon.between(-180,360)&q.lat.between(-90,90)&q.next_lat.between(-90,90)]
    if not len(q):return
    t1=pd.to_datetime(q.time1,utc=True);t2=pd.to_datetime(q.time2,utc=True);n2=pd.to_datetime(q.next_time2,utc=True)
    dt=((t2+(n2-t2)/2)-(t1+(t2-t1)/2)).dt.total_seconds()/86400
    assert (dt>0).all();q['duration_days']=dt
    for colony,g in q.groupby('br_col'):
        for tid in (['CRZE','CRZW'] if colony=='CROZ' else ['ROYD']):
            t=target.loc[tid];lo=np.full(len(g),t.longitude);la=np.full(len(g),t.latitude)
            _,_,before=geod.inv(g.lon,g.lat,lo,la);_,_,after=geod.inv(g.next_lon,g.next_lat,lo,la)
            _,_,distance=geod.inv(g.lon,g.lat,g.next_lon,g.next_lat)
            speed=(before-after)/1000/g.duration_days.to_numpy()
            assert (abs(before-after)<=distance+1e-6).all()
            z=g[keys+['next_time1','next_time2','duration_days']].copy();z['target']=tid
            z['draws']=1;z['radial_sum']=speed;z['radial_square_sum']=speed**2;z['positive']=speed>0
            z['land_flagged']=(g.filterLand|g.next_filterLand).astype(int)
            pieces.append(z.groupby(keys+['next_time1','next_time2','duration_days','target']).agg(draws=('draws','sum'),radial_sum=('radial_sum','sum'),radial_square_sum=('radial_square_sum','sum'),positive=('positive','sum'),land_flagged=('land_flagged','sum')).reset_index())
with io.BufferedReader(Blocks([a.cache/b['file'] for b in m['blocks']])) as stream:
    for i,d in enumerate(pd.read_csv(stream,chunksize=250000)):
        read+=len(d)
        if carry is not None:d=pd.concat([carry,d],ignore_index=True)
        process(d);carry=d.iloc[[-1]].copy()
        if i%20==0:print(json.dumps(dict(chunks=i+1,source_rows=read,seconds=round(time.monotonic()-start))),flush=True)
cols=keys+['next_time1','next_time2','duration_days','target']
t=pd.concat(pieces).groupby(cols).sum().reset_index()
assert t.draws.eq(500).all() and not t.duplicated(keys+['target']).any()
t['mean_radial_km_day']=t.radial_sum/t.draws
t['sd_radial_km_day']=np.sqrt(np.maximum(0,t.radial_square_sum/t.draws-t.mean_radial_km_day**2))
t['positive_fraction']=t.positive/t.draws
t.to_csv(out/'interval_movement.csv.gz',index=False)
v=dict(status='model_location_radial_displacement_not_observed_swimming_speed',source_rows=read,pair_target_rows=len(t),
       unique_pairs=len(t[keys].drop_duplicates()),birds=t.bird_fn.nunique(),bird_years=len(t[['bird_fn','season']].drop_duplicates()),
       support_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
       limits=['Both intervals previously retained and contiguous within same run; no gap bridging',
               'Interval midpoint interpretation, not independently validated position timestamps',
               'GLS position errors and movement priors can dominate apparent speed',
               '500 paths are not independent biological replicates'])
(out/'validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
