"""Compare one-date/two-date support without changing the adopted criterion."""
from pathlib import Path
import itertools,json,hashlib
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/vegetation_expansion_pixels_v1';a=pd.read_csv(OUT/'monthly_mapped_support.csv');rows=[]
for r in a.itertuples():
 f=OUT/r.array_file;assert hashlib.sha256(f.read_bytes()).hexdigest()==r.array_sha256
 with np.load(f) as z:
  assert len(z['dates'])==len(set(z['dates']))==r.observed_dates
  n=z['land'].sum(axis=0);assert ((n>=1)&z['mapped']).sum()==r.mapped_once_pixels;assert ((n>=2)&z['mapped']).sum()==r.mapped_twice_pixels
for (site,month),g in a.groupby(['site_id','month']):
 for l,r in itertools.combinations(list(g.itertuples()),2):
  if l.read_errors or r.read_errors or not l.scenes or not r.scenes:continue
  with np.load(OUT/l.array_file) as x,np.load(OUT/r.array_file) as y:
   for minimum in [1,2]:
    common=(x['land'].sum(axis=0)>=minimum)&(y['land'].sum(axis=0)>=minimum)&x['mapped']
    rows.append(dict(site_id=site,month=month,first_year=l.year,last_year=r.year,minimum_dates=minimum,mapped_common_pixels=int(common.sum())))
b=pd.DataFrame(rows);b.to_csv(OUT/'one_two_date_comparison.csv',index=False)
checks=dict(monthly_pixel_checks=len(a),monthly_scene_reads=int(a.scenes.sum()),read_errors=int(a.read_errors.sum()),pairs_one_date_any=int(((b.minimum_dates==1)&(b.mapped_common_pixels>0)).sum()),pairs_one_date_100=int(((b.minimum_dates==1)&(b.mapped_common_pixels>=100)).sum()),pairs_two_dates_any=int(((b.minimum_dates==2)&(b.mapped_common_pixels>0)).sum()),plant_change_estimated=False)
(OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks);print(b[(b.minimum_dates==1)&(b.mapped_common_pixels>0)].to_string(index=False))
