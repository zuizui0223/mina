#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SERVICE=(
 "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
 "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer/1"
)
POINTS={
 "torgersen":(-64.073,-64.772),
 "king_george":(-58.40,-62.20),
 "laurie_island":(-44.60,-60.75),
 "cape_crozier":(169.23,-77.45),
}

def session():
 s=requests.Session()
 retry=Retry(total=5,backoff_factor=.5,status_forcelist=(429,500,502,503,504),allowed_methods=("GET",),respect_retry_after_header=True)
 s.mount("https://",HTTPAdapter(max_retries=retry))
 s.headers.update({"User-Agent":"mina-scar-add-point-diagnostic/1.0"})
 return s

def get(s,**params):
 r=s.get(SERVICE+"/query",params={"f":"json",**params},timeout=120)
 r.raise_for_status()
 x=r.json()
 if "error" in x: raise RuntimeError(x["error"])
 return x

def count(s,lon,lat,distance,where):
 geom=json.dumps({"x":lon,"y":lat,"spatialReference":{"wkid":4326}})
 params={
  "where":where,
  "geometry":geom,
  "geometryType":"esriGeometryPoint",
  "inSR":4326,
  "spatialRel":"esriSpatialRelIntersects",
  "returnCountOnly":"true",
 }
 if distance:
  params["distance"]=distance
  params["units"]="esriSRUnit_Meter"
 return int(get(s,**params).get("count") or 0)

def main():
 p=argparse.ArgumentParser(); p.add_argument("--out",type=Path,required=True); a=p.parse_args()
 s=session()
 distinct=get(s,where="1=1",outFields="surface",returnDistinctValues="true",returnGeometry="false")
 surfaces=sorted({str((f.get("attributes") or {}).get("surface")) for f in distinct.get("features",[])})
 result={"schema_version":1,"diagnostic_id":"mina-scar-add-point-diagnostic-v1","surface_values":surfaces,"points":{}}
 for name,(lon,lat) in POINTS.items():
  result["points"][name]={"lon":lon,"lat":lat,"counts":{}}
  for d in (0,5000):
   result["points"][name]["counts"][str(d)]={
    "all":count(s,lon,lat,d,"1=1"),
    "land":count(s,lon,lat,d,"surface='land'"),
   }
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps(result,indent=2,sort_keys=True))
 return 0

if __name__=="__main__": raise SystemExit(main())
