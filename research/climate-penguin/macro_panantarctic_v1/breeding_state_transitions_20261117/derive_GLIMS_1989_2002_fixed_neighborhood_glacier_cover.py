#!/usr/bin/env python3
"""Source-pinned GLIMS 1989/2002 ice-polygon support near genuine Gentoo
census 0->positive sites; calculate local geometric change in fixed circles.

Only glacier IDs independently mapped in BOTH epochs count. This is *partial*
glacier-polygon-area change, NOT new accessible bare rock, new terrestrial
land, colony habitat, annual deglaciation, or causality of the nest event.
Glacier disappearance into water remains possible. 2002-12-31 source date
could be a year-end archive convention, not an image capture date.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

BASE="https://www.glims.org/geoserver/ows"
LAYER="GLIMS:GLIMS_Glacier_Outlines"
YEARS=("1989","2002")
LOC={
 "BISC":{"lat":-64.8114,"lon":-63.7775,"zero":1984,"positive":1994,"status":"post GLIMS epoch lies AFTER first positive count"},
 "ORNE":{"lat":-64.662,"lon":-62.673,"zero":1998,"positive":1999,"status":"GLIMS dated epochs 1989 and 2002 bracket both censuses"},
 "GALINDEZ":{"lat":-65.2476,"lon":-64.2399,"zero":1999,"positive":2007,"status":"GLIMS local IDs have incompatible source years 1957 vs 1989"},
}
BUFFERS_KM=(2,5)
def raw_features(place):
    param={"service":"WFS","version":"1.0.0","request":"GetFeature",
          "typeName":LAYER,"outputFormat":"application/json",
          "bbox":f"{place['lon']-.09},{place['lat']-.08},{place['lon']+.09},{place['lat']+.08},EPSG:4326",
          "maxFeatures":80}
    url=BASE+"?"+urllib.parse.urlencode(param)
    req=urllib.request.Request(url,headers={"User-Agent":"mina-glims-fixed-source-area-20261117"})
    with urllib.request.urlopen(req,timeout=35) as f:data=json.loads(f.read(12_000_000))
    assert data["type"]=="FeatureCollection"
    feats=data.get("features",[])
    assert len(feats)<80
    return feats,url
def glacier_contributions(feats):
    from shapely.geometry import shape
    from shapely.ops import transform,unary_union
    from pyproj import Transformer
    proj=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    by=defaultdict(list);dates=defaultdict(set)
    for z in feats:
        p=z.get("properties") or {}
        gid=p.get("glac_id");year=str(p.get("src_date",""))[:4]
        if not gid or year not in YEARS:continue
        geo=shape(z["geometry"])
        if not geo.is_valid:geo=geo.buffer(0)
        assert geo.is_valid
        geom=transform(proj.transform,geo)
        assert geom.area>=0
        by[gid,year].append(geom)
        dates[gid].add(year)
    paired=sorted(k for k in dates if set(YEARS).issubset(dates[k]))
    return by,paired,dates

def calculate(place,features):
    from shapely.geometry import Point
    from shapely.ops import unary_union
    from pyproj import Transformer
    tr=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    x,y=tr.transform(place["lon"],place["lat"])
    by,paired,all_dates=glacier_contributions(features)
    rows=[]
    for km in BUFFERS_KM:
        ball=Point(x,y).buffer(1000*km,resolution=96)
        clipped={}
        for year in YEARS:
            g=[]
            for gid in paired:
                # GLIMS can contain multiple parts of SAME mapped glacier
                for geom in by[gid,year]:
                    if geom.intersects(ball):
                        g.append(geom.intersection(ball))
            clipped[year]=unary_union(g) if g else ball.intersection(Point(-1e9,-1e9).buffer(1))
        old,new=clipped["1989"],clipped["2002"]
        lost=old.difference(new).area/1e6
        gained=new.difference(old).area/1e6
        a0=old.area/1e6;a1=new.area/1e6
        assert abs((a0-a1)-(lost-gained))<1e-6
        rows.append({
          "source_colony_cluster":place["cluster"],
          "fixed_buffer_radius_km":km,
          "source_glacier_id_matched_1989_2002":len(paired),
          "matched_glacier_source_ids":";".join(paired),
          "source_BBOX_glacier_ids_union":len(all_dates),
          "glacier_ice_polygon_cover_1989_km2":a0,
          "glacier_ice_polygon_cover_2002_km2":a1,
          "geometric_polygon_loss_1989_not2002_km2":lost,
          "geometric_polygon_gain_2002_not1989_km2":gained,
          "net_loss_km2":a0-a1,
          "unpaired_glacier_ids_excluded":len(all_dates)-len(paired),
          "fixed_buffer_area_km2":ball.area/1e6,
          "not_new_bare_rock_area":True,
          "source_endpoint_after_nest_count_possible":place["status"],
          "date_2002_12_31_may_be_archive_year_marker":True
        })
    return rows,paired,all_dates

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    rows=[];queries=[];errors=[]
    for name,v in LOC.items():
        q={**v,"cluster":name}
        try:
            fs,url=raw_features(v)
            rr,paired,alldates=calculate(q,fs)
            rows.extend(rr)
            queries.append({"cluster":name,"WFS_query_url":url,"n_raw_source_features":len(fs),
                            "n_unique_source_glacier_ids":len(alldates),
                            "n_multitemporal_same_ID_1989_and_2002":len(paired),
                            "same_id_source_glaciers":paired})
        except Exception as e:
            errors.append({"cluster":name,"status":"FAILED_SOURCE_GEOMETRY",
                           "error":f"{type(e).__name__}: {str(e)[:300]}"})
    cols=list(rows[0]) if rows else ["source_colony_cluster"]
    with (a.out/"original_GLIMS_same_glacier_1989_2002_fixed_buffer_physical.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
    result={
       "status":"GLIMS_HISTORIC_TWO_EPOCH_SAME_GLACIER_ID_LOCAL_GEOMETRY_GATE",
       "glims_layer":LAYER,
       "source_1989":"1989-11-26 source observation date as recorded",
       "source_2002":"2002-12-31 source date (may be year-end archive marker)",
       "n_target_source_clusters":len(LOC),
       "n_retrieved_clipped_distance_rows":len(rows),
       "source_cluster_queries":queries,
       "source_query_errors":errors,
       "source_ice_change_not_new_land_area":True,
       "rock_land_use_and_ice_ramp_connectivity_not_measured":True,
       "not_a_joint_site_year_colonization_model":True,
       "not_a_causal_claim_or_future_nest_forecast":True,
       "results":rows
    }
    (a.out/"GLIMS_local_original_1989_2002_glacier_geometry_receipt.json").write_text(
         json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("GLIMS_LOCAL_GEOMETRY="+json.dumps(
      {"status":result["status"],"queries":queries,"errors":errors,
       "results":rows},ensure_ascii=False),flush=True)

if __name__=="__main__":main()
