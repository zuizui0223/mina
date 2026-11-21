#!/usr/bin/env python3
"""Original 595 fixed colony CMIP6 physical-only delta × genuine counted nest support.
No future penguin count prediction, no 265-series regression, no MPA inference.
"""
import argparse,io,json,zipfile,hashlib
from pathlib import Path
import numpy as np
import pandas as pd

BLOB='source_root/outputs/cmip6_projection_v1/'

def zipped_csv(z,name):return pd.read_csv(io.BytesIO(z.read(name)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def weightmean(data,weight):
    return float(np.average(np.asarray(data,float),weights=np.asarray(weight,float)))

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--cmip6-zip',type=Path,required=True)
 p.add_argument('--observed-zip',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(a.cmip6_zip) as z:
  assert z.testzip() is None
  metadata=json.loads(z.read(BLOB+'manifest.json'))
  source_meta=json.loads(z.read('595_physical_extraction_validation.json'))
  cells=zipped_csv(z,BLOB+'coastal_grid_support.csv')
  models=zipped_csv(z,BLOB+'site_model_changes.csv')
  ensemble=zipped_csv(z,BLOB+'site_model_ensemble.csv')
 with zipfile.ZipFile(a.observed_zip) as z:
  assert z.testzip() is None
  real=zipped_csv(z,'source_observed_2456.csv')
  inventory=zipped_csv(z,'panantarctic_595_site_inventory.csv')
 assert metadata['status']=='complete' and metadata['n_stores_read']==27 and not metadata['failures']
 assert source_meta['status']=='PASS_PHYSICAL_ONLY_595_SELECTED_SOURCE'
 assert len(real)==2456 and inventory.site_id.nunique()==595
 assert (len(ensemble),len(models),len(cells))==(7140,21420,5355)
 assert models.complete_years.eq(20).all() and ensemble.n_models.eq(3).all()
 assert ensemble.site_id.nunique()==595 and models.site_id.nunique()==595
 assert not ensemble.duplicated(['variable_id','experiment_id','period','site_id']).any()
 assert not cells.duplicated(['source_id','variable_id','site_id']).any()
 obs=real.loc[real.season.between(2011,2020)].copy()
 count=obs.groupby(['site_id','species'],as_index=False).agg(median_nests=('observed_nest_count','median'),n_original_years=('season','nunique'))
 weights=count.groupby('site_id',as_index=False).agg(weight_observed_species_medians=('median_nests','sum'),n_recorded_species=('species','nunique'),n_site_species_survey_years=('n_original_years','sum'))
 weight_sum=weights.weight_observed_species_medians.sum()
 assert weights.site_id.nunique()==271 and len(count)==331 and abs(weight_sum-2848329.5)<1e-8
 # both original siconc and sos marine variables must be within model cell distance<=50km for all 3 original models
 ocean=cells[cells.variable_id.isin(['siconc','sos'])]
 assert ocean.groupby('site_id').size().eq(6).all()
 maximum=ocean.groupby('site_id').distance_km.max().rename('max_marine_model_cell_km')
 marine=maximum.le(50).rename('all3_both_marine_variables_within50')
 source=inventory[['site_id','source_region','polar_250km_fixed_grid_block','latitude','longitude']].merge(weights,on='site_id',how='left',validate='one_to_one')
 source['observed_2011_2020_any']=source.weight_observed_species_medians.notna()
 source=source.merge(maximum,on='site_id',validate='one_to_one').merge(marine,on='site_id',validate='one_to_one')
 assert len(source)==595 and source.source_region.nunique()==18
 observed=source.loc[source.observed_2011_2020_any]
 confirmed=observed.loc[observed.all3_both_marine_variables_within50]
 assert len(observed)==271 and len(confirmed)==158
 assert abs(confirmed.weight_observed_species_medians.sum()/weight_sum-0.8020989144689896)<1e-10
 source.to_csv(a.output/'source_595_site_observation_and_marine_distance.csv',index=False)
 count.to_csv(a.output/'source_331_actual_species_site_medians_2011_2020.csv',index=False)
 # do not force 595 unsurveyed sites to have zero weight; preserve NA
 analysis=ensemble.merge(source[['site_id','source_region','polar_250km_fixed_grid_block',
           'weight_observed_species_medians','observed_2011_2020_any',
           'all3_both_marine_variables_within50']],on='site_id',validate='many_to_one')
 analysis.to_csv(a.output/'full_595_3model_4scenario_source_physical_exposure.csv',index=False)
 summary=[];region=[];species=[];leave=[]
 for (ex,period),z in analysis.groupby(['experiment_id','period']):
  wide=z.pivot(index='site_id',columns='variable_id',values='change_mean')
  cats=source.set_index('site_id').join(wide,validate='one_to_one')
  for cohort,f in [('all_595_known_source_sites',cats),('actually_counted_271',cats.loc[cats.observed_2011_2020_any]),
                   ('counted_and_all3_ocean_50km_158',cats.loc[cats.observed_2011_2020_any & cats.all3_both_marine_variables_within50])]:
   w=f.weight_observed_species_medians.to_numpy(float)
   is_counted=int(np.isfinite(w).sum());wsum=float(np.nansum(w))
   row={'experiment_id':ex,'period':period,'cohort':cohort,'source_site_count':len(f),
        'real_counted_site_count':is_counted,
        'n_source_regions':f.source_region.nunique(),
        'source_site_count_pct_of_all_595':100*len(f)/595,
        'nested_observed_nest_median_weight_pct_of_271':100*wsum/weight_sum,
        'source_2011_2020_observed_median_nests_sum':wsum}
   for v in ('siconc','tas','sos'):
    row[v+'_site_equal_mean_change']=float(f[v].mean())
    row[v+'_source_nest_median_weighted_mean_change']=(weightmean(f.loc[f.weight_observed_species_medians.notna(),v],
         f.loc[f.weight_observed_species_medians.notna(),'weight_observed_species_medians']) if wsum>0 else None)
   row['not_a_climate_caused_nesting_forecast']=True
   summary.append(row)
  # species weighting - species-specific source denominator and geographic support
  for sp,g in count.groupby('species'):
   q=g.merge(cats[['siconc','tas','sos','all3_both_marine_variables_within50','source_region']],left_on='site_id',right_index=True,validate='many_to_one')
   for support,ss in [('all_marine_grid_distances',q),('marine_all3_within_50km',q[q.all3_both_marine_variables_within50])]:
    row={'experiment_id':ex,'period':period,'species':sp,'support':support,
         'n_real_source_colonies':len(ss),'total_observed_species_median_nests':float(ss.median_nests.sum()),
         'fraction_species_observed_median_nests':float(ss.median_nests.sum()/g.median_nests.sum())}
    for v in ('siconc','tas','sos'):
     row[v+'_nest_weighted_mean_change']=weightmean(ss[v],ss.median_nests)
     row[v+'_colony_equal_mean_change']=float(ss[v].mean())
    species.append(row)
  # Region source-weight share and original climate signal, without missing observations treated as 0
  actual=cats.loc[cats.observed_2011_2020_any]
  for reg,g in actual.groupby('source_region'):
   row={'experiment_id':ex,'period':period,'source_region':reg,'n_genuine_counted_sites':len(g),
       'observed_species_median_nest_share':float(g.weight_observed_species_medians.sum()/weight_sum)}
   for v in ('siconc','tas'):
    row[v+'_observed_species_median_nest_weighted']=weightmean(g[v],g.weight_observed_species_medians)
   region.append(row)
  # sensitivity: largest colonies and entire regions removed from EXACT counted cohort
  weightactual=actual.weight_observed_species_medians
  largest=weightactual.sort_values(ascending=False)
  for omit,subset in [('none',actual),('largest_source_site',actual.drop(index=largest.index[:1])),
                     ('five_largest_source_sites',actual.drop(index=largest.index[:5]))]:
   leave.append({'experiment_id':ex,'period':period,'omit_type':omit,
     'n_sites':len(subset),'source_nest_weight_fraction':subset.weight_observed_species_medians.sum()/weight_sum,
     'siconc_site_equal_mean':subset.siconc.mean(),
     'siconc_nest_weighted_mean':weightmean(subset.siconc,subset.weight_observed_species_medians)})
  for reg in sorted(actual.source_region.unique()):
   sub=actual[actual.source_region.ne(reg)]
   leave.append({'experiment_id':ex,'period':period,'omit_type':'region_'+reg,
     'n_sites':len(sub),'source_nest_weight_fraction':sub.weight_observed_species_medians.sum()/weight_sum,
     'siconc_site_equal_mean':sub.siconc.mean(),
     'siconc_nest_weighted_mean':weightmean(sub.siconc,sub.weight_observed_species_medians)})
 pd.DataFrame(summary).to_csv(a.output/'physical_595_all_vs_271_vs_158_nesting_weight_scenarios.csv',index=False)
 pd.DataFrame(species).to_csv(a.output/'physical_595_species_specific_nesting_weight_scenarios.csv',index=False)
 pd.DataFrame(region).to_csv(a.output/'physical_595_region_countweight_scenarios.csv',index=False)
 pd.DataFrame(leave).to_csv(a.output/'physical_595_max_colony_and_region_influence.csv',index=False)
 # independent one-pass aggregation by source site first before merging all four scenarios
 audit={'status':'PASS_595_CLIMATE_SOURCE_FULL_COLONIES_PHYSICAL_ONLY',
  'n_source_sites':595,'original_595_source_regions':18,
  'n_sites_with_true_2011_2020_nests':len(observed),
  'n_site_species_actual_medians':len(count),'n_original_2011_2020_nests_sum_proxy':float(weight_sum),
  'n_all3_marine_50km_source_sites_all_595':int(source.all3_both_marine_variables_within50.sum()),
  'n_counted_with_all3_marine_50km':len(confirmed),
  'fraction_all_counted_median_nests_supported_with_all3_marine_50km':float(confirmed.weight_observed_species_medians.sum()/weight_sum),
  'input_sha256':{'source_cmip6_zip':sha(a.cmip6_zip),'source_count_zip':sha(a.observed_zip)},
  'source_original_selected_models':metadata['selected_models'],
  'model_year_reference':'1995–2014 baseline vs 2041–2060 or 2081–2100, Aug–Nov',
  'coastal_marine_grid_dist50_not_bird_foraging_radius':True,
  'source_biological_count_medians_are_not_synchronized_nests':True,
  'model_3_agreement_not_statistical_confidence_interval':True,
  'n_265_breeding_source_unverified':True,
  'no_demographic_forecast_or_legal_mpa_risk_estimated':True,
  'results':summary}
 (a.output/'physical_595_271_158_source_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in audit.items() if k not in ('results','source_original_selected_models')},ensure_ascii=False,indent=2))
 print(pd.DataFrame(summary).to_string(index=False))

if __name__=='__main__':main()
