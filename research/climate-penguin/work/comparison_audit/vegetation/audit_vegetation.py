from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import transform
from pyproj import Geod,Transformer
import json,hashlib,urllib.request,urllib.error

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/'work/comparison_audit/vegetation'; OUT=ROOT/'outputs/comparison_audit'; OUT.mkdir(parents=True,exist_ok=True)
g=gpd.read_file(DATA/'map/PlantarcticaVegetationMap.shp')
sites=pd.read_csv(ROOT/'work/data_audit/mapppdr/sites.csv')
obs=pd.read_csv(ROOT/'work/data_audit/mapppdr/penguin_obs.csv')
trans=Transformer.from_crs(4326,g.crs,always_xy=True).transform
geod=Geod(ellps='WGS84'); rows=[]
for r in sites.itertuples():
    for radius in [500,2000,5000]:
        az=np.linspace(0,360,73)
        lon,lat,_=geod.fwd(np.repeat(r.longitude,len(az)),np.repeat(r.latitude,len(az)),az,np.repeat(radius,len(az)))
        b=transform(trans,Polygon(zip(lon,lat)))
        hits=g.iloc[g.sindex.query(b,predicate='intersects')]
        out=dict(site_id=r.site_id,site_name=r.site_name,region=r.region,radius_m=radius)
        for label in ['Vegetation','Lichen','Snow Algae']:
            h=hits[hits.Vegetation==label]
            out[label.replace(' ','_')+'_features']=len(h)
        out['mapped_terrestrial_detected']=bool(out['Vegetation_features']+out['Lichen_features'])
        out['quality_status']='mapped detection' if out['mapped_terrestrial_detected'] else 'no polygon; absence/coverage unresolved'
        rows.append(out)
support=pd.DataFrame(rows);support.to_csv(OUT/'vegetation_mapppd_spatial_support.csv',index=False)
panel=pd.read_csv(OUT/'mapppd_unambiguous_site_seasons.csv')
focal=panel[panel.species_id.isin(['ADPE','CHPE','GEPE'])].copy()
ss=support[support.radius_m==2000][['site_id','mapped_terrestrial_detected']]
focal=focal.merge(ss,on='site_id',validate='many_to_one')
stats=[]
for species,d in focal.groupby('species_id'):
    for label,keep in [('all',d.season.notna()),('map_composite_2017_2023',d.season.between(2017,2023)),('post_composite_2024_2025',d.season.between(2024,2025))]:
        q=d[keep]
        stats.append(dict(species_id=species,period=label,site_seasons=len(q),sites=q.site_id.nunique(),sites_with_mapped_terrestrial_within_2km=q[q.mapped_terrestrial_detected].site_id.nunique(),seasons=';'.join(map(str,sorted(q.season.unique())))))
pd.DataFrame(stats).to_csv(OUT/'vegetation_temporal_overlap.csv',index=False)
summary=dict(features=len(g),crs=str(g.crs),columns=list(g.columns),classes=g.groupby('Vegetation').size().to_dict(),registered_sites=len(sites),support_by_radius=support.groupby('radius_m').mapped_terrestrial_detected.sum().to_dict(),signy=support[support.site_name.str.contains('Signy',case=False)].to_dict('records'),temporal_overlap=stats)
(OUT/'vegetation_audit_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
manifest=[]
for p in DATA.rglob('*'):
    if p.is_file():manifest.append(dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(OUT/'vegetation_source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
