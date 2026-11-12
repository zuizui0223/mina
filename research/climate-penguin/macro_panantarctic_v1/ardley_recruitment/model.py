"""Stage associations on identical annual transitions; cohort contribution in nest-pair units."""
from pathlib import Path
import numpy as np,pandas as pd
from scipy.optimize import lsq_linear
from scipy.stats import pearsonr
R=Path(__file__).resolve().parent
p=pd.read_csv(R/'panel.csv')
def ols(x,y):return np.linalg.lstsq(np.column_stack([np.ones(len(x)),x]),y,rcond=None)[0]
assoc=[];inputs=[];pred=[]
for (source,sp),g in p.groupby(['source','species']):
    t=g.set_index('year').sort_index().reindex(range(g.year.min(),g.year.max()+1))
    d=t[['ice','sst','output']].diff().assign(log_nests=np.log(t.nests).diff()).dropna()
    inputs.append(d.assign(source=source,species=sp).reset_index())
    for response in ['log_nests','output']:
        y=d[response].values
        for label,cols in [('ice',['ice']),('sst',['sst']),('joint',['ice','sst'])]:
            x=d[cols].values;b=ols(x,y);yp=b[0]+x@b[1:]
            r2=1-np.sum((y-yp)**2)/np.sum((y-y.mean())**2)
            err=[];base=[]
            for year,row in d.iterrows():
                h=d[abs(d.index-year)>1]
                if len(h)<4:continue
                bet=ols(h[cols],h[response])
                err.append((row[response]-bet[0]-row[cols].values@bet[1:])**2)
                base.append((row[response]-h[response].mean())**2)
            assoc.append(dict(source=source,species=sp,response=response,model=label,n=len(d),r2=r2,
                r=pearsonr(x[:,0],y).statistic if len(cols)==1 else np.nan,cv_skill=1-sum(err)/sum(base),
                slope_ice=b[cols.index('ice')+1] if 'ice' in cols else np.nan,
                slope_sst=b[cols.index('sst')+1] if 'sst' in cols else np.nan))
def cohort(g,L):
    t=g.set_index('year').sort_index()
    # Join by calendar year; missing chick counts remain missing.
    return pd.DataFrame(dict(n=t.nests,prev=t.nests.rename(index=lambda y:y+1),
        young=t.chicks.rename(index=lambda y:y+L),past_n=t.nests.rename(index=lambda y:y+L))).dropna()
def forecast(h,row):
    def two(col):
        X=h[['prev',col]].values
        b=lsq_linear(X,h.n,bounds=([0,0],[1,np.inf])).x
        return b@row[['prev',col]],*b
    val,s,k=two('young')
    return dict(persist=row.prev,drift=row.prev*np.exp(np.log(h.n/h.prev).mean()),lagged_nests=two('past_n')[0],cohort=val,carry=s,entry=k)
for sp in ['ADPE','GEPE']:
    a=p.query("species==@sp and source=='UBA_figure'")
    m=p.query("species==@sp and source=='MAPPPD'")
    for L in [3,4,5]:
        fit=cohort(a,L)
        for year,row in fit.iterrows():
            h=fit[fit.index<year]
            if len(h)>=6:pred.append(dict(species=sp,lag=L,scope='rolling_figure',year=year,n_train=len(h),obs=row.n,**forecast(h,row)))
        test=cohort(m,L)
        for year,row in test[test.index>2014].iterrows():
            pred.append(dict(species=sp,lag=L,scope='frozen_post2014',year=year,n_train=len(fit),obs=row.n,**forecast(fit,row)))
a=pd.DataFrame(assoc);d=pd.DataFrame(pred)
for name,table in [('stage_results',a),('stage_transitions',pd.concat(inputs)),('forecasts',d)]:
    table.to_csv(R/(name+'.csv'),index=False,lineterminator='\n')
summary=[]
for (sp,L,s),g in d.groupby(['species','lag','scope']):
    summary.append(dict(species=sp,lag=L,scope=s,targets=len(g),first=g.year.min(),last=g.year.max(),**{k:(g[k]-g.obs).abs().mean() for k in ['persist','drift','lagged_nests','cohort']}))
z=pd.DataFrame(summary);z.to_csv(R/'scores.csv',index=False,lineterminator='\n')
print(a.query("model=='joint'")[['source','species','response','n','r2','cv_skill']].round(3).to_string(index=False));print(z.round(1).to_string(index=False));print(a.query("source=='MAPPPD' and model!='joint'")[['species','response','model','r']].round(3).to_string(index=False))
# Recursion from 2014 without assimilating later counts/chicks. Realized future climate is a conditional input.
multi=[];support=[]
from scipy.spatial import Delaunay
env=pd.read_csv(R.parent/'ardley_reuse/annual_overlap.csv').set_index('year')
sc=pd.read_csv(R.parent/'ice_sst_all/conditional_contrasts.csv').query("site=='ARDL' and pair=='ADPE__GEPE'")
for sp in ['ADPE','GEPE']:
    tr=p.query("species==@sp and source=='UBA_figure'").set_index('year')
    actual=p.query("species==@sp and source=='MAPPPD'").set_index('year')
    climate=tr[['ice','sst','output']].dropna()
    bb=ols(climate[['ice','sst']],climate.output)
    hull=Delaunay(climate[['ice','sst']].values)
    baseline=env.loc[1995:2014,['ice','sst']].mean().values
    for r in sc.itertuples():
        v=baseline+[r.ice,r.sst]
        support.append(dict(species=sp,model=r.model,ssp=r.ssp,period=r.period,ice_delta=r.ice,sst_delta=r.sst,
            translated_ice=v[0],translated_sst=v[1],inside_stage_climate=hull.find_simplex(v)>=0,physical_ice=0<=v[0]<=100))
    for L in [3,4,5]:
        fit=cohort(tr.reset_index(),L)
        par=forecast(fit,fit.iloc[-1]);s,b=par['carry'],par['entry']
        for kind in ['mean_output','climate_output']:
            n=actual.loc[2014,'nests'];young=actual.loc[:2014,'chicks'].to_dict()
            for yr in range(2015,2020):
                n=s*n+b*young[yr-L]
                out=climate.output.mean() if kind=='mean_output' else np.clip(np.dot([1,*env.loc[yr,['ice','sst']]],bb),0,2)
                young[yr]=n*out
                multi.append(dict(species=sp,lag=L,kind=kind,year=yr,pred=n,obs=actual.loc[yr,'nests'],frozen=actual.loc[2014,'nests']))
pd.DataFrame(multi).to_csv(R/'recursive.csv',index=False,lineterminator='\n')
su=pd.DataFrame(support);su.to_csv(R/'scenario_support.csv',index=False,lineterminator='\n')
print(su.groupby('species').inside_stage_climate.sum())
z=pd.DataFrame(multi);z['error']=(z.pred-z.obs).abs();z['baseline']=(z.frozen-z.obs).abs();print(z.groupby(['species','lag','kind'])[['error','baseline']].mean().round(1))
