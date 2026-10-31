"""All January SCL scenes on one fixed local 20m grid; no vegetation trend."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json
import pandas as pd,numpy as np,rasterio
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.windows import from_bounds
from rasterio.transform import from_origin
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
CACHE=ROOT/'work/climate_penguin/scl_multiscene';CACHE.mkdir(exist_ok=True)
d=pd.read_csv(OUT/'satellite_january_catalog_screen.csv');loc=pd.read_csv(OUT/'daily_ice_locations.csv')
d=d[d.year.isin([2019,2024])].merge(loc[['location_id','latitude','longitude']],on=['latitude','longitude'],validate='many_to_one')
GRID=from_origin(-500,500,20,20);rr,cc=np.indices((50,50));INSIDE=((-490+cc*20)**2+(490-rr*20)**2<=500**2)
def run(row):
    path=CACHE/f'{row.location_id}_{row.year}.json'
    if path.exists():return json.loads(path.read_text(encoding='utf-8'))
    crs=f'+proj=aeqd +lat_0={row.latitude} +lon_0={row.longitude} +datum=WGS84 +units=m +no_defs'
    fs=json.loads((ROOT/row.cached_response).read_text(encoding='utf-8'))['features'];daily={};logs=[]
    for f in fs:
        log=dict(scene_id=f['id'],datetime=f['properties']['datetime'],url=f['assets']['scl']['href'])
        try:
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=20,GDAL_HTTP_MAX_RETRY=1):
                with rasterio.open(log['url']) as src:
                    bounds=transform_bounds(crs,src.crs,-540,-540,540,540,densify_pts=21)
                    win=from_bounds(*bounds,src.transform).round_offsets().round_lengths()
                    a=src.read(1,window=win,boundless=True,fill_value=0)
                    b=np.zeros((50,50),dtype=np.uint8)
                    reproject(a,b,src_transform=src.window_transform(win),src_crs=src.crs,dst_transform=GRID,dst_crs=crs,src_nodata=0,dst_nodata=0,resampling=Resampling.nearest)
            date=log['datetime'][:10];land=np.isin(b,[4,5]);valid=np.isin(b,[4,5,6,11])
            if date not in daily:daily[date]=[np.zeros((50,50),bool),np.zeros((50,50),bool)]
            daily[date][0]|=land;daily[date][1]|=valid
            log.update(status='ok',clear_land_fraction=float(land[INSIDE].mean()),usable_scl_fraction=float(valid[INSIDE].mean()))
        except Exception as e:log.update(status='error',error=str(e))
        logs.append(log)
    lands=sum((v[0].astype(np.uint16) for v in daily.values()),start=np.zeros((50,50),np.uint16))
    valid=sum((v[1].astype(np.uint16) for v in daily.values()),start=np.zeros((50,50),np.uint16))
    tif=CACHE/f'{row.location_id}_{row.year}_support.tif'
    with rasterio.open(tif,'w',driver='GTiff',height=50,width=50,count=2,dtype='uint16',crs=crs,transform=GRID,compress='deflate') as dst:
        dst.write(lands,1);dst.write(valid,2);dst.set_band_description(1,'number_of_dates_scl_clear_land');dst.set_band_description(2,'number_of_dates_scl_land_water_snow')
    result=dict(location_id=row.location_id,site_id=row.site_id,cohort=row.cohort,year=int(row.year),scene_count=len(fs),read_success=sum(x['status']=='ok' for x in logs),read_error=sum(x['status']=='error' for x in logs),observed_dates=len(daily),clear_land_once_fraction=float((lands[INSIDE]>=1).mean()),clear_land_twice_fraction=float((lands[INSIDE]>=2).mean()),usable_scl_once_fraction=float((valid[INSIDE]>=1).mean()),support_tif=str(tif.relative_to(ROOT)),support_sha256=hashlib.sha256(tif.read_bytes()).hexdigest(),scenes=logs)
    path.write_text(json.dumps(result,indent=2),encoding='utf-8');return result
rows=[]
with ThreadPoolExecutor(max_workers=8) as pool:
    pending=[pool.submit(run,r) for r in d.itertuples(index=False)]
    for f in as_completed(pending):
        rows.append(f.result())
        if len(rows)%10==0:print('windows',len(rows),'/',len(d),flush=True)
flat=pd.DataFrame([{k:v for k,v in r.items() if k!='scenes'} for r in rows]).sort_values(['location_id','year'])
flat.to_csv(OUT/'satellite_multiscene_support.csv',index=False)
pair=[]
for id,g in flat.groupby('location_id'):
    a=g[g.year.eq(2019)].iloc[0];b=g[g.year.eq(2024)].iloc[0]
    with rasterio.open(ROOT/a.support_tif) as x,rasterio.open(ROOT/b.support_tif) as y:
        assert x.crs==y.crs and x.transform==y.transform
        x=x.read(1);y=y.read(1)
    common1=(x>=1)&(y>=1)&INSIDE;common2=(x>=2)&(y>=2)&INSIDE
    pair.append(dict(location_id=id,site_id=a.site_id,cohort=a.cohort,common_land_once_pixels=int(common1.sum()),common_land_twice_pixels=int(common2.sum()),circle_pixels=int(INSIDE.sum()),common_land_once_fraction=float(common1.sum()/INSIDE.sum()),common_land_twice_fraction=float(common2.sum()/INSIDE.sum()),read_error_total=int(a.read_error+b.read_error)))
pd.DataFrame(pair).to_csv(OUT/'satellite_multiscene_common_support.csv',index=False)
print('DONE; errors',flat.read_error.sum(),'reads',flat.read_success.sum(),flush=True)
