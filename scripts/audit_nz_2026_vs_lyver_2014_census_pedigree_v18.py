#!/usr/bin/env python3
"""2012 old-versus-new Ross census source lineage, not a new biological result.

MD5-verify NZ 2026 original 39-site XLSX, sum fixed 2012 Bird 3 and Crozier 2
subsites, compare directly with published Lyver et al. (2014) 2012 census
counts. Matching source values are not independent biological replication.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_nz_2026_ross_39_colony_census_source_v13 as source

REF_PUBLISHED_2012={"Cape Royds":3083,"Cape Bird":75696,"Cape Crozier":272340}
ORIGINAL_PUBLISHER_MD5="195a9027a0d18012812b09fb345ac60e"
COMPONENTS={
    "Cape Royds":["Cape Royds"],
    "Cape Bird":["Cape Bird North","Cape Bird Middle","Cape Bird South"],
    "Cape Crozier":["Cape Crozier East","Cape Crozier West"],
}

def compare(census_report):
    if census_report.get("status")!="SOURCE_XLSX_VALIDATED_AND_STRUCTURAL_COVERAGE_REPORTED":
        raise ValueError("Original publisher source not validated")
    if census_report.get("verified_md5")!=ORIGINAL_PUBLISHER_MD5:
        raise ValueError("Author 2026 census MD5 mismatch")
    site_counts=census_report.get("focal_Royds_Crozier_CapeBird_source_counts",{})
    if set(site_counts)!=set(sum(COMPONENTS.values(),[])):
        raise ValueError("Original six Ross 2012 component roster not exactly matched")
    audits={}
    for aggregate,units in COMPONENTS.items():
        nums=[]
        for name in units:
            value=site_counts[name].get("2012")
            if type(value)!=int or value<=0:
                raise ValueError("Missing or invalid original 2012 source count at "+name)
            nums.append(value)
        observed=sum(nums)
        ref=REF_PUBLISHED_2012[aggregate]
        audits[aggregate]={
            "original_NZ_2026_2012_subsite_components":dict(zip(units,nums)),
            "NZ_2026_2012_aggregate":observed,
            "Lyver_2014_published_2012_aggregate":ref,
            "exact_reproduction":observed==ref,
            "difference":observed-ref
        }
    allmatch=all(z["exact_reproduction"] for z in audits.values())
    return {
        "status":"SAME_PUBLISHED_2012_CENSUS_AGGREGATES_REPRODUCED" if allmatch else
                "HOLD_DIFFERENT_PUBLISHED_2012_CENSUS_AGGREGATES",
        "source_pedigree_comparison_year":2012,
        "source_original_census_2026_MD5_verified":ORIGINAL_PUBLISHER_MD5,
        "original_2014_paper_Doi":"10.1371/journal.pone.0091188",
        "2026_dataset_Doi":"10.7931/kf06-x745",
        "n_2014_independent_aggregate_colony_counts_compared":len(audits),
        "original_2026_survey_subsite_components_compared":sum(len(x) for x in COMPONENTS.values()),
        "published_source_overlaps":audits,
        "exact_three_aggregate_match":allmatch,
        "2026_independent_2012_new_measurement_claim_supported":False,
        "independent_archive_not_independent_census_observations":allmatch,
        "no_other_year_independence_claim":True,
        "source_count_no_individual_migration_or_success_information":True,
        "no_new_causal_penguin_island_ecology_result":True,
        "not_a_preregistered_biological_hypothesis_test":True,
        "PR189_science_frozen":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    x=source.run()
    if x.get("status")!="SOURCE_XLSX_VALIDATED_AND_STRUCTURAL_COVERAGE_REPORTED":
        report={"status":"HOLD_SOURCE_UNRETRIEVABLE",
                "upstream":x.get("status"),
                "no_new_causal_penguin_island_ecology_result":True,
                "PR189_science_frozen":True}
    else:
        report=compare(x)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print("ORIGINAL_2012_COUNT_PEDIGREE",report["status"])
    for name,ref in report.get("published_source_overlaps",{}).items():
        print("PUBLISHED_AGGREGATE_2012",name,ref["NZ_2026_2012_aggregate"],
              "LYVER_2014",ref["Lyver_2014_published_2012_aggregate"],
              "MATCH",ref["exact_reproduction"])
    print("INDEPENDENT_REPLICATION_2012",False)
if __name__=="__main__":
    main()
