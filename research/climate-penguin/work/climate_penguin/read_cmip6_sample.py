"""Actual CMIP6 array read and coastal grid support, not a calibrated forecast."""
from pathlib import Path
import pandas as pd,numpy as np,xarray as xr,fsspec,json
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
catalog=pd.read_csv(OUT/'cmip6_candidate_stores.csv')
r=catalog[(catalog.source_id=='ACCESS-CM2')&(catalog.member_id=='r1i1p1f1')&(catalog.variable_id=='siconc')&(catalog.experiment_id=='ssp245')].iloc[0]
url=r.zstore.replace('gs://','https://storage.googleapis.com/')
d=xr.open_zarr(fsspec.get_mapper(url),consolidated=True)
lat=d.latitude.values;lon=d.longitude.values
# First frame establishes a model ocean-cell mask, not observed ice presence.
sample=d.siconc.isel(time=8).values
valid=np.isfinite(sample)&(lat<0)
iy,ix=np.where(valid);geo=Geod(ellps='WGS84');rows=[]
sites=pd.read_csv(OUT/'daily_ice_locations.csv')
for s in sites.to_dict('records'):
    distance=geo.inv(np.full(len(ix),s['longitude']),np.full(len(ix),s['latitude']),lon[iy,ix],lat[iy,ix])[2]/1000
    k=int(np.argmin(distance));rows.append(dict(s,grid_j=int(iy[k]),grid_i=int(ix[k]),grid_lat=float(lat[iy[k],ix[k]]),grid_lon=float(lon[iy[k],ix[k]]),distance_km=float(distance[k])))
p=pd.DataFrame(rows);p.to_csv(OUT/'cmip6_sample_coastal_grid_support.csv',index=False)
# Read three September frames across the actual future array.
times=pd.DatetimeIndex(d.time.values);selected=np.flatnonzero((times.month==9)&times.year.isin([2015,2050,2100]))
v=d.siconc.isel(time=selected,j=xr.DataArray(p.grid_j.to_numpy(),dims='location'),i=xr.DataArray(p.grid_i.to_numpy(),dims='location')).load()
a=v.values;assert np.nanmin(a)>=0 and np.nanmax(a)<=100.001
records=[{'location_id':p.iloc[k].location_id,'date':str(times[t].date()),'model':'ACCESS-CM2','scenario':'ssp245','member':'r1i1p1f1','sic_percent':float(a[n,k]),'purpose':'raw_array_access_check_not_calibrated_prediction'} for n,t in enumerate(selected) for k in range(len(p))]
pd.DataFrame(records).to_csv(OUT/'cmip6_sample_actual_values.csv',index=False)
(OUT/'cmip6_array_read_checks.json').write_text(json.dumps({'store':url,'first_date':str(times[0]),'last_date':str(times[-1]),'n_months':len(times),'n_locations':len(p),'unique_model_cells':len(p[['grid_j','grid_i']].drop_duplicates()),'max_distance_km':float(p.distance_km.max()),'median_distance_km':float(p.distance_km.median()),'read_values':len(records),'warning':'One model/member/scenario, uncorrected coarse cells. No behavioral forecast or climate-change attribution.'},indent=2))
print('Read',len(records),'actual values; unique cells',len(p[['grid_j','grid_i']].drop_duplicates()),'distance median/max km',p.distance_km.median(),p.distance_km.max(),flush=True)
