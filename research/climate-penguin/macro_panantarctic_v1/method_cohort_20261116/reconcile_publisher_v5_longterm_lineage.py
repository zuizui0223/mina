#!/usr/bin/env python3
"""Original MAPPPD v5.0 long-term colony roster crosswalk.

Source gate: pinned 2026-10-21 original publisher bytes (729 site registry,
5487 original observation records), not inferred 265 site-series data.
DO NOT publish original nest-count magnitudes, fit climate trends, or use
missing observations as zero. Season labels and census calendar years are
DIFFERENT temporal attributes.
"""
from __future__ import annotations
import argparse, collections, csv, hashlib, json, sys
from pathlib import Path
import requests

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/"work"/"climate_penguin"))
import derive_MAPPPD5_original_macro_source_v1 as original

REF_DERIVED=HERE.parents[1]/"outputs"/"comparison_audit"/"mapppd_unambiguous_site_seasons.csv"
REF_SHA="fc134e364cf38699fa7611d7dee5fbbbcb370c0a"
SPECIES=("ADPE","CHPE","GEPE")
EARLY=(1980,2000)
LATE=(2005,2025)

def git_blob_sha(content):
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\x00"+content).hexdigest()

def valid_year(value):
    s=str(value or "").strip()
    try:
        x=float(s)
        return int(x) if x.is_integer() and 1800<=x<=2100 else None
    except (ValueError,OverflowError):
        return None

def rostering(rows,time_field):
    grouped=collections.defaultdict(list)
    for r in rows:
        year=valid_year(r.get(time_field))
        if year is not None:
            grouped[(r["site_id"],r["species_id"],year)].append(r)
    # Explicit per-year source count agreement, never combine conflicting counts.
    chosen=[]
    reasons=collections.Counter()
    for (site,sp,year), group in grouped.items():
        nums=[float(r["count"].replace(",","")) for r in group]
        if len(set(nums))!=1:
            reasons["conflicting_numeric_count_group"]+=1
            continue
        methods={r["vantage"].strip() for r in group}
        citations={r["citekey"].strip() for r in group}
        methods={m for m in methods if m}
        citations={c for c in citations if c}
        if len(methods)!=1:
            reasons["ambiguous_or_blank_vantage_group"]+=1
        if len(citations)!=1:
            reasons["ambiguous_or_blank_citation_group"]+=1
        chosen.append(dict(site=site,sp=sp,year=year,
            count_nests=nums[0],n_obs=len(group),
            method=next(iter(methods)) if len(methods)==1 else "",
            citation=next(iter(citations)) if len(citations)==1 else "",
            observation_ids=";".join(sorted({r["id"] for r in group})),
            has_one_vantage=len(methods)==1,has_one_citation=len(citations)==1))
    by=collections.defaultdict(list)
    for r in chosen: by[(r["site"],r["sp"])].append(r)
    out=[]
    for (site,sp), records in sorted(by.items()):
        early=[x for x in records if EARLY[0]<=x["year"]<=EARLY[1]]
        late=[x for x in records if LATE[0]<=x["year"]<=LATE[1]]
        if not early or not late: continue
        keep=[x for x in records if x["has_one_vantage"]]
        m_early={r["method"] for r in early if r["has_one_vantage"]}
        m_late={r["method"] for r in late if r["has_one_vantage"]}
        shared=m_early&m_late
        pair_early={(r["method"],r["citation"]) for r in early if r["has_one_vantage"] and r["has_one_citation"]}
        pair_late={(r["method"],r["citation"]) for r in late if r["has_one_vantage"] and r["has_one_citation"]}
        valid_early=[x for x in early if x["has_one_vantage"]]
        valid_late=[x for x in late if x["has_one_vantage"]]
        freq=collections.Counter(x["method"] for x in keep)
        most=sorted(freq.items(),key=lambda z:(-z[1],z[0]))[0][0] if freq else ""
        in_most=bool(most and any(x["method"]==most for x in valid_early) and any(x["method"]==most for x in valid_late))
        one_method_across_windows=bool(len(m_early)==len(m_late)==1 and shared)
        out.append({
            "site_id":site,"species":sp,
            "has_early_late_unambiguous_counts":True,
            "both_periods_have_known_vantage":bool(valid_early and valid_late),
            "any_identical_vantage_across_periods":bool(shared),
            "one_identical_vantage_in_each_period":one_method_across_windows,
            "full_history_most_frequent_vantage_both_periods":in_most,
            "identical_nonblank_citation_and_vantage_across_periods":bool(pair_early&pair_late),
            "earliest_eligible_time_label":min(x["year"] for x in early),
            "latest_eligible_time_label":max(x["year"] for x in late),
            "n_early_eligible_years":len(early),
            "n_late_eligible_years":len(late),
            "n_early_vantage_known_years":len(valid_early),
            "n_late_vantage_known_years":len(valid_late),
            "early_vantage_set":";".join(sorted(m_early)),
            "late_vantage_set":";".join(sorted(m_late)),
            # Original observation IDs allow deterministic row-level lineage;
            # counts themselves remain in upstream original source.
            "early_original_observation_ids":";".join(x["observation_ids"] for x in early),
            "late_original_observation_ids":";".join(x["observation_ids"] for x in late),
        })
    return out,{"original_numeric_count_source_key_groups":len(grouped),
                "unambiguous_count_group_rows":len(chosen),
                "rejections":dict(reasons)}

def summary(roster):
    flags=["has_early_late_unambiguous_counts","both_periods_have_known_vantage",
           "any_identical_vantage_across_periods",
           "one_identical_vantage_in_each_period",
           "full_history_most_frequent_vantage_both_periods",
           "identical_nonblank_citation_and_vantage_across_periods"]
    d={}
    for flag in flags:
        a=[r for r in roster if r[flag]]
        d[flag]={"total":len(a),"species":{s:sum(r["species"]==s for r in a) for s in SPECIES},
                 "site_ids":len({r["site_id"] for r in a})}
    return d

def read_derived():
    raw=REF_DERIVED.read_bytes()
    if git_blob_sha(raw)!=REF_SHA:raise ValueError("STOP: original derived table Git blob changed")
    with REF_DERIVED.open(newline="",encoding="utf-8") as f:rs=list(csv.DictReader(f))
    if len(rs)!=2999:raise ValueError("STOP: derived original rows changed")
    by=collections.defaultdict(list)
    for r in rs:
        if r["species_id"] not in SPECIES:continue
        if r["n_methods"]=="1" and r["method"].strip() not in ("","unknown"):
            by[(r["site_id"],r["species_id"])].append(r)
    eligible=set()
    for (site,sp),a in by.items():
        if any(EARLY[0]<=int(x["season"])<=EARLY[1] for x in a) and any(LATE[0]<=int(x["season"])<=LATE[1] for x in a):
            eligible.add((site,sp))
    if len(eligible)!=268:raise ValueError("STOP: prior 268 derived cohort drift")
    return eligible

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    with requests.Session() as sess:
        sess.headers.update({"User-Agent":"mina-original-v5-longterm-lineage-20261117/1.0"})
        raw={k:original.source_data(sess,k) for k in original.SOURCE}
    release=json.loads(raw["release"])
    if release.get("version")!="5.0" or release.get("release_date")!="2026-10-21":
        raise ValueError("STOP: publisher release/version mismatch")
    sites=original.tabular(raw["sites"],original.SITE_FIELDS)
    obs=(original.tabular(raw["observations_p1"],original.OBS_FIELDS)+
         original.tabular(raw["observations_p2"],original.OBS_FIELDS))
    if (len(sites),len(obs))!=(729,5487):
        raise ValueError("STOP original 729 site, 5487 observation count drift")
    if len({r["id"] for r in obs})!=len(obs):raise ValueError("STOP duplicate original observation ID")
    id_to_site={x["site_id"]:x for x in sites}
    if len(id_to_site)!=729:raise ValueError("STOP duplicate site ID")
    focal=[]
    for r in obs:
        if r["site_id"] not in id_to_site:raise ValueError("STOP unknown site ID")
        if r["species_id"] not in SPECIES or r["type"]!="nests":continue
        if not original.numeric(r["count"]):continue
        if r["presence"] not in ("0","1"):continue
        if r["presence"]=="1" and float(r["count"].replace(",",""))==0:
            raise ValueError("STOP presence/count contradiction")
        if r["presence"]=="0" and float(r["count"].replace(",",""))>0:
            raise ValueError("STOP presence/count contradiction")
        focal.append(r)
    first,season_reject=rostering(focal,"season")
    # The original table has year, month, day, date fields; do not assume all
    # observed values are present. Year labels MAY be different from season.
    has_calendar="year" in obs[0]
    if not has_calendar:raise ValueError("STOP original year field missing; no fabricated dates")
    second,year_reject=rostering(focal,"year")
    old=read_derived()
    def stats_overlap(roster):
        rr={(z["site_id"],z["species"]) for z in roster if z["both_periods_have_known_vantage"]}
        return {"frozen_derived_268":len(old),"original_v5_vantage_roster":len(rr),
                "overlap_exact_site_species":len(old&rr),
                "derived_only":len(old-rr),"publisher_v5_only":len(rr-old),
                "derived_only_by_species":{s:sum(sp==s for _,sp in old-rr) for s in SPECIES},
                "publisher_only_by_species":{s:sum(sp==s for _,sp in rr-old) for s in SPECIES}}
    # A season vs year discrepancy is a real source property, not a climate lag.
    mismatch=sum(valid_year(r.get("year")) is not None
                 and valid_year(r.get("season")) is not None
                 and valid_year(r.get("year"))!=valid_year(r.get("season")) for r in focal)
    completeness={col:{"field_exists":col in obs[0],
          "nonempty":sum(bool(str(r.get(col) or "").strip()) for r in focal)}
          for col in ("year","month","day","date")}
    original_sep={s:sum(r["species_id"]==s for r in focal) for s in SPECIES}
    out={"status":"SOURCE_PINNED_PUBLISHER_V5_LONGTERM_LINEAGE_ONLY",
         "publisher_release":"MAPPPD v5.0 2026-10-21",
         "source_sha256":{k:hashlib.sha256(v).hexdigest() for k,v in raw.items()},
         "original_sites":len(sites),"original_observations":len(obs),
         "focal_numerical_nests":len(focal),"focal_nests_by_species":original_sep,
         "actual_calendar_columns":completeness,
         "focal_calendar_year_differs_from_season":mismatch,
         "season_roster":summary(first),"calendar_year_roster":summary(second),
         "season_source_key_quality":season_reject,
         "calendar_source_key_quality":year_reject,
         "frozen_derived_268_vs_original_v5":stats_overlap(first),
         "external_265_original_observation_roster_available":False,
         "external_265_coefficients_verified":False,
         "no_climate_dose_response_or_population_forecast":True,
         "source_label_warning":"vantage is source vantage, not an independently calibrated census method",
         "missing_year_or_taxon_is_not_zero":True}
    (a.out/"publisher_v5_longterm_source_lineage.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    # Source IDs and all cohort eligibility decisions, no count magnitudes.
    for name,roster in (("season",first),("calendar_year",second)):
        if not roster:raise ValueError("STOP empty original roster")
        with (a.out/f"publisher_v5_{name}_original_ids_no_counts.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(roster[0]))
            w.writeheader();w.writerows(roster)
    print("ORIGINAL_V5_LONGTERM_SOURCE_GATE="+json.dumps({
        "status":out["status"],"n_original_focal_nest_rows":len(focal),
        "season":out["season_roster"],"calendar":out["calendar_year_roster"],
        "frozen_derived_vs_publisher":out["frozen_derived_268_vs_original_v5"],
        "calendar_season_mismatches":mismatch
    },ensure_ascii=False),flush=True)

if __name__=="__main__":main()
