"""BAS Chinstrap V2 original GPS time-gap bracketability audit.

Measured time between exact original GPS fixes. An apparent 85–98% of
*intervals* <=10min can account for only 30–72% of *elapsed GPS-record time*
because gaps are long. This is NOT TDR time coverage and not a dive location.
Source-member SHA pinned to prior first-party GPS audit; no krill/prey or stage.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import statistics
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

DOI="10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92"
EXPECTED_SOURCE_FILES=313
EXPECTED_PIN="f56dc817aefefda41e509541d24a184f68644d12c0a1c28af8071717275101c9"
CUTOFF_SEC=(300,600,1200)
SITES={"SI":"Signy","LI":"Laurie","PI":"Powell","MI":"Monroe"}

def extract(zip_path):
    if not zipfile.is_zipfile(zip_path):
        raise ValueError("missing original BAS Chinstrap V2 source ZIP")
    groups=defaultdict(list)
    all_tags=[]
    sha=hashlib.sha256()
    previous={}
    with zipfile.ZipFile(zip_path) as z:
        names=sorted(
            [n for n in z.namelist() if Path(n).name.endswith("_GPS.csv")],
            key=lambda n:Path(n).name
        )
        if len(names)!=EXPECTED_SOURCE_FILES:
            raise ValueError("original source GPS roster changed")
        for path in names:
            name=Path(path).name
            raw=z.read(path)
            digest=hashlib.sha256(raw).digest()
            sha.update(name.encode()+b"\0"+digest)
            deployment=name.split("_")[0]
            island=deployment[:2]
            if island not in SITES:
                raise ValueError("unknown original island ID")
            if deployment in previous:
                if previous[deployment]!=digest:
                    raise ValueError("conflicting duplicate deployment original GPS member")
                continue
            previous[deployment]=digest
            readings=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
            if not readings:
                continue
            if not {"DateTime","Latitude_degrees_north","Longitude_degrees_east"}<=readings[0].keys():
                raise ValueError("original GPS source field drift")
            times=sorted(set(dt.datetime.fromisoformat(r["DateTime"].replace("Z","+00:00")) for r in readings))
            if len(times)<2:
                continue
            y=times[0].year if times[0].month>=7 else times[0].year-1
            if any((t.year if t.month>=7 else t.year-1)!=y for t in times):
                raise ValueError("source deployment crosses breeding seasons")
            seconds=[(b-a).total_seconds() for a,b in zip(times,times[1:])]
            if any(x<=0 for x in seconds):
                raise ValueError("original GPS time not strictly increasing after dedup")
            record={
                "deployment":deployment,"island":island,"season":y,
                "observed_positions":len(readings),
                "unique_gps_fix_timestamps":len(times),
                "number_of_gaps":len(seconds),
                "median_gap_seconds":statistics.median(seconds),
                "elapsed_gps_span_hours":sum(seconds)/3600,
                "gaps_over_30minutes":sum(x>1800 for x in seconds),
                "fraction_gap_count_over_30minutes":sum(x>1800 for x in seconds)/len(seconds)
            }
            for cutoff in CUTOFF_SEC:
                record[f"gap_count_fraction_le_{cutoff}s"]=sum(v<=cutoff for v in seconds)/len(seconds)
                record[f"gap_elapsed_time_fraction_le_{cutoff}s"]=sum(v for v in seconds if v<=cutoff)/sum(seconds)
            all_tags.append(record)
            groups[island,y].append(seconds)
    if sha.hexdigest()!=EXPECTED_PIN:
        raise ValueError("original BAS GPS source member SHA drift")
    if len(all_tags)!=308:
        raise ValueError("original nonempty GPS deployment roster changed")
    expected={("LI",2011):60,("MI",2015):64,("PI",2013):68,
              ("SI",2011):11,("SI",2013):21,("SI",2015):26,("SI",2018):58}
    if {k:len(v) for k,v in groups.items()}!=expected:
        raise ValueError("original matched-year island roster changed")
    return all_tags,groups,sha.hexdigest()


def summarize(groups):
    result=[]
    for (site,year),tagged in sorted(groups.items()):
        seconds=[gap for tag in tagged for gap in tag]
        time=sum(seconds)
        record={
            "island":site,"island_name":SITES[site],"season_start":year,
            "n_gps_source_deployments":len(tagged),
            "n_original_fix_intervals":len(seconds),
            "median_source_fix_interval_s":statistics.median(seconds),
            "source_elapsed_time_hours":time/3600,
            "fraction_original_intervals_over_30min":sum(v>1800 for v in seconds)/len(seconds),
            "fraction_elapsed_time_over_30min":sum(v for v in seconds if v>1800)/time
        }
        for cutoff in CUTOFF_SEC:
            record[f"fraction_intervals_le_{cutoff}s"]=sum(v<=cutoff for v in seconds)/len(seconds)
            record[f"fraction_record_span_in_bracket_le_{cutoff}s"]=sum(v for v in seconds if v<=cutoff)/time
            record[f"median_deployment_time_coverage_le_{cutoff}s"]=statistics.median(
                sum(v for v in tag if v<=cutoff)/sum(tag) for tag in tagged)
        result.append(record)
    return result


def check(original,summary):
    if len(original)!=308 or len(summary)!=7:
        raise ValueError("source deployment or island-year support")
    expected={
        ("LI",2011):(28364,.348,.8727),
        ("MI",2015):(24277,.436,.8593),
        ("PI",2013):(41415,.321,.8565),
        ("SI",2011):(15539,.718,.9781),
        ("SI",2013):(18780,.396,.8764),
        ("SI",2015):(40944,.575,.9457),
        ("SI",2018):(45979,.300,.8645)
    }
    for r in summary:
        n,part,gap=expected[r["island"],r["season_start"]]
        if r["n_original_fix_intervals"]!=n:
            raise ValueError("source fix interval count changed")
        if abs(r["fraction_record_span_in_bracket_le_600s"]-part)>.001:
            raise ValueError("original time bracket support changed")
        if abs(r["fraction_intervals_le_600s"]-gap)>.001:
            raise ValueError("original fix-count bracket fraction changed")
    return True


def write(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gps-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    individual,byyear,sha=extract(args.gps_zip)
    summary=summarize(byyear)
    if args.check:check(individual,summary)
    args.out.mkdir(parents=True,exist_ok=True)
    write(args.out/"tag_gps_time_support.csv",individual)
    write(args.out/"island_year_gps_time_support.csv",summary)
    result={
        "status":"OBSERVED_ORIGINAL_GPS_INTERFIX_TIME_COVERAGE_NOT_DIVE_POSITION",
        "original_DOI":DOI,"original_member_sha256":sha,
        "n_source_deployments":len(individual),
        "n_interfix_intervals":sum(r["n_original_fix_intervals"] for r in summary),
        "n_island_years":len(summary),
        "strict_bracket_primary_seconds":600,
        "bracket_sensitivities_seconds":list(CUTOFF_SEC),
        "important_bias":"Count fraction of short intervals differs from elapsed-time fraction, so nearest-GPS filtering may select different fractions of diving time between islands.",
        "limitations":[
          "This is elapsed time spanning original GPS fixes, NOT observed diving time or a verified TDR intersection.",
          "Neither pressure offsets nor TDR clock alignment nor per-tag dive overlap are quantified.",
          "GPS track lengths, duty cycles and deployment selection vary by year and island.",
          "These are different islands in mostly different years; no independent krill or future climate causal effect.",
          "Time coverage of source gaps alone does not establish accurate GPS position at a dive, even with two nearby fixes."
        ]}
    (args.out/"decision.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"digest":sha,"status":result["status"],
      "tags":len(individual),"original_fix_intervals":result["n_interfix_intervals"],
      "island_year_time_fraction_le_600s":{
          f"{r['island']}/{r['season_start']}":r["fraction_record_span_in_bracket_le_600s"] for r in summary},
      "checked":args.check},ensure_ascii=False))

if __name__=="__main__":
    main()
