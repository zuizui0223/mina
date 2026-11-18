"""Source-fixed 4-tag Chinstrap TDR candidate-dive GPS cells x BAS krill GAM.

2026-10-31, observational instrument+geometry pilot ONLY. Original TDR ZOC
method requires external sensor calibration; pressure-defined events are not
verified foraging/krill capture. Published Freer GAM shares training acoustics,
sea ice and salinity with our historical analyses; never an independent
ecological mechanism validation or climate-to-breeding forecast.

All four fixed source IDs and all four offset x 2/5/10 dbar combinations are
retained, no preferred result selection. No raw animal coordinates or
pressure series published, only per-tag count/geometry/exposure summaries.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
import chinstrap_tdr_pressure_gps_pilot_v1 as pilot
import chinstrap_tdr_zoc_sensitivity_v2 as zoc
import signy_gps_krill_access_v1 as bas
import south_orkney_chinstrap_island_krill_v1 as island

SOURCE_PILOT=pilot.PILOT
PRIMARY_METHOD="q1_60min"
PRIMARY_THRESHOLD=5
MIN_GPS_RADIUS_KM=10
MAX_GPS_RADIUS_KM=150
REQUIRED_MAX_CLOCK_GAP=600
SOURCE_YEAR_BASELINE="GPS source breeding season T -> model Jan-Feb T; T+1 is retrospective"
MAX_UNCALIBRATED_DRIFT_DBAR=2.0
EXPECTED_PRIMARY_COUNTS={"LIC001":(1481,901),"PI001":(4786,2117),
                         "MIC001":(1369,876),"SIC004":(51,24)}

def source_gps_fixes(gps):
    """Sorted earliest actual source position at duplicate timestamp."""
    seen={}
    for time,lat,lon in gps:
        if time not in seen:
            seen[time]=(float(lat),float(lon))
    return [(t,*seen[t]) for t in sorted(seen)]

def model_cells(points,model,center,year):
    """Equal-weight unique GAM pixels; NOT count- or time-weighted prey capture."""
    arr,tr=model[year]
    if not points:
        return {"n_points_geographic":0,"n_model_valid":0,"n_distinct_cells":0,
                "mean_model_g_m2":None}
    lat=np.array([p[0] for p in points],dtype=float)
    lon=np.array([p[1] for p in points],dtype=float)
    distances=bas.geodesic(lat,lon,center[0],center[1])
    spatial=(distances>=MIN_GPS_RADIUS_KM)&(distances<=MAX_GPS_RADIUS_KM)
    if not np.any(spatial):
        return {"n_points_geographic":0,"n_model_valid":0,"n_distinct_cells":0,
                "mean_model_g_m2":None}
    val,rr,cc=bas.sampled_cells(arr,tr,lat[spatial],lon[spatial])
    good=np.isfinite(val)
    cells=sorted(set(zip(rr[good].tolist(),cc[good].tolist())))
    return {"n_points_geographic":int(spatial.sum()),
            "n_model_valid":int(good.sum()),
            "n_distinct_cells":len(cells),
            "mean_model_g_m2":float(np.mean([arr[r,c] for r,c in cells])) if cells else None}

def analyze(tdr_zip,gps_zip,freer_zip):
    # Source-only spatial origins, independently determined from ALL original
    # same-species Chinstrap first positions, with no krill or dive selection.
    original_gps,support=island.read_all_chinstrap(gps_zip)
    center=island.island_source_centers(original_gps)
    model=bas.source_models(freer_zip)
    result=[]
    baselines=[]
    for loc,tag in SOURCE_PILOT.items():
        source_tdr,tdr_native=pilot.reader(tdr_zip,tag,"TDR")
        source_gps,gps_native=pilot.reader(gps_zip,tag,"GPS")
        gps=source_gps_fixes(source_gps)
        times,t,p,duplicates,invalid=pilot.get_clean_pressure(source_tdr)
        years={q.year if q.month>=7 else q.year-1 for q,_,_ in gps}
        if len(years)!=1:
            raise ValueError("original GPS pilot crosses breeding seasons")
        year=next(iter(years))
        loc_center=center[loc,year]
        anchor=(loc_center["center_lat"],loc_center["center_lon"])
        if not(set(q.year if q.month>=7 else q.year-1 for q in times)=={year}):
            raise ValueError("TDR season and GPS source season differ")
        # GPS and TDR original instruments need not have identical start/end.
        # Preserve differences and compare ONLY the actually overlapping span.
        # An unmatched GPS interval is not evidence of a non-diving bird.
        gps_start,gps_end=gps[0][0].timestamp(),gps[-1][0].timestamp()
        overlap_start,overlap_end=max(gps_start,t[0]),min(gps_end,t[-1])
        if overlap_end<=overlap_start:
            raise ValueError("source GPS and TDR do not overlap in recorded time")
        tdr_span=t[-1]-t[0]
        gps_span=gps_end-gps_start
        overlap_fraction_tdr=(overlap_end-overlap_start)/tdr_span
        overlap_fraction_gps=(overlap_end-overlap_start)/gps_span
        spike=bas.singleton_spike_mask(gps)
        spike_timestamps={gps[i][0].isoformat() for i in np.flatnonzero(spike)}
        in_tdr_time=[q for q in gps if t[0]<=q[0].timestamp()<=t[-1]]
        # Predefined once-per-hour original GPS baseline (all source GPS fixes).
        hourly=bas.selected_hourly([q for q in in_tdr_time if q[0].isoformat() not in spike_timestamps])
        baseline={"island":loc,"source_deployment_id":tag,"breeding_season":year,
                  "gps_original_csv":Path(gps_native).name,
                  "tdr_original_csv":Path(tdr_native).name,
                  "n_GPS_original":len(source_gps),"n_GPS_distinct_time":len(gps),
                  "n_isolated_GPS_spikes":int(spike.sum()),
                  "n_hourly_GPS_source_in_TDR_time":len(hourly),
                  "recorded_time_overlap_seconds":overlap_end-overlap_start,
                  "fraction_TDR_span_overlapping_GPS":overlap_fraction_tdr,
                  "fraction_GPS_span_overlapping_TDR":overlap_fraction_gps,
                  "GPS_source_starts_before_TDR_seconds":max(0.0,t[0]-gps_start),
                  "GPS_source_ends_after_TDR_seconds":max(0.0,gps_end-t[-1]),
                  "different_source_sensor_coverage_is_not_non_diving":True}
        for period,yr in (("preseason",year),("same_summer",year+1)):
            m=model_cells([(r[1],r[2]) for r in hourly],model,anchor,yr)
            baseline[period+"_GPS_reference_mean_model_g_m2"]=m["mean_model_g_m2"]
            baseline[period+"_GPS_reference_distinct_cells"]=m["n_distinct_cells"]
            baseline[period+"_GPS_reference_valid_hourly"]=m["n_model_valid"]
        baselines.append(baseline)
        for method,window,quantile,min_count in zoc.METHODS:
            corrected,cal=zoc.offset_method(t,p,window,quantile,min_count)
            for threshold in zoc.THRESHOLDS:
                events=pilot.dive_candidates(t,corrected,float(threshold))
                matched,qc=pilot.gps_time_brackets(events,source_gps)
                clean=[e for e in matched
                       if e["nearest_original_GPS_timestamp"] not in spike_timestamps]
                row={"island":loc,"source_deployment_id":tag,
                     "breeding_season":year,"TDR_source_name":Path(tdr_native).name,
                     "GPS_source_name":Path(gps_native).name,
                     "zero_offset_method":method,
                     "threshold_dbar":threshold,
                     "provisional_surface_offset_range_dbar":cal["baseline_range_dbar"],
                     "pressure_sensor_large_drift_flag":cal["baseline_range_dbar"]>MAX_UNCALIBRATED_DRIFT_DBAR,
                     "n_TDR_source_unique_pressure":len(t),
                     "n_TDR_invalid_pressure":invalid,
                     "n_TDR_duplicate_time":duplicates,
                     "n_raw_pressure_defined_events":len(events),
                     "n_original_GPS_time_bracketed_events":len(matched),
                     "n_bracketed_events_after_isolated_GPS_spike_filter":len(clean),
                     "fraction_events_time_bracketed":len(matched)/len(events) if events else None,
                     "median_GPS_nearest_time_offset_s":statistics.median(
                        e["original_GPS_time_offset_seconds"] for e in matched) if matched else None,
                     "n_original_GPS_time_bracketed_events_not_model_samples":True,
                     "dive_is_not_confirmed_krill_consumption":True}
                for period,yr in (("preseason",year),("same_summer",year+1)):
                    m=model_cells([(e["nearest_original_GPS_lat"],e["nearest_original_GPS_lon"])
                                  for e in clean],model,anchor,yr)
                    row[period+"_bracketed_events_in_window"]=m["n_points_geographic"]
                    row[period+"_bracketed_model_valid_events"]=m["n_model_valid"]
                    row[period+"_bracketed_unique_model_cells"]=m["n_distinct_cells"]
                    row[period+"_candidate_GPS_cells_krill_model_g_m2"]=m["mean_model_g_m2"]
                    b=baseline[period+"_GPS_reference_mean_model_g_m2"]
                    row[period+"_candidate_cells_vs_all_GPS_cells_model_ratio"]=(
                        m["mean_model_g_m2"]/b if b and m["mean_model_g_m2"] is not None else None)
                result.append(row)
    if len(result)!=48:
        raise ValueError("all 4 source tags × 4 offsets × 3 cutoffs must be retained")
    return result,baselines,support

def verify(rows,baselines):
    by={(r["source_deployment_id"],r["zero_offset_method"],r["threshold_dbar"]):r for r in rows}
    if len(by)!=48:
        raise ValueError("incomplete TDR source response grid")
    for tag,(all_events,bracketed) in EXPECTED_PRIMARY_COUNTS.items():
        r=by[tag,PRIMARY_METHOD,PRIMARY_THRESHOLD]
        if (r["n_raw_pressure_defined_events"],r["n_original_GPS_time_bracketed_events"])!=(all_events,bracketed):
            raise ValueError("source 4-tag TDR/GPS primary receipt changed for "+tag)
        if r["preseason_bracketed_model_valid_events"]>bracketed:
            raise ValueError("model-valid events exceed real GPS brackets")
        if r["preseason_bracketed_unique_model_cells"]>r["preseason_bracketed_model_valid_events"]:
            raise ValueError("duplicated model raster cells miscounted")
    if not by["MIC001",PRIMARY_METHOD,PRIMARY_THRESHOLD]["pressure_sensor_large_drift_flag"]:
        raise ValueError("original Monroe drift gate unexpectedly passed")
    if len(baselines)!=4:return False
    return True

def save(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tdr-zip",required=True,type=Path)
    p.add_argument("--gps-zip",required=True,type=Path)
    p.add_argument("--krill-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check-receipt",action="store_true")
    a=p.parse_args()
    rows,baseline,support=analyze(a.tdr_zip,a.gps_zip,a.krill_zip)
    if a.check_receipt and not verify(rows,baseline):
        raise ValueError("source receipt failed")
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"pilot_48_sensitivity_gps_krill_cells.csv",rows)
    save(a.out/"pilot_4_original_GPS_reference.csv",baseline)
    primary=[r for r in rows if r["zero_offset_method"]==PRIMARY_METHOD
             and r["threshold_dbar"]==PRIMARY_THRESHOLD]
    summary={
        "status":"PILOT_SOURCE_PRESSURE_GPS_GAM_SPATIAL_JOIN_ONLY_NOT_CONFIRMED_DIVES",
        "source_ids":list(SOURCE_PILOT.values()),
        "source_count_rows":len(rows),
        "n_pilot_deployments":len(primary),
        "original_GPS_source_roster":support["qc"],
        "TDR_pressure_zero_offset_validated":False,
        "GPS_to_TDR_clock_externally_validated":False,
        "at_sea_foraging_state_validated":False,
        "krill_observed_at_event_position":False,
        "modelled_krill_fit_used_ice_and_salinity":True,
        "no_island_replicate_and_no_future_breeding_prediction":True,
        "primary":primary,
        "baseline":baseline,
        "limitations":[
            "Only 4 source-first tags (one per island), not representative random individuals.",
            "2/5/10dbar thresholds and four zero-offset methods, some within-track sensor drift >2dbar.",
            "GPS clock co-location assumes native timestamps share clock; external calibration missing.",
            "Real GPS fix is not necessarily actual dive location; no water/land/capture behavior QA.",
            "Raster is Freer 2025 fitted GAM trained on IMR acoustics, ice and salinity: not independent prey observation.",
            "Four islands are in different breeding seasons, island and year confounded.",
            "No validated 2050/2100 penguin abundance, patch N_eff, recolonization or vegetation forecast."
        ]
    }
    (a.out/"decision.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":summary["status"],
        "pilot": [{k:r[k] for k in (
            "island","source_deployment_id","breeding_season",
            "n_raw_pressure_defined_events","n_original_GPS_time_bracketed_events",
            "preseason_bracketed_events_in_window","preseason_bracketed_unique_model_cells",
            "preseason_candidate_GPS_cells_krill_model_g_m2",
            "preseason_candidate_cells_vs_all_GPS_cells_model_ratio",
            "same_summer_candidate_cells_vs_all_GPS_cells_model_ratio",
            "pressure_sensor_large_drift_flag"
        )} for r in primary],
        "receipt_checked":bool(a.check_receipt)
    },ensure_ascii=False))
if __name__=="__main__":
    main()
