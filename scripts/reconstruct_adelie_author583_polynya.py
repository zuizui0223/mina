#!/usr/bin/env python3
"""Descriptive Youngflesh RDS source-pool to DEEP-AA 2004–10 winter exposure.
NOT frozen 439-season model. Must not silently substitute for published panel.
"""
import argparse, calendar, hashlib, json, math, re, zipfile
from collections import defaultdict
from datetime import date
from io import BytesIO
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.io import netcdf_file
from pyproj import Transformer, Geod

MD5='f3f958389cc5e67ac1c4e3a6ee164318'
R_EARTH=6371.0088
def decode(raw, keys):
    if raw[:3]==b'CDF':
        with netcdf_file(BytesIO(raw),mmap=False) as f:
            return [np.array(f.variables[k][:],copy=True) for k in keys]
    from netCDF4 import Dataset
    with Dataset('in_memory.nc',memory=raw) as f:
        return [np.array(np.ma.filled(f.variables[k][:],-999),copy=True) for k in keys]
def xyz(lon,lat):
    a=np.deg2rad(lon);b=np.deg2rad(lat)
    return np.stack([np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)],axis=-1)
def grid_area_km2(lon,lat):
    v=xyz(lon,lat)*R_EARTH
    return np.where(np.isfinite(v).all(axis=-1),
                    np.linalg.norm(np.cross(np.gradient(v,axis=0),np.gradient(v,axis=1)),axis=-1),0)

def main(deep,source,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    h=hashlib.md5()
    with open(deep,'rb') as f:
        for c in iter(lambda:f.read(4<<20),b''):h.update(c)
    if h.hexdigest()!=MD5:raise ValueError('STOP wrong official DEEP-AA MD5')
    d=pd.read_csv(source)
    needed={'site_id','season','x_m','y_m','author_site_avg_n_pix','region','n_image_days','n_pixels'}
    if not needed.issubset(d):raise ValueError('STOP RDS source support columns inconsistent')
    if (d.author_site_avg_n_pix<2).any():
        raise ValueError('STOP author-site-level average pixel support below 2')
    if d.duplicated(['site_id','season']).any():
        raise ValueError('STOP duplicated original source site-years')
    if len(d)!=583 or d.site_id.nunique()!=113 or set(d.season)!=set(range(2004,2011)):
        raise ValueError('STOP author 583-site-year/113-site support gate changed: '+str((len(d),d.site_id.nunique())))
    sites=d.groupby('site_id').agg(x_m=('x_m','median'),y_m=('y_m','median')).reset_index()
    sites['lon'],sites['lat']=Transformer.from_crs(3031,4326,always_xy=True).transform(sites.x_m.to_numpy(),sites.y_m.to_numpy())
    with zipfile.ZipFile(deep) as z:
        ncs=[n for n in z.namelist() if n.lower().endswith('.nc')]
        ll=[n for n in ncs if n.split('/')[-1].lower()=='lonlat.nc']
        if len(ll)!=1:raise ValueError('STOP LonLat.nc absent or duplicated')
        lon,lat=decode(z.read(ll[0]),['Lon','Lat'])
        if lon.shape!=lat.shape or lon.ndim!=2:raise ValueError('STOP malformed geocoding')
        area=grid_area_km2(lon,lat)
        valid=np.flatnonzero(np.isfinite(lon.ravel()) & np.isfinite(lat.ravel()) &
                            (np.abs(lat.ravel())<=90)&(area.ravel()>0))
        tree=cKDTree(xyz(lon.ravel()[valid],lat.ravel()[valid]))
        possible=tree.query_ball_point(xyz(sites.lon.to_numpy(),sites.lat.to_numpy()),
                                      2*np.sin(100.5/(2*R_EARTH)))
        geod=Geod(ellps='WGS84');indices=[]
        for i,site in sites.iterrows():
            a=valid[np.asarray(possible[i],dtype=int)]
            _,_,meters=geod.inv(np.full(len(a),site.lon),np.full(len(a),site.lat),
                                lon.ravel()[a],lat.ravel()[a])
            indices.append(a[np.asarray(meters)<=100000])
        dated={}
        for name in ncs:
            if name==ll[0]:continue
            m=re.search(r'(?<!\d)(20\d{6})(?!\d)',name.split('/')[-1])
            if m:
                s=m[1];day=date(int(s[:4]),int(s[4:6]),int(s[6:8]))
                if 2004<=day.year<=2010 and 6<=day.month<=10:
                    if day in dated:raise ValueError('STOP duplicate day '+str(day))
                    dated[day]=name
        if not dated:raise ValueError('STOP no DEEP-AA winters for 2004-2010')
        first,=decode(z.read(next(iter(dated.values()))),['Map'])
        if first.shape!=lon.shape:raise ValueError('STOP daily Map and LonLat disagree')
        ocean=np.isfinite(first.ravel())&(first.ravel()!=-999)
        area1=area.ravel()
        denom=np.asarray([np.sum(area1[ix[ocean[ix]]]) for ix in indices])
        if not np.all(denom>0):raise ValueError('STOP zero ocean denominator')
        series=[]
        month_days=defaultdict(int)
        for day,name in sorted(dated.items()):
            m,=decode(z.read(name),['Map'])
            if m.shape!=lon.shape:raise ValueError('STOP map geometry changed')
            pixels=m.ravel();coastal=(pixels>0)&((pixels%2)==0)
            for i,ix in enumerate(indices):
                frac=float(np.sum(area1[ix[coastal[ix]]])/denom[i])
                series.append((sites.site_id.iat[i],day.year,day.month,frac,day.isoformat()))
            month_days[(day.year,day.month)]+=1
    days=pd.DataFrame(series,columns=['site_id','season','month','coastal_fraction_100km','date'])
    mon=days.groupby(['site_id','season','month'],as_index=False).agg(fraction=('coastal_fraction_100km','mean'),n_days=('date','nunique'))
    mon['required_days']=mon.apply(lambda z:math.ceil(.8*calendar.monthrange(int(z.season),int(z.month))[1]),axis=1)
    mon['eligible']=mon.n_days>=mon.required_days
    complete=mon[mon.eligible].groupby(['site_id','season']).agg(n_months=('month','nunique'),exposure=('fraction','mean')).reset_index()
    complete=complete[complete.n_months==5]
    joined=d.merge(complete[['site_id','season','exposure']],on=['site_id','season'],how='left',validate='one_to_one')
    joined['source_qualified']=joined.exposure.notna()
    joined['coastal_area_fraction_percent']=100*joined.exposure
    joined=joined.merge(sites[['site_id','lat','lon']],on='site_id',validate='many_to_one')
    joined.to_csv(out/'original_author_source_2004_2010_polynya_site_years.csv',index=False)
    mon.to_csv(out/'original_author_source_monthly_exposure.csv',index=False)
    rec={'status':'AUTHOR_PIXEL_SUPPORT_REPRODUCED_POLYNYA_PANEL_STILL_NOT_FROZEN_439',
         'n_original_author_source_site_years':len(d),'raw_sites':len(sites),
         'n_complete_exposures':int(joined.source_qualified.sum()),
         'n_complete_sites':int(joined.loc[joined.source_qualified,'site_id'].nunique()),
         'original_manuscript_n':439,'original_manuscript_sites':85,
         'n_daily_maps':len(dated),
         'original_author_pixel_rows':179346,'original_author_sites_all_years':119,
         'selection_note':'No arbitrary >=4-year site filter. Original 4-diet-est.R pixel support >=2 averaged per site over all years. Original 439 rows/85 sites not yet identified.',
         'months_total':{f'{yr}-{mo:02d}':int(n) for (yr,mo),n in sorted(month_days.items())},
         'cell_area_method':'spherical finite-difference Jacobian approximated from geographic pixel centres',
         'ocean_mask':'Map != -999 on earliest eligible June-Oct day; coastal positive even IDs',
         'window':'June-Oct 2004-2010; each month at least 80% valid days; monthly equal weighting',
         'cannot_claim_frozen_reproduction':True}
    (out/'source_reconstruction_audit.json').write_text(json.dumps(rec,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rec.items() if k!='months_total'},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('deep');p.add_argument('source');p.add_argument('output')
    a=p.parse_args();main(a.deep,a.source,a.output)
