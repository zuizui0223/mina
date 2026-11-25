#!/usr/bin/env python3
"""Only first 128 KiB of 4 source original BAS Hart TIFFs, no image raster data.

This is a strict source Range support + TIFF IFD georeferencing audit, not
biological remote-sensing extraction. No full image downloads authorized.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urlparse,unquote

import requests
from tifffile import TiffFile

SOURCE_STATUS="VERIFIED_ORIGINAL_SOURCE_FILES_PUBLISHER_SUMMARY_COUNT_DISCREPANCY"
MAX_BYTES=131072
FILE_NAMES={
 "Ashen_Hills":"Ashen_Hills/tiff_images/ASHE_05JAN2019_tile1.tif",
 "Bellingshausen":"Bellingshausen/tiff_images/BELG_09JAN2020_TIF.tif",
 "Beach_Point":"Beach_Point/tiff_images/BEAC_09JAN2020_TIF.tif",
 "Hewison_Point":"Hewison_Point/tiff_images/HEWI_09JAN2020_tile1.tif",
}
HOSTS={"ramadda.data.bas.ac.uk","194.66.5.50"}


def source_image_paths(manifest):
    if manifest.get("status")!=SOURCE_STATUS or len(manifest.get("original_all_file_metadata_only",[]))!=164:
        raise ValueError("SOURCE_STOP original successful V16 source files absent")
    selected={}
    for site,filename in FILE_NAMES.items():
        candidates=[r for r in manifest["original_all_file_metadata_only"]
                    if r.get("original_archive_relative_path")==filename
                    and r.get("top_level_source_locality_folder")==site
                    and r.get("original_source_file_type")=="tif"]
        if len(candidates)!=1:
            raise ValueError("SOURCE_STOP published representative original TIFF missing/duplicate")
        file=candidates[0]
        uri=urlparse(file["source_file_url_https"])
        if (uri.scheme!="https" or uri.hostname not in HOSTS
            or unquote(uri.path)!="/repository/entry/get/"+filename.split("/")[-1]):
            raise ValueError("SOURCE_STOP original TIFF URL unsafe or not published filename")
        selected[site]=file
    return selected


def fetch_bounded_original_tiff_header(file):
    original=file["source_file_url_https"]
    result={"source_original_relative_path":file["original_archive_relative_path"],
            "source_original_file_id":file["original_publisher_archive_id"],
            "status":"HOLD_ORIGINAL_TIFF_HTTP_RANGE",
            "image_raster_pixel_values_read":0,
            "entire_original_source_image_downloaded":False}
    with requests.Session() as sess:
        with sess.get(original,stream=True,timeout=(20,90),
                      headers={"Range":f"bytes=0-{MAX_BYTES-1}",
                               "User-Agent":"mina-original-BAS-tiff-IFD-no-image-pixels-v25/1.0"}) as r:
            r.raise_for_status()
            last=urlparse(r.url)
            if last.scheme!="https" or last.hostname not in HOSTS:
                raise ValueError("SOURCE_STOP original published GeoTIFF redirected off BAS")
            result["HTTP_status"]=r.status_code
            cr=str(r.headers.get("Content-Range",""))
            result["HTTP_Content_Range"]=cr[:80]
            content_type=str(r.headers.get("Content-Type",""))
            result["HTTP_content_type"]=content_type[:100]
            if r.status_code!=206:
                result["status"]="SOURCE_RANGE_NOT_SUPPORTED_FULL_IMAGE_NOT_DOWNLOADED"
                return result
            match=re.fullmatch(r"bytes 0-(\d+)/(\d+|\*)",cr.strip())
            if not match or int(match.group(1))>=MAX_BYTES:
                result["status"]="SOURCE_CONTENT_RANGE_UNEXPECTED"
                return result
            bounded=bytearray()
            for chunk in r.iter_content(chunk_size=16384):
                bounded.extend(chunk)
                if len(bounded)>MAX_BYTES:
                    result["status"]="SOURCE_TOO_MANY_BYTES_RETURNED"
                    return result
            buf=bytes(bounded)
            if len(buf)!=int(match.group(1))+1:
                result["status"]="SOURCE_PARTIAL_HEADER_BYTES_MISMATCH"
                return result
    result["bounded_original_source_header_bytes"]=len(buf)
    result["bounded_original_TIFF_header_SHA256"]=hashlib.sha256(buf).hexdigest()
    if buf[:4] not in (b"II*\x00",b"MM\x00*",b"II+\x00",b"MM\x00+"):
        result["status"]="SOURCE_STOP_BYTES_NOT_TIFF"
        return result
    try:
        with TiffFile(io.BytesIO(buf)) as original:
            page=original.pages[0]
            tags=page.tags
            def value(n):
                item=tags.get(n)
                if item is None:return None
                x=item.value
                if isinstance(x,(tuple,list)):
                    return list(x)[:80]
                if isinstance(x,(str,int,float)):return x
                return repr(x)[:500]
            result.update({
              "status":"ORIGINAL_BAS_GEOTIFF_IFD_PARTIAL_HEADER_READ",
              "original_TIFF_first_IFD_shape":list(page.shape),
              "original_TIFF_first_IFD_dtype":str(page.dtype),
              "original_TIFF_first_IFD_model_pixel_scale_tag_33550":value(33550),
              "original_TIFF_first_IFD_model_tiepoint_tag_33922":value(33922),
              "original_TIFF_first_IFD_geo_key_directory_34735":value(34735),
              "original_TIFF_first_IFD_projection_verified":False,
              "original_TIFF_geo_bounds_and_nest_common_coverage_verified":False,
              "original_image_data_pixel_values_read":0,
            })
    except Exception as e:
        result["status"]="SOURCE_PARTIAL_HEADER_TIFF_IFD_NOT_RESOLVABLE"
        result["error_type"]=type(e).__name__
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v16",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    report={"status":"HOLD_FIRST_PARTIAL_BAS_ORIGINAL_TIFF_HEADERS_V25"}
    try:
        manifest=json.loads(a.v16.read_text(encoding="utf-8"))
        selected=source_image_paths(manifest)
        site={site:fetch_bounded_original_tiff_header(file)
              for site,file in sorted(selected.items())}
        report={
           "status":"BAS_HART_FOUR_SOURCE_IMAGE_TIFF_PARTIAL_HEADER_V25",
           "source_original_publisher_archive":"10.5285/28222725-c53d-40f4-9350-49c368899f0b",
           "source_site_original_representative_TIFF_n":len(site),
           "source_partial_TIFF_metadata_by_site":site,
           "source_first_party_original_image_pixels_read":0,
           "source_complete_mosaic_or_species_coobserved_area_verified":False,
           "original_nest_temporal_acquisition_day_from_filename_only":True,
           "source_original_four_original_image_acquisition_date_markers":{
               "Ashen_Hills":"05JAN2019","Bellingshausen":"09JAN2020",
               "Beach_Point":"09JAN2020","Hewison_Point":"09JAN2020"}
        }
    except Exception as e:
        report["error_type"]=type(e).__name__
        report["error"]=str(e)[:850]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
