"""Freeze full training fit and construct heldout cohort without heldout spectra."""
import hashlib
import json
from pathlib import Path
import pandas as pd
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from fit_matched_training import fit_weights,BANDS

ROOT=Path(__file__).parent

def main():
    train=pd.read_csv(ROOT/'matched_training_samples.csv')
    v=json.loads((ROOT/'matched_training_verdict.json').read_text())
    if v['status']!='TRAINING_RULE_SUPPORTED':raise ValueError('Training rule unsupported')
    scaler=StandardScaler().fit(train[list(BANDS)])
    model=LogisticRegression(C=1,penalty='l2',solver='lbfgs',max_iter=2000,random_state=20261120)
    model.fit(scaler.transform(train[list(BANDS)]),train.label,sample_weight=fit_weights(train))
    frozen=dict(bands=list(BANDS),mean=scaler.mean_.tolist(),scale=scaler.scale_.tolist(),coef=model.coef_[0].tolist(),
      intercept=float(model.intercept_[0]),threshold=v['selected_threshold'],sklearn=sklearn.__version__,
      training_samples_sha256=hashlib.sha256((ROOT/'matched_training_samples.csv').read_bytes()).hexdigest(),spec_commit='80c29977')
    path=ROOT/'matched_center_frozen_model.json'
    if path.exists() and json.loads(path.read_text())!=frozen:raise ValueError('Existing frozen model differs; do not overwrite')
    path.write_text(json.dumps(frozen,indent=2)+'\n',encoding='utf-8',newline='\n')
    d=pd.read_csv(ROOT/'source_positive_records.csv')
    centers=pd.read_csv(ROOT/'published_pixel_exact_matches.csv')[['site_id','easting','northing']].drop_duplicates()
    test=d[d.phase.eq('test')].merge(centers,on=['site_id','easting','northing'],validate='many_to_one')
    final=pd.read_csv(ROOT/'public_grid_evidence/youngflesh2026_tableS2.csv')[['Site ID','Landsat Product Identifier']].drop_duplicates().rename(columns={'Site ID':'site_id','Landsat Product Identifier':'Landsat.Product.Identifier.L1'})
    test=test.merge(final,on=['site_id','Landsat.Product.Identifier.L1'],validate='many_to_one');test['in_final_scene_table']=True
    test.to_csv(ROOT/'matched_center_test_candidates.csv',index=False,lineterminator='\n')
    print('Frozen model and source-only test candidates:',len(test))

if __name__=='__main__':main()
