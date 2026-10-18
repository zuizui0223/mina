#!/usr/bin/env python3
"""Stage3: APBP site coordinates × original SCAR-ADD land/rock geometry.

Only a spatial covariate LINKAGE AUDIT. The 2026 medium-resolution coastline
deletes some small islands; unmatched sites NEVER imply mainland or zero
suitable nesting area. Neither GIS layer measures time-varying available
substrate, and no ecological outcome/coefficients are computed.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import tempfile
from urllib.parse import urlparse, urlencode
import zipfile

import requests
import shapefile
from pyproj import CRS,Transformer
from shapely.geometry import Point,shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

from audit_apbp_darwincore_source_v1 import (
    audited_schema, fetch_original, metadata, rows_for, safe_zip,
)

APBP_SHA="afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf"
COAST_ZIP=(
    "https://ramadda.data.bas.ac.uk/repository/entry/get/"
    "add_coastline_medium_res_polygon_v7_12.shp.zip?"
    "entryid=synth%3Ac9c6d671-ad19-4a78-96b2-7d47e9bac46a"
    "%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19wb2x5Z29uX3Y3XzEyLnNocC56aXA%3D"
)
ROCK_ZIP=(
    "https://ramadda.data.bas.ac.uk/repository/entry/get/"
    "add_rock_outcrop_medium_res_polygon_v7_11.shp.zip?"
    "entryid=synth%3A3f0c400f-04b9-4819-98cb-f6b53716aca5"
    "%3AL2FkZF9yb2NrX291dGNyb3BfbWVkaXVtX3Jlc19wb2x5Z29uX3Y3XzExLnNocC56aXA%3D"
)
COAST_DOI="10.5285/c9c6d671-ad19-4a78-96b2-7d47e9bac46a"
ROCK_DOI="10.5285/3f0c400f-04b9-4819-98cb-f6b53716aca5"
NEAR_M=250
ROCK_RADII_M=(500,2000)
DRIFT_STOP_M=1000
MAX_BYTES=30_000_000
MAX_UNCOMPRESSED=200_000_000

def fetch_bas(url):
    with requests.get(url,timeout=(25,95),stream=True,
                      headers={"User-Agent":"mina-ant-island-spatial-source-audit/1.0"}) as r:
        r.raise_for_status()
        info=urlparse(r.url)
        if info.scheme!="https" or info.hostname not in ("ramadda.data.bas.ac.uk","194.66.5.50"):
            raise ValueError("SOURCE_STOP untrusted source redirect")
        raw=bytearray()
        for block in r.iter_content(chunk_size=65536):
            raw.extend(block)
            if len(raw)>MAX_BYTES:
                raise ValueError("SOURCE_STOP unexpectedly large BAS medium-resolution ZIP")
    if not raw.startswith(b"PK"):
        raise ValueError("SOURCE_STOP original BAS GIS source is not ZIP")
    return bytes(raw)

def unpack_shapefile(blob,target):
    target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        files=z.infolist()
        if len(files)>50 or sum(x.file_size for x in files)>MAX_UNCOMPRESSED or z.testzip() is not None:
            raise ValueError("SOURCE_STOP malformed or huge GIS ZIP")
        for member in files:
            rel=PurePosixPath(member.filename)
            if rel.is_absolute() or ".." in rel.parts or len(rel.parts)>5:
                raise ValueError("SOURCE_STOP unsafe shapefile ZIP path")
            if member.is_dir():continue
            dest=target.joinpath(*rel.parts)
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(z.read(member))
        paths=list(target.rglob("*.shp"))
        if len(paths)!=1:
            raise ValueError("SOURCE_STOP expected exactly one GIS shapefile")
        p=paths[0]
        prj=p.with_suffix(".prj")
        if not prj.is_file():
            raise ValueError("SOURCE_STOP GIS original CRS .prj missing")
        source_crs=CRS.from_wkt(prj.read_text(encoding="utf-8",errors="ignore"))
        if not source_crs.equals(CRS.from_epsg(3031)):
            raise ValueError("CRS_STOP source GIS is not verified EPSG:3031")
        return p

def mapped_features(path, require_surface=False):
    reader=shapefile.Reader(str(path))
    names=[f[0] for f in reader.fields[1:]]
    if require_surface and "surface" not in [x.lower() for x in names]:
        raise ValueError("SOURCE_STOP original land shapefile lacks surface attribute")
    shapes=[]
    bad=0
    attr=Counter()
    for index,sr in enumerate(reader.iterShapeRecords()):
        vals={names[i].lower():sr.record[i] for i in range(len(names))}
        surface=str(vals.get("surface","")).strip().lower()
        attr[surface or "<EMPTY>"]+=1
        try:
            geom=shape(sr.shape.__geo_interface__)
        except Exception:
            bad+=1
            continue
        if geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon","MultiPolygon"):
            bad+=1
            continue
        if require_surface and surface!="land":
            continue
        shapes.append((index,geom,vals))
    if not shapes:
        raise ValueError("GEOMETRY_STOP original source has no valid polygons")
    return shapes,{"original_field_names":names,"all_source_surface_labels":dict(attr),
                   "invalid_or_empty_polygon_features":bad,
                   "retained_valid_features":len(shapes)}

def event_sites(source):
    if hashlib.sha256(source).hexdigest()!=APBP_SHA:
        raise ValueError("SOURCE_VERSION_STOP original v2.3 APBP archive SHA drift")
    audited_schema(source)
    with safe_zip(source) as z:
        tables=metadata(z)
        core=next(t for t in tables if t["rowtype"]=="Event")
        events=list(rows_for(z,core))
    sites=defaultdict(list)
    converter=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    for key,ref,r in events:
        site=str(r.get("locationID","")).strip()
        if not site:
            continue
        try:
            lat=float(r["decimalLatitude"])
            lon=float(r["decimalLongitude"])
        except (ValueError,TypeError,KeyError) as exc:
            raise ValueError("POINT_STOP APBP site event has missing original lat/lon") from exc
        if not (-90<=lat<=-60 and -180<=lon<=180):
            raise ValueError("POINT_STOP APBP source coordinate not in Antarctic envelope")
        x,y=converter.transform(lon,lat)
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError("POINT_STOP nonfinite coordinate reprojection")
        unc=r.get("coordinateUncertaintyInMeters","").strip()
        try:uncm=float(unc) if unc else None
        except ValueError:uncm=None
        sites[site].append({
            "x":float(x),"y":float(y),"lat":lat,"lon":lon,
            "uncertainty_m":uncm,
            "locality":r.get("locality",""),
            "source_islandGroup":r.get("islandGroup",""),
        })
    return sites

def unique_match(point,features,tree,threshold=NEAR_M):
    shapes=[v[1] for v in features]
    ids=list(tree.query(point.buffer(threshold)))
    inside=[int(i) for i in ids if shapes[int(i)].covers(point)]
    if len(inside)==1:
        return inside[0],"EXACT_ONE_LAND_POLYGON"
    if len(inside)>1:
        return None,"HOLD_AMBIGUOUS_OVERLAPPING_LAND_POLYGONS"
    nearby=[(int(i),float(shapes[int(i)].distance(point))) for i in ids
            if shapes[int(i)].distance(point)<=threshold]
    if len(nearby)!=1:
        return None,("HOLD_AMBIGUOUS_NEARBY_LAND" if nearby else "HOLD_UNMATCHED_MEDIUM_COASTLINE")
    return nearby[0][0],"NEAR_LAND_WITHIN_250M_ONLY"

def rock_near_site(point,land,rocks,tree):
    geom=[x[1] for x in rocks]
    out={}
    for r in ROCK_RADII_M:
        circle=point.buffer(r)
        ids=tree.query(circle)
        snippets=[]
        for i in ids:
            g=geom[int(i)]
            if g.intersects(circle):
                clips=g.intersection(circle)
                if not clips.is_empty:
                    snippets.append(clips)
        if snippets:
            rock=unary_union(snippets).intersection(land)
            out[r]=float(rock.area)
        else:
            out[r]=0.0
    return out

def link_sites(sites,land_features,rocks):
    land_geoms=[x[1] for x in land_features]
    rock_geoms=[x[1] for x in rocks]
    landtree=STRtree(land_geoms)
    rocktree=STRtree(rock_geoms)
    largest=max(range(len(land_features)),key=lambda i:land_geoms[i].area)
    result=[]
    for key,events in sorted(sites.items()):
        original=events[0]
        origin=Point(original["x"],original["y"])
        drift=max(origin.distance(Point(e["x"],e["y"])) for e in events)
        record={
            "original_locationID":key,
            "source_locality":original["locality"],
            "publisher_islandGroup_NOT_ISLAND_ID":original["source_islandGroup"],
            "original_event_records":len(events),
            "geographic_coordinate_source":"APBP v2.3 Event core; WGS84 → EPSG:3031",
            "latitude":original["lat"],"longitude":original["lon"],
            "original_max_uncertainty_m":max((e["uncertainty_m"] for e in events
                                            if e["uncertainty_m"] is not None),default=None),
            "within_site_event_coordinate_drift_m":round(drift,2),
            "land_polygon_id":None,
            "land_polygon_area_km2":None,
            "provisional_land_type":"HOLD_UNMATCHED",
            "source_link_status":"",
            "rock_500m_mapped_km2":None,
            "rock_2000m_mapped_km2":None,
        }
        if drift>DRIFT_STOP_M:
            record["source_link_status"]="HOLD_COORDINATE_DRIFT_ABOVE_1000M"
            result.append(record)
            continue
        match,status=unique_match(origin,land_features,landtree)
        record["source_link_status"]=status
        if match is None:
            result.append(record)
            continue
        fid,polygon,attr=land_features[match]
        record["land_polygon_id"]=f"ADD7.12_land_feature_{fid:06d}"
        record["land_polygon_area_km2"]=round(polygon.area/1e6,6)
        record["provisional_land_type"]=(
            "CONTINENT_LARGEST_POLYGON_PROXY" if match==largest
            else "ISLAND_SEPARATE_LAND_POLYGON_PROXY"
        )
        rocks_area=rock_near_site(origin,polygon,rocks,rocktree)
        record["rock_500m_mapped_km2"]=round(rocks_area[500]/1e6,6)
        record["rock_2000m_mapped_km2"]=round(rocks_area[2000]/1e6,6)
        result.append(record)
    return result

def summarize(rows,land_meta,rock_meta,sha_coast,sha_rock):
    vals=Counter(r["source_link_status"] for r in rows)
    classes=Counter(r["provisional_land_type"] for r in rows)
    land_ids=defaultdict(set)
    for r in rows:
        if r["land_polygon_id"]:
            land_ids[r["land_polygon_id"]].add(r["original_locationID"])
    return {
        "status":"ADD_STUDY_SITE_GIS_LINK_QA_NO_ECOLOGICAL_EFFECT",
        "source_provenance":{
            "APBP_v2.3_sha256":APBP_SHA,
            "SCAR_ADD_coast_v7.12_doi":COAST_DOI,
            "SCAR_ADD_coast_zip_sha256":sha_coast,
            "SCAR_ADD_rock_v7.11_doi":ROCK_DOI,
            "SCAR_ADD_rock_zip_sha256":sha_rock,
            "projected_crs":"EPSG:3031",
        },
        "method":"original site IDs matched to actual ADD land-polygon features; largest land feature as mainland proxy; near-coast matching within 250 m only; mapped-rock area within 500/2000 m; no climate join",
        "n_site_ids":len(rows),
        "provisional_landtype_site_counts":dict(classes),
        "site_source_match_categories":dict(vals),
        "distinct_contiguous_land_polygons_with_matched_sites":len(land_ids),
        "repeated_sites_on_same_matched_land_polygon":sum(len(x)>1 for x in land_ids.values()),
        "n_source_sites_with_nonzero_mapped_rock_2000m":sum(
            (r["rock_2000m_mapped_km2"] or 0)>0 for r in rows),
        "original_source_land_qa":land_meta,
        "original_source_rock_qa":rock_meta,
        "critical_limits":[
            "ADD medium coastline 2026 omits isolated <0.1km2 islets; cannot classify missed sites as mainland",
            "ADD medium rock 2025 partly omits <0.02km2 rock polygons; zero mapped rock not evidence of no available land",
            "largest contiguous land geometry is only a preliminary mainland proxy",
            "contemporary rock is not annual nesting land nor demonstrated available colony capacity",
            "same site repeated observations do not establish an independent island population",
        ],
        "ecological_effect_models_fitted":0,
    }

def export(rows,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("w",newline="",encoding="utf-8") as file:
        w=csv.DictWriter(file,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True)
    p.add_argument("--out-csv",required=True)
    args=p.parse_args()
    output=Path(args.out_json)
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="apbp-add-v3-") as tmp:
            base=Path(tmp)
            apbp=fetch_original()
            sites=event_sites(apbp)
            coast_blob=fetch_bas(COAST_ZIP)
            rock_blob=fetch_bas(ROCK_ZIP)
            coast=unpack_shapefile(coast_blob,base/"coast")
            rock=unpack_shapefile(rock_blob,base/"rock")
            land,land_meta=mapped_features(coast,require_surface=True)
            rocks,rock_meta=mapped_features(rock,require_surface=False)
            rows=link_sites(sites,land,rocks)
        result=summarize(rows,land_meta,rock_meta,
                         hashlib.sha256(coast_blob).hexdigest(),
                         hashlib.sha256(rock_blob).hexdigest())
        export(rows,Path(args.out_csv))
        result["derived_site_gis_csv_sha256"]=hashlib.sha256(
            Path(args.out_csv).read_bytes()).hexdigest()
        result["derived_site_gis_csv_rows"]=len(rows)
    except Exception as exc:
        result={"status":"HOLD_ADD_SOURCE_OR_SPATIAL_GEOMETRY",
                "error_type":type(exc).__name__,
                "error":str(exc)[:550],
                "ecological_effect_models_fitted":0}
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)

if __name__=="__main__":
    main()
