"""Audit environmentally and operationally censored observation process.

The ice-limited source years (2013, 2015, 2026) are documented by Skaret2023
and IMR2026 reports. Source observability is NOT penguin ice navigation and
not a causal regression of ice on true krill. Missing 2021/22 not audited,
2013/2026 whole-area krill density NA; 2015 has incomplete south coverage
but original Combined whole-stratum estimate was reported.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
P=HERE/"imr_krill_independent_acoustic_2023_2025_v1.py"
spec=importlib.util.spec_from_file_location("imr_source",P)
primary=importlib.util.module_from_spec(spec)
spec.loader.exec_module(primary)

ICE_YEARS=(2013,2015,2026)
CENSORED=(2013,2026)
UNKNOWN=(2021,2022)
YEARS=tuple(range(2011,2027))

def original_coverage(file,estimate_source,gate):
    records=list(csv.DictReader(Path(file).read_text(encoding="utf-8").splitlines()))
    if tuple(int(r["survey_year"]) for r in records)!=YEARS:
        raise ValueError("Historical coverage ledger year grain changed")
    source,sha=primary.source_rows(estimate_source)
    original={r["year"]:r for r in source}
    primary.check_2026_gate(gate)
    counts={"audited_survey_attempts":0,"regional_estimates":0,
            "not_estimable_documented":0,"years_without_comparable_audited_source":0,
            "explicit_ice_coverage_restriction":0,
            "ice_limited_with_estimate":0,"ice_limited_no_estimate":0,
            "documented_nonice_limited_with_estimate":0,
            "documented_ship_failure":0}
    for r in records:
        year=int(r["survey_year"])
        status=r["whole_stratum_acoustic_estimate_status"]
        attempt=r["audited_attempt_documented"]
        ice=r["pack_ice_restricted_source_reported"]
        ship=r["vessel_failure_documented"]
        expected="not_audited" if year in UNKNOWN else (
            "not_estimable" if year in CENSORED else "estimated")
        if status!=expected:raise ValueError("Full-area estimability source gate changed "+str(year))
        if (year in original)!=(status=="estimated"):
            raise ValueError("The survey-year source has false comparable regional krill value "+str(year))
        if (ice=="True")!=(year in ICE_YEARS):
            raise ValueError("Publisher-documented pack ice source case missing "+str(year))
        if (ship=="True")!=(year==2026):
            raise ValueError("2026 operational survey failure source case missing")
        if attempt not in ("True","unknown") or (attempt=="unknown")!=(year in UNKNOWN):
            raise ValueError("2021/22 activity unknown rather than missing/source conclusion")
        counts["audited_survey_attempts"]+=int(attempt=="True")
        counts["regional_estimates"]+=int(status=="estimated")
        counts["not_estimable_documented"]+=int(status=="not_estimable")
        counts["years_without_comparable_audited_source"]+=int(status=="not_audited")
        counts["explicit_ice_coverage_restriction"]+=int(ice=="True")
        counts["ice_limited_with_estimate"]+=int(ice=="True" and status=="estimated")
        counts["ice_limited_no_estimate"]+=int(ice=="True" and status=="not_estimable")
        counts["documented_nonice_limited_with_estimate"]+=int(
            ice=="not_explicitly_documented" and status=="estimated")
        counts["documented_ship_failure"]+=int(ship=="True")
    expected_counts={"audited_survey_attempts":14,"regional_estimates":12,
            "not_estimable_documented":2,"years_without_comparable_audited_source":2,
            "explicit_ice_coverage_restriction":3,
            "ice_limited_with_estimate":1,"ice_limited_no_estimate":2,
            "documented_nonice_limited_with_estimate":11,
            "documented_ship_failure":1}
    if counts!=expected_counts:
        raise ValueError("Original observation process source counts changed")
    return records,{"status":"DOCUMENTED_ICE_AND_OPERATIONAL_OBSERVABILITY_VS_KRILL_DENSITY",
       "year_roster":list(YEARS),"original_krill_estimate_years":[r["year"] for r in source],
       "source_coverage_counts":counts,
       "primary_Source_acoustic_CSV_SHA256":sha,
       "ice_limited_audited_years":list(ICE_YEARS),
       "not_estimable_ice_years":list(CENSORED),
       "2021_2022_comparable_estimate_source_status":"NOT_AUDITED_NOT_ASSUMED_NO_SURVEY",
       "source_reference":[primary.PRIMARY,primary.IMR24,primary.IMR25,primary.IMR26],
       "limitations":[
           "Study effort not an independent biological population sample. Ice status in other years is simply not explicitly documented in audited sources, NOT absence of ice.",
           "2026 biomass censoring is jointly due to pack ice and a separate trawl/propeller accident, so ice alone cannot be identified as the cause.",
           "2015 source Combined estimate exists despite limited southern coverage and does not imply a uniformly surveyed year.",
           "2013 Skaret original Combined is not estimated; 2026 IMR report explicitly cannot calculate whole-area biomass.",
           "2021-22 comparable annual source not yet audited, not necessarily a year without surveys.",
           "No evidence that research-vessel sea-ice restriction equals penguin route blockage, krill consumption or breeding response.",
           "No marine krill→fecundity or future population/N_eff/vegetation forecast is calibrated."
       ]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--coverage",required=True,type=Path)
    p.add_argument("--acoustic",required=True,type=Path)
    p.add_argument("--2026-gate",required=True,type=Path,dest="gate")
    p.add_argument("--out",required=True,type=Path)
    o=p.parse_args()
    a,result=original_coverage(o.coverage,o.acoustic,o.gate)
    o.out.mkdir(parents=True,exist_ok=True)
    (o.out/"decision.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
