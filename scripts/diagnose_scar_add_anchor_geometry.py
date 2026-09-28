#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import requests
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform as shp_transform

LAYER=(
 "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
 "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer/1"
)
POINTS={
 "torgersen":{"lon":-64.073,"lat":-64.772,"distance":0},
 "king_george":{"lon":-58.40,"lat":-62.20,"distance":5000},
 "laurie_island":{"lon":-44.60,"lat":-60.75,"distance":5000},
 "cape_crozier":{"lon":169.23,"lat":-77.45,"distance":5000},
}

def get(**params):
 r=requests.get(LAYER+"/query",params={"f":"json",**params},timeout=120)
 r.raise_for_status(); x=r.json()
 if "error" in x: raise RuntimeError(x["error"])
 return x

def point_fids(lon,lat,distance):
 geom=json.dumps({"x":lon,"y":lat,"spatialReference":{"wkid":4326}})
 params={
  "where":"surface='land'",
  "geometry":geom,"geometryType":"esriGeometryPoint","inSR":4326,
  "spatialRel":"esriSpatialRelIntersects","returnIdsOnly":"true",
 }
 if distance:
  params["distance"]=distance; params["units"]="esriSRUnit_Meter"
 return sorted(int(v) for v in (get(**params).get("objectIds") or []))

def geom_for_fid(fid,out_sr):
 x=get(
  objectIds=str(fid),outFields="FID,surface",
  returnGeometry="true",outSR=out_sr,
 )
 feats=x.get("features") or []
 if not feats: return None,x.get("spatialReference")
 return feats[0].get("geometry"),x.get("spatialReference")

def esri_rings_to_polys(geometry):
 from shapely.geometry import Polygon
 rings=(geometry or {}).get("rings") or []
 polys=[]
 for ring in rings:
  if len(ring)<4: continue
  p=Polygon([(float(x),float(y)) for x,y,*_ in ring])
  if not p.is_valid: p=p.buffer(0)
  if not p.is_empty: polys.append(p)
 if not polys: return None
 g=polys[0]
 for p in polys[1:]: g=g.symmetric_difference(p)
 if not g.is_valid: g=g.buffer(0)
 return g

def main():
 p=argparse.ArgumentParser(); p.add_argument("--out",type=Path,required=True); a=p.parse_args()
 tr=Transformer.from_crs(4326,3031,always_xy=True)
 out={"schema_version":1,"diagnostic_id":"mina-scar-add-anchor-fid-geometry-v1","points":{}}
 for name,rec in POINTS.items():
  fids=point_fids(rec["lon"],rec["lat"],rec["distance"])
  px,py=tr.transform(rec["lon"],rec["lat"])
  pt=Point(px,py)
  rows=[]
  for fid in fids[:5]:
   g3031,sr3031=geom_for_fid(fid,3031)
   local=esri_rings_to_polys(g3031) if g3031 else None
   first3031=None
   if g3031 and g3031.get("rings") and g3031["rings"][0]:
    first3031=g3031["rings"][0][0][:2]
   g4326,sr4326=geom_for_fid(fid,4326)
   first4326=None
   if g4326 and g4326.get("rings") and g4326["rings"][0]:
    first4326=g4326["rings"][0][0][:2]
   rows.append({
    "fid":fid,
    "service_spatial_reference_3031":sr3031,
    "service_spatial_reference_4326":sr4326,
    "first_coord_3031":first3031,
    "first_coord_4326":first4326,
    "local_point_3031":[px,py],
    "local_distance_to_reconstructed_m":None if local is None else float(pt.distance(local)),
    "local_covers_point":False if local is None else bool(local.covers(pt)),
    "local_bounds_3031":None if local is None else list(local.bounds),
   })
  out["points"][name]={
   **rec,
   "service_match_fids":fids,
   "sample_geometry_checks":rows,
  }
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps(out,indent=2,sort_keys=True))
 return 0
if __name__=="__main__": raise SystemExit(main())
