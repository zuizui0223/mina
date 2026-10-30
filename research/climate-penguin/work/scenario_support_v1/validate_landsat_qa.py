"""Validate Landsat QA arrays and compare 2018/2019 support by window/tier."""
from pathlib import Path
import json,hashlib
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/landsat_vegetation_support_v1';manifest=pd.read_csv(OUT/'read_manifest.csv');rows=[];tiers=[]
for r in manifest.itertuples():
 path=OUT/r.array_file;assert hashlib.sha256(path.read_bytes()).hexdigest()==r.array_sha256
 with np.load(path) as a:
  assert len(a['dates'])==len(a['qa'])==len(a['scene_ids'])==len(a['tiers'])
  tiers.extend(a['tiers'].tolist())
for site,g in manifest.groupby('site_id'):
 assert set(g.year)=={2018,2019}
 for period in ['01','02','01_02']:
  for mode in ['all_tiers','T1_only']:
   for minimum in [1,2]:
    masks=[];daycounts=[]
    for r in g.sort_values('year').itertuples():
     with np.load(OUT/r.array_file) as a:
      selected=np.array([period=='01_02' or d[5:7]==period for d in a['dates']],dtype=bool)
      if mode=='T1_only':selected&=a['tiers']=='T1'
      dates=a['dates'][selected];qa=a['qa'][selected];days=sorted(set(dates));accepted=np.ones(qa.shape,bool)
      for bit in [0,1,2,3,4,5,7]:accepted&=((qa>>bit)&1)==0
      daily=np.stack([accepted[dates==d].any(axis=0) for d in days]) if days else np.zeros((0,34,34),bool)
      masks.append((daily.sum(axis=0)>=minimum)&a['mapped']);daycounts.append(len(days))
    common=masks[0]&masks[1];rows.append(dict(site_id=site,window=period,tier_mode=mode,minimum_dates=minimum,days_2018=daycounts[0],days_2019=daycounts[1],mapped_pixels_2018=int(masks[0].sum()),mapped_pixels_2019=int(masks[1].sum()),common_mapped_pixels=int(common.sum())))
s=pd.DataFrame(rows);s.to_csv(OUT/'paired_qa_support.csv',index=False)
check=dict(site_years=len(manifest),sites=manifest.site_id.nunique(),catalog_scene_references=int(manifest.catalog_scenes.sum()),read_errors=int(manifest.errors.sum()),tier_counts=pd.Series(tiers).value_counts().to_dict(),paired_comparisons=len(s),qa_array_hash_checks=len(manifest),qa_only_not_reflectance=True,georegistration_validated=False)
(OUT/'validation.json').write_text(json.dumps(check,indent=2)+'\n');print(check);print(s[(s.tier_mode=='all_tiers')&(s.minimum_dates==2)].to_string(index=False))
