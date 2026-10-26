#!/usr/bin/env python3
"""V12: 13 repeated Adélie original colony site IDs -> physical SCAR land features.

Read original AADC *geography* only and source V10 compact polygon bounds/QC.
No penguin population counts, P/A/NR or new biological geometry downloaded.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,tempfile
from collections import Counter,defaultdict
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import Point,box
from shapely.strtree import STRtree

from audit_aadc_geography_editions_v1 import source_geography_only,parse_geo
import link_apbp_to_add_island_rock_v3 as bas
import validate_apbp_highres_coast_v4 as coast
from derive_aadc_repeated_colony_boundaries_v10 import identify_source_geometry

LAND_SHA="66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4"
GEO_2025_SHA="ed5f59d11a0e2ca7491ecf32dc8b04de524e83edf7acd268702963c3b7561294"
EXPECTED_SITES=13
EXPECTED_YEARS=28


def read_frozen_v10_rows(path:Path,receipt:dict,selected:list):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=receipt["derived_site_year_metrics_CSV_SHA256"]:
        raise ValueError("SOURCE_STOP V10 original source site-year CSV digest differs")
    with path.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=EXPECTED_YEARS:
        raise ValueError("SAMPLE_STOP original V10 site-year metrics row count drift")
    keys={(r["site_id"],int(r["season_start_year"])) for r in rows}
    if len(keys)!=EXPECTED_YEARS or keys!={(r["site_id"],r["season_start_year"]) for r in selected}:
        raise ValueError("SOURCE_STOP V9 selected source and actual V10 site-years differ")
    return rows


def validate_polygon_bbox(row:dict):
    try:
        bounds=json.loads(row["source_polygon_bounds_epsg3031_m"])
    except (ValueError,TypeError,KeyError) as e:
        raise ValueError("SOURCE_STOP original source bbox not parseable") from e
    if (not isinstance(bounds,list) or len(bounds)!=4 or
        any(not isinstance(v,(float,int)) or not math.isfinite(v) for v in bounds)):
        raise ValueError("SOURCE_STOP original source bbox invalid")
    if bounds[0]>=bounds[2] or bounds[1]>=bounds[3]:
        raise ValueError("SOURCE_STOP original original polygon bbox inverted")
    return box(*bounds)


def crosswalk_repeated_site_references(selected,source_rows,geo,land):
    if len(selected)!=EXPECTED_YEARS or len(source_rows)!=EXPECTED_YEARS:
        raise ValueError("SOURCE_STOP repeated site sample changed")
    features=[z[1] for z in land]
    tree=STRtree(features)
    source_by_site=defaultdict(list)
    for row in source_rows:
        source_by_site[row["site_id"]].append(row)
    frozen_sites=sorted({r["site_id"] for r in selected})
    if len(frozen_sites)!=EXPECTED_SITES:
        raise ValueError("SAMPLE_STOP not exactly thirteen publisher site IDs")
    transformer=Transformer.from_crs(4326,3031,always_xy=True)
    largest=max(land,key=lambda x:x[1].area)[0]
    records=[]
    for sid in frozen_sites:
        orig=geo.get(sid)
        valid=orig is not None and orig["lat"] is not None and orig["lon"] is not None
        site_pts=source_by_site[sid]
        if not site_pts:
            raise ValueError("SOURCE_STOP missing source matched site-year QC")
        group={s["source_group"] for s in site_pts}
        if len(group)!=1:
            raise ValueError("SOURCE_STOP source original site group inconsistency")
        land_id=None
        siteclass="HOLD_NO_ORIGINAL_AADC_REFERENCE"
        original_feature=None
        bbox_distances=[]
        if valid:
            x,y=transformer.transform(orig["lon"],orig["lat"])
            if not all(math.isfinite(z) for z in (x,y)):
                raise ValueError("GEOGRAPHY_STOP original WGS84 site projection invalid")
            p=Point(x,y)
            covers=[int(z) for z in tree.query(p) if features[int(z)].covers(p)]
            original_feature=orig["feature"]
            if len(covers)==1:
                land_id=land[covers[0]][0]
                siteclass=("CONTINENT_LARGEST_LAND_FEATURE_PROXY"
                           if land_id==largest else "EXACT_ONE_OTHER_MAPPED_LAND_FEATURE")
            elif len(covers)>1:
                siteclass="HOLD_MULTIPLE_LAND_FEATURES"
            else:
                siteclass="HOLD_NO_SOURCE_LAND_POLYGON"
            for row in site_pts:
                bbox_distances.append(float(p.distance(validate_polygon_bbox(row))))
        records.append({
            "original_site_id":sid,
            "original_AADC_geographic_reference_found":bool(valid),
            "source_original_site_group":next(iter(group)),
            "original_source_seasons":sorted(int(z["season_start_year"]) for z in site_pts),
            "source_year_count":len(site_pts),
            "original_AADC_author_site_class":original_feature,
            "original_SCAR_land_feature_class":siteclass,
            "exact_matched_original_SCAR_source_land_feature_id":land_id,
            "min_original_sitepoint_distance_to_colony_bbox_m":min(bbox_distances) if bbox_distances else None,
            "max_original_sitepoint_distance_to_colony_bbox_m":max(bbox_distances) if bbox_distances else None,
            "site_bbox_distance_is_true_nest_colony_distance":False,
        })
    same_land=defaultdict(list)
    for r in records:
        if r["exact_matched_original_SCAR_source_land_feature_id"] is not None:
            same_land[str(r["exact_matched_original_SCAR_source_land_feature_id"])].append(r["original_site_id"])
    counts=Counter(r["original_SCAR_land_feature_class"] for r in records)
    originalclass=Counter(str(r["original_AADC_author_site_class"]) for r in records)
    return records,{
        "status":"AADC_REPEATED_ADELIE_COLONY_PHYSICAL_LANDMASS_SOURCE_SUPPORT_V12",
        "original_sites":len(records),
        "original_site_year_source_records":len(source_rows),
        "original_survey_group_site_count":dict(sorted(Counter(r["source_original_site_group"] for r in records).items())),
        "original_geographical_site_class_counts":dict(sorted(originalclass.items())),
        "source_polygon_site_point_status_counts":dict(sorted(counts.items())),
        "distinct_original_SCAR_parent_land_feature_ids_with_repeated_colonies":len(same_land),
        "original_source_land_feature_groups_with_repeated_site_IDs":dict(sorted(same_land.items())),
        "mapped_site_reference_and_colony_bbox_outcome_disagreement_is_breeding_site_change":False,
        "source_land_polygon_feature_equals_official_named_physical_island":False,
        "original_source_publisher_group_equals_independent_island":False,
        "original_observed_population_count_or_P_A_opened":0,
        "island_level_population_restructuring_model_fitted":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v9",type=Path,required=True)
    p.add_argument("--v10",type=Path,required=True)
    p.add_argument("--v10-site-metrics",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--site-crosswalk",type=Path,required=True)
    a=p.parse_args()
    prior=json.loads(a.v10.read_text(encoding="utf-8"))
    manifest=json.loads(a.v9.read_text(encoding="utf-8"))
    selected,_=identify_source_geometry(manifest)
    site_rows=read_frozen_v10_rows(a.v10_site_metrics,prior,selected)
    sources,receipts,manifest_sha=source_geography_only()
    if receipts["potential_geography_2025"]["original_SHA256"]!=GEO_2025_SHA:
        raise ValueError("SOURCE_STOP original AADC source geography SHA mismatch")
    geo,geo_qa=parse_geo(sources["potential_geography_2025"],old=False)
    if len(geo)!=7785:
        raise ValueError("SOURCE_STOP AADC original geographic source rows differ")
    old_max=bas.MAX_BYTES
    try:
        bas.MAX_BYTES=coast.HIGH_ZIP_LIMIT
        land_blob=bas.fetch_bas(coast.HIGH_URL)
    finally:
        bas.MAX_BYTES=old_max
    if hashlib.sha256(land_blob).hexdigest()!=LAND_SHA:
        raise ValueError("SOURCE_STOP exact SCAR original land v7.12 source SHA drift")
    with tempfile.TemporaryDirectory(prefix="aadc-physical-landmass-source-") as root:
        land,land_meta=coast.original_highres_shapes(land_blob,Path(root)/"land",{})
    rows,receipt=crosswalk_repeated_site_references(selected,site_rows,geo,land)
    receipt["original_AADC_2025_geography_sha256"]=GEO_2025_SHA
    receipt["original_SCAR_highres_land_zip_sha256"]=LAND_SHA
    receipt["original_v10_site_year_CSV_SHA256"]=hashlib.sha256(a.v10_site_metrics.read_bytes()).hexdigest()
    receipt["AADC_source_manifest_SHA256"]=manifest_sha
    receipt["source_original_land_polygon_QA"]=land_meta
    a.site_crosswalk.parent.mkdir(parents=True,exist_ok=True)
    with a.site_crosswalk.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    receipt["derived_original_site_source_landmass_CSV_SHA256"]=hashlib.sha256(a.site_crosswalk.read_bytes()).hexdigest()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=="__main__":
    main()
