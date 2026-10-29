"""Exploratory annual breeding-count changes, distinct from settlement behavior."""
from pathlib import Path
import numpy as np,pandas as pd,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
raw=pd.read_csv(ROOT/'work/data_audit/mapppdr/penguin_obs.csv')
known=raw[raw.month.notna()].copy()
expected=known.year-np.where(known.month<=6,1,0)
assert known.season.eq(expected).all()
dates=pd.to_datetime(raw.date,errors='coerce');ok=dates.notna()
assert raw.loc[ok,'year'].eq(dates[ok].dt.year).all()
sites=pd.read_csv(OUT/'daily_ice_locations.csv');sites=sites[sites.cohort=='macro_40']
counts=pd.read_csv(ROOT/'outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv')
counts=counts[(counts.species_id=='ADPE')&counts.site_id.isin(sites.site_id)&counts.season.between(2011,2020)].copy()
evidence=raw[raw.type=='nests'][['site_id','species_id','season','count','month','date','citekey']]
j=counts[['site_id','species_id','season','count']].merge(evidence,on=['site_id','species_id','season','count'],how='left',validate='one_to_many')
j['month_known']=j.month.notna();j['after_september']=j.month.isin([10,11,12,1,2,3])
q=j.groupby(['site_id','species_id','season']).agg(source_records=('citekey','size'),any_month_known=('month_known','any'),all_sources_month_known=('month_known','all'),all_sources_after_september=('after_september','all')).reset_index()
counts=counts.merge(q,on=['site_id','species_id','season'],validate='one_to_one').merge(sites[['site_id','location_id']],on='site_id',validate='many_to_one')
sic=pd.read_csv(OUT/'daily_ice_complete_season_features.csv')
for inner,name in [(0,'near'),(100,'far')]:
    a=sic[(sic.inner_km==inner)&sic.complete_122_days][['location_id','year','sic_mean_month9']].rename(columns={'year':'season','sic_mean_month9':name+'_sic'})
    counts=counts.merge(a,on=['location_id','season'],how='left',validate='many_to_one')
o=pd.read_csv(OUT/'ocean_monthly_2011_2021.csv');o=o[o.month==9].copy()
vars=['surface_salinity','surface_potential_temperature_c','mixed_layer_depth_m']
o.loc[~o.grid_within_25km,vars]=np.nan
counts=counts.merge(o[['location_id','year']+vars].rename(columns={'year':'season'}),on=['location_id','season'],how='left',validate='many_to_one')
flow=pd.read_csv(OUT/'return_drift_monthly_support.csv');flow=flow[flow.month==9].copy();flow.loc[~flow.screen_pass,['east_km_day','north_km_day']]=np.nan
counts=counts.merge(flow[['location_id','year','east_km_day','north_km_day']].rename(columns={'year':'season'}),on=['location_id','season'],how='left',validate='many_to_one')
counts.to_csv(OUT/'count_environment_site_seasons.csv',index=False)
intervals=pd.read_csv(ROOT/'outputs/comparison_audit/mapppd_intervals.csv')
i=intervals[(intervals.species_id=='ADPE')&intervals.site_id.isin(sites.site_id)&intervals.start.between(2011,2019)&intervals.end.between(2012,2020)&intervals.same_known_method&(intervals.gap==1)&(intervals.n_start>0)&(intervals.n_end>0)].copy()
variables=['near_sic','far_sic']+vars+['east_km_day','north_km_day']
for phase in ['start','end']:
    a=counts[['site_id','season','all_sources_after_september']+variables].rename(columns={'season':phase,**{x:phase+'_'+x for x in ['all_sources_after_september']+variables}})
    i=i.merge(a,on=['site_id',phase],how='left',validate='many_to_one')
i['log_growth']=np.log(i.n_end/i.n_start)
i['timing_supported']=i.start_all_sources_after_september&i.end_all_sources_after_september
i.to_csv(OUT/'count_environment_annual_intervals.csv',index=False)
results=[]
for scope,selection in [('all',i),('without_victoria_land',i[i.region!='Victoria Land']),('month_supported_after_september',i[i.timing_supported])]:
    for v in variables:
        for exposure in ['end_level','annual_change']:
            a=selection.copy();a['x']=a['end_'+v] if exposure=='end_level' else a['end_'+v]-a['start_'+v]
            a=a.dropna(subset=['x','log_growth'])
            w=a[['x','log_growth']]-a.groupby('site_id')[['x','log_growth']].transform('mean')
            repeated=a.groupby('site_id').size().loc[lambda z:z>=2]
            results.append(dict(scope=scope,predictor=v,exposure=exposure,intervals=len(a),sites=a.site_id.nunique(),regions=a.region.nunique(),pearson_r=a.x.corr(a.log_growth),within_site_r=w.x.corr(w.log_growth),within_sites_with_repeated_intervals=len(repeated),within_intervals=int(repeated.sum()),interpretation='correlation_not_demographic_mechanism'))
r=pd.DataFrame(results);r.to_csv(OUT/'count_environment_correlations.csv',index=False)
check=dict(raw_records=len(raw),records_with_month=len(known),records_with_date=int(ok.sum()),known_month_season_rule_mismatches=0,selected_count_rows=len(counts),selected_sites=counts.site_id.nunique(),selected_regions=counts.region.nunique(),annual_intervals=len(i),interval_sites=i.site_id.nunique(),interval_regions=i.region.nunique(),intervals_after_september_supported=int(i.timing_supported.sum()),excluded_ocean_distance_km=25)
(OUT/'count_environment_checks.json').write_text(json.dumps(check,indent=2));print(json.dumps(check));print(r[(r.scope=='all')&(r.exposure=='end_level')].to_string(index=False))
