from pathlib import Path
import geopandas as gpd,pandas as pd,numpy as np,json
from shapely.geometry import Polygon
from shapely.ops import transform,unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod,Transformer
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
g=gpd.read_file(ROOT/'work/comparison_audit/vegetation/map/PlantarcticaVegetationMap.shp')
s=pd.read_csv(OUT/'daily_ice_locations.csv');geo=Geod(ellps='WGS84')
f=Transformer.from_crs(4326,g.crs,always_xy=True).transform;b=Transformer.from_crs(g.crs,4326,always_xy=True).transform
rows=[]
for r in s.itertuples():
    for radius in [500,2000]:
        az=np.arange(0,361,5);lon,lat,_=geo.fwd(np.full(len(az),r.longitude),np.full(len(az),r.latitude),az,np.full(len(az),radius))
        circle=transform(f,Polygon(zip(lon,lat)));hits=g.iloc[g.sindex.query(circle,predicate='intersects')]
        for cls in ['Vegetation','Lichen','Snow Algae']:
            selected=hits[hits.Vegetation==cls];area=0.
            if len(selected):
                clipped=unary_union(selected.geometry).intersection(circle)
                parts=[clipped] if clipped.geom_type=='Polygon' else list(clipped.geoms)
                area=sum(abs(geo.geometry_area_perimeter(orient(transform(b,p),sign=1))[0]) for p in parts if p.geom_type=='Polygon')
            rows.append(dict(location_id=r.location_id,site_id=r.site_id,cohort=r.cohort,radius_m=radius,vegetation_class=cls,mapped_area_m2=area,detected_polygon_count=len(selected),no_detection_is_not_absence=True,time_support='2017-2023_composite',annual_change_available=False))
d=pd.DataFrame(rows);d.to_csv(OUT/'vegetation_all_location_support.csv',index=False)
summary=d.assign(positive=d.mapped_area_m2>0).groupby(['cohort','radius_m','vegetation_class']).agg(locations=('location_id','size'),positive_locations=('positive','sum')).reset_index()
summary.to_csv(OUT/'vegetation_all_location_summary.csv',index=False);print(summary.to_string(index=False))
