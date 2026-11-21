"""Audit frozen recurrent-ROI cohort WITHOUT opening new reflectance or isotope outcomes."""
from pathlib import Path
import hashlib,json
import pandas as pd
p=Path(__file__).resolve().parent
source=p.parent/'diet_salinity_source_20261117/recurrent_roi_results'
d=pd.read_csv(source/'recurrent_roi_native_qa.csv')
assert not d.duplicated(['site_id','season']).any()
rows=[]
for threshold in [1,2]:
 v=d[d.qa_valid_native_pixels.ge(threshold)&d.error.isna()].copy()
 v.to_csv(p/f'candidate_cohort_min{threshold}_pixels.csv',index=False,lineterminator='\n')
 for region,g in v.groupby('region'):
  rows.append(dict(min_pixels=threshold,region=region,sites=g.site_id.nunique(),site_seasons=len(g),years=g.season.nunique()))
 counts=dict(site_seasons=len(v),sites=v.site_id.nunique(),regions=v.region.nunique(),years=v.season.nunique(),sites_with_two_seasons=int((v.groupby('site_id').season.nunique()>=2).sum()))
 (p/f'counts_min{threshold}_pixels.json').write_text(json.dumps(counts,indent=2)+'\n',encoding='utf-8',newline='\n')
pd.DataFrame(rows).to_csv(p/'regional_support.csv',index=False,lineterminator='\n')
receipt={'qa_rows':len(d),'qa_zero_rows':int(d.qa_valid_native_pixels.eq(0).sum()),'qa_error_rows':int(d.error.notna().sum()),'new_reflectance_opened':False,'new_isotope_estimated':False,'new_ecological_test_run':False,'sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in ['recurrent_roi_native_qa.csv','fixed_recurrent_guano_roi.csv','fixed_scene_selection.csv']}}
(p/'audit_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
assert len(d)==432 and len(d[d.qa_valid_native_pixels.ge(1)&d.error.isna()])==324
assert len(d[d.qa_valid_native_pixels.ge(2)&d.error.isna()])==277
print(json.dumps(receipt,indent=2))
