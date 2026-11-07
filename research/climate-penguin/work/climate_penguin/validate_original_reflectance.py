"""Compare sampled native COG pixels against listed original JP2 objects."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib,xml.etree.ElementTree as ET
import requests,pandas as pd,numpy as np,rasterio
from rasterio.warp import transform
from rasterio.windows import Window
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
CACHE=ROOT/'work/climate_penguin/reflectance_validation';CACHE.mkdir(exist_ok=True)
catalog=pd.read_csv(OUT/'satellite_january_catalog_screen.csv');features={}
for r in catalog[catalog.year.isin([2019,2024])].itertuples():
    for f in json.loads((ROOT/r.cached_response).read_text())['features']:features[f['id']]=f
locations=pd.read_csv(OUT/'daily_ice_locations.csv').set_index('location_id')
chosen=pd.read_csv(OUT/'reflectance_offset_sensitivity.csv')
def run(row):
    f=features[row.scene_id];loc=locations.loc[row.location_id];logs=[]
    prefix=f['assets']['red-jp2']['href'].split('sentinel-s2-l2a/')[1].rsplit('/',1)[0]+'/'
    endpoint='https://sentinel-s2-l2a.s3.eu-central-1.amazonaws.com/'
    res=requests.get(endpoint,params={'list-type':'2','prefix':prefix,'max-keys':1000},timeout=30);res.raise_for_status()
    (CACHE/(row.scene_id+'_listing.xml')).write_bytes(res.content)
    keys=[x.text for x in ET.fromstring(res.content).iter() if x.tag.endswith('}Key')]
    for band,code in [('red','B04'),('nir','B08')]:
        candidates=[k for k in keys if k.endswith('/R10m/'+code+'.jp2')];assert len(candidates)==1,candidates
        url=endpoint+candidates[0];log=dict(location_id=row.location_id,site_id=row.site_id,year=row.year,scene_id=row.scene_id,band=band,original_url=url,cog_url=f['assets'][band]['href'])
        try:
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif,.jp2',GDAL_HTTP_TIMEOUT=45):
                with rasterio.open(log['cog_url']) as cog,rasterio.open(url) as original:
                    assert cog.crs==original.crs and cog.transform==original.transform
                    x,y=transform('EPSG:4326',cog.crs,[loc.longitude],[loc.latitude]);i,j=cog.index(x[0],y[0]);win=Window(j-32,i-32,64,64)
                    a=cog.read(1,window=win,boundless=True,fill_value=0);b=original.read(1,window=win,boundless=True,fill_value=0)
            valid=(a>0)&(b>0);delta=b.astype(np.int32)-a.astype(np.int32)
            filename=CACHE/f'{row.location_id}_{row.year}_{band}_native_comparison.npz'
            np.savez_compressed(filename,cog=a,original=b,valid=valid)
            log.update(status='ok',valid_pixels=int(valid.sum()),median_original_minus_cog=float(np.median(delta[valid])) if valid.any() else None,
                equal_pixels=int((valid&(delta==0)).sum()),difference1000_pixels=int((valid&(delta==1000)).sum()),
                clipped_one_pixels=int((valid&(a==1)&(b<=1001)).sum()),
                array_sha256=hashlib.sha256(filename.read_bytes()).hexdigest())
        except Exception as e:log.update(status='error',error=str(e))
        logs.append(log)
    (CACHE/(row.location_id+'_'+str(row.year)+'_validation.json')).write_text(json.dumps(logs,indent=2),encoding='utf-8')
    return logs
rows=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    jobs=[pool.submit(run,r) for r in chosen.itertuples(index=False)]
    for j in as_completed(jobs):
        rows.extend(j.result());print('bands completed',len(rows),'/28',flush=True)
pd.DataFrame(rows).to_csv(OUT/'reflectance_original_pixel_validation.csv',index=False)
print(pd.DataFrame(rows).groupby(['year','status']).size().to_string(),flush=True)
