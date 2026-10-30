"""Audit original ERA5 snow-water-equivalent and land fractions; no snow trend."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import requests
import numcodecs
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/snow_grid_support_v1'
URL='https://storage.googleapis.com/gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3'


def main():
    OUT.mkdir(exist_ok=True)
    source=ROOT/'outputs/climate_penguin/daily_ice_locations.csv'
    sites=pd.read_csv(source).drop_duplicates('location_id')
    assert len(sites)==106
    response=requests.get(URL+'/.zmetadata',timeout=30);response.raise_for_status()
    (OUT/'source_zmetadata.json').write_bytes(response.content)
    metadata=response.json()['metadata']
    def chunk(variable,index):
        response=requests.get(URL+'/'+variable+'/'+index,timeout=30);response.raise_for_status()
        desc=metadata[variable+'/.zarray']
        assert desc['filters'] is None
        decoded=numcodecs.get_codec(desc['compressor']).decode(response.content)
        print('READ',variable,index,len(response.content),flush=True)
        return np.frombuffer(decoded,dtype=desc['dtype']).reshape(desc['chunks'])
    dates=['2011-09-01T00:00:00','2020-09-01T00:00:00']
    lat=chunk('latitude','0');lon=chunk('longitude','0')
    assert metadata['snow_depth/.zattrs']['units']=='m of water equivalent'
    assert metadata['time/.zattrs']['units']=='hours since 1900-01-01 00:00:00'
    first=int(chunk('time','0')[0]);length=metadata['time/.zarray']['chunks'][0]
    indices=[]
    for date in dates:
        hour=int((np.datetime64(date)-np.datetime64('1900-01-01T00:00:00'))/np.timedelta64(1,'h'))
        idx=hour-first
        assert int(chunk('time',str(idx//length))[idx%length])==hour
        indices.append(idx)
    arrays={v:np.stack([chunk(v,f'{i}.0.0')[0] for i in indices]) for v in ['land_sea_mask','snow_depth']}
    assert all(np.isfinite(v).all() for v in arrays.values())
    np.savez_compressed(OUT/'source_snapshots.npz',latitude=lat,longitude=lon,**arrays)
    geod=Geod(ellps='WGS84');rows=[]
    for site in sites.to_dict('records'):
        iy=int(np.argmin(abs(lat-site['latitude'])))
        ix=int(np.argmin(abs((lon-site['longitude']+180)%360-180)))
        distance=geod.inv(site['longitude'],site['latitude'],float(lon[ix]),float(lat[iy]))[2]/1000
        for n,date in enumerate(dates):
            fraction=float(arrays['land_sea_mask'][n,iy,ix])
            assert -.001<=fraction<=1.001
            rows.append(dict(location_id=site['location_id'],date=date,latitude=site['latitude'],longitude=site['longitude'],
                grid_lat=float(lat[iy]),grid_lon=float(lon[ix]),distance_km=distance,
                land_fraction=fraction,majority_land=fraction>=.5,
                snow_water_equivalent_m=float(arrays['snow_depth'][n,iy,ix])))
    t=pd.DataFrame(rows);t.to_csv(OUT/'nearest_grid_snapshots.csv',index=False)
    summary=t.groupby('date',as_index=False).agg(locations=('location_id','size'),majority_land=('majority_land','sum'),
        zero_land=('land_fraction',lambda x:int((x<=1e-6).sum())),median_land_fraction=('land_fraction','median'),
        max_distance_km=('distance_km','max'))
    summary.to_csv(OUT/'summary.csv',index=False)
    locations=pd.read_csv(source)
    behavior=pd.read_csv(ROOT/'outputs/climate_penguin/behavior_environment_coordinate_join.csv')
    groups={'all':sites.location_id,'macro40':locations[locations.cohort=='macro_40'].location_id,
            'behavior':behavior.location_id.unique()}
    coverage=[]
    for name,ids in groups.items():
        a=t[t.date==dates[0]];a=a[a.location_id.isin(ids)]
        coverage.append(dict(cohort=name,locations=len(a),land_fraction_above_03=int(a.land_fraction.gt(.3).sum()),
                             land_fraction_at_least_05=int(a.land_fraction.ge(.5).sum()),
                             unique_cells=len(a[['grid_lat','grid_lon']].drop_duplicates())))
    pd.DataFrame(coverage).to_csv(OUT/'cohort_support.csv',index=False)
    manifest=dict(status='grid_support_audit_only',url=URL,dates=dates,
        units=dict(snow_depth=metadata['snow_depth/.zattrs'],land_sea_mask=metadata['land_sea_mask/.zattrs']),
        source_locations_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        snapshots_sha256=hashlib.sha256((OUT/'source_snapshots.npz').read_bytes()).hexdigest(),
        unique_cells=len(t[['grid_lat','grid_lon']].drop_duplicates()),
        maximum_land_fraction_change=float(np.max(abs(arrays['land_sea_mask'][0]-arrays['land_sea_mask'][1]))),
        limits=['Two snapshots are not seasonal means or a snow trend',
                'Water equivalent is not physical snow depth or snow cover fraction',
                'Nearest grid and descriptive 0.5 fraction do not validate breeding-ground snow',
                'No substitution of missing or marine snow values for terrestrial absence'])
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(summary.to_string(index=False));print('unique cells',manifest['unique_cells'])


if __name__=='__main__':main()
