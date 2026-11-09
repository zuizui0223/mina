"""Empirical scenario lengths from matched local survey cells, before examining winners."""
from pathlib import Path
from itertools import combinations
import io, zipfile, hashlib, json
import numpy as np
import pandas as pd
from pyproj import Geod
from scipy.spatial import cKDTree

out=Path('outputs/krill_shift_pairs')
prior=Path('work/circuit_share');grid=np.load(prior/'grid.npz')
lat,lon=grid['lat'],grid['lon']
def xyz(x,y):
    a,b=np.radians(x),np.radians(y)
    return np.column_stack((np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)))
with zipfile.ZipFile('work/highice_prey/krillbase.zip') as z:
    with zipfile.ZipFile(io.BytesIO(z.read(z.namelist()[0]))) as k:
        payload=k.read('krillbase_data.csv')
h=pd.read_csv(io.BytesIO(payload),encoding='cp1252')
density='STANDARDISED_KRILL_UNDER_1M2';dt=pd.to_datetime(h.DATE,dayfirst=True,errors='coerce',format='%d/%m/%Y')
h=h[h.RECORD_TYPE.eq('haul') & h.DATE_ACCURACY.isin(['D','M']) & dt.dt.month.isin([1,2]) & h[density].ge(0)].copy()
h['summer']=dt.loc[h.index].dt.year
tree=cKDTree(xyz(lon.ravel(),lat.ravel()));_,h['cell']=tree.query(xyz(h.LONGITUDE,h.LATITUDE))
dyads=pd.read_csv('outputs/circuit_share_forecast/dyads.csv').drop_duplicates(['A','B'])
geod=Geod(ellps='WGS84');rows=[]
for region,g in dyads.groupby('region'):
    mask=np.zeros(lat.shape,bool)
    for key in g.key:
        spec=np.load(prior/key/'spec.npz');i,j,k,l=spec['cut'];mask[i:j,k:l]|=spec['mask']
    v=h[h.cell.isin(np.flatnonzero(mask))].copy()
    for gear,gear_data in v.groupby('NET_TYPE'):
        layers=gear_data.groupby(['cell','summer'])[density].mean().unstack()
        for year in layers.columns:
            if year+1 not in layers:continue
            common=layers[[year,year+1]].dropna()
            if len(common)<5 or common.sum().min()<=0:continue
            xy=xyz(lon.ravel()[common.index],lat.ravel()[common.index])
            coords=[]
            for col in common:
                x,y,z=np.average(xy,axis=0,weights=common[col]);coords.append((np.degrees(np.arctan2(y,x)),np.degrees(np.arctan2(z,np.hypot(x,y)))))
            bearing,_,dist=geod.inv(*coords[0],*coords[1])
            rows.append(dict(region=region,gear=gear,summer=year,next_summer=year+1,common_cells=len(common),km=dist/1000,bearing_deg=bearing,lon0=coords[0][0],lat0=coords[0][1],lon1=coords[1][0],lat1=coords[1][1]))
t=pd.DataFrame(rows);t.to_csv(out/'empirical_shifts.csv',index=False)
print(t.groupby('region').km.agg(['count','median',lambda a:a.quantile(.75),'max']));print(t.groupby(['region','gear']).size());print(hashlib.sha256(payload).hexdigest())
