"""V31b direct native CMIP6 physical atlas, one fixed model per job."""
import csv,io,json,hashlib,pathlib,sys,zipfile,math,urllib.request,gc
from collections import defaultdict
import numpy as np
import fsspec,xarray as xr
from pyproj import Geod
from scipy.spatial import cKDTree
gate,frame,out=map(pathlib.Path,sys.argv[1:4]);model=sys.argv[4];out.mkdir(parents=True,exist_ok=True)
def rz(p,h):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(p,'digest')
    z=zipfile.ZipFile(p);assert z.testzip() is None;return z
def member(z,n):
    a=[s for s in z.namelist() if pathlib.PurePosixPath(s).name==n];assert len(a)==1,(n,a)
    return z.read(a[0])
def read(z,n):return list(csv.DictReader(io.StringIO(member(z,n).decode('utf-8-sig'))))
gz=rz(gate,'9b30ce7d9ed05c12d723b82a9b1951bf80ad4078d5de8636542425927afb23ee')
fz=rz(frame,'13bfe5866a27f6fbfad681ed4a44d834f6019c663f94193e1039e96b81c22060')
receipt=json.loads(member(gz,'receipt.json'));assert receipt['status']=='ALL_THREE_MODEL_METADATA_READY'
stores={(r['variable_id'],r['experiment_id']):r for r in receipt['stores'] if r['source_id']==model}
models={'ACCESS-CM2':'r1i1p1f1','BCC-CSM2-MR':'r1i1p1f1','CESM2':'r4i1p1f1'}
assert len(stores)==9 and all(r['status']=='verified_metadata' and r['member_id']==models[model] for r in stores.values())
tiles=[r for r in read(fz,'opportunity_tiles.csv') if r['band_km']=='5'];assert len(tiles)==1722 and len({r['tile'] for r in tiles})==1722
V=('siconc','sos','tos');E=('historical','ssp245','ssp585');M=(8,9,10,11)
periods={'historical':[(1995,2014)],'ssp245':[(2041,2060),(2081,2100)],'ssp585':[(2041,2060),(2081,2100)]}
def dump(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def arrayhash(a):return hashlib.sha256(np.ascontiguousarray(a,dtype='<f8').tobytes()).hexdigest()
def normalize(a,v,units):
    a=np.asarray(a,dtype=np.float64)
    if v=='siconc':
        assert units in ('%','percent','percentage','1','fraction')
        if units in ('1','fraction'):a*=100
    elif v=='sos':assert units in ('0.001','psu','1e-3','1.e-3','g kg-1','g/kg')
    elif v=='tos':
        assert units in ('K','kelvin','degC','degrees_C','degree_Celsius','degrees_Celsius')
        if units in ('K','kelvin'):a-=273.15
    return a
def validity(a,v):
    finite=np.isfinite(a)
    if v=='siconc':return finite&(a>=-.001)&(a<=100.001)
    if v=='sos':return finite&(a>0)&(a<=50)
    return finite&(a>=-5)&(a<=45)
def xyz(lat,lon):
    a=np.deg2rad(np.asarray(lat,float));b=np.deg2rad(np.asarray(lon,float))
    return np.column_stack((np.cos(a)*np.cos(b),np.cos(a)*np.sin(b),np.sin(a)))
def extract(v,e):
    r=stores[v,e];url=r['zstore'].replace('gs://','https://storage.googleapis.com/').rstrip('/')
    with urllib.request.urlopen(url+'/.zmetadata',timeout=60) as f:raw=f.read(10000001)
    assert len(raw)<=10000000 and hashlib.sha256(raw).hexdigest()==r['metadata_sha256'],(v,e,'source metadata changed')
    print('V31B_OPEN='+json.dumps({'model':model,'var':v,'experiment':e,'url':url}),flush=True)
    with xr.open_zarr(fsspec.get_mapper(url,client_kwargs={'trust_env':True}),consolidated=True,chunks=None,decode_times=xr.coders.CFDatetimeCoder(use_cftime=True)) as ds:
        da=ds[v];dims=tuple(d for d in da.dims if d!='time')
        assert len(dims)==2 and da.dims[0]=='time'
        la=next(k for k in ('latitude','lat','nav_lat') if k in ds)
        lo=next(k for k in ('longitude','lon','nav_lon') if k in ds)
        lat,lon=xr.broadcast(ds[la],ds[lo])
        lat=np.asarray(lat.transpose(*dims).values,float)
        rawlon=np.asarray(lon.transpose(*dims).values,float)
        geo_valid=np.isfinite(lat)&(abs(lat)<=90)&np.isfinite(rawlon)&(abs(rawlon)<=360)
        invalid_geographic_centers=int((~geo_valid).sum())
        lat=np.where(geo_valid,lat,np.nan);lon=np.where(geo_valid,(rawlon+180)%360-180,np.nan)
        assert lat.shape==lon.shape==tuple(da.shape[1:])
        for k,expected in [('source_id',model),('experiment_id',e),('variant_label',models[model])]:
            if k in ds.attrs:assert ds.attrs[k]==expected,(k,ds.attrs[k],expected)
        if e!='historical' and ds.attrs.get('parent_variant_label'):assert ds.attrs['parent_variant_label']==models[model]
        times=list(ds.time.values)
        expected=[(y,m) for a,b in periods[e] for y in range(a,b+1) for m in M]
        ix=[i for i,t in enumerate(times) if (int(t.year),int(t.month)) in set(expected)]
        got=[(int(times[i].year),int(times[i].month)) for i in ix]
        assert got==expected and len(set(got))==len(expected),(v,e,len(got))
        # Only needed seasonal months; each native time chunk read once in this variable/experiment.
        a=normalize(da.isel(time=ix).values,v,da.attrs.get('units',''))
        assert a.shape==(len(expected),*lat.shape)
        meta={'variable':v,'experiment':e,'url':url,'metadata_sha256':r['metadata_sha256'],'invalid_geographic_centers':invalid_geographic_centers,'lat_sha256':arrayhash(lat),'lon_sha256':arrayhash(lon),'shape':list(lat.shape),'months':len(expected),'calendar':str(getattr(times[ix[0]],'calendar','unknown')),'units':da.attrs.get('units',''),'tracking_id':ds.attrs.get('tracking_id'),'parent_variant_label':ds.attrs.get('parent_variant_label')}
    print('V31B_READ='+json.dumps({**meta,'model':model}),flush=True)
    return lat,lon,a,expected,meta
hist={};histgeo={};metas=[];base_lat=base_lon=None;geometry_checks=[]
assert model=='CESM2'
for v in V:
    la,lo,a,keys,meta=extract(v,'historical')
    if base_lat is None:base_lat,base_lon=la,lo
    else:
        assert la.shape==base_lat.shape
        f=np.isfinite(la)&np.isfinite(lo)&(abs(la)<=90)
        bf=np.isfinite(base_lat)&np.isfinite(base_lon)&(abs(base_lat)<=90)
        south=(f&(la<-45))|(bf&(base_lat<-45))
        # Only common valid centers can enter the native joint ocean mask.
        # The prior coordinate audit showed all 3990 unmatched southern centers are absent from SIC geography.
        assert int((south&(f!=bf)).sum())==3990 and not np.any(south&bf&~f)
        assert int((f&bf&south).sum())==16810
        m=f&bf&south
        gd=Geod(ellps='WGS84')
        _,_,d=gd.inv(base_lon[m],base_lat[m],lo[m],la[m])
        assert np.isfinite(d).all() and np.max(d)<=100
        for aa,bb in ((base_lat,base_lon),(la,lo)):
            u=xyz(aa[m],bb[m]);q,_=cKDTree(u).query(u,k=2)
            assert np.min(2*6371000*np.arcsin(q[:,1]/2))>=200
        geometry_checks.append({'variable':v,'same_index_south_centers':int(m.sum()),'invalid_coordinate_mask_difference_south':int((south&(f!=bf)).sum()),'max_coordinate_displacement_m':float(np.max(d))})
    histgeo[v]=(la,lo)
    hist[v]=(a,keys);metas.append(meta)
valid=np.isfinite(base_lat)&np.isfinite(base_lon)&(base_lat<-45)
maskcounts={}
for v,(a,keys) in hist.items():
    indices=[keys.index((1995,m)) for m in (8,11)]
    mask=np.all(validity(a[indices],v),axis=0)
    maskcounts[v]=int((mask&np.isfinite(base_lat)&(base_lat<-45)).sum())
    la,lo=histgeo[v]
    valid&=mask&np.isfinite(la)&np.isfinite(lo)&(la<-45)
iy,ix=np.where(valid);assert len(iy)>100
lat,lon=base_lat[iy,ix],base_lon[iy,ix];tree=cKDTree(xyz(lat,lon));gd=Geod(ellps='WGS84')
coords=xyz([float(r['lat']) for r in tiles],[float(r['lon']) for r in tiles])
_,near=tree.query(coords,k=1)
mapping=[]
for r,z,j in zip(tiles,coords,near):
    x,y=float(r['lon']),float(r['lat'])
    d0=float(gd.inv(x,y,float(lon[j]),float(lat[j]))[2])
    # Global minimum curvature radius exceeds 6300km; include every spherical
    # candidate that could beat this WGS84 distance, with conservative padding.
    radius=2*math.sin(min(math.pi,(d0+1.)/6300000.)/2)+1e-12
    cand=np.asarray(tree.query_ball_point(z,radius),int);assert len(cand)>0 and j in cand
    _,_,dist=gd.inv(np.full(len(cand),x),np.full(len(cand),y),lon[cand],lat[cand])
    k=int(cand[np.lexsort((ix[cand],iy[cand],dist))[0]])
    d=float(gd.inv(x,y,float(lon[k]),float(lat[k]))[2]/1000)
    assert d<=d0/1000+1e-8
    mapping.append({'tile':r['tile'],'block':r['block'],'grid_y':int(iy[k]),'grid_x':int(ix[k]),'grid_lat':float(lat[k]),'grid_lon':float(lon[k]),'distance_km':d})
points=sorted({(r['grid_y'],r['grid_x']) for r in mapping});lookup={p:i for i,p in enumerate(points)}
pY=np.array([p[0] for p in points]);pX=np.array([p[1] for p in points])
assert valid[pY,pX].all()
for name,rr in [('mapping.csv',mapping)]:
    with (out/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
geo={'model':model,'coordinate_precision_checks':geometry_checks,'native_joint_wet_cells':len(iy),'native_variable_mask_counts':maskcounts,'distinct_mapped_cells':len(points),'tiles':len(mapping),'distance_gate':{str(d):sum(r['distance_km']<=d for r in mapping) for d in (50,100,200)},'distance_max_km':max(r['distance_km'] for r in mapping),'distance_median_km':float(np.median([r['distance_km'] for r in mapping]))}
dump('geometry.json',geo);print('V31B_GEOMETRY='+json.dumps(geo),flush=True)
arrays={};keysets={}
def keep(v,e,a,keys):
    a=a[:,pY,pX]
    assert a.shape==(len(keys),len(points))
    ok=validity(a,v)
    a=np.where(ok,a,np.nan)
    name=v+'__'+e
    arrays[name]=a;keysets[name]=keys
    print('V31B_VALUES='+json.dumps({'model':model,'variable':v,'experiment':e,'finite':int(np.isfinite(a).sum()),'total':a.size,'selected_value_sha256':arrayhash(a)}),flush=True)
for v,(a,keys) in hist.items():keep(v,'historical',a,keys)
del hist,a;gc.collect()
for v in V:
    for e in E[1:]:
        la,lo,a,keys,meta=extract(v,e)
        assert la.shape==histgeo[v][0].shape and np.allclose(la,histgeo[v][0],equal_nan=True,rtol=0,atol=1e-6) and np.allclose(lo,histgeo[v][1],equal_nan=True,rtol=0,atol=1e-6),(v,e,'future grid mismatch')
        keep(v,e,a,keys);metas.append(meta);del a,la,lo;gc.collect()
        # Preserve exact native values as work progresses.
        np.savez_compressed(out/'native_monthly.npz',grid_y=pY,grid_x=pX,**arrays)
        dump('source_metadata.json',{'stores':metas,'keys':keysets})
assert len(arrays)==len(metas)==9
records=[];summary=[]
for e in E:
    for start,end in periods[e]:
        clim={}
        for v in V:
            name=v+'__'+e;keys=keysets[name];take=[i for i,(y,m) in enumerate(keys) if start<=y<=end]
            assert len(take)==80
            values=arrays[name][take];valid=np.isfinite(values).all(axis=0)
            clim[v]=np.where(valid,values.mean(axis=0),np.nan)
        good=np.isfinite(np.column_stack([clim[v] for v in V])).all(axis=1)
        n=0
        for r in mapping:
            k=lookup[r['grid_y'],r['grid_x']]
            row={'model':model,'experiment':e,'period':f'{start}-{end}',**r,'joint_complete':int(good[k]),**{v:float(clim[v][k]) if np.isfinite(clim[v][k]) else None for v in V}}
            records.append(row);n+=int(good[k])
        summary.append({'experiment':e,'period':f'{start}-{end}','complete_tiles':n,'complete_unique_cells':int(good.sum()),'complete_tiles_le100km':sum(r['joint_complete'] and r['distance_km']<=100 for r in records[-1722:])})
assert len(records)==1722*5
with (out/'tile_model_periods.csv').open('w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)
res={'status':'EXECUTED_NATIVE_CMIP6_MODEL','model':model,'member':models[model],'source_stores_verified':len(metas),'geometry':geo,'periods':summary,'limits':'Native model physical conditions, not local downscaling, historical observed values or population forecast; static land frame.'}
dump('result.json',res);print('V31B_RESULT='+json.dumps(res),flush=True)
