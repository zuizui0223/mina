from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import Ridge
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
p=pd.read_csv(OUT/'behavior_environment_coordinate_join.csv')
p=p[p.environment_join_complete].copy()
p['site_species']=p.species+'|'+p.cam
p['weight']=1/p.groupby(['site_species','season_start_year']).settlement.transform('size')
models={'B':['season_start_year','lat'],'L':['season_start_year','lat','spgmedian','near_sic_mean_month9'],'R':['season_start_year','lat','spgmedian','near_sic_mean_month9','far_sic_mean_month9']}
assert p[list(models['R'])+['settlement']].notna().all().all()
rows=[];folds=[]
for year in range(2015,2021):
    train=p[p.season_start_year<year].copy();test=p[p.season_start_year==year].copy()
    seen=test.site_species.isin(train.site_species);unknown=int((~seen).sum());test=test[seen]
    assert train.season_start_year.max()<year
    folds.append(dict(test_year=year,training_rows=len(train),test_rows=len(test),excluded_new_site_species_rows=unknown,training_latest_year=int(train.season_start_year.max()),test_site_species=test.site_species.nunique()))
    if test.empty:continue
    for model,cols in models.items():
        transform=ColumnTransformer([('numeric',StandardScaler(),cols),('site',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['site_species'])])
        x=transform.fit_transform(train);xt=transform.transform(test)
        fit=Ridge(alpha=1).fit(x,train.settlement,sample_weight=train.weight)
        pred=fit.predict(xt)
        for (_,r),hat in zip(test.iterrows(),pred):
            rows.append(dict(source_row_1based=r.source_row_1based,year=year,species=r.species,cam=r.cam,model=model,observed_index=r.settlement,predicted_index=float(hat),weight=r.weight,error=float(hat-r.settlement)))
q=pd.DataFrame(rows);q.to_csv(OUT/'baseline_forward_predictions.csv',index=False)
pd.DataFrame(folds).to_csv(OUT/'baseline_forward_folds.csv',index=False)
assert not q.duplicated(['source_row_1based','model']).any()
metrics=[]
for scope,col in [('all',None),('species','species'),('year','year')]:
    for key,g in q.groupby(['model']+([col] if col else [])):
        model=key[0];label=str(key[1]) if col else 'all'
        metrics.append(dict(scope=scope,label=label,model=model,rows=len(g),site_species_seasons=float(g.weight.sum()),mae=float(np.average(abs(g.error),weights=g.weight)),rmse=float(np.sqrt(np.average(g.error**2,weights=g.weight)))))
m=pd.DataFrame(metrics);m.to_csv(OUT/'baseline_forward_metrics.csv',index=False)
(OUT/'baseline_forward_checks.json').write_text(json.dumps({'input_sha256':hashlib.sha256((OUT/'behavior_environment_coordinate_join.csv').read_bytes()).hexdigest(),'all_training_strictly_before_test':all(x['training_latest_year']<x['test_year'] for x in folds),'models':models,'alpha':1,'interpretation':'public settlement index; conditional retrospective environmental prediction; not calendar dates or mechanistic inference'},indent=2))
print(m[m.scope.isin(['all','species'])].to_string(index=False))
