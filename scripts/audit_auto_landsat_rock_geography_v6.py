#!/usr/bin/env python3
"""V6 independent SCAR Landsat 8 mapped rock × original 7,785 AADC geography.

NO animal presence/absence, counts, breeding histories, survey outcomes or
biological model. This does not reopen the previous strict sample STOP.
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

from pyproj import CRS,Transformer
import shapefile
from shapely.geometry import Point, box, shape
from shapely.strtree import STRtree

from audit_aadc_geography_editions_v1 import source_geography_only,parse_geo
import link_apbp_to_add_island_rock_v3 as bas

URL=(
    "https://ramadda.data.bas.ac.uk/repository/entry/get/"
    "add_rockoutcrop_landsat_v7.3.zip?"
    "entryid=synth%3A178ec50d-1ffb-42a4-a4a3-1145419da2bb"
    "%3AL2FkZF9yb2Nrb3V0Y3JvcF9sYW5kc2F0X3Y3LjMuemlw"
)
DOI="10.5285/178ec50d-1ffb-42a4-a4a3-1145419da2bb"
OLD_CROSSWALK_SHA="c011eddbf2936d627dd22ff7cf5d0dc6992366f047806bf35f63a60bb1e51100"
DISTANCE_TIER_M=(250.,2000.)
MAX_ZIP_BYTES=70_000_000
MAX_UNCOMPRESSED=1_800_000_000
VALID_SHAPE_TYPES=(shapefile.POLYGON,shapefile.POLYGONZ,shapefile.POLYGONM)
CATS=("IN_ONE_ROCK","IN_MULTIPLE_ROCKS","OUTSIDE_ROCK_NEAR_250M",
      "OUTSIDE_ROCK_250_TO_2000M","OUTSIDE_ROCK_MORE_THAN_2000M","HOLD_INVALID_NEAR_SITE")


def source_extract_shapefile(blob:bytes,directory:Path):
    """Zip-slip/multiple shape/projection/zip-bomb STOP before spatial analysis."""
    if not blob.startswith(b"PK") or len(blob)>MAX_ZIP_BYTES:
        raise ValueError("SOURCE_STOP official original Landsat 2020 ZIP missing or oversized")
    digest=hashlib.sha256(blob).hexdigest()
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        info=archive.infolist()
        if len(info)>100 or sum(x.file_size for x in info)>MAX_UNCOMPRESSED:
            raise ValueError("SOURCE_STOP untrusted huge Landsat source ZIP")
        if archive.testzip() is not None:
            raise ValueError("SOURCE_STOP original ZIP CRC mismatch")
        directory.mkdir(parents=True,exist_ok=True)
        for member in info:
            name=PurePosixPath(member.filename)
            if name.is_absolute() or ".." in name.parts or len(name.parts)>5:
                raise ValueError("SOURCE_STOP unsafe source archive path")
            if member.is_dir():continue
            target=directory.joinpath(*name.parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            with archive.open(member) as original, target.open("wb") as out:
                while True:
                    part=original.read(1024*1024)
                    if not part:break
                    out.write(part)
    shps=list(directory.rglob("*.shp"))
    if len(shps)!=1:
        raise ValueError("SCHEMA_STOP official original rock source must have one shp")
    shp=shps[0]
    prj=shp.with_suffix(".prj")
    if not prj.is_file():
        raise ValueError("CRS_STOP original source .prj missing")
    try:
        crs=CRS.from_wkt(prj.read_text(encoding="utf-8",errors="ignore"))
    except Exception as e:
        raise ValueError("CRS_STOP original source .prj unreadable") from e
    if not crs.equals(CRS.from_epsg(3031)):
        raise ValueError("CRS_STOP Landsat rock source not EPSG3031")
    return shp,{"source_ZIP_SHA256":digest,"original_source_ZIP_bytes":len(blob),
                "source_archive_member_count":len(info),
                "original_source_CRS":"EPSG:3031"}


def categorise(nearest:float, covers:int, invalid:bool):
    if invalid:
        return "HOLD_INVALID_NEAR_SITE"
    if covers>1:
        return "IN_MULTIPLE_ROCKS"
    if covers==1:
        return "IN_ONE_ROCK"
    if nearest<=DISTANCE_TIER_M[0]:
        return "OUTSIDE_ROCK_NEAR_250M"
    if nearest<=DISTANCE_TIER_M[1]:
        return "OUTSIDE_ROCK_250_TO_2000M"
    return "OUTSIDE_ROCK_MORE_THAN_2000M"


def index_sites(sites:dict):
    if len(sites)!=7785:
        raise ValueError("SOURCE_STOP original AADC 2025 geo frame must contain 7785 IDs")
    transformer=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    keys=sorted(sites)
    points=[]
    for key in keys:
        src=sites[key]
        if src["lat"] is None or src["lon"] is None:
            raise ValueError("SOURCE_STOP original site location missing")
        x,y=transformer.transform(src["lon"],src["lat"])
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("GEOMETRY_STOP invalid original site projection")
        points.append(Point(x,y))
    return keys,points


def classify_shapes(shapes,keys,points):
    """Only build Shapely geometry for Landsat feature whose bounding box
    intersects the predeclared 2km search envelope around an original site.
    """
    pt_tree=STRtree(points)
    closest=[float("inf")]*len(points)
    inside=[0]*len(points)
    invalid=[False]*len(points)
    qc=Counter()
    for shape_rec in shapes:
        qc["source_shapefile_record_shapes"]+=1
        if shape_rec.shapeType not in VALID_SHAPE_TYPES:
            qc["SOURCE_NONPOLYGON"]+=1
            raise ValueError("SCHEMA_STOP published Landsat rock layer includes unsupported geometry")
        bbox=getattr(shape_rec,"bbox",None)
        if not bbox or len(bbox)!=4 or not all(math.isfinite(float(v)) for v in bbox):
            qc["SOURCE_INVALID_BBOX"]+=1
            raise ValueError("GEOMETRY_STOP source polygon bounding box invalid")
        a,b,c,d=map(float,bbox)
        if a>c or b>d:
            raise ValueError("GEOMETRY_STOP source polygon reversed bbox")
        shortlist=pt_tree.query(box(a-DISTANCE_TIER_M[1],
                                   b-DISTANCE_TIER_M[1],
                                   c+DISTANCE_TIER_M[1],
                                   d+DISTANCE_TIER_M[1]))
        if len(shortlist)==0:continue
        qc["source_features_within_any_site_search_bbox"]+=1
        try:
            geom=shape(shape_rec.__geo_interface__)
            if geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon","MultiPolygon"):
                raise ValueError("invalid shape")
        except Exception:
            qc["SOURCE_INVALID_GEOMETRY_WITHIN_2KM_SITE_WINDOW"]+=1
            for i in shortlist:
                invalid[int(i)]=True
            continue
        for j in shortlist:
            i=int(j)
            p=points[i]
            if geom.covers(p):
                inside[i]+=1
                closest[i]=0.
            else:
                distance=float(geom.distance(p))
                if distance<closest[i]:closest[i]=distance
        qc["polygon_features_exactly_evaluated"]+=1
    output=[]
    for key,d,n,bad in zip(keys,closest,inside,invalid):
        output.append({
            "original_geographic_site_id":key,
            "independent_landsat_2020_mapped_rock_category":categorise(d,n,bad),
            "covering_landsat_rock_source_feature_count":n,
            "nearest_landsat_rock_gap_m_within_2km":(
                None if d>DISTANCE_TIER_M[1] or bad else float(d)
            ),
            "possible_invalid_source_polygon_within_2km":bad,
        })
    return output,dict(qc)


def load_old_source_crosswalk(path:Path):
    raw=path.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=OLD_CROSSWALK_SHA:
        raise ValueError("SOURCE_STOP original earlier 2025 SCAR rock-geography crosswalk SHA drift")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline="")))
    if len(rows)!=7785:
        raise ValueError("SOURCE_STOP original old SCAR crosswalk row count changed")
    lookup={}
    for r in rows:
        sid=r.get("original_geographic_site_id")
        if not sid or sid in lookup:raise ValueError("SOURCE_STOP duplicate historical crosswalk site ID")
        cat=r.get("mapped_rock_spatial_category")
        lookup[sid]=cat
    return lookup,{"source_old_geography_CSV_SHA256":digest,"rows":len(rows)}


def summarize(new:list[dict],sites:dict,old_sites:set,old:dict):
    counts=Counter(x["independent_landsat_2020_mapped_rock_category"] for x in new)
    matrix=Counter()
    groups=defaultdict(Counter)
    for r in new:
        sid=r["original_geographic_site_id"]
        if sid not in old or sid not in sites:
            raise ValueError("SOURCE_STOP site IDs do not match across original rock maps")
        current=r["independent_landsat_2020_mapped_rock_category"]
        prior=old[sid]
        matrix[(prior,current)]+=1
        groups[f"author_site_class_{sites[sid]['feature']}"][current]+=1
        groups["siteID_shared_with_2021" if sid in old_sites else "new_only_in_2025"][current]+=1
    exact=counts["IN_ONE_ROCK"]+counts["IN_MULTIPLE_ROCKS"]
    old_exact=sum(k[0]=="POINT_IN_ONE_MAPPED_ROCK" for k in []) # no inference; actual below
    old_exact=sum(v for (o,n),v in matrix.items() if o=="POINT_IN_ONE_MAPPED_ROCK")
    status={
       "status":"SCAR_V73_LANDSAT_AUTOMATIC_ROCK_VS_V711_MAPPED_ROCK_GEOGRAPHY_V6",
       "original_AADC_source_geographic_sites":len(new),
       "new_independent_landsat_source_rock_category_counts":dict(sorted(counts.items())),
       "new_independent_landsat_exact_point_in_rock_sites":exact,
       "old_original_2025_manual_rock_exact_point_in_rock_sites":old_exact,
       "new_exact_site_centres_missed_by_old_manual_rock":sum(v for (o,n),v in matrix.items()
           if o!="POINT_IN_ONE_MAPPED_ROCK" and n in ("IN_ONE_ROCK","IN_MULTIPLE_ROCKS")),
       "old_exact_sites_missed_by_new_auto_rock":sum(v for (o,n),v in matrix.items()
           if o=="POINT_IN_ONE_MAPPED_ROCK" and n not in ("IN_ONE_ROCK","IN_MULTIPLE_ROCKS")),
       "old_vs_new_original_source_cross_classification":[
            {"old_v711_manual_source_rock_class":o,"new_v73_landsat_auto_class":n,"site_ids":v}
            for (o,n),v in sorted(matrix.items())],
       "2020_auto_rock_geographic_coverage_by_publisher_site_class_and_era":{
          k:dict(sorted(v.items())) for k,v in sorted(groups.items())
       },
       "animal_P_A_NRs_or_penguin_abundance_opened":0,
       "independent_new_biological_population_effect_fitted":False,
       "source_geographic_site_centres_are_field_nest_GPS":False,
       "original_rock_maps_identical_edition_or_mapping_method":False,
       "automatically_mapped_rock_validated_breeding_capacity":False,
       "new_geography_not_authorized_as_posthoc_biological_cohort_rescue":True,
    }
    return status


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--old-crosswalk",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    a.add_argument("--source-sites",required=True,type=Path)
    arg=a.parse_args()
    report={"status":"HOLD_ORIGINAL_LANDSAT_ROCK_GEOGRAPHY_V6",
            "biology_or_P_A_observations_opened":0}
    try:
        geography,receipts,manifest_sha=source_geography_only()
        old_source,_=parse_geo(geography["potential_geography_2021"],old=True)
        sites,_=parse_geo(geography["potential_geography_2025"],old=False)
        old_rock,oldreceipt=load_old_source_crosswalk(arg.old_crosswalk)
        keys,points=index_sites(sites)
        previous=bas.MAX_BYTES
        try:
            bas.MAX_BYTES=MAX_ZIP_BYTES
            blob=bas.fetch_bas(URL)
        finally:
            bas.MAX_BYTES=previous
        with tempfile.TemporaryDirectory(prefix="original-scar-landsat-") as td:
            path,source_receipt=source_extract_shapefile(blob,Path(td))
            with shapefile.Reader(str(path)) as reader:
                result,shapeqa=classify_shapes(reader.iterShapes(),keys,points)
        report=summarize(result,sites,set(old_source),old_rock)
        report["independent_original_2020_Landsat_rock_source_doi"]=DOI
        report["independent_original_Landsat_zip_receipt"]=source_receipt
        report["independent_Landsat_shapefile_source_qa"]=shapeqa
        report["original_old_v711_AADC_crosswalk_source_receipt"]=oldreceipt
        report["original_AADC_geographic_source_sha256"]={
            k:r["original_SHA256"] for k,r in receipts.items()}
        report["original_AADC_publisher_manifest_SHA256"]=manifest_sha
        arg.source_sites.parent.mkdir(parents=True,exist_ok=True)
        with arg.source_sites.open("w",newline="",encoding="utf-8") as dst:
            columns=list(result[0])
            w=csv.DictWriter(dst,fieldnames=columns)
            w.writeheader()
            w.writerows(result)
        report["derived_original_7785_sites_v73_auto_rock_CSV_SHA256"]=hashlib.sha256(
            arg.source_sites.read_bytes()).hexdigest()
    except Exception as ex:
        report["error_type"]=type(ex).__name__
        report["error"]=str(ex)[:1500]
    arg.out.parent.mkdir(parents=True,exist_ok=True)
    arg.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
