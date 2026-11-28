#!/usr/bin/env python3
"""Historical Ledda source-annotation / independent physical-ice crosswalk.

Retrospective, exploratory four additional years 2009, 2010, 2012, 2013.
Original bird states already exposed BEFORE the independent ice cells.
Compares fixed LaRue and Fretwell published centroids at 1/3/5km.
15d ice mosaics allowed only when entirely finished BEFORE image date.
Does not infer breeding viability, founder movement or colonization.
"""
from __future__ import annotations

import argparse
from datetime import date,datetime,timedelta
import json
from pathlib import Path
import sys

import h5py
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import extract_fraser_ledda_frozen_2011_2014_fastice_v1 as primary
import extract_ledda_fretwell_secondary_centroid_fastice_v1 as secondary
import probe_fraser_remote_hdf5_schema_v1 as remote

EVENTS = {
    2009: {"image_date":"2009-10-27","bird_code":"no","annotator_ice":"ice_absent"},
    2010: {"image_date":"2010-10-08","bird_code":"yes","annotator_ice":"not_given_bird_detection"},
    2012: {"image_date":"2012-10-22","bird_code":"no","annotator_ice":"ice_absent"},
    2013: {"image_date":"2013-11-30","bird_code":"yes","annotator_ice":"not_given_bird_detection"},
}
RADII=(1,3,5)


def choose_preimage_indices(year,dates):
    if year not in EVENTS or len(dates)!=24 or dates!=sorted(dates) or len(set(dates))!=24:
        raise ValueError("Year or source clock outside frozen 24-bin plan")
    if any(d.year!=year for d in dates):
        raise ValueError("Mixed or wrong NetCDF year date_alt labels")
    target=date.fromisoformat(EVENTS[year]["image_date"])
    eligible=[i for i,d in enumerate(dates)
              if d>=date(year,5,1) and d+timedelta(days=14)<target]
    if len(eligible)<4 or eligible!=list(range(eligible[0],eligible[-1]+1)):
        raise ValueError("Missing or noncontiguous May-to-image calendar composites")
    if dates[eligible[-1]]+timedelta(days=14)>=target:
        raise ValueError("Postimage exposure leakage")
    return eligible


def metrics(records):
    if not records:
        raise ValueError("No seasonal physical records")
    flags=[r["class4_pixels"]>0 for r in records]
    longest=0
    running=0
    for flag in flags:
        running=running+1 if flag else 0
        longest=max(longest,running)
    trailing=0
    for flag in reversed(flags):
        if flag: break
        trailing+=1
    return {
        "n_preimage_15day_composites":len(records),
        "n_composites_with_any_class4":sum(flags),
        "longest_consecutive_composites_any_class4":longest,
        "trailing_composites_no_class4":trailing,
        "last_fully_preimage":records[-1],
        "first_fully_preimage":records[0],
        "physical_spatial_context_not_confirmed_nest_habitat":True,
    }


def one_year(year,*,file_opener=None):
    if year not in EVENTS:
        raise ValueError("Only four already exposed event years may be inspected")
    info={
        "year":year,
        "source_image":EVENTS[year],
        "status":"NOT_RUN",
        "ice_values_read":0,
        "penguin_outcome_values_read":0,
        "causal_fitted":False
    }
    physical=None
    try:
        physical=remote.LimitedHTTPRangeFile(
            remote.URL.format(year=year),
            **({"opener":file_opener} if file_opener else {})
        )
        with h5py.File(physical,"r") as f:
            ice=f["Fast_Ice_Time_series"]
            if tuple(ice.shape)!=primary.FULL_SHAPE or tuple(ice.chunks)!=primary.CHUNKS:
                raise ValueError("Unrecognized independent ice source grid")
            dates=[datetime.strptime(str(v),"%Y%m%d").date()
                   for v in np.asarray(f["date_alt"][:],dtype=int)]
            ti=choose_preimage_indices(year,dates)
            centers={
                "LaRue_original":(primary.LON,primary.LAT),
                "Fretwell_alternative":(secondary.ALT_LON,secondary.ALT_LAT)
            }
            pos={}
            for name,(lon,lat) in centers.items():
                row,col,rs,cs,masks,residual=secondary.project_cell(f,lon,lat)
                if name=="LaRue_original" and (row,col)!=(3432,1389):
                    raise ValueError("Original source geolocation changed across years")
                pos[name]={"row":row,"col":col,"rs":rs,"cs":cs,"masks":masks,"error_km":residual}
            seasonal={name:{str(r):[] for r in RADII} for name in centers}
            for t in ti:
                for name,p in pos.items():
                    slab=np.asarray(ice[t,p["rs"],p["cs"]])
                    info["ice_values_read"]+=int(slab.size)
                    for rad in RADII:
                        z=primary.summarize_mosaic(slab,p["masks"][rad])
                        if z["n_class_valid"]!=z["n_cells_spatial_mask"]:
                            raise ValueError("Unknown source pixel categories")
                        seasonal[name][str(rad)].append({
                            "time_index":t,
                            "composite_start_yyyymmdd":dates[t].strftime("%Y%m%d"),
                            "composite_end_yyyymmdd":(
                                dates[t]+timedelta(days=14)).strftime("%Y%m%d"),
                            "class4_pixels":z["n_fastice_class4"],
                            "class5_6_edge_pixels":z["n_edge_classes_5_or_6"],
                            "valid_pixels":z["n_class_valid"],
                            "class4_fraction":z["fraction_fastice_over_valid_cells"],
                            "class0_pixels":int(z["class_counts"].get("0",0))
                        })
            info.update({
                "status":"EXPLORATORY_HISTORIC_INDEPENDENT_PHYSICAL_GRID_READ",
                "source_epsg":"EPSG:3412",
                "image_date":EVENTS[year]["image_date"],
                "n_preimage_composites":len(ti),
                "original_coordinates":[primary.LAT,primary.LON],
                "alternative_coordinates":[secondary.ALT_LAT,secondary.ALT_LON],
                "centroid_grid_support":{
                    name:{"row":p["row"],"col":p["col"],"geodesic_residual_km":p["error_km"]}
                    for name,p in pos.items()
                },
                "preimage_physical_by_site_and_radius":{
                    name:{rad:metrics(records) | {"timeline":records}
                          for rad,records in by_radius.items()}
                    for name,by_radius in seasonal.items()
                },
                "biological_status_assigned_from_new_raster":False,
                "2013_late_november_not_stage_comparable_with_october":year==2013
            })
    except Exception as exc:
        info.update({"status":"HOLD_HISTORIC_PHYSICAL_SOURCE",
                     "error_type":type(exc).__name__,
                     "error_message":str(exc)[:250]})
    finally:
        info["http_range_requests"]=physical.request_count if physical else 0
        info["http_body_bytes"]=physical.bytes_network if physical else 0
        if physical: physical.close()
    return info


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    records=[one_year(year) for year in EVENTS]
    report={
        "stage":"EXPLORATORY_ALREADY_EXPOSED_BIRD_SOURCE_HISTORICAL_RASTER_CALIBRATION",
        "contract":"contracts/EMPEROR_LEDDA_2009_2010_2012_2013_AUTHOR_STATE_ICE_CALIBRATION_V1.json",
        "years":list(EVENTS),
        "source_doi":"10.26179/5d267d1ceb60c",
        "year_results":records,
        "all_years_read":all(x["status"]=="EXPLORATORY_HISTORIC_INDEPENDENT_PHYSICAL_GRID_READ" for x in records),
        "total_http_body_bytes":sum(x["http_body_bytes"] for x in records),
        "ice_source_pixel_values_read":sum(x["ice_values_read"] for x in records),
        "new_penguin_response_values_read":0,
        "confirmed_nesting_footprint_available":False,
        "social_inhibition_or_recolonization_fitted":False,
        "PR189_science_modified":False,
        "decision":"EXPLORATORY_PHYSICAL_ANCHOR_SERIES_AVAILABLE_ONLY" if all(
            x["status"]=="EXPLORATORY_HISTORIC_INDEPENDENT_PHYSICAL_GRID_READ" for x in records
        ) else "HOLD_HISTORICAL_EXTERNAL_ICE_CONTEXT"
    }
    a.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print("HISTORICAL_PHYSICAL_READOUT",report["decision"])
    for z in records:
        print("YEAR",z["year"],z["status"],z.get("error_message"))
        if z["status"]=="EXPLORATORY_HISTORIC_INDEPENDENT_PHYSICAL_GRID_READ":
            for name in ("LaRue_original","Fretwell_alternative"):
                m=z["preimage_physical_by_site_and_radius"][name]["3"]
                print("SITE_3KM",name,"season_any",m["n_composites_with_any_class4"],"/",m["n_preimage_15day_composites"],
                      "last",m["last_fully_preimage"]["class4_pixels"],"/",m["last_fully_preimage"]["valid_pixels"],
                      "longest_run",m["longest_consecutive_composites_any_class4"],
                      "trailing_zero",m["trailing_composites_no_class4"])
    print("NO_PENGUIN_SOCIAL_CAUSAL_RESULT")


if __name__=="__main__":
    main()
