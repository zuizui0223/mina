"""Independent input extraction and brute-force grid matching of 3 ensembles."""
from pathlib import Path
import io,json
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Geod
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'ross_directional_exposure_v1'
manifest=json.loads((root/'pointblue_full_positions_v1/acquisition_manifest.json').read_text())
cache=Path('../pointblue_full_positions');ice=Path('../climate_penguin/return_drift')
b=(cache/manifest['blocks'][0]['file']).read_bytes()
raw=pd.read_csv(io.BytesIO(b'\n'.join(b.splitlines()[:-1])))
saved=pd.read_csv(out/'interval_exposure.csv.gz')
g=saved[(saved.bird_fn==raw.bird_fn.iloc[0])&(saved.season==raw.season.iloc[0])&(saved.product_class=='satellite')]
g=g[g.target==g.target.iloc[0]].sort_values('time1')
targets=pd.read_csv(root/'ice_asymmetry/adelie_macro_support_1980_2024.csv').set_index('site_id')
geod=Geod(ellps='WGS84');checks=[]
def unit(lon,lat):
    lon=np.radians(np.asarray(lon,dtype=float));lat=np.radians(np.asarray(lat,dtype=float))
    return np.column_stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])
for r in g.iloc[[0,len(g)//2,len(g)-1]].itertuples():
    a=raw[(raw.bird_fn==r.bird_fn)&(raw.season==r.season)&(raw.time1==r.time1)&(raw.time2==r.time2)]
    assert len(a)==500
    mid=pd.Timestamp(r.time1)+(pd.Timestamp(r.time2)-pd.Timestamp(r.time1))/2
    day=mid+pd.Timedelta(hours=12)
    with xr.open_dataset(ice/f'ice_drift_sh_ease2-750_cdr-v1p0_24h-{day:%Y%m%d}1200.nc') as d:
        lon=d.lon.values.ravel();lat=d.lat.values.ravel()
        grid=unit(lon,lat);points=unit(a.lon,a.lat)
        ix=np.concatenate([np.argmax(points[k:k+25]@grid.T,axis=1) for k in range(0,500,25)])
        dt=(d.t1.values[0].ravel()[ix]-d.t0.values[0].ravel()[ix])/np.timedelta64(1,'D')
        end_lon=d.lon1.values[0].ravel()[ix];end_lat=d.lat1.values[0].ravel()[ix]
        good=np.isin(d.status_flag.values[0].ravel()[ix],[20,21,22,30])&np.isfinite(end_lon)&np.isfinite(end_lat)&np.isfinite(dt)&(dt>0)
        az,_,dist=geod.inv(lon[ix],lat[ix],end_lon,end_lat)
        target=targets.loc[r.target]
        goal,_,_=geod.inv(lon[ix],lat[ix],np.full(500,target.longitude),np.full(500,target.latitude))
        projected=dist/1000/dt*np.cos(np.radians(az-goal))
        assert good.sum()==r.valid
        assert np.isclose(np.sum(projected[good]),r.projected_sum,atol=1e-8)
        checks.append(dict(time1=r.time1,target=r.target,valid=int(good.sum()),projected_sum=float(np.sum(projected[good]))))
v=dict(passed=True,scope='3 complete ensembles from first block; independent extraction and brute-force nearest cells; shared WGS84 geodesic library',checks=checks)
(out/'independent_validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
