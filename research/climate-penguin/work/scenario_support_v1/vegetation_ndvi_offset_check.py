"""Native original/COG comparison for flagged 2022 reflectance metadata."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib,xml.etree.ElementTree as ET
import pandas as pd,numpy as np,requests,rasterio
from rasterio.warp import transform
from rasterio.windows import Window
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/vegetation_annual_ndvi_v1';CACHE=OUT/'native';CACHE.mkdir(exist_ok=True)
chosen=pd.read_csv(OUT/'offset_flagged_scenes.csv').drop_duplicates('scene_id');loc=pd.read_csv(ROOT/'outputs/climate_penguin/daily_ice_locations.csv');loc=loc[loc.cohort.eq('macro_40')].set_index('site_id')
def run(r):
 metadata=CACHE/(r.scene_id+'.json')
 if metadata.exists():return json.loads(metadata.read_text())
 f=next(f for f in json.loads((ROOT/'outputs/vegetation_annual_support_v1/catalog'/f'{r.site_id}_{r.year}.json').read_text())['features'] if f['id']==r.scene_id)
 endpoint='https://sentinel-s2-l2a.s3.eu-central-1.amazonaws.com/';logs=[]
 try:
  prefix=f['assets']['red-jp2']['href'].split('sentinel-s2-l2a/')[1].rsplit('/',1)[0]+'/'
  res=requests.get(endpoint,params={'list-type':'2','prefix':prefix,'max-keys':1000},timeout=30);res.raise_for_status();(CACHE/(r.scene_id+'.xml')).write_bytes(res.content)
  keys=[x.text for x in ET.fromstring(res.content).iter() if x.tag.endswith('}Key')]
  for band,code in [('red','B04'),('nir','B08')]:
   rec=dict(scene_id=r.scene_id,site_id=r.site_id,band=band)
   try:
    candidates=[k for k in keys if k.endswith('/R10m/'+code+'.jp2')];assert len(candidates)==1
    url=endpoint+candidates[0];rec.update(original_url=url,cog_url=f['assets'][band]['href'])
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif,.jp2',GDAL_HTTP_TIMEOUT=30):
     with rasterio.open(rec['cog_url']) as cog,rasterio.open(url) as original:
      assert cog.crs==original.crs and cog.transform==original.transform
      l=loc.loc[r.site_id];x,y=transform('EPSG:4326',cog.crs,[l.longitude],[l.latitude]);i,j=cog.index(x[0],y[0]);win=Window(j-32,i-32,64,64)
      a=cog.read(1,window=win,boundless=True,fill_value=0);b=original.read(1,window=win,boundless=True,fill_value=0)
    valid=(a>0)&(b>1001);delta=b.astype(int)-a.astype(int)
    path=CACHE/(r.scene_id+'_'+band+'.npz');np.savez_compressed(path,cog=a,original=b,valid=valid)
    rec.update(status='ok',valid_pixels=int(valid.sum()),equal_pixels=int((valid&(delta==0)).sum()),difference1000_pixels=int((valid&(delta==1000)).sum()),array_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
   except Exception as e:rec.update(status='error',error=str(e))
   logs.append(rec)
 except Exception as e:logs.append(dict(scene_id=r.scene_id,status='error',error=str(e)))
 metadata.write_text(json.dumps(logs),encoding='utf-8');return logs
rows=[]
with ThreadPoolExecutor(max_workers=2) as pool:
 for future in as_completed([pool.submit(run,r) for r in chosen.itertuples()]):
  rows.extend(future.result());print('native checks',len(rows),flush=True)
pd.DataFrame(rows).to_csv(OUT/'offset_native_checks.csv',index=False);print(pd.DataFrame(rows).to_string(index=False),flush=True)
