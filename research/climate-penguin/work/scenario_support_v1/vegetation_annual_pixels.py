"""Read local SCL pixels for all count-aligned January candidates, retaining dates."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib,zipfile
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.windows import from_bounds
from rasterio.transform import from_origin
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'outputs/vegetation_annual_support_v1';OUT=ROOT/'outputs/vegetation_annual_pixels_v1';OUT.mkdir(exist_ok=True)
CACHE=OUT/'pixels';CACHE.mkdir(exist_ok=True)
archive=OUT/'pixel_sources.zip'
if archive.exists():
 with zipfile.ZipFile(archive) as z:
  for name in z.namelist():
   assert not Path(name).is_absolute() and '..' not in Path(name).parts
   target=OUT/name
   if not target.exists():target.write_bytes(z.read(name))
loc=pd.read_csv(ROOT/'outputs/climate_penguin/daily_ice_locations.csv')
loc=loc[loc.cohort.eq('macro_40')].set_index('site_id')
assert loc.index.is_unique
support=pd.read_csv(SRC/'catalog_support.csv')
rr,cc=np.indices((50,50));INSIDE=((-490+cc*20)**2+(490-rr*20)**2<=500**2);GRID=from_origin(-500,500,20,20)
def run(row):
 key=f'{row.site_id}_{row.image_year}';meta=OUT/(key+'.json');path=CACHE/(key+'.npz')
 if meta.exists() and path.exists():
  old=json.loads(meta.read_text())
  if old['read_errors']==0:return old
 location=loc.loc[row.site_id];crs=f'+proj=aeqd +lat_0={location.latitude} +lon_0={location.longitude} +datum=WGS84 +units=m +no_defs'
 source=SRC/row.cached_file
 assert hashlib.sha256(source.read_bytes()).hexdigest()==row.sha256
 features=json.loads(source.read_text())['features'];bydate={};records=[]
 for f in features:
  rec={'scene_id':f['id'],'date':f['properties']['datetime'][:10]}
  try:
   url=f['assets']['scl']['href'];rec['url']=url
   target=np.zeros((50,50),np.uint8)
   with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=20,GDAL_HTTP_MAX_RETRY=1):
    with rasterio.open(url) as src:
     bounds=transform_bounds(crs,src.crs,-540,-540,540,540,densify_pts=21)
     win=from_bounds(*bounds,src.transform).round_offsets().round_lengths()
     raw=src.read(1,window=win,boundless=True,fill_value=0)
     reproject(raw,target,src_transform=src.window_transform(win),src_crs=src.crs,dst_transform=GRID,dst_crs=crs,src_nodata=0,dst_nodata=0,resampling=Resampling.nearest)
   assert np.isin(target,np.arange(12)).all()
   bydate.setdefault(rec['date'],[]).append(target)
   rec.update(status='ok',land_pixels=int((INSIDE&np.isin(target,[4,5])).sum()),snow_pixels=int((INSIDE&(target==11)).sum()))
  except Exception as exc:rec.update(status='error',error=str(exc))
  records.append(rec)
 dates=sorted(bydate);land=[];snow=[];water=[];conflict=[]
 for date in dates:
  a=np.stack(bydate[date]);l=np.isin(a,[4,5]).any(axis=0)&INSIDE;s=(a==11).any(axis=0)&INSIDE;w=(a==6).any(axis=0)&INSIDE
  bad=(l&s)|(l&w)|(s&w)
  land.append(l&~bad);snow.append(s&~bad);water.append(w&~bad);conflict.append(bad)
 shape=(0,50,50)
 arrays={k:np.stack(v) if v else np.zeros(shape,bool) for k,v in [('land',land),('snow',snow),('water',water),('conflict',conflict)]}
 np.savez_compressed(path,dates=np.array(dates,dtype='U10'),inside=INSIDE,**arrays)
 count=arrays['land'].sum(axis=0)
 rec=dict(site_id=row.site_id,image_year=int(row.image_year),scenes=len(features),read_success=sum(x['status']=='ok' for x in records),read_errors=sum(x['status']=='error' for x in records),observed_dates=len(dates),circle_pixels=int(INSIDE.sum()),land_once_pixels=int((count>=1).sum()),land_twice_pixels=int((count>=2).sum()),snow_once_pixels=int(arrays['snow'].any(axis=0).sum()),conflict_once_pixels=int(arrays['conflict'].any(axis=0).sum()),pixel_file='pixels/'+path.name,pixel_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_sha256=row.sha256,scene_records=records)
 meta.write_text(json.dumps(rec),encoding='utf-8');return rec
results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 fs=[pool.submit(run,r) for r in support.itertuples()]
 for future in as_completed(fs):
  r=future.result();results.append({k:v for k,v in r.items() if k!='scene_records'})
  print(f'{len(results)}/{len(support)} {r["site_id"]} {r["image_year"]}: land twice {r["land_twice_pixels"]}, errors {r["read_errors"]}',flush=True)
s=pd.DataFrame(results).sort_values(['site_id','image_year']);s.to_csv(OUT/'local_support.csv',index=False)
summary=[]
for site,g in s.groupby('site_id'):
 available=g[(g.scenes>0)&(g.read_errors==0)]
 masks=[]
 for r in available.itertuples():
  with np.load(OUT/r.pixel_file) as a:masks.append(a['land'].sum(axis=0)>=2)
 common=np.logical_and.reduce(masks) if masks else np.zeros((50,50),bool)
 summary.append(dict(site_id=site,queried_years=len(g),complete_nonempty_years=len(available),years_with_land_twice=int((available.land_twice_pixels>0).sum()),common_all_available_years_twice_pixels=int(common.sum()),available_years=';'.join(map(str,available.image_year))))
pd.DataFrame(summary).to_csv(OUT/'cross_year_support.csv',index=False)
print('COMPLETE',len(s),'site-years; read errors',s.read_errors.sum(),flush=True)
