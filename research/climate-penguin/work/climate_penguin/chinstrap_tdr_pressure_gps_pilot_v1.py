"""Pressure-offset/dive/GPS timestamp pilot from original BAS Chinstrap V2 files.

PILOT IDs fixed as first source-matched nonempty publisher IDs for each island
before examining pressure: LIC001, PI001/TDR PIC001, MIC001, SIC004.
No krill, sea ice, salinity, chick outcome or ecological hypothesis tested.
Strict temporal brackets: GPS original fixes <=600s apart, dive max timestamp
must be within 300s of a nearest actual GPS fix. No clock shift optimization.
"""
from __future__ import annotations
import argparse
import bisect
import csv
import datetime as dt
import io
import json
import math
import statistics
import zipfile
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from chinstrap_v2_tdr_gps_source_gate import get_id

PILOT={"LI":"LIC001","PI":"PI001","MI":"MIC001","SI":"SIC004"}
THRESHOLDS=(2.0,5.0,10.0)
MIN_EVENT_SECONDS=10.0
MAX_SAMPLE_GAP_SECONDS=3.0
MIN_SURFACE_VALUES_PER_HOUR=300
SURFACE_PERCENTILE=1
MAX_GPS_BRACKET_SECONDS=600.0
MAX_NEAREST_GPS_SECONDS=300.0
MAX_TRACK_FILE_ROWS=2_000_000

def reader(path,deployment,role):
    with zipfile.ZipFile(path) as z:
        names=[r for r in z.namelist() if Path(r).name.lower().endswith("_"+role.lower()+".csv")]
        chosen=[n for n in names if get_id(Path(n).name,role)[0]==deployment]
        if len(chosen)!=1:
            raise ValueError(f"cannot one-to-one resolve original {role} deployment {deployment}: {chosen}")
        with z.open(chosen[0]) as f:
            text=io.TextIOWrapper(f,encoding="utf-8-sig",newline="")
            rows=csv.DictReader(text)
            if role=="GPS":
                expected={"DateTime","Latitude_degrees_north","Longitude_degrees_east"}
            else:
                expected={"DateTime","Pressure [dBars]"}
            if not expected.issubset(set(rows.fieldnames or [])):
                raise ValueError(f"wrong original {role} source header {(rows.fieldnames or [])}")
            out=[]
            for i,r in enumerate(rows):
                if i>=MAX_TRACK_FILE_ROWS:raise ValueError("source row count exceeded pilot protection")
                time=dt.datetime.fromisoformat(r["DateTime"].replace("Z","+00:00"))
                if role=="GPS":
                    lat=float(r["Latitude_degrees_north"])
                    lon=float(r["Longitude_degrees_east"])
                    if not(-90<=lat<=90 and -180<=lon<=180 and math.isfinite(lat+lon)):
                        raise ValueError("invalid original GPS coordinates")
                    out.append((time,lat,lon))
                else:
                    v=r["Pressure [dBars]"]
                    try:pres=float(v)
                    except (ValueError,TypeError):pres=float("nan")
                    out.append((time,pres))
    return out,chosen[0]

def get_clean_pressure(original):
    vals={}
    duplicate=0
    invalid=0
    for timestamp,pressure in original:
        if not math.isfinite(pressure):
            invalid+=1
            continue
        if timestamp in vals:
            duplicate+=1
            continue
        vals[timestamp]=pressure
    if len(vals)<1000:
        raise ValueError("fewer than 1000 original TDR pressure points")
    ordered=sorted(vals)
    times=np.array([z.timestamp() for z in ordered])
    values=np.array([vals[z] for z in ordered],dtype=float)
    if np.any(np.diff(times)<=0):
        raise ValueError("TDR timestamps not strictly increasing after de-dup")
    return ordered,times,values,duplicate,invalid

def hour_offset(times,pressure):
    hours=np.floor((times-times[0])/3600).astype(np.int64)
    unique=np.unique(hours)
    centers=[]
    p01=[]
    n=[]
    for h in unique:
        subset=pressure[hours==h]
        if len(subset)<MIN_SURFACE_VALUES_PER_HOUR:
            continue
        centers.append(times[0]+(h+.5)*3600)
        p01.append(float(np.percentile(subset,SURFACE_PERCENTILE)))
        n.append(len(subset))
    if len(centers)<3:
        raise ValueError("insufficient hours with observed possible surface baseline")
    offset=np.interp(times,np.array(centers),np.array(p01))
    corrected=pressure-offset
    return corrected,{
        "n_hour_windows":len(unique),
        "n_calibrated_hour_windows":len(centers),
        "calibration_window_gaps":int(len(unique)-len(centers)),
        "surface_q01_dbar_median":float(np.median(p01)),
        "surface_q01_dbar_min":float(np.min(p01)),
        "surface_q01_dbar_max":float(np.max(p01)),
        "surface_q01_drift_range_dbar":float(np.max(p01)-np.min(p01)),
        "offset_method":"1st percentile per 60min TDR raw pressure window >=300 valid points, piecewise linear interpolation",
        "pressure_offset_validation_status":"provisional; surface exposure and pressure drift not independently verified"
    }

def dive_candidates(times,corrected,threshold):
    over=(corrected>=threshold)
    dtsec=np.diff(times)
    # Event segments are contiguous samples above fixed dbar threshold
    # with no sample gap longer than 3 seconds.
    indices=np.flatnonzero(over)
    if len(indices)==0:return []
    starts=[0]
    for j in range(1,len(indices)):
        if indices[j]!=indices[j-1]+1 or dtsec[indices[j-1]]>MAX_SAMPLE_GAP_SECONDS:
            starts.append(j)
    starts.append(len(indices))
    events=[]
    for a,b in zip(starts[:-1],starts[1:]):
        ii=indices[a:b]
        duration=float(times[ii[-1]]-times[ii[0]])
        if duration<MIN_EVENT_SECONDS:continue
        peak=int(ii[np.argmax(corrected[ii])])
        events.append({
            "peak_timestamp":float(times[peak]),
            "start_timestamp":float(times[ii[0]]),
            "end_timestamp":float(times[ii[-1]]),
            "duration_seconds":duration,
            "peak_corrected_pressure_dbar":float(corrected[peak])
        })
    return events

def gps_time_brackets(events,gps):
    # The paired tag's source original GPS chronology, not interpolation.
    keep={}
    for time,lat,lon in gps:
        if time in keep:continue
        keep[time]=(lat,lon)
    ts=sorted(keep)
    secs=[z.timestamp() for z in ts]
    matched=[]
    eligible=0
    nearest_seconds=[]
    for e in events:
        t=e["peak_timestamp"]
        k=bisect.bisect_left(secs,t)
        if k<=0 or k>=len(secs):
            continue
        left,right=secs[k-1],secs[k]
        gap=right-left
        if gap>MAX_GPS_BRACKET_SECONDS:
            continue
        nearest=min(t-left,right-t)
        if nearest>MAX_NEAREST_GPS_SECONDS:
            continue
        choice=k-1 if t-left<=right-t else k
        eligible+=1
        nearest_seconds.append(nearest)
        matched.append({**e,"nearest_original_GPS_timestamp":ts[choice].isoformat(),
                        "original_GPS_time_offset_seconds":nearest,
                        "original_GPS_bracket_width_seconds":gap,
                        "nearest_original_GPS_lat":keep[ts[choice]][0],
                        "nearest_original_GPS_lon":keep[ts[choice]][1]})
    return matched,{
        "events_total":len(events),
        "events_time_bracket_qualified":eligible,
        "event_fraction_time_bracket_qualified":eligible/len(events) if events else None,
        "GPS_temporal_overlap_only_no_ocean_or_dive_capture_confirmation":True,
        "median_original_GPS_event_offset_seconds":statistics.median(nearest_seconds) if nearest_seconds else None
    }

def analyze(tdr_path,gps_path):
    result=[]
    for island,deploy in PILOT.items():
        raw_tdr,tdr_member=reader(tdr_path,deploy,"TDR")
        raw_gps,gps_member=reader(gps_path,deploy,"GPS")
        chronological,times,pressure,duplicates,invalid=get_clean_pressure(raw_tdr)
        corrected,cal=hour_offset(times,pressure)
        source_gps=[x[0] for x in raw_gps]
        gps_start=min(source_gps).timestamp()
        gps_end=max(source_gps).timestamp()
        within=int(np.count_nonzero((times>=gps_start)&(times<=gps_end)))
        sample_gaps=np.diff(times)
        row={
          "island":island,"original_deployment_id":deploy,
          "source_TDR_member":Path(tdr_member).name,
          "source_GPS_member":Path(gps_member).name,
          "source_pressure_records":len(raw_tdr),
          "n_valid_unique_pressure":len(times),
          "n_invalid_pressure_records":invalid,
          "n_duplicate_TDR_timestamps":duplicates,
          "n_original_GPS_records":len(raw_gps),
          "TDR_first_UTC_unverified":chronological[0].isoformat(),
          "TDR_last_UTC_unverified":chronological[-1].isoformat(),
          "GPS_first_UTC_unverified":min(source_gps).isoformat(),
          "GPS_last_UTC_unverified":max(source_gps).isoformat(),
          "TDR_finite_samples_within_GPS_time_window":within,
          "fraction_TDR_finite_samples_within_GPS_time_window":within/len(times),
          "source_sample_median_interval_s":float(np.median(sample_gaps)),
          "source_sample_gaps_over_3s":int(np.sum(sample_gaps>3)),
          "raw_pressure_dbar_p01":float(np.percentile(pressure,1)),
          "raw_pressure_dbar_median":float(np.median(pressure)),
          "raw_pressure_dbar_p99":float(np.percentile(pressure,99)),
          **cal
        }
        for cut in THRESHOLDS:
            events=dive_candidates(times,corrected,cut)
            paired,m=gps_time_brackets(events,raw_gps)
            row[f"threshold_{int(cut)}dbar_candidate_events"]=len(events)
            row[f"threshold_{int(cut)}dbar_gps_bracket_events"]=m["events_time_bracket_qualified"]
            row[f"threshold_{int(cut)}dbar_gps_bracket_fraction"]=m["event_fraction_time_bracket_qualified"]
            row[f"threshold_{int(cut)}dbar_max_corrected_pressure"]=max(
                (e["peak_corrected_pressure_dbar"] for e in events),default=None)
            row[f"threshold_{int(cut)}dbar_median_event_duration_s"]=(
                statistics.median(e["duration_seconds"] for e in events) if events else None)
            row[f"threshold_{int(cut)}dbar_median_GPS_nearest_offset_s"]=m["median_original_GPS_event_offset_seconds"]
        result.append(row)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tdr-zip",required=True,type=Path)
    p.add_argument("--gps-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    res=analyze(a.tdr_zip,a.gps_zip)
    a.out.mkdir(parents=True,exist_ok=True)
    with (a.out/"pilot_4source_deployments.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(res[0]))
        w.writeheader();w.writerows(res)
    summary={
        "status":"PILOT_ORIGINAL_TDR_ZOC_AND_GPS_BRACKET_ONLY_NO_KRILL_EFFECT",
        "original_BAS_v2_GPS":"10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92",
        "original_BAS_v2_TDR":"10.5285/da13e049-be2b-4345-bbdd-ab960cb24731",
        "original_pilot_ids":list(PILOT.values()),
        "pilot_by_original_source_members":res,
        "calibration_parameters":{
            "surface_quantile_percent":SURFACE_PERCENTILE,
            "window_minutes":60,
            "minimum_pressure_samples_per_window":MIN_SURFACE_VALUES_PER_HOUR,
            "event_pressure_cutoffs_dbar":list(THRESHOLDS),
            "minimum_continuous_duration_s":MIN_EVENT_SECONDS,
            "max_sample_gap_s":MAX_SAMPLE_GAP_SECONDS,
            "GPS_bracket_duration_limit_s":MAX_GPS_BRACKET_SECONDS,
            "GPS_nearest_actual_fix_limit_s":MAX_NEAREST_GPS_SECONDS},
        "limits":[
            "Pilot IDs fixed before inspecting TDR pressure; not a random sample or an island population estimate.",
            "TDR pressure baseline from within-record hour quantiles provisional; compare with validated diveMove ZOC/visual surface periods before biological inferences.",
            "GPS and TDR timestamps are treated as same clock provisionally; external instrument synchronization is not independently verified.",
            "Pressure-defined events are candidate dives, not confirmed foraging or krill capture.",
            "Original GPS bracket required; no interpolation across >10-minute gaps, so sample selection differs by island.",
            "No GPS-based krill-field value, salinity effect, island food effect or future breeding prediction is computed in pilot."
        ]
    }
    (a.out/"pilot_decision.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":summary["status"],"originals":[{
        "island":r["island"],"id":r["original_deployment_id"],
        "n_pressure":r["n_valid_unique_pressure"],
        "n_GPS":r["n_original_GPS_records"],
        "TDR_within_GPS_fraction":r["fraction_TDR_finite_samples_within_GPS_time_window"],
        "ZOC_drift_dbar":r["surface_q01_drift_range_dbar"],
        "5dbar_candidate_events":r["threshold_5dbar_candidate_events"],
        "5dbar_GPS_bracketed":r["threshold_5dbar_gps_bracket_events"]
    } for r in res]},ensure_ascii=False))

if __name__=="__main__":
    main()
