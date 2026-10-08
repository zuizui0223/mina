"""Inspect original published LaRue (2024) satellite image records of nine
already-exposed posterior mean 0 -> positive transitions. This is a retrospective
source-eligibility audit, NOT a test of real extinction, rescue or colonization.

XLSX uses Python standard-library ZIP/XML to run in GitHub Actions without
installing a different spreadsheet analysis package. The source is pinned to
its exact Git blob SHA. No biological outcomes from years 2022+ are opened.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/"results/EMPEROR_LARUE_2024_50_BY_10_POSTERIOR_ZERO_AUDIT_V1.json"
SOURCE_SHA="a964360e2cc9bc6303199e0971a4e7d40f793752"
SOURCE_URL="https://raw.githubusercontent.com/davidiles/EMPE_Global/13f71112da43c1fd082273677757b41c550457ed/data/empe_satellite_2023-05-25.xlsx"
M="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
P="{http://schemas.openxmlformats.org/package/2006/relationships}"
R="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REQUIRED={"site_id","img_year","bpresent"}


def git_blob(raw: bytes):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()


def address_col(address: str) -> int:
    letters = re.match(r"[A-Z]+", address)
    if letters is None:
        raise ValueError("unexpected cell address")
    n=0
    for c in letters.group():
        n=26*n+ord(c)-ord("A")+1
    return n-1


def sheet_records(raw: bytes, *, check_source=True) -> list[dict]:
    if check_source and git_blob(raw)!=SOURCE_SHA:
        raise ValueError("AUTHOR_WORKBOOK_GIT_BLOB_MISMATCH")
    from io import BytesIO
    with ZipFile(BytesIO(raw)) as z:
        files=set(z.namelist())
        if "xl/workbook.xml" not in files:
            raise ValueError("no XLSX workbook")
        root=ET.fromstring(z.read("xl/workbook.xml"))
        relpath="xl/_rels/workbook.xml.rels"
        if relpath not in files:
            raise ValueError("missing XLSX sheet relations")
        rel={e.attrib["Id"]:e.attrib["Target"] for e in
             ET.fromstring(z.read(relpath)).findall(P+"Relationship")}
        shared=[]
        if "xl/sharedStrings.xml" in files:
            for item in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M+"si"):
                shared.append("".join(x.text or "" for x in item.iter(M+"t")))
        for sh in root.find(M+"sheets"):
            target=rel.get(sh.attrib.get(R+"id"),"")
            target=(target.lstrip("/") if target.startswith("/xl/")
                    else target if target.startswith("xl/")
                    else "xl/"+target.lstrip("/"))
            if target not in files:
                continue
            data=ET.fromstring(z.read(target))
            sheetdata=data.find(M+"sheetData")
            if sheetdata is None:
                continue
            mapped=[]
            for row in sheetdata.findall(M+"row"):
                cells={}
                for c in row.findall(M+"c"):
                    ref=c.get("r","")
                    idx=address_col(ref)
                    typ=c.get("t")
                    v=c.find(M+"v")
                    if typ=="s":
                        value=shared[int(v.text)] if v is not None and v.text else ""
                    elif typ=="inlineStr":
                        value="".join(t.text or "" for t in c.iter(M+"t"))
                    elif v is not None:
                        value=v.text or ""
                    else:
                        value=""
                    cells[idx]=value
                mapped.append(cells)
            if not mapped:
                continue
            head=mapped[0]
            keys={idx:str(value).strip() for idx,value in head.items()}
            actual=set(keys.values())
            if not REQUIRED.issubset(actual):
                continue
            inverse={name:idx for idx,name in keys.items()}
            observations=[]
            for row in mapped[1:]:
                obs={name:row.get(idx,"") for name,idx in inverse.items()}
                if not obs.get("site_id") or not obs.get("img_year"):
                    continue
                yr=int(float(obs["img_year"]))
                if not 2009<=yr<=2018:
                    continue
                obs["img_year"]=yr
                observations.append(obs)
            return observations
    raise ValueError("NO_SHEET_MATCHES_REQUIRED_IMAGE_COLUMNS")


def summarize(rows: list[dict], posterior: dict) -> dict:
    events=posterior["apparent_zero_to_positive_events"]
    if len(events)!=9 or len({(e["site_id"],e["zero_year"]) for e in events})!=9:
        raise ValueError("not nine frozen transitions")
    report=[]
    unique=set()
    for e in events:
        years=[]
        for yr in [e["zero_year"],e["positive_year"]]:
            matching=[r for r in rows if r["site_id"]==e["site_id"]
                      and r["img_year"]==yr]
            unique.add((e["site_id"],yr))
            b=Counter(str(r.get("bpresent","")).strip() for r in matching)
            areazero=sum(str(r.get("area_m2","")).strip() in ("0","0.0","0.00") for r in matching)
            dates=[]
            for r in matching:
                month=str(r.get("img_month","")).strip()
                day=str(r.get("img_day","")).strip()
                pixel=str(r.get("area_m2","")).strip()
                date=(f"{yr}-{month.zfill(2)}-{day.zfill(2)}"
                      if month not in ("","NA","0") and day not in ("","NA","0") else None)
                real_pixel = pixel not in ("","NA")
                nov_or_later = (month.isdigit() and int(month)>=11)
                out_of_window = (month.isdigit() and not (9<=int(month)<=11))
                eligible_based_on_date_and_area_only = (
                    date is not None and real_pixel and not out_of_window and
                    not (nov_or_later and pixel in ("0","0.0","0.00")))
                dates.append({
                    "date":date,"bpresent":str(r.get("bpresent","")).strip(),
                    "area_m2":pixel,"img_qualit":str(r.get("img_qualit","")).strip(),
                    "date_and_area_pass_published_window":eligible_based_on_date_and_area_only,
                    "uncertain_other_original_removal_flags":True
                })
            years.append({
                "year":yr,"raw_images_with_site_year":len(matching),
                "original_bpresent_categories":dict(sorted(b.items())),
                "zero_pixel_area_images":areazero,
                "raw_image_dates_and_codes":dates,
                "verified_independent_fast_ice_present_before_move":False,
                "verified_whole_site_negative_breeding_survey":False,
            })
        report.append({"site_id":e["site_id"],"posterior_zero_year":e["zero_year"],
          "posterior_positive_year":e["positive_year"],"raw_satellite_image_support":years,
          "confirmed_recolonization_into_available_refuge":False})
    bycat=Counter(str(r.get("bpresent","")).strip() for r in rows)
    return {
        "audit_id":"larue-2024-original-satellite-images-vs-9-posterior-reappearances",
        "source_url":SOURCE_URL,
        "source_git_blob_sha":SOURCE_SHA,
        "unit":"raw satellite image records, not independent colonies or breeders",
        "raw_rows_2009_2018":len(rows),
        "raw_bpresent_value_counts":dict(sorted(bycat.items())),
        "already_exposed_model_posterior_0_to_positive_events":len(events),
        "transitions":report,
        "zero_year_events_with_at_least_one_source_image":sum(
            e["raw_satellite_image_support"][0]["raw_images_with_site_year"]>0
            for e in report),
        "zero_year_events_with_bpresent_No":sum(
            any(str(k).lower()=="no" and v>0 for k,v in
                e["raw_satellite_image_support"][0]["original_bpresent_categories"].items())
            for e in report),
        "zero_year_events_with_bpresent_yes":sum(
            any(str(k).lower()=="yes" and v>0 for k,v in
                e["raw_satellite_image_support"][0]["original_bpresent_categories"].items())
            for e in report),
        "positive_year_events_with_bpresent_yes":sum(
            any(str(k).lower()=="yes" and v>0 for k,v in
                e["raw_satellite_image_support"][1]["original_bpresent_categories"].items())
            for e in report),
        "positive_year_events_with_bpresent_no":sum(
            any(str(k).lower()=="no" and v>0 for k,v in
                e["raw_satellite_image_support"][1]["original_bpresent_categories"].items())
            for e in report),
        "positive_year_events_with_bpresent_NA":sum(
            any(str(k).upper()=="NA" and v>0 for k,v in
                e["raw_satellite_image_support"][1]["original_bpresent_categories"].items())
            for e in report),
        "raw_bpresent_no_to_yes_event_count":sum(
            any(k.lower()=="no" and v>0 for k,v in e["raw_satellite_image_support"][0]["original_bpresent_categories"].items())
            and any(k.lower()=="yes" and v>0 for k,v in e["raw_satellite_image_support"][1]["original_bpresent_categories"].items())
            for e in report),
        "positive_year_without_valid_image_according_to_date_and_area_filter":sum(
            not any(d["date_and_area_pass_published_window"] for d in e["raw_satellite_image_support"][1]["raw_image_dates_and_codes"])
            for e in report),
        "zero_year_events_with_independent_verified_physically_available_absent_colony":0,
        "all_refuge_colonization_criteria_met":False,
        "absence_vs_no_ice_separated_using_bpresent_alone":False,
        "site_year_zero_to_positive_posterior_is_real_recolonization":False,
        "new_2022_plus_rows_opened":0,
        "new_causal_effect_estimated":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xlsx",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.xlsx:
        raw=args.xlsx.read_bytes()
    else:
        with urllib.request.urlopen(
            urllib.request.Request(SOURCE_URL,
              headers={"User-Agent":"mina-retrospective-source-audit"}), timeout=45
        ) as r:
            raw=r.read(250000)
    observations=sheet_records(raw)
    prior=json.loads(FROZEN.read_text(encoding="utf-8"))
    result=summarize(observations,prior)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
