"""OSI-450-a1 daily August-November regional exposures; not inferred bird routes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,hashlib,time
import requests
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/climate_penguin'
RAW=ROOT/'work/climate_penguin/osi_concentration';RAW.mkdir(exist_ok=True)
EXTRACT=RAW/'extracted';EXTRACT.mkdir(exist_ok=True)
ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=2011);ap.add_argument('--end',type=int,default=2020);args=ap.parse_args()
sites=pd.read_csv(OUT/'satellite_screen_locations.csv').reset_index(drop=True)
sites['location_id']=['loc'+str(i).zfill(3) for i in sites.index]
sites.to_csv(OUT/'daily_ice_locations.csv',index=False)
sample=xr.open_dataset(ROOT/'work/climate_penguin/conc_sample.nc')
lat=sample.lat.values;lon=sample.lon.values
sample.close();geo=Geod(ellps='WGS84');masks=[]
for s in sites.to_dict('records'):
    distance=geo.inv(np.full(lon.shape,s['longitude']),np.full(lat.shape,s['latitude']),lon,lat)[2]/1000
    for inner,outer in [(0,100),(100,500)]:
        ix=np.flatnonzero((distance>=inner)&(distance<outer))
        masks.append((s['location_id'],inner,outer,ix))
dates=[d for y in range(args.start,args.end+1) for d in pd.date_range(f'{y}-08-01',f'{y}-11-30')]
def fetch(d):
    name=f'ice_conc_sh_ease2-250_cdr-v3p1_{d:%Y%m%d}1200.nc';p=RAW/name
    url=f'https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/conc_450a1_files/{d:%Y/%m}/'+name
    try:
        if not p.exists():
            for attempt in range(3):
                r=requests.get(url,timeout=45)
                if r.status_code not in [429,500,502,503,504]:break
                time.sleep(attempt+1)
            r.raise_for_status()
            assert r.content[:3] in [b'CDF',b'\x89HD'],'not netCDF'
            tmp=p.with_suffix('.part');tmp.write_bytes(r.content);tmp.replace(p)
        return {'date':str(d.date()),'url':url,'path':str(p.relative_to(ROOT)).replace('\\','/'),'ok':True,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    except Exception as e:return {'date':str(d.date()),'url':url,'ok':False,'error':str(e)}
manifest=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    for i,item in enumerate(pool.map(fetch,dates)):
        if item['ok']:
            target=EXTRACT/(item['date']+'.csv')
            if not target.exists():
                with xr.open_dataset(ROOT/item['path']) as z:
                    assert str(pd.Timestamp(z.time.values[0]).date())==item['date']
                    assert z.ice_conc.attrs['units']=='%'
                    a=z.ice_conc.values[0].ravel();f=z.status_flag.values[0].ravel();u=z.total_standard_uncertainty.values[0].ravel()
                    assert a[np.isfinite(a)].min()>=0 and a[np.isfinite(a)].max()<=100.001
                    fi=np.where(np.isfinite(f),f,32767).astype(np.int32)
                    ocean=((fi&3)==0)&np.isfinite(f)
                    rows=[]
                    for loc,inner,outer,ix in masks:
                        oi=ix[ocean[ix]];vi=oi[np.isfinite(a[oi])];n=len(vi)
                        rows.append({'location_id':loc,'date':item['date'],'inner_km':inner,'outer_km':outer,
                         'n_grid':len(ix),'n_ocean':len(oi),'n_valid':n,
                         'sic_percent_mean':float(a[vi].mean()) if n else None,
                         'fraction_cells_ice15':float((a[vi]>=15).mean()) if n else None,
                         'mean_cell_uncertainty_percent':float(np.nanmean(u[vi])) if n else None,
                         'n_interpolated':int(((fi[vi]&96)>0).sum()),
                         'n_land_spill_corrected':int(((fi[vi]&8)>0).sum()),
                         'n_high_temperature_flag':int(((fi[vi]&16)>0).sum()),
                         'n_climatology_zero':int(((fi[vi]&128)>0).sum())})
                pd.DataFrame(rows).to_csv(target,index=False)
        manifest.append(item)
        if (i+1)%25==0 or i==len(dates)-1:
            (OUT/'daily_concentration_manifest.json').write_text(json.dumps(manifest,indent=2))
            print(f'{i+1}/{len(dates)} dates; failures={sum(not x["ok"] for x in manifest)}',flush=True)
frames=[pd.read_csv(EXTRACT/(x['date']+'.csv')) for x in manifest if x['ok']]
d=pd.concat(frames,ignore_index=True)
d.to_csv(OUT/'daily_concentration_2011_2020_aug_nov.csv.gz',index=False,compression='gzip')
assert not d.duplicated(['location_id','date','inner_km']).any()
print('DONE',len(d),'rows',d.date.nunique(),'days',flush=True)
