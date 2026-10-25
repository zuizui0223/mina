#!/usr/bin/env python3
"""Source-eligible bird-site histories after strict independently mapped rock matching.

This is a feasibility audit, NOT a new biological effect or preregistered
AADC confirmation: prior V14 outcomes were already viewed. P/A statuses are
read solely to enforce the published survey-eligibility rules, never fit.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import tempfile

from pyproj import Transformer
import requests

from audit_aadc_original_workbook_headers_v11 import public_dataset_manifests
from audit_aadc_penguin_skua_joint_search_v15 import season_valid, direct_eligible
from audit_aadc_geography_editions_v1 import parse_geo
from build_functional_archipelago_v1 import build_archipelago, download_original_geography
from join_aadc_geography_to_scar_network_v1 import crosswalk_source_sites
from join_aadc_original_site_occupancy_v13 import fetch_original_sources, rows_linked
import link_apbp_to_add_island_rock_v3 as bas
import validate_apbp_highres_coast_v4 as coast

BLOCK_M = 250000
# Seven flying-seabird original AADC codes, unchanged from V14.
FLYING = frozenset({"SGP", "SK", "AP", "CP", "SF", "SP", "WSP"})
SPECIES = FLYING | {"ADP"}
MIN_PROGRAM_SITES = 30
MIN_SITES_IN_BLOCK = 5
MIN_PROGRAM_BLOCKS = 3
MIN_SOURCE_LAND_FEATURES = 3
MIN_CROSS_PROGRAM_BLOCKS = 3


def select_unique_source_eligible(surveys:list[dict]) -> list[dict]:
    groups=defaultdict(list)
    for r in surveys:
        sp=str(r.get("species_code","")).strip()
        prog=str(r.get("source_study","")).strip()
        site=str(r.get("geog_site_id","")).strip()
        season=str(r.get("season","")).strip()
        if sp not in SPECIES or not site or not season_valid(season):
            continue
        if (sp=="ADP" and prog!="penguin_original_search") or (
            sp in FLYING and prog!="flying_seabird_original_search"):
            continue
        groups[(site,sp,season,prog)].append(r)
    return [v[0] for v in groups.values() if len(v)==1 and direct_eligible(v[0])]


def support(surveys:list[dict], sites:dict, mapped:list[dict]):
    linked = {r["original_geographic_site_id"]:r for r in mapped}
    if len(linked)!=len(sites) or len(mapped)!=len(sites):
        raise ValueError("SOURCE_STOP geographic-site IDs not one-to-one")
    eligible=select_unique_source_eligible(surveys)
    proj=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    selected_by_prog=defaultdict(list)
    site_by_prog=defaultdict(set)
    spatial_by_prog=defaultdict(lambda:defaultdict(set))
    land_by_prog=defaultdict(set)
    species_by_prog=defaultdict(lambda:defaultdict(set))
    for r in eligible:
        site=r["geog_site_id"]
        cross=linked.get(site)
        if cross is None or not cross["site_point_inside_whole_rock_with_same_parent_land"]:
            continue
        sp=r["species_code"]
        prog="ADELIE" if sp=="ADP" else "FLYING"
        if site not in sites or sites[site]["lat"] is None:
            raise ValueError("SOURCE_STOP strict geography missing original site")
        x,y=proj.transform(sites[site]["lon"],sites[site]["lat"])
        block=f"{math.floor(x/BLOCK_M)}_{math.floor(y/BLOCK_M)}"
        selected_by_prog[prog].append(r)
        site_by_prog[prog].add(site)
        spatial_by_prog[prog][block].add(site)
        land_by_prog[prog].add(cross["point_land_feature_id"])
        species_by_prog[prog][sp].add(site)

    stats={}
    for prog in ("ADELIE","FLYING"):
        blocks=spatial_by_prog.get(prog,{})
        qualifying=sorted(k for k,v in blocks.items() if len(v)>=MIN_SITES_IN_BLOCK)
        stats[prog]={
            "strict_geography_source_eligible_survey_rows":len(selected_by_prog.get(prog,[])),
            "distinct_original_source_geographic_sites":len(site_by_prog.get(prog,set())),
            "distinct_mapped_land_polygon_features":len(land_by_prog.get(prog,set())),
            "spatial_250km_blocks_with_at_least_5_geographic_sites":len(qualifying),
            "eligible_250km_blocks":qualifying,
            "distinct_sites_by_spatial_250km_block":{
                k:len(v) for k,v in sorted(blocks.items())},
            "species_distinct_source_site_counts":{
                k:len(v) for k,v in sorted(species_by_prog.get(prog,{}).items())},
        }
    blocks_overlapping=set(stats["ADELIE"]["eligible_250km_blocks"]) & set(
        stats["FLYING"]["eligible_250km_blocks"])
    individual_program_passes = {
        k:(v["distinct_original_source_geographic_sites"]>=MIN_PROGRAM_SITES
           and v["spatial_250km_blocks_with_at_least_5_geographic_sites"]>=MIN_PROGRAM_BLOCKS
           and v["distinct_mapped_land_polygon_features"]>=MIN_SOURCE_LAND_FEATURES)
        for k,v in stats.items()
    }
    gate=all(individual_program_passes.values()) and (
        len(blocks_overlapping)>=MIN_CROSS_PROGRAM_BLOCKS)
    return {
        "status":"AADC_STRICT_GEOGRAPHY_SOURCE_ELIGIBILITY_NO_MODEL",
        "strict_site_ids_among_all_original_geography":sum(
            r["site_point_inside_whole_rock_with_same_parent_land"] for r in mapped),
        "source_unique_site_species_season_status_filtered_rows_all_geographies":len(eligible),
        "source_programme_strict_geography_support":stats,
        "program_sample_gate_pass":individual_program_passes,
        "independent_250km_blocks_shared_by_both_programmes":len(blocks_overlapping),
        "shared_geographical_blocks":sorted(blocks_overlapping),
        "cross_programme_future_sample_gate_passes":bool(gate),
        "scientific_decision":(
            "GEOGRAPHY_FEASIBLE_ONLY_BIOLOGY_STILL_EXPLORATORY" if gate
            else "STOP_CROSS_PROGRAMME_STRICT_GEOGRAPHY_SUPPORT"),
        "original_source_P_A_status_read_only_for_eligibility":True,
        "original_source_NR_ever_recoded_to_absence":False,
        "same_season_proves_same_visit":False,
        "original_geographic_site_coordinate_is_nest_GPS":False,
        "AADC_V14_original_biological_outcomes_already_seen":True,
        "new_biological_effect_fitted":False,
        "old_AADC_V14_negative_CV_conclusion_unchanged":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with requests.Session() as session:
        manifest,index=public_dataset_manifests(session)
        originals,source_meta=fetch_original_sources(session,manifest)
    v13meta,source_surveys,_geo_records=rows_linked(originals)
    sites,q=parse_geo(originals["potential_geography_2025"],old=False)
    if len(sites)!=7785 or len(source_surveys)!=33107:
        raise ValueError("SOURCE_STOP original 2025 site/survey lengths unexpectedly changed")
    coastzip,rockzip=download_original_geography()
    with tempfile.TemporaryDirectory(prefix="strict-aadc-scar-survey-") as temp:
        root=Path(temp)
        land,_meta=coast.original_highres_shapes(coastzip,root/"land",{})
        rockpath=bas.unpack_shapefile(rockzip,root/"rock")
        rock,_rockmeta=bas.mapped_features(rockpath,require_surface=False)
        rockrows,_rocksummary=build_archipelago(land,rock)
        crosswalk,_crossmeta=crosswalk_source_sites(sites,land,rock,rockrows)
    result=support(source_surveys,sites,crosswalk)
    result["original_source_lineage"]= {
        k:v["original_SHA256"] for k,v in source_meta.items()}
    result["original_SCAR_land_SHA256"]=hashlib.sha256(coastzip).hexdigest()
    result["original_SCAR_rock_SHA256"]=hashlib.sha256(rockzip).hexdigest()
    result["original_AADC_source_sites"]=len(sites)
    result["original_AADC_survey_metadata_rows"]=len(source_surveys)
    result["original_AADC_public_manifest_SHA256"]=index["source_sha256"]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
