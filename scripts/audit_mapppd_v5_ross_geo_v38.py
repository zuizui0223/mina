#!/usr/bin/env python3
"""V38: MAPPPD v5 public site positions × original SCAR highres; NO bird counts."""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlparse
import requests
from pyproj import Transformer
from shapely.geometry import Point
from shapely.strtree import STRtree
import audit_nz_ross_sea_highres_precision_v37 as v37

API="https://www.penguinmap.com/api/v1/sites/?region=Victoria%20Land&format=json"
RELEASE="https://www.penguinmap.com/api/v1/release/?format=json"
HIGH_SHA="66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4"
FROZEN_YEARS=tuple(list(range(1983,1993))+[2001,2004,2005])
GROUPS=("Beaufort Island","Coulman Island","Inexpressible Island","Ross Island")
# NZ colony: immutable MAPPPD code, source site name, NZ named island, name relation
MATCH={
 "Beaufort Island":("BEAU","Beaufort Island","Beaufort Island","EXACT"),
 "Cape Anne":("ANNE","Cape Anne","Coulman Island","EXACT"),
 "Coulman Island Middle":("CMID","Coulman Middle","Coulman Island","ABBREVIATED"),
 "Coulman Island North":("CNOR","Coulman North","Coulman Island","ABBREVIATED"),
 "Coulman Island South":("CSOU","Coulman South","Coulman Island","ABBREVIATED"),
 "Cape Bird Middle":("BRDM","Cape Bird Middle","Ross Island","EXACT"),
 "Cape Bird North":("BRDN","Cape Bird North","Ross Island","EXACT"),
 "Cape Bird South":("BRDS","Cape Bird South","Ross Island","EXACT"),
 "Cape Royds":("ROYD","Cape Royds","Ross Island","EXACT"),
 "Inexpressible Island":("INEX","Inexpressible Island","Inexpressible Island","EXACT")
}

def get_json(session,url,limit=350000):
    if urlparse(url).scheme!="https" or urlparse(url).hostname!="www.penguinmap.com":
        raise ValueError("SOURCE_STOP untrusted MAPPPD URL")
    with session.get(url,stream=True,timeout=(18,60),headers={"Accept":"application/json",
        "User-Agent":"mina-v38-published-only-site-geography"}) as r:
        r.raise_for_status()
        if urlparse(r.url).hostname!="www.penguinmap.com":
            raise ValueError("SOURCE_STOP MAPPPD redirected to another origin")
        b=bytearray()
        for chunk in r.iter_content(16384):
            b.extend(chunk)
            if len(b)>limit:raise ValueError("SOURCE_STOP MAPPPD public API over bounded size")
        raw=bytes(b)
        if not raw or raw[:1] not in (b"{",b"["):
            raise ValueError("SOURCE_STOP source JSON absent")
        return json.loads(raw),{"source_sha256":hashlib.sha256(raw).hexdigest(),
            "source_bytes":len(raw),"X_MAPPPD_version":r.headers.get("X-MAPPPD-Version")}

def match_sites(release,source):
    if release.get("version")!="5.0" or release.get("release_date")!="2026-10-21":
        raise ValueError("SOURCE_STOP MAPPPD version/release date drift")
    if not isinstance(source,list) or not 30<=len(source)<=800:
        raise ValueError("SOURCE_STOP Victoria Land API site list invalid")
    by_code=defaultdict(list)
    for item in source:by_code[str(item.get("site_id",""))].append(item)
    records={}
    for colony,(site_id,expected,island,relation) in MATCH.items():
        opts=by_code.get(site_id,[])
        if len(opts)!=1:raise ValueError("SOURCE_STOP source site ID absent/duplicated "+site_id)
        rec=opts[0]
        if rec.get("site_name")!=expected or rec.get("mapppd_version")!="5.0" or "ADPE" not in rec.get("species",[]):
            raise ValueError("SOURCE_STOP original MAPPPD source identity drift "+site_id)
        lat=rec.get("latitude");lon=rec.get("longitude")
        if (type(lat) not in (int,float) or type(lon) not in (int,float)
            or not math.isfinite(lat) or not math.isfinite(lon)
            or not -90<=lat<=-60 or not -180<=lon<=180):
            raise ValueError("SOURCE_STOP original MAPPPD coordinate invalid "+site_id)
        records[colony]={"source_NZ_colony_name":colony,"MAPPPD_id":site_id,
            "MAPPPD_name":expected,"fixed_NZ_original_named_island":island,
            "name_match":relation,"MAPPPD_latitude":float(lat),"MAPPPD_longitude":float(lon)}
    if Counter(z["name_match"] for z in records.values())!={"EXACT":7,"ABBREVIATED":3}:
        raise ValueError("SOURCE_STOP frozen exact source matches drift")
    return records

def site_land_overlay(source,shapes):
    polygons=[x[1] for x in shapes]
    tree=STRtree(polygons)
    mainland=max(range(len(polygons)),key=lambda i:polygons[i].area)
    project=Transformer.from_crs(4326,3031,always_xy=True)
    output={}
    for name,row in source.items():
        xx,yy=project.transform(row["MAPPPD_longitude"],row["MAPPPD_latitude"])
        pt=Point(xx,yy)
        matches=list(map(int,tree.query(pt.buffer(2000.))))
        inside=[i for i in matches if polygons[i].covers(pt)]
        if len(inside)==1:
            index=inside[0];status="EXACT_ONE_LAND_POLYGON"
        elif len(inside)>1:
            index=None;status="HOLD_MULTIPLE_CONTAINING_LAND_POLYGONS"
        else:
            nearest=[i for i in matches if polygons[i].distance(pt)<=2000.]
            index=nearest[0] if len(nearest)==1 else None
            status="NEAR_UNIQUE_2KM_ONLY" if len(nearest)==1 else "HOLD_AMBIGUOUS_OR_UNMATCHED"
        exact=status=="EXACT_ONE_LAND_POLYGON" and index!=mainland
        output[name]={**row,"SCAR_highres_source_polygon_id":int(index) if index is not None else None,
            "source_match_type":status,"exact_separate_land_containment":bool(exact),
            "coastline_distance_m":round(float(pt.distance(polygons[index].boundary)),1) if index is not None else None,
            "hypothetical_250m_disk_completely_within_land":bool(exact and polygons[index].covers(pt.buffer(250))),
            "hypothetical_1000m_disk_completely_within_land":bool(exact and polygons[index].covers(pt.buffer(1000))),
            "original_field_GPS_accuracy_verified":False}
    return output

def support_scenarios(rows,v35):
    panel=v35["prespecified_original_GIS_locus_year_support"]["source_named_GIS_island_temporal_support"]
    options=(("exact_names_center",False,"exact_separate_land_containment"),
             ("all_fixed_names_center",True,"exact_separate_land_containment"),
             ("exact_names_250m",False,"hypothetical_250m_disk_completely_within_land"),
             ("exact_names_1000m",False,"hypothetical_1000m_disk_completely_within_land"))
    ans={}
    for label,abbreviations,flag in options:
        islands={}
        poly={}
        for island in GROUPS:
            sites=[(name,r) for name,r in rows.items() if r["fixed_NZ_original_named_island"]==island
                   and (abbreviations or r["name_match"]=="EXACT") and r[flag]]
            indices={r["SCAR_highres_source_polygon_id"] for name,r in sites}
            if len(indices)==1 and sites:
                poly[island]=next(iter(indices))
                islands[island]={name for name,r in sites}
        repeated={p for p,n in Counter(poly.values()).items() if n>1}
        for isl in list(poly):
            if poly[isl] in repeated:
                del islands[isl];del poly[isl]
        chosen={}
        obs=defaultdict(list)
        for isle,allowed in islands.items():
            pairs={}
            for year,names in panel[isle]["original_fixed_source_colonies_by_annual_window"].items():
                y=int(year)
                if y not in FROZEN_YEARS:continue
                matched=sorted(set(names)&allowed)
                if matched:
                    pairs[y]=matched
                    obs[y].append(isle)
            chosen[isle]=pairs
        years=sorted(y for y,isles in obs.items() if len(isles)>=2)
        qualified=sum(len(x)>=5 for x in chosen.values())
        ans[label]={
            "MAPPPD_matching_source_name_policy":"inclusive source alias" if abbreviations else "exact literal only",
            "source_geographically_candidate_named_islands":sorted(islands),
            "named_island_to_highres_land_feature_id":poly,
            "source_matched_colony_year_pair_roster":{isl:{str(y):sites for y,sites in vals.items()} for isl,vals in chosen.items()},
            "n_original_islands_ge5_adjacent_years":qualified,
            "years_ge2_named_islands":years,"n_same_year_island_comparisons":len(years),
            "frozen_source_temporal_support_pass":qualified>=3 and len(years)>=8}
    return ans

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",type=Path,required=True)
    args=p.parse_args()
    result={"status":"HOLD_MAPPPD_V5_SOURCE_OR_SCAR_GEO","ecological_effects_fitted":0}
    try:
        frozen=v37.load_fixed_v35()
        with requests.Session() as session:
            release,releasemeta=get_json(session,RELEASE)
            sites,sitemeta=get_json(session,API)
        fixed=match_sites(release,sites)
        # Exact original colony names already checked in V35 and V37.
        origin=v37.original_publisher_sites()
        known={r["original_census_colony"] for r in origin["site_to_named_island_crosswalk"]}
        if not set(fixed).issubset(known):
            raise ValueError("SOURCE_STOP new MAPPPD sites not fixed original NZ colony names")
        trans=Transformer.from_crs(4326,3031,always_xy=True)
        spots={}
        for name,row in fixed.items():
            x,y=trans.transform(row["MAPPPD_longitude"],row["MAPPPD_latitude"])
            spots[name]=[{"x":x,"y":y}]
        features,geodata,high=v37.high_source_zip_and_shapes(spots)
        if high["sha256"]!=HIGH_SHA:
            raise ValueError("SOURCE_STOP SCAR high-res source SHA drift")
        geography=site_land_overlay(fixed,features)
        cohorts=support_scenarios(geography,frozen)
        result={"status":"V38_MAPPPD_V5_PUBLISHED_SOURCE_SITE_GEO_CROSSWALK",
            "MAPPPD_public_release":{"version":release["version"],"date":release["release_date"],
                "original_JSON_SHA256":releasemeta["source_sha256"]},
            "MAPPPD_original_VictoriaLand_site_metadata_sha256":sitemeta["source_sha256"],
            "original_SCAR_highres_zip_sha256":HIGH_SHA,
            "original_SCAR_highres_polygon_count":geodata["valid_source_land_features"],
            "original_NZ_V35_source_cohort_unchanged":True,
            "public_fixed_crosspublisher_colony_site_coordinates":geography,
            "source_only_gis_and_annual_availability_scenarios":cohorts,
            "MAPPPD_site_coordinates_NOT_verifiable_original_GPS_accuracy":True,
            "original_Adelie_observation_counts_opened":0,
            "V36_biological_effects_reestimated":False,
            "scientific_decision":("NEW_LOCATION_SOURCE_CENTER_SUPPORT_BUT_GPS_UNVERIFIED"
                if cohorts["exact_names_center"]["frozen_source_temporal_support_pass"]
                else "HOLD_SITE_IDENTITY_OR_PRECISE_GEOREFERENCE_SUPPORT")}
    except Exception as ex:
        result["error_type"]=type(ex).__name__;result["error"]=str(ex)[:750]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]=="HOLD_MAPPPD_V5_SOURCE_OR_SCAR_GEO":raise SystemExit(2)

if __name__=="__main__":
    main()
