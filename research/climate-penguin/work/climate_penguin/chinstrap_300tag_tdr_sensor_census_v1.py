"""All 300 original matched BAS Chinstrap GPS/TDR source sensor-QA census.

Source-only instrument audit; no dives, krill or climate outcome fitted.
Original 2011–19 BAS v2 GPS/TDR publisher ZIPs. TDR native PI###/PIC###
mapping is inherited from the audited source module. Every matched tag is
counted, including STOP cases. No filtering based on ecological outcome.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import chinstrap_v2_tdr_gps_source_gate as source
import chinstrap_tdr_pressure_gps_pilot_v1 as pilot

OFFSET_WINDOW_SECONDS=3600
MIN_WINDOW_SOURCE_SAMPLES=300
DRIFT_DIAGNOSTIC_DBAR=2.0
KNOWN_PILOT={"LIC001":0.30,"PI001":0.60,"MIC001":7.7525,"SIC004":0.41}

def hourly_lower_percentiles(t,p):
    """Vectorized disjoint-hour segmentation, exact source percentiles.

    A fast equivalent of the prior single-tag hour_offset() method, without
    O(n_hours x n_sample) mask scans or reading all tags into memory.
    """
    blocks=np.floor((t-t[0])/OFFSET_WINDOW_SECONDS).astype(np.int64)
    uniq,start=np.unique(blocks,return_index=True)
    stop=np.r_[start[1:],len(p)]
    q1=[];q5=[]
    for a,b in zip(start,stop):
        if b-a<MIN_WINDOW_SOURCE_SAMPLES:
            continue
        q1.append(float(np.percentile(p[a:b],1)))
        q5.append(float(np.percentile(p[a:b],5)))
    if len(q1)<3:
        raise ValueError("fewer than three source-hour windows with 300 valid pressure points")
    return {"n_source_hour_windows":len(uniq),
            "n_calibrated_hour_windows":len(q1),
            "q01_hourly_median_dbar":float(np.median(q1)),
            "q01_hourly_min_dbar":min(q1),"q01_hourly_max_dbar":max(q1),
            "q01_hourly_range_dbar":max(q1)-min(q1),
            "q05_hourly_median_dbar":float(np.median(q5)),
            "q05_hourly_range_dbar":max(q5)-min(q5),
            "original_surface_periods_verified":False}

def single_tag(tdr_zip,gps_zip,identifier):
    original,tdr_source=pilot.reader(tdr_zip,identifier,"TDR")
    gps,gps_source=pilot.reader(gps_zip,identifier,"GPS")
    _,t,p,dups,bad=pilot.get_clean_pressure(original)
    result=hourly_lower_percentiles(t,p)
    gps_times=sorted(set(x[0].timestamp() for x in gps))
    if len(gps_times)<2:
        raise ValueError("no two native GPS source timestamps")
    ti=np.asarray(gps_times)
    gps_gaps=np.diff(ti)
    gps_time=ti[-1]-ti[0]
    tdr_time=t[-1]-t[0]
    overlap=max(0.0,min(ti[-1],t[-1])-max(ti[0],t[0]))
    if gps_time<=0 or tdr_time<=0:
        raise ValueError("nonpositive original source time interval")
    pressure_gaps=np.diff(t)
    return {**result,
            "original_TDR_csv":Path(tdr_source).name,
            "original_GPS_csv":Path(gps_source).name,
            "source_pressure_n_original":len(original),
            "source_pressure_n_valid_unique":len(t),
            "source_pressure_n_invalid":bad,
            "source_pressure_n_duplicate_timestamp":dups,
            "native_TDR_median_sampling_seconds":float(np.median(pressure_gaps)),
            "native_TDR_gaps_over_3_seconds":int(np.sum(pressure_gaps>3)),
            "source_GPS_n_positions":len(gps),
            "source_GPS_n_unique_timestamp":len(ti),
            "GPS_total_timeline_seconds":gps_time,
            "TDR_total_timeline_seconds":tdr_time,
            "GPS_TDR_time_overlap_seconds":overlap,
            "fraction_TDR_time_inside_GPS_window":overlap/tdr_time,
            "fraction_GPS_time_inside_TDR_window":overlap/gps_time,
            "GPS_time_fraction_recorded_gaps_10min_or_less":float(np.sum(gps_gaps[gps_gaps<=600])/gps_time),
            "source_pressure_clock_gps_clock_external_sync_verified":False,
            "original_source_not_raw_krill_or_penguin_dive_capture":True,
            "q01_hourly_drift_gt_2dbar":result["q01_hourly_range_dbar"]>DRIFT_DIAGNOSTIC_DBAR,
            "q05_hourly_drift_gt_2dbar":result["q05_hourly_range_dbar"]>DRIFT_DIAGNOSTIC_DBAR}

def run(tdr_zip,gps_zip):
    meta,gp,tdr,ids=source.analyze(tdr_zip,gps_zip)
    if len(ids)!=300 or meta["joint_nonempty_deployments"]!=300:
        raise ValueError("publisher original source 300 GPS/TDR ID intersection drift")
    output=[]
    for i,identifier in enumerate(ids):
        island=identifier[:2]
        if island not in ("LI","PI","MI","SI"):
            raise ValueError("unsupported published island")
        base={"original_deployment_id":identifier,"original_island":island}
        try:
            row=single_tag(tdr_zip,gps_zip,identifier)
            base.update(row)
            base["source_qa_status"]="SENSOR_SOURCE_COMPUTED_NOT_CALIBRATED"
        except (ValueError,KeyError,OSError,RuntimeError) as exc:
            # Retain all original source-selected deployments and explicit
            # reasons; quality failures must not be erased from denominators.
            base["source_qa_status"]="SOURCE_QA_STOP"
            base["source_failure_type"]=type(exc).__name__
            base["source_failure_reason"]=str(exc)[:200]
        output.append(base)
        if (i+1)%50==0:
            print("source_qa_processed",i+1,"of",len(ids),flush=True)
    return output,meta

def summarize(rows,meta):
    group={}
    for island in ("LI","PI","MI","SI"):
        d=[r for r in rows if r["original_island"]==island]
        good=[r for r in d if r["source_qa_status"]=="SENSOR_SOURCE_COMPUTED_NOT_CALIBRATED"]
        drift=[r for r in good if r["q01_hourly_drift_gt_2dbar"]]
        rangevals=[r["q01_hourly_range_dbar"] for r in good]
        group[island]={
            "original_source_matches":len(d),
            "pressure_timeline_source_QA_computed":len(good),
            "source_QA_stop":len(d)-len(good),
            "q01_hourly_drift_above_2dbar_n":len(drift),
            "q01_hourly_drift_median_dbar":statistics.median(rangevals) if rangevals else None,
            "q01_hourly_drift_max_dbar":max(rangevals) if rangevals else None,
            "q01_hourly_drift_flag_is_not_ecological_quality_pass":True
        }
    return {
      "status":"ALL_300_ORIGINAL_CHINSTRAP_TDR_PRESSURE_SENSOR_SOURCE_QA_NOT_DIVE_ECOLOGY",
      "date":"2026-10-31",
      "original_sources":{"TDR":"10.5285/da13e049-be2b-4345-bbdd-ab960cb24731",
                           "GPS":"10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92"},
      "source_ID_matching_metadata":meta["joint_island_support"],
      "canonical_source_TDR_CRC_manifest":meta["source_central_manifest_hashes"]["tdr"],
      "source_matched_deployments":len(rows),
      "source_QA_computed_count":sum(x["source_qa_status"]=="SENSOR_SOURCE_COMPUTED_NOT_CALIBRATED" for x in rows),
      "pressure_QA_not_computed_count":sum(x["source_qa_status"]!="SENSOR_SOURCE_COMPUTED_NOT_CALIBRATED" for x in rows),
      "island_source_summary":group,
      "instrument_drift_diagnostic_gt_2dbar":"flag only; not external surface-depth calibration",
      "source_counting_rule":"300 native original GPS/TDR publisher IDs retained as observation units with source QA STOP reasons",
      "limitations":[
        "This is original source instrument QA across deployed tags, not a random breeding population sample or 300 independent environmental conditions.",
        "The hourly lower percentile can change with dive/land/air exposure and is not proof of verified ocean-surface zero depth.",
        "Pressure-to-depth absolute conversion, GPS/TDR external clock offset, true diving, marine foraging and krill catch not established.",
        "High/low pressure drift values do not imply species or island ecology, prey capture, nesting habitat or population decline.",
        "Freer 2025 modelled krill already used original IMR acoustic data and sea-ice/salinity, not independent prey observations.",
        "No new climate→reproduction→breeding-space future prediction is authorized."
      ]
    }

def verify(rows,meta):
    vals={r["original_deployment_id"]:r for r in rows}
    if len(rows)!=300 or len(vals)!=300:
        raise ValueError("all source 300 candidate IDs not retained")
    for tag,expected in KNOWN_PILOT.items():
        r=vals[tag]
        if r["source_qa_status"]!="SENSOR_SOURCE_COMPUTED_NOT_CALIBRATED":
            raise ValueError("previous fixed known pilot source failed "+tag)
        if not math.isclose(r["q01_hourly_range_dbar"],expected,abs_tol=0.0003):
            raise ValueError("source q1/60min calibration range does not reproduce "+tag)
    if {tag[:2] for tag in vals}!={"LI","PI","MI","SI"}:
        raise ValueError("missing original BAS island in 300 source QA")
    return True

def save(path,rows):
    keys=sorted(set().union(*(set(x) for x in rows)))
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys)
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tdr-zip",required=True,type=Path)
    p.add_argument("--gps-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    rows,meta=run(a.tdr_zip,a.gps_zip)
    result=summarize(rows,meta)
    if a.check:verify(rows,meta)
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"all_300_original_sensor_QA.csv",rows)
    (a.out/"decision.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
