import pandas as pd,itertools,json
from pathlib import Path
from pyproj import Geod
p=Path('outputs/macro_questions');d=pd.read_csv('outputs/comparison_audit/mapppd_intervals.csv');s=pd.read_csv('outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv').drop_duplicates('site_id').set_index('site_id');d=d[(d.gap==1)&(d.same_known_method==True)&(d.transition=='positive_positive')];geo=Geod(ellps='WGS84');rows=[]
for sp,ss in d.groupby('species_id'):
 sets=ss.groupby('site_id')['end'].apply(set)
 for a,b in itertools.combinations(sets.index,2):
  years=sets[a]&sets[b]
  if len(years)<5:continue
  aa=s.loc[a];bb=s.loc[b];km=geo.inv(aa.longitude,aa.latitude,bb.longitude,bb.latitude)[2]/1000
  rows.append(dict(species=sp,site_a=a,site_b=b,n_shared_annual_intervals=len(years),distance_km=km,shared_end_years=';'.join(map(str,sorted(years))),same_region=aa.region==bb.region))
r=pd.DataFrame(rows);r.to_csv(p/'synchrony_pair_support.csv',index=False)
for sp,g in r.groupby('species'):
 print(sp,'pairs5+',len(g),'sites',len(set(g.site_a)|set(g.site_b)),'pairs8+',sum(g.n_shared_annual_intervals>=8),'maxdistance8+',g[g.n_shared_annual_intervals>=8].distance_km.max(),'crossregion8+',sum((g.n_shared_annual_intervals>=8)&~g.same_region))
print('annual intervals',len(d))
