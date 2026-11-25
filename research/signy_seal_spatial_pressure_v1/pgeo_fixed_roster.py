import hashlib, json, sys, zipfile
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

p=Path(sys.argv[1]); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256(p.read_bytes()).hexdigest()=='d67a47fa9c280da82ace6d471f1ea42a63fdc402f4b6aa6c0734ca68317632ab'
with zipfile.ZipFile(p) as z:
    assert z.testzip() is None
    receipt=json.loads(z.read('receipt.json'))
    assert len(receipt['files'])==7
    for n,r in receipt['files'].items():
        assert hashlib.md5(z.read(n)).hexdigest()==r['md5']
        assert hashlib.sha256(z.read(n)).hexdigest()==r['sha256']
    d=pd.read_csv(z.open('raw_109_demo.csv'),sep=';',decimal=',')
    env=pd.read_csv(z.open('env_variables.csv'),sep=None,engine='python')
    coord=pd.read_csv(z.open('coordinates.csv'),sep=None,engine='python')
assert len(d)==3068 and d.colony_code.nunique()==83 and d.year.nunique()==24
assert not d.duplicated(['colony','year']).any()
assert (d.code==d.colony_code+d.year.astype(str)).all()
assert (d.groupby('colony_code').island.nunique()==1).all()
assert env.colony_code.is_unique and coord.colony_code.is_unique
assert set(d.colony_code)==set(env.colony_code)==set(coord.colony_code)
assert d[['adults','chicks']].stack().ge(0).all()
islands=['bernard','petrel','rostand']
years=[int(y) for y,g in d.groupby('year') if g.groupby('island').adults.count().reindex(islands,fill_value=0).gt(0).all()]
foot={c:set(t for s in g.colony for t in s.split('-')) for c,g in d.groupby('colony_code')}
lookup=defaultdict(set)
for c,ts in foot.items():
    for t in ts: lookup[t].add(c)
ambig=set().union(*(cs for cs in lookup.values() if len(cs)>1))
rows=[]
for (c,y),g in d.groupby(['colony_code','year']):
    r={'colony_code':c,'year':int(y),'island':g.island.iloc[0]}
    for v in ['adults','chicks']:
        ts=[t for s in g.loc[g[v].notna(),'colony'] for t in s.split('-')]
        r[v]=g[v].sum(min_count=1)
        r[v+'_complete']=set(ts)==foot[c] and len(ts)==len(set(ts)) and c not in ambig
    rows.append(r)
a=pd.DataFrame(rows)

def metrics(p):
    n=p.sum(axis=0); assert n.gt(0).all()
    neff=n**2/p.pow(2).sum(axis=0)
    y=np.asarray(p.columns,dtype=float)
    def slope(x,t=y):return float(np.polyfit(t,np.log(np.asarray(x)),1)[0])
    def loo(x):
        return [float(np.polyfit(np.delete(y,i),np.log(np.delete(np.asarray(x),i)),1)[0]) for i in range(len(y))]
    s=neff/len(p)
    return {'n_units':len(p),'total_first':float(n.iloc[0]),'total_last':float(n.iloc[-1]),'total_change_pct':float(100*(n.iloc[-1]/n.iloc[0]-1)), 'N_eff_first':float(neff.iloc[0]),'N_eff_last':float(neff.iloc[-1]),'N_eff_change_pct':float(100*(neff.iloc[-1]/neff.iloc[0]-1)),'effective_fraction_first':float(s.iloc[0]),'effective_fraction_last':float(s.iloc[-1]),'log_total_slope_per_year':slope(n),'log_N_eff_slope_per_year':slope(neff),'total_slope_loo_range':[min(loo(n)),max(loo(n))],'N_eff_slope_loo_range':[min(loo(neff)),max(loo(neff))],'annual':[{'year':int(yr),'total_pairs':float(n.loc[yr]),'N_eff':float(neff.loc[yr]),'effective_fraction':float(s.loc[yr])} for yr in p.columns]}
result={'status':'DESCRIPTIVE_FIXED_ROSTER','doi':receipt['doi'],'source_artifact_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'years':years,'excluded_years':sorted(set(range(1998,2022))-set(years)),'ambiguous_units_excluded':sorted(ambig),'source_rows':len(d),'source_units':int(d.colony_code.nunique()),'merged_year_rows':len(a),'complete_counts':{v:int(a[v+'_complete'].sum()) for v in ['adults','chicks']},'raw_missing':{v:int(d[v].isna().sum()) for v in ['adults','chicks']},'primary':{},'author_sum_sensitivity':{},'reproduction_support':{}}
for island in islands:
    g=a[(a.island==island)&a.year.isin(years)&~a.colony_code.isin(ambig)]
    for label,strict in [('primary',True),('author_sum_sensitivity',False)]:
        x=g.assign(value=g.adults.where(g.adults_complete) if strict else g.adults).pivot(index='colony_code',columns='year',values='value').reindex(columns=years).dropna()
        m=metrics(x);m['roster']=list(x.index)
        result[label][island]=m
    # Full same-footprint count pairs; only support, no response fit.
    q=g[g.adults_complete&g.chicks_complete&g.adults.gt(0)&g.chicks.le(2*g.adults)]
    result['reproduction_support'][island]={'n_colony_seasons':len(q),'n_units':int(q.colony_code.nunique()),'n_years':int(q.year.nunique()),'per_year_n':{str(k):int(v) for k,v in q.groupby('year').size().items()}}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('primary','author_sum_sensitivity','reproduction_support')},indent=2))
for label in ['primary','author_sum_sensitivity']:
    print(label)
    for i,r in result[label].items():print(i,{k:v for k,v in r.items() if k not in ('annual','roster')})
print('reproduction_support',result['reproduction_support'])
