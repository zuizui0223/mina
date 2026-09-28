#!/usr/bin/env python3
"""Gate 1A v3: service-native APBP site-to-SCAR ADD land matching.

No demographic outcomes are read. The frozen 122 candidate sites are queried
directly against the SCAR ADD FeatureServer using returnIdsOnly at the
predeclared distances 0/500/1000/2000/5000 m.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import pyreadr
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

MAPPPDR_COMMIT="88c73a507e0921b2541c218c71eaf16721bc6502"
LAYER=(
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer/1"
)
PRIMARY_SPECIES=("ADPE","CHPE","GEPE")
DISTANCES=(0,500,1000,2000,5000)


def load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        frame=x[expected]
    elif len(x)==1:
        frame=next(iter(x.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(x)}")
    if not isinstance(frame,pd.DataFrame):
        raise TypeError(expected)
    return frame


def candidate_sites(root:Path)->pd.DataFrame:
    sites=load_rda(root/"data"/"sites.rda","sites")
    obs=load_rda(root/"data"/"penguin_obs.rda","penguin_obs")
    nest=obs[
        obs["species_id"].isin(PRIMARY_SPECIES)
        & (obs["type"]=="nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest=nest.dropna(subset=["year"])

    units=[]
    for (site_id,species_id),local in nest.groupby(["site_id","species_id"]):
        years=sorted(set(int(y) for y in local["year"]))
        if len(years)>=5 and max(years)-min(years)>=10:
            units.append((str(site_id),str(species_id)))
    if len(units)!=152:
        raise ValueError(f"candidate unit drift: {len(units)} != 152")
    ids=sorted({site_id for site_id,_ in units})
    out=sites[sites["site_id"].isin(ids)].copy()
    if len(out)!=122:
        raise ValueError(f"candidate site drift: {len(out)} != 122")
    return out[["site_id","site_name","region","ccamlr_id","latitude","longitude"]]


def session()->requests.Session:
    s=requests.Session()
    retry=Retry(
        total=8,
        backoff_factor=1.0,
        status_forcelist=(429,500,502,503,504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://",HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent":"mina-antarctic-island-atlas-gate1a-v3/1.0"})
    return s


def query_ids(
    s:requests.Session,
    lon:float,
    lat:float,
    distance:int,
    max_attempts:int=20,
)->list[int]:
    geometry=json.dumps({
        "x":float(lon),
        "y":float(lat),
        "spatialReference":{"wkid":4326},
    })
    params={
        "f":"json",
        "where":"surface='land'",
        "geometry":geometry,
        "geometryType":"esriGeometryPoint",
        "inSR":4326,
        "spatialRel":"esriSpatialRelIntersects",
        "returnIdsOnly":"true",
    }
    if distance>0:
        params["distance"]=int(distance)
        params["units"]="esriSRUnit_Meter"

    for attempt in range(1,max_attempts+1):
        r=s.get(LAYER+"/query",params=params,timeout=120)
        if r.status_code==429:
            retry_after=float(r.headers.get("Retry-After","65"))
            time.sleep(max(65.0,retry_after))
            continue
        r.raise_for_status()
        x=r.json()
        error=x.get("error")
        if error:
            if int(error.get("code",0))==429:
                time.sleep(65.0)
                continue
            raise RuntimeError(error)
        return sorted(int(v) for v in (x.get("objectIds") or []))
    raise RuntimeError(
        f"ArcGIS quota retry exhausted at lon={lon}, lat={lat}, "
        f"distance={distance}"
    )


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--delay-s",type=float,default=0.10)
    a=p.parse_args()

    sites=candidate_sites(a.mapppdr_dir)
    s=session()
    records=[]
    api_calls=0

    for row in sites.to_dict(orient="records"):
        matches={}
        for distance in DISTANCES:
            ids=query_ids(s,float(row["longitude"]),float(row["latitude"]),distance)
            matches[str(distance)]=ids
            api_calls+=1
            if a.delay_s>0:
                time.sleep(a.delay_s)
        records.append({
            "site_id":str(row["site_id"]),
            "site_name":str(row["site_name"]),
            "region":str(row["region"]),
            "ccamlr_id":None if pd.isna(row["ccamlr_id"]) else str(row["ccamlr_id"]),
            "latitude":float(row["latitude"]),
            "longitude":float(row["longitude"]),
            "matching_fids":matches,
        })
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(
            json.dumps(
                {
                    "schema_version":3,
                    "audit_id":"mina-antarctic-add-site-match-audit-v3",
                    "status":"running",
                    "completed_sites":len(records),
                    "expected_sites":122,
                    "api_calls":api_calls,
                    "site_matches":records,
                },
                indent=2,
                sort_keys=True,
            )+"\\n",
            encoding="utf-8",
        )

    summaries={}
    selected=None
    n=len(records)
    for distance in DISTANCES:
        key=str(distance)
        counts=[len(r["matching_fids"][key]) for r in records]
        any_n=sum(v>=1 for v in counts)
        multi=sum(v>1 for v in counts)
        rec={
            "distance_m":distance,
            "candidate_sites":n,
            "land_match_count":any_n,
            "land_match_fraction":any_n/n,
            "multiple_land_match_count":multi,
            "multiple_land_match_fraction":multi/n,
            "unmatched_count":n-any_n,
        }
        summaries[key]=rec
        if (
            selected is None
            and rec["land_match_fraction"]>=0.95
            and rec["multiple_land_match_fraction"]<=0.05
        ):
            selected=distance

    region_summary={}
    for region in sorted({r["region"] for r in records}):
        local=[r for r in records if r["region"]==region]
        region_summary[region]={
            "candidate_sites":len(local),
            "exact_match_count":sum(len(r["matching_fids"]["0"])>=1 for r in local),
            "within_5km_match_count":sum(len(r["matching_fids"]["5000"])>=1 for r in local),
            "within_5km_multiple_count":sum(len(r["matching_fids"]["5000"])>1 for r in local),
            "unmatched_within_5km":[
                r["site_id"] for r in local if not r["matching_fids"]["5000"]
            ],
        }

    result={
        "schema_version":3,
        "audit_id":"mina-antarctic-add-site-match-audit-v3",
        "implementation":"FeatureServer returnIdsOnly spatial queries; no local polygon reconstruction",
        "mapppdr_commit":MAPPPDR_COMMIT,
        "candidate_species_ids":list(PRIMARY_SPECIES),
        "candidate_site_species_units":152,
        "distinct_candidate_sites":122,
        "api_calls":api_calls,
        "candidate_distances_m":list(DISTANCES),
        "distance_summaries":summaries,
        "region_summary":region_summary,
        "selected_distance_m":selected,
        "gate1a_passed":selected is not None,
        "site_matches":records,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="site_matches"},indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
