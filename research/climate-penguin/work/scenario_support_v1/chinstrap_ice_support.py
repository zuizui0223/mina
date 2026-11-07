"""Nearest-cell ice coverage at actual tracking points, with +/-1 day sensitivity."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/chinstrap_winter_v1'
parser=argparse.ArgumentParser();parser.add_argument('--raw-root',type=Path,required=True);args=parser.parse_args()
points=pd.read_csv(OUT/'route_daily_points.csv',dtype={'PTT':str});points['day']=pd.to_datetime(points.day)
geo=Geod(ellps='WGS84');rows=[];files={}
for point in points.to_dict('records'):
    for offset in [-1,0,1]:
        day=point['day']+pd.Timedelta(days=offset)
        row=dict(PTT=point['PTT'],point_day=str(point['day'].date()),ice_day=str(day.date()),day_offset=offset)
        for product,folder,name in [('sic','osi_concentration',f'ice_conc_sh_ease2-250_cdr-v3p1_{day:%Y%m%d}1200.nc'),
                                   ('drift','return_drift',f'ice_drift_sh_ease2-750_cdr-v1p0_24h-{day:%Y%m%d}1200.nc')]:
            path=args.raw_root/folder/name
            # One boundary date can be outside the archived Sep-Oct drift window.
            if not path.exists():
                row[product+'_status']='file_not_cached';continue
            if str(path) not in files:files[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
            with xr.open_dataset(path) as ds:
                assert pd.Timestamp(ds.time.values[0]).date()==day.date()
                lat=ds.lat.values.ravel();lon=ds.lon.values.ravel()
                _,_,dist=geo.inv(np.full(len(lat),point['LONGITUDE']),np.full(len(lat),point['LATITUDE']),lon,lat)
                k=int(np.nanargmin(dist));flag=float(ds.status_flag.values[0].ravel()[k])
                row[product+'_cell_distance_km']=float(dist[k]/1000)
                row[product+'_flag']=flag;row[product+'_grid_lat']=float(lat[k]);row[product+'_grid_lon']=float(lon[k])
                if product=='sic':
                    value=float(ds.ice_conc.values[0].ravel()[k]);ocean=np.isfinite(flag) and (int(flag)&3)==0
                    row['sic_percent']=value if ocean and np.isfinite(value) else np.nan
                    row['sic_status']='ocean_value' if ocean and np.isfinite(value) else 'invalid_or_land'
                else:
                    valid=all(np.isfinite(ds[v].values[0].ravel()[k]) for v in ['dX','dY'])
                    row['drift_status']='satellite_vector' if valid and flag in [20,21,22,30] else ('no_ice' if flag==2 else 'other_unavailable')
        rows.append(row)
result=pd.DataFrame(rows);assert len(result)==114
assert not result.duplicated(['PTT','point_day','day_offset']).any()
result.to_csv(OUT/'route_ice_support.csv',index=False)
summary=result.groupby(['PTT','day_offset'],as_index=False).agg(points=('point_day','size'),valid_sic=('sic_percent','count'),
    mean_sic=('sic_percent','mean'),max_sic=('sic_percent','max'),satellite_vectors=('drift_status',lambda x:int(x.eq('satellite_vector').sum())),
    no_ice_flags=('drift_status',lambda x:int(x.eq('no_ice').sum())),uncached_drift=('drift_status',lambda x:int(x.eq('file_not_cached').sum())))
summary.to_csv(OUT/'route_ice_summary.csv',index=False)
receipt={'passed':True,'point_day_combinations':len(result),'raw_file_sha256':files,
 'point_source_sha256':hashlib.sha256((OUT/'route_daily_points.csv').read_bytes()).hexdigest(),
 'limitations':['nearest grid cell, no interpolation or nearest-valid-cell substitution','same source-clock date and +/-1 day sensitivity, not verified time overlap',
 'no-ice or missing drift is not zero drift','coarse cells do not establish whether bird stood on individual floes','not a transport or return-success estimate']}
(OUT/'route_ice_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(summary.to_string(index=False))
