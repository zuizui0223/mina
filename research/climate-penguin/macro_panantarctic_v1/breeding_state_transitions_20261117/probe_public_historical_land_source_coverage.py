#!/usr/bin/env python3
"""Probe actual public multi-temporal Antarctic coastal land-cover source coverage.

One pass, outcome-blind for candidate Gentoo sites: probe three independent
geographic *clusters*, source-year-centred summer scenes, and GLIMS WFS layer
support. Retrieve only STAC scene metadata and GLIMS layer capabilities;
NEVER classify "no observation" as snow/ice, rock, colony nonoccupation,
or infer a colony founding date. No spectral change or climate effect tested.
"""
from __future__ import annotations
import argparse,collections,csv,datetime as dt,hashlib,json,math,time,urllib.error,urllib.parse,urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# Each grouping is from exact original MAPPPD site coordinates,
# grouped at 10 km in the previous original-source GIS audit.
CLUSTERS={
  "BISC_Biscoe_Point":{"lon":-63.7775,"lat":-64.8114,"codes":["BISC"],"years":[1985,1992,1994,1998,2006,2016]},
  "ORNE_Orne_Islands":{"lon":-62.673,"lat":-64.662,"codes":["ORNE"],"years":[1987,1997,1998,1999,2003,2016]},
  "Galindez_Vernadsky_Tuxen":{"lon":-64.2399,"lat":-65.2476,"codes":["GALE","TXRX","VERN"],"years":[1987,1998,1999,2003,2006,2007,2016]},
}
PC_ENDPOINT="https://planetarycomputer.microsoft.com/api/stac/v1/search"
GLIMS_ENDPOINT="https://www.glims.org/geoserver/ows"
USER_AGENT="mina-original-coastal-land-support-20261117/0.1 (research metadata audit)"

def req_json(endpoint,payload,timeout=40):
    body=json.dumps(payload,separators=(",",":")).encode()
    r=urllib.request.Request(endpoint,data=body,method="POST",
        headers={"Content-Type":"application/json","Accept":"application/geo+json",
                 "User-Agent":USER_AGENT})
    with urllib.request.urlopen(r,timeout=timeout) as f:
        raw=f.read(3_000_000)
        return json.loads(raw)

def categories(scene):
    props=scene.get("properties") or {}
    return {
      "date":str(props.get("datetime",""))[:10],
      "collection_category":str(props.get("landsat:collection_category","UNKNOWN")),
      "cloud_scene_percent":props.get("eo:cloud_cover"),
      "platform":str(props.get("platform","UNKNOWN")),
      "processing_level":str(props.get("processing:level",props.get("landsat:processing_level","UNKNOWN"))),
      "has_QA_PIXEL":("qa_pixel" in (scene.get("assets") or {})),
      "id":str(scene.get("id","")),
    }

def query_annual(cluster,year):
    # December is omitted to avoid mixing the START year of Antarctic
    # breeding seasons. Jan-Mar is not called a census event period.
    lat,lon=cluster["lat"],cluster["lon"]
    bbox=[lon-.035,lat-.025,lon+.035,lat+.025]
    q={
      "collections":["landsat-c2-l2"],
      "bbox":bbox,
      "datetime":f"{year}-01-01T00:00:00Z/{year}-03-31T23:59:59Z",
      "limit":100
    }
    data=req_json(PC_ENDPOINT,q)
    scenes=[categories(f) for f in data.get("features",[])]
    # Force an explicit missing-status warning if response exceeds 100
    # or advertises more pages. Never call counts complete if truncated.
    nxt=[v for v in (data.get("links") or []) if v.get("rel")=="next"]
    meta={
      "source":"Microsoft Planetary Computer STAC / landsat-c2-l2",
      "year":year,
      "query_bbox":bbox,
      "n_scene_records_first_page":len(scenes),
      "more_results_unqueried":bool(nxt),
      "n_qa_pixel_asset":sum(x["has_QA_PIXEL"] for x in scenes),
      "n_tier1":sum(x["collection_category"]=="T1" for x in scenes),
      "n_tier2":sum(x["collection_category"]=="T2" for x in scenes),
      "sensors":dict(collections.Counter(x["platform"] for x in scenes)),
      "n_scene_cloud_below25pct":sum(
          isinstance(x["cloud_scene_percent"],(int,float)) and
          x["cloud_scene_percent"]<25 for x in scenes),
      "scene_coverage_not_site_clear_surface":True
    }
    return meta,scenes

def glims_capabilities():
    param={"service":"WFS","version":"2.0.0","request":"GetCapabilities"}
    url=GLIMS_ENDPOINT+"?"+urllib.parse.urlencode(param)
    try:
        r=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
        with urllib.request.urlopen(r,timeout=35) as f:
            content=f.read(2_500_000)
            mime=f.headers.get("Content-Type","")
        root=ET.fromstring(content)
        names=[(x.text or "") for x in root.iter()
               if x.tag.endswith("}Name") and x.text]
        # Restrict to first 150 layer/operation names in publication output
        return {"url":url,"status":"HTTP_XML_OK","content_type":mime,
                "xml_bytes_loaded":len(content),"names_preview":names[:150],
                "wfs_glacier_names":[n for n in names if "glac" in n.lower()][:50],
                "this_is_only_capabilities_not_multitemporal_glacier_geometry":True}
    except Exception as e:
        return {"url":url,"status":"INACCESSIBLE_OR_PARSE_ERROR",
                "error":f"{type(e).__name__}: {str(e)[:180]}",
                "not_an_evidence_of_glacier_absence":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    searches=[];scene_sources=[];errors=[]
    for name,cl in CLUSTERS.items():
        for y in cl["years"]:
            try:
                m,scenes=query_annual(cl,y)
                m["cluster_id"]=name
                m["original_source_site_codes"]=";".join(cl["codes"])
                searches.append(m)
                for s in scenes:
                    scene_sources.append({"cluster_id":name,"probe_year":y,**s})
            except Exception as e:
                errors.append({"cluster_id":name,"year":y,
                               "error_type":type(e).__name__,
                               "error":str(e)[:240]})
    glims=glims_capabilities()
    rows=sorted(searches,key=lambda x:(x["cluster_id"],x["year"]))
    columns=[
      "cluster_id","original_source_site_codes","year","n_scene_records_first_page",
      "more_results_unqueried","n_qa_pixel_asset","n_tier1","n_tier2",
      "n_scene_cloud_below25pct","sensors","source","scene_coverage_not_site_clear_surface",
      "query_bbox"
    ]
    with (a.out/"landsat_climate_event_summer_scene_availability.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
        for r in rows:
            w.writerow({k:json.dumps(r.get(k),ensure_ascii=False) if k in ("sensors","query_bbox") else r.get(k)
                        for k in columns})
    with (a.out/"original_landsat_scene_identifiers_and_scene_QA_metadata.csv").open("w",newline="") as f:
        columns2=["cluster_id","probe_year","id","date","platform","collection_category",
                  "processing_level","cloud_scene_percent","has_QA_PIXEL"]
        w=csv.DictWriter(f,fieldnames=columns2);w.writeheader()
        w.writerows([{k:x.get(k) for k in columns2} for x in scene_sources])
    v={
      "status":"PUBLIC_ORIGINAL_HISTORIC_GROUND_SURFACE_SOURCE_PROBE_ONLY",
      "n_original_gentoo_site_codes":5,
      "n_spatial_clusters_at_10km":3,
      "n_landsat_searches_requested":sum(len(x["years"]) for x in CLUSTERS.values()),
      "n_landsat_searches_successful":len(searches),
      "n_landsat_search_errors":len(errors),
      "n_landsat_catalog_scene_rows_first_page":len(scene_sources),
      "n_summer_cluster_years_with_some_scenes":sum(z["n_scene_records_first_page"]>0 for z in searches),
      "n_cluster_years_with_at_least_one_tier1_scene":sum(z["n_tier1"]>0 for z in searches),
      "n_cluster_years_with_at_least_one_scene_cloud_below25pct":sum(z["n_scene_cloud_below25pct"]>0 for z in searches),
      "n_cluster_years_with_truncated_scene_list":sum(z["more_results_unqueried"] for z in searches),
      "scene_catalog_coverage_cannot_prove_land_pixel_quality":True,
      "no_glacier_retreat_area_or_bare_rock_change_calculated":True,
      "not_an_independent_breeding_site_nonoccupied_comparator":True,
      "not_dated_colonization_or_breeding_site_area":True,
      "metadata_sources":{
        "planetary_computer_STAC_collection":"https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2",
        "glims_WFS":GLIMS_ENDPOINT,
        "historical_glacier_front_data":"https://doi.org/10.5285/07727663-9B94-4069-A486-67E4D82177D3",
      },
      "glims_WFS":glims,
      "search_errors":errors,
      "per_cluster_year":rows
    }
    (a.out/"land_source_metadata_coverage_receipt.json").write_text(
        json.dumps(v,ensure_ascii=False,indent=2)+"\n")
    print("ORIGINAL_DYNAMIC_LAND_SCENE_SUPPORT="+json.dumps(
      {"status":v["status"],"successful":len(searches),"requested":v["n_landsat_searches_requested"],
       "errors":len(errors),"scene_rows":len(scene_sources),
       "with_scenes":v["n_summer_cluster_years_with_some_scenes"],
       "tier1":v["n_cluster_years_with_at_least_one_tier1_scene"],
       "GLIMS":glims["status"],
       "details":[{"id":z["cluster_id"],"year":z["year"],
                  "n":z["n_scene_records_first_page"],
                  "t1":z["n_tier1"],"t2":z["n_tier2"],
                  "qa_asset":z["n_qa_pixel_asset"]} for z in rows]},
       ensure_ascii=False),flush=True)

if __name__=="__main__":main()
