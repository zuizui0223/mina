#!/usr/bin/env python3
"""Gate 1A v2: outcome-blind APBP-to-SCAR ADD land matching.

The only change from the failed v1 audit is Esri multipart ring reconstruction:
rings are combined by odd-even fill using symmetric difference rather than
orientation-based shell/hole classification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr
import requests
from pyproj import Transformer
from requests.adapters import HTTPAdapter
from shapely.geometry import Point, Polygon
from shapely.ops import transform as shapely_transform
from shapely.strtree import STRtree
from urllib3.util.retry import Retry

PINNED_MAPPPDR_COMMIT="88c73a507e0921b2541c218c71eaf16721bc6502"
SERVICE_URL=(
 "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
 "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer"
)
PRIMARY_SPECIES=("ADPE","CHPE","GEPE")
DISTANCES_M=(0,500,1000,2000,5000)
ANCHORS={
 "torgersen":(-64.073,-64.772),
 "king_george":(-58.40,-62.20),
 "laurie_island":(-44.60,-60.75),
 "cape_crozier":(169.23,-77.45),
}


def load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x: frame=x[expected]
    elif len(x)==1: frame=next(iter(x.values()))
    else: raise ValueError(f"cannot resolve {expected}: {list(x)}")
    if not isinstance(frame,pd.DataFrame): raise TypeError(expected)
    return frame


def session()->requests.Session:
    s=requests.Session()
    retry=Retry(
        total=6,backoff_factor=.8,
        status_forcelist=(429,500,502,503,504),
        allowed_methods=("GET","POST"),
        respect_retry_after_header=True,
    )
    s.mount("https://",HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent":"mina-antarctic-island-atlas-v2/1.0"})
    return s


def get(s,url,**params):
    r=s.get(url,params=params,timeout=120); r.raise_for_status()
    x=r.json()
    if "error" in x: raise RuntimeError(x["error"])
    return x


def post(s,url,**data):
    r=s.post(url,data=data,timeout=120); r.raise_for_status()
    x=r.json()
    if "error" in x: raise RuntimeError(x["error"])
    return x


def discover_layer(s):
    root=get(s,SERVICE_URL,f="json")
    found=[]
    for item in root.get("layers",[]):
        url=f"{SERVICE_URL}/{item['id']}"
        meta=get(s,url,f="json")
        fields=[str(f.get("name","")) for f in meta.get("fields",[])]
        if any(name.lower()=="surface" for name in fields):
            found.append((url,meta))
    if len(found)!=1: raise RuntimeError(f"surface layer count={len(found)}")
    return found[0]


def candidate_sites(root:Path)->pd.DataFrame:
    data=root/"data"
    sites=load_rda(data/"sites.rda","sites")
    obs=load_rda(data/"penguin_obs.rda","penguin_obs")
    nest=obs[
        obs["species_id"].isin(PRIMARY_SPECIES)
        & (obs["type"]=="nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest=nest.dropna(subset=["year"])
    units=[]
    for (site_id,species_id),local in nest.groupby(["site_id","species_id"]):
        years=sorted(set(int(y) for y in local["year"]))
        if len(years)>=5 and max(years)-min(years)>=10:
            units.append((str(site_id),str(species_id)))
    if len(units)!=152: raise ValueError(f"candidate unit drift {len(units)}")
    ids=sorted({a for a,_ in units})
    out=sites[sites["site_id"].isin(ids)].copy()
    if len(out)!=122: raise ValueError(f"candidate site drift {len(out)}")
    return out[["site_id","site_name","region","latitude","longitude"]]


def ring_polygon(ring):
    if not ring or len(ring)<4: return None
    coords=[(float(p[0]),float(p[1])) for p in ring if len(p)>=2]
    if len(coords)<4: return None
    poly=Polygon(coords)
    if not poly.is_valid: poly=poly.buffer(0)
    if poly.is_empty: return None
    return poly


def odd_even_geometry(rings):
    polys=[p for p in (ring_polygon(r) for r in (rings or [])) if p is not None]
    if not polys: return None
    geom=polys[0]
    for poly in polys[1:]:
        geom=geom.symmetric_difference(poly)
    if not geom.is_valid: geom=geom.buffer(0)
    return None if geom.is_empty else geom


def download_land(s,layer_url,object_field):
    ids=get(
        s,f"{layer_url}/query",f="json",
        where="surface='land'",returnIdsOnly="true"
    ).get("objectIds") or []
    ids=sorted(int(v) for v in ids)
    geoms=[]; attrs=[]; repaired=0
    for start in range(0,len(ids),500):
        chunk=ids[start:start+500]
        data=post(
            s,f"{layer_url}/query",
            f="json",
            objectIds=",".join(str(v) for v in chunk),
            outFields="FID,surface,Shape__Area,Shape__Length",
            returnGeometry="true",
            outSR=3031,
            maxAllowableOffset=5,
            geometryPrecision=2,
        )
        batch=data.get("features",[])
        if len(batch)!=len(chunk):
            raise RuntimeError(f"chunk drift {start}: {len(batch)} != {len(chunk)}")
        for feature in batch:
            geom=odd_even_geometry((feature.get("geometry") or {}).get("rings") or [])
            if geom is None: continue
            if not geom.is_valid:
                geom=geom.buffer(0); repaired+=1
            geoms.append(geom); attrs.append(feature.get("attributes") or {})
    if len(geoms)!=len(ids):
        raise RuntimeError(f"geometry count drift {len(geoms)} != {len(ids)}")
    return geoms,attrs,repaired


def local_count(tree,geoms,point,distance):
    if distance==0:
        idxs=tree.query(point)
        return sum(geoms[int(i)].covers(point) for i in idxs)
    idxs=tree.query(point.buffer(distance))
    return sum(point.distance(geoms[int(i)])<=distance+1e-6 for i in idxs)


def service_count(s,layer_url,lon,lat,distance):
    geom=json.dumps({"x":lon,"y":lat,"spatialReference":{"wkid":4326}})
    params={
        "f":"json","where":"surface='land'",
        "geometry":geom,"geometryType":"esriGeometryPoint",
        "inSR":4326,"spatialRel":"esriSpatialRelIntersects",
        "returnCountOnly":"true",
    }
    if distance:
        params["distance"]=distance; params["units"]="esriSRUnit_Meter"
    return int(get(s,f"{layer_url}/query",**params).get("count") or 0)


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()

    sites=candidate_sites(a.mapppdr_dir)
    s=session()
    layer_url,meta=discover_layer(s)
    oid=str(meta.get("objectIdField") or "FID")
    geoms,attrs,repaired=download_land(s,layer_url,oid)
    tree=STRtree(geoms)
    transform=Transformer.from_crs(4326,3031,always_xy=True)

    anchors={}
    anchor_pass=True
    for name,(lon,lat) in ANCHORS.items():
        pt=shapely_transform(transform.transform,Point(lon,lat))
        rows={}
        for distance in (0,5000):
            service=service_count(s,layer_url,lon,lat,distance)
            local=local_count(tree,geoms,pt,distance)
            ok=(service==0) or (local>=1)
            rows[str(distance)]={"service_land_count":service,"local_land_count":local,"pass":ok}
            anchor_pass=anchor_pass and ok
        anchors[name]=rows

    matched=[]
    for row in sites.to_dict(orient="records"):
        pt=shapely_transform(
            transform.transform,
            Point(float(row["longitude"]),float(row["latitude"]))
        )
        counts={str(d):local_count(tree,geoms,pt,d) for d in DISTANCES_M}
        nearest=None; nearest_attrs=None
        idxs=tree.query(pt.buffer(max(DISTANCES_M)))
        ds=[]
        for idx in idxs:
            i=int(idx); ds.append((float(pt.distance(geoms[i])),attrs[i]))
        if ds:
            ds.sort(key=lambda x:x[0]); nearest,nearest_attrs=ds[0]
        matched.append({
            "site_id":str(row["site_id"]),
            "site_name":str(row["site_name"]),
            "region":str(row["region"]),
            "latitude":float(row["latitude"]),
            "longitude":float(row["longitude"]),
            "nearest_land_distance_m":nearest,
            "nearest_land_attributes":nearest_attrs,
            "land_match_counts":counts,
        })

    n=len(matched); summaries={}; selected=None
    for d in DISTANCES_M:
        vals=[int(r["land_match_counts"][str(d)]) for r in matched]
        any_n=sum(v>=1 for v in vals); multi=sum(v>1 for v in vals)
        rec={
            "distance_m":d,"candidate_sites":n,
            "land_match_count":any_n,
            "land_match_fraction":any_n/n,
            "multiple_land_match_count":multi,
            "multiple_land_match_fraction":multi/n,
            "unmatched_count":n-any_n,
        }
        summaries[str(d)]=rec
        if (
            selected is None and rec["land_match_fraction"]>=0.95
            and rec["multiple_land_match_fraction"]<=0.05
        ):
            selected=d

    result={
        "schema_version":2,
        "audit_id":"mina-antarctic-add-site-match-audit-v2",
        "mapppdr_commit":PINNED_MAPPPDR_COMMIT,
        "candidate_site_species_units":152,
        "distinct_candidate_sites":122,
        "downloaded_land_polygon_count":len(geoms),
        "geometry_reconstruction":"odd_even_symmetric_difference_native_epsg3031",
        "repaired_geometry_count":repaired,
        "anchor_validation":anchors,
        "anchor_validation_passed":anchor_pass,
        "distance_summaries":summaries,
        "selected_distance_m":selected,
        "gate1a_passed":bool(anchor_pass and selected is not None),
        "site_matches":matched,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="site_matches"},indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
