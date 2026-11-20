"""Fixed L2-logistic development check with region AND shared-scene holdouts."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from diagnose_grid_spectra import BANDS

ROOT=Path(__file__).parent

def fit_weights(d):
    # Equal group weight; inside each group equal class totals; mean weight one.
    n=d.groupby(['site_id','scene_id','label']).label.transform('size').to_numpy()
    w=1/n
    return w/w.mean()

def evaluation_weights(d):
    # Each class separately: equal sites, then equal scenes per site.
    n=d.groupby(['site_id','scene_id','label']).label.transform('size').to_numpy()
    scenes=d.groupby(['site_id','label']).scene_id.transform('nunique').to_numpy()
    sites=d.groupby('label').site_id.transform('nunique').to_numpy()
    return 1/(n*scenes*sites)

def threshold_table(d):
    a=d.copy();a['weight']=evaluation_weights(a)
    a['wp']=a.weight*a.label;a['wn']=a.weight*(1-a.label)
    agg=a.groupby('score',sort=True)[['wp','wn']].sum()
    scores=agg.index.to_numpy();sums=agg.cumsum()
    return pd.DataFrame(dict(threshold=(scores[:-1]+scores[1:])/2,
      positive_recovery=1-sums.wp.to_numpy()[:-1]/agg.wp.sum(),
      candidate_background_rejection=sums.wn.to_numpy()[:-1]/agg.wn.sum()))

def main():
    receipts=json.loads((ROOT/'matched_training_receipts.json').read_text())
    if any(r['status']=='ACCESS_OR_EXTRACTION_ERROR' for r in receipts):
        raise ValueError('Resolve recorded extraction failures before treating coverage as final')
    d=pd.read_csv(ROOT/'matched_training_samples.csv')
    if not np.isfinite(d[list(BANDS)].to_numpy()).all():raise ValueError('Nonfinite spectra')
    support=dict(sites=d.site_id.nunique(),regions=d.region.nunique(),seasons=d.season.nunique(),
      site_scene_pairs=len(d[['site_id','scene_id']].drop_duplicates()),unique_scenes=d.scene_id.nunique(),
      positive_rows=int(d.label.sum()),candidate_background_rows=int((1-d.label).sum()))
    verdict=dict(support=support,validation='training region-held-out development only',
      true_negatives_available=False,independent_post2013_validation=False)
    if not(support['sites']>=30 and support['regions']>=6 and support['seasons']>=4):
        verdict['status']='TRAINING_SUPPORT_NOT_MET'
    else:
        d['score']=np.nan;folds=[]
        for region in sorted(d.region.unique()):
            test=d.region.eq(region);shared=set(d.loc[test,'scene_id'])
            train=(~test)&(~d.scene_id.isin(shared))
            if set(d.loc[train,'label'])!={0,1}:raise ValueError('Fold lacks both classes')
            scaler=StandardScaler().fit(d.loc[train,list(BANDS)])
            model=LogisticRegression(C=1,penalty='l2',solver='lbfgs',max_iter=2000,random_state=20261120)
            model.fit(scaler.transform(d.loc[train,list(BANDS)]),d.loc[train,'label'],sample_weight=fit_weights(d.loc[train]))
            if int(model.n_iter_.max())>=2000:raise ValueError('Convergence not reached')
            d.loc[test,'score']=model.predict_proba(scaler.transform(d.loc[test,list(BANDS)]))[:,1]
            folds.append(dict(heldout_region=region,training_sites=d.loc[train,'site_id'].nunique(),
              training_regions=d.loc[train,'region'].nunique(),training_rows=int(train.sum()),
              heldout_sites=d.loc[test,'site_id'].nunique(),heldout_rows=int(test.sum()),
              nonheldout_rows_purged_shared_scene=int(((~test)&d.scene_id.isin(shared)).sum()),
              scaler_mean=scaler.mean_.tolist(),scaler_scale=scaler.scale_.tolist(),
              coefficients=model.coef_[0].tolist(),intercept=float(model.intercept_[0])))
        if d.score.isna().any():raise ValueError('Incomplete heldout scoring')
        table=threshold_table(d);passed=table[(table.positive_recovery>=.8)&(table.candidate_background_rejection>=.95)]
        feasible=table[table.positive_recovery>=.8]
        if feasible.empty:raise ValueError('No recovery>=.8 diagnostic threshold')
        diagnostic=feasible.sort_values(['candidate_background_rejection','threshold']).iloc[-1]
        chosen=passed.iloc[-1] if not passed.empty else diagnostic
        verdict.update(status='TRAINING_RULE_SUPPORTED' if not passed.empty else 'TRAINING_RULE_NOT_SUPPORTED',
          selected_threshold=float(chosen.threshold) if not passed.empty else None,
          diagnostic_threshold=float(diagnostic.threshold),
          diagnostic_positive_recovery=float(diagnostic.positive_recovery),
          diagnostic_background_rejection=float(diagnostic.candidate_background_rejection))
        details=[]
        for group in ('ALL',*sorted(d.background_class.unique())):
            a=d if group=='ALL' else d[d.background_class.eq(group)]
            w=evaluation_weights(a);correct=np.where(a.label.eq(1),a.score>=chosen.threshold,a.score<chosen.threshold)
            details.append(dict(group=group,rows=len(a),sites=a.site_id.nunique(),regions=a.region.nunique(),
              weighted_correct_rate=float(np.sum(w*correct)/w.sum()),
              threshold=float(chosen.threshold),threshold_is_adopted=not passed.empty))
        d.to_csv(ROOT/'matched_training_heldout_scores.csv',index=False,lineterminator='\n')
        table.to_csv(ROOT/'matched_training_thresholds.csv',index=False,lineterminator='\n')
        pd.DataFrame(details).to_csv(ROOT/'matched_training_class_diagnostics.csv',index=False,lineterminator='\n')
        (ROOT/'matched_training_fold_models.json').write_text(json.dumps(folds,indent=2)+'\n',encoding='utf-8',newline='\n')
    (ROOT/'matched_training_verdict.json').write_text(json.dumps(verdict,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(verdict,indent=2))

if __name__=='__main__':main()
