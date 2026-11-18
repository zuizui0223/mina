"""Nearest observed ice/open-water interface cell, not a return-trip distance."""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd,xarray as xr
from scipy.ndimage import binary_dilation
from scipy.spatial import cKDTree
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
EX=ROOT/'work/climate_penguin/ice_edge';EX.mkdir(exist_ok=True)
ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=0);args=ap.parse_args()
manifest=json.loads((OUT/'daily_concentration_manifest.json').read_text());items=[x for x in manifest if x['ok']]
if args.limit:items=items[:args.limit]
sites=pd.read_csv(OUT/'daily_ice_locations.csv');geo=Geod(ellps='WGS84')
def xyz(lon,lat):
    a=np.deg2rad(lon);b=np.deg2rad(lat)
    return np.column_stack([np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)])
points=xyz(sites.longitude.values,sites.latitude.values)
cross=np.array([[0,1,0],[1,1,1],[0,1,0]],dtype=bool)
for i,item in enumerate(items):
    out=EX/(item['date']+'.csv')
    if out.exists():continue
    with xr.open_dataset(ROOT/item['path']) as d:
        a=d.ice_conc.values[0];flag=d.status_flag.values[0];lat=d.lat.values;lon=d.lon.values
        f=np.where(np.isfinite(flag),flag,32767).astype(int)
        ocean=((f&3)==0)&np.isfinite(a)&np.isfinite(flag)
        records=[]
        for threshold in [15,30]:
            water=ocean&(a<threshold);ice=ocean&(a>=threshold)
            edge=ice&binary_dilation(water,structure=cross)
            ey,ex=np.where(edge)
            if len(ey):
                _,k=cKDTree(xyz(lon[edge],lat[edge])).query(points)
                destlon=lon[ey[k],ex[k]];destlat=lat[ey[k],ex[k]]
                az,_,dist=geo.inv(sites.longitude.values,sites.latitude.values,destlon,destlat)
            for j,s in sites.iterrows():
                records.append(dict(location_id=s.location_id,date=item['date'],threshold_percent=threshold,n_interface_cells=len(ey),nearest_interface_distance_km=float(dist[j]/1000) if len(ey) else None,interface_longitude=float(destlon[j]) if len(ey) else None,interface_latitude=float(destlat[j]) if len(ey) else None,interface_bearing_deg=float(az[j]) if len(ey) else None,interface_flag=int(f[ey[k[j]],ex[k[j]]]) if len(ey) else None))
    pd.DataFrame(records).to_csv(out,index=False)
    if (i+1)%100==0:print(i+1,'/',len(items),flush=True)
pd.concat([pd.read_csv(EX/(x['date']+'.csv')) for x in items],ignore_index=True).to_csv(OUT/'daily_ice_interface_distances.csv.gz',index=False,compression='gzip')
print('DONE',len(items),'days',flush=True)
