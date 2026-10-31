"""Fixed 44-pair original monthly marine ice extraction and exploratory association.

Provider primary ice_conc, same prior Aug-Nov window and original 100km site
buffers; missing is not zero. No nesting snow, route, warming or causal claim.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from pathlib import Path
import numpy as np
import xarray as xr
from pyproj import Geod
sys.path.insert(0,str(Path(__file__).resolve().parent))
import seaice_monthly_source_v4 as source
import lagged_climate_v3 as regression
PAIR_SHA='c5c6a07c14f73728aa8b5fc40e96c12e95b7718028c02e3bd35154b0ef5f76f0'
SITE_SHA='36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34'
MONTHS=(8,9,10,11)
RADIUS_KM=100.
MIN_VALID_FRACTION=.8
EXPECTED_FLAGS=[1,2,4,8,16,32,64,128]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    with Path(path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def validate_attrs(attrs,year,month):
    expect={'product_id':'osi-450-a1','product_version':'3.1','doi':'10.15770/EUM_SAF_OSI_0023',
      'time_coverage_start':f'{year:04d}-{month:02d}-01T00:00:00Z',
      'time_coverage_end':f'{year:04d}-{month+1:02d}-01T00:00:00Z'}
    for k,v in expect.items():
        if str(attrs.get(k,''))!=v:raise ValueError('original monthly metadata mismatch '+k)

def summarize_cells(sic,flags,indices):
    s=np.asarray(sic).ravel()[indices];f=np.asarray(flags).ravel()[indices]
    finite=np.isfinite(f)&(f>=0)&(f<=32767)
    bits=np.where(finite,f,3).astype(np.int32)
    water=finite&((bits&3)==0);valid=water&np.isfinite(s)
    nwater=int(water.sum());nvalid=int(valid.sum())
    if np.any((s[valid]<0)|(s[valid]>100.001)):raise ValueError('invalid original primary SIC range')
    fraction=nvalid/nwater if nwater else 0.
    average=float(s[valid].mean()) if nvalid else None
    out=dict(n_grid=len(indices),n_ocean=nwater,n_valid=nvalid,
       valid_fraction=fraction,complete_spatial_support=bool(nwater and fraction>=MIN_VALID_FRACTION),
       sic_percent_mean=average if nwater and fraction>=MIN_VALID_FRACTION else None,
       unqualified_valid_pixel_mean=average)
    for name,mask in [('open_water_filtered',4),('landspill',8),('high_t2m',16),('interpolated',96),('climatology_zero',128)]:
        out['n_'+name]=int(((bits[valid]&mask)!=0).sum())
    return out

def overlap_report(masks):
    return [dict(a=a,b=b,shared_cells=len(masks[a]&masks[b]),
       jaccard=len(masks[a]&masks[b])/len(masks[a]|masks[b]) if masks[a]|masks[b] else None)
       for a,b in combinations(sorted(masks),2)]

def join_exposure(pairs,monthly):
    lookup={}
    for r in monthly:
        key=(r['site_id'],int(r['year']),int(r['month']))
        if key in lookup:raise ValueError('duplicate source month')
        lookup[key]=r
    out=[]
    for row in pairs:
        if str(row['prior_precedes_all_source_bounds']) not in ('True','true'):
            raise ValueError('original prior-window chronology no longer passes')
        a,b=int(row['start_year'])-1,int(row['end_year'])-1
        vals=[]
        for year in (a,b):
            months=[]
            for month in MONTHS:
                r=lookup.get((row['site_id'],year,month))
                if r is None:raise ValueError('missing monthly original support')
                if not r['complete_spatial_support'] or r['sic_percent_mean'] is None:
                    raise ValueError('missing monthly spatial support; no replacement')
                months.append(float(r['sic_percent_mean']))
            vals.append(float(np.mean(months)))
        out.append(dict(row,prior_sic_start_percent=vals[0],prior_sic_end_percent=vals[1],
            delta_prior_sic_10pp=(vals[1]-vals[0])/10.))
    return out

def discover(years,out):
    raw=source.get(source.ROOT,4_000_000);cat=source.catalog(raw,source.ROOT)
    (out/'monthly_catalog.xml').write_bytes(raw)
    files=list(cat['datasets']);catalog_receipts=[dict(url=source.ROOT,sha256=hashlib.sha256(raw).hexdigest())]
    for url in source.needed_refs(cat['refs'],years):
        raw=source.get(url,4_000_000);child=source.catalog(raw,url);files.extend(child['datasets'])
        (out/('catalog_'+url.split('/')[-2]+'.xml')).write_bytes(raw)
        catalog_receipts.append(dict(url=url,sha256=hashlib.sha256(raw).hexdigest()))
    jobs=[]
    for year in years:
        for month in MONTHS:
            rel=source.choose_file(files,year,month)
            jobs.append((year,month,'https://thredds.met.no/thredds/fileServer/'+rel))
    return jobs,catalog_receipts

def retrieve(job,folder):
    year,month,url=job
    raw=source.get(url)
    if not (raw.startswith(b'CDF') or raw.startswith(b'\x89HDF')):raise ValueError('not original monthly NetCDF')
    path=folder/Path(url).name;path.write_bytes(raw)
    return dict(year=year,month=month,url=url,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),filename=path.name)

def extract(receipts,sites,rawdir):
    geod=Geod(ellps='WGS84');base_lat=base_lon=None;masks={};ocean_sets={};records=[];pixel_rows=[]
    for receipt in sorted(receipts,key=lambda z:(z['year'],z['month'])):
        year,month=receipt['year'],receipt['month']
        path=rawdir/receipt['filename']
        if sha(path)!=receipt['sha256']:raise ValueError('downloaded source SHA changed')
        with xr.open_dataset(path) as ds:
            validate_attrs(ds.attrs,year,month)
            if ds['ice_conc'].attrs.get('units')!='%':raise ValueError('wrong SIC unit')
            if list(ds['status_flag'].attrs['flag_masks'])!=EXPECTED_FLAGS:raise ValueError('flag semantics changed')
            if ds['ice_conc'].shape!=(1,432,432):raise ValueError('source grid shape changed')
            if ds['time_bnds'].values.astype('datetime64[D]').tolist()!=[[np.datetime64(f'{year}-{month:02d}-01','D').astype(object),np.datetime64(f'{year}-{month+1:02d}-01','D').astype(object)]]:
                raise ValueError('source time bounds mismatch')
            lat,lon=ds['lat'].values,ds['lon'].values
            if base_lat is None:
                base_lat=lat.copy();base_lon=lon.copy()
                for site in sites:
                    distance=geod.inv(np.full(lon.shape,float(site['longitude'])),np.full(lat.shape,float(site['latitude'])),lon,lat)[2]/1000.
                    masks[site['site_id']]=np.flatnonzero((distance>=0)&(distance<RADIUS_KM))
            elif not (np.array_equal(lat,base_lat) and np.array_equal(lon,base_lon)):
                raise ValueError('grid moved between original monthly files')
            sic=ds['ice_conc'].values[0].ravel();flag=ds['status_flag'].values[0].ravel()
            for sid,indices in masks.items():
                values=summarize_cells(sic,flag,indices)
                records.append(dict(site_id=sid,year=year,month=month,**values))
                water={int(i) for i in indices if np.isfinite(flag[i]) and flag[i]>=0 and (int(flag[i])&3)==0}
                if sid not in ocean_sets:ocean_sets[sid]=water
                elif water!=ocean_sets[sid]:raise ValueError('monthly ocean cell support changed; hold unchanged-area analysis')
                for i in indices:
                    pixel_rows.append(dict(site_id=sid,year=year,month=month,flat_cell_index=int(i),
                      lat=float(lat.ravel()[i]),lon=float(lon.ravel()[i]),
                      sic_percent=float(sic[i]) if np.isfinite(sic[i]) else None,
                      flag=int(flag[i]) if np.isfinite(flag[i]) else None))
    return records,pixel_rows,ocean_sets

def main():
    p=argparse.ArgumentParser();p.add_argument('--pairs',required=True,type=Path);p.add_argument('--sites',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path);p.add_argument('--offline',action='store_true');a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True);rawdir=a.out/'original_nc';rawdir.mkdir(exist_ok=True)
    if sha(a.pairs)!=PAIR_SHA or sha(a.sites)!=SITE_SHA:raise ValueError('original paired roster or site SHA mismatch')
    pairs=read(a.pairs)
    if len(pairs)!=44 or len({r['site_id'] for r in pairs})!=7:raise ValueError('original44 roster changed')
    selected={r['site_id'] for r in pairs};sites=[s for s in read(a.sites) if s['site_id'] in selected]
    if len(sites)!=7:raise ValueError('site identity not unique')
    years=sorted({int(r[k])-1 for r in pairs for k in ('start_year','end_year')})
    manifest=a.out/'monthly_download_receipts.json'
    if a.offline:
        receipt=json.loads(manifest.read_text());downloads=receipt['files']
    else:
        jobs,catalogs=discover(years,a.out)
        with ThreadPoolExecutor(max_workers=4) as pool:downloads=list(pool.map(lambda j:retrieve(j,rawdir),jobs))
        receipt={'catalogs':catalogs,'files':downloads};manifest.write_text(json.dumps(receipt,indent=2)+'\n')
    if len(downloads)!=96 or {(r['year'],r['month']) for r in downloads}!={(y,m) for y in years for m in MONTHS}:raise ValueError('required96 months incomplete')
    monthly,pixels,ocean=extract(downloads,sites,rawdir)
    write_csv(a.out/'original_monthly_7site_100km.csv',monthly);write_csv(a.out/'original_selected_grid_cells.csv',pixels)
    common=join_exposure(pairs,monthly);write_csv(a.out/'fixed44_prior_seaice_pairs.csv',common)
    models={};sensitivity={}
    for name,year_effect in [('site_fixed',False),('site_year_fixed',True)]:
        models[name]=regression.fit(common,'delta_prior_sic_10pp',year_effect)
        sensitivity[name]={field:regression.leave_one(common,'delta_prior_sic_10pp',year_effect,field) for field in ('site_id','end_year')}
    outcome={'status':'EXPLORATORY_FIXED44_PRIOR_MARINE_ICE_NOT_CAUSAL',
        'input_pair_sha256':sha(a.pairs),'input_sites_sha256':sha(a.sites),
        'original_month_files':len(downloads),'site_month_rows':len(monthly),'source_years':years,
        'primary_field':'ice_conc (provider filtered primary monthly estimate)',
        'units':'growth difference per 10 percentage-point prior Aug-Nov SIC change',
        'models':models,'deletion_sensitivity_not_CI':sensitivity,
        'n_unique_ocean_cell_supports':len({tuple(sorted(v)) for v in ocean.values()}),
        'marine_support_overlap':overlap_report(ocean),
        'monthly_quality_ranges':{key:[min(z[key] for z in monthly),max(z[key] for z in monthly)] for key in ('n_ocean','n_valid','valid_fraction','n_landspill','n_interpolated','n_high_t2m','n_climatology_zero')},
        'limits':['Same44 positive-endpoint original pairs, exploratory not preregistered confirmation.',
          'Sea-ice retrieval includes ERA5 ancillary input; not fully independent of temperature.',
          'Monthly filtered primary estimate differs from averaging filtered daily files; never substitute silently.',
          '100km marine grid cell support is not nesting snow or direct coastal accessibility.',
          'Overlapping source pixels are not independent site climates.',
          'Current year labels bound prior exposure; field observation dates not independently verified.',
          'No calibrated p value, confidence interval, competing species effect or anthropogenic attribution.']}
    (a.out/'seaice_fixed44_v4_result.json').write_text(json.dumps(outcome,indent=2,allow_nan=False)+'\n')
    print('SEAICE_FIXED44_V4='+json.dumps(outcome,allow_nan=False),flush=True)
if __name__=='__main__':main()
