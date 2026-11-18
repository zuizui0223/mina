"""Assess fixed three-colony concentration with only held-out group-season predictions."""
from pathlib import Path
import numpy as np,pandas as pd
out=Path(__file__).resolve().parent
d=pd.read_csv(out/'three_colony_panel.csv')
r=pd.read_csv(out/'tri_native.csv').set_index(['key','year','beta'])
def accessibility(g,year,beta):
    a=r.loc[(f'tri_{g}_1',year,beta)]; b=r.loc[(f'tri_{g}_2',year,beta)]
    assert abs(a.R_A-b.R_A)<1e-7
    v=-np.log([a.R_A,a.R_B,b.R_B]);return v-v.mean()
for (group,year),s in d.groupby(['group','year']):
    ix=s.sort_values('idx').index
    d.loc[ix,'geo']=accessibility(group,0,0)
    for beta,name in [(2,'penalty'),(-2,'favor')]:
        d.loc[ix,name]=accessibility(group,year,beta)-accessibility(group,year-1,beta)
d['imbalance']=1/3-d.p;d['size_interaction']=d.imbalance*np.log1p(d.total)
def project(v):
    u=np.sort(v)[::-1];cs=np.cumsum(u)-1;k=np.flatnonzero(u>cs/np.arange(1,len(v)+1))[-1]
    return np.maximum(v-cs[k]/(k+1),0)
rows=[]
for (group,year),s in d.groupby(['group','year']):
    region=s.region.iloc[0]
    for fold,mask in [('region',d.region!=region),('forward',d.year<year),('forward_other_region',(d.region!=region)&(d.year<year))]:
        t=d[mask]
        if len(t.drop_duplicates(['group','year']))<3:continue
        for name,extra in [('persistence',[]),('history_geometry',[]),('circuit_penalty',['penalty']),('circuit_favor',['favor'])]:
            pred=s.p.to_numpy()
            if name!='persistence':
                cols=['imbalance','size_interaction','geo']+extra
                X=t[cols].to_numpy();scale=np.sqrt(np.mean(X**2,axis=0));scale[scale<1e-10]=1;X=X/scale
                coef=np.linalg.solve(X.T@X+np.eye(len(cols)),X.T@(t.next_share-t.p))
                pred=project(pred+s[cols].to_numpy()/scale@coef)
            obs=s.next_share.to_numpy()
            rows.append(dict(group=group,year=year,region=region,fold=fold,model=name,H_observed=obs@obs,H_predicted=pred@pred,H_error=abs(obs@obs-pred@pred),share_MAE_pp=100*np.mean(abs(obs-pred))))
z=pd.DataFrame(rows);z.to_csv(out/'three_colony_holdouts.csv',index=False)
m=z.groupby(['fold','model']).agg(n=('year','size'),share_MAE_pp=('share_MAE_pp','mean'),H_MAE=('H_error','mean'));m.to_csv(out/'three_colony_scores.csv');print(m.round(5))
