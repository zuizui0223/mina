#!/usr/bin/env python3
"""Response-blind 2013–2021 L8 OLI separate-sensor scene source feasibility.

Original 88 geography source-only; no optical Y or stable isotope fit; L8 gate preserved.
Before use, L8 OLI requires new RSR/103-original-guano lab calibration and guano-ROI source gate.
See L8_ALT_SENSOR_NEGATIVE_POLYNYA_PRE_Y_SOURCE_AND_CALIBRATION_GATE_20261120_JA.md.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import io
import json
from pathlib import Path
import time
import zipfile
import requests
import pandas as pd

SOURCE_SHA256="702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96"
SITES_CSV="source_original_88_site_polynya_25km_100km_native_grid_geography.csv"
STAC="https://earth-search.aws.element84.com/v1/search"
STAC_COLLECTION="landsat-c2-l2"
TARGET_PLATFORM="landsat-8"
# 2013 Nov through 2022 Feb: original source season y Nov-Dec + y+1 Jan-Feb
NEW_DATES="2013-11-01T00:00:00Z/2022-03-01T00:00:00Z"
CONTROL_DATES="2014-11-01T00:00:00Z/2021-03-01T00:00:00Z"
REQUEST_TIMEOUT=40
MAX_PAGES=12
PAGE_LIMIT=100

def source_sites(path):
    b=Path(path).read_bytes()
    digest=hashlib.sha256(b).hexdigest()
    if digest!=SOURCE_SHA256:
        raise ValueError(f"Original native source-only 88-site artifact SHA256 mismatch: {digest}")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip():raise ValueError("Original source-only ZIP CRC fail")
        names=[n for n in z.namelist() if n==SITES_CSV or n.endswith("/"+SITES_CSV)]
        if len(names)!=1:raise ValueError("Source-only 88 site coordinate CSV missing or duplicated")
        d=pd.read_csv(io.BytesIO(z.read(names[0])))
    if len(d)!=176 or not d.radius_km.isin([25,100]).all():
        raise ValueError("Source-only 88 site×2 fixed radius geography changed")
    d=d.loc[d.radius_km.eq(100)].copy().sort_values("site_id").reset_index(drop=True)
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(88,88,13):
        raise ValueError("Original 88/13 source-only coordinate population changed")
    if not d.colony_lat.between(-90,-50).all() or not d.colony_lon.between(-180,180).all():
        raise ValueError("Original colony coordinate bounds invalid")
    return d

def query_source_point(site,period):
    # Positive control catalog control uses identical point/collection/source filter.
    if period not in ("control","new"):raise ValueError("Unexpected period")
    source_datetime=CONTROL_DATES if period=="control" else NEW_DATES
    payload={"collections":[STAC_COLLECTION],
             "intersects":{"type":"Point","coordinates":[float(site.colony_lon),float(site.colony_lat)]},
             "datetime":source_datetime,
             "limit":PAGE_LIMIT,
             "query":{"platform":{"eq":TARGET_PLATFORM}}}
    session=requests.Session()
    session.headers.update({"Accept":"application/geo+json, application/json","User-Agent":"mina-original88-L8-scene-metadata-gate/1.0"})
    features=[]
    paging=0
    nexturl=STAC
    nextpayload=payload
    try:
        while nexturl:
            if paging>=MAX_PAGES:raise RuntimeError("STAC pagination cap reached; cannot declare zero/absence")
            data=None
            for attempt in range(4):
                try:
                    if nextpayload is not None:
                        response=session.post(nexturl,json=nextpayload,timeout=REQUEST_TIMEOUT)
                    else:
                        response=session.get(nexturl,timeout=REQUEST_TIMEOUT)
                    response.raise_for_status()
                    data=response.json()
                    break
                except (requests.RequestException,ValueError):
                    if attempt==3:raise
                    time.sleep(2**attempt)
            if not isinstance(data,dict) or "features" not in data:
                raise ValueError("Provider returned non-STAC search item features")
            for item in data["features"]:
                prop=item.get("properties",{})
                platform=(prop.get("platform") or "").lower().replace("_","-")
                instruments=[str(s).lower() for s in prop.get("instruments",[])]
                if platform!=TARGET_PLATFORM and ("oli" not in instruments and "oli_tirs" not in instruments):
                    raise ValueError("Server-side Landsat 8-only query returned other sensor; cannot trust filtered catalog")
                dt=prop.get("datetime") or prop.get("start_datetime")
                if not dt or not item.get("id"):
                    raise ValueError("Actual STAC item missing true source ID or datetime")
                yr=int(dt[:4]);month=int(dt[5:7])
                season=yr if month in (11,12) else yr-1 if month in (1,2) else None
                # source item search may return out-of-season imagery, keep only Nov-Feb
                if season is None or (period=="new" and not 2013<=season<=2021):
                    continue
                features.append({
                   "site_id":str(site.site_id),"original_region":str(site.source_region),
                   "original_colony_lat":float(site.colony_lat),"original_colony_lon":float(site.colony_lon),
                   "catalog":"Element84 Earth Search v1","period":period,"season":int(season),
                   "scene_id":str(item["id"]),"source_scene_datetime":str(dt),
                   "platform":platform,"sensor_instruments":";".join(instruments),
                   "wrs_path":prop.get("landsat:wrs_path"),"wrs_row":prop.get("landsat:wrs_row"),
                   "processing_level":prop.get("landsat:processing_level"),
                   "eo_cloud_cover_scene_percent":prop.get("eo:cloud_cover"),
                   "source_scene_type":str(item.get("type")),
                   "source_assets_have_QA_pixel":"qa_pixel" in (item.get("assets") or {}),
                   "source_assets_have_SR_B1":"red" in (item.get("assets") or {}) or "blue" in (item.get("assets") or {}),
                })
            paging+=1
            rel=[x for x in data.get("links",[]) if x.get("rel")=="next"]
            if len(rel)>1:raise ValueError("Multiple STAC next links")
            if rel:
                node=rel[0]
                nexturl=node.get("href")
                if not nexturl:raise ValueError("STAC next href missing")
                # STAC API GET next can reuse url; POST next sometimes has own body.
                nextpayload=node.get("body") if node.get("method","GET").upper()=="POST" else None
                if nextpayload is None and node.get("method","GET").upper()=="POST":
                    raise ValueError("Provider POST pagination missing next page body")
            else:
                nexturl=None
        return {"site_id":str(site.site_id),"period":period,
                "status":"SOURCE_CATALOG_QUERY_VALID",
                "source_datetime":source_datetime,"n_response_pages":paging,
                "total_valid_season_scene_metadata_matches":len(features)},features
    finally:
        session.close()

def main(a):
    sites=source_sites(a.source_only_geography_zip)
    # Compare one fixed separate 2014–2020 metadata-control site from each of three
    # differently placed geographical regions; not selected by target outcome.
    controls=[]
    for region in ("Victoria Land","Wilkes Land","Southwest Antarctic Peninsula"):
        subs=sites[sites.source_region.eq(region)]
        if len(subs)==0:raise ValueError("Missing prespecified control control geography")
        controls.append(next(subs.itertuples(index=False)))
    tasks=[(s,"new") for s in sites.itertuples(index=False)]+[(s,"control") for s in controls]
    receipts=[];itemrows=[];failures=[]
    with ThreadPoolExecutor(max_workers=4) as ex:
        jobmap={ex.submit(query_source_point,s,period):(s.site_id,period) for s,period in tasks}
        for job in as_completed(jobmap):
            site_id,period=jobmap[job]
            try:
                receipt,records=job.result()
                receipts.append(receipt)
                itemrows.extend(records)
            except Exception as e:
                failures.append({"site_id":str(site_id),"period":period,"error":f"{type(e).__name__}: {str(e)[:500]}"})
    a.out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(receipts).to_csv(a.out/"original_88_L8_STAC_query_receipts.csv",index=False)
    if itemrows:
        items=pd.DataFrame(itemrows).drop_duplicates(["site_id","period","scene_id"]).sort_values(["period","site_id","source_scene_datetime"])
    else:
        items=pd.DataFrame(columns=["site_id","period","season","scene_id"])
    items.to_csv(a.out/"original_88_L8_real_scene_metadata_no_Y.csv",index=False)
    counts=items.loc[items.period.eq("new")].groupby(["season","original_region"]).agg(
       site_scene_records=("scene_id","size"),sites_with_scene=("site_id","nunique")).reset_index() if len(items)>0 and "original_region" in items else pd.DataFrame()
    counts.to_csv(a.out/"original_88_L8_scene_presence_by_year_region_no_Y.csv",index=False)
    nnew=int(sum(q["period"]=="new" for q in receipts))
    ncontrol=int(sum(q["period"]=="control" and q["total_valid_season_scene_metadata_matches"]>0 for q in receipts))
    metadata_sites=int(items.loc[items.period.eq("new"),"site_id"].nunique()) if len(items) else 0
    source_regions=int(items.loc[items.period.eq("new"),"original_region"].nunique()) if len(items) and "original_region" in items else 0
    years=int(items.loc[items.period.eq("new"),"season"].nunique()) if len(items) else 0
    # Note: these are scene-coverage *upper bounds*, not clean guano pixel outcomes.
    if failures or nnew!=88 or len(receipts)!=91:
        status="DATA_SOURCE_UNVERIFIED"
    elif ncontrol<1:
        status="CATALOG_QUERY_UNVALIDATED_CONTROL_L8_SCENE_MISSING"
    elif metadata_sites<30 or source_regions<6 or years<4:
        status="NO_GO_L8_SCENE_SOURCE_SUPPORT"
    else:
        status="PASS_L8_SCENE_METADATA_ONLY_NEEDS_NEW_SENSOR_RSR_PLRS_AND_GUANO_QA"
    result={
      "status":status,
      "contract":"L8_ALT_SENSOR_NEGATIVE_POLYNYA_PRE_Y_SOURCE_AND_CALIBRATION_GATE_20261120_JA.md",
      "independent_source_only_prior_geography_sha256":SOURCE_SHA256,
      "original_88_site_population":len(sites),"original_13_regions":int(sites.source_region.nunique()),
      "new_years_frozen":[int(y) for y in range(2013,2022)],
      "source_provider":"Earth Search v1 STAC USGS Landsat Collection2 Level2 catalog",
      "sensor_used_only_for_catalog":"landsat-8",
      "three_separate_2014_2020_validation_query_controls":len(controls),
      "2014_2020_controls_with_a_matching_scene":ncontrol,
      "new_sites_catalog_succeeded":nnew,
      "catalog_sites_with_any_novfeb_scene":metadata_sites,
      "catalog_regions_with_any_novfeb_scene":source_regions,
      "catalog_seasons_with_any_novfeb_scene":years,
      "per_site_raw_results_count":int(len(items.loc[items.period.eq("new")])) if len(items) else 0,
      "query_failures":failures,
      "no_2013_2021_reflectance_or_guano_pixel_read":True,
      "no_optical_delta15N_computed":True,
      "no_polynya_effect_model_fitted":True,
      "catalog_scene_hit_not_proof_clean_valid_guano":True,
      "new_sensor_not_a_substitution_for_frozen_L8":True,
    }
    (a.out/"ORIGINAL88_L8_2013_2021_SEPARATE_SENSOR_SCENE_GATE.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False),flush=True)
    # Missing catalog is an observational no-go, NOT CI implementation error.
    if status=="DATA_SOURCE_UNVERIFIED":
        raise RuntimeError(f"All original 88 source catalog queries not verified: {failures[:3]}")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-only-geography-zip",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    main(parser.parse_args())
