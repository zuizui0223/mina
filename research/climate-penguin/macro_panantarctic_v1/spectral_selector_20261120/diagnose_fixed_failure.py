"""Post-hoc diagnostics; never change the frozen classifier or its threshold."""
import gzip
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).parent
SEED=20261120

def block_mean_intervals(d,columns):
    blocks=sorted(d.block.unique());rng=np.random.default_rng(SEED)
    draws=rng.integers(0,len(blocks),size=(4999,len(blocks)))
    count=np.stack([(draws==i).sum(axis=1) for i in range(len(blocks))],axis=1)
    sums=d.groupby('block')[columns].sum().reindex(blocks)
    sizes=d.groupby('block').size().reindex(blocks).to_numpy()
    estimates=(count@sums.to_numpy())/(count@sizes)[:,None]
    return pd.DataFrame([dict(variable=c,estimate=float(d[c].mean()),
        lower95=float(np.quantile(estimates[:,i],.025)),upper95=float(np.quantile(estimates[:,i],.975)),
        sites=len(d),blocks=len(blocks),replicates=4999) for i,c in enumerate(columns)])

def scene_metadata():
    items={i['id']:i for p in (ROOT/'metadata_cache').glob('*.json') for i in json.loads(p.read_text())}
    if not items:raise ValueError('Run audit_sources.py to restore source-only metadata cache')
    records=[]
    for scene,item in items.items():
        p=item['properties']
        records.append(dict(scene_id=scene,sun_elevation=p.get('view:sun_elevation'),
          scene_cloud_percent=p.get('eo:cloud_cover'),acquisition_datetime=p.get('datetime')))
    return pd.DataFrame(records)

def fixed_effects_diagnostic(scene):
    s=scene.copy()
    s['sun_per10']=s.sun_elevation/10;s['cloud_per10']=s.scene_cloud_percent/10
    s['day_per30']=s.season_day/30;s['core_fraction_per10pp']=s.core3_fraction/.1
    columns=['sun_per10','cloud_per10','day_per30','core_fraction_per10pp']
    s=s.dropna(subset=columns+['recovery'])
    groups=['site_id','season']
    xm=s[columns]-s.groupby(groups)[columns].transform('mean')
    ym=s.recovery-s.groupby(groups).recovery.transform('mean')
    info=pd.Series(np.max(abs(xm.to_numpy()),axis=1)>1e-10,index=s.index).groupby([s.site_id,s.season]).transform('any')
    s=s[info].copy();x=xm[info].to_numpy();y=ym[info].to_numpy()
    w=1/s.groupby('site_id').site_id.transform('size').to_numpy()
    rootw=np.sqrt(w);beta,_,rank,_=np.linalg.lstsq(x*rootw[:,None],y*rootw,rcond=None)
    if rank!=len(columns):raise ValueError('Condition model lacks full rank')
    blocks=sorted(s.block.unique())
    matrices=[];vectors=[]
    for block in blocks:
        use=s.block.eq(block).to_numpy();xb=x[use];wb=w[use];yb=y[use]
        matrices.append((xb*wb[:,None]).T@xb);vectors.append((xb*wb[:,None]).T@yb)
    rng=np.random.default_rng(SEED);draws=rng.integers(0,len(blocks),size=(4999,len(blocks)))
    estimates=[];invalid=0
    for draw in draws:
        a=np.sum(np.asarray(matrices)[draw],axis=0);b=np.sum(np.asarray(vectors)[draw],axis=0)
        if np.linalg.matrix_rank(a)<len(columns):invalid+=1;continue
        estimates.append(np.linalg.solve(a,b))
    estimates=np.asarray(estimates)
    out=pd.DataFrame([dict(variable=c,coefficient=float(beta[i]),lower95=float(np.quantile(estimates[:,i],.025)),
       upper95=float(np.quantile(estimates[:,i],.975))) for i,c in enumerate(columns)])
    s['within_recovery']=y;s['fitted_within_recovery']=x@beta
    summary=dict(sites=s.site_id.nunique(),regions=s.region.nunique(),blocks=len(blocks),site_scene_pairs=len(s),
      informative_site_seasons=len(s[groups].drop_duplicates()),all_site_seasons=len(scene[groups].drop_duplicates()),
      condition_number=float(np.linalg.cond(x*rootw[:,None])),rank=int(rank),
      within_r_squared=float(1-np.sum(w*(y-x@beta)**2)/np.sum(w*y*y)),
      valid_bootstrap=len(estimates),singular_bootstrap=invalid,causal_interpretation=False)
    s.to_csv(ROOT/'failure_condition_model_rows.csv',index=False,lineterminator='\n')
    pd.DataFrame(x,columns=columns).corr().to_csv(ROOT/'failure_within_predictor_correlations.csv',lineterminator='\n')
    out.to_csv(ROOT/'failure_condition_coefficients.csv',index=False,lineterminator='\n')
    return summary

def main():
    frozen=json.loads((ROOT/'matched_center_frozen_model.json').read_text());bands=frozen['bands']
    verdict=json.loads((ROOT/'matched_holdout_verdict.json').read_text());mapping=verdict['shared_scene_block_map']
    train=pd.read_csv(ROOT/'matched_training_samples.csv');train=train[train.label.eq(1)]
    test=pd.read_csv(ROOT/'matched_holdout_scores.csv.gz');test=test[test.label.eq(1)].copy()
    keys=['site_id','easting','northing']
    a=train.groupby(keys)[bands].mean();b=test.groupby(keys)[bands].mean()
    pair=a.join(b,how='inner',lsuffix='_train',rsuffix='_test').reset_index()
    regions=test[['site_id','region']].drop_duplicates()
    pair=pair.merge(regions,on='site_id',validate='many_to_one');pair['block']=pair.region.map(mapping)
    contributions=[]
    for band,coef,scale in zip(bands,frozen['coef'],frozen['scale']):
        name=band+'_contribution';pair[name]=(pair[band+'_test']-pair[band+'_train'])*coef/scale;contributions.append(name)
    pair['total_logit_change']=pair[contributions].sum(axis=1)
    delta=(pair[[b+'_test' for b in bands]].to_numpy()-pair[[b+'_train' for b in bands]].to_numpy())@ (np.array(frozen['coef'])/frozen['scale'])
    if not np.allclose(delta,pair.total_logit_change,atol=1e-10):raise ValueError('Additive decomposition failed')
    site=pair.groupby(['site_id','region','block'])[contributions+['total_logit_change']].mean().reset_index()
    block_mean_intervals(site,contributions+['total_logit_change']).to_csv(ROOT/'failure_spectral_decomposition.csv',index=False,lineterminator='\n')
    site.to_csv(ROOT/'failure_spectral_site_contributions.csv',index=False,lineterminator='\n')
    (ROOT/'failure_coordinate_pairs.csv.gz').write_bytes(gzip.compress(pair.to_csv(index=False,lineterminator='\n').encode(),mtime=0))
    pair[[b+'_test' for b in bands]].corr().to_csv(ROOT/'failure_test_band_correlations.csv',lineterminator='\n')
    cores=pd.read_csv(ROOT/'connected_label_cells.csv');cores=cores[cores.phase.eq('test')]
    matches=pd.read_csv(ROOT/'scene_matches.csv')[['original_product','scene_id']]
    cores=cores.merge(matches,on='original_product',validate='many_to_one')
    core_keys=['site_id','scene_id','cell']
    if cores.duplicated(core_keys).any():raise ValueError('Core label join duplicates')
    test=test.merge(cores[core_keys].assign(core3=True),on=core_keys,how='left',validate='many_to_one')
    test['core3']=test.core3.eq(True);test['block']=test.region.map(mapping)
    grouped=test.groupby(['site_id','region','block','scene_id','core3']).correct.agg(['mean','size']).reset_index()
    rates=grouped.pivot(index=['site_id','region','block','scene_id'],columns='core3',values=['mean','size'])
    rates.columns=['outside_core_recovery','inside_core_recovery','outside_core_n','inside_core_n']
    rates=rates.dropna().reset_index();rates['difference']=rates.inside_core_recovery-rates.outside_core_recovery
    contrast=[]
    for minimum in [1,3]:
        q=rates[(rates.outside_core_n>=minimum)&(rates.inside_core_n>=minimum)]
        ps=q.groupby(['site_id','region','block'])[['inside_core_recovery','outside_core_recovery','difference']].mean().reset_index()
        ci=block_mean_intervals(ps,['inside_core_recovery','outside_core_recovery','difference'])
        ci['minimum_rows_per_group']=minimum;ci['paired_site_scenes']=len(q);ci['regions']=ps.region.nunique();contrast.append(ci)
    rates.to_csv(ROOT/'failure_core_same_image_pairs.csv',index=False,lineterminator='\n')
    pd.concat(contrast).to_csv(ROOT/'failure_core_contrasts.csv',index=False,lineterminator='\n')
    scene=test.groupby(['site_id','region','block','scene_id','season']).agg(recovery=('correct','mean'),
      core3_fraction=('core3','mean'),positive_rows=('cell','size')).reset_index()
    scene=scene.merge(scene_metadata(),on='scene_id',how='left',validate='many_to_one')
    if scene[['sun_elevation','scene_cloud_percent','acquisition_datetime']].isna().any().any():raise ValueError('Missing source metadata')
    date=pd.to_datetime(scene.acquisition_datetime,utc=True)
    start=pd.to_datetime(scene.season.astype(str)+'-11-01',utc=True)
    scene['season_day']=(date.dt.floor('D')-start).dt.days
    if not scene.season_day.between(0,120).all():raise ValueError('Unexpected seasonal date')
    scene.to_csv(ROOT/'failure_scene_conditions.csv',index=False,lineterminator='\n')
    model_summary=fixed_effects_diagnostic(scene)
    summary=dict(paired_coordinates=len(pair),paired_sites=site.site_id.nunique(),paired_regions=site.region.nunique(),
      paired_blocks=site.block.nunique(),condition_model=model_summary,threshold_changed=False,
      classifier_refitted=False,post_hoc_diagnostic=True,new_ecological_outcomes=False)
    (ROOT/'failure_diagnosis_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(summary,indent=2));print(pd.read_csv(ROOT/'failure_spectral_decomposition.csv').to_string(index=False))
    print(pd.read_csv(ROOT/'failure_core_contrasts.csv').to_string(index=False));print(pd.read_csv(ROOT/'failure_condition_coefficients.csv').to_string(index=False))

if __name__=='__main__':main()
