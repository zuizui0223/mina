#!/usr/bin/env python3
"""Exploratory 159-series legacy-only matched climate and neighbor source pilot.

It cannot verify published 265-series coefficients and must not be used to
forecast future counts. Report all four radii, region×species support and
250-km block resampling, not cherry-picked p-values.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

SEED=20261116
B=1000
RADII=(10,25,50,100)
def within_fit(frame,predictors):
    x=frame[predictors].to_numpy(dtype=float,copy=True)
    y=frame.growth_per_decade.to_numpy(dtype=float,copy=True)
    # Fixed original reporting region × species (not region alone).
    grp=(frame.source_region+"|"+frame.species).to_numpy()
    for g in np.unique(grp):
        mask=grp==g
        x[mask]-=np.mean(x[mask],axis=0)
        y[mask]-=np.mean(y[mask])
    informative=int(np.sum(np.abs(y)>1e-14))
    rank=np.linalg.matrix_rank(x)
    if len(frame)<max(25,2*len(predictors)+15) or rank<len(predictors) or frame.polar_250km_block.nunique()<5:
        return None
    coefs=np.linalg.lstsq(x,y,rcond=None)[0]
    return {'n':len(frame),'n_regions':frame.source_region.nunique(),
      'n_site_species_groups':int(len(np.unique(grp))),
      'n_250km_blocks':int(frame.polar_250km_block.nunique()),
      'rank':int(rank),'informative_residual_rows':informative,
      'coefficients':{col:float(v) for col,v in zip(predictors,coefs)}}
def bootstrap(frame,predictors,target):
    rng=np.random.default_rng(SEED)
    keys=np.sort(frame.polar_250km_block.unique())
    pieces={key:frame[frame.polar_250km_block.eq(key)] for key in keys}
    values=[]
    for i in range(B):
        samples=rng.choice(keys,len(keys),replace=True)
        draw=pd.concat([pieces[k] for k in samples],ignore_index=True)
        fit=within_fit(draw,predictors)
        if fit is not None:
            values.append(fit['coefficients'][target])
    if len(values)<.75*B:return {'valid':len(values),'interval':None,'status':'REGION_OR_BLOCK_INFERENCE_UNSTABLE'}
    return {'valid':len(values),'interval':list(map(float,np.quantile(values,[.025,.975]))),
            'status':'EXPLORATORY_BLOCK_RESAMPLING_NOT_POPULATION_CI'}
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--neighborhood-csv',required=True,type=Path)
    p.add_argument('--source-gate-json',required=True,type=Path)
    p.add_argument('--climate-588-csv',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    gate=json.loads(a.source_gate_json.read_text())
    assert gate['status']=='LEGACY_2456_159_PILOT_NOT_265_VERIFICATION'
    src=pd.read_csv(a.neighborhood_csv)
    climate=pd.read_csv(a.climate_588_csv)
    assert len(src)==159 and climate.site_id.nunique()==588
    tab=src.merge(climate[['site_id','PC1']],on='site_id',how='left',validate='many_to_one')
    tab['early_log_n']=np.log1p(tab.early_n)
    tab['log_nearest_conspecific']=np.log1p(tab.nearest_actual_early_positive_conspecific_km)
    tab['log_early_support']=np.log1p(tab.early_years)
    tab['log_late_support']=np.log1p(tab.late_years)
    for radius in RADII:tab[f'pressure_{radius}']=tab[f'log1p_observed_early_conspecific_nests_{radius}km']
    models={}
    configs={
      'climate_PC1_region_species':(['PC1','early_log_n','log_early_support','log_late_support'],'PC1'),
      'joint_climate_and_pressure_50':(['PC1','pressure_50','early_log_n','log_early_support','log_late_support'],'PC1'),
      'nearest_distance_region_species':(['log_nearest_conspecific','early_log_n','log_early_support','log_late_support'],'log_nearest_conspecific'),
    }
    for radius in RADII:
        configs[f'pressure_{radius}_region_species']=([f'pressure_{radius}','early_log_n','log_early_support','log_late_support'],f'pressure_{radius}')
    for model,(predictors,target) in configs.items():
        sub=tab.dropna(subset=['growth_per_decade',*predictors]).copy()
        fit=within_fit(sub,predictors)
        models[model]={'n_matched':len(sub),'target':target,'point_estimate':fit,
                       'block_quantiles':bootstrap(sub,predictors,target) if fit else None,
                       'source_status':'OLD_2456_COHORT_EXPLORATORY_ONLY'}
    output={'status':'LEGACY_159_PILOT_NOT_265_COMPARABLE',
            'source':gate,'n_159_original_pairs':len(tab),
            'n_marine_588_mean_PC1_matched_site_species':int(tab.PC1.notna().sum()),
            'n_marine_588_PC1_missing':int(tab.PC1.isna().sum()),
            'model_versions':models,
            'warnings':['No time-varying climate response identified by site-mean PC1.',
                        'Regional confounding retained even under region×species fixed effects.',
                        'Early neighborhood undercount where catalogue sites lack early conspecific survey.',
                        'No multiple-range p-value significance search.',
                        'Historical 159 subset is not the claimed modern 265 dataset.']}
    a.output.mkdir(parents=True,exist_ok=True)
    tab.to_csv(a.output/'legacy_159_original_pc1_neighbor_source_matrix.csv',index=False)
    (a.output/'legacy_159_climate_neighbor_pilot.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    print('LEGACY159_PILOT='+json.dumps({'matched':output['n_marine_588_mean_PC1_matched_site_species'],
      'n_total':len(tab),'models':{k:{'n':v['n_matched'],
          'beta':v['point_estimate']['coefficients'][v['target']] if v['point_estimate'] else None,
          'block':v['block_quantiles']} for k,v in models.items()}},ensure_ascii=False))
if __name__=='__main__':main()
