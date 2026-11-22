#!/usr/bin/env python3
"""Read *actual* 44 dated Adélie/gentoo Ardley GUANO shapefile polygons within
Zenodo's 4.11GB original published ZIP64 via remote HTTP Range.

No post-2013 optical isotope proxy, and no measured prey/polynya association.
Guano polygon geometry is genuine external positive reference, not yet validated
complete negative labels or transferable L8 30m classifier.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import shapefile
from remotezip import RemoteZip
from pyproj import CRS,Transformer
from shapely.geometry import shape as shapely_shape
from shapely.ops import unary_union

ORIGINAL_FULL_ZIP_SIZE=4109917595
ORIGINAL_FULL_ZIP_MD5="62bb5a89ca7f5f06e54b74e26bf5de5d"
MANIFEST_ARTIFACT_SHA="ef4afd6db995ac83cdd51c798d08d00dcd729e2e39c85b096b91785cb36a6ebc"
MANIFEST_NAME="ARDLEY_4GB_ORIGINAL_ZIP_MEMBER_INDEX.json"
GUANO_SHP=re.compile(r"^Guano/(\d{6})/Ardley_(\d{8})_(adelie|gentoo)\.shp$",re.I)
HEADERS={"User-Agent":"mina-native-guano-44-real-shp-source-geo-validation/1.0"}

def read_manifest(path):
    data=Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest()!=MANIFEST_ARTIFACT_SHA:
        raise ValueError("Original provider verified ZIP64 source manifest archive digest mismatch")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip():raise ValueError("Original native manifest ZIP CRC failure")
        names=[n for n in z.namelist() if n==MANIFEST_NAME or n.endswith("/"+MANIFEST_NAME)]
        if len(names)!=1:raise ValueError("Original full 2,448 member index missing")
        f=json.loads(z.read(names[0]))
    if len(f)!=2448:raise ValueError(f"Original ZIP64 2448-member source native roster changed, got {len(f)}")
    rows=[]
    for m in f:
        hit=GUANO_SHP.match(m["path"])
        if hit:
            timegroup,datestr,sp=hit.groups()
            date=datetime.strptime(datestr,"%Y%m%d")
            if date.year not in (2013,2014,2015,2016,2017,2018):
                raise ValueError("Unexpected source guano event date")
            rows.append({"path":m["path"],"species":sp.lower(),
               "date":date.date().isoformat(),"season_bucket":timegroup,
               "source_native_uncompressed_shp_bytes":int(m["uncompressed_bytes"])})
    if len(rows)!=44:raise ValueError(f"Expected 44 actual native Guano/*.shp, got {len(rows)}")
    if set(v["season_bucket"] for v in rows)!={"201314","201415","201617","201718"}:
        raise ValueError("Native original 4 season buckets drifted")
    if set(v["species"] for v in rows)!={"adelie","gentoo"}:
        raise ValueError("Native species mask semantics drifted")
    return rows

def published_url():
    r=requests.get("https://zenodo.org/api/records/14503437",headers=HEADERS,timeout=45)
    r.raise_for_status()
    d=r.json()
    if d.get("id")!=14503437:raise ValueError("Official provider ID differs")
    fs=d.get("files",[])
    if len(fs)!=1 or fs[0].get("size")!=ORIGINAL_FULL_ZIP_SIZE or fs[0].get("checksum")!="md5:"+ORIGINAL_FULL_ZIP_MD5:
        raise ValueError("Official 4GB source provider metadata changed")
    url=fs[0].get("links",{}).get("content") or fs[0].get("links",{}).get("self")
    if not url:raise ValueError("Published original ZIP64 content URL absent")
    return url

def geofeatures(remote,byname,entry):
    file=entry["path"]
    root=file[:-4]
    parts={}
    for ext in (".shp",".shx",".dbf",".prj"):
        path=root+ext
        if path not in byname:raise ValueError(f"Missing essential native shapefile sidecar {path}")
        if byname[path].file_size>5_000_000:raise ValueError(f"Unexpected huge native guano vector component: {path}")
        data=remote.read(path)
        if len(data)!=byname[path].file_size:raise ValueError(f"Actual source vector bytes mismatch {path}")
        parts[ext]=data
    wkt=parts[".prj"].decode("utf-8",errors="replace")
    crs=CRS.from_wkt(wkt)
    if not crs.is_projected:raise ValueError("Native guano must have projected geographic source")
    with shapefile.Reader(shp=io.BytesIO(parts[".shp"]),shx=io.BytesIO(parts[".shx"]),
                          dbf=io.BytesIO(parts[".dbf"])) as sf:
        n=len(sf);shape_type=sf.shapeTypeName;fields=[v[0] for v in sf.fields[1:]]
        records=[]
        area_raw=0.0;invalid=0
        part_geoms=[]
        # Empty shapefile is legitimate absence if native source wrote an empty guano mask.
        for sr in sf.iterShapeRecords():
            sh=sr.shape
            geom=shapely_shape(sh.__geo_interface__)
            if not geom.is_valid:invalid+=1
            if geom.geom_type not in ("Polygon","MultiPolygon"):
                raise ValueError(f"Real guano shape is {geom.geom_type}, not polygon")
            area_raw+=geom.area
            part_geoms.append(geom)
            if len(records)<3:
                records.append({k:str(v) for k,v in list(sr.record.as_dict().items())[:14]})
        if part_geoms:
            # Important: polygon overlaps can overcount total guano footprint; keep both.
            unionarea=float(unary_union(part_geoms).area)
        else:
            unionarea=0
        bbox=[float(x) for x in sf.bbox] if n else None
    tr=Transformer.from_crs(crs,"EPSG:4326",always_xy=True)
    centroid=None
    if bbox:
        cx=(bbox[0]+bbox[2])/2;cy=(bbox[1]+bbox[3])/2
        lon,lat=tr.transform(cx,cy)
        centroid=[float(lon),float(lat)]
        if not (-63<lat<-61 and -60<lon<-57):
            raise ValueError(f"Guano GIS source not in Ardley region: {centroid}")
    return {**entry,"n_native_guano_polygons":n,
        "native_shape_type":shape_type,"source_WKT_CRS_EPSG":crs.to_epsg(),
        "source_projected_crs_name":crs.name,
        "source_polygon_fields":fields,
        "native_projected_bbox":bbox,"bbox_center_WGS84_lonlat":centroid,
        "invalid_source_geometries":int(invalid),
        "sum_polygon_areas_m2":area_raw,"dissolved_union_footprint_m2":unionarea,
        "3_sample_source_records":records,
        "shp_sha256":hashlib.sha256(parts[".shp"]).hexdigest(),
        "shp_dbf_sha256":hashlib.sha256(parts[".dbf"]).hexdigest(),
        "projection_WKT":wkt[:800],
        "source_is_PUBLISHED_externally_delineated_guano_polygon":True,
        "source_Ardley_not_one_of_88_original_isotope_sites":True}

def main(a):
    entries=read_manifest(a.manifest_artifact_zip)
    url=published_url()
    successes=[];failures=[]
    with RemoteZip(url) as z:
        byname={v.filename:v for v in z.infolist() if not v.is_dir()}
        if len(byname)!=2448:raise ValueError("Source remote original ZIP member support changed")
        for entry in sorted(entries,key=lambda t:(t["season_bucket"],t["species"],t["date"])):
            try:
                val=geofeatures(z,byname,entry)
                successes.append(val)
                print(json.dumps({"actual_guano_file":entry["path"],"n":val["n_native_guano_polygons"],
                  "EPSG":val["source_WKT_CRS_EPSG"],"union_m2":val["dissolved_union_footprint_m2"],
                  "bbox_lonlat":val["bbox_center_WGS84_lonlat"]},ensure_ascii=False),flush=True)
            except Exception as exc:
                failures.append({"file":entry["path"],"error":f"{type(exc).__name__}: {str(exc)[:550]}"})
    a.out.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(successes)
    df.to_csv(a.out/"ARDLEY_44_NATIVE_DATED_GUANO_SHAPEFILE_SOURCE_GEOGRAPHY.csv",index=False)
    periods=[]
    if successes:
        for (season,sp),v in df.groupby(["season_bucket","species"]):
            periods.append({"season_bucket":season,"species":sp,"n_original_source_mask_dates":int(v.date.nunique()),
              "n_dated_shapefiles":len(v),"total_native_polygon_objects":int(v.n_native_guano_polygons.sum()),
              "earliest_original_mask_day":v.date.min(),"latest_original_mask_day":v.date.max(),
              "n_source_proj_CRS_EPSG":v.source_WKT_CRS_EPSG.astype(str).nunique()})
    if periods:
        pd.DataFrame(periods).to_csv(a.out/"ARDLEY_2013_2018_DATED_44_REAL_GUANO_POLYGONS_SEASON_SPECIES_SUPPORT.csv",index=False)
    rpt={"status":"ALL_44_ACTUAL_DATED_ARDLEY_GUANO_SHAPEFILES_GEOGRAPHICALLY_VALIDATED"
          if not failures and len(successes)==44 else "PARTIAL_OR_UNVERIFIED_DATED_ARDLEY_GUANO_SHAPEFILES",
      "original_provider_record":14503437,
      "original_provider_full_4GB_zip_MD5_published_only":ORIGINAL_FULL_ZIP_MD5,
      "origin_native_ZIP64_2448_file_index_verified":True,
      "guano_true_real_shapefiles_expected":44,"actual_guano_shapefiles_opened":len(successes),
      "actual_guano_shapefiles_failed":failures,
      "real_guano_geographic_metadata":successes,
      "source_spans_four_summer_seasons_2013_14_2014_15_2016_17_2017_18":True,
      "original_Youngflesh_88_Ardley_exact_ID_present":False,
      "source_masks_are_positive_GUANO_geometry_not_yet_validated_30m_OLI_binary_truth":True,
      "source_mask_date_and_CRS_must_be_aligned_to_external_L8_scene":True,
      "no_new_2013_2021_optical_delta15N_proxy_computed":True,
      "no_new_polynya_or_foodweb_relation_calculated":True,
      "original_full_4GB_not_downloaded":True}
    (a.out/"ARDLEY_NATIVE_44_GUANO_SHAPEFILE_ACTUAL_GEOGRAPHIC_GATE.json").write_text(
        json.dumps(rpt,indent=2,ensure_ascii=False,default=str)+"\n")
    print(json.dumps({"status":rpt["status"],"checked":len(successes),"failed":len(failures),
         "per_season_species":periods,"source_errors":failures[:8]},ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest-artifact-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
