"""Independent 2020 Zavodovski UAV coordinate SOURCE HEADER ONLY.

No original bird/nest coordinate row is read. Potential year-2022
chinstrap imputation is explicitly forbidden. Source:
Hart et al. 2022, doi 10.5285/28222725-c53d-40f4-9350-49c368899f0b.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import quote, urlparse

import requests

ROOT="28222725-c53d-40f4-9350-49c368899f0b"
HOST="ramadda.data.bas.ac.uk"
FOLDER="synth:"+ROOT+":L1phdm9kb3Zza2kvY29vcmRpbmF0ZXM="
FILES=("ZAVO_2020_Macaroni_coordinates.csv",
       "ZAVO_2020_Mixed_species_coordinates.csv")
KNOWN_CRSPREVALENCE=("EPSG:4326","EPSG:32726")


def validate_headers(headers):
    norm=[re.sub(r"[^a-z0-9]+","_",str(v).strip().lower()).strip("_")
          for v in headers]
    if len(norm)<2 or not all(norm) or len(norm)!=len(set(norm)):
        return {"status":"HOLD_INVALID_NONUNIQUE_CSV_COLUMNS",
                "columns":headers,"normalized":norm,
                "nest_location_rows_read":0,"verified_crs":False}
    s=set(norm)
    lat=bool(s & {"latitude","lat","lat_dd","latitude_dd","gps_lat","y_lat"})
    lon=bool(s & {"longitude","long","lon","lng","longitude_dd","long_dd","gps_lon","x_lon"})
    east=bool(s & {"easting","utm_easting","utm_e","x","x_utm","x_coord","x_coordinate"})
    north=bool(s & {"northing","utm_northing","utm_n","y","y_utm","y_coord","y_coordinate"})
    possible_coords=bool((lat and lon) or (east and north))
    ids=[v for v in norm if v in {"site_id","colony_id","nest_id","point_id","feature_id",
                                    "plot_id","subcolony_id","sub_colony_id"}]
    return {"status":("PASS_POTENTIAL_COORDINATE_HEADER_CRS_UNVERIFIED"
                      if possible_coords else "HOLD_NO_PAIR_OF_COORDINATE_COLUMNS"),
            "columns":headers,"normalized":norm,
            "latitude_longitude_columns":lat and lon,
            "projected_xy_columns":east and north,
            "candidate_record_ids":ids,
            "verified_crs":False,
            "nest_location_rows_read":0,
            "note":"Coordinate headers establish only candidate syntax, not valid dated points, crs or 2020-only provenance."}


def first_csv_header(readline, max_comments=40, max_bytes=4096):
    pre=bytearray()
    for _ in range(max_comments+1):
        line=readline(1537)
        if not line or len(line)>1536 or b"\n" not in line:
            raise ValueError("SOURCE_STOP missing bounded header line")
        if line.strip()==b"" or line.lstrip(b"\xef\xbb\xbf \t").startswith(b"#"):
            if len(pre)+len(line)>max_bytes or len(pre)>max_bytes:
                raise ValueError("SOURCE_STOP source preamble too large")
            pre.extend(line)
            continue
        if line.lstrip().lower().startswith(b"<html"):
            raise ValueError("SOURCE_STOP HTML instead of CSV")
        if line.count(b",")<1:
            raise ValueError("SOURCE_STOP first noncomment is not comma-separated CSV")
        header=line.decode("utf-8-sig").strip("\r\n")
        cols=next(csv.reader(io.StringIO(header)))
        return cols, {"publisher_comment_preamble_sha256":hashlib.sha256(pre).hexdigest(),
                      "publisher_comment_bytes_read":len(pre),
                      "first_data_header_bytes_read":len(line),
                      "first_data_header_sha256":hashlib.sha256(line).hexdigest()}
    raise ValueError("SOURCE_STOP no header in bounded preamble")


def publisher_url(session, filename):
    folder=("https://"+HOST+"/repository/entry/show?entryid="+
            quote(FOLDER,safe="")+"&output=default.csv")
    with session.get(folder,timeout=40,allow_redirects=True) as resp:
        resp.raise_for_status()
        final=urlparse(resp.url)
        if final.scheme!="https" or final.hostname not in {HOST,"194.66.5.50"}:
            raise ValueError("SOURCE_STOP manifest redirect outside publisher")
        if len(resp.content)>100000:
            raise ValueError("SOURCE_STOP manifest too large")
        records=list(csv.DictReader(io.StringIO(resp.text)))
    selected=[r for r in records if r.get("name")==filename]
    if len(selected)!=1 or not selected[0].get("url"):
        raise ValueError("SOURCE_STOP missing or duplicate expected file")
    link=selected[0]["url"]
    parsed=urlparse(link)
    if parsed.hostname!=HOST or parsed.path!="/repository/entry/get/"+filename or parsed.scheme not in ("http","https") or parsed.port not in (None,443):
        raise ValueError("SOURCE_STOP unsafe manifest path")
    return "https://"+HOST+parsed.path+"?"+parsed.query


def examine_first_header(session, filename):
    url=publisher_url(session,filename)
    with session.get(url,stream=True,timeout=(15,45),allow_redirects=True) as resp:
        resp.raise_for_status()
        final=urlparse(resp.url)
        if final.scheme!="https" or final.hostname not in {HOST,"194.66.5.50"}:
            raise ValueError("SOURCE_STOP data redirect outside publisher")
        cols,pre=first_csv_header(resp.raw.readline)
        result=validate_headers(cols)
        result.update(pre)
        result["source_filename"]=filename
        result["declared_content_length_bytes"]=resp.headers.get("Content-Length")
        result["original_nest_location_rows_read"]=0
        result["original_data_values_read"]=False
        return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    receipt={"status":"SOURCE_GATE_STOP","original_nest_location_rows_read":0}
    try:
        with requests.Session() as sess:
            files=[examine_first_header(sess,name) for name in FILES]
        receipt={"status":"POTENTIAL_SOURCE_HEADERS_READ_NO_BIOLOGICAL_ROWS",
                 "source_doi":"10.5285/28222725-c53d-40f4-9350-49c368899f0b",
                 "files":files,
                 "prohibited_year_misclassification":"ZAVO_2022_Chinstrap_coordinates.csv must never represent a 2020 contemporaneous chinstrap observation",
                 "original_nest_location_rows_read":0,
                 "source_stage":"HEADER_ONLY",
                 "biological_effect_computed":False}
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:300]
    Path(args.out).write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="SOURCE_GATE_STOP":
        raise SystemExit(2)

if __name__=="__main__":
    main()
