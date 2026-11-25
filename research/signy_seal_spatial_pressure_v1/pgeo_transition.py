"""PGEO conditional redistribution; frozen contract ba24ec1."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
import pandas as pd, numpy as np, zipfile, hashlib,json
from collections import defaultdict
from pathlib import Path
import sys
ROOT=Path(sys.argv[1]);Z=ROOT/'github-actions-artifact-14987514463.zip'
assert hashlib.sha256(Z.read_bytes()).hexdigest()=='d67a47fa9c280da82ace6d471f1ea42a63fdc402f4b6aa6c0734ca68317632ab'
with zipfile.ZipFile(Z) as z:
 assert z.testzip() is None
 r=json.loads(z.read('receipt.json'));assert len(r['files'])==7
 for k,v in r['files'].items():assert hashlib.md5(z.read(k)).hexdigest()==v['md5'] and hashlib.sha256(z.read(k)).hexdigest()==v['sha256']
 d=pd.read_csv(z.open('raw_109_demo.csv'),sep=';',decimal=',')
assert len(d)==3068 and d.colony_code.nunique()==83 and not d.duplicated(['colony','year']).any() and d.groupby('colony_code').island.nunique().eq(1).all()
foot={c:set(t for s in g.colony for t in s.split('-')) for c,g in d.groupby('colony_code')};lookup=defaultdict(set)
for c,ts in foot.items():
 for t in ts:lookup[t].add(c)
ambig=set().union(*(cs for cs in lookup.values() if len(cs)>1));assert ambig=={'P45','PF10'}
rows=[]
for (c,y),g in d.groupby(['colony_code','year']):
 r={'colony_code':c,'year':int(y),'island':g.island.iloc[0]}
 for v in ['adults','chicks']:
  ts=[t for s in g.loc[g[v].notna(),'colony'] for t in s.split('-')];r[v]=g[v].sum(min_count=1);r[v+'_complete']=set(ts)==foot[c] and len(ts)==len(set(ts)) and c not in ambig
 rows.append(r)
a=pd.DataFrame(rows); valid=a[a.adults_complete&a.chicks_complete&a.adults.gt(0)&a.chicks.ge(0)&a.chicks.le(2*a.adults)].copy()
# Previous 1154 support count excluded years without adult records in all islands: reproduce its scope separately if necessary.
ys=[int(y) for y,g in d.groupby('year') if g.groupby('island').adults.count().reindex(['bernard','petrel','rostand'],fill_value=0).gt(0).all()];print('valid',len(valid), 'common adult years',len(valid[valid.year.isin(ys)]),ys)
# Transitions: observed positive pairs at t, productivity, next calendar season complete count including zero. no gaps.
end=a.loc[a.adults_complete,['colony_code','year','adults']].rename(columns={'adults':'next_adults'});end['year']-=1
v=valid.merge(end,on=['colony_code','year'],validate='one_to_one');print('all transitions',len(v),v.colony_code.nunique(),v.year.nunique(), 'zero next',sum(v.next_adults.eq(0)));print(v.groupby(['year','island']).size().unstack(fill_value=0).to_string())
OUT=Path(sys.argv[2]);OUT.mkdir(parents=True,exist_ok=True)
v=v.copy();v['B']=v.chicks/v.adults
prev=a.loc[a.adults_complete,['colony_code','year','adults']].rename(columns={'adults':'prev_adults'});prev['year']+=1
tr=v.merge(prev,on=['colony_code','year'],validate='one_to_one')
assert len(v)==1035 and v.colony_code.nunique()==79 and v.year.nunique()==18
assert len(tr)<=len(v) and tr.prev_adults.ge(0).all()
def fit(q,weight=False,quadratic=False,positive=False,matched=False):
    if positive:q=q[q.next_adults.gt(0)].copy()
    q=q.reset_index(drop=True);cur=np.log(q.adults.to_numpy(float)) if positive else np.log1p(q.adults.to_numpy(float))
    X=[cur]
    if quadratic:X.append(cur**2)
    X.append(q.B.to_numpy(float))
    Y=[np.log(q.next_adults.to_numpy(float)) if positive else np.log1p(q.next_adults.to_numpy(float))]
    if matched:Y.append(np.log1p(q.prev_adults.to_numpy(float)))
    iy=q.island+':'+q.year.astype(str)
    D=pd.get_dummies(pd.DataFrame({'colony':q.colony_code,'iy':iy}),dtype=float).to_numpy()
    sw=np.sqrt(1/iy.groupby(iy).transform('size').to_numpy(float)) if weight else np.ones(len(q))
    Z=np.column_stack([*X,*Y])*sw[:,None];A=D*sw[:,None]
    R=Z-A@np.linalg.lstsq(A,Z,rcond=None)[0]
    k=len(X);rx=R[:,:k];ry=R[:,k:];assert np.linalg.matrix_rank(rx)==k
    b=np.linalg.lstsq(rx,ry,rcond=None)[0];baseline=ry-rx[:,:-1]@np.linalg.lstsq(rx[:,:-1],ry,rcond=None)[0];full=ry-rx@b
    pr2=1-np.sum(full**2,axis=0)/np.sum(baseline**2,axis=0)
    # Frisch–Waugh–Lovell on productivity, independent from multivariate LS above.
    z=rx[:,-1]-rx[:,:-1]@np.linalg.lstsq(rx[:,:-1],rx[:,-1],rcond=None)[0]
    assert np.allclose(b[-1],z@baseline/(z@z),atol=1e-10,rtol=1e-9)
    o={'n':len(q),'units':int(q.colony_code.nunique()),'years':int(q.year.nunique()),'island_years':int(iy.nunique()),'forward_beta':float(b[-1,0]),'forward_partial_R2':float(pr2[0]),'current_size_beta':float(b[0,0]),'productivity_residual_sd':float(np.std(z/sw))}
    if matched:
        o.update(backward_beta=float(b[-1,1]),backward_partial_R2=float(pr2[1]),contrast=float(b[-1,0]-b[-1,1]));assert np.isclose(np.linalg.lstsq(rx,ry[:,0]-ry[:,1],rcond=None)[0][-1],o['contrast'])
    return o
def omissions(q,col,matched=False):
    return [{'omitted':str(x),**fit(q[q[col]!=x],matched=matched)} for x in sorted(q[col].unique())]
with threadpool_limits(limits=1):
    result={'status':'DESCRIPTIVE_CONDITIONAL_TRANSITION','contract':'ba24ec166478b38b76a6dd38b350388a3898607e','source_artifact':14987514463,'source_sha256':'d67a47fa9c280da82ace6d471f1ea42a63fdc402f4b6aa6c0734ca68317632ab','primary':fit(v),'sensitivity':{'equal_island_year':fit(v,weight=True),'quadratic_current':fit(v,quadratic=True),'positive_endpoints_log':fit(v,positive=True)},'matched':fit(tr,matched=True)}
    result['primary']['deletions']={k:omissions(v,k) for k in ['year','island','colony_code']}
    result['matched']['deletions']={k:omissions(tr,k,True) for k in ['year','island']}
for key in ['primary','matched']:
    r=result[key];r['deletion_ranges']={k:{m:[min(x[m] for x in z),max(x[m] for x in z)] for m in (['forward_beta','backward_beta','contrast'] if key=='matched' else ['forward_beta'])} for k,z in r['deletions'].items()}
result['directional_support']=result['primary']['forward_beta']>0 and all(x['forward_beta']>0 for k in ['year','island'] for x in result['primary']['deletions'][k]);result['temporal_asymmetry_support']=result['matched']['contrast']>0 and all(x['contrast']>0 for k in ['year','island'] for x in result['matched']['deletions'][k])
result['limitations']=['Same observational system as published growth association; not independent replication.','Counts and productivity share current count denominator; conditioning and backward contrast do not eliminate measurement error or time-varying confounding.','No individual movements, recruitment, causal inference, p-values or future forecast. Missing years not bridged.']
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({**result,**{k:{m:t for m,t in result[k].items() if m!='deletions'} for k in ['primary','matched']}},indent=2))
