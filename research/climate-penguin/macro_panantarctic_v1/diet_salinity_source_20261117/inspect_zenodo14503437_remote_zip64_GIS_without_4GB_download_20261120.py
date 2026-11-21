#!/usr/bin/env python3
"""Actual native ZIP64 central-directory and small GIS vector inspection without 4GB transfer.

Public independent Ardley dataset Zenodo 14503437:
- List original 4,109,917,595-byte official ZIP members using HTTP Range (remotezip)
- Verify provider checksums/size metadata, native ZIP member CRC when reading small masks
- If spatial guano vector files exist, inspect exact field names, shape counts, CRS/date.
- Never open 2013–21 isotope proxy Y or fit polynya. Ardley != any fixed original88 ID.
- Do not download full imagery or publish raw copyrighted 4GB file.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile
from collections import defaultdict
from pathlib import Path
import requests
import numpy as np
import shapefile
from remotezip import RemoteZip
ZENODO_REC=14503437
DATASET_SIZE=4109917595
DATASET_MD5="62bb5a89ca7f5f06e54b74e26bf5de5d"
MAX_TOTAL_VECTOR_UNCOMPRESSED=20_000_000
MAX_SINGLE_FILE=8_000_000
VEC_RE=re.compile(r"\.(shp|shx|dbf|prj|cpg|geojson|gml|kml|gpkg|json)$",re.I)
LABEL_RE=re.compile(r"(guano|class|mask|annotation|vector|label|polygon|colony)",re.I)
HEADERS={"User-Agent":"mina-source-only-Ardley-GIS-remotezip-index/1.0 (https://github.com/zuizui0223/mina)"}
def official_metadata():
    r=requests.get(f"https://zenodo.org/api/records/{ZENODO_REC}",headers=HEADERS,timeout=45)
    r.raise_for_status()
    p=r.json()
    if p.get("id")!=ZENODO_REC:raise ValueError("Original Zenodo dataset ID changed")
    files=p.get("files",[])
    if len(files)!=1:raise ValueError(f"Provider nested files changed: {len(files)}")
    entry=files[0]
    if entry.get("size")!=DATASET_SIZE or entry.get("checksum")!=f"md5:{DATASET_MD5}":
        raise ValueError("Ardley published 4.11GB single ZIP fingerprint changed")
    link=entry.get("links",{}).get("content") or entry.get("links",{}).get("self")
    if not link:raise ValueError("Official Zenodo dataset has no direct public content URL")
    return link,p.get("doi"),entry.get("key")

def partial_probe(url):
    # request content small tail. NEVER stream entire 4GB under a 200 response.
    try:
        with requests.get(url,headers={**HEADERS,"Range":"bytes=-65536"},
                          stream=True,timeout=70,allow_redirects=True) as r:
            info={"http_status":r.status_code,
                  "content_range":r.headers.get("Content-Range"),
                  "accept_ranges":r.headers.get("Accept-Ranges"),
                  "content_length_header":r.headers.get("Content-Length"),
                  "final_provider_domain":requests.utils.urlparse(r.url).hostname}
            if r.status_code==206:
                peek=next(r.iter_content(chunk_size=16384),b"")
                info["first_partial_bytes_read"]=len(peek)
                info["partial_source_range_succeeded"]=True
            else:
                # Do not try to consume a 200 4GB response even if status HTTP 200.
                info["partial_source_range_succeeded"]=False
            return info
    except requests.RequestException as e:
        return {"partial_source_range_succeeded":False,
            "error":f"{type(e).__name__}: {str(e)[:500]}"}

def archive_source_inspect(url):
    manifest=[];gis=[];shape_checks=[];mask_hints=[];bytes_downloaded=0
    with RemoteZip(url) as remote:
        infos=remote.infolist()
        if not infos:raise ValueError("Official 4GB remote ZIP has no native directory records")
        for f in infos:
            if f.is_dir():continue
            name=f.filename
            manifest.append({"path":name,"uncompressed_bytes":f.file_size,
                "compressed_bytes":f.compress_size,"zip_crc32":f"{f.CRC:08x}",
                "guano_label_name_hint":bool(LABEL_RE.search(name)),
                "small_vector_extension":bool(VEC_RE.search(name))})
            if VEC_RE.search(name):gis.append(f)
        if len(manifest)>200000:raise ValueError("Unreasonably large ZIP central directory")
        byname={x.filename:x for x in gis}
        # Only read small published vector members. Many PNG/GeoTIFF files are not labels.
        for f in sorted(gis,key=lambda x:(not bool(LABEL_RE.search(x.filename)),x.file_size))[:150]:
            if f.file_size>MAX_SINGLE_FILE or f.file_size+bytes_downloaded>MAX_TOTAL_VECTOR_UNCOMPRESSED:
                continue
            try:
                raw=remote.read(f.filename)
                if len(raw)!=f.file_size:raise ValueError("Uncompressed GIS file byte count wrong")
                bytes_downloaded+=len(raw)
                r={"path":f.filename,"source_SHA256":hashlib.sha256(raw).hexdigest(),
                    "native_bytes":len(raw),"native_CRC32":f"{f.CRC:08x}"}
                if f.filename.lower().endswith(".shp"):
                    prefix=f.filename[:-4]
                    assoc={}
                    for ext in (".dbf",".shx",".prj"):
                        path=prefix+ext
                        inf=byname.get(path) or byname.get(prefix+ext.upper())
                        if inf and inf.file_size<MAX_SINGLE_FILE and inf.file_size+bytes_downloaded<=MAX_TOTAL_VECTOR_UNCOMPRESSED:
                            assoc[ext]=remote.read(inf.filename)
                            bytes_downloaded+=len(assoc[ext])
                    if ".shx" in assoc and ".dbf" in assoc:
                        rd=shapefile.Reader(shp=io.BytesIO(raw),shx=io.BytesIO(assoc[".shx"]),
                            dbf=io.BytesIO(assoc[".dbf"]))
                        r["shape_type"]=rd.shapeTypeName
                        r["n_shapes"]=len(rd)
                        r["coordinate_bbox"]=list(rd.bbox)
                        r["attribute_field_names"]=[str(t[0]) for t in rd.fields[1:]]
                        r["sample_records"]=[x.as_dict() for x in list(rd.iterRecords())[:3]]
                    if ".prj" in assoc:r["WKT_projection"]=assoc[".prj"].decode("utf-8",errors="replace")[:900]
                elif f.filename.lower().endswith((".json",".geojson")):
                    j=json.loads(raw)
                    if isinstance(j,dict):
                        r["json_top_level_type"]=j.get("type")
                        r["json_top_level_field_names"]=list(j)[:60]
                        if isinstance(j.get("features"),list):
                            r["n_geojson_features"]=len(j["features"])
                            r["sample_feature_properties"]=[x.get("properties") for x in j["features"][:3]]
                elif f.filename.lower().endswith(".prj"):
                    r["source_WKT_projection"]=raw.decode("utf-8",errors="replace")[:900]
                shape_checks.append(r)
            except Exception as e:
                shape_checks.append({"path":f.filename,
                    "status":"SMALL_NATIVE_VECTOR_VERIFICATION_ERROR",
                    "error":f"{type(e).__name__}: {str(e)[:600]}"})
    return manifest,shape_checks,bytes_downloaded

def main(a):
    a.out.mkdir(parents=True,exist_ok=True)
    url,doi,filename=official_metadata()
    ranges=partial_probe(url)
    out={"status":"OFFICIAL_4GB_ARDLEY_ZIP_ONLY_METADATA",
        "source_record_id":ZENODO_REC,"source_doi":doi,
        "official_native_filename":filename,
        "official_size_bytes":DATASET_SIZE,"official_md5_not_recomputed_entire_4GB":DATASET_MD5,
        "original_88_has_Ardley_site_ID":False,
        "original_88_nearest_site_is_not_Ardley":True,
        "range_probe":ranges,
        "not_future_isotope_reanalysis":True,
        "not_direct_2013_2021_guano_pixel_GT_until_dates_and_georeferencing_checked":True,
        "never_downloaded_whole_4GB":True}
    try:
        if not ranges.get("partial_source_range_succeeded"):
            raise ValueError("Provider does not confirm byte ranges; refuse full original 4GB download")
        members,parsed,bytes_read=archive_source_inspect(url)
        out["status"]="OFFICIAL_4GB_ZIP_NATIVE_CENTRAL_DIRECTORY_INSPECTED"
        out["original_zip_members_total"]=len(members)
        out["native_GIS_vector_extensions_count"]=sum(x["small_vector_extension"] for x in members)
        out["guano_label_filename_hints_count"]=sum(x["guano_label_name_hint"] for x in members)
        out["actual_small_native_GIS_files_inspected"]=parsed
        out["small_vector_member_uncompressed_bytes_retrieved"]=bytes_read
        Path(a.out/"ARDLEY_4GB_ORIGINAL_ZIP_MEMBER_INDEX.json").write_text(
             json.dumps(members,ensure_ascii=False,indent=2)+"\n")
    except Exception as e:
        out["source_zip_native_index_error"]=f"{type(e).__name__}: {str(e)[:900]}"
        out["actual_GIS_labels_not_verified"]=True
    (a.out/"ARDLEY_4GB_REMOTE_ZIP64_GIS_AND_ACTUAL_LABEL_INSPECTION.json").write_text(
        json.dumps(out,ensure_ascii=False,indent=2,default=str)+"\n")
    print(json.dumps({"status":out["status"],"native_filename":filename,
       "official_zip_size":DATASET_SIZE,"source_range_probe":ranges,
       "native_member_count":out.get("original_zip_members_total"),
       "GIS_vector_extension_count":out.get("native_GIS_vector_extensions_count"),
       "small_vectors_read":len(out.get("actual_small_native_GIS_files_inspected",[])),
       "sample_vectors":out.get("actual_small_native_GIS_files_inspected",[])[:15],
       "error":out.get("source_zip_native_index_error"),
       "no_future_Y_test":True},ensure_ascii=False,indent=2,default=str),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
