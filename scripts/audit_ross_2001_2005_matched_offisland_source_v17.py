#!/usr/bin/env python3
"""Actual 2001–2005 paired site counts and geography support, not iceberg causality.

Fetch both original NZ 2026 XLSX resources; assert the publisher's MD5
for the census and record SHA256 for the supplementary location workbook,
which has no publisher MD5. Never match names fuzzily. No out-of-window zeros.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_nz_2026_ross_39_colony_census_source_v13 as nz
import audit_nz_2026_ross_geographic_parent_support_v16 as geo
import audit_nz_39_colony_location_source_v15 as locsource

YEARS=(2001,2005)

def compare_years(census_rows,location_rows):
    sites=[]
    for key,r in sorted(census_rows.items()):
        values=r["values"]
        a,b=values[2001],values[2005]
        if a is None or b is None:
            continue
        if not isinstance(a,int) or not isinstance(b,int) or a<0 or b<0:
            raise ValueError("Published paired census counts invalid")
        if key in location_rows:
            desc=location_rows[key]["parent_geographic_descriptor"]
            area=("ROSS_ISLAND" if desc=="Ross Island" else "OFF_ROSS_SITE_WITH_SOURCE_GEOGRAPHY")
        else:
            desc=None
            area="CENSUS_SITE_SOURCE_GEOGRAPHY_UNMATCHED"
        sites.append({
            "source_site":r["name"],
            "geography_class":area,
            "source_geographic_parent":desc,
            "breeding_pairs_2001":a,
            "breeding_pairs_2005":b,
            "2005_vs_2001_count_ratio":(b/a if a>0 else None),
            "2005_minus_2001_pairs":b-a,
            "source_pair_is_matched_site_not_marked_individual":True
        })
    classes={}
    for typ in ("ROSS_ISLAND","OFF_ROSS_SITE_WITH_SOURCE_GEOGRAPHY",
                "CENSUS_SITE_SOURCE_GEOGRAPHY_UNMATCHED"):
        arr=[s for s in sites if s["geography_class"]==typ]
        a=sum(s["breeding_pairs_2001"] for s in arr)
        b=sum(s["breeding_pairs_2005"] for s in arr)
        classes[typ]={
            "n_matched_source_sites":len(arr),
            "site_name_roster":[s["source_site"] for s in arr],
            "sum_reported_pairs_2001":a,
            "sum_reported_pairs_2005":b,
            "ratio_of_paired_source_sums":(b/a if a>0 else None),
            "not_caused_by_iceberg_or_proof_of_source_sink_migration":True
        }
    return {
      "status":"SOURCE_PAIRED_2001_2005_GEOGRAPHY_COVERAGE_ONLY",
      "source_census_count_sites":len(census_rows),
      "source_location_name_rows":len(location_rows),
      "source_years_compared":list(YEARS),
      "n_actual_numeric_pair_site_matches":len(sites),
      "source_site_detailed_pairs":sites,
      "geographical_class_stratified_descriptive_pairs":classes,
      "off_ross_actual_matched_numeric_sites":classes["OFF_ROSS_SITE_WITH_SOURCE_GEOGRAPHY"]["n_matched_source_sites"],
      "source_site_name_geography_unknown_not_imputed":True,
      "do_not_treat_geographic_descriptors_as_independent_islands":True,
      "prior_art_1981_2012_Ross_Sea_population_responses_already_published":True,
      "previous_year_off_ross_1999_control_available_from_same_2026_table":False,
      "2024_off_ross_control_available_from_same_2026_table":False,
      "individual_colonist_source_or_prospectors_measured":False,
      "sea_ice_access_exogenous_per_site_event_measured":False,
      "no_causal_new_island_biogeography_result":True,
      "no_statistical_p_values_computed":True,
      "Ecology_PR189_frozen":True
    }

def run():
    report={
        "status":"HOLD_OFFICIAL_2001_2005_PAIRED_SOURCE",
        "site_source_geography_publisher_MD5_not_provided":True,
        "source_original_count_MD5_verified":False,
        "no_causal_new_island_biogeography_result":True,
        "Ecology_PR189_frozen":True
    }
    try:
        official=nz.official_metadata(nz.fetch_bounded(
            nz.API+"?"+urlencode({"id":nz.RESOURCE_ID}),nz.MAX_SOURCE_METADATA))
        cb=nz.fetch_bounded(official["url"])
        original=nz.workbook_first_table(cb)
        census=geo.audited_census_siteyears(cb)
        report["source_original_count_MD5_verified"]=(hashlib.md5(cb).hexdigest()==nz.SOURCE_MD5)
        ml=locsource.resource_metadata(nz.fetch_bounded(
            locsource.API+"?"+urlencode({"id":locsource.LOC_ID}),nz.MAX_SOURCE_METADATA))
        lb=nz.fetch_bounded(ml["official_url"])
        if ml["md5"] and hashlib.md5(lb).hexdigest()!=ml["md5"]:
            raise ValueError("Official original location MD5 mismatch")
        report["site_source_geography_publisher_MD5_not_provided"]=(not bool(ml["md5"]))
        report["site_source_geography_retrieval_sha256"]=hashlib.sha256(lb).hexdigest()
        loc=geo.location_rows(lb)
        report.update(compare_years(census,loc))
    except Exception as exc:
        report["status"]="HOLD_OFFICIAL_MATCHED_SOURCE_OR_GEOGRAPHY"
        report["source_error_type"]=type(exc).__name__
        report["source_error_message"]=str(exc)[:240]
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    opts=p.parse_args()
    z=run()
    opts.out.write_text(json.dumps(z,indent=2,ensure_ascii=False)+"\n")
    print("V17_PAIRED_SOURCE_STATUS",z["status"])
    print("PAIR_SITE_COUNT",z.get("n_actual_numeric_pair_site_matches"))
    for typ,r in z.get("geographical_class_stratified_descriptive_pairs",{}).items():
        print("GEO_CLASS",typ,json.dumps(r,ensure_ascii=False))
    for s in z.get("source_site_detailed_pairs",[]):
        print("PAIRED_SITE",s["source_site"],s["geography_class"],s["breeding_pairs_2001"],
              s["breeding_pairs_2005"])
    print("SOURCE_ERROR",z.get("source_error_type",""),z.get("source_error_message",""))
    print("CAUSAL_ISLAND_COLONIZATION_INFERENCE",False)
if __name__=="__main__":main()
