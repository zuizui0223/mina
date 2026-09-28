#!/usr/bin/env python3
"""Gate 1A v5: throttled outcome-blind unique SCAR land-FID assignment."""
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
BRACKETS=(500,1000,2000,5000)
PRECISION_M=25


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


def make_session()->requests.Session:
    s=requests.Session()
    retry=Retry(
        total=6,
        backoff_factor=2.0,
        status_forcelist=(429,500,502,503,504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://",HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent":"mina-antarctic-island-atlas-gate1a-v5/1.0"})
    return s


def query_ids(
    s:requests.Session,
    lon:float,
    lat:float,
    distance:int,
    cache:dict[int,list[int]],
    delay_s:float,
)->list[int]:
    if distance in cache:
        return cache[distance]

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

    r=s.get(LAYER+"/query",params=params,timeout=120)
    r.raise_for_status()
    x=r.json()
    if x.get("error"):
        raise RuntimeError(x["error"])
    ids=sorted(int(v) for v in (x.get("objectIds") or []))
    cache[distance]=ids
    if delay_s>0:
        time.sleep(delay_s)
    return ids


def resolve_site(s,row,delay_s:float):
    lon=float(row["longitude"]); lat=float(row["latitude"])
    cache={}

    exact=query_ids(s,lon,lat,0,cache,delay_s)
    if len(exact)==1:
        status="assigned_exact"; assigned=exact[0]
        lower=upper=0
    elif len(exact)>1:
        status="ambiguous_exact"; assigned=None
        lower=upper=0
    else:
        lower=0
        upper=None
        for radius in BRACKETS:
            ids=query_ids(s,lon,lat,radius,cache,delay_s)
            if ids:
                upper=radius
                break
            lower=radius
        if upper is None:
            status="unresolved_no_land_within_5km"; assigned=None
        else:
            while upper-lower>PRECISION_M:
                mid=(lower+upper)//2
                ids=query_ids(s,lon,lat,mid,cache,delay_s)
                if ids:
                    upper=mid
                else:
                    lower=mid
            ids=query_ids(s,lon,lat,upper,cache,delay_s)
            if len(ids)==1:
                status="assigned_nearest"; assigned=ids[0]
            else:
                status="ambiguous_nearest_band"; assigned=None

    return {
        "site_id":str(row["site_id"]),
        "site_name":str(row["site_name"]),
        "region":str(row["region"]),
        "ccamlr_id":None if pd.isna(row["ccamlr_id"]) else str(row["ccamlr_id"]),
        "latitude":lat,
        "longitude":lon,
        "assignment_status":status,
        "assigned_fid":assigned,
        "lower_no_match_m":lower if exact==[] else 0,
        "upper_match_m":upper if exact==[] else 0,
        "distance_precision_m":PRECISION_M,
        "exact_fids":exact,
        "upper_match_fids":cache.get(upper,[]) if upper is not None else [],
        "queried_distances_m":sorted(cache),
        "api_calls":len(cache),
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--delay-s",type=float,default=0.5)
    a=p.parse_args()

    sites=candidate_sites(a.mapppdr_dir)
    s=make_session()
    records=[]

    for row in sites.to_dict(orient="records"):
        rec=resolve_site(s,row,a.delay_s)
        records.append(rec)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps({
            "schema_version":5,
            "status":"running",
            "completed_sites":len(records),
            "expected_sites":122,
            "api_calls":sum(r["api_calls"] for r in records),
            "site_assignments":records,
        },indent=2,sort_keys=True)+"\n",encoding="utf-8")

    assigned_status={"assigned_exact","assigned_nearest"}
    unique=[r for r in records if r["assignment_status"] in assigned_status]
    unresolved=[r for r in records if r["assignment_status"] not in assigned_status]
    n=len(records)

    status_counts={}
    for r in records:
        status_counts[r["assignment_status"]]=status_counts.get(r["assignment_status"],0)+1

    region_summary={}
    for region in sorted({r["region"] for r in records}):
        local=[r for r in records if r["region"]==region]
        good=[r for r in local if r["assignment_status"] in assigned_status]
        region_summary[region]={
            "candidate_sites":len(local),
            "unique_assignments":len(good),
            "unique_assignment_fraction":len(good)/len(local),
            "unresolved_site_ids":[
                r["site_id"] for r in local
                if r["assignment_status"] not in assigned_status
            ],
        }

    nearest_widths=[
        int(r["upper_match_m"]-r["lower_no_match_m"])
        for r in records
        if r["assignment_status"] in {"assigned_nearest","ambiguous_nearest_band"}
        and r["upper_match_m"] is not None
    ]

    result={
        "schema_version":5,
        "audit_id":"mina-antarctic-add-site-assignment-v5",
        "implementation":"FeatureServer exact containment plus throttled bracketed nearest search to 25 m precision",
        "mapppdr_commit":MAPPPDR_COMMIT,
        "candidate_species_ids":list(PRIMARY_SPECIES),
        "candidate_site_species_units":152,
        "distinct_candidate_sites":n,
        "api_calls":sum(r["api_calls"] for r in records),
        "distance_precision_m":PRECISION_M,
        "assignment_status_counts":status_counts,
        "unique_assignment_count":len(unique),
        "unique_assignment_fraction":len(unique)/n,
        "unresolved_count":len(unresolved),
        "unresolved_fraction":len(unresolved)/n,
        "maximum_nearest_bracket_width_m":max(nearest_widths) if nearest_widths else 0,
        "region_summary":region_summary,
        "gate1a_passed":len(unique)/n>=0.95 and len(unresolved)/n<=0.05,
        "site_assignments":records,
    }
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="site_assignments"},indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
