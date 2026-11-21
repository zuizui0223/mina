#!/usr/bin/env python3
"""Original Copernicus GLORYS12V1 Sep-2011 wet-grid match for 595 real colonies.

This source-gating pilot only maps physical ocean grid availability, not
breeding suitability, penguin absence, or climatic response. Uses the exact
original source product and checks the earlier frozen 40-site wet-cell map.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import fsspec
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Geod
from scipy.spatial import cKDTree

EXPECTED_BLOBS = {
    "marine_manifest": "7d62ce17e77ae356ea62116d2446b0a8521c7ded",
    "original_40_grid": "5d0f90cab39e192645b3ff3406a40349a0ff22d0"
}
EXPECTED_SOURCE = "https://s3.waw3-1.cloudferro.com/mdl-arco-time-025/arco/GLOBAL_MULTIYEAR_PHY_001_030/cmems_mod_glo_phy_my_0.083deg_P1M-m_202311/timeChunked.zarr"
KNOWN_MARINE_MACRO_COUNT = 40
KNOWN_MACRO_GOOD = 34
SOURCE_SITE_COUNT = 595
DISTANCE_KM = 25.0
SOURCE_YEAR, SOURCE_MONTH = 2011, 9
SOURCE_SAL_MIN, SOURCE_SAL_MAX = 20, 42
MARINE_CANDIDATES = 12


def readcsv(path):
    with path.open(encoding="utf-8",newline="") as src:
        return list(csv.DictReader(src))


def writecsv(path,records):
    cols=list(dict.fromkeys(k for r in records for k in r))
    with path.open("w",encoding="utf-8",newline="") as fp:
        w=csv.DictWriter(fp,fieldnames=cols)
        w.writeheader()
        w.writerows(records)


def pinned(path,expected):
    raw=path.read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha!=expected:
        raise ValueError(f"Original published GLORYS metadata Git blob changed: {path} expected {expected}, got {sha}")
    return raw


def xyz(lat,lon):
    lat=np.deg2rad(np.asarray(lat,dtype=float))
    lon=np.deg2rad(np.asarray(lon,dtype=float))
    return np.column_stack((np.cos(lat)*np.cos(lon),
                            np.cos(lat)*np.sin(lon),
                            np.sin(lat)))


def nearest_wet(source_sites,wet_y,wet_x,wet_lat,wet_lon):
    if not (len(wet_y)==len(wet_x)==len(wet_lat)==len(wet_lon)):
        raise ValueError("Original gridded marine wet coordinate arrays do not align")
    if len(wet_y)<MARINE_CANDIDATES:
        raise ValueError("Native wet marine point set too small for candidate geodesic check")
    geod=Geod(ellps="WGS84")
    unit=xyz(wet_lat,wet_lon)
    tree=cKDTree(unit)
    coords=xyz([float(r["latitude"]) for r in source_sites],
               [float(r["longitude"]) for r in source_sites])
    _,indexes=tree.query(coords,k=MARINE_CANDIDATES)
    output=[]
    for site,neighbors in zip(source_sites,np.atleast_2d(indexes)):
        idx=np.asarray(neighbors,dtype=int)
        latitude=float(site["latitude"])
        longitude=float(site["longitude"])
        # KD tree uses 3D spherical chord only for candidates; true distance
        # and nearest selection are WGS84 geodesic, including 180° wrap.
        az,back,metres=geod.inv(
            np.full(len(idx),longitude),np.full(len(idx),latitude),
            wet_lon[idx],wet_lat[idx])
        order=np.lexsort((wet_x[idx],wet_y[idx],metres))
        best=int(idx[order[0]])
        distance=float(metres[order[0]]/1000)
        output.append({
            "site_id":site["site_id"],
            "source_region":site["source_region"],
            "source_250km_block":site["polar_250km_fixed_grid_block"],
            "colony_latitude":latitude,"colony_longitude":longitude,
            "original_glorys_grid_y":int(wet_y[best]),
            "original_glorys_grid_x":int(wet_x[best]),
            "original_glorys_latitude":float(wet_lat[best]),
            "original_glorys_longitude":float(wet_lon[best]),
            "true_geodesic_source_cell_distance_km":distance,
            "source_wet_2011_september_25km_gate":distance<=DISTANCE_KM,
            "wet_cell_selected_using_observed_colony_counts_or_future_outcome":False,
        })
    return output


def run(args):
    original=json.loads(pinned(args.manifest,EXPECTED_BLOBS["marine_manifest"]))
    if original["store"]!=EXPECTED_SOURCE or original["version"]!="202311":
        raise ValueError("Original GLORYS 202311 Copernicus store identity drift")
    atlas=readcsv(args.atlas)
    ref=readcsv(args.old40)
    pinned(args.old40,EXPECTED_BLOBS["original_40_grid"])
    if len(atlas)!=SOURCE_SITE_COUNT or len({r["site_id"] for r in atlas})!=SOURCE_SITE_COUNT:
        raise ValueError("Original 595 site atlas changed or duplicates")
    macro=[r for r in ref if r["cohort"]=="macro_40"]
    if len(macro)!=KNOWN_MARINE_MACRO_COUNT or len({r["site_id"] for r in macro})!=KNOWN_MARINE_MACRO_COUNT:
        raise ValueError("Original 40 source macro wet-grid reference changed")
    if len([r for r in macro if r["grid_within_25km"]=="True"])!=KNOWN_MACRO_GOOD:
        raise ValueError("Original 34 macro wet-grid source support changed")

    print("OPEN ORIGINAL COPERNICUS SOURCE " + original["store"],flush=True)
    ds=xr.open_zarr(fsspec.get_mapper(original["store"]),consolidated=True)
    for name in ("latitude","longitude","time","elevation","so"):
        if name not in ds.variables:
            raise ValueError("Original Copernicus GLORYS native coordinate or salinity field missing "+name)
    time=pd.DatetimeIndex(ds.time.values)
    selection=np.flatnonzero((time.year==SOURCE_YEAR)&(time.month==SOURCE_MONTH))
    if len(selection)!=1:
        raise ValueError("Original 2011 Sep GLORYS monthly source date missing")
    elevation_idx=int(np.argmin(np.abs(ds.elevation.values)))
    surface_depth=float(ds.elevation.values[elevation_idx])
    if abs(surface_depth-float(original["top_level_coordinate_m"]))>1e-5:
        raise ValueError("Original GLORYS source top level depth differs")
    lat_values=np.asarray(ds.latitude.values)
    lon_values=np.asarray(ds.longitude.values)
    if lat_values.ndim!=1 or lon_values.ndim!=1 or not np.all(np.diff(lat_values)>0):
        raise ValueError("Original source native marine latitude/longitude axes changed")
    shore_lat=np.asarray([float(r["latitude"]) for r in atlas])
    if shore_lat.min()<=lat_values.min() or shore_lat.max()>=lat_values.max():
        raise ValueError("Antarctic colony site outside original GLORYS marine coordinate limits")
    lat_max_idx=int(np.flatnonzero(lat_values<=-53)[-1])
    # One fixed original marine 2D mask for the whole Southern Ocean:
    # no reading one large chunk per colony in this source discovery pass.
    field=ds["so"].isel(
        time=int(selection[0]),elevation=elevation_idx,
        latitude=slice(0,lat_max_idx+1)).load()
    array=np.asarray(field.values,dtype=np.float64)
    if array.shape!=(lat_max_idx+1,len(lon_values)):
        raise ValueError("Original GLORYS latitude/longitude 2D wet mask shape unexpected")
    wet=np.isfinite(array)&(array>=SOURCE_SAL_MIN)&(array<=SOURCE_SAL_MAX)
    yi,xi=np.nonzero(wet)
    if len(yi)<500:
        raise ValueError("Antarctic source marine mask too sparse")
    pos=nearest_wet(atlas,yi.astype(np.int32),xi.astype(np.int32),
                    lat_values[yi],lon_values[xi])
    bysite={r["site_id"]:r for r in pos}
    frozen_match=[]
    for row in macro:
        z=bysite[row["site_id"]]
        selected=(z["original_glorys_grid_y"],z["original_glorys_grid_x"])
        prior=(int(row["grid_y"]),int(row["grid_x"]))
        diff=float(z["true_geodesic_source_cell_distance_km"])-float(row["grid_distance_km"])
        exact_cells=selected==prior
        source_decision=z["source_wet_2011_september_25km_gate"]
        old_decision=row["grid_within_25km"]=="True"
        frozen_match.append({
            "site_id":row["site_id"],
            "old_native_grid_y":prior[0],"old_native_grid_x":prior[1],
            "new_native_grid_y":selected[0],"new_native_grid_x":selected[1],
            "old_nearest_wet_distance_km":float(row["grid_distance_km"]),
            "new_true_geodesic_distance_km":float(z["true_geodesic_source_cell_distance_km"]),
            "distance_difference_km":diff,
            "source_native_grid_cell_identity_matched":exact_cells,
            "source_within_25km_gate_matched":source_decision==old_decision
        })
    original34=[r for r in frozen_match if next(x["grid_within_25km"]=="True"
                       for x in macro if x["site_id"]==r["site_id"])]
    if not all(r["source_native_grid_cell_identity_matched"] for r in original34):
        bad=[r for r in original34 if not r["source_native_grid_cell_identity_matched"]]
        raise ValueError("Original 34 wet-cell IDs changed relative to confirmed GLORYS source: "+
                         json.dumps(bad[:8]))
    if not all(r["source_within_25km_gate_matched"] for r in frozen_match):
        raise ValueError("Original 40 source GLORYS wet-distance 25km gate changed")
    counted=Counter(r["source_region"] for r in pos if r["source_wet_2011_september_25km_gate"])
    full_counts=Counter(r["source_region"] for r in pos)
    result={
        "status":"GLORYS_202311_ORIGINAL_595_ANTARCTIC_NEAREST_WET_GRID_COVERAGE_SOURCE_VERIFIED",
        "original_site_count":SOURCE_SITE_COUNT,
        "original_region_count":len(full_counts),
        "source_2011_September_native_wet_cells_n":len(yi),
        "source_GLORYS_surface_depth_m":surface_depth,
        "source_Copernicus_product":original["product"],
        "source_Copernicus_version":original["version"],
        "source_manifest_git_blob":EXPECTED_BLOBS["marine_manifest"],
        "source_ocean_reference_40_site_grid_git_blob":EXPECTED_BLOBS["original_40_grid"],
        "baseline_source_date":"2011-09",
        "eligible_max_geodesic_distance_km":DISTANCE_KM,
        "n_original_sites_within_25km":sum(r["source_wet_2011_september_25km_gate"] for r in pos),
        "n_source_regions_within_25km":len(counted),
        "source_sites_per_region_eligible":dict(sorted(counted.items())),
        "source_sites_per_region_total":dict(sorted(full_counts.items())),
        "n_original_40_source_cells_reproduced":sum(r["source_native_grid_cell_identity_matched"] for r in frozen_match),
        "n_original_34_source_valid_cells_reproduced":sum(r["source_native_grid_cell_identity_matched"] for r in original34),
        "n_original_40_distance_support_decisions_reproduced":sum(r["source_within_25km_gate_matched"] for r in frozen_match),
        "excluded_site_codes_by_region":{
            region: [r["site_id"] for r in pos if
                    r["source_region"]==region and not r["source_wet_2011_september_25km_gate"]]
            for region in sorted(full_counts)},
        "original_source_595_site_geo_and_species_count_frame_unmodified":True,
        "no_penquins_or_breeding_sites_assumed_absent_outside_25km":True,
        "not_a_biological_recruitment_or_foraging_footprint_model":True,
    }
    args.out.mkdir(parents=True,exist_ok=True)
    writecsv(args.out/"all_original_595_sites_frozen_GLORYS_nearest_2011_September_wet_ocean_cells.csv",pos)
    writecsv(args.out/"original_40_known_GLORYS_source_pixel_crosscheck.csv",frozen_match)
    (args.out/"595_source_GLORYS_wet_grid_geographic_coverage.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("GLORYS_595_SOURCE_WET_GRID_2011_09="+json.dumps(result,ensure_ascii=False),flush=True)
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--atlas",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--old40",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    run(ap.parse_args())
