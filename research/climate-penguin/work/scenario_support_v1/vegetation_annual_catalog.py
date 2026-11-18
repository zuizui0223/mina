"""Acquire January image candidates at observed count years; not usable vegetation."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib,time,zipfile
import pandas as pd
import requests
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/vegetation_annual_support_v1';OUT.mkdir(exist_ok=True)
CACHE=OUT/'catalog';CACHE.mkdir(exist_ok=True)
archive=OUT/'catalog_sources.zip'
if archive.exists():
 with zipfile.ZipFile(archive) as z:
  for name in z.namelist():
   assert name.startswith('catalog/') and '..' not in Path(name).parts
   target=OUT/name
   if not target.exists():target.write_bytes(z.read(name))
cpath=ROOT/'outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv';lpath=ROOT/'outputs/climate_penguin/daily_ice_locations.csv'
c=pd.read_csv(cpath);loc=pd.read_csv(lpath);loc=loc[loc.cohort=='macro_40']
c=c[c.site_id.isin(loc.site_id)&c.season.between(2017,2023)].copy()
rows=[]
for r in c.itertuples():
 for offset in [0,1]:rows.append(dict(site_id=r.site_id,species_id=r.species_id,season=r.season,count=r.count,method=r.method,image_year=int(r.season+offset),calendar_offset=offset,calendar_alignment_verified=False))
candidates=pd.DataFrame(rows);candidates.to_csv(OUT/'count_image_year_candidates.csv',index=False)
tasks=candidates[['site_id','image_year']].drop_duplicates().merge(loc[['site_id','latitude','longitude']],validate='many_to_one')
endpoint='https://earth-search.aws.element84.com/v1/search'
def fetch(r):
 path=CACHE/f'{r.site_id}_{r.image_year}.json';rec=dict(site_id=r.site_id,image_year=int(r.image_year))
 try:
  if path.exists():saved=json.loads(path.read_text());features=saved['features']
  else:
   body={'collections':['sentinel-2-l2a'],'intersects':{'type':'Point','coordinates':[r.longitude,r.latitude]},'datetime':f'{r.image_year}-01-01T00:00:00Z/{r.image_year}-01-31T23:59:59Z','limit':100}
   features=[];url=endpoint;pages=0;method='POST'
   while url:
    response=requests.post(url,json=body,timeout=45) if method=='POST' else requests.get(url,timeout=45)
    response.raise_for_status();data=response.json();features.extend(data.get('features',[]));pages+=1
    nxt=next((x for x in data.get('links',[]) if x.get('rel')=='next'),None)
    if not nxt:break
    if pages>=20:raise RuntimeError('pagination limit; incomplete not accepted')
    url=nxt['href'];method=nxt.get('method','GET');body=nxt.get('body',{})
   saved={'endpoint':endpoint,'query_point':[r.longitude,r.latitude],'image_year':int(r.image_year),'features':features,'retrieved_utc':pd.Timestamp.now(tz='UTC').isoformat(),'complete':True}
   path.write_text(json.dumps(saved),encoding='utf-8')
  assert saved['complete']
  ids=[f['id'] for f in features];assert len(ids)==len(set(ids))
  dates=[f['properties']['datetime'][:10] for f in features]
  assert all(x.startswith(str(r.image_year)+'-01') for x in dates)
  rec.update(status='catalog_complete',scenes=len(features),dates=len(set(dates)),scenes_with_red_nir_scl=sum(all(k in f.get('assets',{}) for k in ['red','nir','scl']) for f in features),cached_file='catalog/'+path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 except Exception as e:rec.update(status='error',error=str(e))
 return rec
results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 futures=[pool.submit(fetch,r) for r in tasks.itertuples()]
 for future in as_completed(futures):
  results.append(future.result())
  if len(results)%20==0:print(f'{len(results)}/{len(tasks)} catalog queries finished',flush=True)
s=pd.DataFrame(results).sort_values(['site_id','image_year']);s.to_csv(OUT/'catalog_support.csv',index=False)
candidates.merge(s,on=['site_id','image_year'],validate='many_to_one').to_csv(OUT/'count_catalog_join.csv',index=False)
receipt={'queries':len(tasks),'completed':int(s.status.eq('catalog_complete').sum()),'errors':int(s.status.eq('error').sum()),'sites':tasks.site_id.nunique(),'actual_count_rows':len(c),'calendar_alignment_verified':False,'local_clear_pixels_verified':False,'vegetation_classified':False,'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [cpath,lpath]}}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt,flush=True)
