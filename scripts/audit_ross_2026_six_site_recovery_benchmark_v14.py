#!/usr/bin/env python3
"""Post-exposure descriptive Ross Island six-site external census benchmark.

Reads source only through exact official CKAN resource + actual XLSX MD5
validated by the existing V13 source audit. This is NOT a test of migration,
island colonization, stage-specific reproduction or a new biological cause.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_nz_2026_ross_39_colony_census_source_v13 as source

SITES=("Cape Bird Middle","Cape Bird North","Cape Bird South",
       "Cape Crozier East","Cape Crozier West","Cape Royds")
YEARS=("1999","2001","2024")

def derive(receipt):
    if receipt.get("status")!="SOURCE_XLSX_VALIDATED_AND_STRUCTURAL_COVERAGE_REPORTED":
        raise ValueError("Official NZ census source not successfully validated")
    if receipt.get("verified_md5")!=source.SOURCE_MD5:
        raise ValueError("NZ source MD5 mismatch")
    six=receipt.get("focal_Royds_Crozier_CapeBird_source_counts",{})
    if set(six)!=set(SITES):
        raise ValueError("Exact six Ross Island units not present in the original roster")
    cells={}
    for name in SITES:
        vals=six[name]
        if any(year not in vals for year in YEARS):
            raise ValueError("All three years must have real recorded counts at every selected site")
        row={year:vals[year] for year in YEARS}
        if any(not isinstance(v,int) or v<=0 for v in row.values()):
            raise ValueError("Published site counts must be explicitly positive numbers for benchmark")
        cells[name]=row
    totals={yr:sum(cells[s][yr] for s in SITES) for yr in YEARS}
    growth=totals["2024"]/totals["1999"]
    by_site={}
    for s in SITES:
        v=cells[s]
        expected=v["1999"]*growth
        by_site[s]={
            "source_counts_1999_2001_2024":v,
            "1999_to_2001_fraction_change":v["2001"]/v["1999"]-1,
            "1999_to_2024_fraction_change":v["2024"]/v["1999"]-1,
            "2001_to_2024_fraction_change":v["2024"]/v["2001"]-1,
            "share_of_six_1999":v["1999"]/totals["1999"],
            "share_of_six_2024":v["2024"]/totals["2024"],
            "expected_2024_pairs_if_all_sites_same_proportional_growth":expected,
            "observed_minus_proportional_expected_2024_pairs":v["2024"]-expected,
            "fraction_of_net_total_gain":(v["2024"]-v["1999"])/(totals["2024"]-totals["1999"])
        }
    bm=by_site["Cape Bird Middle"]
    ro=by_site["Cape Royds"]
    yearcov=receipt.get("surveyed_positive_zero_missing_by_year",{})
    allcount=receipt.get("value_classes",{})
    if sum(allcount.get(k,0) for k in ("EXPLICIT_ZERO_SOURCE","POSITIVE_NUMERIC_COUNT","MISSING_BLANK","TEXT_UNRESOLVED","OTHER_NONNEG_INTEGER_REVIEW")) !=39*44:
        raise ValueError("39 by 44 site-year classification does not reconcile")
    return {
        "status":"ROSS_ISLAND_SIX_NAMED_SITE_PAIR_CENSUS_DESCRIPTIVE_NO_CAUSAL_IMMIGRATION",
        "source_doi":"10.7931/kf06-x745",
        "source_verification_md5":source.SOURCE_MD5,
        "same_named_site_count":len(SITES),
        "year_set":[int(y) for y in YEARS],
        "source_six_site_breeding_pair_totals":totals,
        "total_six_site_1999_to_2024_fraction_change":growth-1,
        "1999_to_2001_fraction_shock_in_six":totals["2001"]/totals["1999"]-1,
        "site_results":by_site,
        "size_similar_reference_1999":{
            "Royds_1999_pairs":ro["source_counts_1999_2001_2024"]["1999"],
            "Cape_Bird_Middle_1999_pairs":bm["source_counts_1999_2001_2024"]["1999"],
            "different_2001_shock_magnitudes_not_matched_or_controlled":True
        },
        "ross_royds_2024_share_relative_to_1999":(
            ro["share_of_six_2024"]/ro["share_of_six_1999"]),
        "Crozier_West_fraction_of_total_net_1999_2024_gain":(
            by_site["Cape Crozier West"]["fraction_of_net_total_gain"]),
        "source_all_39_site_year_cells":39*44,
        "source_positive_numeric_entries":allcount.get("POSITIVE_NUMERIC_COUNT",0),
        "source_explicit_zeros":allcount.get("EXPLICIT_ZERO_SOURCE",0),
        "source_missing_entries":allcount.get("MISSING_BLANK",0),
        "source_2020_n_valid_colony_counts":sum(yearcov.get("2020",{}).get(k,0)
            for k in ("EXPLICIT_ZERO_SOURCE","POSITIVE_NUMERIC_COUNT")),
        "single_Ross_Island_six_subsites_not_six_independent_islands":True,
        "georeferenced_2024_Cape_Barne_census_observation":False,
        "regional_pair_growth_not_individual_migration":True,
        "method_overlap_with_prior_Ross_pair_count_sources_unresolved":True,
        "posterior_demographic_nest_recruitment_model_fitted":False,
        "no_new_causal_island_effect":True,
        "post_outcome_exploratory_not_confirmation":True,
        "frozen_PR189_unmodified":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    data=source.run()
    if data.get("status")!="SOURCE_XLSX_VALIDATED_AND_STRUCTURAL_COVERAGE_REPORTED":
        d={"status":"HOLD_UPSTREAM_OFFICIAL_SOURCE", "upstream":data.get("status"),
           "no_new_causal_island_effect":True,"frozen_PR189_unmodified":True}
    else:
        d=derive(data)
    a.out.write_text(json.dumps(d,indent=2)+"\n")
    print("SIX_SITE_EXTERNAL_CENSUS",d["status"])
    print("SIX_SITE_TOTALS",d.get("source_six_site_breeding_pair_totals",{}))
    for n,v in d.get("site_results",{}).items():
        print("SITE",n,"YEAR_RATIO_2024_1999",round(1+v["1999_to_2024_fraction_change"],6),
              "OBSERVED_PAIRS",v["source_counts_1999_2001_2024"])
    print("NO_DEMOGRAPHIC_SOCIAL_CAUSAL_TEST",True)
if __name__=="__main__":main()
