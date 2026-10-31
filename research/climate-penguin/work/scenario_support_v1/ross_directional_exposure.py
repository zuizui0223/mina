"""Colony-directed ice displacement, never inferred bird transport."""
from pathlib import Path
from functools import lru_cache
import argparse,io,json,hashlib,time
import pandas as pd
import numpy as np
import xarray as xr
from scipy.spatial import cKDTree
from pyproj import Geod,Transformer
from pointblue_stream import Blocks

p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--ice-root',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'ross_directional_exposure_v1';out.mkdir(exist_ok=True)
source=root/'ross_ensemble_ice_v1/interval_support.csv.gz'
support=pd.read_csv(source);meta=pd.read_csv(root/'pointblue_full_positions_v1/trip_support.csv')
support=support.merge(meta[['bird_fn','season','br_col']],validate='many_to_one',on=['bird_fn','season'])
keys=['bird_fn','season','time1','time2']
assert not support.duplicated(keys).any()
targets=pd.read_csv(root/'ice_asymmetry/adelie_macro_support_1980_2024.csv').set_index('site_id')
geod=Geod(ellps='WGS84');project=Transformer.from_crs(4326,6932,always_xy=True)
def xyz(lon,lat):
    x=np.deg2rad(np.asarray(lon,dtype=float));y=np.deg2rad(np.asarray(lat,dtype=float))
    return np.column_stack([np.cos(y)*np.cos(x),np.cos(y)*np.sin(x),np.sin(y)])
with xr.open_dataset(a.ice_root/'return_drift/ice_drift_sh_ease2-750_cdr-v1p0_24h-201709281200.nc') as ds:
    lon=ds.lon.values.ravel().astype(float);lat=ds.lat.values.ravel().astype(float)
tree=cKDTree(xyz(lon,lat));hashes={};errors=[]
@lru_cache(maxsize=130)
def layer(day,target):
    path=a.ice_root/'return_drift'/f'ice_drift_sh_ease2-750_cdr-v1p0_24h-{pd.Timestamp(day):%Y%m%d}1200.nc'
    hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    with xr.open_dataset(path) as ds:
        assert np.allclose(lon,ds.lon.values.ravel()) and np.allclose(lat,ds.lat.values.ravel())
        end_lon=ds.lon1.values[0].ravel();end_lat=ds.lat1.values[0].ravel()
        flag=ds.status_flag.values[0].ravel();dx=ds.dX.values[0].ravel();dy=ds.dY.values[0].ravel()
        valid=np.isfinite(end_lon)&np.isfinite(end_lat)&np.isfinite(dx)&np.isfinite(dy)
        dt=(ds.t1.values[0].ravel()-ds.t0.values[0].ravel())/np.timedelta64(1,'D')
        valid &= np.isfinite(dt)&(dt>0)
        x,y=project.transform(lon[valid],lat[valid]);x1,y1=project.transform(end_lon[valid],end_lat[valid])
        err=max(np.max(abs((x1-x)/1000-dx[valid])),np.max(abs((y1-y)/1000-dy[valid])))
        assert err<.005;errors.append(float(err))
        az,_,distance=geod.inv(lon,lat,end_lon,end_lat)
        t=targets.loc[target];toward,_,before=geod.inv(lon,lat,np.full(len(lon),t.longitude),np.full(len(lon),t.latitude))
        _,_,after=geod.inv(end_lon,end_lat,np.full(len(lon),t.longitude),np.full(len(lon),t.latitude))
        # Projection uses initial geodesic direction; radial distance change is a separate check.
        speed=np.where(valid,distance/1000/dt,np.nan)
        projected=speed*np.cos(np.deg2rad(az-toward))
        radial=np.where(valid,(before-after)/1000/dt,np.nan)
        assert np.all(abs(projected[valid])<=speed[valid]+1e-9)
        return flag,valid,projected,radial

manifest=json.loads((root/'pointblue_full_positions_v1/acquisition_manifest.json').read_text())
for b in manifest['blocks']:
    path=a.cache/b['file'];assert path.stat().st_size==b['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==b['sha256']
pieces=[];read=0;selected=0;start=time.monotonic()
with io.BufferedReader(Blocks([a.cache/b['file'] for b in manifest['blocks']])) as stream:
    for i,d in enumerate(pd.read_csv(stream,chunksize=250000)):
        read+=len(d)
        # Exact previously retained interval keys; inserted and geography are independently screened.
        d=d.merge(support[keys+['drift_day','br_col']],on=keys,how='inner',validate='many_to_one')
        d=d[(~d.inserted)&np.isfinite(d.lon)&np.isfinite(d.lat)&d.lon.between(-180,360)&d.lat.between(-90,90)]
        selected+=len(d)
        if len(d):
            d['cell']=tree.query(xyz(d.lon,d.lat))[1]
            for colony,g in d.groupby('br_col'):
                for target in (['CRZE','CRZW'] if colony=='CROZ' else ['ROYD']):
                    for day,q in g.groupby('drift_day'):
                        flag,valid,proj,radial=layer(day,target);ix=q.cell.to_numpy()
                        for label,accepted in [('satellite',np.isin(flag,[20,21,22,30])),('nominal',flag==30),('wind',np.isin(flag,[23,24,25]))]:
                            good=accepted[ix]&valid[ix]
                            z=q[keys].copy();z['target']=target;z['product_class']=label
                            z['draws']=1;z['valid']=good.astype(int)
                            z['toward']=((proj[ix]>0)&good).astype(int)
                            z['projected_sum']=np.where(good,proj[ix],0.)
                            z['radial_sum']=np.where(good,radial[ix],0.)
                            pieces.append(z.groupby(keys+['target','product_class']).sum().reset_index())
        if i%20==0:print(json.dumps(dict(chunks=i+1,rows=read,selected=selected,seconds=round(time.monotonic()-start))),flush=True)
t=pd.concat(pieces).groupby(keys+['target','product_class']).sum().reset_index()
assert selected==support.draws.sum() and t.draws.eq(500).all()
for col in ['projected_sum','radial_sum']:t[col.replace('_sum','_km_day')]=t[col]/t.valid.replace(0,np.nan)
t['support_fraction']=t.valid/t.draws;t['toward_fraction_given_valid']=t.toward/t.valid.replace(0,np.nan)
t.to_csv(out/'interval_exposure.csv.gz',index=False)
receipt=dict(status='environmental_direction_not_bird_assistance',source_rows=read,selected_draws=selected,
    rows=len(t),maximum_endpoint_reconstruction_error_km=max(errors),ice_hashes=hashes,
    support_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    limits=['Grid direction to mapped colony; Crozier east/west both retained, not exact tag endpoint',
            'Mean among supported model location draws; not independent birds or transport probability',
            'Wind-derived rows are separate model-dependent exposures',
            'No bird velocity, causal assistance, arrival or breeding response estimated'])
(out/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='ice_hashes'}))
