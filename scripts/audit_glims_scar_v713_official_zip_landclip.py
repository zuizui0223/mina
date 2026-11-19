#!/usr/bin/env python3
"""SCAR v7.13 STATIC-LAND support filter of GLIMS apparent outline differences.

This is a source-only geography gate. Land may be ice-covered. Neither land
clipping nor same-SCAR-feature proximity proves newly exposed rock, consistent
surveyed absence, actual nesting, causality or a biological island.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import io
import tempfile
from zipfile import ZipFile
import shapefile
import pandas as pd
import pyreadr
from pyproj import Transformer, CRS
from shapely.geometry import Point, shape
from shapely.ops import transform, unary_union
from shapely.strtree import STRtree

from scripts.audit_glims_antarctic_island_source import PILOT_BBOXES, WFS, http_get
from scripts.audit_glims_mapppd_retreat_proximity import (
    dated_grouped_features, retreat_candidate_shapes, TARGET_SPECIES, load_rda)
from scripts.audit_scar_v713_official_zip import ARCHIVE_URL, download_archive

LAYER_URL=ARCHIVE_URL
GLIMS_LAYER="GLIMS:GLIMS_Glacier_Outlines"
GLIMS_CAP=500
SCAR_CAP=2000

OFFICIAL_SHA = "1e9103e9afaa012b0746eec487c0a473c70834bfc85220f89082e747658aaa66"

def load_official_land():
    """Read publisher compressed SHP once, in its original EPSG:3031.
    
    Source polygon row ID is *not* a biological island or stable geographic ID.
    """
    raw, meta = download_archive()
    if meta["zip_sha256"] != OFFICIAL_SHA:
        raise ValueError("SCAR source archive SHA changed; do not mix GIS editions")
    with tempfile.TemporaryDirectory(prefix="scar-v713-shp-") as tmp:
        root = Path(tmp)
        with ZipFile(io.BytesIO(raw)) as archive:
            for suffix in (".shp", ".shx", ".dbf", ".prj"):
                names = [name for name in archive.namelist()
                         if name.lower().endswith(suffix)]
                if len(names) != 1:
                    raise ValueError(f"SCAR archive missing or repeated {suffix}")
                (root / ("land" + suffix)).write_bytes(archive.read(names[0]))
        crs = CRS.from_wkt((root / "land.prj").read_text(
            encoding="utf-8", errors="replace"))
        if not crs.equals(CRS.from_epsg(3031)):
            raise ValueError("SCAR original shapefile projection is not EPSG3031")
        reader = shapefile.Reader(str(root / "land.shp"))
        names = [f[0].lower() for f in reader.fields[1:]]
        if "surface" not in names:
            raise ValueError("SCAR original shapefile missing surface field")
        surface_index = names.index("surface")
        land = []
        labels = []
        fails = Counter()
        for i, obj in enumerate(reader.iterShapeRecords()):
            value = str(obj.record[surface_index]).strip().lower()
            if value != "land":
                fails["non_land_original_feature"] += 1
                continue
            try:
                geo = shape(obj.shape.__geo_interface__)
                if geo.is_empty or geo.geom_type not in ("Polygon", "MultiPolygon"):
                    fails["non_polygon_or_empty_original_land"] += 1
                    continue
                if not geo.is_valid or geo.area <= 0:
                    fails["invalid_original_land_not_repaired"] += 1
                    continue
                land.append(geo)
                labels.append(str(i))
            except (TypeError,ValueError,KeyError):
                fails["unreadable_original_geometry"] += 1
        n_total = len(reader)
        reader.close()
    if len(land) < 1000:
        raise ValueError("SCAR original archive land polygon coverage unexpectedly small")
    qa = {
        "original_scar_sha256": meta["zip_sha256"],
        "original_scar_archive_bytes": meta["zip_bytes"],
        "original_shapefile_total_features": n_total,
        "original_land_valid_features": len(land),
        "original_scar_field_names": names,
        "original_scar_exclusions": dict(fails),
        "source_crs": "EPSG:3031",
    }
    return land,labels,qa


def clip_to_current_terrestrial(shapes:list[dict],lands:list,labels:list):
    """Clip GLIMS apparent change into official land features, preserving FIDs."""
    tree=STRtree(lands)
    parts=defaultdict(list)
    issues=Counter()
    for row in shapes:
        g=row["geometry"]
        try:
            ix=tree.query(g,predicate="intersects")
            if not len(ix):
                issues["apparent_diff_off_terrestrial_mask"]+=1
                continue
            for i in ix:
                mask=lands[int(i)]
                clipped=g.intersection(mask)
                if clipped.is_empty or clipped.area<=0:
                    continue
                if not clipped.is_valid:
                    issues["invalid_land_intersection"]+=1;continue
                parts[labels[int(i)]].append(clipped)
        except Exception:
            issues["mask_intersection_error"]+=1
    dissolved={}
    for k, poly in parts.items():
        try:
            v=unary_union(poly)
            if not v.is_valid:
                issues["invalid_feature_union"]+=1;continue
            dissolved[k]=v
        except Exception:
            issues["invalid_feature_union"]+=1
    return dissolved,dict(issues)

def sites_with_same_feature(sites:pd.DataFrame,lands:list,labels:list,
                            land_diff:dict,project) -> list[dict]:
    tree=STRtree(lands)
    result=[]
    for r in sites.itertuples(index=False):
        pt=Point(*project(float(r.longitude),float(r.latitude)))
        feature_ix=[int(i) for i in tree.query(pt,predicate="intersects")
                    if lands[int(i)].covers(pt)]
        chosen=sorted(set(labels[i] for i in feature_ix))
        if len(chosen)!=1:
            status="SITE_NO_EXACT_UNIQUE_LAND_FEATURE"
            dist=None;fid=None
        else:
            fid=chosen[0]
            if fid not in land_diff:
                status="SITE_FEATURE_WITHOUT_MATCHED_GLIMS_DIFFERENCE"
                dist=None
            else:
                status="SITE_EXACT_SAME_SCAR_LAND_FEATURE_GEOGRAPHY_ONLY"
                dist=float(pt.distance(land_diff[fid]))
        result.append({
            "site_id":str(r.site_id),"site_name":str(r.site_name),
            "latitude":float(r.latitude),"longitude":float(r.longitude),
            "land_source_feature_id":fid if len(chosen)==1 else None,
            "feature_assignment_status":status,
            "distance_m_same_feature_terrestrial_glims_difference":round(dist,2) if dist is not None else None,
            "within_1km_source_only":bool(dist is not None and dist<=1000),
            "within_5km_source_only":bool(dist is not None and dist<=5000),
            "landmask_proves_new_rock":False,
        })
    return result

def run(mapppdr:Path) -> tuple[dict,pd.DataFrame]:
    sites=load_rda(mapppdr/"data/sites.rda","sites")
    links=load_rda(mapppdr/"data/site_species.rda","site_species")
    ids=set(links.loc[links["species_id"].isin(TARGET_SPECIES),"site_id"].astype(str))
    sites=sites[sites["site_id"].astype(str).isin(ids)]
    project=Transformer.from_crs(4326,3031,always_xy=True).transform
    report={
       "source_layer_scar":LAYER_URL,
       "source_edition":"7.13",
       "doi_scar":"10.5285/1c81cf24-576f-43df-be72-a5c7dbb51ffb",
       "source_layer_glims":GLIMS_LAYER,
       "analysis_class":"SOURCE_ONLY_LAND_MASK_NOT_ROCK_NOT_NEW_SETTLEMENT",
       "date_utc":datetime.now(timezone.utc).isoformat(),
       "count_outcome_opened":False,
       "regions":{},
    }
    lands,fids,scar_qa=load_official_land()
    report['original_official_scar_archive']=scar_qa
    rows=[]
    for label,bbox in PILOT_BBOXES.items():
        west,south,east,north=bbox
        # Use the one verified, publisher-archived source for all regions.
        # Do not rely on the oversized ArcGIS per-bbox GeoJSON response.
        scar_sha = scar_qa["original_scar_sha256"]
        scar_exclusions = scar_qa["original_scar_exclusions"]
        glims=http_get({
            "service":"WFS","version":"1.0.0","request":"GetFeature",
            "typeName":GLIMS_LAYER,"maxFeatures":str(GLIMS_CAP),
            "outputFormat":"application/json","srsName":"EPSG:4326",
            "bbox":f"{west},{south},{east},{north}",
        })
        original=json.loads(glims)
        if len(original.get("features",[]))>=GLIMS_CAP:
            raise ValueError(f"{label}: GLIMS page limit reached")
        grouped,glims_exclusions=dated_grouped_features(original,project)
        diffs,glims_pair_exclusions=retreat_candidate_shapes(grouped)
        parts,clip_exclusions=clip_to_current_terrestrial(diffs,lands,fids)
        sel=sites[sites["latitude"].between(south,north)
                  & sites["longitude"].between(west,east)].copy()
        local=sites_with_same_feature(sel,lands,fids,parts,project)
        for row in local: row["region_bbox"]=label
        rows+=local
        report["regions"][label]={
           "source_scar_sha256":scar_sha,
           "source_glims_sha256":hashlib.sha256(glims).hexdigest(),
           "scar_features_returned":scar_qa["original_shapefile_total_features"],
           "scar_valid_land_features":len(lands),
           "scar_source_exclusions":scar_exclusions,
           "glims_features_returned":len(original.get("features",[])),
           "glims_apparent_difference_ids":len(diffs),
           "scar_land_features_with_apparent_glims_difference":len(parts),
           "glims_geometry_exclusions":glims_exclusions,
           "glims_pair_exclusions":glims_pair_exclusions,
           "clip_source_exclusions":clip_exclusions,
           "source_site_points":len(local),
           "site_exact_unique_scar_land_features":sum(x["land_source_feature_id"] is not None for x in local),
           "site_same_scar_feature_landfiltered_1km":sum(x["within_1km_source_only"] for x in local),
           "site_same_scar_feature_landfiltered_5km":sum(x["within_5km_source_only"] for x in local),
        }
    frame=pd.DataFrame(rows).sort_values(["region_bbox","site_id"]).reset_index(drop=True)
    # Baseline from the original GLIMS-only source audit, not an ecological threshold.
    # A conservative mask should not increase the original nearby-site count.
    if len(frame) != 133:
        raise ValueError(f"MAPPPD source-site geographic scope drift: {len(frame)} vs 133")
    if int(frame["within_1km_source_only"].sum()) > 59 or int(frame["within_5km_source_only"].sum()) > 109:
        raise ValueError("land-only masking unexpectedly increases source proximity count")
    report["summary"]={
       "site_rows":len(frame),
       "unique_site_ids":int(frame["site_id"].nunique()),
       "site_exact_unique_land_feature":int(frame["land_source_feature_id"].notna().sum()),
       "site_1km_landfiltered_same_feature":int(frame["within_1km_source_only"].sum()),
       "site_5km_landfiltered_same_feature":int(frame["within_5km_source_only"].sum()),
    }
    report["source_limits"]=[
       "SCAR land mask is static and can be ice-covered; not bare rock, and not a new ice-free patch.",
       "Original SCAR shapefile row indexes are map features, NOT verified biological islands or physical landmass identities.",
       "GLIMS old-minus-new can be real glacier loss, calving at sea or cartographic discrepancy.",
       "Same-feature proximity is a conservative geography support check, not penguin nesting access.",
       "Date-specific exposure, inhabited physical patch, and independent visited A/P series not measured.",
    ]
    return report,frame

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    a=p.parse_args()
    try:
        report,frame=run(a.mapppdr_dir)
        report["status"]="SOURCE_LAND_MASK_GEOGRAPHY_COMPLETED_NO_BIOLOGICAL_INFERENCE"
    except Exception as e:
        report={"status":"HOLD_SCAR_OFFICIAL_ZIP_LAND_MASK_OR_GEOMETRY",
                "reason":str(e)[:500],"biology_opened":False}
        frame=pd.DataFrame()
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    if not frame.empty:
        a.out_csv.parent.mkdir(parents=True,exist_ok=True)
        frame.to_csv(a.out_csv,index=False)
    print(json.dumps({"status":report["status"],"summary":report.get("summary"),
                      "reason":report.get("reason")},sort_keys=True))

if __name__=="__main__":
    main()
