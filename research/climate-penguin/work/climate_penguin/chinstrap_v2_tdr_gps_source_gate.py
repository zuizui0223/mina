"""Chinstrap BAS Version 2 source-only TDR/GPS deployment and column audit.

2026-10-31. Source-only: no pressure/dive thresholds or spatial krill effects.
Never treat missing GPS/TDR as nondiving, and never reuse V1 chinstrap TDR
because BAS explicitly corrected GPS/TDR mismatches in Version 2.
Uses ZIP central directory + small prefix per original TDR member; no full
decompression of potentially multi-GB 1Hz pressure records.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

TDR_DOI="10.5285/da13e049-be2b-4345-bbdd-ab960cb24731"
GPS_DOI="10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92"
ISLAND={"SI":"Signy","LI":"Laurie","PI":"Powell","MI":"Monroe"}
EXPECTED_GPS_ARCHIVE_CSV=313
EXPECTED_GPS_DIGEST="f56dc817aefefda41e509541d24a184f68644d12c0a1c28af8071717275101c9"

def is_track_name(name,suffix):
    base=Path(name).name
    return base.lower().endswith(".csv") and f"_{suffix.lower()}" in base.lower()

def get_id(name,suffix):
    base=Path(name).name
    stem=base[:-4]
    marker=f"_{suffix}"
    if marker.lower() not in stem.lower():
        raise ValueError("instrument code not in basename")
    id_=stem.split("_")[0]
    loc=id_[:2]
    legal=((loc in {"SI","LI","MI"} and re.fullmatch(loc+r"C[0-9]+",id_) is not None)
           or (loc=="PI" and re.fullmatch(r"PI[0-9]+",id_) is not None))
    if not legal or loc not in ISLAND:
        raise ValueError("unexpected publisher deployment ID "+id_)
    return id_,loc

def member_head(z, info):
    """Read just first ~32 KiB of decompressed CSV and parse headers/sample lines."""
    with z.open(info, "r") as f:
        raw=f.read(32768)
    if not raw:
        return {"header":[],"sample_rows_read":0,"first_csv_timestamp":"","has_pressure":False}
    text=None
    for enc in ("utf-8-sig","utf-8","cp1252","latin-1"):
        try:
            text=raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise ValueError("no text encoding")
    # Do not parse last truncated line as complete
    if len(raw)==32768 and "\n" in text:
        text=text[:text.rfind("\n")+1]
    rows=list(csv.reader(io.StringIO(text)))
    if not rows:
        return {"header":[],"sample_rows_read":0,"first_csv_timestamp":"","has_pressure":False}
    cols=[x.strip() for x in rows[0]]
    sample=[r for r in rows[1:] if r and any(x.strip() for x in r)][:10]
    date_i=next((i for i,x in enumerate(cols) if re.search("datetime|date.?time|timestamp",x,re.I)),None)
    pressure_cols=[x for x in cols if re.search("pressure|depth",x,re.I)]
    temperatures=[x for x in cols if re.search("temperature|temp",x,re.I)]
    time0=sample[0][date_i].strip() if sample and date_i is not None and date_i<len(sample[0]) else ""
    try:
        dt.datetime.fromisoformat(time0.replace("Z","+00:00"))
        parseable=bool(time0)
    except (ValueError,TypeError):
        parseable=False
    return {
        "header":cols,"sample_rows_read":len(sample),
        "has_datetime_col":date_i is not None,
        "has_pressure":bool(pressure_cols),
        "pressure_columns":pressure_cols,
        "temperature_columns":temperatures,
        "first_csv_timestamp":time0,
        "first_datetime_python_iso":parseable,
        "first_sample_widths":sorted(set(len(x) for x in sample)),
    }

def scan(path,suffix,check_expected=None):
    if not zipfile.is_zipfile(path):
        raise ValueError("publisher ZIP missing/not ZIP "+str(path))
    all_rows=[]
    seen={}
    aggregate=hashlib.sha256()
    zip_bytes=Path(path).stat().st_size
    with zipfile.ZipFile(path) as z:
        info=[x for x in z.infolist() if not x.is_dir() and is_track_name(x.filename,suffix)]
        info.sort(key=lambda x:Path(x.filename).name)
        if check_expected is not None and len(info)!=check_expected:
            raise ValueError(f"expected {check_expected} original {suffix} files; got {len(info)}")
        for item in info:
            name=Path(item.filename).name
            deploy,loc=get_id(name,suffix)
            h=member_head(z,item)
            row={"deployment_id":deploy,"island_code":loc,"island_name":ISLAND[loc],
                 "original_member_path":item.filename,
                 "original_bytes_uncompressed":item.file_size,
                 "original_member_crc32":f"{item.CRC:08x}",
                 "compressed_member_bytes":item.compress_size,
                 "is_empty_or_header_only":item.file_size<120 or h["sample_rows_read"]==0,
                 **h}
            all_rows.append(row)
            if deploy in seen:
                # duplicate original source members may be same or different;
                # preserve all, do not silently choose.
                row["duplicate_deployment_name"]=True
                seen[deploy]["duplicate_deployment_name"]=True
            else:
                row["duplicate_deployment_name"]=False
                seen[deploy]=row
            # central directory is only CRC evidence; full content SHA must
            # be computed when source event rows are opened in v2.
            aggregate.update(name.encode()+b"\0"+str(item.file_size).encode()
                             +b"\0"+f"{item.CRC:08x}".encode()+b"\0")
    return {
       "source_zip_size":zip_bytes,"source_member_count":len(all_rows),
       "distinct_deployment_ids":len(seen),
       "files_with_no_sample_rows":sum(z["is_empty_or_header_only"] for z in all_rows),
       "duplicated_deployment_files":sum(z["duplicate_deployment_name"] for z in all_rows),
       "source_uncompressed_track_bytes":sum(z["original_bytes_uncompressed"] for z in all_rows),
       "central_directory_manifest_sha256":aggregate.hexdigest(),
       "island_roster":dict(sorted(Counter(z["island_name"] for z in all_rows).items())),
       "header_shapes":dict(sorted(Counter(tuple(z["header"]) for z in all_rows).items(),key=lambda x:-x[1])),
       "rows":all_rows
    }

def analyze(tdr_source,gps_source):
    gps=scan(gps_source,"GPS",EXPECTED_GPS_ARCHIVE_CSV)
    tdr=scan(tdr_source,"TDR")
    gp={x["deployment_id"] for x in gps["rows"] if not x["is_empty_or_header_only"]}
    dp={x["deployment_id"] for x in tdr["rows"] if not x["is_empty_or_header_only"]}
    all_both=sorted(gp&dp)
    by_island={}
    for key,name in ISLAND.items():
        g={s for s in gp if s.startswith(key)}
        d={s for s in dp if s.startswith(key)}
        by_island[name]={
            "gps_nonempty_unique":len(g),
            "tdr_nonempty_unique":len(d),
            "both_nonempty_unique":len(g&d),
            "gps_only":len(g-d),"tdr_only":len(d-g)
        }
    meta={
        "status":"ORIGINAL_BAS_CHINSTRAP_V2_GPS_TDR_SCHEMA_ONLY_NO_DIVES",
        "doi":{"GPS":GPS_DOI,"TDR":TDR_DOI},
        "data_version":"2.0 explicit GPS/TDR correction",
        "gps_source_member_count":gps["source_member_count"],
        "tdr_source_member_count":tdr["source_member_count"],
        "nonempty_gps_source_deployments":len(gp),
        "nonempty_tdr_source_deployments":len(dp),
        "joint_nonempty_deployments":len(all_both),
        "joint_island_support":by_island,
        "tdr_headers":{str(k):v for k,v in tdr["header_shapes"].items()},
        "gps_headers":{str(k):v for k,v in gps["header_shapes"].items()},
        "tdr_uncompressed_total_bytes":tdr["source_uncompressed_track_bytes"],
        "tdr_date_iso_first_sample_count":sum(z["first_datetime_python_iso"] for z in tdr["rows"]),
        "tdr_pressure_header_count":sum(z["has_pressure"] for z in tdr["rows"]),
        "GPS_nonempty_without_TDR":sorted(gp-dp),
        "TDR_nonempty_without_GPS":sorted(dp-gp),
        "TDR_duplicates":sorted(z["deployment_id"] for z in tdr["rows"] if z["duplicate_deployment_name"]),
        "GPS_duplicates":sorted(z["deployment_id"] for z in gps["rows"] if z["duplicate_deployment_name"]),
        "original_GPS_canonical_prior_SHA256":EXPECTED_GPS_DIGEST,
        "source_central_manifest_hashes":{
            "gps":gps["central_directory_manifest_sha256"],
            "tdr":tdr["central_directory_manifest_sha256"]
        },
        "limits":[
            "TDR pressure is reported in dbar and needs baseline/zero-offset QC before being equated with depth or dive events.",
            "Metadata say 1-second TDR sampling, but real per-device time intervals and clock alignment are not yet validated.",
            "GPS original fixes and TDR are linked by publisher deployment ID, not necessarily perfectly synchronized clocks.",
            "Only ZIP central directory and tiny CSV prefixes opened, not original pressure outcomes or complete time series.",
            "Duplicate and missing files must be resolved, not interpreted as nondive events.",
            "Dive locations require independently checked GPS time gaps, interpolation uncertainty and ocean/land mask.",
            "No krill capture, salinity effect, future climate elasticity, nest count or N_eff forecast can be inferred from a dive event."
        ]
    }
    return meta,gps,tdr,all_both

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gps-zip",required=True,type=Path)
    p.add_argument("--tdr-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    meta,gps,tdr,ids=analyze(a.tdr_zip,a.gps_zip)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"source_gate.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (a.out/"gps_tdr_joint_deployment_ids.txt").write_text("\n".join(ids)+"\n",encoding="utf-8")
    (a.out/"TDR_source_member_header_manifest.json").write_text(json.dumps(tdr["rows"],indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":meta["status"],"source_gps":meta["gps_source_member_count"],
        "source_tdr":meta["tdr_source_member_count"],
        "joint":meta["joint_nonempty_deployments"],
        "island_support":meta["joint_island_support"],
        "pressure_files":meta["tdr_pressure_header_count"],
        "first_date_iso_files":meta["tdr_date_iso_first_sample_count"],
        "tdr_header_samples":tdr["rows"][:3],
        "tdr_uncompressed_bytes":meta["tdr_uncompressed_total_bytes"]
    },ensure_ascii=False))

if __name__=="__main__":
    main()
