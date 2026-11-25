"""PGEO fixed-roster wetness × P100. Contract bb3fa02 before fitting."""
import hashlib,json,sys,zipfile
from pathlib import Path
from collections import defaultdict
import numpy as np,pandas as pd
ROOT=Path(sys.argv[1]);OUT=Path(sys.argv[2]);OUT.mkdir(parents=True,exist_ok=True)
PINS={14987514463:'d67a47fa9c280da82ace6d471f1ea42a63fdc402f4b6aa6c0734ca68317632ab',14926710177:'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8',13829236358:'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5'}
def get(i):
 p=ROOT/f'github-actions-artifact-{i}.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==PINS[i];z=zipfile.ZipFile(p);assert z.testzip() is None;return z
with get(14987514463) as z:
 receipt=json.loads(z.read('receipt.json'));assert len(receipt['files'])==7
 for k,r in receipt['files'].items():
  assert hashlib.md5(z.read(k)).hexdigest()==r['md5'] and hashlib.sha256(z.read(k)).hexdigest()==r['sha256']
 d=pd.read_csv(z.open('raw_109_demo.csv'),sep=';',decimal=',');env=pd.read_csv(z.open('env_variables.csv'),sep=';')
with get(14926710177) as z:p=pd.read_csv(z.open('winter_595.csv'))
with get(13829236358) as z:h=pd.read_csv(z.open('original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv'))
assert len(d)==3068 and d.colony_code.nunique()==83 and not d.duplicated(['colony','year']).any() and env.colony_code.is_unique
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
a=pd.DataFrame(rows);valid=a[a.adults_complete&a.chicks_complete&a.adults.gt(0)&a.chicks.ge(0)&a.chicks.le(2*a.adults)].copy()
P=p[(p.site_id=='PGEO')&(p.radius_km==100)&(p.n_valid_months==5)].copy();P['P100_pp']=100*P.direct_DEEPAA_coastal_polynya_fraction
H=h[(h.site_id=='PGEO')&(h.original_source_4_OSISAF_months==4)&(h.original_source_4_GLORYS_months==4)].copy()
cl=P[['season','P100_pp']].rename(columns={'season':'year'}).merge(H[['year','mean_source_SIC_pp','mean_GLORYS_thetao_C','mean_GLORYS_salinity']],on='year',validate='one_to_one');assert len(cl)==15
q=valid.merge(cl,on='year',validate='many_to_one');years=sorted(q.groupby('year').island.nunique().loc[lambda x:x==3].index.tolist());assert years==[2004,2005,2007,2008,2009,2014,2017,2018,2019,2020]
q=q[q.year.isin(years)].merge(env[['colony_code','twid']],on='colony_code',validate='many_to_one');assert len(q)==649 and q.twid.notna().all()
roster=q.groupby('colony_code').year.nunique().loc[lambda x:x==len(years)].index;f=q[q.colony_code.isin(roster)].copy();assert len(f)==330 and len(roster)==33
# Fixed scaling, independent of response. Group-specific centers use fixed-roster islands.
u=f[['colony_code','island','twid']].drop_duplicates();assert len(u)==33
u['w0']=u.twid-u.groupby('island').twid.transform('mean');scale=float(np.sqrt(np.mean(u.w0**2)));assert scale>0
f=f.merge(u[['colony_code','w0']],on='colony_code',validate='many_to_one');f['w']=f.w0/scale;f['r']=f.chicks/f.adults;q['r']=q.chicks/q.adults
cl=cl.set_index('year').loc[years].reset_index();
def annual_slopes(frame):
 rows=[]
 for y,g in frame.groupby('year'):
  x=g.w-g.groupby('island').w.transform('mean');r=g.r-g.groupby('island').r.transform('mean');den=float(x@x);assert den>0
  rows.append({'year':int(y),'wetness_slope':float(x@r/den),'n':len(g),'mean_chicks_per_pair':float(g.r.mean()),'sum_chicks_per_pair':float(g.chicks.sum()/g.adults.sum())})
 return pd.DataFrame(rows).merge(cl,on='year',validate='one_to_one')
def fit(df,adj=False):
 y=df.wetness_slope.to_numpy(float);x=df.P100_pp.to_numpy(float);controls=[df.year.to_numpy(float)-np.mean(df.year)]
 if adj:controls.append(df.mean_source_SIC_pp.to_numpy(float)-df.mean_source_SIC_pp.mean())
 C=np.column_stack([np.ones(len(df)),*controls]);X=np.column_stack([C,x]);assert np.linalg.matrix_rank(X)==X.shape[1]
 b=np.linalg.lstsq(X,y,rcond=None)[0];rx=x-C@np.linalg.lstsq(C,x,rcond=None)[0];ry=y-C@np.linalg.lstsq(C,y,rcond=None)[0];assert np.isclose(b[-1],rx@ry/(rx@rx));return {'beta':float(b[-1]),'partial_R2':float((rx@ry)**2/((rx@rx)*(ry@ry))),'P_residual_sd_pp':float(np.sqrt(np.mean(rx**2))),'residual_df':len(df)-X.shape[1]}
s=annual_slopes(f);res={'status':'EXPLORATORY_LAND_SEA_INTERACTION','contract':'bb3fa02691fce47ac1a3d942940b2fa97dfb74b5','pins':PINS,'years':years,'n_fixed_units':len(roster),'n_fixed_rows':len(f),'n_unbalanced_rows':len(q),'island_roster':{k:int(v) for k,v in u.island.value_counts().items()},'TWI_pooled_within_island_RMS':scale,'fixed_roster':sorted(roster.tolist()),'annual':s.to_dict('records'),'models':{}}
for adj,label in [(False,'time'),(True,'time_SIC')]:
 r=fit(s,adj);r['leave_year']=[{'omitted':int(y),**fit(s[s.year!=y],adj)} for y in years];r['leave_island']=[{'omitted':i,**fit(annual_slopes(f[f.island!=i]),adj)} for i in sorted(f.island.unique())];res['models'][label]=r
# Unbalanced sensitivity: same static standardized TWI; year and P interactions; colony and island-year FE; each year total weight one.
# Subtracting any fixed island-level mean from TWI does not change coefficients after island-year FE.
q['w']=q.twid/scale;q['wx']=q.w*q.P100_pp;q['wt']=q.w*(q.year-np.mean(years));q['iy']=q.island+':'+q.year.astype(str)
def unbalanced_fit(g):
 W=1/g.groupby('year').year.transform('size').to_numpy(float);sw=np.sqrt(W);D=pd.get_dummies(g[['colony_code','iy']],dtype=float).to_numpy();Y=g[['r','wx','wt']].to_numpy(float)*sw[:,None];A=D*sw[:,None];R=Y-A@np.linalg.lstsq(A,Y,rcond=None)[0];b=np.linalg.lstsq(R[:,1:],R[:,0],rcond=None)[0];assert np.linalg.matrix_rank(R[:,1:])==2;return {'beta':float(b[0]),'time_interaction':float(b[1])}
res['unbalanced_sensitivity']=unbalanced_fit(q);res['unbalanced_sensitivity']['leave_year']=[{'omitted':y,**unbalanced_fit(q[q.year!=y])} for y in years];a=res['models']['time'];b=res['models']['time_SIC'];res['directional_support']=a['beta']>0 and all(v['beta']>0 for v in a['leave_year']+a['leave_island']);res['SIC_robustness']=b['beta']>0 and all(v['beta']>0 for v in b['leave_year']);res['full_hydro']='not fitted: residual df 4 < 5';res['inference']='descriptive; 10 shared environmental years; no independent spatial climate exposure, no p-value or causal mechanism';(OUT/'result.json').write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n');s.to_csv(OUT/'annual_slopes.csv',index=False);print(json.dumps(res,indent=2))
