"""Precommitted alternative published Ledda centroid, sensitivity only.

Fretwell et al. 2021 Table 2: -74.272 -131.243 (doi:10.1002/rse2.176).
Compare the SAME 2011 / 2014 frozen Fraser/Massom 15-day composites and
1/3/5km spatial radii as PR195's earlier LaRue-centroid primary extraction.
This must NOT be used to choose the more favorable centroid after results.
No penguin outcome data, migration or social/causal model is read or fitted.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys

import h5py
import numpy as np
from pyproj import Transformer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_fraser_ledda_frozen_2011_2014_fastice_v1 as primary
import probe_fraser_remote_hdf5_schema_v1 as remote

ALT_LAT=-74.272
ALT_LON=-131.243
PRIMARY_LAT=primary.LAT
PRIMARY_LON=primary.LON
YEARS=primary.YEARS
RADII=primary.SPATIAL_RADII
EPSG="EPSG:3412"
WINDOW_HALF_WIDTH=7


def is_frozen_plan():
    return (YEARS==(2011,2014) and RADII==(1,3,5)
            and primary.FROZEN_YEAR[2011]["primary_t"]==16
            and primary.FROZEN_YEAR[2014]["primary_t"]==18
            and primary.FROZEN_YEAR[2011]["overlap_t"]==17
            and primary.FROZEN_YEAR[2014]["overlap_t"]==19
            and 14<primary.haversine_km(PRIMARY_LAT,PRIMARY_LON,ALT_LAT,ALT_LON)<16)


def project_cell(f, lon, lat):
    xx,yy=Transformer.from_crs("EPSG:4326",EPSG,always_xy=True).transform(lon,lat)
    x=np.asarray(f["x"][:],dtype=float)
    y=np.asarray(f["y"][:],dtype=float)
    if x.ndim!=1 or y.ndim!=1 or len(x)!=5625 or len(y)!=4700:
        raise ValueError("Unexpected physical-grid coordinate axes")
    col=int(np.argmin(np.abs(x-xx)))
    row=int(np.argmin(np.abs(y-yy)))
    residual=primary.haversine_km(
        lat,lon,float(f["latitude"][row,col]),float(f["longitude"][row,col]))
    if residual>3 or not np.isfinite(residual):
        raise ValueError("Alternative centroid cannot be geolocated on frozen source grid")
    rs=slice(row-WINDOW_HALF_WIDTH,row+WINDOW_HALF_WIDTH+1)
    cs=slice(col-WINDOW_HALF_WIDTH,col+WINDOW_HALF_WIDTH+1)
    grid_x,grid_y=np.meshgrid(x[cs],y[rs])
    d=np.hypot(grid_x-xx,grid_y-yy)
    masks={radius:d<=radius*1000 for radius in RADII}
    if any(not m.any() for m in masks.values()):
        raise ValueError("No grid cell in some fixed spatial radius")
    return row,col,rs,cs,masks,residual


def read_one_year(year,*,file_opener=None):
    if not is_frozen_plan():
        raise ValueError("Primary frozen year/time/radius plan changed; no silent adaptation")
    if year not in YEARS:
        raise ValueError("Only original frozen year pair allowed")
    info={"year":year,"status":"NOT_RUN","physical_ice_values_read":0,
          "penguin_rows_read":0,"causal_or_social_effect_fitted":False}
    remote_file=None
    try:
        remote_file=remote.LimitedHTTPRangeFile(
            remote.URL.format(year=year),
            **({"opener":file_opener} if file_opener else {}))
        with h5py.File(remote_file,"r") as f:
            ice=f["Fast_Ice_Time_series"]
            if tuple(ice.shape)!=primary.FULL_SHAPE or tuple(ice.chunks)!=primary.CHUNKS:
                raise ValueError("Not the frozen 2011/2014 source grid")
            time=primary.FROZEN_YEAR[year]
            date_alt=np.asarray(f["date_alt"][:],dtype=int)
            if (len(date_alt)!=24 or int(date_alt[time["primary_t"]])!=time["primary_date_alt"]
                or int(date_alt[time["overlap_t"]])!=time["overlap_date_alt"]):
                raise ValueError("Alternative location source/composite time mismatch")
            row,col,rs,cs,masks,residual=project_cell(f,ALT_LON,ALT_LAT)
            chosen=sorted(set(time["preimage_indices"]+(time["overlap_t"],)))
            records=[]
            for t in chosen:
                slab=np.asarray(ice[t,rs,cs])
                info["physical_ice_values_read"]+=int(slab.size)
                results={str(radius):primary.summarize_mosaic(slab,masks[radius]) for radius in RADII}
                records.append({
                    "time_index":t,
                    "composite_start_yyyymmdd":int(date_alt[t]),
                    "primary_preimage":t==time["primary_t"],
                    "overlaps_or_follows_original_image":t==time["overlap_t"],
                    "radius_summaries_km":results
                })
            info.update({
                "status":"ALTERNATIVE_PUBLISHED_CENTROID_ICE_PIXEL_CONTEXT_READ",
                "alternative_coord":[ALT_LAT,ALT_LON],
                "primary_coord":[PRIMARY_LAT,PRIMARY_LON],
                "centroid_distance_km":primary.haversine_km(PRIMARY_LAT,PRIMARY_LON,ALT_LAT,ALT_LON),
                "grid_row":row,"grid_col":col,
                "grid_geodesic_residual_km":residual,
                "source_projection":EPSG,
                "preimage_t_index":time["primary_t"],
                "image_overlapping_sensitivity_t_index":time["overlap_t"],
                "record_count":len(records),
                "composite_records":records,
                "nest_footprint_verified":False,
                "historical_colony_moved_14km_verified":False
            })
    except Exception as e:
        info.update({"status":"HOLD_SECONDARY_LOCATION_FASTICE",
                     "error_type":type(e).__name__,
                     "error_message":str(e)[:250]})
    finally:
        info["http_range_requests"]=remote_file.request_count if remote_file else 0
        info["http_body_bytes"]=remote_file.bytes_network if remote_file else 0
        if remote_file: remote_file.close()
    return info


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    results=[read_one_year(y) for y in YEARS]
    both=all(r["status"]=="ALTERNATIVE_PUBLISHED_CENTROID_ICE_PIXEL_CONTEXT_READ" for r in results)
    report={
        "status":"SECONDARY_ICE_GRID_READ_FOR_COORDINATE_SENSITIVITY_ONLY" if both else "HOLD_SECONDARY_GRID",
        "contract":"contracts/EMPEROR_LEDDA_TWO_CENTROID_SENSITIVITY_PRE_ICE_V1.json",
        "source_doi":primary.SOURCE_DOI,
        "source_years":list(YEARS),
        "secondary_site":[ALT_LAT,ALT_LON],
        "comparison_centroid":[PRIMARY_LAT,PRIMARY_LON],
        "year_results":results,
        "all_years_secondary_source_read":both,
        "total_network_bytes":sum(z["http_body_bytes"] for z in results),
        "new_penguin_response_rows_read":0,
        "full_breeding_viability_confirmed":False,
        "inferred_social_interaction_or_colony_migration":False,
        "primary_protocol_changed":False,
        "PR189_science_modified":False
    }
    output=json.dumps(report,indent=2)+"\n"
    a.out.write_text(output,encoding="utf8")
    print("SECONDARY_COORDINATE_ICE_DECISION",report["status"])
    for r in results:
        print("YEAR",r["year"],r["status"],
              "BYTES",r["http_body_bytes"],"ERROR",r.get("error_message"))
    print("NO_CAUSAL_RESULT")


if __name__=="__main__":
    main()
