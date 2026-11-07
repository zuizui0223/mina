from pathlib import Path
import pandas as pd
import requests, hashlib, json
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'outputs/climate_penguin'
raw=ROOT/'work/climate_penguin/cmip6';raw.mkdir(exist_ok=True)
url='https://storage.googleapis.com/cmip6/cmip6-zarr-consolidated-stores.csv'
p=raw/'catalog.csv'
if not p.exists():
    with requests.get(url,stream=True,timeout=60) as r:
        r.raise_for_status()
        with p.open('wb') as f:
            for b in r.iter_content(1024*1024): f.write(b)
selected=[]; total=0
for c in pd.read_csv(p,chunksize=50000):
    total+=len(c)
    selected.append(c[c.variable_id.isin(['siconc','siu','siv','tas']) & c.experiment_id.isin(['historical','ssp126','ssp245','ssp585'])])
d=pd.concat(selected)
d.to_csv(out/'cmip6_candidate_stores.csv',index=False)
s=d.groupby(['variable_id','table_id','experiment_id']).agg(stores=('zstore','size'),models=('source_id','nunique')).reset_index()
s.to_csv(out/'cmip6_variable_availability.csv',index=False)
# Presence of all experiments in a model/member/grid/table is only a catalog gate.
keys=['source_id','member_id','grid_label','table_id','variable_id']
matched=d.groupby(keys).experiment_id.agg(lambda x: '|'.join(sorted(set(x)))).reset_index()
matched=matched[matched.experiment_id.str.split('|').str.len()==4]
matched.to_csv(out/'cmip6_four_experiment_candidates.csv',index=False)
(out/'cmip6_catalog_manifest.json').write_text(json.dumps({'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'total_rows':total,'selected_rows':len(d),'warning':'Catalog presence only; arrays, dates, Southern Hemisphere coverage and calendars not yet validated'},indent=2))
print(s.to_string(index=False));print('Four-experiment combinations:',len(matched))
