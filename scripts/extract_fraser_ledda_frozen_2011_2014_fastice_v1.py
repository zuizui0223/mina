"""Source-independent fast-ice measurement at frozen Ledda Bay 2011/2014.

This reads exact preselected 15-day MODIS mosaics (2011 t=16, 2014 t=18)
and a frozen May→preimage time window plus an image-overlapping sensitivity
(t=17 and 19, explicitly NOT a pre-decision exposure).

All sample locations are fixed from the WGS84 Ledda colony centroid and
independent EPSG:3412 x/y plus published lat/lon, NOT bird detections.
No new penguin rows and NO inferential ecology/p-values.
Remote uses HTTP 206 chunked HDF5 range reads, <=20MiB per year.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys

import h5py
import numpy as np
from pyproj import Transformer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_fraser_remote_hdf5_schema_v1 as remote

SITE_ID="LEDD"
LAT=-74.228
LON=-130.784
EPSG="EPSG:3412"
SOURCE_DOI="10.26179/5d267d1ceb60c"
SOURCE_GRID_CLASS4=4
YEARS=(2011,2014)
FULL_SHAPE=(24,4700,5625)
CHUNKS=(4,784,938)
SPATIAL_RADII=(1,3,5)
PRIMARY_RADIUS_KM=3
WINDOW_HALF_WIDTH=7
FROZEN_YEAR={
    2011:{"image_date":"2011-09-23","primary_t":16,"overlap_t":17,
          "primary_date_alt":20110829,"overlap_date_alt":20110913,
          "preimage_indices":tuple(range(8,17))},
    2014:{"image_date":"2014-10-13","primary_t":18,"overlap_t":19,
          "primary_date_alt":20140928,"overlap_date_alt":20141013,
          "preimage_indices":tuple(range(8,19))},
}


def haversine_km(a,b,c,d):
    p=math.pi/180
    z=(math.sin((c-a)*p/2)**2
       +math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2)
    return 6371.0088*2*math.asin(min(1,math.sqrt(max(0,z))))


def summarize_mosaic(arr:np.ndarray,mask:np.ndarray)->dict:
    if arr.shape != mask.shape:
        raise ValueError("Spatial ice subset and fixed radius mask disagree")
    values=np.asarray(arr[mask],dtype=np.int16)
    if values.size==0:
        raise ValueError("No valid grid centers inside fixed radius")
    allcounts={str(int(v)):int(n) for v,n in
               zip(*np.unique(values,return_counts=True))}
    recognized=np.isin(values,[0,1,2,3,4,5,6])
    marine=np.isin(values,[0,4,5,6])
    n_all=int(values.size)
    n_valid=int(recognized.sum())
    n_marine=int(marine.sum())
    n_fast=int((values==4).sum())
    n_edges=int(np.isin(values,[5,6]).sum())
    return{
        "n_cells_spatial_mask":n_all,
        "class_counts":allcounts,
        "n_class_valid":n_valid,
        "n_marine_classes_0_4_5_6":n_marine,
        "n_fastice_class4":n_fast,
        "n_edge_classes_5_or_6":n_edges,
        "fraction_fastice_over_valid_cells":n_fast/n_valid if n_valid else None,
        "fraction_fastice_over_marine_and_edge":n_fast/n_marine if n_marine else None,
        "fraction_any_fastice":bool(n_fast>0),
        "n_unknown_or_fill":n_all-n_valid,
    }


def read_one_year(year:int,*,file_opener=None)->dict:
    if year not in YEARS:
        raise ValueError("Year not in independently frozen comparison")
    timing=FROZEN_YEAR[year]
    info={
        "year":year,
        "site":SITE_ID,
        "author_image_date":timing["image_date"],
        "primary_preimage_index":timing["primary_t"],
        "same_bin_overlap_sensitivity_index":timing["overlap_t"],
        "status":"NOT_RUN",
        "physical_ice_pixel_values_read":0,
        "penguin_values_opened":0,
        "causal_model_fit":False,
    }
    remoteio=None
    try:
        remoteio=remote.LimitedHTTPRangeFile(
            remote.URL.format(year=year),
            **({"opener":file_opener} if file_opener else {})
        )
        with h5py.File(remoteio,"r") as f:
            ice=f["Fast_Ice_Time_series"]
            if tuple(ice.shape)!=FULL_SHAPE or tuple(ice.chunks)!=CHUNKS:
                raise ValueError("Unexpected frozen physical ice HDF5 schema")
            x=np.asarray(f["x"][:],dtype=float)
            y=np.asarray(f["y"][:],dtype=float)
            dates=np.asarray(f["date_alt"][:],dtype=int)
            if len(dates)!=24 or int(dates[timing["primary_t"]])!=timing["primary_date_alt"] or int(dates[timing["overlap_t"]])!=timing["overlap_date_alt"]:
                raise ValueError("Frozen preimage composite calendar mismatch")
            X,Y=Transformer.from_crs("EPSG:4326",EPSG,always_xy=True).transform(LON,LAT)
            r=int(np.argmin(np.abs(y-Y)))
            c=int(np.argmin(np.abs(x-X)))
            if (r,c)!=(3432,1389):
                raise ValueError("Author-independent coordinate mapping differs from frozen valid grid")
            lat_grid=float(f["latitude"][r,c])
            lon_grid=float(f["longitude"][r,c])
            residual=haversine_km(LAT,LON,lat_grid,lon_grid)
            if residual>3:
                raise ValueError("Independent latlon grid residual exceeds 3km")
            rs=slice(r-WINDOW_HALF_WIDTH,r+WINDOW_HALF_WIDTH+1)
            cs=slice(c-WINDOW_HALF_WIDTH,c+WINDOW_HALF_WIDTH+1)
            xx,yy=np.meshgrid(x[cs],y[rs])
            distance=np.hypot(xx-X,yy-Y)
            masks={radius: distance<=radius*1000 for radius in SPATIAL_RADII}
            if any(not m.any() for m in masks.values()):
                raise ValueError("No center cells inside radius")

            # NOTE only these PRE-COMMITTED index sets are permitted to open
            # actual physical landfast ice values in this scientific lane.
            chosen=sorted(set(timing["preimage_indices"]+(timing["overlap_t"],)))
            records=[]
            for t in chosen:
                slab=ice[t,rs,cs]
                info["physical_ice_pixel_values_read"]+=slab.size
                if slab.shape != distance.shape:
                    raise ValueError("Missing spatial part of chunk")
                hist={str(radius):summarize_mosaic(slab,masks[radius]) for radius in SPATIAL_RADII}
                records.append({
                    "time_index":t,
                    "composite_start_yyyymmdd":int(dates[t]),
                    "overlaps_or_follows_original_image":t==timing["overlap_t"],
                    "primary_preimage":t==timing["primary_t"],
                    "radius_summaries_km":hist,
                })
            pre=[z for z in records if z["time_index"] in timing["preimage_indices"]]
            seasonal={}
            for radius in SPATIAL_RADII:
                series=[z["radius_summaries_km"][str(radius)] for z in pre]
                fractions=[a["fraction_fastice_over_valid_cells"] for a in series]
                seasonal[str(radius)]={
                    "n_preimage_composites":len(series),
                    "n_with_any_fastice":sum(a["fraction_any_fastice"] for a in series),
                    "fastice_frac_valid_mean":(
                        float(np.mean([v for v in fractions if v is not None]))
                        if any(v is not None for v in fractions) else None
                    ),
                    "fastice_frac_valid_min":(
                        float(min(v for v in fractions if v is not None))
                        if any(v is not None for v in fractions) else None
                    ),
                    "fastice_frac_valid_max":(
                        float(max(v for v in fractions if v is not None))
                        if any(v is not None for v in fractions) else None
                    ),
                }
            info.update({
                "status":"EXPLORATORY_INDEPENDENT_FASTICE_GRID_EXTRACTED",
                "grid_row":r,"grid_col":c,
                "source_epsg":EPSG,
                "frozen_site_geographic_residual_km":residual,
                "x_grid_spacing_m":float(abs(np.median(np.diff(x)))),
                "y_grid_spacing_m":float(abs(np.median(np.diff(y)))),
                "n_radius_cells":{str(v):int(m.sum()) for v,m in masks.items()},
                "year_date_alt":dates.tolist(),
                "composite_records":records,
                "preimage_season_summaries":seasonal,
            })
    except Exception as e:
        info["status"]="HOLD_FAILED_ICE_EXTRACTION"
        info["error_type"]=type(e).__name__
        info["error_message"]=str(e)[:250]
    finally:
        info["http_range_requests"]=remoteio.request_count if remoteio else 0
        info["http_body_bytes"]=remoteio.bytes_network if remoteio else 0
        if remoteio:
            remoteio.close()
    return info


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data=[read_one_year(y) for y in YEARS]
    report={
        "audit_id":"ledda-independent-modis-fastice-2011-2014-physical-cell-v1",
        "date":"2026-10-08",
        "contract":"contracts/EMPEROR_LEDDA_2011_2014_INDEPENDENT_FASTICE_PIXELS_V1.json",
        "external_source":"https://doi.org/"+SOURCE_DOI,
        "already_exposed_author_bird_states":{"2011":"fast ice available; birds not seen",
                                              "2014":"fast ice available; birds not seen"},
        "source_years":list(YEARS),
        "year_results":data,
        "both_years_physical_classes_retrieved":all(
            a["status"]=="EXPLORATORY_INDEPENDENT_FASTICE_GRID_EXTRACTED" for a in data),
        "total_http_body_bytes":sum(a["http_body_bytes"] for a in data),
        "total_ice_source_pixel_values_read":sum(a["physical_ice_pixel_values_read"] for a in data),
        "new_penguin_response_rows_opened":0,
        "causal_effect_or_social_displacement_fitted":False,
        "important_caveats":[
            "Selected two pre-exposed author-image negatives within one original Ledda site.",
            "15-day maps are composites; preimage t indexes are the last FINISHED composites before original image.",
            "Same-bin overlap index includes days after the image and cannot be a before-choice treatment.",
            "Landfast ice class at rounded centroid does not prove physical nest-site platform or full breeding season.",
            "No directly observed successful breeding, marked arrivals, social inhibition or neighbor rescue effects."
        ],
        "decision":(
            "INDEPENDENT_PHYSICAL_FASTICE_DESCRIPTIVE_EVIDENCE_AVAILABLE_ONLY"
            if all(a["status"]=="EXPLORATORY_INDEPENDENT_FASTICE_GRID_EXTRACTED" for a in data)
            else "HOLD_INDEPENDENT_PHYSICAL_FASTICE_EXTRACTION"
        )
    }
    payload=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    args.out.write_text(payload,encoding="utf8")
    print(payload,end="")


if __name__=="__main__":
    main()
