"""Apply frozen model once, score limited historical recovery, no ecological Y."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit

ROOT=Path(__file__).parent

def site_rates(d):
    scene=d.groupby(['region','site_id','scene_id','label']).correct.mean().reset_index()
    return scene.groupby(['region','site_id','label']).correct.mean().reset_index()

def region_intervals(s,n=4999):
    regions=sorted(s.region.unique());rng=np.random.default_rng(20261120)
    draws=rng.integers(0,len(regions),size=(n,len(regions)))
    counts=np.stack([(draws==i).sum(axis=1) for i in range(len(regions))],axis=1)
    results={}
    for label,name in [(1,'positive_recovery'),(0,'candidate_background_rejection')]:
        a=s[s.label.eq(label)].groupby('region').correct.agg(['sum','count']).reindex(regions,fill_value=0)
        denominator=counts@a['count'].to_numpy();estimate=(counts@a['sum'].to_numpy())/denominator
        if not np.isfinite(estimate).all():raise ValueError('Invalid regional bootstrap replicate')
        results[name]=dict(estimate=float(a['sum'].sum()/a['count'].sum()),
          lower95=float(np.quantile(estimate,.025)),upper95=float(np.quantile(estimate,.975)),replicates=n)
    return results

def shared_scene_blocks(candidates):
    parent={r:r for r in candidates.region.unique()}
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    for _,g in candidates.groupby('Landsat.Product.Identifier.L1'):
        regions=sorted(g.region.unique())
        for r in regions[1:]:parent[find(r)]=find(regions[0])
    return {r:find(r) for r in parent}

def main(input_dir):
    sample_paths=sorted(input_dir.rglob('matched_test_shard*_samples.csv'))
    receipt_paths=sorted(input_dir.rglob('matched_test_shard*_receipts.json'))
    if len(sample_paths)!=8 or len(receipt_paths)!=8:raise ValueError('Require all eight shards')
    receipts=[r for path in receipt_paths for r in json.loads(path.read_text())]
    if any(r['status']=='ACCESS_OR_EXTRACTION_ERROR' for r in receipts):raise ValueError('Unresolved source failures')
    candidates=pd.read_csv(ROOT/'matched_center_test_candidates.csv')
    expected=set(map(tuple,candidates[['site_id','Landsat.Product.Identifier.L1']].drop_duplicates().to_numpy()))
    received=[(r['site_id'],r['original_product']) for r in receipts]
    if len(received)!=len(set(received)) or set(received)!=expected:raise ValueError('Source cohort coverage differs')
    d=pd.concat([pd.read_csv(p) for p in sample_paths],ignore_index=True)
    key=['site_id','scene_id','label','easting','northing']
    if d.duplicated(key).any():raise ValueError('Duplicated test sample')
    frozen_path=ROOT/'matched_center_frozen_model.json';f=json.loads(frozen_path.read_text())
    x=d[f['bands']].to_numpy()
    if not np.isfinite(x).all() or not d.season.between(2008,2012).all():raise ValueError('Invalid heldout features/years')
    d['score']=expit(((x-np.array(f['mean']))/np.array(f['scale']))@np.array(f['coef'])+f['intercept'])
    d['predicted_positive']=d.score.ge(f['threshold'])
    d['correct']=d.predicted_positive.eq(d.label.eq(1))
    sites=site_rates(d);intervals=region_intervals(sites)
    omit=[]
    for region in sorted(sites.region.unique()):
        a=sites[~sites.region.eq(region)]
        omit.append(dict(omitted_region=region,positive_recovery=float(a[a.label.eq(1)].correct.mean()),
          candidate_background_rejection=float(a[a.label.eq(0)].correct.mean())))
    loo=pd.DataFrame(omit)
    block_map=shared_scene_blocks(candidates)
    block_sites=sites.copy();block_sites['region']=block_sites.region.map(block_map)
    block_intervals=region_intervals(block_sites)
    block_omit=[]
    for block in sorted(block_sites.region.unique()):
        a=block_sites[~block_sites.region.eq(block)]
        block_omit.append(dict(omitted_shared_scene_block=block,positive_recovery=float(a[a.label.eq(1)].correct.mean()),
          candidate_background_rejection=float(a[a.label.eq(0)].correct.mean())))
    block_loo=pd.DataFrame(block_omit)
    block_ok=(block_intervals['positive_recovery']['lower95']>=.8 and block_intervals['candidate_background_rejection']['lower95']>=.95
      and block_loo.positive_recovery.ge(.8).all() and block_loo.candidate_background_rejection.ge(.95).all())
    support=dict(sites=d.site_id.nunique(),regions=d.region.nunique(),seasons=d.season.nunique(),
      site_scene_pairs=len(d[['site_id','scene_id']].drop_duplicates()),unique_scenes=d.scene_id.nunique(),
      positive_rows=int(d.label.sum()),candidate_background_rows=int((1-d.label).sum()),
      candidate_site_scene_pairs=len(expected),candidate_positive_rows=len(candidates),
      no_qa_positive_pairs=sum(r['status']=='NO_QA_POSITIVES' for r in receipts),
      no_background_pairs=sum(r['status']=='NO_CANDIDATE_BACKGROUND' for r in receipts))
    support_ok=support['sites']>=30 and support['regions']>=6 and support['seasons']>=4
    ci_ok=intervals['positive_recovery']['lower95']>=.8 and intervals['candidate_background_rejection']['lower95']>=.95
    loo_ok=loo.positive_recovery.ge(.8).all() and loo.candidate_background_rejection.ge(.95).all()
    verdict=dict(status='LIMITED_HISTORICAL_RECOVERY_SUPPORTED' if support_ok and ci_ok and loo_ok else 'LIMITED_HISTORICAL_RECOVERY_NOT_SUPPORTED',
      support=support,support_passed=bool(support_ok),confidence_bounds_passed=bool(ci_ok),all_region_omissions_passed=bool(loo_ok),
      rates=intervals,threshold=f['threshold'],frozen_model_sha256=hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
      shared_scene_block_map=block_map,shared_scene_blocks=int(block_sites.region.nunique()),
      shared_scene_block_rates=block_intervals,shared_scene_sensitivity_passed=bool(block_ok),
      guano_purity_validated=False,L8_measurement_validated=False,post2013_ecological_replication=False)
    (ROOT/'matched_holdout_verdict.json').write_text(json.dumps(verdict,indent=2)+'\n',encoding='utf-8',newline='\n')
    sites.to_csv(ROOT/'matched_holdout_site_rates.csv',index=False,lineterminator='\n')
    loo.to_csv(ROOT/'matched_holdout_region_omissions.csv',index=False,lineterminator='\n')
    block_loo.to_csv(ROOT/'matched_holdout_shared_scene_omissions.csv',index=False,lineterminator='\n')
    detailed=[]
    for dimension in ['region','season','background_class']:
        for value,g in d.groupby(dimension):
            a=site_rates(g)
            for label,h in a.groupby('label'):
                detailed.append(dict(dimension=dimension,value=value,label=int(label),sites=h.site_id.nunique(),
                  rows=int(g.label.eq(label).sum()),site_weighted_correct_rate=float(h.correct.mean())))
    pd.DataFrame(detailed).to_csv(ROOT/'matched_holdout_stratified_rates.csv',index=False,lineterminator='\n')
    raw=d.to_csv(index=False,lineterminator='\n').encode()
    (ROOT/'matched_holdout_scores.csv.gz').write_bytes(gzip.compress(raw,mtime=0))
    (ROOT/'matched_holdout_source_receipts.json.gz').write_bytes(gzip.compress(json.dumps(receipts).encode(),mtime=0))
    print(json.dumps(verdict,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input-dir',type=Path,required=True)
    main(p.parse_args().input_dir)
