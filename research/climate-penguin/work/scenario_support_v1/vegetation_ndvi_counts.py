"""Descriptive same-pixel NDVI/count cochange; overlapping pairs are not replicates."""
from pathlib import Path
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/vegetation_annual_ndvi_v1'
p=pd.read_csv(OUT/'same_pixel_changes.csv');c=pd.read_csv(ROOT/'outputs/vegetation_annual_support_v1/dated_count_alignment.csv');rows=[]
for offset in [0,1]:
 a=p.copy();a['start_season']=a.first_year-offset;a['end_season']=a.last_year-offset
 for phase in ['start','end']:
  q=c[['site_id','species_id','season','count','vantage','month','year','date']].rename(columns={k:phase+'_'+k for k in ['season','count','vantage','month','year','date']})
  a=a.merge(q,on=['site_id',phase+'_season'],how='inner',validate='many_to_many')
  if phase=='start':a=a.rename(columns={'species_id':'start_species'})
 a=a[a.start_species==a.species_id].copy();a['january_offset']=offset;a['same_method']=a.start_vantage.eq(a.end_vantage)&a.start_vantage.notna()&a.end_vantage.notna()
 a['year_gap']=a.last_year-a.first_year
 a['annual_log1p_count_change']=(np.log1p(a.end_count)-np.log1p(a.start_count))/a.year_gap
 a['annual_ndvi_change']=a.median_pixel_ndvi_change/a.year_gap
 a['both_count_months_known']=a.start_month.notna()&a.end_month.notna()
 a['interpretation']='prior_January_to_count' if offset==0 else 'same_breeding_season_January_may_follow_count'
 assert not a.duplicated(['site_id','species_id','start_season','end_season']).any()
 rows.append(a)
j=pd.concat(rows,ignore_index=True);j.to_csv(OUT/'ndvi_count_pairs.csv',index=False)
summary=[]
for (offset,sp),g in j.groupby(['january_offset','species_id']):
 for cutoff in [1,100]:
  a=g[g.same_method&(g.common_pixels>=cutoff)].copy()
  r=a.annual_ndvi_change.corr(a.annual_log1p_count_change) if len(a)>=3 and a.site_id.nunique()>=3 else np.nan
  summary.append(dict(january_offset=offset,species_id=sp,minimum_common_pixels=cutoff,pairs=len(a),sites=a.site_id.nunique(),pearson_r_descriptive=r,rank_r_descriptive=a.annual_ndvi_change.rank().corr(a.annual_log1p_count_change.rank()) if np.isfinite(r) else np.nan,status='descriptive_overlapping_pairs_no_p_value' if np.isfinite(r) else 'insufficient_independent_site_support'))
s=pd.DataFrame(summary);s.to_csv(OUT/'ndvi_count_correlations.csv',index=False);print(s.to_string(index=False))
