"""V26c direct GLORYS tile wet-grid geometry gate, no ecological model."""
import csv,io,json,hashlib,pathlib,sys,zipfile,math,statistics
from collections import Counter
import fsspec,numpy as np,pandas as pd,xarray as xr
from pyproj import Geod
from scipy.spatial import cKDTree
frame,oldgeo,oldmonthly,out=map(pathlib.Path,sys.argv[1:5]);out.mkdir(exist_ok=True,parents=True)
def get(p,h,n):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(p,'digest')
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        names=[x for x in z.namelist() if pathlib.PurePosixPath(x).name==n];assert len(names)==1
        return list(csv.DictReader(io.StringIO(z.read(names[0]).decode('utf-8-sig'))))
tiles=[x for x in get(frame,'13bfe5866a27f6fbfad681ed4a44d834f6019c663f94193e1039e96b81c22060','opportunity_tiles.csv') if x['band_km']=='5']
assert len(tiles)==1722 and len({r['tile'] for r in tiles})==1722
# Exact original source URL and source version used in previous marine audit.
store='https://s3.waw3-1.cloudferro.com/mdl-arco-time-025/arco/GLOBAL_MULTIYEAR_PHY_001_030/cmems_mod_glo_phy_my_0.083deg_P1M-m_202311/timeChunked.zarr'
ds=xr.open_zarr(fsspec.get_mapper(store),consolidated=True)
for k in ['latitude','longitude','elevation','time','so','thetao']:assert k in ds.variables
lat=np.asarray(ds.latitude.values);lon=np.asarray(ds.longitude.values)
assert lat.ndim==lon.ndim==1 and np.all(np.diff(lat)>0)
t=pd.DatetimeIndex(ds.time.values)
ix=np.flatnonzero((t.year==2011)&(t.month==9));assert len(ix)==1
depth=int(np.argmin(abs(ds.elevation.values)));assert abs(float(ds.elevation.values[depth])+0.49402499198913574)<1e-5
imax=int(np.flatnonzero(lat<=-53)[-1])
arr=np.asarray(ds.so.isel(time=int(ix[0]),elevation=depth,latitude=slice(0,imax+1)).load().values,dtype=float)
assert arr.shape==(imax+1,len(lon))
yi,xi=np.nonzero(np.isfinite(arr)&(arr>=20)&(arr<=42));assert len(yi)>500
def xyz(a,b):
    a=np.deg2rad(np.asarray(a,float));b=np.deg2rad(np.asarray(b,float))
    return np.column_stack((np.cos(a)*np.cos(b),np.cos(a)*np.sin(b),np.sin(a)))
tree=cKDTree(xyz(lat[yi],lon[xi]));geo=Geod(ellps='WGS84')
def mapping(places,la,lo):
    _,neighbors=tree.query(xyz([float(x[la]) for x in places],[float(x[lo]) for x in places]),k=12)
    out=[]
    for r,ids in zip(places,neighbors):
        _,_,dist=geo.inv(np.full(len(ids),float(r[lo])),np.full(len(ids),float(r[la])),lon[xi[ids]],lat[yi[ids]])
        order=np.lexsort((xi[ids],yi[ids],dist));k=int(ids[order[0]])
        out.append((int(yi[k]),int(xi[k]),float(dist[order[0]])/1000))
    return out
old=get(oldgeo,sys.argv[5],'all_original_595_sites_frozen_GLORYS_nearest_2011_September_wet_ocean_cells.csv')
assert len(old)==595
o=mapping(old,'colony_latitude','colony_longitude');matches=0;maxd=0.
for r,(a,b,d) in zip(old,o):
    assert (a,b)==(int(r['original_glorys_grid_y']),int(r['original_glorys_grid_x']))
    maxd=max(maxd,abs(d-float(r['true_geodesic_source_cell_distance_km'])))
    assert abs(d-float(r['true_geodesic_source_cell_distance_km']))<1e-5
    matches+=1
mapped=[]
for r,(a,b,d) in zip(tiles,mapping(tiles,'lat','lon')):
    mapped.append({**r,'wet_y':a,'wet_x':b,'wet_lat':float(lat[a]),'wet_lon':float(lon[b]),'distance_km':d,'eligible':int(d<=25)})
eligible=[r for r in mapped if r['eligible']]
points=sorted({(r['wet_y'],r['wet_x']) for r in eligible});lookup={p:i for i,p in enumerate(points)}
report={'status':'GEOMETRY_PASSED_PENDING_NATIVE_VALUE_PILOT','tiles':len(mapped),'eligible_tiles':len(eligible),'distinct_wet_cells':len(points),'blocks':len({r['block'] for r in eligible}),'old_595_exact_wet_cell_matches':matches,'old_max_distance_error_km':maxd,'distance_median_km':statistics.median(r['distance_km'] for r in mapped),'distance_max_km':max(r['distance_km'] for r in mapped),'groups':{g:{'tiles':sum(int(r['recorded_'+g]) for r in mapped),'eligible_tiles':sum(int(r['recorded_'+g]) for r in eligible)} for g in ('known','modern','ADPE','CHPE','GEPE')}}
(out/'geometry.json').write_text(json.dumps(report,indent=2));print('V26C_GEOMETRY='+json.dumps(report),flush=True)
with (out/'wet_tile_mapping.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(mapped[0]));w.writeheader();w.writerows(mapped)
months=np.flatnonzero((t.year==2011)&np.isin(t.month,[8,9,10,11]));assert len(months)==4
sel={'time':xr.DataArray(months,dims='month'),'latitude':xr.DataArray([p[0] for p in points],dims='wet_cell'),'longitude':xr.DataArray([p[1] for p in points],dims='wet_cell'),'elevation':depth}
vv={}
for name in ('so','thetao'):
    data=np.asarray(ds[name].isel(**sel).load().transpose('month','wet_cell').values,dtype=float)
    assert data.shape==(4,len(points));vv[name]=data
    print('V26C_NATIVE='+json.dumps({'var':name,'finite':int(np.isfinite(data).sum()),'cells':len(points)}),flush=True)
oldrows=get(oldmonthly,'247204637096ae7659f16286b43c75f3801dc9068f619bc3446df5f0438061d9','all_original_eligible_colony_GLORYS12_1993_2020_AugNov_monthly.csv')
n=0;err=0.
for r in oldrows:
    if r['year']!='2011' or r['month'] not in ('8','9','10','11') or not r['surface_GLORYS_salinity'] or not r['surface_GLORYS_thetao_C']:continue
    k=(int(r['source_original_wet_grid_y']),int(r['source_original_wet_grid_x']))
    if k not in lookup:continue
    j=int(r['month'])-8;i=lookup[k]
    for name,field in [('so','surface_GLORYS_salinity'),('thetao','surface_GLORYS_thetao_C')]:
        d=abs(float(vv[name][j,i])-float(r[field]));assert d<=1e-5,(name,k,j,d)
        err=max(err,d);n+=1
assert n>0
records=[]
for r in mapped:
    for j,m in enumerate((8,9,10,11)):
        i=lookup.get((r['wet_y'],r['wet_x'])) if r['eligible'] else None
        a,b=(float(vv['so'][j,i]),float(vv['thetao'][j,i])) if i is not None else (None,None)
        ok=a is not None and math.isfinite(a) and math.isfinite(b) and 20<=a<=42 and -4<=b<=25
        records.append({'tile':r['tile'],'year':2011,'month':m,'sss':a if ok else None,'sst_C':b if ok else None})
with (out/'native_pilot.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
report.update(status='GEOMETRY_AND_NATIVE_PILOT_PASSED',source_old_value_checks=n,max_old_value_difference=err,valid_tile_months=sum(r['sss'] is not None for r in records))
(out/'result.json').write_text(json.dumps(report,indent=2));print('V26C_RESULT='+json.dumps(report),flush=True)
