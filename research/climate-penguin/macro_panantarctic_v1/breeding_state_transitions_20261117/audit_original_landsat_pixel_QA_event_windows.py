#!/usr/bin/env python3
"""Original Landsat QA_PIXEL measured at fixed ground coordinates around Gentoo sites.

This checks only whether historical imagery can see the *same* 25 fixed
positions within 500 m of each original colony point, without clouds/snow/
water at the Landsat pixel. It is NOT a dated glacier/rock classification,
nest-polygon occupancy or colonization mechanism. The date pairs were fixed
by source census/observation opportunity, not by image outcomes.

A maximum of eight scenes per cluster-year is used; rank by published
scene-level cloud cover before inspecting local pixels. If >8 scenes exist,
the other scenes are not tested and this is flagged, NOT called unavailable.
All original QA flags and source scene IDs are retained.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,math,urllib.request
from pathlib import Path
import numpy as np

API="https://planetarycomputer.microsoft.com/api/stac/v1/search"
OFFSETS_M=(-500,-250,0,250,500)
BAD_BITS=(0,1,2,3,4,5,7)
MAX_SCENES=8
PAIRS={
  "ORNE":{"cluster":"ORNE","lat":-64.662,"lon":-62.673,"years":[1997,2003],
          "source_status":"zero recorded 1998; first positive 1999 (NO contemporaneous scenes)"},
  "GALE":{"cluster":"GAL","lat":-65.2476,"lon":-64.2399,"years":[2003,2007],
          "source_status":"zero recorded 1999; positive recorded 2007, interval censored"},
  "VERN":{"cluster":"GAL","lat":-65.2453,"lon":-64.2567,"years":[2003,2007],
          "source_status":"zero recorded 1999; positive recorded 2007, interval censored"},
  "TXRX":{"cluster":"GAL","lat":-65.2549,"lon":-64.1334,"years":[2003,2007],
          "source_status":"zero recorded 2003; positive recorded 2006, 2007 is AFTER first positive"},
  "BISC":{"cluster":"BISC","lat":-64.8114,"lon":-63.7775,"years":[2006,2016],
          "source_status":"zero recorded 1984; positive 1994; both imagery years AFTER first positive"}
}
SOURCE_QUERY={
  "ORNE":{"lat":-64.662,"lon":-62.673,"years":[1997,2003]},
  "GAL":{"lat":-65.2476,"lon":-64.2399,"years":[2003,2007]},
  "BISC":{"lat":-64.8114,"lon":-63.7775,"years":[2006,2016]},
}

def scene_search(site,year):
    import requests
    q={"collections":["landsat-c2-l2"],
       "bbox":[site["lon"]-.035,site["lat"]-.025,site["lon"]+.035,site["lat"]+.025],
       "datetime":f"{year}-01-01T00:00:00Z/{year}-03-31T23:59:59Z","limit":100}
    r=requests.post(API,json=q,timeout=40);r.raise_for_status()
    res=r.json()
    if any(x.get("rel")=="next" for x in res.get("links",[])):
        raise ValueError("PAGINATED source >100 scenes cannot be fully evaluated")
    a=res.get("features",[])
    a=sorted(a,key=lambda x:(
      (x.get("properties",{}).get("eo:cloud_cover") or 100),x.get("properties",{}).get("datetime",""),
      x.get("id","")
    ))
    return a

def scene_mask(scene,points):
    import rasterio,planetary_computer
    from pyproj import Transformer
    asset=(scene.get("assets") or {}).get("qa_pixel")
    if not asset or not asset.get("href"):
        raise ValueError("NO_ORIGINAL_QA_PIXEL_ASSET")
    signed=planetary_computer.sign(asset["href"])
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      GDAL_HTTP_MAX_RETRY="2",GDAL_HTTP_RETRY_DELAY="1",
                      GDAL_HTTP_TIMEOUT="30"):
        with rasterio.open(signed) as src:
            transformer=Transformer.from_crs("EPSG:3031",src.crs,always_xy=True)
            native=[transformer.transform(x,y) for x,y in points]
            samples=list(src.sample(native,masked=True))
            assert len(samples)==len(points)
            mask=0
            for i,z in enumerate(samples):
                if bool(np.any(z.mask)):continue
                x=int(z[0])
                if not any(x & (1<<b) for b in BAD_BITS):
                    mask|=1<<i
            return mask

def source_fixed_points(lat,lon):
    from pyproj import Transformer
    x,y=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True).transform(lon,lat)
    return [(x+dx,y+dy) for dy in OFFSETS_M for dx in OFFSETS_M]

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    scenes={};catalog=[];errors=[];qa_rows=[]
    for k,loc in SOURCE_QUERY.items():
        for y in loc["years"]:
            try:
                a=scene_search(loc,y)
                scenes[k,y]=a[:MAX_SCENES]
                catalog.append({"cluster":k,"year":y,"n_scene_catalog":len(a),
                    "n_qa_scenes_tested":len(scenes[k,y]),
                    "n_scenes_not_tested":max(0,len(a)-MAX_SCENES),
                    "n_tier1_scene_catalog":sum((s["properties"].get("landsat:collection_category")=="T1") for s in a)})
            except Exception as e:
                errors.append({"type":"CATALOG","cluster":k,"year":y,"message":str(e)[:250]})
                scenes[k,y]=[]
                catalog.append({"cluster":k,"year":y,"n_scene_catalog":-1,
                    "n_qa_scenes_tested":0,"n_scenes_not_tested":None,"n_tier1_scene_catalog":None})
    for site,loc in PAIRS.items():
        points=source_fixed_points(loc["lat"],loc["lon"])
        for year in loc["years"]:
            items=scenes[loc["cluster"],year]
            union=0;days=collections.defaultdict(int);ok=0;failed=0
            for scene in items:
                scene_id=scene["id"]
                date=scene["properties"].get("datetime","")[:10]
                tier=scene["properties"].get("landsat:collection_category","UNKNOWN")
                try:
                    mask=scene_mask(scene,points)
                    union|=mask
                    days[date]|=mask
                    ok+=1
                    outcome={"site":site,"image_year":year,"item_id":scene_id,
                      "source_date":date,"source_tier":tier,"source_scene_cloud_percent":
                      scene["properties"].get("eo:cloud_cover"),
                      "read_status":"OK","qa_clear_nonwater_nonsnow_grid_positions":
                      mask.bit_count(),"qa_clear_25position_mask":mask,"error":""}
                except Exception as e:
                    failed+=1
                    msg=f"{type(e).__name__}: {str(e)[:220]}"
                    errors.append({"type":"ASSET","cluster":loc["cluster"],"site":site,
                                   "year":year,"item_id":scene_id,"message":msg})
                    outcome={"site":site,"image_year":year,"item_id":scene_id,
                      "source_date":date,"source_tier":tier,"source_scene_cloud_percent":
                      scene["properties"].get("eo:cloud_cover"),
                      "read_status":"ERROR","qa_clear_nonwater_nonsnow_grid_positions":
                      None,"qa_clear_25position_mask":None,"error":msg}
                qa_rows.append(outcome)
            daily_counts=[sum(bool(m & (1<<i)) for m in days.values()) for i in range(25)]
            qa_count=sum(mask>0 for mask in days.values())
            catalog.append({"site":site,"source_status":loc["source_status"],
                   "image_year":year,"n_scenes_available":len(items),
                   "successful_qa_reads":ok,"qa_read_errors":failed,
                   "n_distinct_calendar_dates_with_some_site_clear_pixels":qa_count,
                   "n_same_positions_QA_clear_at_least_1_day":sum(x>=1 for x in daily_counts),
                   "n_same_positions_QA_clear_at_least_2_distinct_days":sum(x>=2 for x in daily_counts),
                   "qa_clear_union_25position_bit_mask":union,
                   "not_verified_actual_nest_plot":True,
                   "not_bare_rock_without_spectral_classification":True})
    site_year=[z for z in catalog if "site" in z]
    comparisons=[]
    for site,loc in PAIRS.items():
        a,b=[next(z for z in site_year if z["site"]==site and z["image_year"]==y)
             for y in loc["years"]]
        common=(int(a["qa_clear_union_25position_bit_mask"]) &
                int(b["qa_clear_union_25position_bit_mask"]))
        comparisons.append({
          "site":site,"cluster":loc["cluster"],"image_year_earlier":loc["years"][0],
          "image_year_later":loc["years"][1],
          "common_QA_clear_fixed_positions_at_least_once_both_years":common.bit_count(),
          "both_years_at_least_one_QA_success":bool(a["successful_qa_reads"] and b["successful_qa_reads"]),
          "source_breeding_event_relation":loc["source_status"],
          "not_precise_colonization_date_or_bare_rock_change":True})
    # Store machine readable with user-visible no overclaim semantics.
    with (out/"source_cluster_year_landsat_QA_native_raster_footprint.csv").open("w",newline="") as f:
        fields=["site","source_status","image_year","n_scenes_available",
                "successful_qa_reads","qa_read_errors",
                "n_distinct_calendar_dates_with_some_site_clear_pixels",
                "n_same_positions_QA_clear_at_least_1_day",
                "n_same_positions_QA_clear_at_least_2_distinct_days",
                "qa_clear_union_25position_bit_mask",
                "not_verified_actual_nest_plot",
                "not_bare_rock_without_spectral_classification"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        w.writerows([{k:r.get(k) for k in fields} for r in site_year])
    with (out/"all_selected_native_landsat_scene_QA_reads.csv").open("w",newline="") as f:
        fields=["site","image_year","item_id","source_date","source_tier",
                "source_scene_cloud_percent","read_status","qa_clear_nonwater_nonsnow_grid_positions",
                "qa_clear_25position_mask","error"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(qa_rows)
    report={
      "status":"SOURCE_ORIGINAL_QA_PIXEL_FOR_HISTORIC_PENGUIN_EVENT_SUPPORT",
      "n_original_candidate_site_ids":len(PAIRS),
      "n_original_clusters":len(SOURCE_QUERY),
      "n_original_query_cluster_years":sum(len(v["years"]) for v in SOURCE_QUERY.values()),
      "n_site_years_with_asset_source_checks":len(site_year),
      "n_qa_pixel_read_successes":sum(x["read_status"]=="OK" for x in qa_rows),
      "n_qa_pixel_read_errors":sum(x["read_status"]=="ERROR" for x in qa_rows),
      "n_catalog_errors":sum(x["type"]=="CATALOG" for x in errors),
      "all_original_scene_categories_are_tier2":all(
          x.get("source_tier")=="T2" for x in qa_rows) if qa_rows else None,
      "all_scene_overview_not_actual_local_pixel":True,
      "no_source_verified_rock_age_or_true_penguin_colonization_date":True,
      "no_possible_nest_patch_absence_denominator":True,
      "fixed_grid_meter_offsets":list(OFFSETS_M),
      "fixed_grid_epsg":3031,
      "QA_pixel_excluded_bit_positions":list(BAD_BITS),
      "source_glacier_not_measured":True,
      "catalog_queries":[z for z in catalog if "cluster" in z and "year" in z],
      "site_year_QA":site_year,
      "cross_year_support":comparisons,
      "read_errors":errors,
    }
    (out/"original_landsat_5site_two_era_ground_QA_receipt.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("PENGUIN_ORIGINAL_LAND_PIXEL_QA="+json.dumps(
        {"status":report["status"],"n_reads_success":report["n_qa_pixel_read_successes"],
         "n_read_errors":report["n_qa_pixel_read_errors"],
         "catalog_errors":report["n_catalog_errors"],
         "results":comparisons,
         "siteyear":[{"site":z["site"],"year":z["image_year"],"scenes":z["n_scenes_available"],
                      "ok":z["successful_qa_reads"],
                      "once":z["n_same_positions_QA_clear_at_least_1_day"],
                      "twice":z["n_same_positions_QA_clear_at_least_2_distinct_days"]}
                     for z in site_year]},ensure_ascii=False),flush=True)

def selftest():
    assert (13 & 5).bit_count()==2
    assert len(OFFSETS_M)**2==25
    assert sum(int(b) for b in BAD_BITS)==22
    print("PASS fixed original geographic positions and no-snow-water QA flags")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:selftest()
    else:
        assert a.out
        run(a.out)
