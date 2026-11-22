#!/usr/bin/env python3
"""Response-blind USGS Collection-2 L8 QA_PIXEL/QA_RADSAT at original guano POINTs.
Not new guano classification, not valid new isotope δ15N, and not a polynya effect.
Frozen QA pilot: first lexical site in Victoria/Wilkes/Southwest Peninsula, season 2018,
earliest and lowest-catalog-cloud L8 scene per site (no response used).
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import zipfile
import requests
import planetary_computer
import numpy as np
import pandas as pd
from pyproj import Transformer
import rasterio

SOURCE_OLD_GUANO_GEOGRAPHY_SHA256="0ee6a774bd960a132b270e34a8873529600dc985015085fdd3351626c653f4e7"
SOURCE_L8_SCENES_SHA256="575dc514c6103b1aaefb0bce1bf7f5084aedc5d2c4edb3519d0ac03af82a2750"
OLD_COORD_CSV="original_88_source_stable_site_cell_coordinate_candidates_NOT_future_roi.csv"
L8_SCENES_CSV="original_88_L8_real_scene_metadata_no_Y.csv"
REGIONS=("Victoria Land","Wilkes Land","Southwest Antarctic Peninsula")
YEAR=2018
STAC_ITEM_URL="https://earth-search.aws.element84.com/v1/collections/landsat-c2-l2/items/"
MIRROR_SAME_SCENE_ID_ITEM_URL="https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2/items/"
SOURCE_CRS="EPSG:3031"
QA_PIXEL_INVALID_BITS=(0,1,2,3,4,5,7) # fill, dilated cloud, cirrus, cloud, shadow, snow, water; bit 6 is clear
# L8 OLI/TIRS QA_RADSAT bits 0..6 reflectance saturation, bit 11 terrain occlusion.
QA_RADSAT_INVALID_MASK=sum(1<<i for i in range(0,7))|(1<<11)

def source_bytes(zip_path,checksum,member):
    raw=Path(zip_path).read_bytes()
    got=hashlib.sha256(raw).hexdigest()
    if got!=checksum: raise ValueError(f"source-only ZIP SHA drift: {got}")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip():raise ValueError("source-only ZIP CRC fail")
        hits=[x for x in z.namelist() if x==member or x.endswith("/"+member)]
        if len(hits)!=1:raise ValueError(f"Expected source-only member missing/ambiguous: {member}")
        return z.read(hits[0])

def get_fixed_pilot(old_zip,scenes_zip):
    old=pd.read_csv(io.BytesIO(source_bytes(old_zip,SOURCE_OLD_GUANO_GEOGRAPHY_SHA256,OLD_COORD_CSV)))
    scenes=pd.read_csv(io.BytesIO(source_bytes(scenes_zip,SOURCE_L8_SCENES_SHA256,L8_SCENES_CSV)))
    required={"site_id","source_geometry_easting","source_geometry_northing","source_pixel_cell_id"}
    if not required.issubset(old): raise ValueError("Old original POINT geometry columns missing")
    if old.site_id.nunique()!=88 or len(old)!=15347:
        raise ValueError(f"Original fixed 88 ROI point source denominator changed: {len(old)}, {old.site_id.nunique()}")
    if not np.isfinite(old[["source_geometry_easting","source_geometry_northing"]]).all().all():
        raise ValueError("Old native EPSG3031 POINT coordinates corrupted")
    chosen=[]
    for region in REGIONS:
        s=scenes.loc[
            scenes.period.eq("new") &
            scenes.season.eq(YEAR) &
            scenes.original_region.eq(region)
        ].copy()
        if s.empty:raise ValueError(f"No actual L8 scenes in frozen 2018 region: {region}")
        # Site selected by ID; independently and before any cloud/pixel evaluation.
        site=str(sorted(s.site_id.astype(str).unique())[0])
        s=s.loc[s.site_id.astype(str).eq(site)].sort_values(["source_scene_datetime","scene_id"])
        if s.empty or site not in set(old.site_id.astype(str)):
            raise ValueError(f"Source site ID missing old guano PIXEL or new scene: {site}")
        first=s.iloc[0]
        available=s.loc[s.eo_cloud_cover_scene_percent.notna()].sort_values(
            ["eo_cloud_cover_scene_percent","source_scene_datetime","scene_id"])
        second=available.iloc[0] if len(available)>0 else first
        if str(second.scene_id)==str(first.scene_id):
            second=s.iloc[1] if len(s)>1 else first
        for mode,row in (("first_chronological",first),("minimum_scene_cloud",second)):
            chosen.append({"region":region,"site_id":site,"selection_rule":mode,
              "season":YEAR,"scene_id":str(row.scene_id),
              "scene_datetime":str(row.source_scene_datetime),
              "scene_cloud_percent":float(row.eo_cloud_cover_scene_percent) if pd.notna(row.eo_cloud_cover_scene_percent) else None,
              "original_fixed_guano_point_count":int((old.site_id.astype(str)==site).sum())})
    pilot=pd.DataFrame(chosen)
    if not pilot.scene_id.str.startswith("LC08_").all():
        raise ValueError("Sourced L8 scene ID prefix not LC08")
    return old,pilot

def get_asset(item,short):
    a=item.get("assets",{})
    if short not in a:
        raise ValueError(f"Public STAC item has no official {short} asset")
    entry=a[short]
    url=entry.get("href")
    if not url or not (url.startswith("https://") or url.startswith("s3://")):
        raise ValueError(f"Official source {short} asset href not a supported URL")
    return url

def qa_values(points,asset):
    # Dataset is over HTTPS/s3. rasterio.sample reads only selected original ROI positions.
    # Do not load new red/blue/green/SWIR image pixels or produce any new isotope proxy.
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="YES",
         CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF,.tif",AWS_NO_SIGN_REQUEST="YES",
         AWS_REQUEST_PAYER="requester"):
        with rasterio.open(asset) as src:
            if src.count!=1:raise ValueError(f"Unexpected native QA raster count {src.count}")
            if not src.crs:raise ValueError("Native QA asset missing CRS")
            xs=points.source_geometry_easting.to_numpy(dtype=float)
            ys=points.source_geometry_northing.to_numpy(dtype=float)
            tr=Transformer.from_crs(SOURCE_CRS,src.crs,always_xy=True)
            tx,ty=tr.transform(xs,ys)
            sampled=np.ma.asarray(list(src.sample(list(zip(tx,ty)),indexes=1,masked=True)))
            # rasterio.sample(indexes=1) yields one-band vector per point: (n,1).
            if sampled.shape!=(len(points),1):
                raise ValueError(f"Point rasterio.sample expected (n,1), got {sampled.shape} for {len(points)}")
            sampled=sampled[:,0]
            mask=np.ma.getmaskarray(sampled)
            val=np.ma.filled(sampled,-999).astype(np.int64)
            idx=np.array([src.index(float(x),float(y)) for x,y in zip(tx,ty)])
            in_window=(idx[:,0]>=0)&(idx[:,0]<src.height)&(idx[:,1]>=0)&(idx[:,1]<src.width)
            return val, mask|(~in_window), {"crs":str(src.crs),"size":[src.height,src.width],
                   "pixel_resolution":[float(abs(src.res[0])),float(abs(src.res[1]))],
                   "source_driver":str(src.driver),"source_nodata":src.nodata}

def one(item,original):
    site=str(item["site_id"])
    points=original.loc[original.site_id.astype(str).eq(site)].copy()
    if len(points)!=int(item["original_fixed_guano_point_count"]):
        raise ValueError("Old truly geolocated ROI denominator changed per colony")
    scene=item["scene_id"]
    url=STAC_ITEM_URL+scene
    resp=requests.get(url,headers={"Accept":"application/geo+json, application/json","User-Agent":"mina-source-only-L8QA/1.0"},timeout=55)
    resp.raise_for_status()
    info=resp.json()
    if info.get("id")!=scene:raise ValueError("Source requested STAC item ID mismatch")
    if str(info.get("properties",{}).get("platform","")).lower().replace("_","-")!="landsat-8":
        raise ValueError("STAC original scene not Landsat 8")
    # Earth Search STAC points to USGS s3 requester-pays: GitHub unauthenticated
    # runner was rejected. PC mirrors the SAME USGS C2 scene ID without changing
    # instrument, source season or QA_PIXEL semantics. Sign its Azure blob only.
    pc_response=requests.get(MIRROR_SAME_SCENE_ID_ITEM_URL+scene,
       headers={"Accept":"application/geo+json, application/json",
                "User-Agent":"mina-original-source-L8-QA-same-scene-pc-mirror/1.0"},timeout=55)
    pc_response.raise_for_status()
    pc_item=pc_response.json()
    if pc_item.get("id")!=info.get("id") or pc_item.get("id")!=scene:
        raise ValueError("PC and USGS-source Earth Search scene identity mismatch")
    if pc_item.get("properties",{}).get("platform","").lower().replace("_","-")!="landsat-8":
        raise ValueError("PC mirrored USGS source is not same Landsat 8 platform")
    qa_source=get_asset(pc_item,"qa_pixel")
    rad_source=get_asset(pc_item,"qa_radsat")
    qa_url=planetary_computer.sign(qa_source)
    rad_url=planetary_computer.sign(rad_source)
    pixel,miss,pix_meta=qa_values(points,qa_url)
    rad,missrad,rad_meta=qa_values(points,rad_url)
    if pix_meta["crs"]!=rad_meta["crs"] or pix_meta["size"]!=rad_meta["size"]:
        raise ValueError("USGS native QA_PIXEL and QA_RADSAT raster geospatial source not aligned")
    fill=(pixel & (1<<0))!=0
    cloudy=(pixel & ((1<<1)|(1<<2)|(1<<3)|(1<<4)))!=0
    snow=(pixel & (1<<5))!=0
    water=(pixel & (1<<7))!=0
    sat=(rad & QA_RADSAT_INVALID_MASK)!=0
    invalid=miss|missrad|fill|cloudy|snow|water|sat
    receipt={**item,
       "valid_original_2018_L8_QA_selected_source_points":int((~invalid).sum()),
       "native_old_guano_ROI_points_falling_inside_scene":int((~miss).sum()),
       "native_QA_rasters_fully_valid_inside":int((~miss&~missrad).sum()),
       "source_native_L8_QA_fill":int((~miss&fill).sum()),
       "source_native_L8_QA_clouds_shadow_cirrus":int((~miss&cloudy).sum()),
       "source_native_L8_QA_snow":int((~miss&snow).sum()),
       "source_native_L8_QA_water":int((~miss&water).sum()),
       "source_native_L8_RADSAT_saturation_terrain":int((~missrad&sat).sum()),
       "new_L8_QA_PIXEL_source_unsigned_href":qa_source,
       "new_L8_QA_RADSAT_source_unsigned_href":rad_source,
       "native_publisher_scene_id_identical_across_EarthSearch_and_PC":True,
       "qa_source_mirror":"Microsoft Planetary Computer signed temporary SAS for SAME USGS C2 L2 scene",
       "native_raster_source":pix_meta,
       "source_satellite_2018_spectral_reflectance_not_read":True,
       "new_current_guano_presence_not_determined":True,
    }
    return receipt

def main(a):
    old,pilot=get_fixed_pilot(a.old_original_roi_zip,a.l8_scene_zip)
    a.out.mkdir(parents=True,exist_ok=True)
    pilot.to_csv(a.out/"predeclared_three_region_2018_L8_QA_scene_site_pilot.csv",index=False)
    receipts=[];errors=[]
    for selection in pilot.to_dict("records"):
        try:
            receipt=one(selection,old)
            receipts.append(receipt)
            print(json.dumps({"site":selection["site_id"],"scene":selection["scene_id"],
                  "source_native_QA_pass":receipt["valid_original_2018_L8_QA_selected_source_points"],
                  "source_old_pixels":receipt["original_fixed_guano_point_count"]},ensure_ascii=False),flush=True)
        except Exception as e:
            errors.append({**selection,"error":f"{type(e).__name__}: {str(e)[:800]}"})
    if receipts:
        pd.DataFrame(receipts).drop(columns="native_raster_source").to_csv(
            a.out/"actual_2018_L8_QA_original_source_ROI_points_only_NO_Y.csv",index=False)
    if errors:
        pd.DataFrame(errors).to_csv(a.out/"native_source_L8_QA_pilot_failure_diagnostics.csv",index=False)
    status=("SOURCE_L8_2018_QA_OLD_ROI_READABLE_ONLY_NOT_CURRENT_GUANO" if not errors
            else "DATA_SOURCE_UNVERIFIED_OR_L8_QA_ASSET_UNREADABLE")
    result={"status":status,
       "three_region_fixed_pilot_regions":list(REGIONS),"source_frozen_season":YEAR,
       "old_source_roi_sha256":SOURCE_OLD_GUANO_GEOGRAPHY_SHA256,
       "new_stac_L8_scene_metadata_sha256":SOURCE_L8_SCENES_SHA256,
       "scenes_attempted":len(pilot),"source_qa_scenes_succeeded":len(receipts),
       "native_qa_2018_old_roi_results":receipts,
       "source_errors":errors,
       "no_new_guano_classifier_or_polygon_derived":True,
       "no_new_year_guano_pixel_assumed_from_historic_roi":True,
       "no_new_L8_spectral_reflectance_opened":True,
       "no_new_delta15N_computed":True,
       "no_polynya_effect_fitted":True,
       "not_full_original_88_L8_image_pixel_eligibility":True}
    (a.out/"2018_L8_THREE_REGION_NATIVE_QA_ONLY_OLD_SOURCE_GUANO_ROI_PILOT.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":status,"attempted":len(pilot),"succeeded":len(receipts),
         "errors":errors[:5]},indent=2,ensure_ascii=False),flush=True)
    if errors:
        raise RuntimeError("Native L8 QA pilot source not fully accessible; see persisted receipt, no Y opened")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--old-original-roi-zip",type=Path,required=True)
    p.add_argument("--l8-scene-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
