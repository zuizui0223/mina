"""Date-independent SCL support inside mapped vegetation, Jan and Feb separately."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse,json,hashlib,itertools
import pandas as pd,numpy as np,geopandas as gpd,rasterio
from shapely.geometry import Point
from shapely.ops import transform,unary_union
from pyproj import Transformer
from rasterio.features import rasterize
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.windows import from_bounds
from rasterio.transform import from_origin
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'outputs/vegetation_expansion_v1';OUT=ROOT/'outputs/vegetation_expansion_pixels_v1';OUT.mkdir(exist_ok=True);CACHE=OUT/'arrays';CACHE.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--map',type=Path,required=True);args=p.parse_args();g=gpd.read_file(args.map);g=g[g.Vegetation.isin(['Vegetation','Lichen'])]
s=pd.read_csv(SRC/'catalog_support.csv');locations=s[['site_id','latitude','longitude']].drop_duplicates();assert locations.site_id.is_unique
rr,cc=np.indices((50,50));inside=((-490+cc*20)**2+(490-rr*20)**2<=500**2);grid=from_origin(-500,500,20,20);masks={};projections={}
for r in locations.itertuples():
 local=f'+proj=aeqd +lat_0={r.latitude} +lon_0={r.longitude} +datum=WGS84 +units=m +no_defs';projections[r.site_id]=local;circle=Point(0,0).buffer(500,resolution=128);query=transform(Transformer.from_crs(local,g.crs,always_xy=True).transform,circle);h=g.iloc[g.sindex.query(query,predicate='intersects')].to_crs(local);u=unary_union(h.geometry).intersection(circle)
 masks[r.site_id]=rasterize([(u,1)],out_shape=(50,50),transform=grid).astype(bool)&inside
np.savez_compressed(OUT/'mapped_masks.npz',**masks)
def run(r):
 key=f'{r.site_id}_{r.year}_{r.month:02}';meta=OUT/(key+'.json');path=CACHE/(key+'.npz')
 if meta.exists() and path.exists():
  old=json.loads(meta.read_text())
  if old['read_errors']==0:return old
 source=SRC/r.cached_file;assert hashlib.sha256(source.read_bytes()).hexdigest()==r.sha256;features=json.loads(source.read_text())['features'];bydate={};records=[]
 for f in features:
  rec=dict(scene_id=f['id'],date=f['properties']['datetime'][:10],url=f['assets']['scl']['href'])
  try:
   target=np.zeros((50,50),np.uint8)
   with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=20,GDAL_HTTP_MAX_RETRY=1):
    with rasterio.open(rec['url']) as src:
     bounds=transform_bounds(projections[r.site_id],src.crs,-540,-540,540,540,densify_pts=21);win=from_bounds(*bounds,src.transform).round_offsets().round_lengths();raw=src.read(1,window=win,boundless=True,fill_value=0)
     reproject(raw,target,src_transform=src.window_transform(win),src_crs=src.crs,dst_transform=grid,dst_crs=projections[r.site_id],src_nodata=0,dst_nodata=0,resampling=Resampling.nearest)
   assert np.isin(target,np.arange(12)).all();bydate.setdefault(rec['date'],[]).append(target);rec.update(status='ok',mapped_clear_pixels=int((np.isin(target,[4,5])&masks[r.site_id]).sum()))
  except Exception as e:rec.update(status='error',error=str(e))
  records.append(rec)
 dates=sorted(bydate);land=[];snow=[]
 for date in dates:
  a=np.stack(bydate[date]);l=np.isin(a,[4,5]).any(axis=0)&inside;w=(a==6).any(axis=0);ice=(a==11).any(axis=0);land.append(l&~w&~ice);snow.append(ice&~l&~w&inside)
 land=np.stack(land) if land else np.zeros((0,50,50),bool);snow=np.stack(snow) if snow else np.zeros((0,50,50),bool)
 n=land.sum(axis=0);np.savez_compressed(path,dates=np.array(dates),land=land,snow=snow,mapped=masks[r.site_id])
 rec=dict(site_id=r.site_id,year=int(r.year),month=int(r.month),scenes=len(features),read_errors=sum(x['status']=='error' for x in records),observed_dates=len(dates),mapped_pixels=int(masks[r.site_id].sum()),mapped_once_pixels=int(((n>=1)&masks[r.site_id]).sum()),mapped_twice_pixels=int(((n>=2)&masks[r.site_id]).sum()),array_file='arrays/'+path.name,array_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),scene_records=records);meta.write_text(json.dumps(rec),encoding='utf-8');return rec
rows=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 for future in as_completed([pool.submit(run,r) for r in s.itertuples()]):
  r=future.result();rows.append({k:v for k,v in r.items() if k!='scene_records'});print(f'{len(rows)}/{len(s)} {r["site_id"]} {r["year"]}-{r["month"]}: mapped twice {r["mapped_twice_pixels"]}, errors {r["read_errors"]}',flush=True)
a=pd.DataFrame(rows).sort_values(['site_id','year','month']);a.to_csv(OUT/'monthly_mapped_support.csv',index=False);pairs=[]
for (site,month),q in a.groupby(['site_id','month']):
 for l,r in itertools.combinations(list(q.itertuples()),2):
  if l.read_errors or r.read_errors or not l.scenes or not r.scenes:continue
  with np.load(OUT/l.array_file) as x,np.load(OUT/r.array_file) as y:
   common=(x['land'].sum(axis=0)>=2)&(y['land'].sum(axis=0)>=2)&x['mapped'];assert np.array_equal(x['mapped'],y['mapped'])
  pairs.append(dict(site_id=site,month=month,first_year=l.year,last_year=r.year,mapped_common_twice_pixels=int(common.sum())))
pd.DataFrame(pairs).to_csv(OUT/'same_month_pair_support.csv',index=False);print('COMPLETE',flush=True)
