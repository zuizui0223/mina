"""Frozen geographic transfer: contract 0dab128, no outcome-dependent candidate selection."""
import json, hashlib, zipfile, sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(sys.argv[1]); OUT=Path(sys.argv[2]); OUT.mkdir(parents=True,exist_ok=True)
PINS={14935924098:'fbeeffce21a8323f8f9afa75986b6d3cc05d7d66053ee872a43a39d7251b0e06',13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',14926710177:'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8',13829236358:'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5'}
def get(i):
 p=ROOT/f'github-actions-artifact-{i}.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==PINS[i]; z=zipfile.ZipFile(p); assert z.testzip() is None; return z
with get(14935924098) as z:
 raw=z.read('985565_v1_global_seabird_breeding_success.csv');assert hashlib.sha256(raw).hexdigest()=='1f1f7c0b6aeb4d9f4ae5288edea9b668666fcbc25bfa93c607229ec9d317c6e3';b=pd.read_csv(z.open('985565_v1_global_seabird_breeding_success.csv'))
with get(13669533413) as z:a=pd.read_csv(z.open('panantarctic_595_site_inventory.csv'))
with get(14926710177) as z:p=pd.read_csv(z.open('winter_595.csv'))
with get(13829236358) as z:h=pd.read_csv(z.open('original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv'))
assert len(b)==6602 and len(a)==595 and a.site_id.is_unique
MAPPING={'Admiralty Bay':['LLAN','PTHO','DEMA','UCHA'],'Cape Shirreff':['SHIR'],'Palmer':['TORG','HUMB','LITC','CHIS','CORM'],'Signy':['MLGE','PANT','OLIC','OUTE','PAGE','GOPT','CONF','PAND','PORT','SPRO'],'Pointe Geologie':['PGEO']}
SPEC={'Pygoscelis adeliae':'ADPE','Pygoscelis antarcticus':'CHPE','Pygoscelis papua':'GEPE'}
YEARS=set(range(2004,2011))|set(range(2013,2021));VARS=['P100_pp','mean_source_SIC_pp','mean_GLORYS_salinity','mean_GLORYS_thetao_C']
P=p[(p.radius_km==100)&(p.n_valid_months==5)].copy();P['P100_pp']=100*P.direct_DEEPAA_coastal_polynya_fraction
H=h[(h.original_source_4_OSISAF_months==4)&(h.original_source_4_GLORYS_months==4)]
cl=P[['site_id','season','P100_pp']].rename(columns={'season':'year'}).merge(H[['site_id','year',*VARS[1:]]],on=['site_id','year'],validate='one_to_one');cl=cl[cl.year.isin(YEARS)]
assert len(cl)==588*15 and cl[VARS].notna().all().all()
q=b[b.site.isin(MAPPING)&b.ScientificName_accepted.isin(SPEC)&b.year.isin(YEARS)&b.breeding_success.notna()].copy();q['species']=q.ScientificName_accepted.map(SPEC);q['response']=q.breeding_success
assert not q.duplicated(['site','species','year']).any() and q.response.between(0,2).all()
# Verify fixed candidate sets against source coordinates, not outcomes.
exposures={};distances={};rows=[]
for site,ids in MAPPING.items():
 g=q[q.site==site];assert g[['latitude','longitude']].drop_duplicates().shape[0]==1
 lat,lon=g.iloc[0][['latitude','longitude']];l1,l2=np.deg2rad(a.latitude),np.deg2rad(lat);delta=np.deg2rad(a.longitude-lon);dist=2*6371.0088*np.arcsin(np.sqrt(np.sin((l1-l2)/2)**2+np.cos(l1)*np.cos(l2)*np.sin(delta/2)**2))
 assert set(a.loc[dist<=5,'site_id'])==set(ids)
 distances[site]={i:float(dist[a.site_id==i].iloc[0]) for i in ids}
 x=cl[cl.site_id.isin(ids)];assert len(x)==15*len(ids) and x.groupby('site_id').year.nunique().eq(15).all()
 exposures[site]=x.groupby('year')[VARS].mean().reset_index()
 rows.append(g[['site','species','year','response']].merge(exposures[site],on='year',validate='many_to_one'))
d=pd.concat(rows,ignore_index=True);print(d.groupby(["site","species"]).size().to_string());assert len(d)==127 and len(d[d.site!="Pointe Geologie"])==112
# Standardized predictor condition number, and FWL check.
def fit(g,adjust=False):
 n=len(g);ctrl=['year']+(VARS[1:] if adjust else []);x=g.P100_pp.to_numpy(float);y=g.response.to_numpy(float);C=g[ctrl].to_numpy(float);Z=np.column_stack([C,x]);sd=Z.std(axis=0)
 df=n-Z.shape[1]-1
 if np.any(sd==0):return {'n':n,'residual_df':df,'status':'ZERO_VARIANCE'}
 cond=float(np.linalg.cond((Z-Z.mean(axis=0))/sd));A=np.column_stack([np.ones(n),C-C.mean(axis=0)]);X=np.column_stack([A,x]);rank=int(np.linalg.matrix_rank(X))
 if df<5 or rank<X.shape[1] or cond>30:return {'n':n,'residual_df':df,'condition':cond,'status':'GATE_FAILED'}
 beta=np.linalg.lstsq(X,y,rcond=None)[0][-1];rx=x-A@np.linalg.lstsq(A,x,rcond=None)[0];ry=y-A@np.linalg.lstsq(A,y,rcond=None)[0];assert np.isclose(beta,rx@ry/(rx@rx),rtol=1e-9,atol=1e-11)
 return {'status':'FIT','n':n,'beta':float(beta),'partial_R2':float((rx@ry)**2/(rx@rx)/(ry@ry)),'residual_df':df,'condition':cond,'P_residual_sd_pp':float(rx.std()),'P_min_max':[float(x.min()),float(x.max())]}
def analyze(g,site):
 r={}
 for adj,key in [(False,'time'),(True,'time_hydro')]:
  f=fit(g,adj);f['leave_year']={str(int(y)):fit(g[g.year!=y],adj) for y in sorted(g.year.unique())}
  f['candidate_fits']={i:fit(g[['year','response']].merge(cl.loc[cl.site_id==i,['year',*VARS]],on='year',validate='one_to_one'),adj) for i in MAPPING[site]}
  r[key]=f
 return r
series={f'{site}|{sp}':analyze(g,site) for (site,sp),g in d.groupby(['site','species'])}
external=['Admiralty Bay','Palmer','Signy'];transfer={}
for key,adj in [('time',False),('time_hydro',True)]:
 z={s:series[s+'|ADPE'][key] for s in external};assert all(v['status']=='FIT' for v in z.values())
 means={s:float(np.mean([v['beta'] for t,v in z.items() if s!=t])) for s in external}
 leave_global={str(y):float(np.mean([fit(d[(d.site==s)&(d.species=='ADPE')&(d.year!=y)],adj)['beta'] for s in external])) for y in sorted(YEARS)}
 transfer[key]={'equal_site_mean':float(np.mean([v['beta'] for v in z.values()])),'leave_site_means':means,'leave_global_year_means':leave_global,'all_sites_positive':all(v['beta']>0 for v in z.values()),'all_site_year_omissions_positive':all(f['status']=='FIT' and f['beta']>0 for v in z.values() for f in v['leave_year'].values()),'all_candidates_positive':all(f['status']=='FIT' and f['beta']>0 for v in z.values() for f in v['candidate_fits'].values())}
contrasts={}
for site,base in [('Admiralty Bay','ADPE'),('Signy','ADPE'),('Cape Shirreff','CHPE'),('Signy','CHPE')]:
 g=d[d.site==site];v=g.pivot(index='year',columns='species',values='response');r=(v.GEPE-v[base]).dropna().rename('response').reset_index().merge(exposures[site],on='year',validate='one_to_one');contrasts[f'{site}|GEPE-{base}']=analyze(r,site)
result={'contract':'0dab128cda1d9cc1d52db69ef9d4badcdcf51c5d','source_pins':PINS,'status':'EXPLORATORY_GEOGRAPHIC_TRANSFER','external_sites':4,'external_series':8,'external_observed_species_years':112,'candidate_mapping':MAPPING,'candidate_distance_km':distances,'series':series,'ADPE_transfer':transfer,'matched_species_contrasts':contrasts,'limitations':['Geographic transfer, not verified independent source-event lineage. BCO outcome compilation may share underlying monitoring with previous Signy/Cape studies.','Equal mean of nearby atlas centre exposure estimates is a regional proxy; no verified common biological footprint.','Few years and regions; deletion ranges descriptive, not confidence intervals. No causal mechanism, prediction or demographic forecast.']}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');d.to_csv(OUT/'matched_series.csv',index=False)
for group in ['series','matched_species_contrasts']:
 print(group)
 for k,v in result[group].items():
  print(k,[(m,r.get('n'),r.get('beta'),r.get('partial_R2'),r.get('condition'),[min(x['beta'] for x in r['leave_year'].values() if x['status']=='FIT'),max(x['beta'] for x in r['leave_year'].values() if x['status']=='FIT')],[min(x['beta'] for x in r['candidate_fits'].values() if x['status']=='FIT'),max(x['beta'] for x in r['candidate_fits'].values() if x['status']=='FIT')]) for m,r in v.items() if r['status']=='FIT'])
print('TRANSFER',json.dumps(transfer,indent=2))
