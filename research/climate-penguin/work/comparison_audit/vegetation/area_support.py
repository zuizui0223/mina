from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import transform,unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod,Transformer
import json
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'outputs/comparison_audit'
g=gpd.read_file(ROOT/'work/comparison_audit/vegetation/map/PlantarcticaVegetationMap.shp')
g=g[g.Vegetation.isin(['Vegetation','Lichen'])]
sites=pd.read_csv(ROOT/'work/data_audit/mapppdr/sites.csv')
forward=Transformer.from_crs(4326,g.crs,always_xy=True).transform
back=Transformer.from_crs(g.crs,4326,always_xy=True).transform
geod=Geod(ellps='WGS84'); rows=[]
for r in sites.itertuples():
    az=np.linspace(0,360,73)
    lon,lat,_=geod.fwd(np.repeat(r.longitude,len(az)),np.repeat(r.latitude,len(az)),az,np.repeat(2000,len(az)))
    b=transform(forward,Polygon(zip(lon,lat)))
    hits=g.iloc[g.sindex.query(b,predicate='intersects')]
    area=0.
    if len(hits):
        union=unary_union(hits.geometry).intersection(b)
        polys=[union] if union.geom_type=='Polygon' else list(union.geoms)
        area=sum(abs(geod.geometry_area_perimeter(orient(transform(back,p),sign=1))[0]) for p in polys if p.geom_type=='Polygon')
    rows.append(dict(site_id=r.site_id,site_name=r.site_name,mapped_terrestrial_union_area_2km_m2=area,no_polygon_is_not_verified_absence=True))
a=pd.DataFrame(rows);a.to_csv(OUT/'vegetation_2km_mapped_area.csv',index=False)
c=pd.read_csv(OUT/'candidate_series.csv')
c=c.merge(a,on=['site_id','site_name'],validate='many_to_one')
c.to_csv(OUT/'candidate_series_vegetation_support.csv',index=False)
p=pd.read_csv(OUT/'mapppd_unambiguous_site_seasons.csv');p=p[p.season.between(2017,2023)]
q=p.merge(c[['site_id','species_id']],on=['site_id','species_id'],validate='many_to_one')
result=dict(candidate_site_species=len(c),candidate_unique_sites=c.site_id.nunique(),candidate_with_mapped_area_site_species=int((c.mapped_terrestrial_union_area_2km_m2>0).sum()),candidate_with_mapped_area_unique_sites=c.loc[c.mapped_terrestrial_union_area_2km_m2>0,'site_id'].nunique(),candidate_composite_period_site_seasons=len(q),candidate_composite_period_unique_sites=q.site_id.nunique(),candidate_composite_period_site_species=len(q[['site_id','species_id']].drop_duplicates()))
(OUT/'vegetation_candidate_summary.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
