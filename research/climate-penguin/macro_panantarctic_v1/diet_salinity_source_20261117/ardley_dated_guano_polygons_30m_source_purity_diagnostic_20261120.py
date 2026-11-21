#!/usr/bin/env python3
"""Independent external Ardley dated (2013-2018) guano polygon -> 30m support feasibility.

Source-only descriptive geometry diagnostic: DO NOT access colony isotope, 2013+
satellite spectral reflectance, or any penguin-polynya associations.
Source is 44 real native SHP/Shx/Dbf/Prj files in original Zenodo 14503437 ZIP64.
Landsat8 OLI's nominal 30m footprint is the motivation. This is a *nine-phase
30m UTM grid approximation* (shifts x,y in 0/10/20m), NOT the exact Landsat
scene native grid. Treat every polygon in Guano SHP as a possible guano-positive:
generous upper-bound for positive ground coverage; no independent negatives.
No p-value, threshold selection or ecological test.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile,math
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import requests,shapefile
from remotezip import RemoteZip
from pyproj import CRS
from shapely.geometry import box,shape as as_shape
from shapely.ops import unary_union

ORIGINAL_MANIFEST_SHA="ef4afd6db995ac83cdd51c798d08d00dcd729e2e39c85b096b91785cb36a6ebc"
ORIGINAL_FILELIST="ARDLEY_4GB_ORIGINAL_ZIP_MEMBER_INDEX.json"
ORIGINAL_ZENODO_ID=14503437
ORIGINAL_MD5="62bb5a89ca7f5f06e54b74e26bf5de5d"
NATIVE_ZIP_BYTES=4109917595
GUANO_RE=re.compile(r"^Guano/(\d{6})/Ardley_(\d{8})_(adelie|gentoo)\.shp$",re.I)
PIXEL_SIDE_M=30.
GRID_PHASES_M=(0.,10.,20.)
FRACTIONS=(.25,.50,.80,.95)
HEAD={"User-Agent":"mina-ardley-30m-positive-guano-source-only-raster-footprint/1.0"}

def file_index(p):
    b=Path(p).read_bytes()
    if hashlib.sha256(b).hexdigest()!=ORIGINAL_MANIFEST_SHA:
        raise ValueError("Original ZIP64 actual 2448-file listing SHA mismatch")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip(): raise ValueError("Original ZIP64 file index archive CRC failed")
        ns=[x for x in z.namelist() if x==ORIGINAL_FILELIST or x.endswith("/"+ORIGINAL_FILELIST)]
        if len(ns)!=1: raise ValueError("Original index member missing")
        members=json.loads(z.read(ns[0]))
    if len(members)!=2448: raise ValueError("Not same actual 2448-file archive")
    selected=[]
    for m in members:
        hit=GUANO_RE.fullmatch(m["path"])
        if hit:
            season,datestr,sp=hit.groups()
            selected.append({"path":m["path"],"season_bucket":season,
               "date":datestr,"species":sp.lower()})
    if len(selected)!=44:raise ValueError("Actual native 44 guano shapefile index drift")
    if len(set((x["date"],x["species"]) for x in selected))!=44:
        raise ValueError("Unexpected source duplicate dated guano shapefiles")
    return selected

def zenodo_url():
    r=requests.get(f"https://zenodo.org/api/records/{ORIGINAL_ZENODO_ID}",headers=HEAD,timeout=45)
    r.raise_for_status()
    j=r.json()
    if j.get("id")!=ORIGINAL_ZENODO_ID: raise ValueError("Original source Zenodo record drift")
    files=j["files"]
    if len(files)!=1 or files[0].get("size")!=NATIVE_ZIP_BYTES or files[0].get("checksum")!="md5:"+ORIGINAL_MD5:
        raise ValueError("Original source 4GB record bytes/MD5 changed")
    return files[0]["links"].get("content") or files[0]["links"]["self"]

def shapes_in_source(remote,inventory,entry):
    stem=entry["path"][:-4]
    files={}
    for suff in (".shp",".shx",".dbf",".prj"):
        name=stem+suff
        if name not in inventory:raise ValueError("Missing native guano polygon sidecar: "+name)
        f=inventory[name]
        if f.file_size>7_000_000:
            raise ValueError("Native shapefile unexpectedly huge")
        files[suff]=remote.read(name)
        if len(files[suff])!=f.file_size:
            raise ValueError("Native source bytes truncated")
    projection=CRS.from_wkt(files[".prj"].decode("utf-8",errors="replace"))
    if projection.to_epsg()!=32721:
        raise ValueError("Original 44 polygon CRS not original source EPSG32721")
    reader=shapefile.Reader(shp=io.BytesIO(files[".shp"]),
         shx=io.BytesIO(files[".shx"]),dbf=io.BytesIO(files[".dbf"]))
    shapes=[]
    category_flags=[]
    for rec in reader.iterShapeRecords():
        poly=as_shape(rec.shape.__geo_interface__)
        if not poly.is_valid or poly.is_empty or poly.geom_type not in ("Polygon","MultiPolygon"):
            raise ValueError("Invalid guano source geometry; never auto-repair originals")
        shapes.append(poly)
        category_flags.append({k:str(v) for k,v in rec.record.as_dict().items()})
    reader.close()
    if len(shapes)<1:raise ValueError("Actual native source dated polygon unexpectedly empty")
    merged=unary_union(shapes)
    if merged.is_empty or merged.area<=0:raise ValueError("Native guano source union area nonpositive")
    return merged,len(shapes),category_flags

def purity(geom, x_offset_m, y_offset_m):
    step=PIXEL_SIDE_M
    area=step**2
    minx,miny,maxx,maxy=geom.bounds
    ix0=math.floor((minx-x_offset_m)/step)
    ix1=math.floor((maxx-x_offset_m)/step)
    iy0=math.floor((miny-y_offset_m)/step)
    iy1=math.floor((maxy-y_offset_m)/step)
    if (ix1-ix0+1)*(iy1-iy0+1)>250_000:
        raise ValueError("Impossible positive guano polygon region bbox for native Ardley source")
    fractions=[]
    for ix in range(ix0,ix1+1):
        x0=ix*step+x_offset_m
        for iy in range(iy0,iy1+1):
            y0=iy*step+y_offset_m
            overlap=geom.intersection(box(x0,y0,x0+step,y0+step)).area
            if overlap>1.e-8:
                fract=overlap/area
                if fract>1+1e-8:
                    raise ValueError("Geometry overlap fraction exceeds pixel")
                fractions.append(min(fract,1.))
    return {
      "positive_touched_30m_cells":len(fractions),
      "maximum_fraction_of_any_30m_cell_covered_by_source_guano_polygon":
       float(max(fractions)) if fractions else 0.,
      "n_pixels_fraction_ge_25pct":int(sum(x>=.25 for x in fractions)),
      "n_pixels_fraction_ge_50pct":int(sum(x>=.50 for x in fractions)),
      "n_pixels_fraction_ge_80pct":int(sum(x>=.80 for x in fractions)),
      "n_pixels_fraction_ge_95pct":int(sum(x>=.95 for x in fractions)),
      "effective_total_guano_area_equivalent_30m_pixels":float(sum(fractions)),
      "pixel_grid_UTM_x_origin_phase_m":x_offset_m,
      "pixel_grid_UTM_y_origin_phase_m":y_offset_m,
    }

def main(a):
    entries=file_index(a.original_manifest_zip)
    url=zenodo_url()
    shape_rows=[]
    source_geometries=defaultdict(dict)
    with RemoteZip(url) as z:
        lookup={x.filename:x for x in z.infolist() if not x.is_dir()}
        if len(lookup)!=2448: raise ValueError("Full original remote ZIP64 source member manifest changed")
        for i,entry in enumerate(sorted(entries,key=lambda x:(x["date"],x["species"]))):
            geom,n,flags=shapes_in_source(z,lookup,entry)
            source_geometries[entry["date"]][entry["species"]]=geom
            shape_rows.append({**entry,"n_true_source_polygons":n,
               "positive_mask_union_m2":float(geom.area),
               "feature_flag_names":sorted(set().union(*(set(f) for f in flags)))})
            if i%5==0:print(f"NATIVE_MASKS_READ {i+1}/{len(entries)}",flush=True)
    if len(source_geometries)!=22 or any(set(v)!={"adelie","gentoo"} for v in source_geometries.values()):
        raise ValueError("Unexpected original 22 separate dates each containing both 2 species")
    grids=[]
    for date,byspecies in sorted(source_geometries.items()):
        u=unary_union(list(byspecies.values()))
        if u.area<=0:raise ValueError("Zero combined actual positive guano area")
        for label,geom in sorted([("all_penguin_guano_candidate",u)]+list(byspecies.items())):
            for x in GRID_PHASES_M:
                for y in GRID_PHASES_M:
                    g=purity(geom,x,y)
                    grids.append({"date":date,"species_or_combined":label,
                        "positive_source_guano_polygon_m2":float(geom.area),
                        **g})
    df=pd.DataFrame(grids)
    src=pd.DataFrame(shape_rows)
    summaries=[]
    for key,group in df.groupby("species_or_combined",sort=True):
        source_dates=group.groupby("date",sort=True).agg(
           positive_union_m2=("positive_source_guano_polygon_m2","first"),
           max_of_9_phase_any_30m_pixel_fraction=("maximum_fraction_of_any_30m_cell_covered_by_source_guano_polygon","max"),
           min_of_9_phase_any_30m_pixel_fraction=("maximum_fraction_of_any_30m_cell_covered_by_source_guano_polygon","min"),
           min_pure_80pct_pixels_over_grid_phases=("n_pixels_fraction_ge_80pct","min"),
           max_pure_80pct_pixels_over_grid_phases=("n_pixels_fraction_ge_80pct","max"),
           min_pure_50pct_pixels_over_grid_phases=("n_pixels_fraction_ge_50pct","min"),
           max_pure_50pct_pixels_over_grid_phases=("n_pixels_fraction_ge_50pct","max")
        ).reset_index()
        for d in source_dates.to_dict("records"):
            summaries.append({"species_or_combined":key,**d})
    sm=pd.DataFrame(summaries)
    a.out.mkdir(parents=True,exist_ok=True)
    src.to_csv(a.out/"ARDLEY_44_SOURCE_GUANO_POLYGON_AREA_DATES_SPECIES_NO_Y.csv",index=False)
    df.to_csv(a.out/"ARDLEY_22DATES_THREE_CLASSES_9PHASES_NOMINAL30M_POLYGON_PURITY_NO_Y.csv",index=False)
    sm.to_csv(a.out/"ARDLEY_22DATES_SPECIES_BOUND_30M_GEOMETRIC_COVERAGE_NO_Y.csv",index=False)
    outcome=[]
    for kind,g in sm.groupby("species_or_combined",sort=True):
        outcome.append({
           "source_species_or_union":kind,
           "n_true_independent_source_dates":int(len(g)),
           "guano_area_m2_min_median_max":[float(g.positive_union_m2.min()),
               float(g.positive_union_m2.median()),float(g.positive_union_m2.max())],
           "n_dates_with_zero_80pct_pure_pixels_all_9_UTM_phases":int((g.max_pure_80pct_pixels_over_grid_phases==0).sum()),
           "n_dates_with_at_least_one_80pct_pure_pixel_any_UTM_phase":int((g.max_pure_80pct_pixels_over_grid_phases>0).sum()),
           "n_dates_with_zero_50pct_pure_pixels_all_9_UTM_phases":int((g.max_pure_50pct_pixels_over_grid_phases==0).sum()),
           "max_possible_guano_pixel_fraction_grid_phase_9_median":float(g.max_of_9_phase_any_30m_pixel_fraction.median()),
           "median_max_purity_over_all_phases":float(g.min_of_9_phase_any_30m_pixel_fraction.median()),
        })
    rec={
       "status":"REAL_44_ARDLEY_GUANO_SHAPEFILES_22DATES_NOMINAL_30M_PURITY_GEOMETRIC_SOURCE_AUDIT",
       "zenodo_original_4GB_MD5_metadata_only":ORIGINAL_MD5,
       "all_44_real_native_guano_shapefiles_read":True,
       "actual_true_source_species":["adelie","gentoo"],
       "real_native_GIS_EPSG":32721,
       "actual_independent_source_dates":sorted(source_geometries.keys()),
       "30m_nominal_L8_pixel_area_m2":900,
       "grid_IS_NOT_TRUE_NATIVE_L8_ALIGNED":True,
       "grid_UTM_phases_each_axis_m":list(GRID_PHASES_M),
       "n_source_date_species_phase_rows":len(df),
       "treat_source_Guano_geometry_as_generous_positive_upper_bound":True,
       "quantitative_support_by_class":outcome,
       "no_independent_negative_rocks_snow_ice_labels_verified":True,
       "site_Ardley_not_in_original_88_isotope_sites":True,
       "new_2013_2021_L8_optical_delta15N_not_opened":True,
       "new_coastal_polynya_ecological_effect_not_fitted":True,
       "not_a_true_L8_sensor_classifier_accuracy_estimate":True
    }
    (a.out/"ARDLEY_22DATES_TRUE_GUANO_GEOMETRY_30M_MIXED_PIXEL_SUPPORT_REPORT.json").write_text(
        json.dumps(rec,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(rec,indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-manifest-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
