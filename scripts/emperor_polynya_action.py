#!/usr/bin/env python3
"""Independent emperor-penguin × DEEP-AA Apr–Aug screening. Never substitutes data."""
from __future__ import annotations
import hashlib, itertools, json, math, re, sys, zipfile
from collections import defaultdict
from datetime import date
from io import BytesIO
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import t as student_t

DEEP_MD5 = 'f3f958389cc5e67ac1c4e3a6ee164318'
COLONY_GIT_BLOB = '133c900c9dfbf2ce23ca403c9a59edecd9b51ace'
R = 6371.0088
RADII = (50, 100, 200)


def get_nc(raw, names):
    if raw[:4] in (b'CDF\x01', b'CDF\x02'):
        from scipy.io import netcdf_file
        with netcdf_file(BytesIO(raw), mmap=False) as ds:
            return [np.asarray(ds.variables[n][:]).copy() for n in names]
    if raw[:8] == b'\x89HDF\r\n\x1a\n':
        from netCDF4 import Dataset
        with Dataset('in_memory.nc', memory=raw) as ds:
            return [np.asarray(np.ma.filled(ds.variables[n][:], -999)) for n in names]
    raise ValueError('Unexpected NetCDF format')


def xyz(lon, lat):
    a, b = np.deg2rad(np.asarray(lon)), np.deg2rad(np.asarray(lat))
    return np.stack((np.cos(b)*np.cos(a), np.cos(b)*np.sin(a), np.sin(b)), axis=-1)


def verify(deep, response):
    if deep.name != 'SIC60_6.25km_20d.zip':
        raise ValueError('Primary subset must be SIC60_6.25km_20d.zip')
    h=hashlib.md5()
    with deep.open('rb') as f:
        for block in iter(lambda:f.read(4<<20), b''): h.update(block)
    if h.hexdigest()!=DEEP_MD5: raise ValueError('DEEP-AA MD5 mismatch')
    b=response.read_bytes()
    if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!=COLONY_GIT_BLOB:
        raise ValueError('LaRue Git blob hash mismatch')
    df=pd.read_csv(BytesIO(b))
    if len(df)!=500 or df.site_id.nunique()!=50 or df.duplicated(['site_id','year']).any():
        raise ValueError('LaRue 50-colony × 10-year model results invalid')
    if set(df.year)!=set(range(2009,2019)) or not set(['lat','lon','ice_reg','N_mean']).issubset(df):
        raise ValueError('LaRue model release schema mismatch')
    return df


def extract(deep, colony):
    sites=colony[['site_id','lon','lat','ice_reg']].drop_duplicates('site_id').reset_index(drop=True)
    with zipfile.ZipFile(deep) as zf:
        ncs=[p for p in zf.namelist() if p.lower().endswith('.nc')]
        ll=[p for p in ncs if p.split('/')[-1].lower()=='lonlat.nc']
        if len(ll)!=1: raise ValueError('DEEP-AA requires unique LonLat.nc')
        lon,lat=get_nc(zf.read(ll[0]), ('Lon','Lat'))
        if lon.shape!=lat.shape or lon.ndim!=2: raise ValueError('Geographical grid malformed')
        valid=np.flatnonzero(np.isfinite(lon.ravel()) & np.isfinite(lat.ravel()) &
                            (np.abs(lat.ravel())<=90))
        tree=cKDTree(xyz(lon.ravel()[valid],lat.ravel()[valid]))
        cent=xyz(sites.lon.to_numpy(),sites.lat.to_numpy())
        idx={r:[valid[np.asarray(q,dtype=int)] for q in tree.query_ball_point(
            cent, 2*np.sin(r/(2*R)))] for r in RADII}
        dated={}
        for name in ncs:
            if name==ll[0]: continue
            m=re.search(r'(?<!\d)(20\d{6})(?!\d)', name.split('/')[-1])
            if not m: continue
            day=date.fromisoformat(m[1][:4]+'-'+m[1][4:6]+'-'+m[1][6:8])
            if 2009<=day.year<=2018 and 4<=day.month<=8:
                if day in dated: raise ValueError(f'Duplicate date: {day}')
                dated[day]=name
        sums=defaultdict(lambda: {r:np.zeros(len(sites),float) for r in RADII})
        daycounts=defaultdict(int)
        for day,name in sorted(dated.items()):
            mm,=get_nc(zf.read(name),('Map',))
            if mm.shape!=lon.shape: raise ValueError('Daily Map / LonLat shape mismatch: no blind transpose')
            a=mm.ravel()
            coastal=(a>0)&(a%2==0)
            for radius in RADII:
                sums[day.year][radius]+=[int(np.count_nonzero(coastal[ix])) for ix in idx[radius]]
            daycounts[day.year]+=1
    out=[]; auditing=[]
    for year in range(2009,2019):
        expected=(date(year,9,1)-date(year,4,1)).days
        ndays=daycounts[year];coverage=ndays/expected
        auditing.append(dict(year=year, days=ndays, expected=expected, coverage=coverage, eligible=coverage>=.95))
        for i,site in sites.iterrows():
            row=dict(site_id=site.site_id,year=year,eligible=coverage>=.95,coverage=coverage)
            for radius in RADII:
                row[f'coastal_{radius}km']=float(39.0625*sums[year][radius][i]/ndays) if ndays else np.nan
            out.append(row)
    df=colony.merge(pd.DataFrame(out),on=['site_id','year'],validate='one_to_one')
    return df,auditing


def fixed_effects(df, regional_year=False, bootstrap=True):
    df=df[df.eligible].copy().reset_index(drop=True)
    if len(df)<300: raise ValueError('Fewer than 300 complete colony years')
    y=np.log1p(df.N_mean.to_numpy(float)); x=np.log1p(df.coastal_100km.to_numpy(float))
    if not (np.isfinite(x).all() and np.isfinite(y).all()): raise ValueError('Non-finite values')
    yr=(df.ice_reg.astype(str)+'__'+df.year.astype(str)) if regional_year else df.year.astype(str)
    z=np.column_stack([np.ones(len(df)),pd.get_dummies(df.site_id,drop_first=True,dtype=float).to_numpy(),
                       pd.get_dummies(yr,drop_first=True,dtype=float).to_numpy()])
    u,s,_=np.linalg.svd(z,full_matrices=False)
    rank=int(np.sum(s>1e-9*s[0])); q=u[:,:rank]
    xr=x-q@(q.T@x); yr=y-q@(q.T@y)
    sd=float(np.std(xr,ddof=1))
    if sd<1e-7: raise ValueError('No identifiable exposure variation')
    xr=xr/sd
    denom=float(xr@xr)
    regions=df.ice_reg.astype(str).to_numpy(); labels=sorted(set(regions))
    inds=np.searchsorted(labels,regions); g=len(labels); n=len(df); p=rank+1
    if not 6<=g<=12 or p>=n: raise ValueError('Insufficient cluster identifiability')
    def est(v):
        beta=float(xr@v/denom);res=v-beta*xr
        score=np.bincount(inds,weights=xr*res,minlength=g)
        se=float(np.sqrt((g/(g-1))*((n-1)/(n-p))*sum(score*score)/denom**2))
        return beta,se,beta/se if se>1e-15 else float('nan')
    beta,se,t=est(yr)
    if not np.isfinite(t): raise ValueError('Undefined cluster t statistic')
    extreme=0
    for signs in itertools.product((-1.,1.),repeat=g):
        trial=yr*np.asarray(signs)[inds];trial-=q@(q.T@trial)
        ts=est(trial)[2]
        extreme+=int(np.isfinite(ts) and abs(ts)>=abs(t)-1e-12)
    loo={}
    for lab in labels:
        sub=df[df.ice_reg.astype(str)!=lab]
        xx=np.log1p(sub.coastal_100km.to_numpy(float)); yy=np.log1p(sub.N_mean.to_numpy(float))
        subyr=(sub.ice_reg.astype(str)+'__'+sub.year.astype(str)) if regional_year else sub.year.astype(str)
        zz=np.column_stack([np.ones(len(sub)),pd.get_dummies(sub.site_id,drop_first=True,dtype=float).to_numpy(),
                            pd.get_dummies(subyr,drop_first=True,dtype=float).to_numpy(),xx])
        loo[lab]=float(np.linalg.lstsq(zz,yy,rcond=None)[0][-1])
    return dict(model='colony+region_year FE' if regional_year else 'colony+year FE',
                n=n,n_colonies=df.site_id.nunique(),n_years=df.year.nunique(),n_regions=g,
                exposure_within_fe_sd_log_units=sd,beta_per_sd=beta,
                cluster_se=se,ci95=[beta-student_t.ppf(.975,g-1)*se,beta+student_t.ppf(.975,g-1)*se],
                cluster_p=float(2*student_t.sf(abs(t),g-1)),signflip_p=extreme/(2**g),
                permutations=2**g,leave_region_out_beta_per_log_unit=loo)


def main():
    if len(sys.argv)!=4:
        raise SystemExit('Usage: python emperor_polynya_action.py <DEEP ZIP> <LaRue CSV> <outdir>')
    deep,source,out=map(Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=True)
    response=verify(deep,source)
    joined,years=extract(deep,response)
    joined.to_csv(out/'colony_year_exposure.csv',index=False)
    report=dict(input_verified=True,expected_hash={'deep_md5':DEEP_MD5,'larue_git_blob':COLONY_GIT_BLOB},
                years=years,n_eligible=int(joined.eligible.sum()))
    (out/'coverage_and_sources.json').write_text(json.dumps(report,indent=2)+'\n')
    if report['n_eligible']<300: raise ValueError('STOP: fewer than 300 eligible colony years')
    p=fixed_effects(joined); q=fixed_effects(joined,regional_year=True)
    decision='positive_screen_only' if p['beta_per_sd']>0 and p['signflip_p']<=.05 and q['beta_per_sd']>0 and all(v>0 for v in p['leave_region_out_beta_per_log_unit'].values()) else 'frozen_hypothesis_not_supported'
    report.update(primary=p,region_year_control=q,screening_decision=decision,
                  publication_gate='NOT MET: joint response/posterior and independent sea-ice controls not included')
    (out/'empirical_screening.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='EMPIRICAL_SCREEN_DONE',screening_decision=decision,
                           beta=p['beta_per_sd'],p_signflip=p['signflip_p'],n=p['n'])))

if __name__=='__main__': main()
