#!/usr/bin/env python3
"""Independent original source chronology, covariance, MAE and 250-km support gate."""
from __future__ import annotations
import argparse,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from scipy.linalg import cho_factor,cho_solve
SEED=20261116
PRED=['model_persistence_log_n','model_region_species_ssm_log_n','model_5year_ice_ssm_log_n']
def load(path,name):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return pd.read_csv(io.BytesIO(z.read(name)))
def run(source,ice,out,draws):
    count=load(source,'source_observed_2456.csv')
    sites=load(source,'panantarctic_595_site_inventory.csv')
    months=load(ice,'ice_595_outputs/original_595_site_months_120_source_QA.csv')
    y=pd.read_csv(out/'population_dynamics_original_hidden_censuses.csv')
    scores=pd.read_csv(out/'population_dynamics_original_retrospective_scores.csv')
    annual=pd.read_csv(out/'595_original_annual_5year_ice_anomalies.csv')
    fit=json.loads((out/'population_dynamics_model_verdict.json').read_text())
    assert len(count)==2456 and len(months)==71400 and len(sites)==595
    assert len(annual)==17850 and len(y)==149
    assert y.site_id.nunique()==72
    assert len(y[y.cutoff==2010])==71 and len(y[y.cutoff==2015])==78
    assert not y.duplicated(['cutoff','site_id','species']).any()
    geo=y.merge(sites[['site_id','polar_250km_fixed_grid_block','source_region']],
                on='site_id',validate='many_to_one',suffixes=('','_original'))
    assert (geo.original_250km_block==geo.polar_250km_fixed_grid_block).all()
    assert (geo.source_region==geo.source_region_original).all()
    assert geo.groupby('cutoff').original_250km_block.nunique().to_dict()=={2010:9,2015:10}
    source_index=count.set_index(['site_id','species','season'])
    for v in y.itertuples(index=False):
        assert int(source_index.loc[(v.site_id,v.species,v.t_last)].observed_nest_count)==int(v.n_last)
        assert int(source_index.loc[(v.site_id,v.species,v.t_test)].observed_nest_count)==int(v.n_test)
        assert v.t_last<=v.cutoff<v.t_test and 1<=v.t_test-v.cutoff<=10
        assert abs(v.y_test-np.log1p(v.n_test))<1e-10
        assert abs(v.y_last-np.log1p(v.n_last))<1e-10
        assert abs(v.model_persistence_log_n-v.y_last)<1e-10
    annual_sic=months.groupby(['site_id','year']).source_25km_buffer_mean_SIC_pct.mean()
    a=annual.set_index(['site_id','year']).sic
    assert np.max(np.abs(annual_sic.reindex(a.index).to_numpy()-a.to_numpy()))<1e-12
    assert annual.loc[annual.year<1995,'ice5'].isna().all()
    for cut in (2010,2015):
        for model in ('SSM_no_climate','SSM_climate_5yr'):
            q=fit['fitted'][str(cut)][model]['q'];r=fit['fitted'][str(cut)][model]['r']
            g=np.array([1,5,2,8],float);D=np.zeros((4,5))
            for i in range(4):D[i,i]=-1;D[i,i+1]=1
            direct=D@(r*np.eye(5))@D.T+np.diag(q*g)
            M=np.diag(q*g+2*r)+np.diag([-r]*3,1)+np.diag([-r]*3,-1)
            assert np.max(np.abs(M-direct))<1e-12
            vector=np.array([.2,-.35,1.1,-.8])
            c=cho_factor(M,lower=True)
            assert abs(vector@np.linalg.solve(M,vector)-vector@cho_solve(c,vector))<1e-11
    comparisons=[]
    species=[]
    subsets=list(y.groupby('cutoff'))+[('both_not_independent',y)]
    for cut,sub in subsets:
        key=('both_repeated_sites_not_independent' if isinstance(cut,str) else str(cut))
        observed={}
        for pred in PRED:
            mae=float(np.mean(np.abs(sub[pred]-sub.y_test)))
            ref=scores[(scores.cutoff.astype(str)==key)&(scores.model==pred)]
            assert len(ref)==1 and abs(float(ref.MAE_log1p.iloc[0])-mae)<1e-12
            observed[pred]=mae
        blocks=np.sort(sub.original_250km_block.unique())
        rng=np.random.default_rng(SEED+(0 if cut==2010 else 5 if cut==2015 else 10))
        loss_results={}
        for name,model,benchmark in (
           ('drift_vs_persistence',PRED[1],PRED[0]),
           ('ice_vs_persistence',PRED[2],PRED[0]),
           ('ice_vs_drift',PRED[2],PRED[1])):
            diff=(sub[model]-sub.y_test).abs().to_numpy()-(sub[benchmark]-sub.y_test).abs().to_numpy()
            groups={k:diff[sub.original_250km_block.to_numpy()==k] for k in blocks}
            bootstrap=[]
            for _ in range(draws):
                sampled=rng.choice(blocks,size=len(blocks),replace=True)
                bootstrap.append(float(np.mean(np.concatenate([groups[x] for x in sampled]))))
            loss_results[name]={'mean_MAE_delta':float(diff.mean()),
                   'conditional_spatial_block_percentiles':list(map(float,np.quantile(bootstrap,[.025,.975]))),
                   'positive_means_worse':True}
        comparisons.append({'cutoff':key,'n':len(sub),'n_sites':sub.site_id.nunique(),
             'n_regions':sub.source_region.nunique(),'n_250km_blocks':len(blocks),
             'scores':observed,'spatial_block_loss':loss_results})
        for sp,grp in sub.groupby('species'):
            species.append({'cutoff':key,'species':sp,'n':len(grp),'n_sites':grp.site_id.nunique(),
                            'n_250km_blocks':grp.original_250km_block.nunique(),
                 **{'MAE_'+pred:float(np.mean(np.abs(grp[pred]-grp.y_test))) for pred in PRED}})
    pd.DataFrame(species).to_csv(out/'state_space_species_and_cutoff_MAE.csv',index=False)
    receipt={'status':'PASS_ORIGINAL_SOURCE_CHRONOLOGY_250KM_COVARIANCE_MAE',
             'source_counts':2456,'source_months':71400,
             'n_original_test_predictions':149,'n_unique_original_site_ids':72,
             'cluster_draws':draws,'no_population_CIs_claimed':True,
             'survival_recruitment_individually_identified':False,
             'future_CMIP6_nest_numbers_estimated':False,
             'comparisons':comparisons}
    (out/'independent_state_space_250km_validation.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
    print('INDEPENDENT_SOURCE_VALIDATION='+json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--counts-source-zip',required=True,type=Path)
    p.add_argument('--ice-source-zip',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--cluster-draws',type=int,default=4000)
    a=p.parse_args();run(a.counts_source_zip,a.ice_source_zip,a.output,a.cluster_draws)
