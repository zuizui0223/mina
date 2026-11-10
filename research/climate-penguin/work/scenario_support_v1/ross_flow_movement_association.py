"""Exploratory association of environmental flow and model-derived movement."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'ross_movement_pairs_v1'
movement=out/'interval_movement.csv.gz';exposure=root/'ross_directional_exposure_v1/interval_exposure.csv.gz'
support=root/'ross_ensemble_ice_v1/interval_support.csv.gz'
m=pd.read_csv(movement);e=pd.read_csv(exposure);s=pd.read_csv(support)
keys=['bird_fn','season','time1','time2']
d=m.merge(e,on=keys+['target'],validate='one_to_many',suffixes=('_movement','_exposure'))
d=d.merge(s[keys+['drift_day']],on=keys,validate='many_to_one')
start=pd.to_datetime(d.time1,utc=True);end=pd.to_datetime(d.time2,utc=True);nend=pd.to_datetime(d.next_time2,utc=True)
mid=start+(end-start)/2;nmid=end+(nend-end)/2
flow_end=pd.to_datetime(d.drift_day,utc=True)+pd.Timedelta(hours=12);flow_start=flow_end-pd.Timedelta(days=1)
left=pd.concat([mid,flow_start],axis=1).max(axis=1);right=pd.concat([nmid,flow_end],axis=1).min(axis=1)
d['nominal_overlap_fraction']=np.maximum(0,(right-left).dt.total_seconds())/(nmid-mid).dt.total_seconds()
assert d.nominal_overlap_fraction.between(0,1).all()
d['date']=start.dt.strftime('%Y-%m-%d');d['month']=start.dt.month
d['trip']=d.bird_fn.astype(str)+'_'+d.season.astype(str)
d.to_csv(out/'joined_exposure_movement.csv.gz',index=False)
def fit(a,mode):
    x=a.projected_km_day.to_numpy();y=a.mean_radial_km_day.to_numpy()
    z=np.ones((len(a),1))
    if mode!='pooled':z=pd.get_dummies(a.trip,dtype=float).to_numpy()
    if mode=='trip_date':z=np.column_stack([z,pd.get_dummies(a.date,drop_first=True,dtype=float)])
    if not len(a):return dict(r=np.nan,slope=np.nan,df=0)
    residual=np.column_stack([x,y])-z@np.linalg.lstsq(z,np.column_stack([x,y]),rcond=None)[0]
    rx,ry=residual.T;xx=rx@rx;yy=ry@ry
    df=len(a)-np.linalg.matrix_rank(np.column_stack([z,x]))
    good=xx>1e-10 and yy>1e-10 and df>0
    slope=rx@ry/xx if good else np.nan
    if good:assert np.isclose(slope,np.linalg.lstsq(np.column_stack([z,x]),y,rcond=None)[0][-1],atol=1e-8)
    return dict(r=rx@ry/np.sqrt(xx*yy) if good else np.nan,slope=slope,df=df)
rows=[]
for target_choice in ['east','west']:
    b=d[d.target.isin(['ROYD','CRZE' if target_choice=='east' else 'CRZW'])]
    for product in ['satellite','nominal','wind']:
        for threshold in [.5,1.]:
            a=b[(b.product_class==product)&(b.support_fraction>=threshold)&(b.nominal_overlap_fraction>=.5)].copy()
            for period in [9,10]:
                g=a[a.month==period]
                for mode in ['pooled','trip','trip_date']:
                    for delete in ['none']+list(map(str,sorted(g.season.unique()))):
                        q=g if delete=='none' else g[g.season!=int(delete)]
                        rows.append(dict(target_choice=target_choice,product=product,threshold=threshold,month=period,mode=mode,
                            deleted_season=delete,n=len(q),trips=q.trip.nunique(),birds=q.bird_fn.nunique(),dates=q.date.nunique(),
                            **fit(q,mode)))
t=pd.DataFrame(rows);t.to_csv(out/'associations.csv',index=False)
v=dict(status='descriptive_model_path_association_not_independent_tracking_confirmation',specifications=len(t),
       estimable=int(t.r.notna().sum()),hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [movement,exposure,support]},
       limits=['Shared model positions enter exposure assignment and response; correlated errors remain',
               'Trip/date adjustment is descriptive, not causal identification',
               'Nominal time-window overlap >=50%, not per-cell complete temporal co-observation',
               'No p-values: few shared dates/years, repeated individuals and spatial grid dependence',
               'No extrapolation of these slopes to future swimming speed or arrival dates'])
(out/'association_validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v));print(t[(t.target_choice=='east')&(t['product']=='satellite')&(t.threshold==.5)&(t.deleted_season=='none')].to_string(index=False))
