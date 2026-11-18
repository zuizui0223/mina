"""Descriptive associations and strict calendar/region holdouts. No outcome-based tuning."""
from pathlib import Path
import numpy as np,pandas as pd
out=Path(__file__).resolve().parent
d=pd.read_csv(out/'transitions.csv')
r=pd.read_csv(out/'native_resistances.csv')
r['access']=np.log(r.R_B/r.R_A)  # Positive means lower effective resistance for A.
lookup=r.set_index(['key','year','beta']).access
d['geo']=[lookup[k,0,0] for k in d.key]
for beta,label in [(2,'penalty'),(-2,'favor')]:
    d[label]=[lookup[k,y,beta]-lookup[k,y-1,beta] for k,y in zip(d.key,d.year)]
d['share_change']=d.next_share-d.p
d['imbalance']=.5-d.p
d['size_interaction']=d.imbalance*np.log1p(d.total)
d.to_csv(out/'analysis_panel.csv',index=False)
def concentration(p):
    return p*p+(1-p)*(1-p)
models={'persistence':[], 'history_geometry':['imbalance','size_interaction','geo']}
for sign in ['penalty','favor']:models['circuit_'+sign]=models['history_geometry']+[sign]
preds=[]
def predict(train,test,fold,block):
    for model,cols in models.items():
        change=np.zeros(len(test))
        if cols:
            # No intercept so relabelling A/B reverses all fitted share changes.
            X=train[cols].to_numpy();scale=np.sqrt(np.mean(X**2,axis=0));scale[scale<1e-10]=1
            X=X/scale
            coef=np.linalg.solve(X.T@X+np.eye(len(cols)),X.T@train.share_change)
            change=(test[cols].to_numpy()/scale)@coef
        est=np.clip(test.p.to_numpy()+change,0,1)
        for row,p in zip(test.itertuples(),est):
            preds.append(dict(fold=fold,block=block,model=model,key=row.key,region=row.region,species=row.species,year=row.year,
                              p=row.p,target=row.next_share,predicted=p,total=row.total,next_total=row.next_total,
                              share_abs_pp=100*abs(p-row.next_share),concentration_abs=abs(concentration(p)-concentration(row.next_share))))
for year,g in d.groupby('year'):
    train=d[d.year<year]
    if len(train)>=8:predict(train,g,'forward',str(year))
for region,g in d.groupby('region'):
    predict(d[d.region!=region],g,'region',region)
    for year,test in g.groupby('year'):
        train=d[(d.region!=region)&(d.year<year)]
        if len(train)>=8:predict(train,test,'forward_other_region',region+str(year))
v=pd.DataFrame(preds);v.to_csv(out/'holdout_predictions.csv',index=False)
summary=v.groupby(['fold','model']).agg(n=('key','size'),share_MAE_pp=('share_abs_pp','mean'),H_MAE=('concentration_abs','mean')).reset_index()
summary.to_csv(out/'holdout_scores.csv',index=False)
v.groupby(['fold','region','model']).agg(n=('key','size'),share_MAE_pp=('share_abs_pp','mean'),H_MAE=('concentration_abs','mean')).to_csv(out/'regional_scores.csv')
# Shared region-species-seasons with four or more supported, disjoint colonies.
multi=[]
for (fold,region,species,year,model),g in v.groupby(['fold','region','species','year','model']):
    if len(g)<2:continue
    pred=np.r_[g.total*g.predicted,g.total*(1-g.predicted)]/g.total.sum()
    obs=np.r_[g.next_total*g.target,g.next_total*(1-g.target)]/g.next_total.sum()
    multi.append(dict(fold=fold,region=region,species=species,year=year,model=model,n_sites=len(obs),
                      H_observed=obs@obs,H_pred=pred@pred,error=abs(obs@obs-pred@pred)))
pd.DataFrame(multi).to_csv(out/'multi_colony_holdout.csv',index=False)
assoc=[]
for name,g in [('all',d)]+list(d.groupby('region')):
    for x in ['penalty','favor']:
        xx=g[x]-g.groupby('key')[x].transform('mean'); yy=g.share_change-g.groupby('key').share_change.transform('mean')
        assoc.append(dict(region=name,model=x,n=len(g),r_raw=g[x].corr(g.share_change),within_pair_r=xx.corr(yy),
                          slope_pp_per_10pct_relative_access=100*np.log(1.1)*np.dot(xx,yy)/np.dot(xx,xx)))
pd.DataFrame(assoc).to_csv(out/'association.csv',index=False)
print(summary.round(4).to_string(index=False));print(pd.DataFrame(assoc).round(3).to_string(index=False))
