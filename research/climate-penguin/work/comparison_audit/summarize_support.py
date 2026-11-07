from pathlib import Path
import pandas as pd, numpy as np, json
R=Path(__file__).resolve().parents[2];O=R/'outputs/comparison_audit'
p=pd.read_csv(O/'mapppd_unambiguous_site_seasons.csv');t=pd.read_csv(O/'mapppd_trajectory_inventory.csv');it=pd.read_csv(O/'mapppd_intervals.csv');n=pd.read_csv(O/'mapppd_contemporaneous_neighbor_support.csv')
pg=['ADPE','CHPE','GEPE'];p=p[p.species_id.isin(pg)];t=t[t.species_id.isin(pg)];it=it[it.species_id.isin(pg)]
eligible=t[(t.n_seasons>=5)&(t.span>=10)]
strict=t[(t.n_seasons>=10)&(t.span>=20)]
eligible.to_csv(O/'candidate_series.csv',index=False)
ov=[]
for a,b in [('ADPE','CHPE'),('ADPE','GEPE'),('CHPE','GEPE')]:
    paired=p[p.species_id==a].merge(p[p.species_id==b],on=['site_id','season'],suffixes=('_a','_b'))
    ov.append(dict(species_a=a,species_b=b,shared_sites=paired.site_id.nunique(),shared_site_seasons=len(paired),sites_ge5_shared_seasons=int((paired.groupby('site_id').size()>=5).sum())))
pd.DataFrame(ov).to_csv(O/'mapppd_species_overlap.csv',index=False)
it=it.merge(n,left_on=['site_id','species_id','start'],right_on=['site_id','species_id','season'],how='left',validate='many_to_one')
rows=[]
for s,g in it.groupby('species_id'):
    g=g[(g.gap==1)&g.same_known_method&(g.n_start>0)&(g.n_end>0)]
    rows.append(dict(species_id=s,annual_positive_same_method_intervals=len(g),sites=g.site_id.nunique(),with_1_neighbor_50km=int((g.neighbors_50km>=1).sum()),with_3_neighbors_50km=int((g.neighbors_50km>=3).sum()),with_1_neighbor_100km=int((g.neighbors_100km>=1).sum())))
pd.DataFrame(rows).to_csv(O/'mapppd_growth_neighbor_support.csv',index=False)
state=pd.read_csv(O/'mapppd_state_intervals.csv');state=state[state.species_id.isin(pg)]
z=state[(state.state_start==0)&(state.state_end==1)]
z.to_csv(O/'mapppd_reappearance_intervals.csv',index=False)
rez={'pygoscelis_unambiguous_site_seasons':len(p),'pygoscelis_sites':p.site_id.nunique(),'candidate_series':len(eligible),'candidate_sites':eligible.site_id.nunique(),'strict_series':len(strict),'strict_sites':strict.site_id.nunique(),'consistent_state_zero_positive_intervals':len(z),'zero_positive_sites':z.site_id.nunique(),'annual_zero_positive_intervals':int((z.gap==1).sum()),'annual_zero_positive_sites':z.loc[z.gap==1,'site_id'].nunique()}
# Match the four focal Palmer sites to explicit public IDs; census IDs are separate namespaces.
sites=pd.read_csv(R/'work/data_audit/mapppdr/sites.csv')
sel=sites[sites.site_name.isin(['Litchfield Island','Christine Island','Cormorant Island','Humble Island','Torgersen Island'])].copy()
lit=sel[sel.site_name=='Litchfield Island'].iloc[0]
lat1=np.radians(lit.latitude);lat2=np.radians(sel.latitude.to_numpy());dl=np.radians(sel.longitude.to_numpy()-lit.longitude)
sel['geodesic_km_from_litchfield']=6371*2*np.arcsin(np.sqrt(np.clip(np.sin((lat2-lat1)/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin(dl/2)**2,0,1)))
sel.to_csv(O/'palmer_site_coordinates.csv',index=False)
(O/'support_summary.json').write_text(json.dumps(rez,indent=2))
print(json.dumps(rez));print(pd.DataFrame(ov).to_string(index=False));print(pd.DataFrame(rows).to_string(index=False));print(z[z.gap==1].to_string(index=False));print(sel.to_string(index=False))
balanced=[]
for (species,region),g in p.groupby(['species_id','region']):
    for length in [5,10]:
        for start in range(max(1980,int(g.season.min())),int(g.season.max())-length+2):
            sub=g[g.season.between(start,start+length-1)]
            support=sub.groupby('site_id').agg(n=('season','nunique'),methods=('method','nunique'),method=('method','first'))
            ok=support[(support.n==length)&(support.methods==1)&(~support.method.str.contains('unknown|\\|',regex=True))].index
            if len(ok)>=2:balanced.append(dict(species_id=species,region=region,start=start,end=start+length-1,n_years=length,n_sites=len(ok),site_ids=';'.join(sorted(ok))))
bal=pd.DataFrame(balanced);bal.to_csv(O/'mapppd_balanced_windows.csv',index=False)
best=bal.sort_values(['n_sites','end'],ascending=False).groupby(['species_id','n_years']).head(1)
print('BEST BALANCED WINDOWS');print(best.to_string(index=False))
