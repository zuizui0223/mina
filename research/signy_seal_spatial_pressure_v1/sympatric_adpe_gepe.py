"""Sympatric ADPE–GEPE analysis; frozen contract feb2487."""
import hashlib, json, zipfile, sys, itertools
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(sys.argv[1]);OUT=Path(sys.argv[2]);OUT.mkdir(parents=True,exist_ok=True)
PINS={14934334550:'0264797d82bee62df3b14346428abb4a4994ec01224906c3468afbe99a2c56c4',13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',14926710177:'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8',13829236358:'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5'}
def read(i,name,pin=None):
 p=ROOT/f'github-actions-artifact-{i}.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==PINS[i]
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  if pin:assert hashlib.sha256(z.read(name)).hexdigest()==pin
  return pd.read_csv(z.open(name))
x=read(14934334550,'public_source.csv','d169c409cf278b137d6df35fbeb9ab3409bdea15f41c39bcaec549a4d4dbca89');a=read(13669533413,'panantarctic_595_site_inventory.csv');p=read(14926710177,'winter_595.csv');h=read(13829236358,'original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv')
assert len(x)==5487 and len(a)==595 and a.site_id.is_unique
x=x[x.count_type.eq('nests')&x.common_name.isin(['adelie penguin','gentoo penguin'])&x.penguin_count.notna()].copy();assert x.penguin_count.ge(0).all()
x['sp']=x.common_name.map({'adelie penguin':'ADPE','gentoo penguin':'GEPE'});x['cite']=x.reference.str.extract(r'id="([^\"]+)"');x['method']=x.vantage.fillna('unknown')
g=x.groupby(['site_id','sp','season_starting']).agg(n=('penguin_count','nunique'),method_n=('method','nunique'),method=('method','first'),cite_n=('cite','nunique'),cite=('cite','first'),missing_cite=('cite',lambda s:s.isna().sum()),count=('penguin_count','first')).reset_index();g=g[(g.n==1)&(g.method_n==1)&(g.method!='unknown')&(g.cite_n==1)&(g.missing_cite==0)]
j=g[g.sp=='ADPE'].merge(g[g.sp=='GEPE'],on=['site_id','season_starting'],suffixes=('_A','_G'),validate='one_to_one');j=j[(j.method_A==j.method_G)&(j.cite_A==j.cite_G)].merge(a[['site_id','source_region','latitude','longitude','polar_250km_fixed_grid_block']],on='site_id',how='left',validate='many_to_one');assert j.source_region.notna().all() and len(j)==112 and j.site_id.nunique()==27
q=j[j.season_starting.between(1993,2020)].sort_values(['site_id','season_starting']).copy();assert len(q)==85 and q.site_id.nunique()==23
for col in ['season_starting','method_A','cite_A','count_A','count_G']:
 q['next_'+col]=q.groupby('site_id')[col].shift(-1)
q=q[q.next_season_starting.sub(q.season_starting).between(1,5)&q.method_A.eq(q.next_method_A)].copy();q['start']=q.season_starting.astype(int);q['end']=q.next_season_starting.astype(int);q['duration']=q.end-q.start;assert len(q)==55 and q.site_id.nunique()==7
q['delta_A']=q.next_count_A-q.count_A;q['delta_G']=q.next_count_G-q.count_G
# Component construction, never double-count site within window. Radius is geographic proxy, not movement range.
def distance(a,b):
 l1,l2=np.deg2rad([a.latitude,b.latitude]);return float(2*6371.0088*np.arcsin(np.sqrt(np.sin((l1-l2)/2)**2+np.cos(l1)*np.cos(l2)*np.sin(np.deg2rad(a.longitude-b.longitude)/2)**2)))
def comps(z,radius):
 records={r.site_id:r for r in z.itertuples()};adj={k:{k} for k in records}
 for u,v in itertools.combinations(records,2):
  if distance(records[u],records[v])<=radius:adj[u].add(v);adj[v].add(u)
 seen=set();ret=[]
 for u in sorted(records):
  if u in seen:continue
  cc={u};todo=[u]
  while todo:
   v=todo.pop();n=adj[v]-cc;cc|=n;todo.extend(n)
  seen|=cc
  if len(cc)>=2:ret.append(z[z.site_id.isin(cc)])
 return ret

def network_rows(radius,strict=False,omit_site=None,omit_year=None):
 r=[];cols=['source_region','start','end','method_A']+(['cite_A','next_cite_A'] if strict else [])
 for k,z in q[q.duration.eq(1)].groupby(cols):
  if omit_year is not None and k[1]==omit_year:continue
  # Delete site within frozen full component; do not add new sites or merge windows.
  for c in comps(z,radius):
   if omit_site is not None:c=c[c.site_id!=omit_site]
   if len(c)<2:continue
   t={'region':k[0],'start':int(k[1]),'end':int(k[2]),'method':k[3],'sites':sorted(c.site_id.tolist()),'shared_crosssite_citations':bool(c.cite_A.nunique()==c.next_cite_A.nunique()==1)}
   for sp in ['A','G']:
    d=c['delta_'+sp];L=float((-d.clip(upper=0)).sum());G=float(d.clip(lower=0).sum());assert np.isclose(G-L,d.sum())
    t[sp]={'loss':L,'gain':G,'net':G-L,'C':min(L,G)/L if L>0 else None,'uncapped':G/L if L>0 else None}
   r.append(t)
 return r

def summarize(rows):
 paired=[r for r in rows if r['A']['loss']>0 and r['G']['loss']>0]
 def pool(rr,sp):
  t=[r[sp] for r in rr if r[sp]['loss']>0];L=sum(z['loss'] for z in t);G=sum(z['gain'] for z in t)
  return {'n_loss_windows':len(t),'loss':L,'gain_in_loss_windows':G,'capped_compensation':sum(min(z['loss'],z['gain']) for z in t)/L if L else None,'uncapped_gain_loss':G/L if L else None,'net_all_windows':sum(r[sp]['net'] for r in rr)}
 dif=[r['G']['C']-r['A']['C'] for r in paired]
 return {'n_windows':len(rows),'sites':sorted({s for r in rows for s in r['sites']}),'n_paired_loss_windows':len(paired),'paired_differences':dif,'mean_paired_difference':float(np.mean(dif)) if dif else None,'positive_paired_differences':sum(t>0 for t in dif),'all_loss_pool':{sp:pool(rows,sp) for sp in ['A','G']},'paired_loss_pool':{sp:pool(paired,sp) for sp in ['A','G']}}
network={}
for radius in [50,100]:
 strict=network_rows(radius,True);assert len(strict)==0
 rows=network_rows(radius);assert len(rows)==11
 network[str(radius)]={'strict_windows':len(strict),'windows':rows,'summary':summarize(rows),'omit_year':{str(y):summarize(network_rows(radius,omit_year=y)) for y in sorted({r['start'] for r in rows})},'omit_site':{s:summarize(network_rows(radius,omit_site=s)) for s in sorted({s for r in rows for s in r['sites']})}}
# All four marine variables must be measured in every year from start+1 to end.
V=['P100_pp','mean_source_SIC_pp','mean_GLORYS_salinity','mean_GLORYS_thetao_C']
P=p[(p.radius_km==100)&(p.n_valid_months==5)].copy();P['P100_pp']=P.direct_DEEPAA_coastal_polynya_fraction*100
H=h[(h.original_source_4_OSISAF_months==4)&(h.original_source_4_GLORYS_months==4)]
cl=P[['site_id','season','P100_pp']].rename(columns={'season':'year'}).merge(H[['site_id','year',*V[1:]]],on=['site_id','year'],validate='one_to_one');assert len(cl)==588*15 and cl[V].notna().all().all()
zero=x[x.penguin_count.eq(0)].groupby('site_id').season_starting.apply(set).to_dict()
valid=[];excluded={'nonpositive_endpoint':0,'observed_intervening_zero':0,'incomplete_marine':0}
for r in q.itertuples():
 if min(r.count_A,r.count_G,r.next_count_A,r.next_count_G)<=0:excluded['nonpositive_endpoint']+=1;continue
 if set(range(r.start+1,r.end))&zero.get(r.site_id,set()):excluded['observed_intervening_zero']+=1;continue
 t=cl[(cl.site_id==r.site_id)&cl.year.between(r.start+1,r.end)]
 if set(t.year)!=set(range(r.start+1,r.end+1)):excluded['incomplete_marine']+=1;continue
 ga=np.log(r.next_count_A/r.count_A)/r.duration;gg=np.log(r.next_count_G/r.count_G)/r.duration
 valid.append({'site_id':r.site_id,'region':r.source_region,'block':r.polar_250km_fixed_grid_block,'start':r.start,'end':r.end,'duration':r.duration,'A_growth':float(ga),'G_growth':float(gg),'contrast':float(gg-ga),**{k:float(t[k].mean()) for k in V}})
v=pd.DataFrame(valid);assert len(v)+sum(excluded.values())==55

def fit(g):
 g=g[g.groupby('site_id').site_id.transform('size')>=2].copy();n=len(g);ns=g.site_id.nunique();ny=g.end.nunique();out={'n':n,'sites':int(ns),'years':int(ny),'regions':int(g.region.nunique()),'site_ids':sorted(g.site_id.unique().tolist())}
 if n==0: return {**out,'status':'NO_ROWS'}
 D=pd.get_dummies(pd.DataFrame({'site':g.site_id,'year':g.end.astype(str)}),dtype=float).to_numpy();w=np.sqrt(1/g.groupby('site_id').site_id.transform('size').to_numpy(float));A=D*w[:,None];Z=g[V+['contrast']].to_numpy(float)*w[:,None];R=Z-A@np.linalg.lstsq(A,Z,rcond=None)[0];rankFE=int(np.linalg.matrix_rank(A));rankX=int(np.linalg.matrix_rank(R[:,:4],tol=1e-9));df=n-rankFE-rankX
 out.update(rank_FE=rankFE,rank_physical=rankX,residual_df=df)
 if ns<3 or rankX<4 or df<5:return {**out,'status':'GATE_FAILED'}
 X=R[:,:4];Y=R[:,4];b=np.linalg.lstsq(X,Y,rcond=None)[0];C=X[:,1:];rx=X[:,0]-C@np.linalg.lstsq(C,X[:,0],rcond=None)[0];ry=Y-C@np.linalg.lstsq(C,Y,rcond=None)[0];assert np.isclose(b[0],rx@ry/(rx@rx));return {**out,'status':'FIT','P100_beta':float(b[0]),'partial_R2':float((rx@ry)**2/(rx@rx)/(ry@ry)),'coefficients':dict(zip(V,map(float,b)))}
marine={}
for name,t in [('annual',v[v.duration.eq(1)]),('one_to_five',v)]:
 f=fit(t);f['before_repeat_gate']={'n':len(t),'sites':int(t.site_id.nunique()),'site_ids':sorted(t.site_id.unique().tolist())};f['deletions']={k:{str(x):fit(t[t[k]!=x]) for x in sorted(t[k].unique())} for k in ['region','site_id','block']} if f['status']=='FIT' else None
 marine[name]=f
res={'contract':'feb248795020a94d12a77b14f644295e87361388','source_pins':PINS,'support':{'strict_all':112,'strict_1993_2020':85,'adjacent_intervals':55,'interval_sites':7,'climate_excluded':excluded,'climate_valid':len(v)},'network':network,'marine':marine,'limitations':['Observed gains/losses in changing measured rosters, not individual relocation; cross-site references differ in all secondary windows.','Same site/year/vantage/citation does not prove same census day, coverage or identical realized marine niche.','No new ecological causal or forecasting claims; existing source only.']}
(OUT/'result.json').write_text(json.dumps(res,indent=2)+'\n');v.to_csv(OUT/'marine_support.csv',index=False);print(json.dumps({'support':res['support'],'network':{k:{'summary':z['summary'],'windows':z['windows'],'year_delete_means':{y:x['mean_paired_difference'] for y,x in z['omit_year'].items()},'site_delete_means':{s:x['mean_paired_difference'] for s,x in z['omit_site'].items()}} for k,z in network.items()},'marine':marine},indent=2))
