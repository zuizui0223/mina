from pathlib import Path
import pandas as pd,numpy as np,geopandas as gpd
from pyproj import Geod,Transformer
from shapely.geometry import Polygon
from shapely.ops import transform,unary_union
from shapely.geometry.polygon import orient
R=Path.cwd();P=R/'work/spatial_feasibility/signy';O=R/'outputs/spatial_feasibility';O.mkdir(exist_ok=True,parents=True)
fixed=pd.read_csv(R/'outputs/signy_exploration/matched_counts.csv').query('species != "Shag"')[['species','colony']].drop_duplicates()
rows=[]
for species,file in [('Adelie','GPS Adelie Colony.csv'),('Chinstrap','GPS Chinstrap Colonies.csv')]:
 d=pd.read_csv(P/file);d.columns=['colony','location','latitude','longitude']+list(d.columns[4:]);d['colony']=d.colony.str.replace(' ','');d['species']=species;rows+=d[['species','colony','location','latitude','longitude']].to_dict('records')
x=fixed.merge(pd.DataFrame(rows),on=['species','colony'],validate='one_to_one');x['GPS_approx_accuracy_m']=6.096;x['coordinate_date']='not supplied';x['geometry']='colony reference point; not boundary';x.to_csv(O/'signy_gps_crosswalk.csv',index=False)
g=gpd.read_file(R/'work/comparison_audit/vegetation/map/PlantarcticaVegetationMap.shp');geo=Geod(ellps='WGS84');fwd=Transformer.from_crs(4326,g.crs,always_xy=True).transform;back=Transformer.from_crs(g.crs,4326,always_xy=True).transform
v=[];pairs=[]
for i,r in x.iterrows():
 for _,s in x.iloc[i+1:].iterrows():
  dd=geo.inv(r.longitude,r.latitude,s.longitude,s.latitude)[2]
  if dd<100:pairs.append(dict(colony1=r.colony,colony2=s.colony,distance_m=dd))
 for rad in [25,50,100,200]:
  az=np.linspace(0,360,145);lon,lat,_=geo.fwd(np.repeat(r.longitude,len(az)),np.repeat(r.latitude,len(az)),az,np.repeat(rad,len(az)));b=transform(fwd,Polygon(zip(lon,lat)));h=g.iloc[g.sindex.query(b,predicate='intersects')]
  for cls in ['Vegetation','Lichen','Snow Algae']:
   z=h[h.Vegetation==cls];area=0
   if len(z):
    u=transform(back,unary_union(z.geometry).intersection(b));polys=[u] if u.geom_type=='Polygon' else list(u.geoms);area=sum(abs(geo.geometry_area_perimeter(orient(a,sign=1))[0]) for a in polys if a.geom_type=='Polygon')
   v.append(dict(species=r.species,colony=r.colony,location=r.location,radius_m=rad,vegetation_class=cls,features=len(z),mapped_area_m2=area))
pd.DataFrame(v).to_csv(O/'signy_gps_vegetation_buffers.csv',index=False);pd.DataFrame(pairs).sort_values('distance_m').to_csv(O/'signy_close_point_pairs.csv',index=False)
print(x.to_string(index=False));print(pd.DataFrame(pairs).sort_values('distance_m').head(8).to_string(index=False));print(pd.DataFrame(v).query('radius_m == 100').to_string(index=False))
