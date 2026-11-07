"""Source-selected 4 islands x 4 native Chinstrap GPS/TDR 5-dbar sensor QA.

16 original tag IDs fixed from source-only 300 ID overlap, BEFORE opening
new pressure records: LI001–004, PI001–004, MI001–004, SI004/008/009/010.
All 4 previously fixed offset methods retained. No dive is assumed to be
prey capture; sensor drift and GPS gap censoring measured, not optimized.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from pathlib import Path
import numpy as np
import chinstrap_tdr_pressure_gps_pilot_v1 as pilot
import chinstrap_tdr_zoc_sensitivity_v2 as zoc

SOURCE_TAGS={
    "LI":("LIC001","LIC002","LIC003","LIC004"),
    "PI":("PI001","PI002","PI003","PI004"),
    "MI":("MIC001","MIC002","MIC003","MIC004"),
    "SI":("SIC004","SIC008","SIC009","SIC010")
}
PRIMARY="q1_60min"
THRESHOLD_DBAR=5.0
DRIFT_FLAG_DBAR=2.0
GPS_SOURCE_OVERLAP_REQUIRED=False
EXPECTED_PILOT={"LIC001":(1481,901),"PI001":(4786,2117),
                "MIC001":(1369,876),"SIC004":(51,24)}

def choose():
    out=[(island,tag) for island,ids in SOURCE_TAGS.items() for tag in ids]
    if len(out)!=16 or len(set(t for _,t in out))!=16:
        raise ValueError("fixed publisher source-only 16-tag roster invalid")
    return out

def fetch_sensor(tdr,gps,tag):
    original,tdr_member=pilot.reader(tdr,tag,"TDR")
    original_gps,gps_member=pilot.reader(gps,tag,"GPS")
    _,times,pressure,duplicate,missing=pilot.get_clean_pressure(original)
    gps_t=[x[0].timestamp() for x in original_gps]
    if len(gps_t)<2:
        raise ValueError("GPS original has <2 valid source points")
    first,last=min(gps_t),max(gps_t)
    overlap=max(0.0,min(last,times[-1])-max(first,times[0]))
    tdr_duration=times[-1]-times[0]
    gps_duration=last-first
    if tdr_duration<=0 or gps_duration<=0:
        raise ValueError("invalid original instrument span")
    audit={
        "tag":tag,
        "source_TDR_member":Path(tdr_member).name,
        "source_GPS_member":Path(gps_member).name,
        "n_pressure_unique_valid":len(times),
        "n_pressure_missing":missing,
        "n_pressure_duplicate_timestamp":duplicate,
        "n_original_GPS_fixes":len(original_gps),
        "TDR_seconds":tdr_duration,
        "GPS_seconds":gps_duration,
        "GPS_TDR_overlap_seconds":overlap,
        "fraction_TDR_span_within_GPS":overlap/tdr_duration,
        "fraction_GPS_span_within_TDR":overlap/gps_duration,
        "TDR_median_sample_step_s":float(np.median(np.diff(times))),
        "n_TDR_gaps_more_than_3_seconds":int(np.sum(np.diff(times)>3)),
        "raw_pressure_dbar_p01":float(np.percentile(pressure,1)),
        "raw_pressure_dbar_p99":float(np.percentile(pressure,99))
    }
    return times,pressure,original_gps,audit

def execute(tdr,gps):
    table=[]
    for island,tag in choose():
        try:
            t,p,coords,source=fetch_sensor(tdr,gps,tag)
        except (ValueError,KeyError,OSError,RuntimeError) as e:
            for name,_,_,_ in zoc.METHODS:
                table.append({"island":island,"original_source_tag":tag,
                    "offset_method":name,"pressure_threshold_dbar":THRESHOLD_DBAR,
                    "status":"SOURCE_QA_STOP","source_issue":type(e).__name__+":"+str(e)})
            continue
        for name,window,percentile,min_n in zoc.METHODS:
            try:
                corrected,bounds=zoc.offset_method(t,p,window,percentile,min_n)
                candidates=pilot.dive_candidates(t,corrected,THRESHOLD_DBAR)
                gps_link,info=pilot.gps_time_brackets(candidates,coords)
                row={
                    "island":island,"original_source_tag":tag,
                    "offset_method":name,"pressure_threshold_dbar":THRESHOLD_DBAR,
                    "status":"SOURCE_PRESSURE_CANDIDATE_ONLY_NOT_CALIBRATED",
                    **source,
                    "n_original_pressure_defined_events":len(candidates),
                    "n_original_GPS_bracketed_events":len(gps_link),
                    "fraction_candidates_GPS_bracketed":(
                         len(gps_link)/len(candidates) if candidates else None),
                    "estimated_pressure_zero_min_dbar":bounds["min_baseline_dbar"],
                    "estimated_pressure_zero_max_dbar":bounds["max_baseline_dbar"],
                    "estimated_zero_offset_range_dbar":bounds["baseline_range_dbar"],
                    "provisional_drift_above_2dbar":(
                        bounds["baseline_range_dbar"]>DRIFT_FLAG_DBAR if name!="global_q1" else None),
                    "calibrated_surface_periods_confirmed":False,
                    "capture_or_foraging_verified":False,
                    "GPS_TDR_external_clock_check":False
                }
            except (ValueError,KeyError) as e:
                row={
                    "island":island,"original_source_tag":tag,
                    "offset_method":name,"pressure_threshold_dbar":THRESHOLD_DBAR,
                    "status":"CALIBRATION_QA_STOP",
                    "source_issue":type(e).__name__+":"+str(e)
                }
            table.append(row)
    if len(table)!=16*len(zoc.METHODS):
        raise ValueError("did not preserve all original sixteen source tags×four ZOC options")
    return table

def summarize(rows):
    output=[]
    for island,tag in choose():
        group=[r for r in rows if r["original_source_tag"]==tag]
        primary=next(r for r in group if r["offset_method"]==PRIMARY)
        good=[r for r in group if r["status"]=="SOURCE_PRESSURE_CANDIDATE_ONLY_NOT_CALIBRATED"]
        c=[r["n_original_pressure_defined_events"] for r in good]
        g=[r["n_original_GPS_bracketed_events"] for r in good]
        outcome={
            "island":island,"original_source_tag":tag,
            "primary_pressure_source_QA_available":primary["status"]=="SOURCE_PRESSURE_CANDIDATE_ONLY_NOT_CALIBRATED",
            "number_offset_methods_with_derived_candidates":len(good),
            "min_candidate_events_across_ZOC_methods":min(c) if c else None,
            "max_candidate_events_across_ZOC_methods":max(c) if c else None,
            "min_GPS_bracketed_across_ZOC_methods":min(g) if g else None,
            "max_GPS_bracketed_across_ZOC_methods":max(g) if g else None,
            "primary_Q1hour_zero_range_dbar":primary.get("estimated_zero_offset_range_dbar"),
            "primary_Q1hour_zero_drift_above_2dbar":primary.get("provisional_drift_above_2dbar"),
            "primary_candidate_events":primary.get("n_original_pressure_defined_events"),
            "primary_GPS_bracketed_events":primary.get("n_original_GPS_bracketed_events"),
            "primary_GPS_bracket_fraction":primary.get("fraction_candidates_GPS_bracketed"),
            "primary_fraction_TDR_span_within_GPS":primary.get("fraction_TDR_span_within_GPS"),
            "primary_fraction_GPS_span_within_TDR":primary.get("fraction_GPS_span_within_TDR"),
            "same_island_year_source_support_only":True,
            "sensor_QA_does_not_validate_dive_ecology":True
        }
        if c and outcome["primary_candidate_events"]:
            outcome["ZOC_candidate_count_range_over_primary"]=(
              (max(c)-min(c))/outcome["primary_candidate_events"])
        else:
            outcome["ZOC_candidate_count_range_over_primary"]=None
        output.append(outcome)
    return output

def verify(rows,summary):
    x={(r["original_source_tag"],r["offset_method"]):r for r in rows}
    for tag,(n,g) in EXPECTED_PILOT.items():
        r=x[tag,PRIMARY]
        if (r.get("n_original_pressure_defined_events"),
            r.get("n_original_GPS_bracketed_events"))!=(n,g):
            raise ValueError("original four fixed tag receipt mismatch: "+tag)
    if len(summary)!=16 or len({r["original_source_tag"] for r in summary})!=16:
        raise ValueError("16 source-selected original tags not all audited")
    if next(r for r in summary if r["original_source_tag"]=="MIC001")[
        "primary_Q1hour_zero_drift_above_2dbar"] is not True:
        raise ValueError("known Monroe high sensor drift not detected")
    return True

def save(path,rows):
    keys=sorted(set().union(*(set(r) for r in rows)))
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tdr-zip",required=True,type=Path)
    ap.add_argument("--gps-zip",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--check",action="store_true")
    a=ap.parse_args()
    rows=execute(a.tdr_zip,a.gps_zip)
    summary=summarize(rows)
    if a.check:verify(rows,summary)
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"source_sensor_methods.csv",rows)
    save(a.out/"frozen16_source_tag_summary.csv",summary)
    decision={
      "status":"SOURCE_FIXED_16_TAG_TDR_SENSOR_QA_NOT_VALIDATED_FORAGING",
      "source_selection":"First four already-GPS/TDR-matched original IDs per island, frozen from source-only archive, before opening any additional pressure outcomes.",
      "source_islands":list(SOURCE_TAGS),
      "source_n_tags":len(summary),
      "source_n_method_tag_rows":len(rows),
      "primary_source_candidate_not_biological_depth":PRIMARY,
      "threshold_dbar":THRESHOLD_DBAR,
      "drift_diagnostic_flag_dbar":DRIFT_FLAG_DBAR,
      "source_counts":{
          "primary_method_ok":sum(x["primary_pressure_source_QA_available"] for x in summary),
          "provisional_large_pressure_drift":sum(x["primary_Q1hour_zero_drift_above_2dbar"] is True for x in summary),
          "original_tag_with_all_4_ZOC_methods":sum(x["number_offset_methods_with_derived_candidates"]==4 for x in summary)
      },
      "source_tags":summary,
      "limits":[
        "16 earliest source-matched tags per island are not a randomized demographic or foraging sample.",
        "Pressure zero-offset q1/q5 is provisional, surface intervals and sensor drift correction not independently confirmed.",
        "A positive pressure candidate does not mean prey capture or even correctly calibrated physical depth.",
        "GPS bracket fraction is biased by device recording/position availability, not real dive effort.",
        "No ocean/land mask, GPS clock offset external validation, or prey availability original acoustic survey here.",
        "No four-island pressure/event count ecological effect or future breeding-space forecast is estimated."
      ]
    }
    (a.out/"decision.json").write_text(json.dumps(decision,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":decision["status"],"counts":decision["source_counts"],
         "per_tag":[{k:r[k] for k in ("island","original_source_tag","primary_Q1hour_zero_range_dbar",
            "primary_candidate_events","primary_GPS_bracketed_events",
            "primary_GPS_bracket_fraction","ZOC_candidate_count_range_over_primary")}
            for r in summary],"check":bool(a.check)},ensure_ascii=False))

if __name__=="__main__":
    main()
