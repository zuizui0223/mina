#!/usr/bin/env python3
"""Actually retrieve QA-filtered ORIGINAL Landsat-8 source spectral measurements.

Only 50 observed colony site-years from Git-blob-pinned existing original tables.
Fixed 77 EPSG:3031 points within 2 km per site, consistent across seasons.
No true vegetation labels, no penguin outcome modeling, and no significant p tests.

Original STAC: Planetary Computer / landsat-c2-l2 / USGS Landsat 8 C2 L2.
Assets: qa_pixel, qa_radsat, red, nir08; original COGs accessed via SDK SAS.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SRC=HERE/"outputs"
JOINT=HERE/"joint_support_outputs"
OUT=HERE/"landsat_original_outputs"
OUT.mkdir(parents=True,exist_ok=True)

STAC="https://planetarycomputer.microsoft.com/api/stac/v1/search"
COLLECTION="landsat-c2-l2"
BANDS=("qa_pixel","qa_radsat","red","nir08")
BAD_QA_BITS=(0,1,2,3,4,5,7)
OFFSETS_M=tuple(range(-1600,1601,400))
GRID=[(dx,dy) for dy in OFFSETS_M for dx in OFFSETS_M
      if dx*dx+dy*dy<=2000*2000]
assert len(GRID)==77
N_SCENES=3
CLOUD_MAX=100
YEARS=(2017,2018,2019,2020)
SITES=25
SUMMER_START="12-01T00:00:00Z"
SUMMER_END="02-28T23:59:59Z"

def table(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_table(path, rows, expected=None):
    if not rows:
        if expected is None:raise ValueError("Empty source record not allowed")
        fields=expected
    else:
        fields=list(rows[0])
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="raise")
        w.writeheader()
        w.writerows(rows)

def req_page(url, payload, method):
    error=None
    for attempt in range(3):
        try:
            data=json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8") if method=="POST" else None
            with urlopen(Request(url,data=data,method=method,headers={
                "Content-Type":"application/json",
                "Accept":"application/geo+json,application/json",
                "User-Agent":"mina-Landsat8-original-25site-summer-source-gate-20261109"
            }),timeout=55) as f:
                raw=f.read(8000000)
            obj=json.loads(raw)
            if not isinstance(obj,dict) or not isinstance(obj.get("features"),list):
                raise ValueError("STAC response not a FeatureCollection")
            return obj,hashlib.sha256(raw).hexdigest()
        except (HTTPError,URLError,TimeoutError,OSError,ValueError) as e:
            error=e
            if isinstance(e,HTTPError) and e.code not in (408,429,500,502,503,504):
                break
            time.sleep(0.8+attempt*1.4)
    raise RuntimeError(f"{type(error).__name__}: {str(error)[:180]}")

def stac(site,lat,lon,year):
    lat=float(lat); lon=float(lon)
    if not(-90<=lat<=-50 and -180<=lon<=180):
        raise ValueError("Invalid source coordinate at Antarctic penguin site")
    # Source *only* center query; no spatial search shifted to locations with
    # favorable NDVI. STAC scenes can intersect the center and miss 2km edges.
    bbox=[lon-.002,lat-.002,lon+.002,lat+.002]
    query={"collections":[COLLECTION],"bbox":bbox,
           "datetime":f"{year}-{SUMMER_START}/{year+1}-{SUMMER_END}",
           "limit":100}
    data=[]
    url=STAC
    seen=set()
    digests=[]
    for pageno in range(10):
        key=(url,json.dumps(query,sort_keys=True) if query is not None else None)
        if key in seen:raise ValueError("STAC source pagination loop")
        seen.add(key)
        page,digest=req_page(url,query,"POST" if query is not None else "GET")
        digests.append(digest)
        data.extend(page["features"])
        links=[z for z in page.get("links",[]) if z.get("rel")=="next"]
        if not links:
            break
        if len(links)!=1:raise ValueError("Ambiguous next page")
        link=links[0]
        nxt=urljoin(url,link.get("href",""))
        # STAC pagination must stay on official Planetary Computer service.
        if urlparse(nxt).netloc!=urlparse(STAC).netloc:
            raise ValueError("Unexpected STAC next-page host")
        method=link.get("method","GET").upper()
        if method=="GET":query=None
        elif method=="POST":query=link.get("body",{})
        else:raise ValueError("Unexpected STAC pagination method")
        url=nxt
    else:
        raise ValueError("Source STAC pagination >10 pages; incomplete")
    selected=[]
    for z in data:
        props=z.get("properties") or {}
        if not str(z.get("id","")).startswith("LC08_"):
            continue
        assets=z.get("assets") or {}
        if not all(k in assets and assets[k].get("href") for k in BANDS):
            continue
        timestamp=props.get("datetime","")
        if not timestamp[:10]:continue
        day=timestamp[:10]
        cloud=props.get("eo:cloud_cover")
        try:
            cloud=float(cloud) if cloud is not None else 101.
        except (ValueError,TypeError):
            cloud=101.
        if cloud>CLOUD_MAX:continue
        selected.append({"item_id":z["id"],"day":day,
           "cloud_pct":cloud,"scene":z,"source_json_sha":hashlib.sha256(
           json.dumps(z,sort_keys=True).encode()).hexdigest()})
    # No local optical values were inspected for item selection.
    selected.sort(key=lambda x:(x["cloud_pct"],x["day"],x["item_id"]))
    uniq=[];dates=set()
    for x in selected:
        if x["day"] in dates:continue
        uniq.append(x)
        dates.add(x["day"])
        if len(uniq)==N_SCENES:break
    return {
      "site_id":site,"survey_season":year,
      "all_provider_features":len(data),
      "suitable_Landsat8_with_all_assets":len(selected),
      "selected_qa_blind_scene_days":len(uniq),
      "source_stac_pages":len(digests),
      "stac_sha256_each_page":";".join(digests),
      "source_host":urlparse(STAC).netloc
    },uniq

def selected_source(scene):
    # Original public non-expiring source URLs and item IDs only.
    return {k:((scene["scene"]["assets"][k]["href"] or "").split("?")[0])
            for k in BANDS}

def qa_clear(v):
    return not any(int(v)&(1<<b) for b in BAD_QA_BITS)

def raw_sr(dn):
    if dn is None:return None
    val=int(dn)
    if not 7273<=val<=43636:return None
    r=val*0.0000275-.2
    if not 0.0<r<=1.2:return None
    return r

def sample_spectral(site,year,loc,entry):
    import planetary_computer
    import rasterio
    from pyproj import Transformer
    # 77 fixed EPSG3031 points, not image-dependent or bird-outcome locations.
    xy=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    cx,cy=xy.transform(float(loc["longitude"]),float(loc["latitude"]))
    polar_points=[(cx+dx,cy+dy) for dx,dy in GRID]
    pointvalues={}
    scene=entry["scene"]
    urls=selected_source(entry)
    bands={}
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      GDAL_HTTP_MAX_RETRY="3",GDAL_HTTP_RETRY_DELAY="1"):
        for key,url in urls.items():
            signed=planetary_computer.sign(url)
            with rasterio.open(signed) as ds:
                source_projection=str(ds.crs)
                original_resolution=tuple(round(abs(v),5) for v in ds.res)
                transfer=Transformer.from_crs("EPSG:3031",ds.crs,always_xy=True)
                sample_coords=[transfer.transform(x,y) for x,y in polar_points]
                out=[]
                for value in ds.sample(sample_coords,masked=True):
                    mask=value.mask
                    invalid=bool(mask.any()) if hasattr(mask,"any") else bool(mask)
                    out.append(None if invalid else int(value[0]))
                if len(out)!=77:raise ValueError("Unexpected point sample count")
                bands[key]=out
        # all original bands must coincide geographically at same EPSG3031 points
    rows=[]
    reasons=Counter()
    for i,(dx,dy) in enumerate(GRID):
        qa=bands["qa_pixel"][i]
        sat=bands["qa_radsat"][i]
        red=raw_sr(bands["red"][i])
        nir=raw_sr(bands["nir08"][i])
        status="qa_clear_land_non_snow"
        ndvi=None
        if qa is None or sat is None:
            status="original_pixel_unavailable"
        elif not qa_clear(qa):
            status="cloud_snow_water_or_fill_QA"
        elif sat!=0:
            status="radiometric_saturation_or_occlusion_QA"
        elif red is None or nir is None or red+nir<=0.01:
            status="invalid_surface_reflectance"
        else:
            ndvi=(nir-red)/(nir+red)
            if not -1.0001<=ndvi<=1.0001:
                raise ValueError("NDVI outside mathematical range")
        reasons[status]+=1
        rows.append({
          "site_id":site,"survey_season":year,
          "original_item_id":entry["item_id"],"original_scene_date":entry["day"],
          "original_scene_cloud_pct":entry["cloud_pct"],
          "point_id":i,"dx_EPSG3031_m":dx,"dy_EPSG3031_m":dy,
          "qa_status":status,"ndvi":ndvi if ndvi is not None else "",
          "SR_red":red if status=="qa_clear_land_non_snow" else "",
          "SR_nir":nir if status=="qa_clear_land_non_snow" else "",
          "source_qa_pixel_raw":qa if qa is not None else "",
          "source_qa_radsat_raw":sat if sat is not None else "",
          "source_item_json_sha256":entry["source_json_sha"],
          "original_raster_resolution_m":original_resolution[0],
          "original_raster_crs":source_projection,
          "is_validated_botanical_vegetation":False,
        })
    return rows,dict(reasons),urls

def main():
    matched=table(JOINT/"matched_63_observed_rows.csv")
    original=table(JOINT/"site_25_environmental_context.csv")
    land=table(SRC/"contemporary_vegetation_site_species_197.csv")
    if len(matched)!=63 or len(original)!=25:
        raise ValueError("Wrong 63 source observations or 25 sites")
    sites={r["site_id"] for r in original}
    locations=defaultdict(list)
    for z in land:
        if z["site_id"] in sites:
            locations[z["site_id"]].append(z)
    if set(locations)!=sites:raise ValueError("Unknown 25 source land site coordinates")
    centers={}
    for k,locs in locations.items():
        values={(round(float(z["latitude"]),6),round(float(z["longitude"]),6))
                for z in locs}
        if len(values)!=1:raise ValueError("Source site coordinates vary by species: "+k)
        centers[k]={"latitude":locs[0]["latitude"],"longitude":locs[0]["longitude"]}
    actual_siteyears=sorted(set((z["site_id"],int(z["actual_census_year"])) for z in matched))
    if len(actual_siteyears)!=50 or len({z[0] for z in actual_siteyears})!=25:
        raise ValueError("Original fixed source census site-years drift")

    catalogs={}
    features={}
    # Parallel source catalog queries only; do not issue unlimited provider load.
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(stac,site,centers[site]["latitude"],
                             centers[site]["longitude"],year):(site,year)
                 for site,year in actual_siteyears}
        for future in as_completed(futures):
            site,year=futures[future]
            try:
                receipt,items=future.result()
                receipt["catalog_status"]="ok"
                receipt["error"]=""
                catalogs[(site,year)]=receipt
                features[(site,year)]=items
            except Exception as exc:
                catalogs[(site,year)]={
                  "site_id":site,"survey_season":year,
                  "all_provider_features":0,"suitable_Landsat8_with_all_assets":0,
                  "selected_qa_blind_scene_days":0,"source_stac_pages":0,
                  "stac_sha256_each_page":"","source_host":urlparse(STAC).netloc,
                  "catalog_status":"source_error",
                  "error":str(exc)[:220]}
                features[(site,year)]=[]
    catalog_rows=[catalogs[z] for z in actual_siteyears]
    write_table(OUT/"original_landsat_catalog_50_siteyears.csv",catalog_rows)
    print("ORIGINAL_LANDSAT_STAC_FAILURE_DETAILS="+json.dumps([{"site":r["site_id"],"year":r["survey_season"],"error":r.get("error","")} for r in catalog_rows if r["catalog_status"]!="ok"][:6]),flush=True)

    scene_rows=[];sample_rows=[]
    for k,(site,year) in enumerate(actual_siteyears,1):
        selected=features[(site,year)]
        for entry in selected:
            common={
              "site_id":site,"survey_season":year,
              "original_item_id":entry["item_id"],
              "original_scene_date":entry["day"],
              "scene_cloud_pct":entry["cloud_pct"],
              "source_item_json_sha256":entry["source_json_sha"],
              "raster_band_sources_json":json.dumps(selected_source(entry),sort_keys=True),
              "qa_good_fixed_points":0,
              "qa_total_fixed_points":77,
              "qa_reasons_json":"{}",
              "retrieval_status":"source_error",
              "error":""}
            try:
                sampled,reasons,urlmap=sample_spectral(site,year,centers[site],entry)
                sample_rows.extend(sampled)
                common["qa_good_fixed_points"]=reasons.get("qa_clear_land_non_snow",0)
                common["qa_reasons_json"]=json.dumps(reasons,sort_keys=True)
                common["retrieval_status"]="ok"
            except Exception as exc:
                common["error"]=type(exc).__name__+": "+str(exc)[:180]
            scene_rows.append(common)
        print(f"ORIGINAL_LANDSAT_SOURCE_PROGRESS={k}/{len(actual_siteyears)} "+
              f"site={site} year={year} selected={len(selected)} "+
              f"read_ok={sum(z['retrieval_status']=='ok' for z in scene_rows if z['site_id']==site and z['survey_season']==year)}",flush=True)
    write_table(OUT/"original_L8_scene_QA_receipts.csv",scene_rows,expected=[
       "site_id","survey_season","original_item_id","original_scene_date",
       "scene_cloud_pct","source_item_json_sha256","raster_band_sources_json",
       "qa_good_fixed_points","qa_total_fixed_points","qa_reasons_json","retrieval_status","error"])
    write_table(OUT/"original_geo_point_scene_NDVI_quality.csv",sample_rows,expected=[
       "site_id","survey_season","original_item_id","original_scene_date",
       "original_scene_cloud_pct","point_id","dx_EPSG3031_m","dy_EPSG3031_m",
       "qa_status","ndvi","SR_red","SR_nir","source_qa_pixel_raw","source_qa_radsat_raw",
       "source_item_json_sha256","original_raster_resolution_m",
       "original_raster_crs","is_validated_botanical_vegetation"])

    by_key=defaultdict(lambda:defaultdict(list))
    for row in sample_rows:
        if row["qa_status"]!="qa_clear_land_non_snow":continue
        key=(row["site_id"],int(row["survey_season"]),int(row["point_id"]))
        by_key[key][row["original_scene_date"]].append(float(row["ndvi"]))
    from statistics import median
    sitepoints=[]
    for (site,year,pt),scene_dates in sorted(by_key.items()):
        if any(len(v)!=1 for v in scene_dates.values()):
            raise ValueError("Expected one qa-blind scene per original day")
        val=median(list(scene_dates.values()))
        sitepoints.append({
          "site_id":site,"survey_season":year,"point_id":pt,
          "n_distinct_qa_valid_original_scene_dates":len(scene_dates),
          "median_original_QA_clear_spectral_NDVI":val,
          "matched_observed_site_year_not_background":True,
          "is_verified_botanical_greening":False})
    write_table(OUT/"siteyear_QA_clear_geo_points.csv",sitepoints,expected=[
      "site_id","survey_season","point_id",
      "n_distinct_qa_valid_original_scene_dates",
      "median_original_QA_clear_spectral_NDVI",
      "matched_observed_site_year_not_background","is_verified_botanical_greening"])

    by_sy=defaultdict(dict)
    for z in sitepoints:by_sy[z["site_id"],int(z["survey_season"])][int(z["point_id"])]=z
    pairs=[]
    valid_counts={}
    for site,year in actual_siteyears:
        valid_counts[(site,year)]=sum(int(z["n_distinct_qa_valid_original_scene_dates"])>=2
                        for z in by_sy.get((site,year),{}).values())
    from itertools import combinations
    for site in sorted(sites):
        years=sorted({y for s,y in actual_siteyears if s==site})
        for ya,yb in combinations(years,2):
            aa=by_sy.get((site,ya),{})
            bb=by_sy.get((site,yb),{})
            common=sorted(set(aa)&set(bb))
            eligible=[pt for pt in common if
                     int(aa[pt]["n_distinct_qa_valid_original_scene_dates"])>=2 and
                     int(bb[pt]["n_distinct_qa_valid_original_scene_dates"])>=2]
            delta=[float(bb[pt]["median_original_QA_clear_spectral_NDVI"])-
                   float(aa[pt]["median_original_QA_clear_spectral_NDVI"])
                   for pt in eligible]
            pairs.append({
              "site_id":site,"first_actual_census_season":ya,
              "later_actual_census_season":yb,
              "n_fixed_points_QA_clear_at_least_one_date_both":len(common),
              "n_fixed_points_with_2_distinct_QA_clear_dates_in_each_season":len(eligible),
              "source_support_gate":"READY_SPECTRAL_PAIR_NOT_VEGETATION" if len(eligible)>=6 else "INSUFFICIENT_SAME_LOCATION_CLEAR_DATES",
              "median_spectral_NDVI_difference_only":median(delta) if len(eligible)>=6 else "",
              "not_a_botanical_greenery_growth_estimate":True
            })
    write_table(OUT/"source_fixed_same_position_siteyear_spectral_pairs.csv",pairs,expected=[
       "site_id","first_actual_census_season","later_actual_census_season",
       "n_fixed_points_QA_clear_at_least_one_date_both",
       "n_fixed_points_with_2_distinct_QA_clear_dates_in_each_season",
       "source_support_gate","median_spectral_NDVI_difference_only",
       "not_a_botanical_greenery_growth_estimate"])
    ready=[r for r in pairs if r["source_support_gate"]=="READY_SPECTRAL_PAIR_NOT_VEGETATION"]
    catalog_errors=sum(r["catalog_status"]!="ok" for r in catalog_rows)
    original_scenes_ok=sum(r["retrieval_status"]=="ok" for r in scene_rows)
    failed=len(scene_rows)-original_scenes_ok
    source_error=catalog_errors>0 or (failed>0 and original_scenes_ok==0)
    # Source errors are reported explicitly; a status of no comparable pairs
    # is only final if zero failed catalog requests. Individual COG errors
    # still limit local power and must not be confused with no vegetation.
    status=("SOURCE_ERROR_INCOMPLETE" if source_error else
       "READY_SPECTRAL_PAIRS_NOT_BOTANICAL_VEGETATION" if ready else
       "NO_COMPARABLE_ANNUAL_SPECTRAL_PAIRS")
    summary={
      "status":status,
      "source_Landsat8_collection":COLLECTION,
      "original_scene_source_api":STAC,
      "source_scenes_selected_by":"scene_cloud_then_date_then_id, top 3 distinct dates, no local NDVI inspection",
      "n_original_census_survey_siteyears_requested":len(actual_siteyears),
      "n_original_sites":len(sites),
      "n_original_paired_observed_species_census_rows":len(matched),
      "n_catalog_siteyear_errors":catalog_errors,
      "n_siteyears_with_original_catalog_Landsat8_scene":sum(r["suitable_Landsat8_with_all_assets"]>0 for r in catalog_rows),
      "n_siteyears_with_3_qa_blind_scene_dates":sum(r["selected_qa_blind_scene_days"]>=3 for r in catalog_rows),
      "n_original_scenes_selected":len(scene_rows),
      "n_original_scene_raster_reads_ok":original_scenes_ok,
      "n_original_scene_raster_reads_failed":failed,
      "n_original_source_scene_pixel_QA_accepted":len(sample_rows),
      "n_original_qa_clear_spectral_observations":sum(r["qa_status"]=="qa_clear_land_non_snow" for r in sample_rows),
      "n_siteyear_fixed_points_QA_clear_on_at_least_2_dates":sum(valid_counts.values()),
      "n_potential_actual_census_siteyear_pairs":len(pairs),
      "n_actual_siteyear_pairs_with_fixed_point_2dates_each_year_6points":len(ready),
      "n_sites_with_2year_paired_original_spectral_NDVI":len({r["site_id"] for r in ready}),
      "original_qa_bits_rejected":list(BAD_QA_BITS),
      "fixed_grid_crs":"EPSG:3031 77 source-independent locations within 2000m of source site",
      "time_window":"Austral summer Dec of breeding season Y through Feb 28 of Y+1",
      "source_scope_notes":[
          "QA-clear Landsat spectral NDVI is not a verified botanical plant index. Do not call a positive difference greening.",
          "December-February scenes may be after original penguin count or the count month may be missing.",
          "Regional/local snow, exposed rock, algal stains, guano, water/cloud and phenology can confound vegetation inference.",
          "Only originally surveyed colonies; no false absence, no independent all-Antarctic SDM future prediction",
          "Cloud ranking independent of local vegetation response; a missing scene or COG failure is not zero green habitat",
          "Reuse the same EPSG:3031 physical grid points, but native Landsat pixels may shift across image grids",
          "More Landsat/STAC years are not independent botanical/individual penguin replication"
      ]
    }
    (OUT/"original_L8_annual_spectral_support.json").write_text(
       json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("ORIGINAL_LANDSAT_2017_2020_SUPPORT_GATE="+json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
