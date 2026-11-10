from pathlib import Path
import pandas as pd
import numpy as np
import json, hashlib, urllib.request

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/comparison_audit'; OUT.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'work/data_audit/mapppdr'
obs=pd.read_csv(DATA/'penguin_obs.csv')
sites=pd.read_csv(DATA/'sites.csv')
sp=pd.read_csv(DATA/'species.csv')
keys=['site_id','species_id','season']
nest=obs.loc[(obs.type=='nests') & obs['count'].notna() & obs.season.notna()].copy()
nest['season']=nest.season.astype(int)
# No averaging across conflicting sources, within-season dates, or methods.
groups=nest.groupby(keys)
checks=groups.agg(n_rows=('count','size'),n_counts=('count','nunique'),count_min=('count','min'),count_max=('count','max'),n_methods=('vantage','nunique')).reset_index()
checks.to_csv(OUT/'mapppd_duplicate_audit.csv',index=False)
# Presence audit can retain unequal positive counts, but rejects zero/positive disagreement.
states=checks[(checks.count_min>0)|(checks.count_max==0)].copy()
states['occupied']=(states.count_max>0).astype(int)
states=states.merge(sites,on='site_id',validate='many_to_one')
states.to_csv(OUT/'mapppd_consistent_observed_states.csv',index=False)
state_int=[]
for (sid,species),g in states.groupby(['site_id','species_id']):
    g=g.sort_values('season')
    for j in range(1,len(g)):
        a,b=g.iloc[j-1],g.iloc[j]
        state_int.append(dict(site_id=sid,species_id=species,start=int(a.season),end=int(b.season),gap=int(b.season-a.season),state_start=int(a.occupied),state_end=int(b.occupied)))
pd.DataFrame(state_int).to_csv(OUT/'mapppd_state_intervals.csv',index=False)
panel=checks[checks.n_counts==1].copy().rename(columns={'count_min':'count'})
panel=panel.merge(sites,on='site_id',validate='many_to_one')
panel['method']=panel.apply(lambda r:'|'.join(sorted(nest.loc[(nest.site_id==r.site_id)&(nest.species_id==r.species_id)&(nest.season==r.season),'vantage'].fillna('unknown').unique())),axis=1)
panel.to_csv(OUT/'mapppd_unambiguous_site_seasons.csv',index=False)
summ=[]; trajectories=[]; intervals=[]; episodes=[]
for (sid,species),g in panel.groupby(['site_id','species_id']):
    g=g.sort_values('season'); ys=g.season.to_numpy(); ns=g['count'].to_numpy()
    trajectories.append(dict(site_id=sid,species_id=species,site_name=g.site_name.iloc[0],region=g.region.iloc[0],n_seasons=len(g),first=int(ys.min()),last=int(ys.max()),span=int(ys.max()-ys.min()),zero_seasons=int((ns==0).sum()),years=';'.join(map(str,ys)),counts=';'.join(map(str,ns))))
    for j in range(1,len(g)):
        a=g.iloc[j-1]; b=g.iloc[j]
        intervals.append(dict(site_id=sid,species_id=species,region=b.region,site_name=b.site_name,start=int(a.season),end=int(b.season),gap=int(b.season-a.season),n_start=a['count'],n_end=b['count'],transition=('positive' if a['count']>0 else 'zero')+'_'+('positive' if b['count']>0 else 'zero'),same_known_method=a.method==b.method and a.method!='unknown',method_start=a.method,method_end=b.method))
    # A zero episode = observed zero following positive; missing seasons are not zeros.
    for j in range(1,len(g)):
        if ns[j]==0 and ns[j-1]>0:
            k=j
            while k+1<len(g) and ns[k+1]==0:k+=1
            episodes.append(dict(site_id=sid,species_id=species,site_name=g.site_name.iloc[0],last_positive=int(ys[j-1]),first_observed_zero=int(ys[j]),last_observed_zero=int(ys[k]),n_zero_visits=k-j+1,reappearance=int(ys[k+1]) if k+1<len(g) else None,last_observation=int(ys[-1]),continuous_zero_observations=bool(np.all(np.diff(ys[j:k+1])==1))))
traj=pd.DataFrame(trajectories); ints=pd.DataFrame(intervals); ep=pd.DataFrame(episodes)
traj.to_csv(OUT/'mapppd_trajectory_inventory.csv',index=False); ints.to_csv(OUT/'mapppd_intervals.csv',index=False); ep.to_csv(OUT/'mapppd_zero_episodes.csv',index=False)
for s,g in panel.groupby('species_id'):
    t=traj[traj.species_id==s]; it=ints[ints.species_id==s]; e=ep[ep.species_id==s]
    summ.append(dict(species_id=s,raw_nest_rows=int((nest.species_id==s).sum()),unique_site_seasons=len(g),sites=g.site_id.nunique(),first_season=int(g.season.min()),last_season=int(g.season.max()),ge5_span10=int(((t.n_seasons>=5)&(t.span>=10)).sum()),ge10_span20=int(((t.n_seasons>=10)&(t.span>=20)).sum()),adjacent_intervals=int((it.gap==1).sum()),adjacent_known_same_method=int(((it.gap==1)&it.same_known_method).sum()),zero_site_seasons=int((g['count']==0).sum()),zero_sites=g.loc[g['count']==0,'site_id'].nunique(),zero_episodes=len(e),episodes_with_reappearance=int(e.reappearance.notna().sum()),adjacent_positive_zero=int(((it.gap==1)&(it.transition=='positive_zero')).sum()),adjacent_zero_positive=int(((it.gap==1)&(it.transition=='zero_positive')).sum())))
pd.DataFrame(summ).merge(sp,on='species_id').to_csv(OUT/'mapppd_species_coverage.csv',index=False)
# Region/year panel support for source-population indices (observed only).
reg=panel.groupby(['species_id','region','season']).agg(sites=('site_id','nunique'),positive_sites=('count',lambda x:int((x>0).sum()))).reset_index()
reg.to_csv(OUT/'mapppd_region_season_coverage.csv',index=False)
# Distance here is geodesic lower bound, NOT a sea route; no landscape barrier claim.
f=panel[panel.species_id.isin(['ADPE','CHPE','GEPE'])].copy()
neigh=[]
for (s,y),g in f.groupby(['species_id','season']):
    for _,r in g.iterrows():
        others=g[(g.site_id!=r.site_id)&(g['count']>0)]
        lat1=np.radians(r.latitude); lat2=np.radians(others.latitude.to_numpy()); dl=np.radians(others.longitude.to_numpy()-r.longitude)
        d=6371*2*np.arcsin(np.sqrt(np.clip(np.sin((lat2-lat1)/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin(dl/2)**2,0,1)))
        z=dict(site_id=r.site_id,species_id=s,season=int(y),nearest_observed_positive_km=float(d.min()) if len(d) else None)
        for rad in [10,25,50,100]:z[f'neighbors_{rad}km']=int((d<=rad).sum())
        neigh.append(z)
pd.DataFrame(neigh).to_csv(OUT/'mapppd_contemporaneous_neighbor_support.csv',index=False)
summary=dict(raw_observations=len(obs),sites_in_registry=len(sites),raw_nest_rows=len(nest),nest_site_season_groups=len(checks),conflicting_count_groups=int((checks.n_counts>1).sum()),unambiguous_site_seasons=len(panel),negative_counts=int((nest['count']<0).sum()),presence_count_contradictions=int((((nest.presence==0)&(nest['count']>0))|((nest.presence==1)&(nest['count']==0))).sum()),year_season_differences=int((nest.year!=nest.season).sum()))
(OUT/'mapppd_audit_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary));print(pd.DataFrame(summ).to_string(index=False)); print('ZERO EPISODES');print(ep.to_string(index=False))
print('BINARY_STATE_CONFLICTS',len(checks)-len(states))
print(pd.DataFrame(state_int).groupby(['species_id','state_start','state_end']).agg(intervals=('gap','size'),annual=('gap',lambda x:int((x==1).sum()))).to_string())

url='https://pallter-data.marine.rutgers.edu/erddap/tabledap/AdeliePenguinCensus.csv?study_name,time,island_name,colony_code,num_breeding_pairs'
target=ROOT/'work/comparison_audit/palmer_census.csv'
if not target.exists():
    try:
        with urllib.request.urlopen(url,timeout=45) as response:target.write_bytes(response.read())
    except Exception as exc:print('PALMER_FETCH_FAILED',str(exc))
if target.exists():
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    p=pd.read_csv(target,skiprows=[1]);p['year']=pd.to_datetime(p.time).dt.year
    p['num_breeding_pairs']=pd.to_numeric(p.num_breeding_pairs,errors='coerce')
    p=p[p.island_name.isin(['CHR','COR','HUM','LIT','TOR'])]
    agg=p.groupby(['island_name','year']).agg(count=('num_breeding_pairs',lambda x:x.sum(min_count=len(x))),components=('colony_code','size')).reset_index()
    agg.to_csv(OUT/'palmer_five_island_counts.csv',index=False)
    print('PALMER',digest,len(p),agg.groupby('island_name').agg(n=('year','size'),first=('year','min'),last=('year','max')).to_string());print(agg[agg['count']==0].to_string(index=False))
    (OUT/'palmer_source.json').write_text(json.dumps(dict(url=url,sha256=digest,frozen_match=digest=='b4ef04e2275ea779fc8fe54fa13528dc2052d37dd88a60c811d54c7601f67b16'),indent=2))

manifest=[]
for path in list(DATA.glob('*'))+[ROOT/'work/comparison_audit/audit.py']+([target] if target.exists() else []):
    manifest.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
(OUT/'source_manifest.json').write_text(json.dumps(manifest,indent=2))
