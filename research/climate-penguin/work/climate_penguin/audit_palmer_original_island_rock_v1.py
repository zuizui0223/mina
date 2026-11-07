"""Exact SCAR published land and rock geometry crosswalk for five Palmer island site points.

This is 2026 mapped GEOGRAPHY ONLY. Coordinates are site centroids not nest GPS;
rock-area feature sums are static mapping artifacts, not breeding capacity.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import tempfile
import zipfile
from collections import Counter,defaultdict
from pathlib import Path,PurePosixPath
from urllib.parse import urlparse

import requests
import shapefile
from pyproj import CRS,Transformer
from shapely.geometry import Point,shape

ROOT=Path(__file__).resolve().parents[2]
SITES=ROOT/"outputs/comparison_audit/palmer_site_coordinates.csv"
COAST_URL=(
  "https://ramadda.data.bas.ac.uk/repository/entry/get/"
  "add_coastline_high_res_polygon_v7_12.shp.zip?"
  "entryid=synth%3A13c4d2f1-8903-4d7f-8977-592121975554"
  "%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N18xMi5zaHAuemlw"
)
COAST_SHA="66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4"
ROCK_SHA="4d93119052d3c6bf51d20dab218447686e2273e7489e1b63351b69e4bc3d7d8b"
MAX_BYTES=90_000_000
MAX_UNZIPPED=1_000_000_000
NEAR_DIAGNOSTIC_M=250.0

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def csvrows(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def original_publisher_zip():
    with requests.get(COAST_URL,timeout=(25,90),stream=True,
       headers={"User-Agent":"mina-palmer-island-land-identity-source-audit/1.0"}) as response:
        response.raise_for_status()
        location=urlparse(response.url)
        if location.scheme!="https" or location.hostname not in ("ramadda.data.bas.ac.uk","194.66.5.50"):
            raise ValueError("SOURCE_STOP unexpected original publisher redirect")
        data=bytearray()
        for part in response.iter_content(chunk_size=65536):
            data.extend(part)
            if len(data)>MAX_BYTES:
                raise ValueError("SOURCE_STOP original coast ZIP unexpectedly large")
    raw=bytes(data)
    if not raw.startswith(b"PK") or sha(raw)!=COAST_SHA:
        raise ValueError("SOURCE_STOP original SCAR high-res land source SHA/magic mismatch")
    return raw

def unpack(blob,path):
    path.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        members=z.infolist()
        if len(members)>60 or sum(x.file_size for x in members)>MAX_UNZIPPED or z.testzip() is not None:
            raise ValueError("SOURCE_STOP invalid original coastline ZIP")
        for item in members:
            rel=PurePosixPath(item.filename)
            if rel.is_absolute() or ".." in rel.parts or len(rel.parts)>5:
                raise ValueError("SOURCE_STOP unsafe original ZIP path")
            if item.is_dir():continue
            dest=path.joinpath(*rel.parts)
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(z.read(item))
    shps=list(path.rglob("*.shp"))
    assert len(shps)==1
    prj=shps[0].with_suffix(".prj")
    assert prj.is_file()
    if not CRS.from_wkt(prj.read_text(encoding="utf-8",errors="ignore")).equals(CRS.from_epsg(3031)):
        raise ValueError("SOURCE_STOP original land polygon CRS is not EPSG:3031")
    return shps[0]

def geometry_source_candidates(shp, points):
    r=shapefile.Reader(str(shp))
    fields=[x[0].lower() for x in r.fields[1:]]
    assert "surface" in fields, "Original SCAR surface field missing"
    candidates=[]
    surface_n=Counter()
    # Only decode polygons with bounding boxes within 250 m of the
    # predeclared five site points. Retain raw original feature row IDs.
    for fid,sr in enumerate(r.iterShapeRecords()):
        prop={fields[k]:sr.record[k] for k in range(len(fields))}
        surface=str(prop["surface"]).strip().lower()
        surface_n[surface]+=1
        if surface!="land":
            continue
        bbox=sr.shape.bbox
        if not any(bbox[0]-NEAR_DIAGNOSTIC_M<=p.x<=bbox[2]+NEAR_DIAGNOSTIC_M and
                   bbox[1]-NEAR_DIAGNOSTIC_M<=p.y<=bbox[3]+NEAR_DIAGNOSTIC_M for p in points.values()):
            continue
        g=shape(sr.shape.__geo_interface__)
        if g.is_empty or not g.is_valid or g.geom_type not in ("Polygon","MultiPolygon"):
            raise ValueError("GEOMETRY_STOP invalid original source polygon covering candidate site bounds")
        candidates.append((fid,g))
    if surface_n["land"]!=17269:
        raise ValueError(f"SOURCE_STOP original land feature count differs: {surface_n['land']}")
    return candidates,dict(surface_n)

def classify(point, polygons):
    strict=[(fid,geom) for fid,geom in polygons if geom.covers(point)]
    if len(strict)==1:
        fid,geom=strict[0]
        return {"category":"EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON",
                "original_land_fid":fid,"source_land_area_epsg3031_km2":geom.area/1e6,
                "nearest_diagnostic_m":0.0}
    if len(strict)>1:
        return {"category":"HOLD_MULTIPLE_ORIGINAL_MAPPED_LAND_POLYGONS",
                "original_land_fid":None,"source_land_area_epsg3031_km2":None,
                "nearest_diagnostic_m":0.0}
    near=sorted((point.distance(geom),fid) for fid,geom in polygons)
    if near and near[0][0]<=NEAR_DIAGNOSTIC_M:
        return {"category":"NEAR_ONLY_HOLD_NOT_EXACT",
                "original_land_fid":None,"source_land_area_epsg3031_km2":None,
                "nearest_diagnostic_m":float(near[0][0])}
    return {"category":"HOLD_SITE_POINT_UNMATCHED",
            "original_land_fid":None,"source_land_area_epsg3031_km2":None,
            "nearest_diagnostic_m":float(near[0][0]) if near else None}

def rock_index(path, summary):
    rows=csvrows(path)
    assert len(rows)==summary["mapped_rock_polygon_n"]==31480
    assert summary["mapped_land_polygon_n"]==17269
    assert summary["unambiguous_rock_polygon_n"]==28099
    assert summary["provenance"]["land_original_zip_sha256"]==COAST_SHA
    assert summary["provenance"]["rock_original_zip_sha256"]==ROCK_SHA
    by_land=defaultdict(lambda:{"source_rock_features":0,"sum_original_rock_feature_area_epsg3031_km2":0.0})
    exact=0
    seen=set()
    for row in rows:
        rid=row["rock_source_feature_id"]
        assert rid not in seen
        seen.add(rid)
        if row["assignment_status"]!="EXACT_WHOLE_ROCK_ONE_LAND":
            continue
        exact+=1
        fid=int(row["land_source_feature_id"])
        area=float(row["rock_projected_area_epsg3031_km2"])
        assert math.isfinite(area) and area>0
        by_land[fid]["source_rock_features"]+=1
        by_land[fid]["sum_original_rock_feature_area_epsg3031_km2"]+=area
    assert exact==28099
    return by_land

def audit(original_land,rock_csv,rock_summary):
    sites=csvrows(SITES)
    assert len(sites)==5 and {r["site_id"] for r in sites}=={"CHIS","CORM","HUMB","LITC","TORG"}
    project=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    points={}
    for s in sites:
        x,y=project.transform(float(s["longitude"]),float(s["latitude"]))
        assert math.isfinite(x) and math.isfinite(y)
        points[s["site_id"]]=Point(x,y)
    raw=original_publisher_zip()
    with tempfile.TemporaryDirectory(prefix="palmer-five-physical-land-") as temp:
        shp=unpack(raw,Path(temp))
        polys,surface=geometry_source_candidates(shp,points)
    by_land=rock_index(rock_csv,rock_summary)
    out=[]
    for rec in sites:
        sid=rec["site_id"]
        item=classify(points[sid],polys)
        if item["original_land_fid"] is not None:
            item.update(by_land.get(item["original_land_fid"],{
                "source_rock_features":0,
                "sum_original_rock_feature_area_epsg3031_km2":0.0}))
        else:
            item["source_rock_features"]=None
            item["sum_original_rock_feature_area_epsg3031_km2"]=None
        out.append({"site_id":sid,"site_name":rec["site_name"],"source_point_lat":float(rec["latitude"]),
                    "source_point_lon":float(rec["longitude"]),**item})
    exact=[r for r in out if r["category"]=="EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON"]
    fids=[r["original_land_fid"] for r in exact]
    return {"schema":1,"status":"2026_original_mapped_land_rock_source_only_not_historical_capacity",
        "source_files":{"coast_doi":"10.5285/13c4d2f1-8903-4d7f-8977-592121975554",
                       "coast_original_sha256":sha(raw),
                       "rock_doi":"10.5285/3f0c400f-04b9-4819-98cb-f6b53716aca5",
                       "rock_original_sha256_from_archipelago_atlas":ROCK_SHA,
                       "rock_derived_csv_sha256":sha(Path(rock_csv).read_bytes()),
                       "site_coordinates_sha256":sha(SITES.read_bytes())},
        "geographic_source":{"original_surface_counts":surface,
                             "land_polygons_decoded_near_predeclared_sites":len(polys)},
        "sites":out,"n_sites":len(out),"n_exact_mapped_land_site_points":len(exact),
        "n_distinct_exact_source_land_features":len(set(fids)),
        "all_five_exact_unique_mapped_land_ids":len(exact)==5 and len(set(fids))==5,
        "no_island_persistence_or_capacity_inferred":True,
        "strict_limitations":[
            "Exact site point containment is not a validated nest or colony polygon.",
            "SCAR v7.12 land and v7.11 rock are 2026 cartographic layers, not annually accessible land from 1991–2017.",
            "Rock polygon feature areas are summed, NOT unioned; overlap and false mapped rock remain possible.",
            "Zero mapped rock feature is not zero nesting capacity and a point outside mapped land is not real off-island location.",
            "No annual snow/melt, physical shore-to-nest access, climate-forced abundance response or vegetation change is inferred."
        ]}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--rock-csv",required=True,type=Path)
    a.add_argument("--rock-summary",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    summary=json.loads(args.rock_summary.read_text(encoding="utf-8"))
    result=audit(COAST_URL,args.rock_csv,summary)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print("PALMER_PHYSICAL_LAND_ROCK_SOURCE_RECEIPT="+json.dumps(result,ensure_ascii=False,allow_nan=False),flush=True)

if __name__=="__main__":
    main()
