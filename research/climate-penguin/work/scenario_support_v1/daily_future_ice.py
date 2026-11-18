"""Extract actual SIday series; coarse nearest-ocean support is explicit."""
from pathlib import Path
import argparse,hashlib,json
import pandas as pd
import numpy as np
import xarray as xr
import fsspec
import dask
from pyproj import Geod

parser=argparse.ArgumentParser();parser.add_argument('--catalog',required=True);args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[2]/'outputs'
OUT=ROOT/'daily_future_ice_v1';OUT.mkdir(exist_ok=True)
catalog=pd.read_csv(args.catalog)
selected=catalog[(catalog.variable_id=='siconc')&(catalog.table_id=='SIday')&catalog.experiment_id.isin(['historical','ssp245','ssp585'])]
assert len(selected)==3 and selected.source_id.eq('GFDL-CM4').all() and selected.member_id.eq('r1i1p1f1').all()
selected.to_csv(OUT/'selected_sources.csv',index=False)
locations=pd.read_csv(ROOT/'climate_penguin/daily_ice_locations.csv')
locations=locations[locations.cohort=='phenology_coordinate_group'].reset_index(drop=True)
assert len(locations)==66
geod=Geod(ellps='WGS84');mapping=None;meta=[]
for experiment in ['historical','ssp245','ssp585']:
    row=selected[selected.experiment_id==experiment].iloc[0]
    url=row.zstore.replace('gs://','https://storage.googleapis.com/')
    ds=xr.open_zarr(fsspec.get_mapper(url,client_kwargs={'trust_env':True}),consolidated=True)
    assert ds.siconc.attrs['units']=='%'
    dates=ds.time.values;years=ds.time.dt.year.values;months=ds.time.dt.month.values
    lat,lon=np.meshgrid(ds.lat.values,ds.lon.values,indexing='ij')
    if mapping is None:
        # Southern ocean winter mask from an actual historical frame, no
        # replacement by a temporally varying nearest valid cell.
        i=np.flatnonzero((years==2011)&(months==8))[0]
        with dask.config.set(scheduler='synchronous'):frame=ds.siconc.isel(time=i).values
        valid=np.isfinite(frame)&(lat< -45)
        rows=[]
        for a in locations.itertuples():
            _,_,dist=geod.inv(np.full(valid.sum(),a.longitude),np.full(valid.sum(),a.latitude),lon[valid],lat[valid])
            k=int(np.argmin(dist));iy,ix=np.argwhere(valid)[k]
            rows.append(dict(location_id=a.location_id,site_id=a.site_id,latitude=a.latitude,longitude=a.longitude,
                iy=int(iy),ix=int(ix),grid_lat=float(lat[iy,ix]),grid_lon=float(lon[iy,ix]),distance_km=float(dist[k]/1000)))
        mapping=pd.DataFrame(rows);mapping.to_csv(OUT/'grid_support.csv',index=False)
    np.testing.assert_allclose(lat[mapping.iy,mapping.ix],mapping.grid_lat)
    np.testing.assert_allclose(lon[mapping.iy,mapping.ix],mapping.grid_lon)
    selected_years=((years>=2011)&(years<=2014)) if experiment=='historical' else (((years>=2015)&(years<=2020))|((years>=2041)&(years<=2060))|((years>=2081)&(years<=2100)))
    indices=np.flatnonzero(selected_years&(months>=8)&(months<=11))
    out=OUT/f'daily_{experiment}.npz'
    if not out.exists():
        subset=ds.siconc.isel(time=indices,lat=xr.DataArray(mapping.iy.to_numpy(),dims='location'),lon=xr.DataArray(mapping.ix.to_numpy(),dims='location'))
        print(f'Reading {experiment}: {len(indices)} days x {len(mapping)} locations',flush=True)
        with dask.config.set(scheduler='synchronous'):values=subset.transpose('time','location').values
        assert np.isfinite(values).all() and values.min()>=0 and values.max()<=100
        strings=np.array([str(t)[:10] for t in dates[indices]])
        np.savez_compressed(out,dates=strings,values=values,location_ids=mapping.location_id.to_numpy(dtype=str))
    with np.load(out) as a:
        assert a['values'].shape==(len(indices),len(mapping))
    meta.append(dict(experiment=experiment,url=url,units=ds.siconc.attrs['units'],calendar=ds.time.encoding.get('calendar'),chunks=ds.siconc.encoding.get('chunks'),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),days=len(indices)))
    print(f'Completed {experiment}',flush=True)
(OUT/'extraction.json').write_text(json.dumps(dict(sources=meta,catalog_sha256=hashlib.sha256(Path(args.catalog).read_bytes()).hexdigest(),locations=66,limits=['One GFDL-CM4 member only','Native product gr2 is coarse; nearest ocean cell is not the observed coastal buffer','Daily model values are not bias corrected']),indent=2)+'\n')
