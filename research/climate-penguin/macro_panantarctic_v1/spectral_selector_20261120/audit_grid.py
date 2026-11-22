"""Audit POINT-to-native-cell correspondence without reading spectral values."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import planetary_computer
import rasterio
import requests

ROOT=Path(__file__).parent

def main():
    d=pd.read_csv(ROOT/'source_positive_records.csv')
    m=pd.read_csv(ROOT/'scene_matches.csv')
    items={i['id']:i for f in (ROOT/'metadata_cache').glob('*.json') for i in json.loads(f.read_text())}
    rows=[]
    for product,g in d.groupby('Landsat.Product.Identifier.L1'):
        matched=m[m.original_product.eq(product)]
        if len(matched)!=1 or matched.iloc[0].n_l2_matches!=1:
            raise ValueError('Scene identity missing/ambiguous')
        scene=matched.iloc[0].scene_id
        p=items[scene]['properties'];t=p['proj:transform']
        if p['proj:epsg']!=3031 or t[1]!=0 or t[3]!=0 or abs(t[0])!=30 or abs(t[4])!=30:
            raise ValueError('Unsupported native grid')
        dates=pd.to_datetime(g[['year','month','day']]).dt.strftime('%Y%m%d')
        if not dates.eq(product.split('_')[3]).all():raise ValueError('Acquisition date mismatch')
        x=(g.easting-t[2])/t[0]-.5;y=(g.northing-t[5])/t[4]-.5
        dx=abs(x-np.round(x))*30;dy=abs(y-np.round(y))*30
        inside=(x>=-.5)&(y>=-.5)&(x<p['proj:shape'][1]-.5)&(y<p['proj:shape'][0]-.5)
        rows.append(dict(original_product=product,scene_id=scene,epsg=p['proj:epsg'],
          positive_rows=len(g),center_aligned_rows=int(((dx<1e-5)&(dy<1e-5)).sum()),
          boundary_both_axes_rows=int(((abs(dx-15)<1e-5)&(abs(dy-15)<1e-5)).sum()),
          inside_rows=int(inside.sum()),max_center_offset_axis_m=float(np.maximum(dx,dy).max())))
    a=pd.DataFrame(rows);a.to_csv(ROOT/'grid_alignment.csv',index=False,lineterminator='\n')
    # One earliest training acquisition per region, source-only, before raster access.
    chosen=d[d.phase.eq('train')].sort_values(['year','month','day','site_id','Landsat.Product.Identifier.L1']).groupby('region',sort=True).head(1)
    receipts=[]
    for _,g in chosen.iterrows():
        product=g['Landsat.Product.Identifier.L1'];scene=m.loc[m.original_product.eq(product),'scene_id'].iloc[0]
        url='https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2/items/'+scene
        try:
            response=requests.get(url,timeout=45);response.raise_for_status();item=response.json()
            if item['id']!=scene:raise ValueError('Mirror scene mismatch')
            href=item['assets']['red']['href']
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='YES',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.TIF,.tif'):
                with rasterio.open(planetary_computer.sign(href)) as r:
                    actual=list(r.transform)[:6];expected=items[scene]['properties']['proj:transform'][:6]
                    cx,cy=r.xy(*r.index(g.easting,g.northing))
                    receipts.append(dict(region=g.region,site_id=g.site_id,scene_id=scene,
                      status='HEADER_READ',unsigned_asset=href,crs=str(r.crs),
                      area_or_point=r.tags().get('AREA_OR_POINT'),transform=actual,
                      matches_catalog_transform=bool(np.allclose(actual,expected)),
                      point_easting=g.easting,point_northing=g.northing,
                      containing_cell_center_easting=float(cx),containing_cell_center_northing=float(cy)))
        except Exception as e:
            receipts.append(dict(region=g.region,site_id=g.site_id,scene_id=scene,status='ACCESS_ERROR',error=str(e).split('?')[0]))
        print(g.region,receipts[-1]['status'],flush=True)
    (ROOT/'native_header_receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8',newline='\n')
    summary={k:int(a[k].sum()) for k in ['positive_rows','center_aligned_rows','boundary_both_axes_rows','inside_rows']}
    summary.update(native_header_success=sum(r['status']=='HEADER_READ' for r in receipts),
                   sampled_regions=len(receipts),source_geometry='POINT, EPSG:3031',
                   original_pixel_footprint_verified=False,
                   status='SOURCE_FOOTPRINT_NOT_VERIFIED',classifier_fitted=False,new_isotope_estimated=False)
    (ROOT/'grid_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(summary)

if __name__=='__main__':main()
