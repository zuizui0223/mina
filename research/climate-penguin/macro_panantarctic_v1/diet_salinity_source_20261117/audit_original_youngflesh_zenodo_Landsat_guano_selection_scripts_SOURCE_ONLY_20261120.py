#!/usr/bin/env python3
"""Audit original Youngflesh et al 2026 archived LANDSAT pixel selection scripts
without opening new 2013+ satellite images, δ15N optical Y, or polynya effects.

The original published Zenodo data.zip (record 17409948) is MD5-verified.
This reads source code member names, hashes and relevant extraction instructions;
does NOT execute all source scripts or distribute the whole 256 MB original.
"""
from __future__ import annotations
import argparse,hashlib,json,re,urllib.request,zipfile
from pathlib import Path
SOURCE_REC=17409948
SOURCE_ARCHIVE_MD5="e29a2f68c84e3a515044d554540def2f"
SOURCE_BYTES=256425816
UA={"User-Agent":"mina-source-original-guano-pipeline-audit/1.0 https://github.com/zuizui0223/mina",
    "Accept":"application/json"}
SCRIPT_ENDINGS=(".r",".rmd",".py",".ipynb",".md",".txt",".qmd",".sh")
SEARCH_PATTERNS={
    "pixel_segmentation":r"guano_bin|guano(_|-)?mask|classif|segmentation|guano|n_pix",
    "native_site_pixel_selection":r"landsat|etm|tm|surface_reflect|pixel|cell|bad|polygon|site_id",
    "cloud_and_snow_QA":r"cloud|shadow|snow|qa_pixel|quality|saturation|mask",
    "source_sensor_support":r"\bL4\b|\bL5\b|\bL7\b|\bL8\b|[4-9]_TM|OLI|RSR|radiometric",
    "data_provenance":r"gee|earth ?engine|landsat|USGS|landsat_reflectance|\.rds",
    "spatial_polygon_inputs":r"st_read|read_sf|vect\(|shapefile|\.shp|roi|buffer|sf::"
}
PATTERNS={k:re.compile(v,re.I) for k,v in SEARCH_PATTERNS.items()}
def get_record():
    req=urllib.request.Request("https://zenodo.org/api/records/17409948",headers=UA)
    with urllib.request.urlopen(req,timeout=60) as src:r=json.load(src)
    if r.get("id")!=SOURCE_REC:raise ValueError("Original publisher record changed")
    fs=r.get("files",[])
    f=next((f for f in fs if f.get("key")=="data.zip"),None)
    if not f or f.get("size")!=SOURCE_BYTES or f.get("checksum")!="md5:"+SOURCE_ARCHIVE_MD5:
        raise ValueError("Original source file metadata changed")
    return f.get("links",{}).get("content") or f["links"]["self"]
def fetch_zip(path):
    url=get_record()
    digest=hashlib.md5();num=0
    with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=240) as src,path.open("wb") as dest:
        while True:
            chunk=src.read(1_048_576)
            if not chunk:break
            dest.write(chunk);digest.update(chunk);num+=len(chunk)
            if num>SOURCE_BYTES:raise ValueError("Original publisher download exceeded source size")
    if (num,digest.hexdigest())!=(SOURCE_BYTES,SOURCE_ARCHIVE_MD5):
        raise ValueError("Original publisher ZIP byte count or checksum failed")
    return {"original_publisher_md5":digest.hexdigest(),"source_original_archive_bytes":num}
def main(a):
    a.out.mkdir(parents=True,exist_ok=True)
    archive=a.out/"_TEMP_original_256MB_source_delete.zip"
    src_info=fetch_zip(archive)
    whole=[];scripts=[];hits=[];other=[]
    try:
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:raise ValueError("Original publisher ZIP archive CRC fails")
            for f in z.infolist():
                if f.is_dir():continue
                path=f.filename
                item={"path":path,"bytes":f.file_size,"CRC32":format(f.CRC,"08x")}
                whole.append(item)
                base=Path(path).name.lower()
                if re.search(r"(guano|land(sat)?|colony|roi|shape|mask|pixel|site|scripts|coordinate)",path,re.I):
                    other.append(item)
                if not base.endswith(SCRIPT_ENDINGS) or f.file_size>2_000_000:continue
                raw=z.read(f.filename)
                # The scripts are public source; do not rehost full source, only inspect
                text=raw.decode("utf-8",errors="replace")
                lines=text.splitlines()
                script={"path":path,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"total_lines":len(lines)}
                found={k:sum(1 for line in lines if pattern.search(line)) for k,pattern in PATTERNS.items()}
                script["match_line_counts"]=found
                scripts.append(script)
                if sum(found.values())==0:continue
                # Minimize copyright exposure to brief code-line cues, preserve line positions for exact reproductions.
                selected=[]
                for i,line in enumerate(lines,1):
                    cats=[k for k,pattern in PATTERNS.items() if pattern.search(line)]
                    if not cats:continue
                    selected.append({"line":i,"category":cats,"line_excerpt":line.strip()[:260]})
                hits.append({"path":path,"number_of_target_lines":len(selected),
                             "first_matching_line_excerpts":selected[:90]})
    finally:
        archive.unlink(missing_ok=True)
    expected_rds="L0/Landsat/landsat_reflectance_L457-2025-07-16.rds"
    if not any(x["path"]==expected_rds for x in whole):
        raise ValueError("Expected original source RDS absent from 256MB original ZIP")
    result={
      "status":"PUBLISHER_VERIFIED_FULL_ORIGINAL_YOUNGFLESH_SOURCE_CODE_INVENTORY_NO_FUTURE_Y",
      **src_info,
      "archive_original_Zenodo":SOURCE_REC,
      "actual_native_zip_member_files_n":len(whole),
      "published_source_300mb_deleted_after_read":True,
      "real_publisher_script_members":scripts,
      "target_landsat_guano_files":other,
      "relevant_source_script_line_excerpts":hits,
      "new_L8_2013_2021_satellite_Y_not_opened":True,
      "winter_coastal_polynya_association_not_refitted":True,
      "not_author_hierarchical_diet_index_reproduction":True,
    }
    (a.out/"ORIGINAL_ZENODO_17409948_LANDSAT_GUANO_PIPELINE_SOURCE_CODE_INVENTORY.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    (a.out/"ORIGINAL_ZENODO_17409948_ALL_FILE_PATHS_METADATA_ONLY.json").write_text(
        json.dumps(whole,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":result["status"],"native_file_count":len(whole),
        "source_scripts_n":len(scripts),"source_scripts_by_name":
        [{k:x[k] for k in ("path","bytes","total_lines","match_line_counts")} for x in scripts],
        "land_guano_named_source":other[:55],"source_relevant_script_line_match_counts":
        [{"path":x["path"],"n":x["number_of_target_lines"]} for x in hits],
        "no_future_Y":True},indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
