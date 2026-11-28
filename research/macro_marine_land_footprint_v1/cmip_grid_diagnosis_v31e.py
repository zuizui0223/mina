"""V31d: source-only geometry diagnosis, no climate values read."""
import csv,io,json,hashlib,pathlib,sys,zipfile,urllib.request
import numpy as np
import fsspec,xarray as xr
from pyproj import Geod
from scipy.spatial import cKDTree
gate,out=map(pathlib.Path,sys.argv[1:3]);out.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256(gate.read_bytes()).hexdigest()=='9b30ce7d9ed05c12d723b82a9b1951bf80ad4078d5de8636542425927afb23ee'
with zipfile.ZipFile(gate) as z:
    assert z.testzip() is None
    n=[n for n in z.namelist() if pathlib.PurePosixPath(n).name=='receipt.json'];assert len(n)==1
    r=json.loads(z.read(n[0]))
def unit(la,lo):
    a,b=np.deg2rad(la),np.deg2rad(lo)
    return np.column_stack((np.cos(a)*np.cos(b),np.cos(a)*np.sin(b),np.sin(a)))
gd=Geod(ellps='WGS84');models={}
for model in ('CESM2',):
    arrays={};metadata=[]
    for s in r['stores']:
        if s['source_id']!=model:continue
        u=s['zstore'].replace('gs://','https://storage.googleapis.com/').rstrip('/')
        with urllib.request.urlopen(u+'/.zmetadata',timeout=60) as f:b=f.read(10000001)
        assert hashlib.sha256(b).hexdigest()==s['metadata_sha256']
        v,e=s['variable_id'],s['experiment_id']
        with xr.open_zarr(fsspec.get_mapper(u,client_kwargs={'trust_env':True}),consolidated=True,chunks=None,decode_times=False) as ds:
            d=tuple(x for x in ds[v].dims if x!='time');assert len(d)==2
            a=next(k for k in ('latitude','lat','nav_lat') if k in ds)
            o=next(k for k in ('longitude','lon','nav_lon') if k in ds)
            la,lo=xr.broadcast(ds[a],ds[o]);la=np.asarray(la.transpose(*d).values,float);rawlo=np.asarray(lo.transpose(*d).values,float);valid=np.isfinite(la)&(abs(la)<=90)&np.isfinite(rawlo)&(abs(rawlo)<=360);invalid=int((~valid).sum());la=np.where(valid,la,np.nan);lo=np.where(valid,(rawlo+180)%360-180,np.nan);print('V31E_COORD_RANGE='+json.dumps({'variable':v,'experiment':e,'invalid_geographic_centers':invalid}),flush=True)
            assert la.shape==lo.shape
            metadata.append({'variable':v,'experiment':e,'dims':d,'shape':list(la.shape),'lat_name':a,'lon_name':o,'lat_dtype':str(ds[a].dtype),'lon_dtype':str(ds[o].dtype),'lat_attrs':dict(ds[a].attrs),'lon_attrs':dict(ds[o].attrs)})
            arrays[v,e]=(la,lo)
    assert len(arrays)==9
    def compare(a,b,label):
        x,y=a;u,v=b
        rec={'comparison':label,'shape_equal':x.shape==u.shape}
        if x.shape!=u.shape:return rec
        fa=np.isfinite(x)&np.isfinite(y);fb=np.isfinite(u)&np.isfinite(v)
        south=(fa&(x<-45))|(fb&(u<-45))
        good=fa&fb&south
        _,_,d=gd.inv(y[good],x[good],v[good],u[good])
        d=np.asarray(d,float);assert np.isfinite(d).all() and len(d)>0
        rec.update(common_south_centers=int(good.sum()),finite_mask_mismatches_south=int((south&(fa!=fb)).sum()),max_m=float(d.max()),median_m=float(np.median(d)),q95_m=float(np.quantile(d,.95)),above100m=int((d>100).sum()),lat_max_abs_deg=float(np.max(np.abs(x[good]-u[good]))),lon_max_abs_deg=float(np.max(np.abs((y[good]-v[good]+180)%360-180))))
        return rec
    comparisons=[]
    for v in ('siconc','sos','tos'):
        for e in ('ssp245','ssp585'):comparisons.append(compare(arrays[v,'historical'],arrays[v,e],v+':historical_to_'+e))
    for v in ('sos','tos'):comparisons.append(compare(arrays['siconc','historical'],arrays[v,'historical'],'siconc_to_'+v))
    spacing={}
    for v in ('siconc','sos','tos'):
        la,lo=arrays[v,'historical'];mask=np.isfinite(la)&np.isfinite(lo)&(la<-45)
        q=unit(la[mask],lo[mask]);dist,_=cKDTree(q).query(q,k=2)
        m=2*6371000*np.arcsin(np.minimum(1,dist[:,1]/2))
        spacing[v]={'centers':int(len(m)),'min_spherical_neighbor_m':float(m.min()),'median_spherical_neighbor_m':float(np.median(m)),'below200m':int((m<200).sum())}
    models[model]={'metadata':metadata,'comparisons':comparisons,'spacing':spacing}
    print('V31D_GRID='+json.dumps({'model':model,'comparisons':comparisons,'spacing':spacing}),flush=True)
    np.savez_compressed(out/(model+'_coordinates.npz'),**{v+'__'+e+'__'+k:a[i] for (v,e),a in arrays.items() for i,k in enumerate(('lat','lon'))})
(out/'receipt.json').write_text(json.dumps({'status':'EXECUTED_COORDINATE_ONLY_DIAGNOSTIC','models':models},indent=2,allow_nan=False)+'\n')
