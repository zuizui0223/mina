"""Matched dates, raw reflectance crops and offset sensitivity; no greening claim."""
from pathlib import Path
import json,hashlib
import pandas as pd,numpy as np,rasterio
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.windows import from_bounds
from rasterio.transform import from_origin
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
CACHE=ROOT/'work/climate_penguin/reflectance_pairs';CACHE.mkdir(exist_ok=True)
catalog=pd.read_csv(OUT/'satellite_january_catalog_screen.csv');features={}
for r in catalog[catalog.year.isin([2019,2024])].itertuples():
    for f in json.loads((ROOT/r.cached_response).read_text(encoding='utf-8'))['features']:features[f['id']]=f
locations=pd.read_csv(OUT/'daily_ice_locations.csv').set_index('location_id')
GRID=from_origin(-500,500,20,20);rr,cc=np.indices((50,50));INSIDE=((-490+cc*20)**2+(490-rr*20)**2<=500**2)
pairs=[];rows=[]
for file in sorted((ROOT/'work/climate_penguin/scl_multiscene').glob('*_2019.json')):
    a=json.loads(file.read_text());b=json.loads(file.with_name(a['location_id']+'_2024.json').read_text());choices=[]
    for x in a['scenes']:
        for y in b['scenes']:
            if x['status']!='ok' or y['status']!='ok' or min(x['clear_land_fraction'],y['clear_land_fraction'])<.1:continue
            gap=abs(int(x['datetime'][8:10])-int(y['datetime'][8:10]))
            if gap<=5:choices.append((gap,-min(x['clear_land_fraction'],y['clear_land_fraction']),x['scene_id'],y['scene_id']))
    if not choices:continue
    gap,_,s1,s2=min(choices);id=a['location_id'];loc=locations.loc[id]
    crs=f'+proj=aeqd +lat_0={loc.latitude} +lon_0={loc.longitude} +datum=WGS84 +units=m +no_defs'
    pair=dict(location_id=id,site_id=a['site_id'],cohort=a['cohort'],date_gap_days=gap,scene2019=s1,scene2024=s2);masks=[]
    for year,scene in [(2019,s1),(2024,s2)]:
        f=features[scene];meta=dict(location_id=id,site_id=a['site_id'],year=year,scene_id=scene,datetime=f['properties']['datetime'],baseline=f['properties'].get('s2:processing_baseline'),boa_offset_applied=f['properties'].get('earthsearch:boa_offset_applied'))
        arrays=[]
        for band in ['red','nir','scl']:
            asset=f['assets'][band];meta[band+'_url']=asset['href'];target=np.full((50,50),np.nan,np.float32)
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=30):
                with rasterio.open(asset['href']) as src:
                    bounds=transform_bounds(crs,src.crs,-540,-540,540,540,densify_pts=21);win=from_bounds(*bounds,src.transform).round_offsets().round_lengths()
                    raw=src.read(1,window=win,boundless=True,fill_value=0)
                    reproject(raw,target,src_transform=src.window_transform(win),src_crs=src.crs,dst_transform=GRID,dst_crs=crs,src_nodata=0,dst_nodata=np.nan,resampling=Resampling.nearest if band=='scl' else Resampling.average)
            arrays.append(target)
            if band!='scl':
                rb=asset['raster:bands'][0];meta[band+'_scale']=rb.get('scale',1);meta[band+'_offset']=rb.get('offset',0)
        red,nir,scl=arrays;mask=INSIDE&np.isin(scl,[4,5])&np.isfinite(red)&np.isfinite(nir);masks.append(mask)
        r=red*meta['red_scale'];n=nir*meta['nir_scale']
        r2=r+meta['red_offset'];n2=n+meta['nir_offset']
        with np.errstate(divide='ignore',invalid='ignore'):
            ndvi=(n-r)/(n+r);ndvi2=(n2-r2)/(n2+r2)
        good=mask&(n+r>1e-6)&(n2+r2>1e-6)&np.isfinite(ndvi)&np.isfinite(ndvi2)
        meta.update(clear_land_pixels=int(mask.sum()),both_interpretations_pixels=int(good.sum()),ndvi_scale_only_median=float(np.median(ndvi[good])) if good.any() else None,ndvi_asset_offset_median=float(np.median(ndvi2[good])) if good.any() else None,median_absolute_ndvi_difference=float(np.median(abs(ndvi[good]-ndvi2[good]))) if good.any() else None,offset_negative_reflectance_pixels=int((mask&((r2<0)|(n2<0))).sum()))
        path=CACHE/f'{id}_{year}_raw_red_nir_scl.tif'
        with rasterio.open(path,'w',driver='GTiff',height=50,width=50,count=3,dtype='float32',crs=crs,transform=GRID,nodata=np.nan,compress='deflate') as dst:
            dst.write(np.stack(arrays));dst.descriptions=('raw_red_DN_20m_average','raw_nir_DN_20m_average','SCL_nearest')
        meta['raw_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();meta['raw_crop']=str(path.relative_to(ROOT));rows.append(meta)
        print(id,year,'land pixels',mask.sum(),flush=True)
    pair['common_clear_land_pixels']=int((masks[0]&masks[1]).sum());pair['circle_pixels']=int(INSIDE.sum());pairs.append(pair)
pd.DataFrame(rows).to_csv(OUT/'reflectance_offset_sensitivity.csv',index=False)
pd.DataFrame(pairs).to_csv(OUT/'reflectance_matched_date_pairs.csv',index=False)
print('pairs',len(pairs),flush=True)
