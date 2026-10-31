"""Fuse two immutable source-QA artifacts without approving ecological inference."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
ALL_SHA="a985b036716bf18f1356988ccba08374ab3b0b97c579f53a86f5bef07f4207fc"
SIX_SHA="aae4af287ad7fed0a3b08d00464abe6ac01c8d98fea6ee23bffe07dbd64117b6"
HARD={"PI009","PI011","PI054","SIC033","SIC036","SIC039"}
EXPECTED={"n":300,"q1":42,"q5":33,"any_q":43,"hard":6,
          "low_overlap":13,"low_timing":227,"any_timing":240,"no_flag":52}
def reader(path,sha):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("immutable source receipt changed "+str(path))
    return list(csv.DictReader(raw.decode("utf-8").splitlines()))
def classify(row,anomaly=None):
    key=row["original_deployment_id"]
    q1,q5=float(row["q01_hourly_range_dbar"]),float(row["q05_hourly_range_dbar"])
    overlap=float(row["fraction_TDR_time_inside_GPS_window"])
    short=float(row["GPS_time_fraction_recorded_gaps_10min_or_less"])
    if row["source_qa_status"]!="SENSOR_SOURCE_COMPUTED_NOT_CALIBRATED":
        raise ValueError("source QA status not computed "+key)
    if (key in HARD)!=(anomaly is not None):
        raise ValueError("source-selected six original members not joined "+key)
    timestamp=(anomaly is not None and int(anomaly["same_timestamp_different_pressure_from_first"])>0)
    extreme=q1>100
    if key in HARD and not(timestamp or extreme):
        raise ValueError("6-source original extreme receipt changed "+key)
    return {
      "source_ID":key,"island":row["original_island"],
      "source_pressure_rows":int(row["source_pressure_n_original"]),
      "original_duplicate_time_rows":int(row["source_pressure_n_duplicate_timestamp"]),
      "q1_range_dbar":q1,"q5_range_dbar":q5,
      "clock_native_multivalued_pressure":timestamp,
      "extreme_hourly_q1_span_gt100":extreme,
      "provisional_q1_range_gt2":q1>2,"provisional_q5_range_gt2":q5>2,
      "GPS_TDR_source_span_overlap_lt50":overlap<.5,
      "GPS_time_short_gaps_coverage_lt50":short<.5,
      "needs_publisher_original_trace_review":timestamp or extreme,
      "needs_provisional_surface_offset_review":q1>2 or q5>2,
      "GPS_time_support_limited":overlap<.5 or short<.5,
      "none_of_these_automated_warnings":not(timestamp or extreme or q1>2 or q5>2 or overlap<.5 or short<.5),
      "calibration_independently_verified":False,
      "ecologically_approved_dive_or_foraging_track":False}
def run(path300,path6):
    rows=reader(path300,ALL_SHA)
    six=reader(path6,SIX_SHA)
    by={x["source_deployment_id"]:x for x in six}
    if set(by)!=HARD or len(rows)!=300 or len({x["original_deployment_id"] for x in rows})!=300:
        raise ValueError("source original ID denominator is not fixed")
    result=[classify(row,by.get(row["original_deployment_id"])) for row in rows]
    def count(k):return sum(r[k] for r in result)
    summary={"n":len(result),"q1":count("provisional_q1_range_gt2"),
             "q5":count("provisional_q5_range_gt2"),
             "any_q":count("needs_provisional_surface_offset_review"),
             "hard":count("needs_publisher_original_trace_review"),
             "low_overlap":count("GPS_TDR_source_span_overlap_lt50"),
             "low_timing":count("GPS_time_short_gaps_coverage_lt50"),
             "any_timing":count("GPS_time_support_limited"),
             "no_flag":count("none_of_these_automated_warnings")}
    if summary!=EXPECTED:raise ValueError("original source cohort counts drifted "+str(summary))
    island={}
    for site in sorted({r["island"] for r in result}):
        sub=[r for r in result if r["island"]==site]
        island[site]={
          "original_tags":len(sub),
          "original_source_HOLD":sum(r["needs_publisher_original_trace_review"] for r in sub),
          "offset_QA_review":sum(r["needs_provisional_surface_offset_review"] for r in sub),
          "time_source_review":sum(r["GPS_time_support_limited"] for r in sub),
          "no_automated_flags_but_not_ecological_certification":sum(r["none_of_these_automated_warnings"] for r in sub)}
    decision={
      "status":"300_SOURCE_INSTRUMENT_AND_GPS_TIME_FLAGS_0_ECOLOGICALLY_VALIDATED",
      "immutable_inputs":{"all300_sha256":ALL_SHA,"six_original_trace_sha256":SIX_SHA},
      "source_ci":{"all300":41177252296,"six_original":41177957583},
      "counts":summary,"by_island":island,"ecologically_approved_tags":0,
      "warnings":[
        "Automatic absence of listed issues in 52 tracks is not validated sensor surface, true depth, GPS/TDR clock or krill capture.",
        "PI009 has different original pressure samples within one published timestamp and must not undergo naive first-record dedup for dive timing.",
        "Five source traces exceed 100dbar hourly lower-quantile range, not demonstrated penguin dive depth.",
        "Q1/Q5 >2dbar is exploratory pressure instrument QA, not sensor failure incidence.",
        "GPS gaps and overlapping recording timelines determine event geolocation selection, not biological dive effort.",
        "No source-only instrument result estimates climate, salinity, breeding or vegetation mechanism."
      ]}
    return result,decision
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source300",required=True,type=Path)
    ap.add_argument("--source6",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    a=ap.parse_args();rows,decision=run(a.source300,a.source6)
    a.out.mkdir(parents=True,exist_ok=True)
    with (a.out/"all_300_original_source_QA_status.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (a.out/"decision.json").write_text(json.dumps(decision,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":decision["status"],"counts":decision["counts"],"islands":decision["by_island"]},ensure_ascii=False))
if __name__=="__main__":main()
