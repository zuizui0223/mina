"""Inspect ORIGINAL BAS Signy three-penguin-species GPS source structure.

Source-only gate: no location-density, foraging distance, krill-index effect,
spatial fit or fledgling response is computed. This establishes physical
observed-trajectory coverage before replacing arbitrary colony-centred buffers.
Do not treat tags/positions as independent regional climate replicates.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter,defaultdict
from pathlib import Path

SOURCES={
 "Adelie":{"doi":"10.5285/55b4d36f-c5e1-4d64-bb14-0b832dcd4b88",
           "entry_id":"55b4d36f-c5e1-4d64-bb14-0b832dcd4b88","species_code":"A",
           "published_scope":"Signy 2011-2016"},
 "Chinstrap":{"doi":"10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92",
           "entry_id":"8f8ccba5-01af-4b00-8a3b-c3c85b24bf92","species_code":"C",
           "published_scope":"South Orkney sites 2011-2019, Version 2.0"},
 "Gentoo":{"doi":"10.5285/9cb04ca6-f88f-4368-b715-45ff73ff81eb",
           "entry_id":"9cb04ca6-f88f-4368-b715-45ff73ff81eb","species_code":"G",
           "published_scope":"Signy 2011-2016"}
}

def metadata_csv(raw, name):
    text=None
    for enc in ("utf-8-sig","utf-8","cp1252","latin-1"):
        try:
            text=raw.decode(enc)
            break
        except UnicodeDecodeError: pass
    if text is None:
        raise ValueError("no supported CSV text encoding: "+name)
    f=io.StringIO(text)
    reader=csv.reader(f)
    head=next(reader,[])
    rows=0
    for x in reader:
        if x and any(str(z).strip() for z in x):
            rows+=1
    return {
        "original_member":name,
        "original_member_sha256":hashlib.sha256(raw).hexdigest(),
        "bytes":len(raw),
        "header":[str(x).strip() for x in head],
        "nonempty_rows":rows,
        "header_has_datetime_candidate":any(re.search(r"time|date",x,re.I) for x in head),
        "header_has_lat_candidate":any(re.search(r"(^lat$|latitude)",x,re.I) for x in head),
        "header_has_lon_candidate":any(re.search(r"(^lon$|^long$|longitude)",x,re.I) for x in head),
        "original_position_numeric_values_opened":False,
        "original_bird_attributes_opened":False
    }


def visit(species, source):
    info=SOURCES[species]
    if not zipfile.is_zipfile(source):
        raise ValueError("Publisher GPS source ZIP invalid: "+species)
    result=[]
    with zipfile.ZipFile(source) as z:
        for f in sorted(z.infolist(),key=lambda x:x.filename):
            if f.is_dir():
                continue
            if f.filename.lower().endswith(".csv"):
                item=metadata_csv(z.read(f.filename),f.filename)
                name=Path(f.filename).name
                token=re.sub(r"[^A-Za-z0-9]","",name).upper()
                item["site_prefix_signy"]=token.startswith("SI")
                item["species_code_prefix_correct"]=token.startswith("SI"+info["species_code"])
                item["gps_in_filename"]="GPS" in name.upper()
                item["looks_like_gps_track"]=bool(
                    item["species_code_prefix_correct"]
                    and item["gps_in_filename"]
                    and item["header_has_datetime_candidate"]
                    and item["header_has_lat_candidate"]
                    and item["header_has_lon_candidate"]
                )
                result.append(item)
    gps=[x for x in result if x["looks_like_gps_track"]]
    track_candidates=[x for x in result if x["gps_in_filename"]
                      and x["header_has_lat_candidate"] and x["header_has_lon_candidate"]]
    missing_headers=[x["original_member"] for x in result if
                     x["species_code_prefix_correct"] and x["gps_in_filename"]
                     and not x["looks_like_gps_track"]]
    return {
        "doi":info["doi"],
        "source_url":f"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid={info['entry_id']}&output=zip.tree",
        "publisher_scope":info["published_scope"],
        "zip_wrapper_sha256":hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        "zip_size_bytes":Path(source).stat().st_size,
        "csv_member_count":len(result),
        "candidate_gps_csv_count_any_site":len(track_candidates),
        "signy_gps_track_csv_count_with_all_headers":len(gps),
        "signy_positions_row_count_potential":sum(x["nonempty_rows"] for x in gps),
        "signy_tracks_missing_expected_timestamp_or_coordinates":missing_headers,
        "other_sites_present":sum(not x["site_prefix_signy"] for x in track_candidates),
        "original_csvs":result
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    all={}
    for sp in SOURCES:
        src=a.root/(sp.lower()+".zip")
        all[sp]=visit(sp,src)
    report={
        "status":"BAS_PUBLISHER_GPS_SOURCE_HEADERS_ONLY_NO_POSITION_VALUES_OR_OUTCOMES",
        "date":"2026-10-30",
        "species":all,
        "track_availability_not_trajectory_analysis":True,
        "limits":[
            "GPS positions and bird metadata values not opened yet; no claim about actual foraging distances.",
            "Chinstrap Version 2.0 replaces the previously identified Version 1.0 mismatch.",
            "Different species, sites and deployment years; one row/point/tag is not an independent krill or climate observation.",
            "Must preserve exact deployment ID, date, land/offshore position filters and per-bird sampling before route-based spatial coupling.",
            "Source ZIP wrapper can be regenerated; freeze original member content hashes, not only wrapper SHA.",
            "A GPS point is not a confirmed foraging/prey-capture event without dive or behavior.",
            "Raster krill prediction includes fitted sea ice and salinity; GPS coupling alone cannot establish their independent causal role."
        ]
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":report["status"],
        "species":{s:{
            "zip_bytes":x["zip_size_bytes"],
            "csv_members":x["csv_member_count"],
            "candidate_gps_csv_any_site":x["candidate_gps_csv_count_any_site"],
            "signy_tracks_recognized":x["signy_gps_track_csv_count_with_all_headers"],
            "signy_position_rows_without_analysis":x["signy_positions_row_count_potential"],
            "other_sites_present":x["other_sites_present"],
            "sample_headers":[r["header"] for r in x["original_csvs"] if r["gps_in_filename"]][:2]
        } for s,x in all.items()}
    },ensure_ascii=False))


if __name__=="__main__":
    main()
