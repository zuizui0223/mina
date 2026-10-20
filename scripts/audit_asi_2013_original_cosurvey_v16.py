#!/usr/bin/env python3
"""Publisher-MD5 verified ASI multi-taxon same-site/day census support; never read Count."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

URL="https://esapubs.org/archive/ecol/E094/243/Antarctic_Site_Inventory_census_data_1994_2012.csv"
MD5="00871bd47b6ec30cda68d1506120bfb3"
REQUIRED={"Site_ID","Region","Site_name","Latitude","Longitude","Species","Date","Season",
          "Count","Counted_object","Accuracy","Notes","Source"}
PENGUINS={"ADPE","CHPE","GEPE","MCPE"}
FLYING={"BESH","KEGU","SOGP"}
REGIONS={"CW","EI","NE","NW","SH","SO","SW"}

def fetch_original(fetcher=None):
    if fetcher is not None:
        final,data=fetcher(URL)
    else:
        req=Request(URL,headers={"User-Agent":"mina-original-asi-research/1.0"})
        with urlopen(req,timeout=35) as reply:
            final=reply.geturl()
            data=reply.read(2000001)
    if urlparse(final).hostname not in {"esapubs.org","www.esapubs.org"}:
        raise ValueError("SOURCE_STOP unexpected publisher redirect")
    if not data or len(data)>2000000:
        raise ValueError("SOURCE_STOP original file absent or oversized")
    md5=hashlib.md5(data).hexdigest()
    if md5!=MD5:
        raise ValueError("SOURCE_STOP publisher original MD5 mismatch "+md5)
    return data,final

def parse_original(data):
    try:
        content=data.decode("utf-8-sig")
    except UnicodeDecodeError:
        content=data.decode("latin-1")
    reader=csv.DictReader(io.StringIO(content,newline=""))
    if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
        raise ValueError("SCHEMA_STOP publisher columns unavailable")
    rows=list(reader)
    if len(rows)!=1124:
        raise ValueError("SOURCE_STOP publisher expected 1124 census rows")
    return rows

def eligible_metadata(r):
    if str(r["Source"]).strip().upper()!="ASI" or str(r["Counted_object"]).strip().upper()!="N":
        return None
    sp=str(r["Species"]).strip()
    if sp not in PENGUINS|FLYING:
        return None
    try:
        accuracy=int(str(r["Accuracy"]).strip())
        season=int(str(r["Season"]).strip())
        latitude=float(r["Latitude"]);longitude=float(r["Longitude"])
    except (TypeError,ValueError):
        return None
    if not (1<=accuracy<=3 and 1994<=season<=2012 and -90<=latitude<=-50 and -180<=longitude<=180):
        return None
    site=str(r["Site_ID"]).strip(); region=str(r["Region"]).strip()
    if not re.fullmatch(r"[A-Z0-9]{4}",site) or region not in REGIONS:
        return None
    raw=str(r["Date"]).strip()
    if not re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}",raw):
        return None
    try:
        when=datetime.strptime(raw,"%m/%d/%Y").date()
    except ValueError:
        return None
    if (when.year if when.month>=7 else when.year-1)!=season:
        return None
    return (site,region,sp,season,when.isoformat())

def structural(rows):
    if not rows or not REQUIRED.issubset(set(rows[0])):
        raise ValueError("SCHEMA_STOP incomplete original source")
    candidate=defaultdict(list)
    site_regions={}
    for r in rows:
        m=eligible_metadata(r)
        if m is None:
            continue
        site,region,sp,season,day=m
        if site in site_regions and site_regions[site]!=region:
            raise ValueError("SOURCE_STOP one Site_ID in multiple source regions")
        site_regions[site]=region
        candidate[(site,season,day,sp)].append(m)
    duplicate={k:v for k,v in candidate.items() if len(v)>1}
    retained=[items[0] for items in candidate.values() if len(items)==1]
    by_event=defaultdict(set)
    for site,region,sp,season,day in retained:
        by_event[(site,region,season,day)].add(sp)
    pairs={"multi":[], "penguin_pair":[], "penguin_flying":[]}
    exact_pair_counts=Counter()
    for (site,region,season,day),species in by_event.items():
        ps=sorted(species & PENGUINS); fs=sorted(species & FLYING)
        if len(species)>=2:
            pairs["multi"].append((site,region,day))
        if len(ps)>=2:
            pairs["penguin_pair"].append((site,region,day))
        if ps and fs:
            pairs["penguin_flying"].append((site,region,day))
        for i in range(len(ps)):
            for other in ps[i+1:]:
                exact_pair_counts[ps[i]+"_"+other]+=1
            for other in fs:
                exact_pair_counts[ps[i]+"_"+other]+=1
    def summary(v):
        return {
            "distinct_same_site_day_events":len(v),
            "distinct_original_sites":len({site for site,region,day in v}),
            "distinct_original_regions":len({region for site,region,day in v}),
            "events_by_region":dict(sorted(Counter(region for site,region,day in v).items()))
        }
    pp=summary(pairs["penguin_pair"]); cross=summary(pairs["penguin_flying"])
    ppass=(pp["distinct_same_site_day_events"]>=60 and pp["distinct_original_sites"]>=20
           and pp["distinct_original_regions"]>=4)
    fpass=(cross["distinct_same_site_day_events"]>=25 and cross["distinct_original_sites"]>=10
           and cross["distinct_original_regions"]>=3)
    return {
        "status":"V16_AUTHENTIC_ASI_MULTISPECIES_SOURCE_SUPPORT_NO_BIOLOGY",
        "source_original_rows":len(rows),
        "source_sites_after_structural_filter":len(site_regions),
        "eligible_strict_ASI_exact_day_nest_rows":len(retained),
        "excluded_duplicate_source_groups":len(duplicate),
        "excluded_duplicate_source_rows":sum(len(v) for v in duplicate.values()),
        "source_rows_in_eligible_metadata_before_duplicate_filter":sum(map(len,candidate.values())),
        "two_or_more_species":summary(pairs["multi"]),
        "two_penguin_species":pp,
        "penguin_flying_species":cross,
        "source_exact_site_day_pair_counts":dict(sorted(exact_pair_counts.items())),
        "penguin_pair_support_gate_pass":bool(ppass),
        "penguin_flying_support_gate_pass":bool(fpass),
        "numeric_original_Count_cells_opened":0,
        "actual_joint_observer_or_visit_ID_verified":False,
        "independence_from_MAPPPD_source_records_verified":False,
        "ecological_model_fit":False,
        "scientific_decision":("HOLD_ORIGINAL_PEDIGREE_AND_INDEPENDENT_ENVIRONMENT"
             if ppass or fpass else "STOP_INSUFFICIENT_CODATED_NEST_SURVEY_SUPPORT"),
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    receipt={"status":"HOLD_ORIGINAL_SOURCE","ecological_model_fit":False}
    try:
        data,final=fetch_original()
        receipt={**structural(parse_original(data)),
                 "source_url":final,
                 "publisher_original_md5":MD5,
                 "original_sha256":hashlib.sha256(data).hexdigest(),
                 "original_bytes":len(data)}
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:600]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_ORIGINAL_SOURCE":
        raise SystemExit(2)
if __name__=="__main__":
    main()
