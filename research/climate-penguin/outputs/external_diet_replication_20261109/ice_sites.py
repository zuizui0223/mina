from pathlib import Path
import netCDF4 as nc,numpy as np,pandas as pd
from pyproj import Geod
out=Path('outputs/cape_diet_replication');raw=Path('work/climate_penguin/osi_concentration')
sites={'Cape_Shirreff':(-62.4575,-60.7874),'Stranger_Point':(-62-16/60,-58-37/60),'ASPA128':(-62-10/60,-58-30/60)}
rows=[]; masks={}
for year in range(1995,2015):
 for d in pd.date_range(f'{year}-08-01',f'{year}-11-30'):
  with nc.Dataset(raw/f'ice_conc_sh_ease2-250_cdr-v3p1_{d:%Y%m%d}1200.nc') as ds:
   if not masks:
    lat=ds['lat'][:].data;lon=ds['lon'][:].data
    for name,(y,x) in sites.items():
     dist=Geod(ellps='WGS84').inv(lon,lat,np.full_like(lon,x),np.full_like(lat,y))[2];masks[name]=np.where(dist<100000)
   a=ds['ice_conc'][0];f=ds['status_flag'][0]
   for name,idx in masks.items():
    v=a[idx];flag=f[idx];ocean=(~np.ma.getmaskarray(flag)) & ((np.asarray(flag).astype(int)&3)==0);valid=ocean & ~np.ma.getmaskarray(v); assert valid.any() and valid.sum()>=.8*ocean.sum()
    rows.append([d,name,valid.sum(),float(v[valid].mean())])
df=pd.DataFrame(rows,columns=['date','site','valid_pixels','sic']);df.to_csv(out/'daily_sites.csv',index=False); a=df.groupby(['site',df.date.dt.year,df.date.dt.month]).sic.mean().groupby(level=[0,1]).mean(); a.index.names=['site','start_year'];a.to_csv(out/'historical_ice.csv');print(a.groupby(level=0).quantile(.75))
