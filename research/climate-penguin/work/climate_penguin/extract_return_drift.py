"""Geographic ice displacement in Sep-Oct; not individual transport assistance."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,time,json,hashlib
import pandas as pd,numpy as np,xarray as xr
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
RAW=ROOT/'work/climate_penguin/return_drift';RAW.mkdir(exist_ok=True)
EX=RAW/'extracted';EX.mkdir(exist_ok=True)
sites=pd.read_csv(OUT/'daily_ice_locations.csv');geo=Geod(ellps='WGS84')
dates=[d for y in range(2011,2021) for d in pd.date_range(f'{y}-09-01',f'{y}-10-31')]
def get(d):
    name=f'ice_drift_sh_ease2-750_cdr-v1p0_24h-{d:%Y%m%d}1200.nc'
    url=f'https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/drift_455m_files/merged/{d:%Y/%m}/'+name
    p=RAW/name
    try:
        if not p.exists():
            for attempt in range(3):
                r=requests.get(url,timeout=45)
                if r.status_code not in (429,500,502,503,504):break
                time.sleep(attempt+1)
            r.raise_for_status();assert r.content[:3] in (b'CDF',b'\x89HD')
            tmp=p.with_suffix('.part');tmp.write_bytes(r.content);tmp.replace(p)
        return dict(date=str(d.date()),url=url,path=str(p.relative_to(ROOT)).replace('\\','/'),ok=True,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    except Exception as e:return dict(date=str(d.date()),url=url,ok=False,error=str(e))
masks=None;manifest=[]
with ThreadPoolExecutor(max_workers=2) as pool:
    for i,item in enumerate(pool.map(get,dates)):
        if item['ok']:
            target=EX/(item['date']+'.csv')
            if not target.exists():
                with xr.open_dataset(ROOT/item['path']) as z:
                    lat=z.lat.values;lon=z.lon.values
                    if masks is None:
                        masks={}
                        for s in sites.to_dict('records'):
                            dist=geo.inv(np.full(lon.shape,s['longitude']),np.full(lat.shape,s['latitude']),lon,lat)[2]/1000
                            masks[s['location_id']]=(dist>=100)&(dist<500)
                    flag=z.status_flag.values[0];valid=np.isfinite(z.dX.values[0])&np.isfinite(z.dY.values[0])
                    azi,_,length=geo.inv(lon,lat,z.lon1.values[0],z.lat1.values[0])
                    north=length*np.cos(np.deg2rad(azi))/1000;east=length*np.sin(np.deg2rad(azi))/1000
                    sat=valid&np.isin(flag,[20,21,22,30]);nominal=valid&(flag==30);wind=valid&np.isin(flag,[23,24,25])
                    rows=[]
                    for loc,m in masks.items():
                        k=m&sat;n=m&nominal
                        rows.append(dict(location_id=loc,date=item['date'],n_grid=int(m.sum()),n_satellite=int(k.sum()),n_nominal=int(n.sum()),n_wind=int((m&wind).sum()),east_km_day=float(np.mean(east[k])) if k.any() else None,north_km_day=float(np.mean(north[k])) if k.any() else None,nominal_east_km_day=float(np.mean(east[n])) if n.any() else None,nominal_north_km_day=float(np.mean(north[n])) if n.any() else None))
                pd.DataFrame(rows).to_csv(target,index=False)
        manifest.append(item)
        if (i+1)%25==0 or i==len(dates)-1:
            p=OUT/'return_drift_manifest.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(manifest,indent=2));tmp.replace(p)
            print(f'{i+1}/{len(dates)}; errors={sum(not x["ok"] for x in manifest)}',flush=True)
pd.concat([pd.read_csv(EX/(r['date']+'.csv')) for r in manifest if r['ok']],ignore_index=True).to_csv(OUT/'return_drift_daily_2011_2020.csv.gz',index=False,compression='gzip')
print('DONE',len(manifest),flush=True)
