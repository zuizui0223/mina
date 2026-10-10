#!/usr/bin/env python3
"""Author-published narrative evidence audit, never an invented annual census.

Emslie 2026 Cape Royds/Barne is an independent published historical counterexample
to *unconditional sufficiency* of old nests/guano for current breeding.
It does not identify a treatment effect or the fate of a specifically failed
pioneer, and gap years remain UNSURVEYED/UNKNOWN for this evidence source.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

EXPECTED_IDS=(
    "old_1912",
    "attempts_1960s",
    "five_1988_89",
    "abandonment_late_1990s",
    "jan_2001",
    "remnant_2024"
)
EXPECTED_YEAR_GAPS_WITHOUT_SOURCE_ROSTER=("1999","2000","2002","2023")


def audit(contract):
    records=contract.get("frozen_evidence_before_any_model",[])
    by={x["evidence_id"]:x for x in records}
    if tuple(x["evidence_id"] for x in records)!=EXPECTED_IDS or len(by)!=len(records):
        raise ValueError("Source narrative event roster changed")
    if any(x.get("breeding_pair_count") is not None
           for x in records if x["evidence_id"]!="five_1988_89"):
        raise ValueError("Unsourced exact breeding counts detected")
    if by["five_1988_89"]["breeding_pair_count"]!=5:
        raise ValueError("Published 1988/89 five occupied nests changed")
    last=by["remnant_2024"]
    if last.get("physical_legacy_confirmed") is not True:
        raise ValueError("No modern physical memory to contrast")
    if contract["conclusions_supported"]["physical_remnants_alone_guarantee_breeding_reestablishment"]:
        raise ValueError("Physical memory sufficiency false")
    if any(x.get("observed_breeding_success") for x in records):
        raise ValueError("Historical nest presence cannot become chick success")
    if contract["conclusions_supported"]["historical_zero_breeding_in_every_unsampled_year"]:
        raise ValueError("Narrative source does not support zero-filled annual panel")
    time_spans={
        "years_from_1988_observed_nesting_to_2024_remnants":2024-1988,
        "years_from_1988_observed_nesting_to_Jan2001_nondetection":2001-1988,
        "years_from_Jan2001_nondetection_to_Dec2024_abandoned_with_remnants":2024-2001
    }
    return {
        "status":"NEGATIVE_EXAMPLE_UNCONDITIONAL_PHYSICAL_LEGACY_SUFFICIENCY",
        "source_doi":contract["source"]["doi"],
        "published_evidence_entries":len(records),
        "published_contemporary_occupied_nests_in_1988_89":5,
        "post_1988_reported_abandonment_by_late_1990s":True,
        "jan2001_no_breeding_pairs_during_visit":True,
        "dec2024_physical_pebble_and_guano_remains":True,
        "dec2024_source_reports_site_still_abandoned":True,
        "chronological_elapsed_year_differences_NOT_absence_duration":time_spans,
        "no_unverified_annual_absence_imputation":True,
        "historical_specific_year_zeros_inferred_from_unmonitored_periods":0,
        "site_survey_status_each_unsampled_gap":{
            y:"UNKNOWN_NOT_OBSERVED_ABSENT" for y in EXPECTED_YEAR_GAPS_WITHOUT_SOURCE_ROSTER
        },
        "no_directly_verified_1988_chick_fledging":True,
        "no_independent_causal_immigration_or_ice_access_effect":True,
        "no_observed_genuinely_failed_pioneer_vs_never_used_patch_comparison":True,
        "structural_example_only_not_novel_mechanistic_discovery":True,
        "new_penguin_raw_field_data_read":0,
        "fitted_effect_size_or_pvalue":False,
        "PR189_frozen_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    obj=json.loads(a.contract.read_text())
    report=audit(obj)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print("CAPE_BARNE_SOURCE_RESULT",report["status"])
    print("HISTORIC_1988_NESTS",report["published_contemporary_occupied_nests_in_1988_89"])
    print("2024_PERSISTENT_NEST_STRUCTURES",report["dec2024_physical_pebble_and_guano_remains"])
    print("REPORT_2024_ABANDONED",report["dec2024_source_reports_site_still_abandoned"])
    print("CONTINUOUS_ZERO_PANEL",False)
    print("SOCIAL_CAUSAL_ESTIMATE",False)


if __name__=="__main__":
    main()
