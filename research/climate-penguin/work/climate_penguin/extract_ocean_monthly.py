"""Public GLORYS monthly top-level ocean context; not direct satellite salinity."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd,xarray as xr,fsspec
from scipy.spatial import cKDTree
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
RAW=ROOT/'work/climate_penguin/salinity'
j=json.loads((RAW/'monthly.json').read_text(encoding='utf-8'));url=j['assets']['timeChunked']['href']
d=xr.open_zarr(fsspec.get_mapper(url),consolidated=True)
depth_index=int(np.argmin(np.abs(d.elevation.values)))
sites=pd.read_csv(OUT/'daily_ice_locations.csv');geo=Geod(ellps='WGS84')
sample=d.so.isel(elevation=depth_index).sel(time='2011-09-01',latitude=slice(-80,-48)).load()
lat,lon=np.meshgrid(sample.latitude.values,sample.longitude.values,indexing='ij')
wet=np.isfinite(sample.values);iy,ix=np.where(wet)
def xyz(lon,lat):
    a=np.deg2rad(lon);b=np.deg2rad(lat)
    return np.column_stack([np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)])
_,k=cKDTree(xyz(lon[wet],lat[wet])).query(xyz(sites.longitude.values,sites.latitude.values))
gy=iy[k];gx=ix[k]
gridlat=lat[gy,gx];gridlon=lon[gy,gx]
# sample is a leading slice of the full latitude dimension; assert before indexing.
assert np.array_equal(d.latitude.values[:sample.sizes['latitude']],sample.latitude.values)
sites['grid_lat']=gridlat;sites['grid_lon']=gridlon;sites['grid_y']=gy;sites['grid_x']=gx
sites['grid_distance_km']=geo.inv(sites.longitude.values,sites.latitude.values,gridlon,gridlat)[2]/1000
sites['grid_within_25km']=sites.grid_distance_km<=25
sites.to_csv(OUT/'ocean_grid_support.csv',index=False)
times=pd.DatetimeIndex(d.time.values);chosen=np.flatnonzero((times.year>=2011)&(times.year<=2021)&times.month.isin([8,9,10,11]))
assert len(chosen)==44
arrays={}
for var in ['so','thetao','mlotst']:
    cache=RAW/(var+'_monthly_points.nc')
    if cache.exists():a=xr.open_dataarray(cache).load()
    else:
        a=d[var]
        if 'elevation' in a.dims:a=a.isel(elevation=depth_index)
        a=a.isel(time=chosen,latitude=xr.DataArray(gy,dims='location'),longitude=xr.DataArray(gx,dims='location')).load()
        a.to_netcdf(cache)
    arrays[var]=a.values
    print('Read',var,a.shape,'finite',int(np.isfinite(a.values).sum()),flush=True)
rows=[]
for n,t in enumerate(times[chosen]):
    for i,s in sites.iterrows():
        rows.append(dict(location_id=s.location_id,year=t.year,month=t.month,date=str(t.date()),surface_salinity=float(arrays['so'][n,i]),surface_potential_temperature_c=float(arrays['thetao'][n,i]),mixed_layer_depth_m=float(arrays['mlotst'][n,i]),grid_distance_km=s.grid_distance_km,grid_within_25km=s.grid_within_25km))
p=pd.DataFrame(rows);p.to_csv(OUT/'ocean_monthly_2011_2021.csv',index=False)
manifest={'store':url,'product':'GLOBAL_MULTIYEAR_PHY_001_030','version':'202311','top_level_coordinate_m':float(d.elevation.values[depth_index]),'variables':{v:d[v].attrs for v in arrays},'coordinate_warning':'elevation coordinates negative despite positive=down attribute; nearest-to-zero level selected by absolute value','months':44,'locations':len(sites),'unique_wet_cells':len(sites[['grid_y','grid_x']].drop_duplicates()),'rows':len(p),'distance_max_km':float(sites.grid_distance_km.max()),'distance_median_km':float(sites.grid_distance_km.median()),'locations_beyond_25km':int((~sites.grid_within_25km).sum()),'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in RAW.glob('*_monthly_points.nc')}}
(OUT/'ocean_monthly_manifest.json').write_text(json.dumps(manifest,indent=2,default=str),encoding='utf-8')
print('DONE',len(p),'rows; beyond25km',manifest['locations_beyond_25km'],flush=True)
