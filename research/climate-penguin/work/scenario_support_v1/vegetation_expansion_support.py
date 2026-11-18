"""Outcome-blind expansion support from repeated counts and mapped vegetation."""
from pathlib import Path
import argparse,json,hashlib
import pandas as pd,numpy as np,geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union,transform
from pyproj import Transformer
from rasterio.features import rasterize
from rasterio.transform import from_origin
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/vegetation_expansion_v1';OUT.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--map',type=Path,required=True);args=p.parse_args()
cohort=pd.read_csv(ROOT/'outputs/vegetation_response_v1/site_species_cohort.csv');counts=pd.read_csv(ROOT/'outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv')
c=cohort[cohort.observed_seasons.ge(2)&cohort.positive_mapped_detection].copy()
g=gpd.read_file(args.map);g=g[g.Vegetation.isin(['Vegetation','Lichen'])];rr,cc=np.indices((50,50));inside=((-490+cc*20)**2+(490-rr*20)**2<=500**2);grid=from_origin(-500,500,20,20)
rows=[]
for r in c.drop_duplicates('site_id').itertuples():
 local=f'+proj=aeqd +lat_0={r.latitude} +lon_0={r.longitude} +datum=WGS84 +units=m +no_defs';circle=Point(0,0).buffer(500,resolution=128);query=transform(Transformer.from_crs(local,g.crs,always_xy=True).transform,circle)
 h=g.iloc[g.sindex.query(query,predicate='intersects')].to_crs(local);u=unary_union(h.geometry).intersection(circle) if len(h) else circle.difference(circle)
 mask=rasterize([(u,1)],out_shape=(50,50),transform=grid).astype(bool)&inside if not u.is_empty else np.zeros((50,50),bool)
 rows.append(dict(site_id=r.site_id,mapped_area_500m_m2=u.area,mapped_pixel_centers_500m=int(mask.sum())))
a=c.merge(pd.DataFrame(rows),on='site_id',validate='many_to_one');m=counts[counts.season.between(2017,2023)&counts.site_id.isin(a.site_id)&counts.species_id.isin(['ADPE','CHPE','GEPE'])].copy()
method=m[m.method.notna()&m.method.ne('unknown')].groupby(['site_id','species_id','method']).season.nunique().reset_index(name='same_method_years')
maxmethod=method.groupby(['site_id','species_id']).same_method_years.max().reset_index()
a=a.merge(maxmethod,on=['site_id','species_id'],how='left',validate='one_to_one');a['same_method_repeat_supported']=a.same_method_years.ge(2)
a['mapped_100_centers']=a.mapped_pixel_centers_500m.ge(100);a.to_csv(OUT/'candidate_support.csv',index=False)
selected=a[a.same_method_repeat_supported&a.mapped_100_centers].copy()
selected.to_csv(OUT/'mapped_repeat_candidates.csv',index=False)
years=m.merge(selected[['site_id','species_id']],validate='many_to_one');years['same_season_january_year']=years.season+1;years.to_csv(OUT/'candidate_count_years.csv',index=False)
receipt=dict(candidate_site_species=len(a),candidate_sites=a.site_id.nunique(),same_method_and_100_center_site_species=len(selected),same_method_and_100_center_sites=selected.site_id.nunique(),regions=selected.region.nunique(),selection_uses_ndvi_or_count_change=False,map_sha256=hashlib.sha256(args.map.read_bytes()).hexdigest())
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt);print(selected[['site_id','species_id','region','observed_season_list','mapped_pixel_centers_500m']].to_string(index=False))
