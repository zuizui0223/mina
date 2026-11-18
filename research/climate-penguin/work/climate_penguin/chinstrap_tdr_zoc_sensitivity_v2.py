"""TDR pressure zero-offset sensitivity: source-fixed 4 deployment pilot.

Compute all predefined q1 30-min, q1 60-min (previous primary), q5 60-min
and global q1 offsets, with unchanged 2/5/10dbar and 10s dive-candidate
rules and strict original GPS bracketing. Do not select a method using
island model-krill, reproductive, or ecological outcomes. No prey estimation.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from pathlib import Path
import numpy as np
import chinstrap_tdr_pressure_gps_pilot_v1 as original

METHODS=(
 ("q1_60min",3600,1,300),
 ("q1_30min",1800,1,300),
 ("q5_60min",3600,5,300),
 ("global_q1",None,1,None),
)
THRESHOLDS=(2,5,10)

def offset_method(t,p,window,percentile,min_n):
    if window is None:
        value=float(np.percentile(p,percentile))
        return p-value,{"n_valid_windows":1,"min_baseline_dbar":value,
                        "max_baseline_dbar":value,"baseline_range_dbar":0.0}
    h=np.floor((t-t[0])/window).astype(np.int64)
    anchors=[]
    levels=[]
    for idx in np.unique(h):
        item=p[h==idx]
        if len(item)<min_n:
            continue
        anchors.append(t[0]+(idx+.5)*window)
        levels.append(float(np.percentile(item,percentile)))
    if len(anchors)<3:
        raise ValueError("insufficient full source hours for interpolation")
    base=np.interp(t,np.array(anchors),np.array(levels))
    return p-base,{"n_valid_windows":len(anchors),
                   "min_baseline_dbar":min(levels),"max_baseline_dbar":max(levels),
                   "baseline_range_dbar":max(levels)-min(levels)}

def run(tdr_zip,gps_zip):
    rows=[]
    for island,identifier in original.PILOT.items():
        raw_tdr,_=original.reader(tdr_zip,identifier,"TDR")
        gps,_=original.reader(gps_zip,identifier,"GPS")
        _,t,p,duplicates,invalid=original.get_clean_pressure(raw_tdr)
        for name,window,q,min_n in METHODS:
            corrected,offset=offset_method(t,p,window,q,min_n)
            for threshold in THRESHOLDS:
                events=original.dive_candidates(t,corrected,float(threshold))
                placed,location=original.gps_time_brackets(events,gps)
                rows.append({
                    "island":island,"source_deployment_id":identifier,
                    "offset_method":name,"time_window_seconds":window,
                    "surface_quantile_percent":q,
                    "pressure_threshold_dbar":threshold,
                    "offset_valid_windows":offset["n_valid_windows"],
                    "estimated_offset_min_dbar":offset["min_baseline_dbar"],
                    "estimated_offset_max_dbar":offset["max_baseline_dbar"],
                    "estimated_offset_range_dbar":offset["baseline_range_dbar"],
                    "original_valid_pressure_records":len(t),
                    "missing_pressure_records":invalid,
                    "duplicate_timestamp_records":duplicates,
                    "n_candidate_dive_events":len(events),
                    "n_GPS_bracketed_events":len(placed),
                    "fraction_GPS_bracketed":location["event_fraction_time_bracket_qualified"],
                    "mean_event_peak_relative_pressure_dbar":(
                        float(statistics.mean(x["peak_corrected_pressure_dbar"] for x in events)) if events else None),
                    "calibration_source_validated_surface_state":False,
                    "candidate_dives_not_capture_events":True
                })
    if len(rows)!=len(original.PILOT)*len(METHODS)*len(THRESHOLDS):
        raise ValueError("not all fixed calibration combinations evaluated")
    return rows

def receipt(rows):
    expected={
      "LIC001":(1481,901),
      "PI001":(4786,2117),
      "MIC001":(1369,876),
      "SIC004":(51,24)
    }
    for tag,(n,g) in expected.items():
        r=next(x for x in rows if x["source_deployment_id"]==tag and
               x["offset_method"]=="q1_60min" and x["pressure_threshold_dbar"]==5)
        if (r["n_candidate_dive_events"],r["n_GPS_bracketed_events"])!=(n,g):
            raise ValueError(f"original pilot numerical receipt mismatch {tag}")
    return True

def summarize(rows):
    out=[]
    for site,tag in original.PILOT.items():
        same=[z for z in rows if z["source_deployment_id"]==tag and
              z["pressure_threshold_dbar"]==5]
        primary=next(z for z in same if z["offset_method"]=="q1_60min")
        counts=[x["n_candidate_dive_events"] for x in same]
        placed=[x["n_GPS_bracketed_events"] for x in same]
        out.append({
            "island":site,"original_source_id":tag,
            "q1_60min_n_events":primary["n_candidate_dive_events"],
            "q1_60min_GPS_bracketed":primary["n_GPS_bracketed_events"],
            "minimum_n_events_5dbar_across_offset_methods":min(counts),
            "maximum_n_events_5dbar_across_offset_methods":max(counts),
            "minimum_GPS_bracketed_events_across_offset_methods":min(placed),
            "maximum_GPS_bracketed_events_across_offset_methods":max(placed),
            "primary_local_offset_range_dbar":primary["estimated_offset_range_dbar"],
            "large_local_drift_flag_2dbar":primary["estimated_offset_range_dbar"]>2,
            "pressure_to_depth_validated":False,
            "not_an_island_effect":True
        })
    return out

def csv_write(path,records):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]))
        writer.writeheader();writer.writerows(records)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tdr-zip",type=Path,required=True)
    p.add_argument("--gps-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--check-receipt",action="store_true")
    a=p.parse_args()
    results=run(a.tdr_zip,a.gps_zip)
    if a.check_receipt:receipt(results)
    summary=summarize(results)
    a.out.mkdir(parents=True,exist_ok=True)
    csv_write(a.out/"original_tdr_offset_event_sensitivity.csv",results)
    csv_write(a.out/"per_original_tag_qc_gate.csv",summary)
    report={
       "status":"TDR_OFFSET_SENSITIVITY_PILOT_NO_BEHAVIORAL_EFFECT",
       "bas_original_GPS_DOI":"10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92",
       "bas_original_TDR_DOI":"10.5285/da13e049-be2b-4345-bbdd-ab960cb24731",
       "all_fixed_pressure_calibration_methods":list(m[0] for m in METHODS),
       "all_fixed_threshold_dbar":list(THRESHOLDS),
       "all_original_pilot_tags":list(original.PILOT.values()),
       "n_rows":len(results),"per_tag":summary,
       "caveats":[
          "Source original pressure may drift with temperature; local q1 is provisional and not certified zero-offset correction.",
          "Global q1 is only a sensitivity comparator, not a recommended valid calibration method.",
          "Original first/last surface anchors, wet/dry, and sensor-specific diveMove/ZOC plots not independently reviewed.",
          "Unit is one TDR tag. Four pre-fixed pilot tags cannot establish island ecological differences.",
          "GPS time brackets are a stringent selected subset and not all diving hours.",
          "No krill observed at GPS-linked locations, no dive-confirmed prey and no future climate/reproduction model."
       ]}
    (a.out/"decision.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"receipt":bool(a.check_receipt),"tag_5dbar_method_ranges":summary},ensure_ascii=False))
if __name__=="__main__":
    main()
