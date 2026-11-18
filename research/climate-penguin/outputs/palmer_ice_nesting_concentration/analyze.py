from pathlib import Path
import numpy as np
import pandas as pd
out=Path(__file__).resolve().parent
d=pd.read_csv('work/comparison_audit/palmer_census.csv',skiprows=[1])
d['year']=pd.to_datetime(d.time,utc=True).dt.year
assert not d.duplicated(['island_name','colony_code','year']).any()
ice=pd.read_csv('work/mina-sync/research/climate-penguin/outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv')
ice=ice.query('site_id=="LITC" and inner_km==0 and 8<=month<=10')
assert ice.groupby('year').size().eq(3).all() and ice.sic_mean.notna().all()
sic=ice.groupby('year').sic_mean.mean()
rows=[]
def save(scale,year,v):
    a=np.asarray(v,float); total=a.sum()
    if total>0: rows.append(dict(scale=scale,year=year,total=total,neff=total**2/(a@a),sic=sic.loc[year]))
for y,g in d.groupby('year'):
    assert len(g.island_name.unique())==5
    save('among_five_islands',y,g.groupby('island_name').num_breeding_pairs.sum())
    for island in ['COR','HUM','LIT']:
        save(island,y,g[g.island_name==island].num_breeding_pairs)
a=pd.DataFrame(rows);a.to_csv(out/'annual.csv',index=False)
def corr(x,y):return np.corrcoef(x,y)[0,1]
def detrend(t,x):return x-np.polyval(np.polyfit(t,x,1),t)
for name,g in a.groupby('scale'):
    t=g.year.to_numpy();x=g.sic.to_numpy();y=g.neff.to_numpy();ok=np.diff(t)==1
    print(name,len(g),y[0],y[-1],*[round(v,3) for v in [corr(x,y),corr(detrend(t,x),detrend(t,y)),corr(np.diff(x)[ok],np.diff(y)[ok])]])
print('earliest census month',pd.to_datetime(d.time,utc=True).dt.month.min())
