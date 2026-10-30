"""Overlay fixed mapped vegetation on existing NDVI pixels; not annual cover."""
from pathlib import Path
import argparse,hashlib,json
import geopandas as gpd
import pandas as pd,numpy as np
from shapely.geometry import Point
from shapely.ops import transform,unary_union
from pyproj import Transformer
from rasterio.features import rasterize
from rasterio.transform import from_origin
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/ndvi_vegetation_overlay_v1';OUT.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--map',type=Path,required=True);args=p.parse_args()
g=gpd.read_file(args.map);g=g[g.Vegetation.isin(['Vegetation','Lichen'])].copy();assert g.geometry.is_valid.all()
source=ROOT/'outputs/vegetation_annual_ndvi_v1';annual=pd.read_csv(source/'checked_support.csv');pairs=pd.read_csv(source/'same_pixel_changes.csv')
locations=pd.read_csv(ROOT/'outputs/climate_penguin/daily_ice_locations.csv');locations=locations[locations.cohort.eq('macro_40')].set_index('site_id')
rr,cc=np.indices((50,50));inside=((-490+cc*20)**2+(490-rr*20)**2<=500**2);grid=from_origin(-500,500,20,20)
masks={};site_rows=[];pair_rows=[]
for site in sorted(annual.site_id.unique()):
 l=locations.loc[site];local=f'+proj=aeqd +lat_0={l.latitude} +lon_0={l.longitude} +datum=WGS84 +units=m +no_defs';circle=Point(0,0).buffer(500,resolution=128)
 query=transform(Transformer.from_crs(local,g.crs,always_xy=True).transform,circle)
 hits=g.iloc[g.sindex.query(query,predicate='intersects')].to_crs(local)
 union=unary_union(hits.geometry).intersection(circle) if len(hits) else circle.difference(circle)
 for touched in [False,True]:
  mask=rasterize([(union,1)],out_shape=(50,50),transform=grid,all_touched=touched).astype(bool)&inside if not union.is_empty else np.zeros((50,50),bool)
  if not touched:
   independent=np.array([union.covers(Point(-490+j*20,490-i*20)) for i,j in zip(rr.ravel(),cc.ravel())]).reshape(50,50)&inside
   assert np.array_equal(mask,independent)
  kind='any_overlap' if touched else 'pixel_center';masks[(site,kind)]=mask
  site_rows.append(dict(site_id=site,mask=kind,mapped_polygons=len(hits),mapped_union_area_500m_m2=union.area,mapped_pixels=int(mask.sum()),circle_pixels=int(inside.sum())))
for r in pairs.itertuples():
 with np.load(source/'checked_arrays'/f'{r.site_id}_{r.first_year}.npz') as a,np.load(source/'checked_arrays'/f'{r.site_id}_{r.last_year}.npz') as b:
  x=a['annual_median'];y=b['annual_median'];common=np.isfinite(x)&np.isfinite(y);assert common.sum()==r.common_pixels
  for kind in ['pixel_center','any_overlap']:
   veg=common&masks[(r.site_id,kind)];other=common&~masks[(r.site_id,kind)]
   rec=dict(site_id=r.site_id,first_year=r.first_year,last_year=r.last_year,mask=kind,common_pixels=r.common_pixels,mapped_common_pixels=int(veg.sum()),unmapped_common_pixels=int(other.sum()),mapped_median_ndvi_change=float(np.median(y[veg]-x[veg])) if veg.any() else np.nan,unmapped_median_ndvi_change=float(np.median(y[other]-x[other])) if other.any() else np.nan)
   assert rec['mapped_common_pixels']+rec['unmapped_common_pixels']==r.common_pixels
   pair_rows.append(rec)
a=pd.DataFrame(site_rows);b=pd.DataFrame(pair_rows);a.to_csv(OUT/'site_mapped_support.csv',index=False);b.to_csv(OUT/'pair_mapped_changes.csv',index=False)
summary=[]
for kind,q in b.groupby('mask'):
 summary.append(dict(mask=kind,pairs=len(q),sites=q.site_id.nunique(),pairs_any_mapped_pixels=int((q.mapped_common_pixels>0).sum()),sites_any_mapped_pixels=q.loc[q.mapped_common_pixels>0,'site_id'].nunique(),pairs_100_mapped_pixels=int((q.mapped_common_pixels>=100).sum())))
s=pd.DataFrame(summary);s.to_csv(OUT/'support_summary.csv',index=False)
np.savez_compressed(OUT/'mapped_masks.npz',**{site+'_'+kind:mask for (site,kind),mask in masks.items()})
checks=dict(site_masks=len(a),pair_mask_comparisons=len(b),pixel_center_independent_checks=len(annual.site_id.unique()),classification='fixed_2017_2023_map_not_annual_truth',unmapped_is_not_verified_absence=True,map_hashes={f.suffix:hashlib.sha256(f.read_bytes()).hexdigest() for f in args.map.parent.glob(args.map.stem+'.*')})
(OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n');print(s.to_string(index=False));print(a[a['mask']=='pixel_center'].to_string(index=False))
