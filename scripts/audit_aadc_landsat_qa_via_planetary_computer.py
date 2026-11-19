#!/usr/bin/env python3
"""Read same two AADC Landsat QA scenes via anonymous Planetary Computer SAS.

Alternative transport ONLY. The scene IDs and original AADC site centroid
were selected prior to consulting actual local pixels. Tokens never logged,
cached in artifact, or committed. No biological/ice/rock effect fitting.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
from urllib.parse import quote,urlparse
import rasterio
import requests
from pyproj import Transformer
from shapely.geometry import shape,Point
from scripts.audit_aadc_landsat_local_qa_pilot import qa_flags

PC_STAC="https://planetarycomputer.microsoft.com/api/stac/v1"
PC_SAS="https://planetarycomputer.microsoft.com/api/sas/v1/sign"
COLLECTION="landsat-c2-l2"

def get_item(scene_id):
    url=PC_STAC+"/collections/"+COLLECTION+"/items/"+quote(scene_id,safe="")
    r=requests.get(url,timeout=(20,40),
                   headers={"User-Agent":"mina-source-only-landsat-qa-secondary/1.0"})
    r.raise_for_status()
    if len(r.content)>5_000_000:raise ValueError("PC STAC scene metadata >5MB")
    o=r.json()
    if o.get("id")!=scene_id or o.get("collection")!=COLLECTION:
        raise ValueError("PC item scene ID or collection changed")
    return o

def sign_validated_asset(asset_url):
    unsigned=urlparse(asset_url)
    if unsigned.scheme!="https" or not unsigned.hostname or not unsigned.hostname.endswith(".blob.core.windows.net"):
        raise ValueError("PC source asset must be an Azure Blob HTTPS URI")
    r=requests.get(PC_SAS,params={"href":asset_url},timeout=(15,40),
                   headers={"User-Agent":"mina-fixed-landsat-qa-source/1.0"})
    r.raise_for_status()
    # SAS URL contains short-lived signature: do not log/persist it.
    o=r.json()
    signed=o.get("href","")
    p=urlparse(signed)
    if p.scheme!="https" or p.hostname!=unsigned.hostname or p.path!=unsigned.path:
        raise ValueError("PC signed source host or path mismatch")
    if not p.query:raise ValueError("PC did not sign original source asset")
    return signed,p.hostname

def read_qa_chip(signed,lat,lon):
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="YES",GDAL_HTTP_TIMEOUT="25",
                      GDAL_HTTP_MAX_RETRY="1"):
      with rasterio.open(signed) as ds:
        if not ds.crs:raise ValueError("PC source QA has no CRS")
        x,y=Transformer.from_crs(4326,ds.crs,always_xy=True).transform(lon,lat)
        row,col=ds.index(x,y)
        if min(row,col)<10 or row+10>=ds.height or col+10>=ds.width:
            raise ValueError("Original AADC geographic centroid outside 21x21 source QA")
        chip=ds.read(1,window=rasterio.windows.Window(col-10,row-10,21,21))
        if chip.shape!=(21,21):raise ValueError("Not full 21x21 pixel QA window")
        return {"source_pixel_size_m":[float(abs(ds.res[0])),float(abs(ds.res[1]))],
                "source_qa_crs":str(ds.crs),
                "QA_pixel_at_AADC_geographic_centroid":int(chip[10,10]),
                "QA_21x21_counts":qa_flags(chip)}

def audit(original):
    rec=json.loads(original.read_text(encoding="utf-8"))
    if rec.get("source_site_id")!="IS_105" or rec.get("original_A_to_P")!=[2017,2018]:
        raise ValueError("Fixed original AADC QA pilot receipt changed")
    scenes=rec.get("source_seasons",{})
    if set(scenes)!={"reported_A_season","reported_P_season"}:
        raise ValueError("Original two Landsat source seasons not identified")
    report={
      "status":"PC_SAS_ORIGINAL_LANDSAT_QA_PIXEL_SOURCE_ONLY",
      "date_utc":datetime.now(timezone.utc).isoformat(),
      "source_original_earthsearch_full_run":44538120002,
      "source_original_s3_403_run":44539638611,
      "secondary_stac_provider":PC_STAC,
      "secondary_sas_authority":PC_SAS,
      "fixed_site_id":"IS_105","fixed_species":"ADP",
      "fixed_observed_A_to_P_seasons":[2017,2018],
      "original_site_is_exact_nest_patch":False,
      "a_new_rock_or_colonization_effect_fitted":False,
      "selected_scenes":{},
    }
    for key,v in sorted(scenes.items()):
        out={"original_EarthSearch_scene_id":v["scene_id"],
             "original_EarthSearch_acquired":v["acquired"],
             "source_scene_global_cloud":v["scene_global_cloud"],
             "previous_original_S3_status":v["status"]}
        try:
            item=get_item(v["scene_id"])
            lon,lat=(-0.0,0.0)
            # Original source point from frozen full STAC check (IS_105):
            lon,lat=39.253369,-69.037767
            if not shape(item["geometry"]).covers(Point(lon,lat)):
                raise ValueError("PC exact same scene footprint does not cover original AADC centroid")
            assets=item.get("assets") or {}
            qa=assets.get("qa_pixel") or assets.get("qa")
            if not qa or not qa.get("href"):
                raise ValueError("PC exact scene has no QA band asset")
            signed,host=sign_validated_asset(qa["href"])
            out["signed_asset_host"]=host  # never print/store signed href
            out.update(read_qa_chip(signed,lat,lon))
            out["status"]="SOURCE_QA_PIXELS_READ_FREE_PC"
        except Exception as e:
            out["status"]="HOLD_SECONDARY_QA_ASSET"
            out["error"]=f"{type(e).__name__}: {str(e)}"[:230]
        report["selected_scenes"][key]=out
    report["n_seasons_with_actual_QA_pixels"]=sum(
        v["status"]=="SOURCE_QA_PIXELS_READ_FREE_PC"
        for v in report["selected_scenes"].values())
    report["limitations"]=[
      "Provider transport changed to public PC SAS but same preselected original Landsat scene IDs and same original source geographic point.",
      "No SAS query strings, signed URLs, secret keys or credentials are persisted.",
      "QA valid != bare rock, QA snow != permanent glacier; reflectance bands and repeated summers not yet checked.",
      "AADC site coordinate is a geographic island/rock site centroid; exact nest patch association missing.",
      "Site-level reported A->P does not prove first occupation or ice-loss causation.",
    ]
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--previous-qa-source-json",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    try:r=audit(a.previous_qa_source_json)
    except Exception as e:
        r={"status":"HOLD_PC_LANDSAT_QA_PILOT",
           "error":f"{type(e).__name__}: {str(e)}"[:350],
           "new_biological_effect_fitted":False}
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":r["status"],
                      "n_seasons_with_actual_QA_pixels":r.get("n_seasons_with_actual_QA_pixels"),
                      "seasons":{k:{"status":v.get("status"),"error":v.get("error"),
                                    "counts":v.get("QA_21x21_counts")}
                                 for k,v in r.get("selected_scenes",{}).items()}},
                      sort_keys=True))

if __name__=="__main__":main()
