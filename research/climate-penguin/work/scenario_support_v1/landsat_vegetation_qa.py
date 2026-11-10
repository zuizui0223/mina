"""Landsat-8 QA-only support in mapped vegetation; both years, one sensor."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.parse import urlparse
import argparse,json,hashlib
from threading import Lock
TOKEN_LOCK=Lock(); TOKENS={}; TOKEN_FAILURES={}
import pandas as pd,numpy as np,requests,geopandas as gpd,rasterio
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.windows import from_bounds
from rasterio.features import rasterize
from shapely.geometry import Point
from shapely.ops import transform,unary_union
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/landsat_vegetation_support_v1';OUT.mkdir(exist_ok=True);CAT=OUT/'catalog';CAT.mkdir(exist_ok=True);CACHE=OUT/'arrays';CACHE.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--map',type=Path,required=True);args=p.parse_args()
a=pd.read_csv(ROOT/'outputs/vegetation_expansion_v1/catalog_support.csv');locations=a[a.year.eq(2018)][['site_id','latitude','longitude']].drop_duplicates();assert locations.site_id.is_unique
maps=gpd.read_file(args.map);maps=maps[maps.Vegetation.isin(['Vegetation','Lichen'])];grid=from_origin(-510,510,30,30);rr,cc=np.indices((34,34));inside=((-495+cc*30)**2+(495-rr*30)**2<=500**2);masks={};projs={}
for r in locations.itertuples():
 crs=f'+proj=aeqd +lat_0={r.latitude} +lon_0={r.longitude} +datum=WGS84 +units=m +no_defs';projs[r.site_id]=crs;circle=Point(0,0).buffer(500,resolution=128);query=transform(Transformer.from_crs(crs,maps.crs,always_xy=True).transform,circle);h=maps.iloc[maps.sindex.query(query,predicate='intersects')].to_crs(crs);u=unary_union(h.geometry).intersection(circle);masks[r.site_id]=rasterize([(u,1)],out_shape=(34,34),transform=grid).astype(bool)&inside
np.savez_compressed(OUT/'mapped_masks_30m.npz',**masks)
def run(task):
 r,year=task;key=f'{r.site_id}_{year}';meta=OUT/(key+'.json');array=CACHE/(key+'.npz')
 if meta.exists() and array.exists():
  cached=json.loads(meta.read_text())
  if cached['errors']==0:return cached
 path=CAT/(key+'.json')
 if path.exists():features=json.loads(path.read_text())['features']
 else:
  url='https://planetarycomputer.microsoft.com/api/stac/v1/search';body={'collections':['landsat-c2-l2'],'intersects':{'type':'Point','coordinates':[r.longitude,r.latitude]},'datetime':f'{year}-01-01T00:00:00Z/{year}-02-28T23:59:59Z','limit':100,'query':{'platform':{'eq':'landsat-8'}}};features=[];pages=0;method='POST'
  while url:
   response=requests.post(url,json=body,timeout=30) if method=='POST' else requests.get(url,timeout=30);response.raise_for_status();d=response.json();features.extend(d.get('features',[]));pages+=1
   nxt=next((x for x in d.get('links',[]) if x.get('rel')=='next'),None)
   if not nxt:break
   if pages>20:raise ValueError('pagination limit')
   url=nxt['href'];method=nxt.get('method','GET');body=nxt.get('body',{})
  path.write_text(json.dumps(dict(features=features,complete=True,retrieved_utc=pd.Timestamp.now(tz='UTC').isoformat())),encoding='utf-8')
 assert all(f['properties']['platform']=='landsat-8' for f in features)
 arrays=[];ids=[];dates=[];tiers=[];records=[];tokens=TOKENS
 for f in features:
  url=f['assets']['qa_pixel']['href'];date=f['properties']['datetime'][:10];tier=f['properties'].get('landsat:collection_category',f['id'].split('_')[-1]);rec=dict(scene_id=f['id'],date=date,tier=tier,url=url)
  try:
   u=urlparse(url);keytoken=(u.hostname.split('.')[0],u.path.split('/')[1])
   with TOKEN_LOCK:
    if keytoken in TOKEN_FAILURES:raise RuntimeError('Signing unavailable for this run: '+TOKEN_FAILURES[keytoken])
    if keytoken not in tokens:
     token=requests.get('https://planetarycomputer.microsoft.com/api/sas/v1/token/'+'/'.join(keytoken),timeout=30)
     if token.status_code!=200:
      TOKEN_FAILURES[keytoken]=str(token.status_code);token.raise_for_status()
     tokens[keytoken]=token.json()['token']
   signed=url+'?'+tokens[keytoken];target=np.ones((34,34),np.uint16)
   with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_TIMEOUT=25,GDAL_HTTP_MAX_RETRY=1):
    with rasterio.open(signed) as src:
     bounds=transform_bounds(projs[r.site_id],src.crs,-550,-550,550,550,densify_pts=21);win=from_bounds(*bounds,src.transform).round_offsets().round_lengths();raw=src.read(1,window=win,boundless=True,fill_value=1)
     reproject(raw,target,src_transform=src.window_transform(win),src_crs=src.crs,dst_transform=grid,dst_crs=projs[r.site_id],src_nodata=1,dst_nodata=1,resampling=Resampling.nearest)
   arrays.append(target);ids.append(f['id']);dates.append(date);tiers.append(tier);rec['status']='ok'
  except Exception as e:rec.update(status='error',error=str(e).split('?')[0][:300])
  records.append(rec)
 stack=np.stack(arrays) if arrays else np.ones((0,34,34),np.uint16);dates=np.array(dates);tiers=np.array(tiers)
 bad=sum(1<<b for b in [0,1,2,3,4,5,7]);clear=((stack&bad)==0)&inside
 # Independent per-bit equality check for the mask.
 independent=np.ones(stack.shape,bool)
 for bit in [0,1,2,3,4,5,7]:independent&=((stack>>bit)&1)==0
 assert np.array_equal(clear,independent&inside)
 np.savez_compressed(array,qa=stack,scene_ids=np.array(ids),dates=dates,tiers=tiers,mapped=masks[r.site_id])
 rows=[]
 for month in ['01','02']:
  for tier_mode in ['all_tiers','T1_only']:
   selected=np.array([d[5:7]==month for d in dates],dtype=bool)
   if tier_mode=='T1_only':selected&=tiers=='T1'
   days=sorted(set(dates[selected]));daily=np.stack([clear[selected&(dates==d)].any(axis=0) for d in days]) if days else np.zeros((0,34,34),bool)
   n=daily.sum(axis=0);rows.append(dict(site_id=r.site_id,year=year,month=int(month),tier_mode=tier_mode,scenes=int(selected.sum()),dates=len(days),mapped_pixels=int(masks[r.site_id].sum()),mapped_once_pixels=int(((n>=1)&masks[r.site_id]).sum()),mapped_twice_pixels=int(((n>=2)&masks[r.site_id]).sum())))
 result=dict(site_id=r.site_id,year=year,catalog_scenes=len(features),errors=sum(x['status']=='error' for x in records),array_file='arrays/'+array.name,array_sha256=hashlib.sha256(array.read_bytes()).hexdigest(),records=records,monthly_support=rows);meta.write_text(json.dumps(result),encoding='utf-8');return result
results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 for future in as_completed([pool.submit(run,(r,y)) for r in locations.itertuples() for y in [2018,2019]]):
  result=future.result();results.append(result);print(f'{len(results)}/16 {result["site_id"]} {result["year"]}, errors {result["errors"]}',flush=True)
pd.DataFrame([x for r in results for x in r['monthly_support']]).sort_values(['site_id','year','month','tier_mode']).to_csv(OUT/'monthly_qa_support.csv',index=False)
pd.DataFrame([{k:v for k,v in r.items() if k not in ['records','monthly_support']} for r in results]).to_csv(OUT/'read_manifest.csv',index=False);print('COMPLETE',flush=True)
