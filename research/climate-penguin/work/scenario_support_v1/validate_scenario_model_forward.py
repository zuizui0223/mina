"""Forward diagnostic for the unregularized site+air+ice scenario response model.

Actual test-year environments are supplied; this is not an operational forecast.
Year-FE scenarios cannot predict a new year effect and are not validated here.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/conditional_response_v1/forward';OUT.mkdir(exist_ok=True)
source=ROOT/'outputs/relationship_response_v1/cohort.csv';cohort=pd.read_csv(source)
folds=[];predictions=[];rng=np.random.default_rng(20261030)
for (scope,species),d in cohort.groupby(['scope','species']):
    for year in range(2015,2021):
        train=d[d.year<year];all_test=d[d.year==year];test=all_test[all_test.cam.isin(train.cam)]
        rec=dict(scope=scope,species=species,test_year=year,train_n=len(train),test_n=len(test),new_site_rows_excluded=len(all_test)-len(test))
        if not len(test):
            folds.append(dict(rec,status='no_seen_site_test'));continue
        assert train.year.max()<year and train.year.nunique()>=3
        levels=sorted(train.cam.unique())
        z=np.column_stack([np.ones(len(train))]+[(train.cam==s).to_numpy(float) for s in levels[1:]])
        zt=np.column_stack([np.ones(len(test))]+[(test.cam==s).to_numpy(float) for s in levels[1:]])
        x=train[['airC','ice10']].to_numpy();xt=test[['airC','ice10']].to_numpy();y=train.y.to_numpy()
        design=np.column_stack([z,x]);rank=np.linalg.matrix_rank(design)
        if rank<design.shape[1] or len(train)<=rank:
            folds.append(dict(rec,status='training_response_not_identifiable'));continue
        coef=np.linalg.lstsq(design,y,rcond=None)[0]
        beta=coef[-2:]
        rx=x-z@np.linalg.lstsq(z,x,rcond=None)[0];ry=y-z@np.linalg.lstsq(z,y,rcond=None)[0]
        assert np.allclose(beta,np.linalg.lstsq(rx,ry,rcond=None)[0],atol=1e-8)
        base=zt@np.linalg.lstsq(z,y,rcond=None)[0]
        estimate=np.column_stack([zt,xt])@coef
        # Baseline predictions independently equal each training site's mean.
        assert np.allclose(base,test.cam.map(train.groupby('cam').y.mean()),atol=1e-8)
        folds.append(dict(rec,status='estimated',air_coefficient=beta[0],ice10_coefficient=beta[1],residual_df=len(train)-rank))
        for k,r in enumerate(test.itertuples()):
            predictions.append(dict(scope=scope,species=species,year=year,cam=r.cam,observed=r.y,baseline=base[k],environment=estimate[k],
              absolute_error_baseline=abs(r.y-base[k]),absolute_error_environment=abs(r.y-estimate[k]),
              delta_absolute_error=abs(r.y-estimate[k])-abs(r.y-base[k]),
              outside_training_marginal_range=bool(((xt[k]<x.min(axis=0))|(xt[k]>x.max(axis=0))).any())))
folds=pd.DataFrame(folds);pred=pd.DataFrame(predictions)
folds.to_csv(OUT/'folds.csv',index=False);pred.to_csv(OUT/'predictions.csv',index=False)
summary=[]
for (scope,species),d in pred.groupby(['scope','species']):
    rec=dict(scope=scope,species=species,test_rows=len(d),sites=d.cam.nunique(),years=d.year.nunique(),
             baseline_MAE=d.absolute_error_baseline.mean(),environment_MAE=d.absolute_error_environment.mean(),
             delta_MAE=d.delta_absolute_error.mean(),outside_training_marginal_range=int(d.outside_training_marginal_range.sum()))
    for cluster in ['cam','year']:
        g=d.groupby(cluster).delta_absolute_error.agg(['sum','count'])
        index=rng.integers(0,len(g),size=(9999,len(g)))
        values=g['sum'].to_numpy()[index].sum(axis=1)/g['count'].to_numpy()[index].sum(axis=1)
        rec[cluster+'_delta_low'],rec[cluster+'_delta_high']=np.quantile(values,[.025,.975])
    summary.append(rec)
summary=pd.DataFrame(summary);summary.to_csv(OUT/'summary.csv',index=False)
pred.groupby(['scope','species','year'],as_index=False).agg(test_rows=('cam','size'),delta_MAE=('delta_absolute_error','mean')).to_csv(OUT/'year_errors.csv',index=False)
receipt={'passed':True,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'planned_folds':len(folds),'estimated_folds':int(folds.status.eq('estimated').sum()),'predictions':len(pred),
 'estimand':'unregularized site-fixed-effect two-environment model tested on later years at previously observed sites with realized September inputs',
 'limitations':['not new-site validation','not future climate transformation validation','not a real-time return forecast','not validation of future year fixed effects','conditional scenarios retain unverified calendar origin',
 'paired error resampling describes limited site/year support, not full uncertainty or an effect significance test']}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(summary.to_string(index=False));print(folds.status.value_counts().to_string())
