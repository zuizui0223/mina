"""BAS Chinstrap 300 source GPS/TDR original observability QA selection.

Input is the original successful 300-tag source audit artifact from run
41177252296. Full denominator retained. Post-exposure sensor/logging criteria
are NOT independent surface zero, true diving, prey catch or climate effects.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from collections import Counter

INPUT_SHA="a985b036716bf18f1356988ccba08374ab3b0b97c579f53a86f5bef07f4207fc"
RUN="https://github.com/zuizui0223/mina/actions/runs/41177252296"
ISLANDS=("LI","MI","PI","SI")
EXPECTED={"LI":(60,39,14),"MI":(64,27,8),"PI":(68,45,7),"SI":(108,79,23)}

def read(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=INPUT_SHA:
        raise ValueError("source-recomputed all-300 original CSV SHA mismatch")
    vals=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if len(vals)!=300 or len({r["original_deployment_id"] for r in vals})!=300:
        raise ValueError("source original unique deployment roster changed")
    if any(r["source_qa_status"]!="SENSOR_SOURCE_COMPUTED_NOT_CALIBRATED" for r in vals):
        raise ValueError("one or more source original tags lacks instrument QA")
    return vals

def evaluate(rows):
    out=[]
    for r in rows:
        q01=float(r["q01_hourly_range_dbar"])
        q05=float(r["q05_hourly_range_dbar"])
        dup=int(r["source_pressure_n_duplicate_timestamp"])
        overlap=float(r["fraction_TDR_time_inside_GPS_window"])
        gps=float(r["GPS_time_fraction_recorded_gaps_10min_or_less"])
        if r["original_island"] not in ISLANDS or not (0<=overlap<=1 and 0<=gps<=1 and q01>=0 and q05>=0 and dup>=0):
            raise ValueError("invalid source original instrument QA domain")
        q1=(q01<=2)
        q5=(q05<=2)
        unique=(dup==0)
        aligned=(overlap>=.5)
        gps20=(gps>=.2)
        gps50=(gps>=.5)
        base=q1 and q5 and unique and aligned and gps20
        out.append({
            "original_source_id":r["original_deployment_id"],
            "original_island":r["original_island"],
            "q01_range_dbar":q01,"q05_range_dbar":q05,
            "original_pressure_duplicate_timestamps":dup,
            "TDR_window_in_GPS_fraction":overlap,
            "GPS_recorded_intervals_le10min_fraction":gps,
            "q01_le2":q1,"q05_le2":q5,
            "no_original_time_duplicate":unique,
            "time_overlap_ge50pct":aligned,
            "GPS_coverage_ge20pct":gps20,
            "GPS_coverage_ge50pct":gps50,
            "primary_source_observability":base,
            "strict_GPS_sensitivity":base and gps50,
            "q01_only_sensitivity":q1 and unique and aligned and gps20,
            "observation_not_validated_dive_or_foraging":True,
            "failure_reasons":";".join(x for x,v in (
                ("q01_gt2",q1),("q05_gt2",q5),("timestamp_duplicate",unique),
                ("TDR_GPS_overlap_below50pct",aligned),("GPS_coverage_below20pct",gps20)) if not v)
        })
    return out

def summary(rows):
    counts=Counter()
    by={}
    for island in ISLANDS:
        sub=[r for r in rows if r["original_island"]==island]
        by[island]={"original_source":len(sub),
            "primary":sum(x["primary_source_observability"] for x in sub),
            "strict":sum(x["strict_GPS_sensitivity"] for x in sub),
            "q01_only":sum(x["q01_only_sensitivity"] for x in sub),
            "q01_outside":sum(not x["q01_le2"] for x in sub),
            "q05_outside":sum(not x["q05_le2"] for x in sub)}
    keys=("q01_le2","q05_le2","no_original_time_duplicate","time_overlap_ge50pct",
          "GPS_coverage_ge20pct","GPS_coverage_ge50pct","primary_source_observability",
          "strict_GPS_sensitivity","q01_only_sensitivity")
    for k in keys:counts[k]=sum(r[k] for r in rows)
    return dict(counts),by

def verify(counts,by):
    expected={"q01_le2":258,"q05_le2":267,"no_original_time_duplicate":299,
              "time_overlap_ge50pct":287,"GPS_coverage_ge20pct":230,
              "GPS_coverage_ge50pct":73,"primary_source_observability":190,
              "strict_GPS_sensitivity":52,"q01_only_sensitivity":191}
    if counts!=expected:raise ValueError(f"source numerical receipt changed: {counts}")
    if any((by[k]["original_source"],by[k]["primary"],by[k]["strict"])!=v for k,v in EXPECTED.items()):
        raise ValueError("original four-island source QA receipt drift")
    return True

def save(path,records):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]))
        w.writeheader();w.writerows(records)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-qa",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    r=evaluate(read(args.original_qa))
    count,islands=summary(r)
    if args.check:verify(count,islands)
    args.out.mkdir(parents=True,exist_ok=True)
    save(args.out/"all_300_operational_source_tags.csv",r)
    save(args.out/"island_coverage.csv",[{"island":x,**a} for x,a in islands.items()])
    decision={
        "status":"DESCRIPTIVE_POST_SOURCE_TDR_GPS_OBSERVABILITY_NOT_TRUE_DIVE_ECOLOGY",
        "original_300_run":RUN,"source_CSV_sha256":INPUT_SHA,
        "original_source_n":len(r),
        "primary_count":count["primary_source_observability"],
        "stricter_count":count["strict_GPS_sensitivity"],
        "source_counts":count,"source_island_coverage":islands,
        "screening_criteria_post_source_not_preregistered":(
            "Both q01 and q05 60min baseline candidate spans <=2dbar; "
            "no same timestamp pressure duplicate; TDR within GPS window >=50%; "
            "GPS <=10min gaps cover >=20% original timeline; stricter >=50%"),
        "no_source_rows_dropped":True,
        "cautions":[
            "Source-only sensor/time observability, not an external sea surface zero correction or observed depth.",
            "Neither GPS source visibility nor pressure duration identifies foraging or captured krill.",
            "Island confounded with year and deployment protocol; do not interpret island tier counts as ecology.",
            "Source artifact may expire; rerun original 300tag BAS source census and match input SHA.",
            "No sea-ice/salinity→prey→reproduction→breeding-space 2050/2100 forecast is validated."
        ]}
    (args.out/"decision.json").write_text(json.dumps(decision,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"source_n":len(r),"counts":count,"islands":islands,"check":bool(args.check)},ensure_ascii=False))
if __name__=="__main__":
    main()
