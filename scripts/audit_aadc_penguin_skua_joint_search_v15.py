#!/usr/bin/env python3
"""V15: outcome-blind structural co-survey gate on original AADC island records."""
import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
from pyproj import Transformer

SITE_SHA="48c716c38c41a054eefc20c03de3c21d75047049e6e277d471d9b9135aab7da5"
SURVEY_SHA="dba39d79f6309f90e23e896415177ea75086aaf2ecb5523256e48895e95dfc5c"
REQUIRED_SITE={"geog_site_id","geog_site_feature","geog_site_area","latitude","longitude"}
REQUIRED_SURVEY={"geog_site_id","species_code","season","occurrence","occurrence_cert_cat",
    "certainty_lookup","vantage","day","month","year","day_uncertainty","obs_number"}

def read_pinned(path,sha):
    data=Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest()!=sha:
        raise ValueError("SOURCE_STOP pinned V13 CSV SHA mismatch")
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))

def season_valid(value):
    s=str(value).strip()
    if not re.fullmatch(r"(?:18|19|20)\d{4}",s):
        return False
    year=int(s[:4])
    return 1980<=year<=2020 and int(s[4:])==(year+1)%100

def direct_eligible(r):
    if r["certainty_lookup"]!="EXACT_CERTAINTY_RULE":
        return False
    code=str(r["occurrence"]).strip()
    cat=str(r["occurrence_cert_cat"]).strip()
    return (code=="P" and cat in {"5","5.0"}) or (code=="A" and cat in {"4","4.0"})

def exact_date(r):
    try:
        if str(r["day_uncertainty"]).strip() not in {"","0","0.0"}:
            return None
        y,m,d=[int(str(r[k]).strip()) for k in ("year","month","day")]
        if 1980<=y<=2021 and 1<=m<=12 and 1<=d<=31:
            return y,m,d
    except (ValueError,TypeError,KeyError):
        pass
    return None

def index_islands(rows):
    if not rows or not REQUIRED_SITE.issubset(rows[0]):
        raise ValueError("SCHEMA_STOP source geography columns")
    projection=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    seen=set()
    sites={}
    for r in rows:
        sid=str(r["geog_site_id"]).strip()
        if not sid or sid in seen:
            raise ValueError("SOURCE_STOP duplicate/empty geographic ID")
        seen.add(sid)
        if str(r["geog_site_feature"]).lower().strip()!="island":
            continue
        try:
            area=float(r["geog_site_area"])
            lat=float(r["latitude"]);lon=float(r["longitude"])
            if not (math.isfinite(area) and area>0 and -90<=lat<=-60 and -180<=lon<=180):
                continue
            x,y=projection.transform(lon,lat)
            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            sites[sid]=f"{math.floor(x/250000)}_{math.floor(y/250000)}"
        except (ValueError,TypeError):
            pass
    return sites

def structural_pairs(survey,geo):
    if not survey or not REQUIRED_SURVEY.issubset(survey[0]):
        raise ValueError("SCHEMA_STOP original observation fields")
    groups=defaultdict(list)
    for r in survey:
        sp=str(r["species_code"]).strip()
        if sp not in {"ADP","SK","SP"}:
            continue
        sid=str(r["geog_site_id"]).strip()
        if sid in geo and season_valid(r["season"]):
            groups[(sid,str(r["season"]).strip(),sp)].append(r)
    allowed={k:rows[0] for k,rows in groups.items()
             if len(rows)==1 and direct_eligible(rows[0])}
    output={}
    for sp in ("SK","SP"):
        pairs=[(sid,season,allowed[(sid,season,"ADP")],other)
               for (sid,season,tax),other in allowed.items() if tax==sp
               and (sid,season,"ADP") in allowed]
        sites={sid for sid,_,_,_ in pairs}
        blocks=Counter(geo[sid] for sid in sites)
        dated=[(sid,season) for sid,season,adp,other in pairs
               if exact_date(adp) is not None and exact_date(adp)==exact_date(other)]
        dated_sites={sid for sid,_ in dated}
        same_vantage=sum(bool(adp["vantage"]) and adp["vantage"]==other["vantage"]
                         for sid,season,adp,other in pairs)
        same_obs_num=sum(bool(adp["obs_number"]) and adp["obs_number"]==other["obs_number"]
                         for sid,season,adp,other in pairs)
        output[sp]={
            "paired_original_site_seasons":len(pairs),
            "distinct_original_island_site_IDs":len(sites),
            "distinct_sites_per_250km_block":dict(sorted(blocks.items())),
            "blocks_ge5_distinct_paired_sites":sum(v>=5 for v in blocks.values()),
            "same_exact_day_paired_site_seasons":len(dated),
            "same_exact_day_distinct_sites":len(dated_sites),
            "same_exact_day_distinct_blocks":len({geo[sid] for sid in dated_sites}),
            "same_vantage_text_pairs_not_joint_survey":same_vantage,
            "same_obsnumber_text_pairs_not_joint_survey":same_obs_num,
            "P_A_biological_outcomes_tabulated":False,
        }
    return output

def decision(x):
    sk,sp=x["SK"],x["SP"]
    primary=(sk["distinct_original_island_site_IDs"]>=60
             and sk["blocks_ge5_distinct_paired_sites"]>=5
             and sk["same_exact_day_paired_site_seasons"]>=30
             and sk["same_exact_day_distinct_sites"]>=20
             and sk["same_exact_day_distinct_blocks"]>=4)
    comparator=(sp["distinct_original_island_site_IDs"]>=40
                and sp["blocks_ge5_distinct_paired_sites"]>=4)
    return {
        "primary_source_gate_pass":bool(primary),
        "prechosen_comparator_gate_pass":bool(comparator),
        "same_original_survey_visit_id_verified":False,
        "ecological_outcomes_opened":0,
        "ecological_models_fit":0,
        "scientific_decision":("HOLD_NO_VERIFIED_SHARED_SURVEY_ID" if primary and comparator
            else "STOP_INSUFFICIENT_OR_UNMATCHED_INDEPENDENT_COSURVEY_SUPPORT")
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--sites",required=True,type=Path)
    parser.add_argument("--surveys",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args()
    report={"status":"HOLD_AADC_ORIGINAL_SOURCE","ecological_models_fit":0}
    try:
        geo=index_islands(read_pinned(a.sites,SITE_SHA))
        paired=structural_pairs(read_pinned(a.surveys,SURVEY_SHA),geo)
        report={
            "status":"V15_SOURCE_STRUCTURE_ONLY_COMPLETE",
            "source_sites_sha256":SITE_SHA,"source_surveys_sha256":SURVEY_SHA,
            "eligible_valid_island_geography_count":len(geo),
            "primary_Adelie_partner":"SK",
            "predeclared_negative_comparator":"SP",
            "support_counts":paired,
            "NR_not_used_as_absence":True,
            "same_year_does_not_prove_same_field_visit":True,
            **decision(paired),
        }
    except Exception as exc:
        report["error_type"]=type(exc).__name__
        report["error"]=str(exc)[:500]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"]!="V15_SOURCE_STRUCTURE_ONLY_COMPLETE":
        raise SystemExit(2)

if __name__=="__main__":
    main()
