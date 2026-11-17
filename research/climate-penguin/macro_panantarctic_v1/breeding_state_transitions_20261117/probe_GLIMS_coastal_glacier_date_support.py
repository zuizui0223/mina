#!/usr/bin/env python3
"""Probe GLIMS WFS for *dated multi-temporal glacier geometries* near source
Gentoo colonies. The probe checks whether source observations of ice extent
actually straddle the zero->positive nest observation interval.

GLIMS polygon overlap with a wide coastal buffer does not prove the local
nest substrate or access was ice covered. Merely obtaining a glacier outline
never establishes new rock area; that requires validated historical glacier
outlines of the SAME named glacier, source dates, topology, and land mask.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
BASE="https://www.glims.org/geoserver/ows"
PLACES={
    "BISC":{"lat":-64.8114,"lon":-63.7775,"zero":1984,"positive":1994},
    "ORNE":{"lat":-64.662,"lon":-62.673,"zero":1998,"positive":1999},
    "GALINDEZ":{"lat":-65.2476,"lon":-64.2399,"zero":1999,"positive":2007},
}
def req(params,limit=5_000_000):
    url=BASE+"?"+urllib.parse.urlencode(params)
    r=urllib.request.Request(url,headers={"User-Agent":"mina-deglaciation-source-probe/20261117"})
    with urllib.request.urlopen(r,timeout=30) as f:
        b=f.read(limit)
        mime=f.headers.get("Content-Type","")
    return url,b,mime

def list_layers():
    url,content,mime=req({"service":"WFS","version":"2.0.0","request":"GetCapabilities"})
    root=ET.fromstring(content)
    found=[]
    for el in root.iter():
        if not el.tag.endswith("}FeatureType"):continue
        row={}
        for child in el:
            if child.tag.endswith("}Name"):row["name"]=child.text or ""
            if child.tag.endswith("}Title"):row["title"]=child.text or ""
        if row.get("name"):found.append(row)
    layers=[x for x in found if "glac" in (x["name"]+" "+x.get("title","")).lower()]
    ranked=sorted(layers,key=lambda x:(
        0 if "glims" in x["name"].lower() else 1,
        0 if "outline" in (x["name"]+" "+x.get("title","")).lower() else 1,
        x["name"]))
    return {"source_url":url,"n_features_advertised":len(found),
            "n_glacier_feature_types":len(layers),
            "glacier_types":ranked[:50],"all_types_preview":found[:35],
            "requested_layer":ranked[0]["name"] if ranked else None}

def probe(place,layer):
    # WFS 1.0.0 uses long/lat order for EPSG:4326.
    # Coarse 0.12 x 0.12 bounding, NOT actual accessible land.
    lat,lon=place["lat"],place["lon"]
    bbox=f"{lon-.09},{lat-.08},{lon+.09},{lat+.08},EPSG:4326"
    q={"service":"WFS","version":"1.0.0","request":"GetFeature",
       "typeName":layer,"outputFormat":"application/json",
       "bbox":bbox,"maxFeatures":80}
    url,raw,mime=req(q,10_000_000)
    result=json.loads(raw)
    if result.get("type")!="FeatureCollection":
        raise ValueError("WFS not valid GeoJSON feature collection")
    fs=result.get("features",[])
    rows=[]
    for z in fs:
        p=z.get("properties") or {}
        candidates=[(k,v) for k,v in p.items()
                    if any(t in k.lower() for t in ("date","time","year","analysis","glacier","source","glac","area","ref"))]
        rows.append({"id":z.get("id"),"properties":dict(candidates[:28]),
                     "geometry_type":(z.get("geometry") or {}).get("type")})
    return {"query_url":url,"requested_source_bbox":bbox,"mime":mime,"n_returned_features":len(fs),
            "possibly_truncated_at80":len(fs)>=80,"glacier_attribute_records":rows,
            "geometry_downloaded_but_not_area_differenced":True,
            "source_ice_to_land_transition_not_measured":True}

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    try:
        layer=list_layers();err=None
    except Exception as e:
        layer={"requested_layer":None,"n_features_advertised":None}
        err={"kind":"CAPABILITIES","error":f"{type(e).__name__}: {str(e)[:300]}"}
    probes={};errors=[err] if err else []
    if layer["requested_layer"]:
        for name,v in PLACES.items():
            try:probes[name]=probe(v,layer["requested_layer"])
            except Exception as e:
                errors.append({"kind":"GET_FEATURE","place":name,
                               "error":f"{type(e).__name__}: {str(e)[:300]}"})
    summary={
      "status":"GLIMS_DATED_GLACIER_SOURCE_SUPPORT_AUDIT_NOT_ROCK_CHANGE",
      "source_WFS":BASE,
      "n_target_original_site_clusters":len(PLACES),
      "capabilities":layer,
      "n_successful_target_bbox_queries":len(probes),
      "target_bbox_results":probes,
      "errors":errors,
      "no_glacier_area_change_computed":True,
      "no_yearly_icefree_rock_time_series_confirmed":True,
      "source_date_is_not_colony_founding_date":True,
      "no_islandization_connectivity_time_series":True
    }
    (out/"glims_original_multitemporal_glacier_source_receipt.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print("GLIMS_HISTORIC_SOURCE="+json.dumps(
      {"status":summary["status"],"layers":layer.get("n_features_advertised"),
       "glacier_types":layer.get("n_glacier_feature_types"),
       "chosen_layer":layer.get("requested_layer"),"success_bboxes":len(probes),
       "counts":{k:v["n_returned_features"] for k,v in probes.items()},
       "errors":errors},ensure_ascii=False),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    v=p.parse_args()
    run(v.out)
