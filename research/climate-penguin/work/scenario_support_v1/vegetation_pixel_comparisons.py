"""Reproduce cross-year common-pixel support and dated-count join."""
from pathlib import Path
import itertools,hashlib,json
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[2];p=ROOT/'outputs/vegetation_annual_pixels_v1';s=pd.read_csv(p/'local_support.csv');rows=[]
for r in s.itertuples():
 f=p/r.pixel_file;assert hashlib.sha256(f.read_bytes()).hexdigest()==r.pixel_sha256
 with np.load(f) as a:
  assert len(a['dates'])==len(set(a['dates']))==r.observed_dates
  assert int((a['land'].sum(axis=0)>=2).sum())==r.land_twice_pixels
  assert not (a['land']&a['snow']).any() and not (a['land']&a['water']).any()
for site,g in s.groupby('site_id'):
 for l,r in itertools.combinations(list(g.itertuples()),2):
  if l.read_errors or r.read_errors or not l.scenes or not r.scenes:continue
  with np.load(p/l.pixel_file) as a,np.load(p/r.pixel_file) as b:count=int(((a['land'].sum(axis=0)>=2)&(b['land'].sum(axis=0)>=2)).sum())
  rows.append(dict(site_id=site,first_image_year=l.image_year,last_image_year=r.image_year,common_twice_pixels=count))
pairs=pd.DataFrame(rows);pairs.to_csv(p/'pairwise_common_support.csv',index=False)
c=pd.read_csv(ROOT/'outputs/vegetation_annual_support_v1/dated_count_alignment.csv')
a=c.merge(s.rename(columns={'image_year':'same_breeding_season_january_year'}),on=['site_id','same_breeding_season_january_year'],how='left',validate='many_to_one');assert len(a)==117
a.to_csv(p/'same_season_count_support.csv',index=False)
expected=json.loads((p/'validation.json').read_text())
assert expected['site_year_pixel_checks']==len(s)
assert expected['scenes']==s.scenes.sum()
assert expected['failed_scene_reads']==s.read_errors.sum()
for cutoff,label in [(1,'any'),(100,'100')]:
 sel=pairs[pairs.common_twice_pixels>=cutoff]
 key='pairs_with_any_common_twice_land' if cutoff==1 else 'pairs_with_100_common_twice_land'
 assert expected[key]==len(sel)
assert expected['sites_with_any_pair_common_twice_land']==pairs.loc[pairs.common_twice_pixels>0,'site_id'].nunique()
assert expected['sites_with_100_pair_common_twice_land']==pairs.loc[pairs.common_twice_pixels>=100,'site_id'].nunique()
print('Verified all 159 pixel products and reproduced all year-pair and dated-count joins.')
