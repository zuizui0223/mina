#!/usr/bin/env python3
"""Audit exact MAPPPD publisher source references for 357 species pair/site-years.

Crucially: the earlier source CSV *is nests-only*: original comparison_audit
audit.py filters obs.type=='nests' BEFORE aggregation. This tool examines
original publisher citekeys and vantage; it does not refit ecological outcomes.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "original_source_method_audit"
OUT.mkdir(parents=True, exist_ok=True)

PAIR_NAMES = (
    ("ADPE","GEPE"),
    ("ADPE","CHPE"),
    ("CHPE","GEPE"),
)
FIXED_PAIR_SUPPORT={
    "ADPE__GEPE":(100,25),
    "ADPE__CHPE":(89,24),
    "CHPE__GEPE":(168,33)
}

def load_csv(p):
    with p.open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def emit_csv(path, rows):
    if not rows:raise ValueError("Empty source QA table")
    with path.open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)

def load_pinned_provider_module():
    p=ROOT/"work/climate_penguin/derive_MAPPPD5_original_macro_source_v1.py"
    spec=importlib.util.spec_from_file_location("mapppd_pinned_2026",p)
    assert spec and spec.loader
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def primary_original_source_rows(module):
    import requests
    with requests.Session() as session:
        session.headers.update({"User-Agent":"mina-original-MAPPPD5-357-siteyear-source-citation-audit-20261110"})
        binary={name:module.source_data(session,name)
                for name in ("release","sites","observations_p1","observations_p2")}
    release=json.loads(binary["release"])
    if release.get("version")!="5.0" or release.get("release_date")!="2026-10-21":
        raise ValueError("Original pinned MAPPPD publisher release drift")
    ss=module.tabular(binary["sites"],module.SITE_FIELDS)
    pp1=module.tabular(binary["observations_p1"],module.OBS_FIELDS)
    pp2=module.tabular(binary["observations_p2"],module.OBS_FIELDS)
    if (len(ss),len(pp1),len(pp2))!=(729,5000,487):
        raise ValueError("Publisher row count/pagination changed")
    return pp1+pp2,{
        "version":release["version"],
        "release_date":release["release_date"],
        "publisher_source_sha256":{k:hashlib.sha256(v).hexdigest() for k,v in binary.items()},
        "publisher_original_observation_rows":len(pp1)+len(pp2),
        "original_site_rows":len(ss),
        "original_publisher_dataset":"Oceanites, Inc. MAPPPD v5.0 released 2026-10-21"
    }

def source_exact_matches(publisher,site,year,species,count,method):
    matches=[]
    for z in publisher.get((site,species,year),[]):
        if z["type"]!="nests" or z["vantage"].strip()!=method:
            continue
        original=z["count"].strip().replace(",","")
        try:
            original_value=float(original)
        except ValueError:
            continue
        if not math.isfinite(original_value):
            continue
        if math.isclose(original_value,float(count),rel_tol=0,abs_tol=1e-6):
            matches.append(z)
    return matches

def main():
    original_aggregate=load_csv(ROOT/"outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv")
    original_meta = json.loads((ROOT/"outputs/comparison_audit/mapppd_audit_summary.json").read_text(encoding="utf-8"))
    root_script=(ROOT/"work/comparison_audit/audit.py").read_text(encoding="utf-8")
    # This is exact source generator filter, which is the primary concern for nests versus adults/chicks.
    if "obs.type=='nests'" not in root_script:
        raise ValueError("Upstream original count unit nests-only lineage missing")
    if original_meta["unambiguous_site_seasons"]!=2999 or len(original_aggregate)!=2999:
        raise ValueError("Original 2999-count source sample changed")
    selected=load_csv(HERE/"outputs/source_observed_2456.csv")
    coseasons=load_csv(HERE/"outputs/observed_multi_species_same_year_303.csv")
    if len(selected)!=2456 or len(coseasons)!=303:
        raise ValueError("The original 595-site recorded-count source changed")
    bysurvey={(z["site_id"],z["species"],int(z["season"])):z for z in selected}
    if len(bysurvey)!=2456:
        raise ValueError("Duplicate selected colony-species-year")
    bysite_year={(z["site_id"],int(z["census_season"])):z for z in coseasons}
    if len(bysite_year)!=303:raise ValueError("Original co-observed colony-year duplicates")

    publisher_module=load_pinned_provider_module()
    primary,publisher_receipt=primary_original_source_rows(publisher_module)
    pindex=defaultdict(list)
    original_census_types=Counter()
    ids=set()
    for z in primary:
        if z["id"] in ids:raise ValueError("Publisher original observation IDs duplicate")
        ids.add(z["id"])
        original_census_types[z["type"]]+=1
        try:
            season=int(z["season"])
        except (ValueError,TypeError):
            continue
        pindex[(z["site_id"],z["species_id"],season)].append(z)

    qa=[]
    for (site,year),source in sorted(bysite_year.items()):
        if not 1991<=year<=2020:
            continue
        for a,b in PAIR_NAMES:
            if source[a+"_observed_nests"]=="" or source[b+"_observed_nests"]=="":
                continue
            pair=a+"__"+b
            oa=bysurvey.get((site,a,year))
            ob=bysurvey.get((site,b,year))
            if oa is None or ob is None:
                raise ValueError("A species missing from selected source census")
            if int(oa["observed_nest_count"])!=int(source[a+"_observed_nests"]):
                raise ValueError("Publisher selected source biological count differs")
            if int(ob["observed_nest_count"])!=int(source[b+"_observed_nests"]):
                raise ValueError("Publisher selected source species count differs")
            method_a=oa["original_survey_method"]
            method_b=ob["original_survey_method"]
            compatible_method=method_a==method_b
            x=source_exact_matches(pindex,site,year,a,oa["observed_nest_count"],method_a)
            y=source_exact_matches(pindex,site,year,b,ob["observed_nest_count"],method_b)
            cx={z["citekey"].strip() for z in x if z["citekey"].strip()}
            cy={z["citekey"].strip() for z in y if z["citekey"].strip()}
            common=sorted(cx&cy)
            qa.append({
                "species_pair":pair,"source_site_id":site,"breeding_season":year,
                "source_region":oa["source_region"],
                "selected_method_species_a":method_a,
                "selected_method_species_b":method_b,
                "same_recorded_method":compatible_method,
                "original_publisher_matched_nest_count_method_a":len(x),
                "original_publisher_matched_nest_count_method_b":len(y),
                "both_species_match_original_MAPPPD5_published_count_method":bool(x and y),
                "both_original_source_citekeys_nonempty":bool(cx and cy),
                "same_nonempty_original_publication_citekey":bool(common),
                "shared_citekeys":";".join(common),
                "strict_shared_publisher_source_and_method":bool(compatible_method and common),
                "exact_same_field_observation_day_known":False,
                "not_a_species_absence_or_future_prediction":True
            })
    if len(qa)!=357:
        raise ValueError(f"Pre-frozen observed site-year species pair count drift: {len(qa)}")
    if sum(z["same_recorded_method"]=="False" for z in qa)!=1 or [
            (z["source_site_id"],z["breeding_season"],z["species_pair"])
            for z in qa if not z["same_recorded_method"]] not in ([],[("PEIN",2015,"ADPE__GEPE")]):
        # Python booleans aren't str; check again below.
        pass
    mixed=[z for z in qa if z["same_recorded_method"] is False]
    if len(mixed)!=1 or [(z["source_site_id"],z["breeding_season"],z["species_pair"]) for z in mixed]!=[("PEIN",2015,"ADPE__GEPE")]:
        raise ValueError("Original 1/357 method mismatch changed")
    bypair=defaultdict(list)
    for z in qa:bypair[z["species_pair"]].append(z)
    summary={}
    for pair,(count,sites) in FIXED_PAIR_SUPPORT.items():
        rows=bypair[pair]
        if len(rows)!=count or len({z["source_site_id"] for z in rows})!=sites:
            raise ValueError("The three original co-observed species-pair cohorts changed")
        summary[pair]={
            "reported_same_site_season_source_pairs":len(rows),
            "distinct_original_site_ids":len({z["source_site_id"] for z in rows}),
            "pairs_sharing_method":sum(z["same_recorded_method"] for z in rows),
            "pairs_matching_both_original_published_nest_count_and_method":sum(
                z["both_species_match_original_MAPPPD5_published_count_method"] for z in rows),
            "pairs_sharing_nonempty_original_citekey_and_same_vantage":sum(
                z["strict_shared_publisher_source_and_method"] for z in rows),
            "sites_with_strict_shared_citation_method":len({
                z["source_site_id"] for z in rows
                if z["strict_shared_publisher_source_and_method"]
            }),
            "no_exact_same_day_census_verified":True
        }

    receipt={
        "status":"PUBLISHER_ORIGINAL_NESTS_FILTER_AND_PAIR_SOURCE_COMPATIBILITY_AUDITED",
        "project_original_2999_count_aggregation_nests_only":True,
        "matched_source_mapppd_snapshot_input_2999_site_species_years":len(original_aggregate),
        "original_595_site_panel_selected_census_rows":len(selected),
        "original_paired_colony_species_season_comparisons":len(qa),
        "n_pair_examples_different_observed_method":len(mixed),
        "publisher_2026_v5_original":publisher_receipt,
        "publisher_v5_counts_by_record_type":dict(original_census_types),
        "pair_specific_support":summary,
        "inferential_boundary":[
          "Same nominal colony season and same vantage do NOT imply exact same calendar day or equal field effort.",
          "Different original publisher citekeys cannot be relabeled as a genuinely joint co-census, regardless of equal season.",
          "A common citekey and vantage is stronger provenance but still does not prove identical survey dates.",
          "The old mapppdr original cohort may not be identical to the Oct-2026 MAPPPD v5 API; count/method matches are audited explicitly.",
          "This verifies survey and original citation lineage, NOT sea-ice effect or biology; do not select a significant subcohort by citation.",
          "All source data here are original nests, not adult/chick abundance."
        ]}
    emit_csv(OUT/"original_357_pairs_source_method_and_citation.csv",qa)
    (OUT/"original_357_pair_publisher_citation_provenance.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("MAPPPD_ORIGINAL_357_PAIR_NEST_AND_CITATION_SOURCE_GATE="+json.dumps(receipt,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
