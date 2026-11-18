"""Check 3 full ensembles with brute-force spherical nearest cells."""
from pathlib import Path
import argparse,io,json
import numpy as np
import pandas as pd
import xarray as xr

p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--ice-root',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'ross_ensemble_ice_v1'
m=json.loads((root/'pointblue_full_positions_v1/acquisition_manifest.json').read_text())
b=(a.cache/m['blocks'][0]['file']).read_bytes();lines=b.splitlines()[:-1]
raw=pd.read_csv(io.BytesIO(b'\n'.join(lines)))
bird=raw.iloc[0].bird_fn;season=raw.iloc[0].season
saved=pd.read_csv(out/'interval_support.csv.gz');g=saved[(saved.bird_fn==bird)&(saved.season==season)].sort_values('time1')
assert len(g)>=3
def unit(lon,lat):
    lon=np.asarray(lon,dtype=np.float64);lat=np.asarray(lat,dtype=np.float64)
    longitude=np.deg2rad(lon);latitude=np.deg2rad(lat)
    return np.column_stack([np.cos(latitude)*np.cos(longitude),np.cos(latitude)*np.sin(longitude),np.sin(latitude)])
checks=[]
for r in g.iloc[[0,len(g)//2,len(g)-1]].itertuples():
    sample=raw[(raw.bird_fn==bird)&(raw.season==season)&(raw.time1==r.time1)&(raw.time2==r.time2)]
    assert len(sample)==r.draws==500 and sample.run.nunique()==500
    stats={}
    for product,folder,name in [('sic','osi_concentration',f'ice_conc_sh_ease2-250_cdr-v3p1_{pd.Timestamp(r.sic_day):%Y%m%d}1200.nc'),
                                ('drift','return_drift',f'ice_drift_sh_ease2-750_cdr-v1p0_24h-{pd.Timestamp(r.drift_day):%Y%m%d}1200.nc')]:
        path=a.ice_root/folder/name;assert path.exists()
        with xr.open_dataset(path) as d:
            lon=d.lon.values.ravel();lat=d.lat.values.ravel();valid=np.isfinite(lon)&np.isfinite(lat);ids=np.flatnonzero(valid)
            grid=unit(lon[valid],lat[valid]);points=unit(sample.lon.to_numpy(),sample.lat.to_numpy())
            indices=[]
            for start in range(0,len(points),25):indices.extend(ids[np.argmax(points[start:start+25]@grid.T,axis=1)])
            k=np.array(indices);flag=d.status_flag.values[0].ravel()[k]
            midpoint=pd.Timestamp(r.time1)+(pd.Timestamp(r.time2)-pd.Timestamp(r.time1))/2
            bounds=pd.to_datetime(d.time_bnds.values[0],utc=True)
            assert bounds[0]<=midpoint<bounds[1]
            if product=='sic':
                value=d.ice_conc.values[0].ravel()[k]
                good=np.isfinite(flag)&np.isfinite(value)&((np.nan_to_num(flag).astype(int)&3)==0)
                assert int(good.sum())==r.sic_valid and int((good&(value<15)).sum())==r.sic_under15
                assert np.isclose(np.where(good,value,0).sum(),r.sic_sum,rtol=1e-10,atol=1e-10)
                stats['sic_valid']=int(good.sum())
            else:
                good=np.isin(flag,[20,21,22,30])&np.isfinite(d.dX.values[0].ravel()[k])&np.isfinite(d.dY.values[0].ravel()[k])
                assert int(good.sum())==r.drift_valid and int((good&(flag==30)).sum())==r.drift_nominal
                assert int((flag==2).sum())==r.drift_noice
                stats['drift_valid']=int(good.sum())
    checks.append(dict(bird_fn=bird,season=season,time1=r.time1,draws=len(sample),**stats))
pd.DataFrame(checks).to_csv(out/'independent_interval_checks.csv',index=False)
trip=pd.read_csv(out/'trip_support.csv');full=pd.read_csv(root/'pointblue_full_positions_v1/trip_support.csv')
assert saved.draws.sum()==trip.draws.sum()==full.late_selected_rows.sum()
assert len(trip)==full.late_selected_rows.gt(0).sum()
result=dict(passed=True,brute_force_intervals=len(checks),draws_per_interval=500,products_per_draw=2,
            aggregate_draw_count=int(saved.draws.sum()),
            scope='3 complete ensembles from first raw block; full row conservation. Not all-cell validation or transport inference')
(out/'independent_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
