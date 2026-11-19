#!/usr/bin/env python3
"""Frozen source-only Antarctic island vs continental ASI geography support gate.

Use original SCAR ADD v7.13 high-res land geometry (publisher SHA pinned) and
Schrimpf et al 2020 original 196 sites / 1565 ASI visits. Only map exact
unique land polygons. The largest land source polygon is a conservative
continental proxy, NOT independently verified field-island identity. No
penguin biological effect, climate attribution, or predator mechanism fits.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely.geometry import Point
from shapely.strtree import STRtree

from scripts.audit_asi_glims_rock_candidate_source import (
    ASI_COMMIT,ASI_GIT_BLOBS,parse_asi,annual_panel,SPECIES
)
from scripts.audit_glims_scar_v713_official_zip_landclip import (
    OFFICIAL_SHA,load_official_land
)

SPATIAL_BLOCK_M=100_000
# A structural gate, not a p-value threshold or a promise of independent islands.
MIN_SITES_PER_GROUP=8
MIN_SITES_REPEAT_PER_GROUP=5
MIN_SITE_SEASONS_PER_GROUP=20
MIN_100KM_BLOCKS_PER_GROUP=3

def classify_source_sites(meta:pd.DataFrame,lands:list,labels:list)->pd.DataFrame:
    if not lands or len(labels)!=len(lands):
        raise ValueError("original SCAR land geometries missing")
    mainland_ix=max(range(len(lands)),key=lambda i:lands[i].area)
    mainland_label=labels[mainland_ix]
    tree=STRtree(lands)
    convert=Transformer.from_crs(4326,3031,always_xy=True)
    out=[]
    for r in meta.itertuples(index=False):
        lat=float(r.Lat);lon=float(r.Lon)
        x,y=convert.transform(lon,lat)
        p=Point(x,y)
        exact_ix=sorted({int(i) for i in tree.query(p,predicate="intersects")
                         if lands[int(i)].covers(p)})
        if len(exact_ix)!=1:
            group="OFF_LAND_OR_AMBIGUOUS"
            source_idx=None
            size=None
        else:
            source_idx=exact_ix[0]
            group=("CONTINENT_LARGEST_LAND_POLYGON_PROXY"
                   if labels[source_idx]==mainland_label
                   else "NONCONTINENTAL_LAND_POLYGON_PROXY")
            size=round(lands[source_idx].area/1e6,4)
        out.append({
           "Code":str(r.Code),"Name":str(r.Name),
           "ASI_lat":lat,"ASI_lon":lon,
           "SCAR_source_land_index":str(labels[source_idx]) if source_idx is not None else None,
           "land_area_km2_source_polygon":size,
           "geography_group":group,
           "exact_one_land_source_polygon":len(exact_ix)==1,
           "geographic_x_3031":round(x,1),
           "geographic_y_3031":round(y,1),
           "spatial_block_100km":f"{int(np.floor(x/SPATIAL_BLOCK_M))}_{int(np.floor(y/SPATIAL_BLOCK_M))}",
           "polygon_source_row_is_validated_physical_island":False,
           "continental_proxy_does_not_confirm_predation_exposure":True,
        })
    return pd.DataFrame(out)

def geography_support(geo,panel,visits):
    meta=geo.merge(visits.groupby("Code",as_index=False)
                   .agg(visit_count=("Code","size"),
                        surveyed_seasons=("season_start","nunique")),
                   how="left",on="Code",validate="one_to_one")
    meta["visit_count"]=meta["visit_count"].fillna(0).astype(int)
    meta["surveyed_seasons"]=meta["surveyed_seasons"].fillna(0).astype(int)
    if int(meta["visit_count"].sum())!=len(visits):
        raise ValueError("ASI original visit count drift after location join")
    report={}
    for group,d in meta.groupby("geography_group"):
        local_codes=set(d.Code)
        local_panel=panel[panel.Code.isin(local_codes)]
        raw=visits[visits.Code.isin(local_codes)]
        record={
            "site_codes":int(d.Code.nunique()),
            "source_visits":int(d.visit_count.sum()),
            "source_site_seasons":int(len(local_panel)),
            "sites_surveyed_two_or_more_seasons":int(d.surveyed_seasons.ge(2).sum()),
            "sites_surveyed_five_or_more_seasons":int(d.surveyed_seasons.ge(5).sum()),
            "distinct_100km_blocks":int(d.spatial_block_100km.nunique()),
            "distinct_scar_source_land_polygons":int(d.SCAR_source_land_index.nunique()),
            "source_land_proxy_feature_ids_are_islands":False,
            "species_scored_visit_counts":{sp:int(raw[sp].isin(["0","1","2"]).sum())
                                            for sp in SPECIES},
            "species_breeding_detected_visit_counts":{sp:int(raw[sp].eq("2").sum())
                                            for sp in SPECIES},
            "species_site_season_scored":{sp:int((local_panel[sp]!="INCOMPLETE_OR_MISSING").sum())
                                            for sp in SPECIES},
        }
        report[group]=record
    supported={}
    for g in ("CONTINENT_LARGEST_LAND_POLYGON_PROXY","NONCONTINENTAL_LAND_POLYGON_PROXY"):
        v=report.get(g,{})
        supported[g]={
           "min_site_codes":v.get("site_codes",0)>=MIN_SITES_PER_GROUP,
           "min_repeated_site_codes":v.get("sites_surveyed_two_or_more_seasons",0)>=MIN_SITES_REPEAT_PER_GROUP,
           "min_site_seasons":v.get("source_site_seasons",0)>=MIN_SITE_SEASONS_PER_GROUP,
           "min_spatial_blocks":v.get("distinct_100km_blocks",0)>=MIN_100KM_BLOCKS_PER_GROUP,
        }
    return report,supported,meta

def run(raw_path:Path,meta_path:Path):
    visits,sites=parse_asi(raw_path,meta_path)
    panel=annual_panel(visits)
    lands,labels,source_qa=load_official_land()
    if source_qa["original_scar_sha256"] != OFFICIAL_SHA:
        raise ValueError("publisher coastline original source drift")
    geo=classify_source_sites(sites,lands,labels)
    if len(geo)!=196 or geo["Code"].nunique()!=196:
        raise ValueError("original ASI site geometry roster drift")
    groups,gates,joined=geography_support(geo,panel,visits)
    return {
        "status":"SOURCE_ONLY_ISLAND_CONTINENT_GEOGRAPHY_AUDITED_NO_ECOLOGICAL_EFFECT",
        "original_asi_commit":ASI_COMMIT,
        "original_asi_git_blob_sha1":ASI_GIT_BLOBS,
        "original_scar_land_sha256":source_qa["original_scar_sha256"],
        "original_source_asi_visited_sites":196,
        "original_source_asi_visits":1565,
        "original_source_asi_site_seasons":int(len(panel)),
        "SCAR_source_geometry_valid_land_features":len(lands),
        "mainland_proxy_rule":"single largest original land polygon by EPSG3031 planar area; source polygon only, no physical island validation",
        "geographic_spatial_support":groups,
        "fixed_structural_gate":{
            "site_codes_per_group_gte":MIN_SITES_PER_GROUP,
            "sites_two_or_more_surveyed_seasons_per_group_gte":MIN_SITES_REPEAT_PER_GROUP,
            "site_seasons_per_group_gte":MIN_SITE_SEASONS_PER_GROUP,
            "distinct_100km_spatial_blocks_per_group_gte":MIN_100KM_BLOCKS_PER_GROUP,
        },
        "support_flags":gates,
        "sample_structure_qualifies_for_fresh_predeclared_island_association_study":all(all(v.values()) for v in gates.values()),
        "biology_effect_fitted":False,
        "interpretation_limits":[
          "SCAR coastline land contains ice-covered terrain; source feature rows are not validated biological islands.",
          "ASI visit records provide imperfect-detection observations (0=not detected), not true breeding occupancy at nest-patch locations.",
          "Continent vs offshore site sampling is not random; area, region, colony identity, trophic access and observer effort are confounded.",
          "Even if the structural gate passes, a new inferential design must account for detection, regional spatial blocks and source overlap before any island-effect test.",
          "No binary predator treatment is measured anywhere in this source; predator-free versus exposed UK causal interaction is not identifiable.",
        ]
    },joined,panel

def main():
    p=argparse.ArgumentParser()
    for arg in ("raw-asi-csv","asi-site-csv","out-json","out-geography-csv"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    report,sites,_=run(a.raw_asi_csv,a.asi_site_csv)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    sites.to_csv(a.out_geography_csv,index=False)
    print(json.dumps({"status":report["status"],
                      "groups":report["geographic_spatial_support"],
                      "passes":report["sample_structure_qualifies_for_fresh_predeclared_island_association_study"]},sort_keys=True))

if __name__=="__main__":
    main()
