from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,calendar,hashlib,zipfile
import pandas as pd,requests
ROOT=Path('research/climate-penguin');OUT=ROOT/'outputs/vegetation_expansion_pixels_v1';CACHE=OUT/'fallback_catalog';CACHE.mkdir(exist_ok=True)
a=pd.read_csv(ROOT/'outputs/vegetation_expansion_v1/catalog_support.csv');a=a[a.year.eq(2018)&a.scenes.eq(0)]
def fetch(t):
 r,collection=t;path=CACHE/f'{collection}_{r.site_id}_{r.year}_{r.month:02}.json';rec=dict(site_id=r.site_id,year=r.year,month=r.month,collection=collection)
 try:
  body={'collections':[collection],'intersects':{'type':'Point','coordinates':[r.longitude,r.latitude]},'datetime':f'{r.year}-{r.month:02}-01T00:00:00Z/{r.year}-{r.month:02}-{calendar.monthrange(r.year,r.month)[1]}T23:59:59Z','limit':100};url='https://earth-search.aws.element84.com/v1/search';features=[];pages=0;method='POST'
  while url:
   res=requests.post(url,json=body,timeout=30) if method=='POST' else requests.get(url,timeout=30);res.raise_for_status();d=res.json();features.extend(d.get('features',[]));pages+=1
   nxt=next((l for l in d.get('links',[]) if l.get('rel')=='next'),None)
   if not nxt:break
   if pages>20:raise ValueError('pagination incomplete')
   url=nxt['href'];method=nxt.get('method','GET');body=nxt.get('body',{})
  assert len({f['id'] for f in features})==len(features)
  saved=dict(query=rec,features=features,retrieved_utc=pd.Timestamp.now(tz='UTC').isoformat());path.write_text(json.dumps(saved),encoding='utf-8')
  rec.update(status='complete',scenes=len(features),dates=len({f['properties']['datetime'][:10] for f in features}),cached_file='fallback_catalog/'+path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 except Exception as e:rec.update(status='error',error=str(e))
 return rec
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,[(r,col) for r in a.itertuples() for col in ['sentinel-2-c1-l2a','landsat-c2-l2']]))
s=pd.DataFrame(rows);s.to_csv(OUT/'fallback_catalog_support.csv',index=False)
with zipfile.ZipFile(OUT/'fallback_sources.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for f in CACHE.glob('*.json'):z.write(f,'fallback_catalog/'+f.name)
print(s.groupby('collection').agg(queries=('site_id','size'),scenes=('scenes','sum'),positive=('scenes',lambda x:(x>0).sum())).to_string())
