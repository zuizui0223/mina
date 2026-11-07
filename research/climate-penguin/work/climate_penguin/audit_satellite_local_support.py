"""Read SCL pixels at all 106 locations; scene availability is not vegetation data."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib
import pandas as pd,numpy as np,rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
CACHE=ROOT/'work/climate_penguin/scl_support';CACHE.mkdir(exist_ok=True)
d=pd.read_csv(OUT/'satellite_january_catalog_screen.csv');loc=pd.read_csv(OUT/'daily_ice_locations.csv')
d=d[d.year.isin([2019,2024])].merge(loc[['location_id','latitude','longitude']],on=['latitude','longitude'],validate='many_to_one')
assert len(d)==212
def run(row):
    path=CACHE/f'{row.location_id}_{row.year}.json'
    if path.exists():
        old=json.loads(path.read_text(encoding='utf-8'))
        if old['status'] in ['ok','no_scene']:return old
    r=dict(location_id=row.location_id,site_id=row.site_id,cohort=row.cohort,year=int(row.year),radius_m=500,selection='lowest_scene_cloud_one_candidate',latitude=row.latitude,longitude=row.longitude)
    features=json.loads((ROOT/row.cached_response).read_text(encoding='utf-8'))['features']
    if not features:r['status']='no_scene'
    else:
        f=min(features,key=lambda x:(x['properties'].get('eo:cloud_cover',100),x['id']))
        r.update(scene_id=f['id'],datetime=f['properties']['datetime'],scene_cloud_percent=f['properties'].get('eo:cloud_cover'),scl_url=f['assets']['scl']['href'])
        try:
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=30,GDAL_HTTP_MAX_RETRY=1):
                with rasterio.open(r['scl_url']) as src:
                    x,y=transform('EPSG:4326',src.crs,[row.longitude],[row.latitude]);x=x[0];y=y[0]
                    win=from_bounds(x-500,y-500,x+500,y+500,src.transform).round_offsets().round_lengths()
                    a=src.read(1,window=win,boundless=True,fill_value=0);tf=src.window_transform(win)
                    rr,cc=np.indices(a.shape);xx=tf.c+(cc+.5)*tf.a;yy=tf.f+(rr+.5)*tf.e
                    inside=(xx-x)**2+(yy-y)**2<=500**2;v=a[inside];assert len(v)>0
                    prof=src.profile.copy();prof.update(height=a.shape[0],width=a.shape[1],transform=tf,count=1)
                    tif=CACHE/f'{row.location_id}_{row.year}_SCL.tif'
                    with rasterio.open(tif,'w',**prof) as dst:dst.write(a,1)
            r.update(status='ok',pixels=len(v),scl_sha256=hashlib.sha256(tif.read_bytes()).hexdigest(),scl_crop=str(tif.relative_to(ROOT)),
                nodata_defective_fraction=float(np.isin(v,[0,1]).mean()),cloud_shadow_fraction=float(np.isin(v,[3,8,9,10]).mean()),snow_ice_fraction=float((v==11).mean()),water_fraction=float((v==6).mean()),dark_unclassified_fraction=float(np.isin(v,[2,7]).mean()),clear_land_fraction=float(np.isin(v,[4,5]).mean()),scl_vegetation_fraction=float((v==4).mean()))
            for cls in range(12):r[f'scl_{cls}_pixels']=int((v==cls).sum())
            assert sum(r[f'scl_{i}_pixels'] for i in range(12))==len(v)
        except Exception as e:r.update(status='error',error=str(e))
    path.write_text(json.dumps(r,indent=2),encoding='utf-8');return r
rows=[]
with ThreadPoolExecutor(max_workers=6) as pool:
    pending=[pool.submit(run,r) for r in d.itertuples(index=False)]
    for f in as_completed(pending):
        rows.append(f.result())
        if len(rows)%20==0:print('completed',len(rows),'/',len(d),flush=True)
a=pd.DataFrame(rows).sort_values(['location_id','year']);a.to_csv(OUT/'satellite_local_scl_support.csv',index=False)
a['candidate_clear_land']=a.status.eq('ok')&(a.cloud_shadow_fraction+a.nodata_defective_fraction<=.2)&a.clear_land_fraction.ge(.1)
a.pivot(index=['location_id','cohort','site_id'],columns='year',values='candidate_clear_land').reset_index().to_csv(OUT/'satellite_local_candidate_pairs.csv',index=False)
a.groupby(['cohort','year']).agg(locations=('location_id','size'),candidates=('candidate_clear_land','sum'),median_cloud=('cloud_shadow_fraction','median'),median_clear_land=('clear_land_fraction','median'),median_snow=('snow_ice_fraction','median')).reset_index().to_csv(OUT/'satellite_local_support_summary.csv',index=False)
print(a.groupby(['cohort','year','status']).size().to_string(),flush=True)
