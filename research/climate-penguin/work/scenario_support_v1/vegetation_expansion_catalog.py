"""Acquire Jan/Feb catalog support for outcome-blind mapped-vegetation candidates."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,calendar,hashlib,zipfile
import pandas as pd,requests
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/vegetation_expansion_v1';CACHE=OUT/'catalog';CACHE.mkdir(exist_ok=True)
c=pd.read_csv(OUT/'candidate_count_years.csv');locations=c[['site_id','latitude','longitude']].drop_duplicates();assert not locations.site_id.duplicated().any()
years=c[['site_id','same_season_january_year']].drop_duplicates().merge(locations,validate='many_to_one');tasks=[]
for r in years.itertuples():
 for month in [1,2]:tasks.append(dict(site_id=r.site_id,year=int(r.same_season_january_year),month=month,latitude=r.latitude,longitude=r.longitude))
endpoint='https://earth-search.aws.element84.com/v1/search'
def fetch(r):
 path=CACHE/f'{r["site_id"]}_{r["year"]}_{r["month"]:02}.json';rec=dict(r)
 try:
  if path.exists():saved=json.loads(path.read_text());features=saved['features']
  else:
   y,m=r['year'],r['month'];end=calendar.monthrange(y,m)[1];body={'collections':['sentinel-2-l2a'],'intersects':{'type':'Point','coordinates':[r['longitude'],r['latitude']]},'datetime':f'{y}-{m:02}-01T00:00:00Z/{y}-{m:02}-{end}T23:59:59Z','limit':100};url=endpoint;method='POST';features=[];pages=0
   while url:
    res=requests.post(url,json=body,timeout=30) if method=='POST' else requests.get(url,timeout=30);res.raise_for_status();data=res.json();features.extend(data.get('features',[]));pages+=1
    nxt=next((l for l in data.get('links',[]) if l.get('rel')=='next'),None)
    if not nxt:break
    if pages>20:raise ValueError('Incomplete pagination')
    url=nxt['href'];method=nxt.get('method','GET');body=nxt.get('body',{})
   saved={'features':features,'query':r,'endpoint':endpoint,'complete':True,'retrieved_utc':pd.Timestamp.now(tz='UTC').isoformat()};path.write_text(json.dumps(saved),encoding='utf-8')
  assert saved['complete'];ids=[f['id'] for f in features];assert len(ids)==len(set(ids));dates={f['properties']['datetime'][:10] for f in features}
  assert all(d.startswith(f'{r["year"]}-{r["month"]:02}') for d in dates)
  rec.update(status='complete',scenes=len(features),dates=len(dates),cached_file='catalog/'+path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 except Exception as e:rec.update(status='error',error=str(e))
 return rec
rows=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 for f in as_completed([pool.submit(fetch,r) for r in tasks]):rows.append(f.result())
s=pd.DataFrame(rows).sort_values(['site_id','year','month']);s.to_csv(OUT/'catalog_support.csv',index=False)
with zipfile.ZipFile(OUT/'catalog_sources.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for f in sorted(CACHE.glob('*.json')):z.write(f,'catalog/'+f.name)
(OUT/'.gitignore').write_text('catalog/\n');print(s.groupby(['year','month']).agg(queries=('site_id','size'),with_scenes=('scenes',lambda x:(x>0).sum()),scenes=('scenes','sum')).to_string());print('errors',int(s.status.eq('error').sum()),'queries',len(s))
