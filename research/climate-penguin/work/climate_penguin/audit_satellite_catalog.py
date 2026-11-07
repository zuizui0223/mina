"""Bounded January STAC coverage screen, not a usable-image or absence test."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, time, hashlib
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/climate_penguin'
CACHE = ROOT / 'work/climate_penguin/stac'
CACHE.mkdir(parents=True, exist_ok=True)
ENDPOINT = 'https://earth-search.aws.element84.com/v1/search'
macro = pd.read_csv(ROOT / 'outputs/ice_asymmetry/osi_1991_2020_macro_cohort.csv')
sites = macro[['site_id','latitude','longitude']].copy()
sites['cohort'] = 'macro_40'
p = pd.read_csv(OUT / 'phenology_observed_cohort.csv')
p = p[['cam','lat','long']].drop_duplicates().rename(columns={'cam':'site_id','lat':'latitude','long':'longitude'})
p['cohort'] = 'phenology_coordinate_group'
sites = pd.concat([sites,p], ignore_index=True)
assert not sites[['latitude','longitude']].isna().any().any()
sites.to_csv(OUT / 'satellite_screen_locations.csv', index=False)

def query(arg):
    site, year = arg
    # Small search envelope around a known point; this is not a colony boundary.
    lon, lat = float(site['longitude']), float(site['latitude'])
    params = {'collections':'sentinel-2-l2a','bbox':f'{lon-.02},{lat-.01},{lon+.02},{lat+.01}',
              'datetime':f'{year}-01-01T00:00:00Z/{year}-01-31T23:59:59Z','limit':100}
    key = hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest()[:20]
    path = CACHE / (key+'.json')
    row = dict(site, year=year, month=1, collection='sentinel-2-l2a', endpoint=ENDPOINT)
    try:
        if path.exists():
            j=json.loads(path.read_text())
        else:
            for attempt in range(3):
                r=requests.get(ENDPOINT,params=params,timeout=45)
                if r.status_code not in (429,500,502,503,504): break
                time.sleep(attempt+1)
            r.raise_for_status(); j=r.json()
            path.write_text(json.dumps(j),encoding='utf-8')
        fs=j.get('features',[])
        clouds=[f['properties'].get('eo:cloud_cover') for f in fs]
        clouds=[c for c in clouds if c is not None]
        row.update(status='ok',number_matched=j.get('numberMatched'),returned=len(fs),
                   paginated=len(fs)<j.get('numberMatched',len(fs)),
                   min_scene_cloud=min(clouds) if clouds else None,
                   cached_response=str(path.relative_to(ROOT)).replace('\\','/'))
    except Exception as e:
        row.update(status='error',error=str(e))
    return row

tasks=[(s,y) for s in sites.to_dict('records') for y in (2016,2019,2022,2024)]
with ThreadPoolExecutor(max_workers=6) as pool:
    rows=list(pool.map(query,tasks))
d=pd.DataFrame(rows)
d.to_csv(OUT/'satellite_january_catalog_screen.csv',index=False)
d['has_catalog_scene']=d['number_matched'].fillna(0).gt(0)
summary=d.groupby(['cohort','year']).agg(queries=('site_id','size'),successful_queries=('status',lambda x:(x=='ok').sum()),with_scene=('has_catalog_scene','sum'),pages_incomplete=('paginated','sum')).reset_index()
summary.to_csv(OUT/'satellite_january_catalog_summary.csv',index=False)
print(summary.to_string(index=False))
print('Errors:',int((d.status!='ok').sum()),flush=True)
