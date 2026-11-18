"""Post-result original-TDR anomaly diagnosis, NOT penguin dive inference.

Selected because *source-only* all-300 q1/60min baseline span >100 dbar
(PI011, PI054, SIC033, SIC036, SIC039), or exact timestamp collisions
>100k source rows (PI009). Sensor and timestamp semantics are unresolved.
Do not treat these anomalies as confirmed technical failures or biology.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics,zipfile
from collections import Counter
from pathlib import Path
import numpy as np
import chinstrap_tdr_pressure_gps_pilot_v1 as pilot
import chinstrap_v2_tdr_gps_source_gate as gate
SOURCE_TAGS={
 "PI011":407.7,"PI054":404.4,"SIC033":125.94,
 "SIC036":255.94,"SIC039":255.94,"PI009":0.3
}
def within_timestamp_source(raw):
    first={}
    n_repeat=0;n_repeat_different=0
    counts=Counter()
    min_time=None;max_time=None
    for timestamp,pres in raw:
        counts[timestamp]+=1
        if min_time is None or timestamp<min_time:min_time=timestamp
        if max_time is None or timestamp>max_time:max_time=timestamp
        if timestamp in first:
            n_repeat+=1
            prior=first[timestamp]
            if (math.isfinite(pres) and math.isfinite(prior)
                and abs(pres-prior)>1e-6):
                n_repeat_different+=1
        else:
            first[timestamp]=pres
    return {"source_original_rows":len(raw),
            "distinct_original_clock_timestamps":len(first),
            "same_timestamp_extra_records":n_repeat,
            "same_timestamp_different_pressure_from_first":n_repeat_different,
            "timestamp_groups_more_than_1_record":sum(n>1 for n in counts.values()),
            "maximum_records_at_one_timestamp":max(counts.values()) if counts else 0,
            "start_original_time":min_time.isoformat() if min_time else None,
            "end_original_time":max_time.isoformat() if max_time else None}

def hourly_original_range(t,p):
    ix=np.floor((t-t[0])/3600).astype(np.int64)
    groups,start=np.unique(ix,return_index=True)
    stop=np.r_[start[1:],len(p)]
    source=[]
    for g,a,b in zip(groups,start,stop):
        if b-a<300:continue
        win=p[a:b]
        source.append((int(g),float(np.percentile(win,1)),float(np.percentile(win,5)),
                       float(np.median(win)),len(win)))
    if len(source)<3:raise ValueError("source has no valid 3 hour windows")
    q01=[s[1] for s in source]
    q05=[s[2] for s in source]
    worst=max(source,key=lambda x:x[1])
    lowest=min(source,key=lambda x:x[1])
    return {
       "original_60min_hour_windows":len(groups),
       "valid_60min_quantile_windows":len(source),
       "hourly_q01_baseline_range_dbar":max(q01)-min(q01),
       "hourly_q05_baseline_range_dbar":max(q05)-min(q05),
       "source_hours_q01_above_50dbar":sum(x>50 for x in q01),
       "source_hours_q01_above_100dbar":sum(x>100 for x in q01),
       "source_hours_q01_below_minus_20dbar":sum(x<(-20) for x in q01),
       "source_highest_q01_hour_index":worst[0],
       "source_highest_q01_hour_q01_dbar":worst[1],
       "source_highest_q01_hour_median_pressure_dbar":worst[3],
       "source_lowest_q01_hour_index":lowest[0],
       "source_lowest_q01_hour_q01_dbar":lowest[1]
    }

def analyze(path):
    if not zipfile.is_zipfile(path):raise ValueError("not the original BAS TDR publisher ZIP")
    output=[]
    with zipfile.ZipFile(path) as z:
        for tag,expected in SOURCE_TAGS.items():
            original,member=pilot.reader(path,tag,"TDR")
            _,t,p,dups,invalid=pilot.get_clean_pressure(original)
            source=within_timestamp_source(original)
            seg=hourly_original_range(t,p)
            if not math.isclose(seg["hourly_q01_baseline_range_dbar"],expected,abs_tol=0.001):
                raise ValueError("source original raw pressure differs from prior all-300 QC: "+tag)
            selected=[n for n in z.namelist() if Path(n).name==Path(member).name]
            if len(selected)!=1:raise ValueError("original raw TDR content member ambiguous")
            data=z.read(selected[0])
            out={
                "source_deployment_id":tag,
                "source_original_TDR_name":Path(member).name,
                "source_original_member_sha256":hashlib.sha256(data).hexdigest(),
                "source_original_member_bytes":len(data),
                **source,**seg,
                "source_pressure_n_invalid":invalid,
                "source_timestamp_duplicates_after_first":dups,
                "native_pressure_q01_dbar":float(np.percentile(p,1)),
                "native_pressure_median_dbar":float(np.median(p)),
                "native_pressure_q99_dbar":float(np.percentile(p,99)),
                "native_pressure_min_dbar":float(np.min(p)),
                "native_pressure_max_dbar":float(np.max(p)),
                "native_pressure_fraction_gt_100dbar":float(np.mean(p>100)),
                "native_pressure_fraction_lt_minus_20dbar":float(np.mean(p<(-20))),
                "pressure_baseline_extreme_is_not_validated_diving":True
            }
            output.append(out)
    return output

def verify(result):
    if len(result)!=6 or {x["source_deployment_id"] for x in result}!=set(SOURCE_TAGS):
        raise ValueError("original instrument abnormal tag ID support changed")
    dup=next(x for x in result if x["source_deployment_id"]=="PI009")
    if dup["same_timestamp_extra_records"]!=668268:
        raise ValueError("source 668268 duplicate timestamps not recovered")
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-tdr-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    result=analyze(a.original_tdr_zip)
    if a.check:verify(result)
    a.out.mkdir(parents=True,exist_ok=True)
    keys=list(result[0])
    with (a.out/"original_source_6tag_anomalies.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader();writer.writerows(result)
    document={
      "status":"POST_RESULT_ORIGINAL_TDR_INSTRUMENT_ANOMALY_TRACE_DIAGNOSTIC_NO_BIOLOGY",
      "original_DOI":"10.5285/da13e049-be2b-4345-bbdd-ab960cb24731",
      "source_selected_ids":list(SOURCE_TAGS),
      "source_300_QA_workflow":"https://github.com/zuizui0223/mina/actions/runs/41177252296",
      "original_source_tags":result,
      "limits":[
        "Source ID selection is deliberately post-result after high q1 span or duplicate timestamps, never a confirmatory ecology sample.",
        "Extreme pressure quantiles might reflect sensor offset, other metadata, non-surface windows or corrupted values; no causes assigned without source-based inspection.",
        "Pressure >100dbar is not automatically a penguin dive; origin and zero-offset are uncalibrated.",
        "Repeated same-second timestamps may reflect actual higher-frequency samples or duplicate logging; first-sample dedup cannot claim physical event fidelity.",
        "No island-level physiological or marine prey effect and no future penguin abundance forecast is calculated."
      ]
    }
    (a.out/"decision.json").write_text(json.dumps(document,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":document["status"],"findings":[{
       k:r[k] for k in ("source_deployment_id","same_timestamp_extra_records",
         "same_timestamp_different_pressure_from_first","maximum_records_at_one_timestamp",
         "hourly_q01_baseline_range_dbar","source_hours_q01_above_50dbar",
         "native_pressure_fraction_gt_100dbar")
    } for r in result]},ensure_ascii=False))
if __name__=="__main__":main()
