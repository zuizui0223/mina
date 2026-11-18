"""Join exact deposited coordinates to their extracted environments, not MAPPPD sites."""
from pathlib import Path
import json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
p=pd.read_csv(OUT/'phenology_observed_cohort.csv')
loc=pd.read_csv(OUT/'daily_ice_locations.csv')
loc=loc[loc.cohort=='phenology_coordinate_group'].rename(columns={'site_id':'cam','latitude':'lat','longitude':'long'})
assert not loc.duplicated(['cam','lat','long']).any()
p=p.merge(loc[['cam','lat','long','location_id']],on=['cam','lat','long'],how='left',validate='many_to_one')
assert len(p)==288 and p.location_id.notna().all()
e=pd.read_csv(OUT/'daily_ice_complete_season_features.csv')
e=e[e.complete_122_days].copy()
cols=['sic_mean_month8','sic_mean_month9','sic_mean_month10','sic_mean_month11','mean_interpolated_fraction','mean_spill_corrected_fraction']
for inner,name in [(0,'near'),(100,'far')]:
    t=e[e.inner_km==inner][['location_id','year']+cols].rename(columns={'year':'season_start_year',**{c:name+'_'+c for c in cols}})
    p=p.merge(t,on=['location_id','season_start_year'],how='left',validate='many_to_one')
p['environment_join_complete']=p[[f'{b}_sic_mean_month{m}' for b in ['near','far'] for m in [8,9,10,11]]].notna().all(axis=1)
p['calendar_origin_verified']=False
p['mapppd_site_join_accepted']=False
p.to_csv(OUT/'behavior_environment_coordinate_join.csv',index=False)
summary=[]
for species,g in p.groupby('species'):
    a=g[g.environment_join_complete]
    summary.append(dict(species=species,all_rows=len(g),matched_rows=len(a),geographic_codes=a.cam.nunique(),code_seasons=len(a[['cam','season_start_year']].drop_duplicates()),camera_codes=a.colname3.nunique(),start_year=a.season_start_year.min(),end_year=a.season_start_year.max()))
pd.DataFrame(summary).to_csv(OUT/'behavior_environment_join_support.csv',index=False)
# Env-only conditional correlations. Camera records are first given equal total
# weight per geographic code/species/season via a descriptive mean aggregation.
diag=[]
for species,g in p[p.environment_join_complete].groupby('species'):
    cols2=['near_sic_mean_month9','far_sic_mean_month9','spgmedian']
    a=g.groupby(['cam','season_start_year'])[cols2].mean().reset_index()
    x=pd.get_dummies(a[['cam','season_start_year']].astype(str),drop_first=True,dtype=float)
    x=np.column_stack([np.ones(len(a)),x.to_numpy()])
    v=a[cols2].to_numpy();res=v-x@np.linalg.lstsq(x,v,rcond=None)[0]
    rank=int(np.linalg.matrix_rank(x));corr=np.corrcoef(res,rowvar=False) if len(a)-rank>2 else np.full((3,3),np.nan)
    diag.append(dict(species=species,code_seasons=len(a),residual_df=len(a)-rank,near_far_raw_r=a[cols2[0]].corr(a[cols2[1]]),near_far_code_year_residual_r=corr[0,1],near_temperature_residual_r=corr[0,2],far_temperature_residual_r=corr[1,2],note='Environmental separability diagnostic only; no settlement fit, no independence claim'))
pd.DataFrame(diag).to_csv(OUT/'behavior_environment_separability.csv',index=False)
(OUT/'behavior_environment_join_checks.json').write_text(json.dumps({'source_rows':288,'retained_rows':len(p),'all_coordinates_matched':bool(p.location_id.notna().all()),'complete_environment_rows':int(p.environment_join_complete.sum()),'unverified_calendar_origin':True,'uses_count_site_join':False,'outcome_model_fitted':False},indent=2))
print(pd.DataFrame(summary).to_string(index=False));print(pd.DataFrame(diag).to_string(index=False))
