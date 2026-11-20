"""Native OC-CCI extraction with a static ETOPO1 marine denominator."""
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date
from pyproj import Geod
from run import digest, write

URL='https://comet.nefsc.noaa.gov/erddap/griddap/occci_v6_daily_4km'

def fixed_mask(root):
    path=root/'work/polynya_temporal_review/chlorophyll_v6/etopo1_ice_surface_antarctic.nc'
    with Dataset(path) as f:
        assert 'Ice Sheet Surface' in f.title and f.variables['altitude'].units=='m'
        assert f.variables['altitude'].dimensions==('latitude','longitude')
        lat=np.asarray(f.variables['latitude'][:]);lon=np.asarray(f.variables['longitude'][:])
        assert np.allclose(np.diff(lat),1/60) and np.allclose(np.diff(lon),1/60)
        a=np.ma.asarray(f.variables['altitude'][:]).filled(32767)
    def marine(xx,yy):
        assert yy.min()>=lat.min() and yy.max()<=lat.max()
        xx=(xx+180)%360-180
        i=np.floor((yy-lat[0])*60+.5).astype(int);j=np.floor((xx-lon[0])*60+.5).astype(int)
        return a[i,j]<0
    write(dict(source='NOAA ETOPO1 ice-sheet surface',url='https://upwell.pfeg.noaa.gov/erddap/griddap/etopo180.nc?altitude[(-80):1:(-55)][(-180):1:(180)]',sha256=digest(path),units='m',rule='nearest native 1-arcminute elevation <0',denominator='fixed marine domain excluding land and ice-shelf surface; seasonal sea ice retained'),'chlorophyll_mask_manifest.json')
    return marine

def extract(paths,site,year,clat,clon,mask):
    geod=Geod(ellps='WGS84');pieces=[];meta=[]
    for path in paths:
        with Dataset(path) as f:
            assert f.product_version=='6.0'
            assert f.variables['chlor_a'].dimensions==('time','latitude','longitude')
            assert f.variables['chlor_a_log10_rmsd'].dimensions==('time','latitude','longitude')
            assert f.variables['chlor_a'].units=='milligram m-3'
            assert f.variables['latitude'].units=='degrees_north' and f.variables['longitude'].units=='degrees_east'
            lat=np.asarray(f.variables['latitude'][:]);lon=np.asarray(f.variables['longitude'][:]);xx,yy=np.meshgrid(lon,lat)
            assert np.allclose(np.diff(lat),-1/24) and np.allclose(np.diff(lon),1/24)
            _,_,dist=geod.inv(np.full(xx.size,clon),np.full(xx.size,clat),xx.ravel(),yy.ravel())
            circle=dist<=100000
            keep=circle&mask(xx.ravel(),yy.ravel())
            weights=np.cos(np.deg2rad(yy.ravel()[keep]));assert weights.sum()>0
            v=f.variables['chlor_a'];arr=np.ma.asarray(v[:],dtype=float).filled(np.nan).reshape(-1,xx.size)[:,keep]
            if hasattr(v,'valid_min'):arr[arr<float(v.valid_min)]=np.nan
            if hasattr(v,'valid_max'):arr[arr>float(v.valid_max)]=np.nan
            if hasattr(v,'valid_range'):
                arr[(arr<float(v.valid_range[0]))|(arr>float(v.valid_range[1]))]=np.nan
            arr[arr<=0]=np.nan
            rms=np.ma.asarray(f.variables['chlor_a_log10_rmsd'][:],dtype=float).filled(np.nan).reshape(-1,xx.size)[:,keep]
            tt=f.variables['time'];dates=[str(q)[:10] for q in num2date(tt[:],tt.units,only_use_cftime_datetimes=False)]
            pieces.append((arr,rms,weights,dates))
            meta.append(dict(path=path.name,chlorophyll_units=getattr(v,'units',''),product_version=getattr(f,'product_version',''),marine_pixels=int(keep.sum()),circle_pixels=int(circle.sum())))
    dates=pieces[0][3];assert all(q[3]==dates for q in pieces)
    arr=np.concatenate([q[0] for q in pieces],axis=1);rms=np.concatenate([q[1] for q in pieces],axis=1);w=np.concatenate([q[2] for q in pieces])
    valid=np.isfinite(arr);coverage=(valid*w).sum(axis=1)/w.sum();mean=np.nansum(arr*w,axis=1)/np.where((valid*w).sum(axis=1)>0,(valid*w).sum(axis=1),np.nan)
    rv=np.isfinite(rms)&valid;rmean=np.nansum(np.where(rv,rms,np.nan)*w,axis=1)/np.where((rv*w).sum(axis=1)>0,(rv*w).sum(axis=1),np.nan)
    out=pd.DataFrame(dict(site_id=site,season=year,date=dates,coverage=coverage,chlor_a=mean,log10_rms=rmean,marine_pixels=arr.shape[1]))
    out['passes_daily']=out.coverage.ge(.2)&out.chlor_a.gt(0)
    return out,meta
