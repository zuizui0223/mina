"""Read actual pixels for two catalog-screen examples; no colony classifier."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/climate_penguin'
RAW=ROOT/'work/climate_penguin/satellite_crops';RAW.mkdir(exist_ok=True)
d=pd.read_csv(OUT/'satellite_january_catalog_screen.csv')
# Signy may be represented by a camera rather than the 40-site historical cohort.
signy=d[(d.latitude.between(-60.8,-60.6)) & (d.longitude.between(-45.8,-45.4)) & (d.year==2024)]
chosen=[d[(d.site_id=='ADAR') & (d.year==2019)].iloc[0]]
if len(signy): chosen.append(signy.iloc[0])
records=[];panels=[]
for row in chosen:
    j=json.loads((ROOT/row.cached_response).read_text())
    f=min(j['features'],key=lambda a:a['properties'].get('eo:cloud_cover',100))
    name=f['id']; arrays=[]; meta=None
    for band in ['nir','green','blue']:
        href=f['assets'][band]['href']
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=60):
            with rasterio.open(href) as src:
                x,y=transform('EPSG:4326',src.crs,[row.longitude],[row.latitude])
                win=from_bounds(x[0]-1500,y[0]-1500,x[0]+1500,y[0]+1500,src.transform).round_offsets().round_lengths()
                a=src.read(1,window=win,boundless=True,fill_value=0)
                if meta is None:
                    meta=src.profile.copy();meta.update(height=a.shape[0],width=a.shape[1],count=3,transform=src.window_transform(win))
                arrays.append(a)
    stack=np.stack(arrays)
    with rasterio.open(RAW/(name+'_NIR_G_B.tif'),'w',**meta) as dst:dst.write(stack)
    valid=np.all(stack>0,axis=0)
    rgb=[]
    for a in stack:
        lo,hi=np.percentile(a[valid],[2,98]) if valid.any() else (0,1)
        rgb.append(np.uint8(np.clip((a.astype(float)-lo)/max(hi-lo,1),0,1)*255))
    im=Image.fromarray(np.stack(rgb,axis=-1)).resize((600,600))
    canvas=Image.new('RGB',(600,655),'white');canvas.paste(im,(0,55))
    draw=ImageDraw.Draw(canvas);draw.text((8,6),name,fill='black');draw.text((8,24),'3 km x 3 km; NIR / green / blue; per-band stretch',fill='black')
    canvas.save(OUT/(name+'_preview.png'));panels.append(canvas)
    records.append({'site_id':row.site_id,'scene_id':name,'scene_cloud_percent':f['properties'].get('eo:cloud_cover'),'valid_pixel_fraction':float(valid.mean()),'latitude':row.latitude,'longitude':row.longitude,'datetime':f['properties']['datetime'],'bands':'nir|green|blue','classification':'not performed'})
    print(name,'read pixels',stack.shape,flush=True)
pd.DataFrame(records).to_csv(OUT/'satellite_pixel_sample_manifest.csv',index=False)
