from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,pandas as pd,numpy as np,rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
d=pd.read_csv(OUT/'satellite_january_catalog_screen.csv')
r=d[(d.latitude.between(-60.8,-60.6)) & (d.longitude.between(-45.8,-45.4)) & (d.year==2024)].iloc[0]
features=json.loads((ROOT/r.cached_response).read_text())['features']
def read(f):
    result={'scene_id':f['id'],'scene_cloud_percent':f['properties'].get('eo:cloud_cover'),'datetime':f['properties']['datetime']}
    try:
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=60):
            with rasterio.open(f['assets']['scl']['href']) as src:
                x,y=transform('EPSG:4326',src.crs,[r.longitude],[r.latitude])
                w=from_bounds(x[0]-1500,y[0]-1500,x[0]+1500,y[0]+1500,src.transform).round_offsets().round_lengths()
                a=src.read(1,window=w,boundless=True,fill_value=0)
        result.update(status='ok',local_cloud_shadow_fraction=float(np.isin(a,[3,8,9,10]).mean()),local_nodata_fraction=float(np.isin(a,[0,1]).mean()),local_snow_fraction=float((a==11).mean()))
    except Exception as e:result.update(status='error',error=str(e))
    return result
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(read,features))
p=pd.DataFrame(rows).sort_values('local_cloud_shadow_fraction')
p.to_csv(OUT/'signy_january2024_local_cloud.csv',index=False)
print(p.head(6).to_string(index=False))
