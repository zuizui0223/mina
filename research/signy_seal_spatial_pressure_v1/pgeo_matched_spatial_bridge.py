"""Same-year PGEO sea/productivity/allocation bridge. Frozen contract 830baf0."""
import sys,json,hashlib,zipfile
from pathlib import Path
from collections import defaultdict
import numpy as np,pandas as pd
from threadpoolctl import threadpool_limits
ROOT=Path(sys.argv[1]);OUT=Path(sys.argv[2]);OUT.mkdir(parents=True,exist_ok=True)
PINS={14987514463:'d67a47fa9c280da82ace6d471f1ea42a63fdc402f4b6aa6c0734ca68317632ab',14926710177:'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8',13829236358:'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5'}
def get(i):
 p=ROOT/f'github-actions-artifact-{i}.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==PINS[i];z=zipfile.ZipFile(p);assert z.testzip() is None;return z
with get(14987514463) as z:
 receipt=json.loads(z.read('receipt.json'));assert len(receipt['files'])==7
 for k,r in receipt['files'].items():assert hashlib.md5(z.read(k)).hexdigest()==r['md5'] and hashlib.sha256(z.read(k)).hexdigest()==r['sha256']
 d=pd.read_csv(z.open('raw_109_demo.csv'),sep=';',decimal=',')
with get(14926710177) as z:p=pd.read_csv(z.open('winter_595.csv'))
with get(13829236358) as z:h=pd.read_csv(z.open('original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv'))
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
a=pd.DataFrame(rows);valid=a[a.adults_complete&a.chicks_complete&a.adults.gt(0)&a.chicks.ge(0)&a.chicks.le(2*a.adults)].copy();end=a.loc[a.adults_complete,['colony_code','year','adults']].rename(columns={'adults':'next_adults'});end['year']-=1
v=valid.merge(end,on=['colony_code','year'],validate='one_to_one');assert len(v)==1035 and v.next_adults.ge(0).all()
P=p[(p.site_id=='PGEO')&(p.radius_km==100)&(p.n_valid_months==5)].copy();P['P100_pp']=P.direct_DEEPAA_coastal_polynya_fraction*100
H=h[(h.site_id=='PGEO')&(h.original_source_4_OSISAF_months==4)&(h.original_source_4_GLORYS_months==4)]
cl=P[['season','P100_pp']].rename(columns={'season':'year'}).merge(H[['year','mean_source_SIC_pp']],on='year',validate='one_to_one');assert len(cl)==15
q=v.merge(cl,on='year',validate='many_to_one');assert len(q)==699 and q.year.nunique()==12
q['B']=q.chicks/q.adults
years=sorted(q.groupby('year').island.nunique().loc[lambda x:x==3].index.tolist());assert years==[2004,2007,2008,2014,2017,2018,2019,2020]
c=q[q.year.isin(years)];roster=c.groupby('colony_code').year.nunique().loc[lambda x:x==len(years)].index;f=c[c.colony_code.isin(roster)].copy();assert len(c)==497 and len(f)==248 and len(roster)==31

def island_summary(g):
 p=g.adults.to_numpy(float);n=g.next_adults.to_numpy(float);b=g.B.to_numpy(float);assert p.sum()>0 and n.sum()>0
 p=p/p.sum();n=n/n.sum();ne=1/(p@p);ne1=1/(n@n)
 B=float(p@b);S=float((n-p)@b);D=float((ne1-ne)/len(g));assert abs(S-(n@b-p@b))<1e-12
 return {'n':len(g),'B':B,'S':S,'D':D,'N_eff':float(ne),'next_N_eff':float(ne1),'total_pairs':float(g.adults.sum()),'next_pairs':float(g.next_adults.sum())}
ig=pd.DataFrame([{'year':int(y),'island':i,**island_summary(g)} for (y,i),g in f.groupby(['year','island'])]);assert len(ig)==24

def annual(g):return g.groupby('year')[['B','S','D']].mean().reset_index().merge(cl,on='year',validate='one_to_one')
def exposure_fit(g,outcome):
 y=g[outcome].to_numpy(float);x=g.P100_pp.to_numpy(float);C=np.column_stack([np.ones(len(g)),g.year-g.year.mean()]);X=np.column_stack([C,x]);assert np.linalg.matrix_rank(X)==3
 b=np.linalg.lstsq(X,y,rcond=None)[0];rx=x-C@np.linalg.lstsq(C,x,rcond=None)[0];ry=y-C@np.linalg.lstsq(C,y,rcond=None)[0];assert np.isclose(b[-1],rx@ry/(rx@rx));return {'beta':float(b[-1]),'partial_R2':float((rx@ry)**2/((rx@rx)*(ry@ry))),'residual_df':len(g)-3,'P_residual_sd_pp':float(np.sqrt(np.mean(rx**2)))}
s=annual(ig);fits={}
for m in ['B','S','D']:
 r=exposure_fit(s,m);r['leave_year']=[{'omitted':int(y),**exposure_fit(s[s.year!=y],m)} for y in years];r['leave_island']=[{'omitted':i,**exposure_fit(annual(ig[ig.island!=i]),m)} for i in sorted(ig.island.unique())];fits[m]=r

def conditional(g):
 iy=g.island+':'+g.year.astype(str);A=pd.get_dummies(pd.DataFrame({'colony':g.colony_code,'iy':iy}),dtype=float).to_numpy();Z=np.column_stack([np.log1p(g.adults),g.B,np.log1p(g.next_adults)]);R=Z-A@np.linalg.lstsq(A,Z,rcond=None)[0];X=R[:,:2];Y=R[:,2];assert np.linalg.matrix_rank(X)==2
 b=np.linalg.lstsq(X,Y,rcond=None)[0];ry=Y-X[:,:1]@np.linalg.lstsq(X[:,:1],Y,rcond=None)[0];rx=X[:,1]-X[:,:1]@np.linalg.lstsq(X[:,:1],X[:,1],rcond=None)[0];assert np.isclose(b[-1],rx@ry/(rx@rx));return {'n':len(g),'units':int(g.colony_code.nunique()),'years':int(g.year.nunique()),'beta':float(b[-1]),'partial_R2':float(1-np.sum((Y-X@b)**2)/np.sum(ry**2))}
cf={}
with threadpool_limits(limits=1):
 for name,g in [('all_matched',q),('fixed',f)]:
  r=conditional(g);r['leave_year']=[{'omitted':int(y),**conditional(g[g.year!=y])} for y in sorted(g.year.unique())];r['leave_island']=[{'omitted':i,**conditional(g[g.island!=i])} for i in sorted(g.island.unique())];cf[name]=r
result={'contract':'830baf03952d673eae88154a65802730bf8592f7','status':'DESCRIPTIVE_MATCHED_SPATIAL_BRIDGE','pins':PINS,'support':{'all_transitions':len(v),'matched':len(q),'matched_units':int(q.colony_code.nunique()),'matched_years':int(q.year.nunique()),'common_island_rows':len(c),'fixed_rows':len(f),'fixed_units':len(roster),'fixed_roster':sorted(roster.tolist()),'years':years,'fixed_next_zero':int(f.next_adults.eq(0).sum())},'island_year':ig.to_dict('records'),'annual':s.to_dict('records'),'annual_mean_sorting':float(s.S.mean()),'positive_sorting_island_years':int(ig.S.gt(0).sum()),'positive_sorting_years':int(s.S.gt(0).sum()),'exposure_fits':fits,'conditional_fits':cf,'limitations':['Eight shared regional exposure years, three islands in one region, fixed observed subset only.','S is descriptive reweighting of previously observed productivity, not recruitment or actual movement. D is effective fraction, not area.','No SIC-adjusted annual fit (df4), mediation, causal or future projection.']}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');ig.to_csv(OUT/'island_year.csv',index=False);s.to_csv(OUT/'annual.csv',index=False)
print(json.dumps({**{k:v for k,v in result.items() if k not in ['island_year','exposure_fits','conditional_fits']},'exposure_fits':{k:{'beta':v['beta'],'partial_R2':v['partial_R2'],'year_range':[min(x['beta'] for x in v['leave_year']),max(x['beta'] for x in v['leave_year'])],'island_range':[min(x['beta'] for x in v['leave_island']),max(x['beta'] for x in v['leave_island'])]} for k,v in fits.items()},'conditional_fits':{k:{'beta':v['beta'],'partial_R2':v['partial_R2'],'year_range':[min(x['beta'] for x in v['leave_year']),max(x['beta'] for x in v['leave_year'])],'island_range':[min(x['beta'] for x in v['leave_island']),max(x['beta'] for x in v['leave_island'])]} for k,v in cf.items()}},indent=2))
