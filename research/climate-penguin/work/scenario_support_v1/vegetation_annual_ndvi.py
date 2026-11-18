"""Daily NDVI from count-aligned scenes; local SCL mask, no greening attribution."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib,warnings
import pandas as pd
import numpy as np
import rasterio
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.windows import from_bounds
from rasterio.transform import from_origin
ROOT=Path(__file__).resolve().parents[2];SUP=ROOT/'outputs/vegetation_annual_pixels_v1';CAT=ROOT/'outputs/vegetation_annual_support_v1';OUT=ROOT/'outputs/vegetation_annual_ndvi_v1';OUT.mkdir(exist_ok=True);CACHE=OUT/'arrays';CACHE.mkdir(exist_ok=True)
support=pd.read_csv(SUP/'local_support.csv');support=support[(support.land_twice_pixels>0)&(support.read_errors==0)]
loc=pd.read_csv(ROOT/'outputs/climate_penguin/daily_ice_locations.csv');loc=loc[loc.cohort.eq('macro_40')].set_index('site_id');assert loc.index.is_unique
GRID=from_origin(-500,500,20,20)
def run(r):
 key=f'{r.site_id}_{r.image_year}';meta=OUT/(key+'.json');path=CACHE/(key+'.npz')
 if meta.exists() and path.exists():
  old=json.loads(meta.read_text())
  if old['errors']==0:return old
 info=json.loads((SUP/(key+'.json')).read_text());wanted={x['scene_id'] for x in info['scene_records'] if x['status']=='ok' and x['land_pixels']>0}
 features=json.loads((CAT/'catalog'/(key+'.json')).read_text())['features'];features=[f for f in features if f['id'] in wanted]
 location=loc.loc[r.site_id];crs=f'+proj=aeqd +lat_0={location.latitude} +lon_0={location.longitude} +datum=WGS84 +units=m +no_defs'
 with np.load(SUP/r.pixel_file) as a:
  dates=a['dates'];land=a['land'];inside=a['inside']
 daymask={date:mask for date,mask in zip(dates,land)};bydate={};records=[];raws=[];ids=[]
 for f in features:
  rec=dict(scene_id=f['id'],date=f['properties']['datetime'][:10],offset_already_applied=f['properties'].get('earthsearch:boa_offset_applied'),bands={})
  try:
   arrays=[]
   for band in ['red','nir','scl']:
    asset=f['assets'][band];target=np.full((50,50),np.nan,np.float32)
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=20,GDAL_HTTP_MAX_RETRY=1):
     with rasterio.open(asset['href']) as src:
      bounds=transform_bounds(crs,src.crs,-540,-540,540,540,densify_pts=21);win=from_bounds(*bounds,src.transform).round_offsets().round_lengths();raw=src.read(1,window=win,boundless=True,fill_value=0)
      reproject(raw,target,src_transform=src.window_transform(win),src_crs=src.crs,dst_transform=GRID,dst_crs=crs,src_nodata=0,dst_nodata=np.nan,resampling=Resampling.nearest if band=='scl' else Resampling.average)
    arrays.append(target)
    if band!='scl':
     rb=asset['raster:bands'][0];offset=rb.get('offset',0);applied=rec['offset_already_applied']
     if applied is True:offset=0
     elif applied is not False and offset!=0:raise ValueError('Ambiguous reflectance offset metadata')
     rec['bands'][band]=dict(url=asset['href'],scale=rb.get('scale',1),asset_offset=rb.get('offset',0),used_offset=offset)
   rawred,rawnir,scl=arrays;red=rawred*rec['bands']['red']['scale']+rec['bands']['red']['used_offset'];nir=rawnir*rec['bands']['nir']['scale']+rec['bands']['nir']['used_offset']
   mask=daymask[rec['date']]&inside&np.isin(scl,[4,5])&np.isfinite(red)&np.isfinite(nir)&(red>0)&(nir>0)
   nd=np.full((50,50),np.nan,np.float32);nd[mask]=(nir[mask]-red[mask])/(nir[mask]+red[mask]);assert (np.abs(nd[mask])<=1).all()
   bydate.setdefault(rec['date'],[]).append(nd);raws.append(np.stack(arrays));ids.append(f['id']);rec.update(status='ok',valid_pixels=int(mask.sum()))
  except Exception as e:rec.update(status='error',error=str(e))
  records.append(rec)
 outdates=sorted(bydate);daily=[]
 with warnings.catch_warnings():
  warnings.simplefilter('ignore',RuntimeWarning)
  for date in outdates:daily.append(np.nanmedian(np.stack(bydate[date]),axis=0))
  daily=np.stack(daily) if daily else np.zeros((0,50,50),np.float32)
  annual=np.nanmedian(daily,axis=0) if len(daily) else np.full((50,50),np.nan)
  spread=np.nanquantile(daily,.75,axis=0)-np.nanquantile(daily,.25,axis=0) if len(daily) else np.full((50,50),np.nan)
 n=np.isfinite(daily).sum(axis=0);annual[n<2]=np.nan;spread[n<2]=np.nan
 np.savez_compressed(path,raw_bands=np.stack(raws) if raws else np.zeros((0,3,50,50)),scene_ids=np.array(ids),dates=np.array(outdates),daily_ndvi=daily,annual_median=annual,daily_iqr=spread,valid_dates=n)
 result=dict(site_id=r.site_id,image_year=int(r.image_year),selected_scenes=len(features),successful_scenes=sum(x['status']=='ok' for x in records),errors=sum(x['status']=='error' for x in records),dates=len(outdates),pixels_two_dates=int((n>=2).sum()),array_file='arrays/'+path.name,array_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),records=records)
 meta.write_text(json.dumps(result),encoding='utf-8');return result
results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 fs=[pool.submit(run,r) for r in support.itertuples()]
 for future in as_completed(fs):
  r=future.result();results.append({k:v for k,v in r.items() if k!='records'});print(f'{len(results)}/{len(support)} {r["site_id"]} {r["image_year"]}: {r["pixels_two_dates"]} pixels, {r["errors"]} errors',flush=True)
pd.DataFrame(results).sort_values(['site_id','image_year']).to_csv(OUT/'annual_support.csv',index=False)
print('COMPLETE',flush=True)
