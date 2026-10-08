"""Retrospective mass accounting for model-zero → positive emperor colony indices.

This computes how much *modeled positive change* is assigned to state switches
that appear as posterior mean zero→positive, NOT the number of immigrants or
actual biological recolonizations. Observations are already published (2009–18).
Original author CSV is pinned by exact Git blob SHA. It also requires the
independently audited raw-image status for each of the nine model switches.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
S="13f71112da43c1fd082273677757b41c550457ed"
SOURCE_BLOB="133c900c9dfbf2ce23ca403c9a59edecd9b51ace"
SOURCE=f"https://raw.githubusercontent.com/davidiles/EMPE_Global/{S}/analysis/output/model_results/3_Colony_Level/colony_summary.csv"
RAW_NINE=BASE/"results/EMPEROR_LARUE_RAW_SATELLITE_TRANSITION_SUPPORT_V1.json"
CAT_DATE="raw_no_to_yes_but_next_image_only_date_area_gate"
CAT_LATE="raw_no_to_yes_next_image_outside_date_area_gate"
CAT_MISMATCH="raw_observations_not_no_to_yes"


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def read_published_csv(data: bytes, *, enforce_pin=True):
    if enforce_pin and git_blob(data) != SOURCE_BLOB:
        raise ValueError("PINNED_PUBLISHED_AUTHOR_MODEL_CSV_BLOB_MISMATCH")
    source=csv.DictReader(io.StringIO(data.decode("utf8-sig")))
    expected={"year","site_id","N_mean"}
    if not expected.issubset(source.fieldnames or ()):
        raise ValueError("source schema missing")
    out={}
    for row in source:
        site,year,n=row["site_id"],int(row["year"]),float(row["N_mean"])
        if not site or year not in range(2009,2019) or not math.isfinite(n) or n<0:
            raise ValueError("source value/identity outside frozen support")
        key=(site,year)
        if key in out:
            raise ValueError("duplicate site-year")
        out[key]=n
    ids={s for s,_ in out}
    if len(ids)!=50 or len(out)!=500 or any((s,y) not in out
                                               for s in ids for y in range(2009,2019)):
        raise ValueError("pinned 50x10 source support changed")
    return out


def audit(model: dict, nine: list[dict]):
    gain=gross_loss=0.
    annual=[]
    ids=sorted({s for s,_ in model})
    for y in range(2009,2018):
        gp=gn=0.
        for s in ids:
            delta=model[s,y+1]-model[s,y]
            gp+=max(0.,delta)
            gn+=max(0.,-delta)
        gain+=gp
        gross_loss+=gn
        annual.append({"from":y,"to":y+1,"gross_positive_model_change":gp,
                       "gross_negative_model_change":gn})
    assert len(nine)==9
    recorded=set()
    groups={
        CAT_DATE:{"episodes":[],"positive_mass":0.},
        CAT_LATE:{"episodes":[],"positive_mass":0.},
        CAT_MISMATCH:{"episodes":[],"positive_mass":0.}
    }
    for event in nine:
        s,y,z=(event["site_id"],event["posterior_zero_year"],
               event["posterior_positive_year"])
        if (s,y,z) in recorded or z!=y+1 or model[s,y]!=0 or model[s,z]<=0:
            raise ValueError("transition raw image receipts inconsistent with pinned model")
        recorded.add((s,y,z))
        has_raw_no_yes=(event["prior_original_bpresent"].lower()=="no" and
                        event["next_original_bpresent"].lower()=="yes")
        if has_raw_no_yes:
            category=(CAT_DATE if event["next_date_and_pixel_filter_valid"]
                      else CAT_LATE)
        else:
            category=CAT_MISMATCH
        amount=model[s,z]
        groups[category]["episodes"].append({
            "site":s,"zero_year":y,"positive_year":z,"posterior_mean_gain":amount,
            "next_raw_status":event["next_original_bpresent"],
            "date_area_window_passes_only":bool(event["next_date_and_pixel_filter_valid"]),
        })
        groups[category]["positive_mass"]+=amount

    gross_model_zero_positive=sum(x["positive_mass"] for x in groups.values())
    for group in groups.values():
        group["n"]=len(group["episodes"])
        group["share_of_all_model_gross_positive_change"]=group["positive_mass"]/gain
        group["share_of_model_zero_reappearance_mass"]=group["positive_mass"]/gross_model_zero_positive
    return {
        "status":"POST_RESULT_PUBLISHED_MODEL_ALLOCATION_QA_NOT_NEW_MIGRATION_OR_CAUSAL_ECOLOGY",
        "source_pinned_sha":SOURCE_BLOB,
        "authors_colony_years":len(model),"number_sites":len(ids),
        "annual":annual,
        "sum_gross_positive_posterior_mean_change_across_nine_year_transitions":gain,
        "sum_gross_negative_posterior_mean_change_across_nine_year_transitions":gross_loss,
        "apparent_model_zero_to_positive_episodes":len(recorded),
        "sum_of_model_zero_to_positive_allocated_mean_abundance":gross_model_zero_positive,
        "share_of_model_gross_positive_change_all_zero_to_positive":gross_model_zero_positive/gain,
        "image_evidence_categories":groups,
        "verified_prior_physically_available_but_empty_refuge_events":0,
        "confirmed_first_time_breeding_in_new_site_from_these_episodes":0,
        "interpretation":"The mass sums repeatedly across time and represents published MODEL posterior means, not tracked penguins or cumulative unique individuals. Raw next-image date and area filters do NOT prove actual original-model inclusion (removal flags). All nine lack independent prior physical ice, surveyed empty history and new confirmed breeding.",
        "biological_causal_effect_fitted":False,
        "previously_locked_PR189_and_external_PRs_unchanged":True,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",type=Path)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    if args.input:
        raw=args.input.read_bytes()
    else:
        req=urllib.request.Request(SOURCE,headers={"User-Agent":"mina-2026-published-sensitivity-qa"})
        with urllib.request.urlopen(req,timeout=35) as f:
            raw=f.read(240000)
    nine=json.loads(RAW_NINE.read_text(encoding="utf8"))["nine_posterior_transition_image_matches"]
    receipt=audit(read_published_csv(raw),nine)
    data=json.dumps(receipt,indent=2,ensure_ascii=False)+"\n"
    if args.out:
        args.out.write_text(data,encoding="utf8")
    print(data,end="")


if __name__=="__main__":
    main()
