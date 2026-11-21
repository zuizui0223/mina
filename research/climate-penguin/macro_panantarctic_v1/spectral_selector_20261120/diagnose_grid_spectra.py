"""Fixed 12 site-scene pairs (11 scenes), training-only SR diagnostic, no isotope."""
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import planetary_computer
import rasterio
from rasterio.windows import Window
import requests

ROOT=Path(__file__).parent
BANDS=('blue','green','red','nir08','swir16','swir22')
PIXEL_MASK=sum(1<<i for i in (0,1,3,4))
RAD_MASK=sum(1<<i for i in (0,1,2,3,4,6,9))

def overlap_cells(x,y,dx,dy,t):
    """Exact rectangles on the verified north-up 30 m grid; no point shift."""
    left,right=x-dx/2,x+dx/2;bottom,top=y-dy/2,y+dy/2
    c0=math.floor((left-t.c)/t.a);c1=math.floor((right-t.c)/t.a)
    r0=math.floor((top-t.f)/t.e);r1=math.floor((bottom-t.f)/t.e)
    result=[]
    for r in range(r0,r1+1):
        for c in range(c0,c1+1):
            l=t.c+c*t.a;rr=l+t.a;tt=t.f+r*t.e;bb=tt+t.e
            area=max(0,min(right,rr)-max(left,l))*max(0,min(top,tt)-max(bottom,bb))
            if area>1e-7:result.append((r,c,area))
    return result

def one(receipt,d,grids,matches):
    site=receipt['site_id'];scene=receipt['scene_id']
    product=matches.loc[matches.scene_id.eq(scene),'original_product'].iloc[0]
    g=d[d.site_id.eq(site)&d['Landsat.Product.Identifier.L1'].eq(product)]
    if g.empty or not g.phase.eq('train').all():raise ValueError('Pilot must use fixed training rows')
    fit=grids[grids.site_id.eq(site)]
    if len(fit)!=1 or fit.iloc[0].status!='UNIQUE_LATTICE':raise ValueError('No fixed training lattice')
    dx=float(fit.iloc[0].dx_m);dy=abs(float(fit.iloc[0].dy_m))
    cache=ROOT/'spectral_diagnostic_cache';cache.mkdir(exist_ok=True)
    item_path=cache/f'{scene}.json'
    if item_path.exists():item=json.loads(item_path.read_text())
    else:
        response=requests.get('https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2/items/'+scene,timeout=50)
        response.raise_for_status();item=response.json()
        if item['id']!=scene:raise ValueError('Mirror identity mismatch')
        item_path.write_text(json.dumps(item),encoding='utf-8')
    mtl_path=cache/f'{scene}_mtl.json'
    if mtl_path.exists():mtl=json.loads(mtl_path.read_text())
    else:
        response=requests.get(planetary_computer.sign(item['assets']['mtl.json']['href']),timeout=50)
        response.raise_for_status();mtl=response.json();mtl_path.write_text(json.dumps(mtl),encoding='utf-8')
    metadata=mtl['LANDSAT_METADATA_FILE']
    l1=metadata['LEVEL1_PROCESSING_RECORD']['LANDSAT_PRODUCT_ID']
    arrays={};native_transform=None;window=None
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='YES',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.TIF,.tif'):
        for band in (*BANDS,'qa_pixel','qa_radsat'):
            asset=item['assets'][band]
            with rasterio.open(planetary_computer.sign(asset['href'])) as src:
                if src.crs.to_epsg()!=3031 or tuple(src.res)!=(30.0,30.0):raise ValueError('Native grid changed')
                if native_transform is None:
                    native_transform=src.transform
                    r0,c0=src.index(float(g.easting.min()-dx),float(g.northing.max()+dy))
                    r1,c1=src.index(float(g.easting.max()+dx),float(g.northing.min()-dy))
                    if r0<0 or c0<0 or r1>=src.height or c1>=src.width:raise ValueError('Pilot window outside image')
                    window=Window(c0,r0,c1-c0+1,r1-r0+1)
                elif native_transform!=src.transform:raise ValueError('Bands not co-registered')
                local=cache/f'{site}_{scene}_{band}.npy'
                if local.exists():a=np.load(local)
                else:
                    a=src.read(1,window=window);np.save(local,a)
                if a.shape!=(int(window.height),int(window.width)):raise ValueError('Cached window shape drift')
                arrays[band]=a
                if band in BANDS:
                    rb=asset['raster:bands'][0]
                    if (rb['scale'],rb['offset'],rb['nodata'])!=(2.75e-5,-.2,0):raise ValueError('Unexpected SR scale')
    valid=(arrays['qa_pixel']&PIXEL_MASK)==0
    valid &= (arrays['qa_radsat']&RAD_MASK)==0
    for b in BANDS:valid &= arrays[b]!=0
    rr0,cc0=int(window.row_off),int(window.col_off)
    rows=[]
    for _,p in g.iterrows():
        cells=overlap_cells(p.easting,p.northing,dx,dy,native_transform)
        covered=sum(a for r,c,a in cells)
        if not np.isclose(covered,dx*dy,rtol=1e-8):raise ValueError('Incomplete footprint')
        r=math.floor((p.northing-native_transform.f)/native_transform.e)-rr0
        c=math.floor((p.easting-native_transform.c)/native_transform.a)-cc0
        point_ok=bool(valid[r,c]);area_ok=all(valid[rr-rr0,cc-cc0] for rr,cc,a in cells)
        record=dict(site_id=site,region=p.region,scene_id=scene,season=int(p.season),cell=int(p.cell),
          source_point_easting=p.easting,source_point_northing=p.northing,
          assumed_rectangle_area_m2=covered,n_contributing_native_cells=len(cells),
          point_qa_valid=point_ok,all_overlap_qa_valid=bool(area_ok),
          source_l1_product_exact_match=l1==product)
        for b in BANDS:
            point=arrays[b][r,c]*2.75e-5-.2 if point_ok else np.nan
            avg=sum((arrays[b][rr-rr0,cc-cc0]*2.75e-5-.2)*a/covered for rr,cc,a in cells) if area_ok else np.nan
            record[f'{b}_point_sr']=point;record[f'{b}_assumed_area_sr']=avg
            record[f'{b}_area_minus_point']=avg-point
        rows.append(record)
    meta=dict(site_id=site,region=receipt['region'],scene_id=scene,original_product=product,
      metadata_l1_product=l1,exact_l1_product_match=l1==product,
      projection_attributes=metadata['PROJECTION_ATTRIBUTES'],
      level1_projection_parameters=metadata['LEVEL1_PROJECTION_PARAMETERS'],
      original_study_resampling_known=False)
    print(site,len(rows),'rows extracted',flush=True)
    return rows,meta

def main():
    d=pd.read_csv(ROOT/'source_positive_records.csv');grids=pd.read_csv(ROOT/'training_recovered_lattices.csv')
    matches=pd.read_csv(ROOT/'scene_matches.csv');receipts=json.loads((ROOT/'native_header_receipts.json').read_text())
    with ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(lambda r:one(r,d,grids,matches),receipts))
    rows=pd.DataFrame([row for group,meta in results for row in group])
    rows.to_csv(ROOT/'historical_sr_grid_diagnostic.csv',index=False,lineterminator='\n')
    support=rows.groupby(['site_id','region']).agg(rows=('cell','size'),point_qa_valid=('point_qa_valid','sum'),all_overlap_qa_valid=('all_overlap_qa_valid','sum')).reset_index()
    support.to_csv(ROOT/'historical_sr_grid_support.csv',index=False,lineterminator='\n')
    metrics=[]
    for b in BANDS:
        v=rows[f'{b}_area_minus_point'].dropna().abs()
        metrics.append(dict(band=b,paired_rows=len(v),median_absolute_difference=float(v.median()),
          maximum_absolute_difference=float(v.max()),mean_absolute_difference=float(v.mean())))
    pd.DataFrame(metrics).to_csv(ROOT/'historical_sr_grid_differences.csv',index=False,lineterminator='\n')
    differences=[f'{b}_area_minus_point' for b in BANDS]
    site_medians=rows.groupby(['site_id','region'])[differences].agg(
        lambda v:float(v.dropna().abs().median()) if v.notna().any() else np.nan).reset_index()
    site_medians.to_csv(ROOT/'historical_sr_grid_site_medians.csv',index=False,lineterminator='\n')
    (ROOT/'historical_l1_metadata_receipts.json').write_text(json.dumps([m for _,m in results],indent=2)+'\n',encoding='utf-8',newline='\n')
    print(support.to_string(index=False));print(pd.DataFrame(metrics).to_string(index=False))

if __name__=='__main__':main()
