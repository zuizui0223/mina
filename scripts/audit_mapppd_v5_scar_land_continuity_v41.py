#!/usr/bin/env python3
"""V41 MAPPPD5 original same-method adjacent nests × SCAR unique land polygons.

SOURCE AND GEOGRAPHY ONLY; never opens original bird count magnitudes.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path
from pyproj import Transformer,Geod
from shapely.geometry import Point
from shapely.strtree import STRtree
import requests
import audit_mapppd_v5_macro_source_lineage_v40 as v40
import audit_nz_ross_sea_highres_precision_v37 as v37
import validate_apbp_highres_coast_v4 as high
import link_apbp_to_add_island_rock_v3 as v3

GIS_SHA="66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4"
EXACT_SOURCE_TRANSITIONS=771
EXACT_SOURCE_PAIR_SITES=95
BINS=((.5,15.),(15.,60.),(60.,100.))
NEAREST_MAX_M=2000.
MIN_MATCHED_STRATA=12
MIN_LAND_POLYGONS=6
MIN_REGIONS=3
MIN_SPECIES=2
CRS=3031

def strict_source_pairs():
    with requests.Session() as session:
        downloads={k:v40.fetch(session,url) for k,url in v40.SOURCE.items()}
    release=json.loads(downloads["release"][0])
    if release.get("version")!=v40.VERSION or release.get("release_date")!=v40.DATE:
        raise ValueError("SOURCE_STOP original MAPPPD release changed")
    source=v40.index_sites(v40.csvrows(downloads["sites"][0],v40.SITE_COLUMNS))
    first=v40.csvrows(downloads["observations_p1"][0],v40.OBS_COLUMNS)
    second=v40.csvrows(downloads["observations_p2"][0],v40.OBS_COLUMNS)
    if len(first)!=5000 or len(second)!=487 or int(first[-1]["id"])+1!=int(second[0]["id"]):
        raise ValueError("SOURCE_STOP MAPPPD observation original pagination drift")
    gate,metadata,good=v40.support(first+second,source)
    if gate["source_original_strict_same_site_species_year_method_nest_transitions"]!=EXACT_SOURCE_TRANSITIONS or \
       gate["distinct_original_siteIDs"]!=EXACT_SOURCE_PAIR_SITES:
        raise ValueError("SOURCE_STOP frozen V40 original 771/95 original sample changed")
    rows=[]
    for (site,species,y),r in good.items():
        nxt=good.get((site,species,y+1))
        if not nxt or not r["citekey"].strip() or not r["vantage"].strip():continue
        if r["citekey"]!=nxt["citekey"] or r["vantage"]!=nxt["vantage"]:continue
        rows.append({"site":site,"species":species,"year":y,
                     "region":source[site]["region"],
                     "citekey":r["citekey"],"vantage":r["vantage"]})
    if len(rows)!=EXACT_SOURCE_TRANSITIONS:raise ValueError("SOURCE_STOP reconstruct V40 paired keys failed")
    return source,rows,{k:v[1] for k,v in downloads.items()}

def get_polygons(site_meta):
    converter=Transformer.from_crs(4326,CRS,always_xy=True)
    xys={}
    for r in site_meta:
        lat=float(r["latitude"]);lon=float(r["longitude"])
        if not (-90<=lat<=-40 and -180<=lon<=180):
            raise ValueError("SOURCE_STOP out-of-bounds MAPPPD source site coordinates")
        x,y=converter.transform(lon,lat)
        xys[r["site_id"]]=[{"x":float(x),"y":float(y)}]
    return xys

def classify(sites,features):
    land=[r[1] for r in features]
    tree=STRtree(land)
    largest=max(range(len(land)),key=lambda i:land[i].area)
    transformer=Transformer.from_crs(4326,CRS,always_xy=True)
    result={}
    for site,data in sites.items():
        lat=float(data["latitude"]);lon=float(data["longitude"])
        x,y=transformer.transform(lon,lat)
        pt=Point(x,y)
        nearby=list(map(int,tree.query(pt.buffer(NEAREST_MAX_M))))
        inside=[i for i in nearby if land[i].covers(pt)]
        if len(inside)==1:
            idx=inside[0];label="EXACT_ONE_LAND_POLYGON"
        elif len(inside)>1:
            idx=None;label="HOLD_MULTIPLE_CONTAINING_POLYGONS"
        else:
            candidates=[i for i in nearby if land[i].distance(pt)<=NEAREST_MAX_M]
            idx=candidates[0] if len(candidates)==1 else None
            label="NEAR_UNIQUE_PROVISIONAL" if idx is not None else "HOLD_AMBIGUOUS_OR_UNMATCHED"
        if idx==largest:
            label="CONTINENT_LARGEST_MAPPED_POLYGON_PROXY"
        result[site]={"source_site":site,"region":data["region"],
                      "latitude":lat,"longitude":lon,
                      "land_feature":idx,"status":label,
                      "is_separate_land":idx is not None and idx!=largest,
                      "source_three_decimal_coords_not_verified_field_GPS":True}
    return result,dict(Counter(x["status"] for x in result.values()))

def distance_km(a,b,geod):
    az1,az2,meters=geod.inv(a["longitude"],a["latitude"],b["longitude"],b["latitude"])
    return meters/1000

def make_pairs(rows,geo,provisional=False):
    groups=defaultdict(dict)
    for r in rows:
        g=geo[r["site"]]
        if not g["is_separate_land"]:continue
        if g["status"]!="EXACT_ONE_LAND_POLYGON" and not (
            provisional and g["status"]=="NEAR_UNIQUE_PROVISIONAL"):
            continue
        key=(r["region"],r["species"],r["year"],r["citekey"],r["vantage"])
        if r["site"] in groups[key]:
            raise ValueError("SOURCE_STOP duplicated site in original method group")
        groups[key][r["site"]]=g
    pairs=[]
    geod=Geod(ellps="WGS84")
    for key,sites in groups.items():
        if len(sites)<2:continue
        for a,b in combinations(sorted(sites),2):
            d=distance_km(sites[a],sites[b],geod)
            for i,(low,high) in enumerate(BINS):
                if low<d<=high:
                    typ=("within_same_land_polygon" if sites[a]["land_feature"]==
                         sites[b]["land_feature"] else "between_distinct_land_polygons")
                    pairs.append({"group":key,"bin":i,"pair":(a,b),
                                  "kind":typ,
                                  "land_features":(sites[a]["land_feature"],sites[b]["land_feature"])})
                    break
    return pairs

def summarize(pairs,geo,method):
    strata=defaultdict(list)
    for r in pairs:strata[(r["group"],r["bin"])].append(r)
    matched=[]
    all_regions=set();all_species=set();islands=set()
    for (group,binid),rows in strata.items():
        types=Counter(r["kind"] for r in rows)
        if not (types["within_same_land_polygon"] and types["between_distinct_land_polygons"]):
            continue
        all_regions.add(group[0]);all_species.add(group[1])
        for r in rows:islands.update(r["land_features"])
        matched.append({
           "publisher_region":group[0],"species":group[1],
           "source_season_start_year":group[2],
           "distance_bin_km":BINS[binid],
           "within_polygon_site_pairs":types["within_same_land_polygon"],
           "across_polygon_site_pairs":types["between_distinct_land_polygons"]})
    matches=len(matched)
    return {
       "source_geography_tier":method,
       "total_original_site_pairs_at_frozen_distance":len(pairs),
       "all_distance_constrained_pair_categories":dict(Counter(r["kind"] for r in pairs)),
       "source_species_year_region_citation_method_distance_cells_with_both_kinds":matches,
       "matched_strata_by_publisher_region":dict(Counter(x["publisher_region"] for x in matched)),
       "matched_strata_by_penguin_species":dict(Counter(x["species"] for x in matched)),
       "distinct_publisher_region_names_in_matched_cells":len(all_regions),
       "distinct_original_species_in_matched_cells":len(all_species),
       "distinct_noncontinental_polygon_ids_in_matched_cells":len(islands),
       "frozen_distance_bins_km":[list(t) for t in BINS],
       "first_25_source_only_matching_cells":sorted(matched,key=lambda x:(x["publisher_region"],x["species"],x["source_season_start_year"],x["distance_bin_km"]))[:25],
       "future_island_boundary_sample_gate_passes":(
          matches>=MIN_MATCHED_STRATA and len(all_regions)>=MIN_REGIONS and
          len(all_species)>=MIN_SPECIES and len(islands)>=MIN_LAND_POLYGONS),
       "bird_count_magnitudes_or_correlations_opened":0
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    report={"status":"HOLD_ORIGINAL_SOURCE_GEOMETRY","effect_fitted":False}
    try:
        sources,rows,receipts=strict_source_pairs()
        members={r["site"] for r in rows}
        keep={site:sources[site] for site in members}
        prev=v3.MAX_BYTES
        try:
            v3.MAX_BYTES=high.HIGH_ZIP_LIMIT
            blob=v3.fetch_bas(high.HIGH_URL)
        finally:v3.MAX_BYTES=prev
        if hashlib.sha256(blob).hexdigest()!=GIS_SHA:
            raise ValueError("SOURCE_STOP authoritative original SCAR high-res ZIP SHA drift")
        xys=get_polygons(keep.values())
        import tempfile
        with tempfile.TemporaryDirectory(prefix="mapppd5-scar-") as path:
            features,shapemeta=high.original_highres_shapes(blob,Path(path),xys)
            geo,types=classify(keep,features)
        exact=summarize(make_pairs(rows,geo,False),geo,"EXACT_LAND_CENTER_ONLY")
        near=summarize(make_pairs(rows,geo,True),geo,"EXACT_OR_NEAR_UNIQUE_WITHIN_2KM_PROVISIONAL")
        report={
            "status":"V41_MAPPPD5_SOURCE_SCAR_GIS_LAND_CONTINUITY_SUPPORT",
            "original_source_census_observation_page_SHA":receipts,
            "source_MACRO_record_n":EXACT_SOURCE_TRANSITIONS,
            "original_source_distinct_site_IDs":EXACT_SOURCE_PAIR_SITES,
            "official_highres_SCAR_source_sha256":GIS_SHA,
            "official_highres_land_source_geometry":shapemeta,
            "source_original_site_polygon_statuses":types,
            "primary_exact_polygon_matched_geographical_comparison":exact,
            "secondary_provisional_nearby_polygon_source_sensitivity":near,
            "all_MAPPPD_original_nest_count_values_opened":0,
            "original_site_position_GPS_uncertainty_certified":False,
            "landpolygon_ID_is_official_named_island_ID":False,
            "source_polygon_continuity_is_island_causal_effect":False,
            "scientific_decision":("PROCEED_SEPARATE_FROZEN_V42_BIOLOGICAL_TEST"
                if exact["future_island_boundary_sample_gate_passes"] else
                "STOP_STRICT_WITHIN_VS_BETWEEN_LAND_POLYGON_GEOGRAPHY_SUPPORT")
        }
    except Exception as ex:
        report["error_type"]=type(ex).__name__;report["error"]=str(ex)[:730]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"]=="HOLD_ORIGINAL_SOURCE_GEOMETRY":raise SystemExit(2)
if __name__=="__main__":main()
