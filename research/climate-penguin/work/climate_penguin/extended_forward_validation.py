from pathlib import Path
import numpy as np,pandas as pd,json,hashlib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import Ridge
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
p=pd.read_csv(OUT/'behavior_environment_drift_join.csv')
edge=pd.read_csv(OUT/'daily_ice_interface_distances.csv.gz',parse_dates=['date'])
assert edge.date.nunique()==1220
edge=edge[(edge.threshold_percent==15)&(edge.date.dt.month==9)].copy();edge['season_start_year']=edge.date.dt.year
e=edge.groupby(['location_id','season_start_year']).agg(edge_days=('nearest_interface_distance_km','count'),edge_distance_km=('nearest_interface_distance_km','mean')).reset_index()
assert e.edge_days.eq(30).all()
p=p.merge(e,on=['location_id','season_start_year'],how='left',validate='many_to_one')
s=pd.read_csv(OUT/'appendix_s1_cameras.csv')
assert not s.camera.duplicated().any()
s['appendix_first_year']=s['first'].str.extract(r'[sS](\d{2})').astype(float)+2000
s['appendix_last_year']=s['last'].str.extract(r'[sS](\d{2})').astype(float)+2000
p=p.merge(s[['camera','colony','appendix_first_year','appendix_last_year']],left_on='colname3',right_on='camera',how='left',validate='many_to_one')
p['appendix_range_consistent']=p.season_start_year.between(p.appendix_first_year,p.appendix_last_year)
p['site_species']=p.species+'|'+p.cam
models={'B':['season_start_year','lat'],'L':['season_start_year','lat','spgmedian','near_sic_mean_month9'],'R':['season_start_year','lat','spgmedian','near_sic_mean_month9','far_sic_mean_month9']}
models['E']=models['R']+['edge_distance_km'];models['D']=models['E']+['drift_m9_east_km_day','drift_m9_north_km_day']
p['extended_complete']=p.environment_join_complete&p.drift_both_months_screen&p[models['D']+['settlement']].notna().all(axis=1)
p.to_csv(OUT/'extended_analysis_cohort.csv',index=False)
rows=[];folds=[];support=[]
for cohort in ['csv_labels','appendix_range_consistent']:
    a=p[p.extended_complete].copy()
    if cohort!='csv_labels':a=a[a.appendix_range_consistent].copy()
    a['weight']=1/a.groupby(['site_species','season_start_year']).settlement.transform('size')
    support.append({'cohort':cohort,'rows':len(a),'geographic_codes':a.cam.nunique(),'site_species_seasons':len(a[['site_species','season_start_year']].drop_duplicates())})
    for year in range(2015,2021):
        train=a[a.season_start_year<year];alltest=a[a.season_start_year==year];test=alltest[alltest.site_species.isin(train.site_species)]
        folds.append(dict(cohort=cohort,year=year,train_rows=len(train),test_rows=len(test),excluded_new_rows=len(alltest)-len(test),latest_train_year=int(train.season_start_year.max())))
        assert train.season_start_year.max()<year
        if test.empty:continue
        for model,cols in models.items():
            tx=ColumnTransformer([('x',StandardScaler(),cols),('site',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['site_species'])])
            fit=Ridge(alpha=1).fit(tx.fit_transform(train),train.settlement,sample_weight=train.weight)
            predictions=fit.predict(tx.transform(test))
            for (_,r),pred in zip(test.iterrows(),predictions):
                rows.append(dict(cohort=cohort,model=model,source_row_1based=r.source_row_1based,year=year,species=r.species,cam=r.cam,observed_index=r.settlement,predicted_index=float(pred),error=float(pred-r.settlement),weight=r.weight))
q=pd.DataFrame(rows);q.to_csv(OUT/'extended_forward_predictions.csv',index=False)
pd.DataFrame(folds).to_csv(OUT/'extended_forward_folds.csv',index=False)
pd.DataFrame(support).to_csv(OUT/'extended_cohort_support.csv',index=False)
metrics=[]
for (cohort,model),g in q.groupby(['cohort','model']):
    metrics.append(dict(cohort=cohort,model=model,rows=len(g),site_species_seasons=g.weight.sum(),mae=np.average(abs(g.error),weights=g.weight),rmse=np.sqrt(np.average(g.error**2,weights=g.weight))))
m=pd.DataFrame(metrics);m.to_csv(OUT/'extended_forward_metrics.csv',index=False)
rng=np.random.default_rng(20261029);diffs=[]
for cohort,g in q.groupby('cohort'):
    unit=g.assign(abs_error=abs(g.error)).groupby(['cam','species','year','model']).abs_error.mean().unstack('model')
    assert unit.notna().all().all()
    for model in models:
        v=(unit[model]-unit['B']).groupby(level='cam').agg(['sum','count'])
        sampled=rng.integers(0,len(v),size=(2000,len(v)))
        boot=v['sum'].to_numpy()[sampled].sum(axis=1)/v['count'].to_numpy()[sampled].sum(axis=1)
        diffs.append(dict(cohort=cohort,model=model,mae_difference_vs_B=float((unit[model]-unit['B']).mean()),block_interval_low=float(np.quantile(boot,.025)),block_interval_high=float(np.quantile(boot,.975)),geographic_blocks=len(v)))
pd.DataFrame(diffs).to_csv(OUT/'extended_forward_mae_differences.csv',index=False)
(OUT/'extended_forward_checks.json').write_text(json.dumps({'models':models,'source_sha256':hashlib.sha256((OUT/'behavior_environment_drift_join.csv').read_bytes()).hexdigest(),'shared_model_test_rows':bool(q.groupby(['cohort','source_row_1based']).model.nunique().eq(5).all()),'outcome_calendar_origin_verified':False,'source_seasons_reconciled':False,'causal_test':False},indent=2))
print(m.to_string(index=False));print(pd.DataFrame(diffs).to_string(index=False))
