from pathlib import Path
import pandas as pd,numpy as np,xarray as xr,json
from pyproj import Geod,CRS,Transformer
out=Path('outputs/ice_asymmetry');d=pd.read_csv('outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv');ids=pd.read_csv('outputs/comparison_audit/candidate_series.csv').query('species_id=="ADPE"').site_id;d=d[(d.species_id=='ADPE')&d.site_id.isin(ids)&d.season.between(1991,2020)]
g=d.groupby('site_id').season.agg(['count','min','max']);ids=g[(g['count']>=5)&((g['max']-g['min'])>=10)].index;d=d[d.site_id.isin(ids)];sites=d.drop_duplicates('site_id');sites[['site_id','site_name','region','latitude','longitude']].merge(g,left_on='site_id',right_index=True).to_csv(out/'osi_1991_2020_macro_cohort.csv',index=False)
files=json.loads((out/'osi_download_manifest.json').read_text());geo=Geod(ellps='WGS84');rows=[]
with xr.open_dataset(files[0]['file']) as z:lat=z.lat.values;lon=z.lon.values
mask={}
for _,s in sites.iterrows():
 dist=geo.inv(np.full(lon.shape,s.longitude),np.full(lat.shape,s.latitude),lon,lat)[2]/1000
 mask[s.site_id]=(dist>=100)&(dist<=500)
for item in files:
 if not item['ok']:continue
 with xr.open_dataset(item['file']) as z:
  flag=z.status_flag.values[0];dx=z.dX.values[0];dy=z.dY.values[0];l1=z.lat1.values[0];o1=z.lon1.values[0]
  azi,_,distance=geo.inv(lon,lat,o1,l1);north=distance*np.cos(np.deg2rad(azi))/1000;east=distance*np.sin(np.deg2rad(azi))/1000
  valid=np.isfinite(dx)&np.isfinite(dy);sat=valid&np.isin(flag,[20,21,22,30]);nominal=valid&(flag==30)
  for _,s in sites.iterrows():
   m=mask[s.site_id];k=m&sat
   rows.append(dict(site_id=s.site_id,region=s.region,year=item['year'],month=item['month'],n_grid=int(m.sum()),n_valid=int((m&valid).sum()),n_satellite=int(k.sum()),n_nominal=int((m&nominal).sum()),n_wind=int((m&valid&np.isin(flag,[23,24,25])).sum()),north_km_day=float(np.nanmean(north[k])) if k.any() else np.nan,east_km_day=float(np.nanmean(east[k])) if k.any() else np.nan))
r=pd.DataFrame(rows);r.to_csv(out/'osi_snapshot_spatial_support.csv',index=False)
# Nominal calendar-year join only: seasonal labels need source-date audit before fitting.
a=r.assign(phase=np.where(r.month<6,'apr_may','sep_oct')).groupby(['site_id','year','phase']).agg(months_with_satellite=('n_satellite',lambda x:int((x>0).sum())),north=('north_km_day','mean'),east=('east_km_day','mean')).reset_index();w=a.pivot(index=['site_id','year'],columns='phase',values=['months_with_satellite','north','east']);w.columns=['_'.join(x) for x in w.columns];w=w.reset_index();w['both_two_snapshots']=(w.months_with_satellite_apr_may==2)&(w.months_with_satellite_sep_oct==2);w.to_csv(out/'osi_snapshot_phase_screen.csv',index=False)
j=d[['site_id','season','region']].merge(w,left_on=['site_id','season'],right_on=['site_id','year'],how='left');print('cohort',len(sites),'records',len(d),'bothphaseswithall4sampledays',int(j.both_two_snapshots.sum()),'sites',j.loc[j.both_two_snapshots==True].site_id.nunique());print(j.groupby('region').agg(records=('site_id','size'),four_sample_days=('both_two_snapshots','sum')).to_string())
print('all120filesbytes',sum(x['bytes'] for x in files));print('snapshot_pairs',len(w),int(w.both_two_snapshots.sum()))
