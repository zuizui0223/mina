"""Retrospective classification of 20 No-coded original 2009-2018 images.

Original public LaRue et al 2024 annotations are a SAME-OBSERVER, single-image
description of ice and penguins, NOT a temporally independent fast-ice dataset,
whole-season biological absence, successful breeding or natal dispersal.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import re
import urllib.request
from pathlib import Path

from audit_larue_original_satellite_image_support_v1 import (
    SOURCE_SHA, SOURCE_URL, sheet_records,
)

ICE_ABSENT="AUTHOR_NOTES_ICE_ABSENT_OR_ALREADY_BROKEN"
ICE_PRESENT="AUTHOR_NOTES_FAST_ICE_PRESENT_BIRDS_UNDETECTED"
ICE_UNRESOLVED="ICE_STATUS_NOT_EXPLICITLY_STATED"


def numeric(value):
    if value is None or str(value).strip().lower() in ("", "na", "nan"):
        return None
    try:
        x=float(value)
    except (ValueError, TypeError):
        return None
    return x if math.isfinite(x) else None


def state_from_no(row):
    if str(row.get("bpresent","")).strip().lower()!="no":
        raise ValueError("Only literal No may receive explicit ice state")
    txt=" ".join(str(row.get("comments","") or "").lower().split())
    absent=bool(re.search(r"\bno\s+fast\s+ice\b",txt)
                or re.search(r"\bice\s+has\s+broken\s+out\b",txt))
    present="fast ice available" in txt
    if absent and present:
        raise ValueError("contradictory source annotation")
    return ICE_ABSENT if absent else ICE_PRESENT if present else ICE_UNRESOLVED


def fits_basic_original_window(row):
    """Published LaRue author code: Sept-Nov, no zero-area from November 1,
    original explicit remove flag blank, and finite satellite area; this
    does NOT verify other quality judgments or sustained breeding."""
    month=numeric(row.get("img_month"))
    area=numeric(row.get("area_m2"))
    remove=str(row.get("remove","") or "").strip().lower()
    return (month is not None and 9<=month<=11 and
            area is not None and (month<11 or area!=0) and
            remove in ("", "na", "none"))


def image_date(row):
    try:
        y=int(float(row["img_year"]))
        m=int(float(row["img_month"]))
        d=int(float(row["img_day"]))
        return f"{y:04d}-{m:02d}-{d:02d}" if 1<=m<=12 and 1<=d<=31 else None
    except (TypeError, ValueError, KeyError):
        return None


def audit(source):
    rows=[r for r in source if 2009<=int(r.get("img_year") or 0)<=2018]
    counts=Counter(str(r.get("bpresent","")).strip().lower() for r in rows)
    if len(rows)!=599 or counts!=Counter({"yes":502,"no":20,"na":77}):
        raise ValueError("pinned 2009-2018 original published source counts changed")
    no_cases=[]
    for row in rows:
        if str(row.get("bpresent","")).strip().lower()!="no":
            continue
        no_cases.append({
            "site_id":row.get("site_id"),
            "site_name":row.get("site_name"),
            "image_date":image_date(row),
            "comment":str(row.get("comments","") or ""),
            "annotation_state":state_from_no(row),
            "area_m2":numeric(row.get("area_m2")),
            "quality":numeric(row.get("img_qualit")),
            "passes_basic_original_model_date_area_remove_filter":
                fits_basic_original_window(row),
            "independent_same_season_ice_available_verified":False,
            "whole_site_repeated_negative_breeding_survey_verified":False
        })
    no_cases.sort(key=lambda c:(c["site_id"],c["image_date"] or ""))
    groups=Counter(c["annotation_state"] for c in no_cases)
    if groups!=Counter({ICE_ABSENT:4,ICE_PRESENT:3,ICE_UNRESOLVED:13}):
        raise ValueError("author ice-note classification changed: halt")
    yes_zero=[{
        "site_id":r.get("site_id"),"image_date":image_date(r),
        "comment":str(r.get("comments","") or "")
    } for r in rows if str(r.get("bpresent","")).lower()=="yes"
      and numeric(r.get("area_m2"))==0]
    no_positive=[{
        "site_id":c["site_id"],"image_date":c["image_date"],
        "area_m2":c["area_m2"]
    } for c in no_cases if c["area_m2"] is not None and c["area_m2"]>0]
    if len(yes_zero)!=3 or len(no_positive)!=1:
        raise ValueError("presence-code/area disagreement counts changed")
    ledda=[]
    for row in sorted((r for r in rows if r.get("site_id")=="LEDD"),
                      key=lambda r:(int(r["img_year"]),int(r["img_month"]),int(r["img_day"]))):
        bp=str(row.get("bpresent","")).strip().lower()
        status=(state_from_no(row) if bp=="no"
                else "SOURCE_PRESENCE_YES_NOT_SUCCESSFUL_BREEDING" if bp=="yes"
                else "INCONCLUSIVE_IMAGE")
        ledda.append({
            "year":int(row["img_year"]), "image_date":image_date(row),
            "bpresent":bp, "ice_or_presence_state":status,
            "quality":numeric(row.get("img_qualit")),
            "area_m2":numeric(row.get("area_m2")),
            "passes_basic_original_fit_filter":fits_basic_original_window(row),
            "comment":str(row.get("comments","") or "")
        })
    if len(ledda)!=10:
        raise ValueError("Ledda is not the expected 2009-2018 ten-year roster")
    next_positive={}
    next_positive_both_in_filter={}
    for category in (ICE_ABSENT,ICE_PRESENT):
        next_positive[category]=sum(
            a["ice_or_presence_state"]==category and b["bpresent"]=="yes"
            for a,b in zip(ledda[:-1],ledda[1:]))
        next_positive_both_in_filter[category]=sum(
            a["ice_or_presence_state"]==category and b["bpresent"]=="yes"
            and a["passes_basic_original_fit_filter"]
            and b["passes_basic_original_fit_filter"]
            for a,b in zip(ledda[:-1],ledda[1:]))
    return {
        "result_id":"larue-2009-18-annotated-ice-noice-vs-bird-nondetection-v1",
        "source_blob_sha":SOURCE_SHA,
        "scope":"ORIGINAL_AUTHOR_IMAGE_INTERPRETATIONS_NOT_INDEPENDENT_ICE_OR_CAUSAL_TEST",
        "raw_image_rows_2009_2018":len(rows),
        "bpresent_original_counts":{"yes":502,"no":20,"NA":77},
        "no_annotation_state_counts":dict(sorted(groups.items())),
        "no_passing_basic_original_fit_filter":sum(
            c["passes_basic_original_model_date_area_remove_filter"]
            for c in no_cases),
        "no_source_rows":no_cases,
        "no_with_positive_area":no_positive,
        "yes_with_zero_area":yes_zero,
        "LEDD_original_image_year_history":ledda,
        "LEDD_no_fast_ice_years":[r["year"] for r in ledda
                                   if r["ice_or_presence_state"]==ICE_ABSENT],
        "LEDD_fast_ice_available_birds_not_seen_years":[r["year"]
            for r in ledda if r["ice_or_presence_state"]==ICE_PRESENT],
        "LEDD_fast_ice_available_birds_not_seen_inside_author_basic_fit_years":[
            r["year"] for r in ledda if r["ice_or_presence_state"]==ICE_PRESENT
            and r["passes_basic_original_fit_filter"]],
        "LEDD_positive_detection_code_years":[r["year"] for r in ledda
                                               if r["bpresent"]=="yes"],
        "LEDD_next_image_yes_after_author_ice_annotation":next_positive,
        "LEDD_next_image_yes_where_both_scenes_pass_basic_fit":next_positive_both_in_filter,
        "source_ice_available_comment_proves_whole_season_suitable_ice":False,
        "source_image_no_code_identifies_true_biological_vacancy":False,
        "source_image_yes_code_identifies_completed_breeding":False,
        "new_2022plus_outcomes_read":0,
        "causal_effect_estimated":False,
        "independent_ice_time_series_for_followup":
            "Fraser & Massom 2000-2018 version2.2 doi:10.26179/5d267d1ceb60c (1km/15-day maps; not accessed in this audit)"
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xlsx",type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.xlsx:
        source=args.xlsx.read_bytes()
    else:
        req=urllib.request.Request(
            SOURCE_URL,headers={"User-Agent":"mina-published-emperor-annotation-audit"}
        )
        with urllib.request.urlopen(req,timeout=40) as stream:
            source=stream.read(300000)
    result=audit(sheet_records(source))
    output=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        args.out.write_text(output,encoding="utf8")
    print(output,end="")


if __name__=="__main__":
    main()
