#!/usr/bin/env python3
"""V35 source-only JNCC site <> RSPB predator island reference *point* screen.

RSPB island points are not polygons; nearest-point candidates cannot identify
within-parent physical islands or mammals during either JNCC original census.
NO JNCC bird numerical counts, declines, shares, concentration E are opened.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree

import audit_jncc_two_censuses_source_v28 as v28
import audit_jncc_comparable_site_panels_v29 as v29
import model_jncc_component_concentration_v30 as v30
import audit_jncc_predator_island_source_v33 as predators

NEAR_M=250.0
SECOND_DISTANT_M=750.0
AREA_SOURCE_SHA="3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5"
PREDATOR_TAXA=("American mink","Brown rat")


def classify_point(d0:float,d1:float,key:int)->dict:
    if d0<=NEAR_M and d1>SECOND_DISTANT_M:
        return {"class":"UNIQUE_NEAR_RSPB_CENTROID_NOT_PHYSICAL_ISLAND_ID",
                "candidate_lowid":key,"nearest_m":float(d0),"second_nearest_m":float(d1)}
    if d0<=NEAR_M:
        return {"class":"AMBIGUOUS_TWO_OR_MORE_RSPB_CENTROIDS",
                "candidate_lowid":None,"nearest_m":float(d0),"second_nearest_m":float(d1)}
    return {"class":"NO_RSPB_CENTROID_WITHIN_250M",
            "candidate_lowid":None,"nearest_m":float(d0),"second_nearest_m":float(d1)}


def assign_sites(island_meta:dict[int,dict],points:set[tuple[float,float]])->dict:
    island_pairs=sorted(
        (key,float(record["latitude"]),float(record["longitude"]))
        for key,record in island_meta.items()
    )
    if len(island_pairs)!=9688:
        raise ValueError("ORIGINAL_SOURCE_RSPB_ISLAND_FRAME_MISMATCH")
    converter=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
    pts_lon=np.array([p[2] for p in island_pairs])
    pts_lat=np.array([p[1] for p in island_pairs])
    xs,ys=converter.transform(pts_lon,pts_lat)
    tree=cKDTree(np.column_stack([xs,ys]))
    q=sorted(points)
    orig_lon=np.array([p[1] for p in q])
    orig_lat=np.array([p[0] for p in q])
    sx,sy=converter.transform(orig_lon,orig_lat)
    d,index=tree.query(np.column_stack([sx,sy]),k=2)
    if len(q)!=len(d):
        raise ValueError("SOURCE_POINT_QUERY_SHAPE_GATE")
    return {key:classify_point(float(ds[0]),float(ds[1]),island_pairs[int(inds[0])][0])
            for key,ds,inds in zip(q,d,index)}


def status_group(text:str)->str:
    code=str(text).strip()
    if code in {"1","2"}:return "REPORTED_CONFIRMED_OR_PROBABLE"
    if code=="0":return "ASSUMED_OR_KNOWN_ABSENT_COMBINED"
    if code=="3":return "POSSIBLE_OR_INCIDENTAL"
    return "UNKNOWN_SOURCE"


def summarize_source_panels(
        panels:dict,matched:dict,predator_rows:dict[int,dict])->dict:
    stats=Counter()
    country=defaultdict(Counter)
    species=defaultdict(Counter)
    parent_source_states=Counter()
    distinct_candidate_lowids=set()
    mixed_pairs=Counter()
    only_counts=Counter()
    examples=[]
    source_children=0
    for parent,records in sorted(panels.items()):
        source_children+=len(records)
        positions=[(float(x["lat"]),float(x["lon"])) for x,_ in records]
        lookups=[matched[p] for p in positions]
        labels=[item["class"] for item in lookups]
        unique=[x["candidate_lowid"] for x in lookups if x["candidate_lowid"] is not None]
        stats.update(labels)
        country[parent[1]].update(labels)
        species[parent[0]].update(labels)
        only_counts["original_panels_total"]+=1
        if len(unique)==len(records):
            only_counts["parents_all_children_have_unique_centroid_candidate"]+=1
        if len(set(unique))>=2:
            only_counts["parents_any_two_distinct_candidate_island_points"]+=1
        if len(unique)==len(records) and len(set(unique))>=2:
            only_counts["parents_ALL_children_unique_and_at_least_two_distinct_centroid_ids"]+=1
            distinct_candidate_lowids.update(unique)
            for taxon in PREDATOR_TAXA:
                states={
                    status_group(predator_rows[i]["status_codes"].get(taxon,""))
                    for i in set(unique)
                }
                if ("REPORTED_CONFIRMED_OR_PROBABLE" in states
                   and "ASSUMED_OR_KNOWN_ABSENT_COMBINED" in states):
                    mixed_pairs[taxon]+=1
            if len(examples)<6:
                examples.append({
                   "source_species":parent[0],
                   "source_country":parent[1],
                   "source_original_count_unit":parent[3],
                   "original_child_component_count":len(records),
                   "distinct_nearby_RSPB_centroids":len(set(unique)),
                   "not_verified_physical_island_membership":True,
                })
        parent_source_states["ALL_NEAR_SOURCE_CENTROIDS" if len(unique)==len(records)
                             else "INCOMPLETE_CENTROID_SITE_COVERAGE"]+=1
    return {
        "original_V30_structural_parents":len(panels),
        "original_JNCC_child_records":source_children,
        "distinct_original_JNCC_child_coordinates":len(matched),
        "child_source_proximity_classes":dict(stats),
        "original_country_source_proximity_classes":{str(k):dict(v) for k,v in sorted(country.items())},
        "original_species_source_proximity_classes":{str(k):dict(v) for k,v in sorted(species.items())},
        "original_parent_source_point_support":dict(only_counts),
        "candidate_mixed_parent_with_different_status_reference_labels":dict(mixed_pairs),
        "distinct_RSPB_centroid_lowids_in_candidate_mixed_parent":len(distinct_candidate_lowids),
        "illustrative_unnamed_parent_support":examples,
        "critical_status":"UNVERIFIED_POINT_PROXIMITY_NO_PHYSICAL_ISLAND_GIS_ASSIGNED",
        "V32_H2_strict_physical_island_test_ready":False,
        "no_either_era_predator_absence_confirmed":True,
        "JNCC_numeric_site_count_magnitudes_opened":0,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    arg=ap.parse_args()
    data={
        "status":"V35_JNCC_RSPB_SOURCE_ONLY_GEO_PROXIMITY_IN_PROGRESS",
        "original_2017_predator_source_checksum":AREA_SOURCE_SHA,
        "original_JNCC_expected_metadata_parent_panels":1483,
        "original_RSPB_expected_source_islands":9688,
        "JNCC_original_numeric_breeding_counts_opened":0,
        "JNCC_predator_mechanism_effect_fitted":False,
        "GIS_parent_landmass_id_certified":False,
    }
    try:
        raw,meta=v28.download_original()
        if meta["original_sha256"]!=v29.ORIGINAL_SHA:
            raise ValueError("SOURCE_SHA_CHANGED original JNCC XLSX")
        safe,qa=v30.extract_structural(v29.original_rows(raw))
        if not qa["pre_count_structural_gate_pass"] or len(safe)!=1483:
            raise ValueError("SOURCE_PARENT_GUARD_CHANGED")
        original_ids,island_meta,predator_source=predators.fetch_rpsb_islands()
        if len(original_ids)!=9688:
            raise ValueError("SOURCE_ISLAND_IDS_CHANGED")
        supplement=predators.bounded_get(predators.SUPPLEMENTS["ESM5"],predators.MAX_SUPP_BYTES)
        if hashlib.sha256(supplement).hexdigest()!=AREA_SOURCE_SHA:
            raise ValueError("SOURCE_ESM5_CHECKSUM_CHANGED")
        extracted=[]
        sheet,_=predators.sheet_rows(supplement,island_meta,extracted)
        if len(extracted)!=9688:
            raise ValueError("SOURCE_PREDATOR_STATUS_JOIN_LOST")
        statuses={record["lowid"]:record for record in extracted}
        if set(statuses)!=original_ids:
            raise ValueError("SOURCE_PREDATOR_STATUS_ISLAND_IDS_DIFFER")
        coords={(float(rec["lat"]),float(rec["lon"]))
                for child in safe.values() for rec,_ in child}
        labels=assign_sites(island_meta,coords)
        result=summarize_source_panels(safe,labels,statuses)
        data["JNCC_original_source_sha256"]=v29.ORIGINAL_SHA
        data["RSPB_original_islands"]=len(original_ids)
        data["original_Stanbury_ESM5_exact_lowid_overlap"]=len(statuses)
        data["original_source_panel_geographic_support"]=result
        data["point_matching_contract"]={
            "coordinate_reference":"EPSG3035",
            "nearby_RSPB_source_point_centroid_max_m":NEAR_M,
            "second_nearest_RSPB_source_point_centroid_min_m":SECOND_DISTANT_M,
            "point_matched_landmass_is_NOT_verified":True,
            "not_a_JNCC_site_colony_polygon":True
        }
        data["status"]="V35_ORIGINAL_JNCC_TO_RSPB_CENTROID_PROXIMITY_SUPPORT_ONLY"
    except Exception as exc:
        data["status"]="V35_SOURCE_HOLD_NOT_BIOLOGICAL_NULL"
        data["error_type"]=type(exc).__name__
        data["error"]=str(exc)[:500]
    arg.out.parent.mkdir(parents=True,exist_ok=True)
    arg.out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
       "status":data["status"],
       "source_parents":data.get("original_source_panel_geographic_support",{}).get("original_V30_structural_parents"),
       "source_child_counts":data.get("original_source_panel_geographic_support",{}).get("child_source_proximity_classes"),
       "source_parent_support":data.get("original_source_panel_geographic_support",{}).get("original_parent_source_point_support"),
       "candidate_status_variation":data.get("original_source_panel_geographic_support",{}).get("candidate_mixed_parent_with_different_status_reference_labels"),
       "h2_strict_physical_island_verified":False,
       "error":data.get("error")
    }))
    if data["status"]=="V35_SOURCE_HOLD_NOT_BIOLOGICAL_NULL":
        raise SystemExit(2)


if __name__=="__main__":
    main()
