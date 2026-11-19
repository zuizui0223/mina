#!/usr/bin/env python3
"""Source-only crosswalk: GLIMS apparent ice loss × later-dated SCAR bare rock × MAPPPD.

All three publishers' original source data are checked before use.
Even positive overlap is NOT new terrestrial exposure or a colonization event.
No penguin counts, occupancy transitions or inferential coefficients are opened.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import tempfile
from zipfile import ZipFile
import pandas as pd
import shapefile
from pyproj import CRS, Transformer
from shapely.geometry import Point, shape
from shapely.strtree import STRtree
from scripts.audit_glims_antarctic_island_source import PILOT_BBOXES, http_get
from scripts.audit_glims_mapppd_retreat_proximity import (
    TARGET_SPECIES, load_rda, dated_grouped_features, retreat_candidate_shapes
)
from scripts.audit_glims_scar_v713_official_zip_landclip import (
    load_official_land, GLIMS_LAYER, GLIMS_CAP
)
from scripts.audit_scar_rock_v711_source_dates import (
    fetch_archive as fetch_rock_archive
)

ROCK_SHA = "e21f76b886e723ba5009d971946de55a6f6eb43fd0e9c9d2920bb265a6df9d76"
EXPECTED_MAPPPD_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"

def read_recent_rock_source() -> tuple[list, list[dict], dict]:
    """Validate source rock source dates. Full polygons only after source year >= 2000."""
    data,meta=fetch_rock_archive()
    if meta["zip_sha256"] != ROCK_SHA:
        raise ValueError("STOP: publisher rock archive SHA drift")
    geoms=[];attrs=[]
    flags=Counter()
    with tempfile.TemporaryDirectory(prefix="scar-rock-") as work:
        base=Path(work)
        with ZipFile(io.BytesIO(data)) as z:
            for suffix in (".shp",".shx",".dbf",".prj"):
                names=[name for name in z.namelist()
                       if name.lower().endswith(suffix)]
                if len(names)!=1:
                    raise ValueError(f"missing/duplicate rock {suffix}")
                (base/("rock"+suffix)).write_bytes(z.read(names[0]))
        crs=CRS.from_wkt((base/"rock.prj").read_text(
            encoding="utf-8",errors="replace"))
        if not crs.equals(CRS.from_epsg(3031)):
            raise ValueError("rock archive not EPSG3031")
        reader=shapefile.Reader(str(base/"rock.shp"),encoding="latin1")
        fields=[x[0].lower() for x in reader.fields[1:]]
        if "sourcedate" not in fields or "sourceprec" not in fields:
            raise ValueError("rock temporal provenance fields missing")
        ti,pi=fields.index("sourcedate"),fields.index("sourceprec")
        for idx,item in enumerate(reader.iterShapeRecords()):
            v=str(item.record[ti]) if item.record[ti] is not None else ""
            prec=str(item.record[pi]).lower().strip() if item.record[pi] is not None else ""
            if len(v)<4 or not v[:4].isdigit():
                flags["missing_sourcedate"]+=1
                continue
            y=int(v[:4])
            if not (2000<=y<=2026 and prec in {"day","year"}):
                flags["outside_eligible_year_or_precision"]+=1
                continue
            try:
                geom=shape(item.shape.__geo_interface__)
                if geom.is_empty or geom.geom_type not in ("Polygon","MultiPolygon"):
                    flags["non_polygon_source_rock"]+=1
                    continue
                if not geom.is_valid or geom.area<=0:
                    flags["invalid_source_rock_not_repaired"]+=1
                    continue
                geoms.append(geom)
                attrs.append({"source_rock_row_index":idx,
                              "source_rock_year":y,
                              "source_date_precision":prec})
            except (ValueError,TypeError,KeyError):
                flags["unreadable_source_rock"]+=1
        total=len(reader)
        reader.close()
    if len(geoms)<1000:
        raise ValueError("source-dated rock geometry sample unexpectedly small")
    return geoms,attrs,{
        "official_rock_zip_sha256":meta["zip_sha256"],
        "official_rock_zip_bytes":meta["zip_bytes"],
        "source_rock_original_features":total,
        "eligible_rock_valid_geometries_since2000":len(geoms),
        "rock_source_exclusions":dict(flags),
        "source_year_from_attribute":"sourcedate",
        "source_year_precision_from_attribute":"sourceprec",
        "source_crs":"EPSG:3031",
    }

def support_fragments(diffs,rocks,rock_attr,lands,land_labels):
    """Find only later-date rock that overlaps apparent loss and current land."""
    rock_tree=STRtree(rocks)
    land_tree=STRtree(lands)
    fragments=defaultdict(list)
    supported_glims=set()
    source_rocks=set()
    flags=Counter()
    for cand in diffs:
        glims_id=cand["glims_id"]
        geom=cand["geometry"]
        rock_ix=rock_tree.query(geom,predicate="intersects")
        for idx in rock_ix:
            idx=int(idx)
            attr=rock_attr[idx]
            if attr["source_rock_year"]<=cand["late_year"]:
                flags["rock_source_not_later_than_last_glims_outline"]+=1
                continue
            try:
                overlap=geom.intersection(rocks[idx])
                if overlap.is_empty or overlap.area<=0:
                    continue
                if not overlap.is_valid:
                    flags["invalid_glims_rock_intersection"]+=1
                    continue
                land_ix=land_tree.query(overlap,predicate="intersects")
                if not len(land_ix):
                    flags["rock_glims_intersection_off_current_land"]+=1
                    continue
                for li in land_ix:
                    li=int(li)
                    landcut=overlap.intersection(lands[li])
                    if landcut.is_empty or landcut.area<=0:
                        continue
                    if not landcut.is_valid:
                        flags["invalid_three_source_intersection"]+=1
                        continue
                    labels=str(land_labels[li])
                    fragments[labels].append({
                        "geometry":landcut,
                        "glims_id":glims_id,
                        "glims_early_year":cand["early_year"],
                        "glims_late_year":cand["late_year"],
                        "rock_row":attr["source_rock_row_index"],
                        "rock_source_year":attr["source_rock_year"],
                        "rock_source_precision":attr["source_date_precision"],
                        "source_overlap_m2":float(landcut.area),
                    })
                    supported_glims.add(glims_id)
                    source_rocks.add(attr["source_rock_row_index"])
            except Exception:
                flags["source_intersection_error"]+=1
    return fragments,{
        "glims_id_with_later_dated_rock_on_scar_land":len(supported_glims),
        "rock_source_polygons_used":len(source_rocks),
        "source_frags":sum(len(x) for x in fragments.values()),
        "source_land_features_with_frags":len(fragments),
        "source_intersection_exclusions":dict(flags),
    }

def site_rows(sites,lands,labels,fragments,project):
    tree=STRtree(lands)
    rows=[]
    for r in sites.itertuples(index=False):
        pt=Point(*project(float(r.longitude),float(r.latitude)))
        land_ix=tree.query(pt,predicate="intersects")
        chosen=sorted({str(labels[int(i)]) for i in land_ix
                       if lands[int(i)].covers(pt)})
        row={"site_id":str(r.site_id),"site_name":str(r.site_name),
             "latitude":float(r.latitude),"longitude":float(r.longitude),
             "exact_unique_source_land_feature":len(chosen)==1,
             "land_source_feature_id":chosen[0] if len(chosen)==1 else None,
             "source_overlap_is_confirmed_new_rock":False,
             "verified_surveyed_absence":False}
        if len(chosen)!=1:
            row["source_status"]="AMBIGUOUS_OR_OFF_SOURCE_LAND"
            row["distance_m"]=None
        elif chosen[0] not in fragments:
            row["source_status"]="NO_LATER_DATED_ROCK_GLIMS_OVERLAP_SAME_FEATURE"
            row["distance_m"]=None
        else:
            best=min(fragments[chosen[0]],key=lambda x:
                     (pt.distance(x["geometry"]),x["glims_id"],x["rock_row"]))
            row["source_status"]="LATER_DATED_ROCK_AND_GLIMS_ON_SAME_SCARED_SOURCE_FEATURE"
            row["distance_m"]=round(float(pt.distance(best["geometry"])),2)
            row["glims_id"]=best["glims_id"]
            row["glims_early_year"]=best["glims_early_year"]
            row["glims_late_year"]=best["glims_late_year"]
            row["rock_source_year"]=best["rock_source_year"]
            row["rock_source_precision"]=best["rock_source_precision"]
            row["rock_source_row"]=best["rock_row"]
        d=row["distance_m"]
        row["near_1km_source_only"]=d is not None and d<=1000
        row["near_5km_source_only"]=d is not None and d<=5000
        rows.append(row)
    return rows

def run(mapppdr):
    lands,land_ids,land_qa=load_official_land()
    rocks,rock_attr,rock_qa=read_recent_rock_source()
    site=load_rda(mapppdr/"data/sites.rda","sites")
    links=load_rda(mapppdr/"data/site_species.rda","site_species")
    ids=set(links.loc[links["species_id"].isin(TARGET_SPECIES),"site_id"].astype(str))
    site=site.loc[site["site_id"].astype(str).isin(ids)].copy()
    project=Transformer.from_crs(4326,3031,always_xy=True).transform
    report={
        "status":"SOURCE_PROVENANCE_MATCHED_GEOGRAPHY_NOT_NEW_EXPOSURE",
        "date_utc":datetime.now(timezone.utc).isoformat(),
        "frozen_original_mapppdr":EXPECTED_MAPPPD_COMMIT,
        "land_source":land_qa,"rock_source":rock_qa,"regions":{},
        "penguin_nest_count_read":False,
        "risk_set_survey_A_P_history_read":False,
        "claim_new_rock_or_colonization":False,
        "comparison_rule":"original GLIMS(old polygon minus new polygon), intersect source-dated SCAR rock with source_year > GLIMS late_year, intersect original SCAR land; distance only within exact matching SCAR source polygon; no extrapolation",
    }
    all_rows=[]
    for region,(w,s,e,n) in PILOT_BBOXES.items():
        blob=http_get({"service":"WFS","version":"1.0.0",
                      "request":"GetFeature","typeName":GLIMS_LAYER,
                      "maxFeatures":str(GLIMS_CAP),"outputFormat":"application/json",
                      "srsName":"EPSG:4326","bbox":f"{w},{s},{e},{n}"})
        original=json.loads(blob)
        if len(original.get("features",[]))>=GLIMS_CAP:
            raise ValueError(f"{region} GLIMS page cap triggered")
        groups,flag_group=dated_grouped_features(original,project)
        diffs,flag_pair=retreat_candidate_shapes(groups)
        frags,qa=support_fragments(diffs,rocks,rock_attr,lands,land_ids)
        local=site[site["longitude"].between(w,e)
                   & site["latitude"].between(s,n)].copy()
        rows=site_rows(local,lands,land_ids,frags,project)
        for row in rows:row["bbox_region"]=region
        all_rows+=rows
        report["regions"][region]={
          "glims_original_wfs_sha256":hashlib.sha256(blob).hexdigest(),
          "glims_original_features":len(original.get("features",[])),
          "glims_source_apparent_loss_ids":len(diffs),
          "matched_source_later_rock_support":qa,
          "source_glims_group_exclusions":flag_group,
          "source_glims_pair_exclusions":flag_pair,
          "mapppdr_original_site_count":len(rows),
          "site_exact_unique_land":sum(x["exact_unique_source_land_feature"] for x in rows),
          "site_1km_three_source_proximity":sum(x["near_1km_source_only"] for x in rows),
          "site_5km_three_source_proximity":sum(x["near_5km_source_only"] for x in rows),
        }
    frame=pd.DataFrame(all_rows).sort_values(["bbox_region","site_id"]).reset_index(drop=True)
    if len(frame)!=133 or frame["site_id"].nunique()!=133:
        raise ValueError("MAPPPD site window drift from prior 133 source-only snapshot")
    one=int(frame["near_1km_source_only"].sum())
    five=int(frame["near_5km_source_only"].sum())
    if one>36 or five>51:
        raise ValueError("three-source chronologically constrained mask cannot increase land-only support")
    report["summary"]={
      "site_rows":int(len(frame)),
      "site_exact_unique_source_land":int(frame["exact_unique_source_land_feature"].sum()),
      "site_same_feature_later_source_rock_1km":one,
      "site_same_feature_later_source_rock_5km":five,
      "distinct_scar_source_feature_ids_among_1km_sites":int(frame.loc[frame["near_1km_source_only"],"land_source_feature_id"].nunique()),
      "site_exact_zero_distance_rock_intersection":int((frame["distance_m"]==0).sum()),
    }
    report["limitations"]=[
      "GLIMS source glacier ID, polygon continuity and image-era mapping have not been independently verified with original imagery.",
      "SCAR rock mapped after GLIMS last outline does NOT prove rock became ice-free in the GLIMS date interval.",
      "Source-date rock is positive-only support; unclassified polygons and older sourcedates are missing information, not no-rock.",
      "Some polygons use vintage source data and differ in spatial accuracy; 1km is a descriptive search radius, not a verified habitat effect.",
      "Several sites may share one physical island or a large SCAR source land feature; pseudo-replication prohibited.",
      "No explicit verified pre-nesting absence or whole-risk-set habitat survey has been joined; no colonization, occupancy or demographic inference.",
    ]
    return report,frame

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    a=p.parse_args()
    try:
        receipt,frame=run(a.mapppdr_dir)
    except Exception as exc:
        receipt={"status":"HOLD_THREE_SOURCE_PROVENANCE_OR_GEOMETRY",
                 "reason":f"{type(exc).__name__}: {str(exc)}"[:500],
                 "penguin_counts_read":False}
        frame=pd.DataFrame()
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(receipt,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    if not frame.empty:
        a.out_csv.parent.mkdir(parents=True,exist_ok=True)
        frame.to_csv(a.out_csv,index=False)
    print(json.dumps({k:receipt.get(k) for k in ("status","reason","summary")},sort_keys=True))

if __name__=="__main__":
    main()
