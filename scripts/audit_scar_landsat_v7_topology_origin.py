#!/usr/bin/env python3
"""V7 source-only topology sensitivity for the Antarctic Landsat rock map.

Preserves V6 raw invalid-rock HOLD receipt; each original and topology-repaired
polygon is attributed to its original DBF feature/lineage. No animal records.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,tempfile
from collections import Counter,defaultdict
from pathlib import Path

import shapefile
from shapely.geometry import box,Point,shape
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely.validation import make_valid

from audit_aadc_geography_editions_v1 import source_geography_only,parse_geo
from audit_auto_landsat_rock_geography_v6 import (
    URL,DOI,MAX_ZIP_BYTES,DISTANCE_TIER_M,
    VALID_SHAPE_TYPES,index_sites,source_extract_shapefile,
    categorise,load_old_source_crosswalk
)
import link_apbp_to_add_island_rock_v3 as bas

SOURCE_SHA_V6="7eb0cae84016b758c98a61977c90d0a8c2c6450c4bf82433e08d03ef2e5a4a5a"


def source_origin(r:dict)->str:
    """Only source-documented GRIDCODE (1 automated, 0 manual), else explicit text."""
    norm={str(k).casefold():v for k,v in r.items()}
    grid=norm.get("gridcode")
    if grid is not None and str(grid).strip():
        code=str(grid).strip()
        if code in ("1","1.0"):return "LANDSAT_AUTOMATED_GRIDCODE_1"
        if code in ("0","0.0"):return "MANUAL_FALLBACK_GRIDCODE_0"
        return "UNKNOWN_GRIDCODE_SOURCE"
    text=str(norm.get("source","") or "").casefold()
    if "landsat" in text or "automatic" in text:return "LANDSAT_SOURCE_TEXT"
    if "manual" in text:return "MANUAL_SOURCE_TEXT"
    return "UNKNOWN_ORIGIN"


def polygon_repair(geometry):
    """Run *only* Shapely make_valid and polygonal projection, not snap/buffer."""
    repaired=make_valid(geometry)
    if repaired.is_empty:return None,"EMPTY_AFTER_MAKE_VALID"
    if repaired.geom_type in ("Polygon","MultiPolygon"):
        polygon=repaired
        remainder=False
    elif repaired.geom_type=="GeometryCollection":
        members=[e for e in repaired.geoms if e.geom_type in ("Polygon","MultiPolygon")
                 and e.area>0]
        remainder=any(e.geom_type not in ("Polygon","MultiPolygon")
                      for e in repaired.geoms)
        if not members:return None,"NONPOLYGON_REMAINDER_ONLY"
        polygon=unary_union(members)
    else:return None,"NONPOLYGON_AFTER_MAKE_VALID"
    if polygon.is_empty or not polygon.is_valid or polygon.area<=0 or polygon.geom_type not in ("Polygon","MultiPolygon"):
        return None,"INVALID_OR_ZERO_AREA_AFTER_MAKE_VALID"
    return polygon,"GEOMETRYCOLLECTION_POLYGONAL_WITH_REMAINDER" if remainder else "POLYGON_VALID_AFTER_MAKE_VALID"


def compare_original_record_rocks(records:list,keys:list,points:list):
    tree=STRtree(points)
    native_near=[float("inf")]*len(points)
    v7_near=[float("inf")]*len(points)
    native_cover=[0]*len(points)
    repaired_cover=[0]*len(points)
    native_origins=[set() for _ in points]
    repaired_origins=[set() for _ in points]
    unrepaired_hold=[False]*len(points)
    sources=Counter()
    qc=Counter()
    for sr in records:
        shp=sr.shape
        qc["original_shape_records"]+=1
        if shp.shapeType not in VALID_SHAPE_TYPES:
            raise ValueError("SCHEMA_STOP unexpected non-polygon original source shape")
        provenance=source_origin(sr.record.as_dict())
        sources[provenance]+=1
        bb=shp.bbox
        if not bb or len(bb)!=4 or not all(math.isfinite(float(z)) for z in bb):
            raise ValueError("GEOMETRY_STOP invalid original rock bbox")
        xmin,ymin,xmax,ymax=map(float,bb)
        candidates=tree.query(box(xmin-DISTANCE_TIER_M[1],ymin-DISTANCE_TIER_M[1],
                                  xmax+DISTANCE_TIER_M[1],ymax+DISTANCE_TIER_M[1]))
        if not len(candidates):continue
        qc["original_rock_features_with_2km_candidate_bbox"]+=1
        original=shape(shp.__geo_interface__)
        is_native=(original.is_valid and not original.is_empty and
                   original.geom_type in ("Polygon","MultiPolygon") and original.area>0)
        if is_native:
            working=original
            qc["original_native_valid_feature_near_candidate"]+=1
        else:
            qc["original_invalid_feature_near_candidate"]+=1
            try:working,status=polygon_repair(original)
            except Exception:
                working,status=None,"MAKE_VALID_EXCEPTION"
            qc["source_repair_status_"+status]+=1
            if working is None:
                for idx in candidates:unrepaired_hold[int(idx)]=True
                continue

        for ix in candidates:
            idx=int(ix)
            pt=points[idx]
            if working.covers(pt):
                distance=0.0
                if is_native:
                    native_cover[idx]+=1
                    native_origins[idx].add(provenance)
                else:
                    repaired_cover[idx]+=1
                    repaired_origins[idx].add(provenance)
            else:
                distance=float(working.distance(pt))
                if distance>DISTANCE_TIER_M[1]:continue
                if is_native:
                    native_origins[idx].add(provenance)
                else:
                    repaired_origins[idx].add(provenance)
            if distance<v7_near[idx]:v7_near[idx]=distance
            if is_native and distance<native_near[idx]:native_near[idx]=distance
    rows=[]
    for i,ident in enumerate(keys):
        orig= categorise(native_near[i],native_cover[i],False)
        repaired_count= native_cover[i]+repaired_cover[i]
        outcome= categorise(v7_near[i],repaired_count,unrepaired_hold[i])
        rows.append({
            "original_geographic_site_id":ident,
            "native_valid_original_rock_class":orig,
            "topology_repaired_source_rock_class":outcome,
            "covering_original_native_valid_rock_features":native_cover[i],
            "covering_source_invalid_but_make_valid_repaired_rock_features":repaired_cover[i],
            "nearest_native_valid_rock_gap_m_within_2km":native_near[i] if native_near[i]<=DISTANCE_TIER_M[1] else None,
            "nearest_topology_repaired_source_rock_gap_m_within_2km":v7_near[i] if v7_near[i]<=DISTANCE_TIER_M[1] and not unrepaired_hold[i] else None,
            "source_rock_feature_origin_categories_native":";".join(sorted(native_origins[i])),
            "source_rock_feature_origin_categories_repaired":";".join(sorted(repaired_origins[i])),
            "source_invalid_feature_could_not_be_repaired_near_site":unrepaired_hold[i],
        })
    return rows,dict(qc),dict(sources)


def summarize(rows,geo,old:dict,qa,origins):
    total=len(rows)
    if total!=7785:raise ValueError("SOURCE_STOP 7785 geographic site IDs unexpectedly changed")
    native=Counter(x["native_valid_original_rock_class"] for x in rows)
    repaired=Counter(x["topology_repaired_source_rock_class"] for x in rows)
    per_region=defaultdict(Counter)
    old_class=Counter()
    for r in rows:
        sid=r["original_geographic_site_id"]
        if sid not in geo or sid not in old:raise ValueError("SOURCE_STOP AADC site crosswalk ID mismatch")
        t=r["topology_repaired_source_rock_class"]
        per_region[str(geo[sid]["feature"])][t]+=1
        old_class[(old[sid],t)]+=1
    cats=("IN_ONE_ROCK","IN_MULTIPLE_ROCKS")
    native_exact=sum(native.get(k,0) for k in cats)
    repair_exact=sum(repaired.get(k,0) for k in cats)
    return {
      "status":"SCAR_V73_LANDSAT_ORIGIN_AND_POLYGON_TOPOLOGY_V7_NO_BIOLOGY",
      "original_AADC_2025_geographic_site_n":total,
      "original_Landsat_source_geometry_QA":qa,
      "original_Landsat_source_feature_provenance_by_gridcode_or_source_text":origins,
      "original_rock_native_valid_polygon_only_counts":dict(sorted(native.items())),
      "original_plus_make_valid_polygon_geometry_counts":dict(sorted(repaired.items())),
      "native_source_exact_point_in_rock_sites":native_exact,
      "including_source_shape_make_valid_exact_point_in_rock_sites":repair_exact,
      "source_geometry_repair_added_exact_site_hits":repair_exact-native_exact,
      "source_reference_2025_manual_rock_polygon_exact_point_hits":sum(1 for sid,x in old.items() if x=="POINT_IN_ONE_MAPPED_ROCK"),
      "sites_where_only_original_invalid_rock_geometry_contains_point":sum(
        x["covering_original_native_valid_rock_features"]==0 and
        x["covering_source_invalid_but_make_valid_repaired_rock_features"]>0
        for x in rows),
      "comparison_old2025_vs_topology_repaired_2020_source":[
        {"old_source_manual_geographic_point_class":o,
         "new_source_repaired_polygon_point_class":n,
         "original_sites":v}
        for (o,n),v in sorted(old_class.items())],
      "source_author_site_class_repaired_geography":{
         k:dict(sorted(v.items())) for k,v in sorted(per_region.items())},
      "ecological_outcomes_downloaded":0,
      "map_repair_is_validated_true_breeding_habitat":False,
      "source_map_classes_or_origins_imply_independent_animal_replication":False,
      "earlier_AADC_strict_scar_site_fate_gate_reopened":False
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--old-crosswalk",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--site-features",type=Path,required=True)
    args=ap.parse_args()
    result={"status":"HOLD_SOURCE_TOPOLOGY_V7","ecological_outcomes_downloaded":0}
    try:
        sources,original_recs,manifest_sha=source_geography_only()
        sites,_=parse_geo(sources["potential_geography_2025"],old=False)
        keys,points=index_sites(sites)
        old,old_receipt=load_old_source_crosswalk(args.old_crosswalk)
        original_limit=bas.MAX_BYTES
        try:
            bas.MAX_BYTES=MAX_ZIP_BYTES
            source=bas.fetch_bas(URL)
        finally:bas.MAX_BYTES=original_limit
        if hashlib.sha256(source).hexdigest()!=SOURCE_SHA_V6:
            raise ValueError("SOURCE_STOP exact SCAR Landsat v7.3 ZIP SHA drift")
        with tempfile.TemporaryDirectory(prefix="scar-l8-rock-topology-") as root:
            shp,receipt=source_extract_shapefile(source,Path(root))
            with shapefile.Reader(str(shp)) as reader:
                rows,qc,source_origins=compare_original_record_rocks(reader.iterShapeRecords(),keys,points)
        result=summarize(rows,sites,old,qc,source_origins)
        result["source_original_scar_Landsat_v73_zip_SHA256"]=receipt["source_ZIP_SHA256"]
        result["independent_source_2020_Landsat_rock_DOI"]=DOI
        result["source_original_aadc_2025_and_2021_geography_sha256"]={
            k:v["original_SHA256"] for k,v in original_recs.items()}
        result["original_source_AADC_manifest_sha256"]=manifest_sha
        result["original_manual_reference_csv_sha256"]=old_receipt["source_old_geography_CSV_SHA256"]
        args.site_features.parent.mkdir(parents=True,exist_ok=True)
        with args.site_features.open("w",newline="",encoding="utf-8") as output:
            writer=csv.DictWriter(output,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
        result["derived_original_site_source_geography_CSV_SHA256"]=hashlib.sha256(
            args.site_features.read_bytes()).hexdigest()
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:1300]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
