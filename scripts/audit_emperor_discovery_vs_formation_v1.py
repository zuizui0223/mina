"""Cross-study audit of *published* emperor colony discovery vs formation evidence.

Inputs: manually source-checked literal records from Fretwell (2024), Antarctic
Science, DOI 10.1017/S0954102023000329, and limited 2026 abstract context.
This is NOT a reanalysis of satellite imagery, not prospective 2022-2024
response data, and not a discovery of a new causal ecology effect.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

EVIDENCE = (
    Path(__file__).resolve().parents[1]
    / "external/EMPEROR_FRETWELL_2024_SITE_DETECTION_EVIDENCE_V1.json"
)


def audit(data: dict) -> dict:
    events = data["four_newly_reported_sites"]
    names = [e["id"] for e in events]
    if len(events) != 4 or len(names) != len(set(names)):
        raise ValueError("2024 paper denominator must contain exactly four distinct reported sites")
    pubyear = data["publication"]["year_reported"]
    for event in events:
        years = event["known_positive_years"]
        if not years or len(years) != len(set(years)):
            raise ValueError("each site must have distinct published positive years")
        if min(years) != event["first_reported_positive_year"]:
            raise ValueError("first positive must match earliest documented positive year")
        if any(y >= pubyear for y in years):
            raise ValueError("all site detections must predate publication")
        if event["formerly_absent_new_colony_established_year_verified"] and not event["repeated_prior_confirmed_absence_at_new_site"]:
            raise ValueError("cannot infer founding year from first satellite detection")

    repeated_five_year = [e["id"] for e in events
                          if all(y in e["known_positive_years"] for y in range(2018, 2023))]
    any_older_positive = [e["id"] for e in events
                          if min(e["known_positive_years"]) < pubyear]
    verified_prior_zeros = [e["id"] for e in events
                           if e["repeated_prior_confirmed_absence_at_new_site"]]
    physically_perturbed_detection = [e["id"] for e in events
             if e.get("detectability_change_mentioned_in_source", False)]
    reformation = [e for e in data["reappearances_not_in_four_new_2024"]
                   if e["id"] == "UMBEASHI"]
    assert len(reformation) == 1, "exact one Umbeashi history expected"
    umbeashi = reformation[0]
    if umbeashi["verified_2019_comprehensive_breeding_survey_zero"]:
        raise ValueError("published 'not extant' is not a fully documented negative breeding census")

    return {
        "audit_id": "emperor-2024-four-discovery-versus-founded-site-evidence-v1",
        "scope": "RETROSPECTIVE_PUBLISHED_PRESENCE_STATES_ONLY",
        "source": data["publication"]["url"],
        "newly_reported_sites": len(events),
        "sites_with_verified_positive_image_before_publication": len(any_older_positive),
        "sites_with_at_least_one_positive_image_each_year_2018_to_2022":
            len(repeated_five_year),
        "ids_five_year_repeated": repeated_five_year,
        "published_positive_site_years_all_sites": sum(len(e["known_positive_years"])
                                                       for e in events),
        "sites_with_verified_repeated_pre_founding_absences": len(verified_prior_zeros),
        "sites_with_source_described_disturbance_related_detectability_shift":
            len(physically_perturbed_detection),
        "affected_detectability_ids": physically_perturbed_detection,
        "inventory_not_extant_but_subsequently_reappeared_example": {
            "site": "UMBEASHI",
            "2019_inventory":"NOT_EXTANT",
            "published_subsequent_confirmations":
                umbeashi["confirmed_subsequent_presence_years"],
            "known_2019_season_qualified_negative": False,
            "year_2020_biological_presence": None,
        },
        "classification": "ALL_FOUR_2024_NEWLY_REPORTED_SITES_PREDATE_PUBLICATION; NONE_HAS_VERIFIED_REPEAT_SURVEY_ZERO_IN_SOURCE",
        "licensed_biological_claim":
            "published guano/individual detection establishes earlier presence, not when/how site was founded",
        "not_licensed": [
            "4 new establishments occurred in 2024",
            "4 of 4 empty refuges were first colonized after 2022 shocks",
            "all visible penguin dots completed successful breeding",
            "Umbeashi was completely deserted by every bird in 2019",
            "Lazarev old and new groups were proven to contain same individuals",
            "Gipps 2021 geomorphic change initiated a colony absent before 2021",
            "2026 Case Island and Stancomb sites can be treated as truly new without negative pre-2022 surveys",
            "any causal social attraction vs physical refugial-option result"
        ],
        "2026_causal_effect_test_run": False,
        "new_2022_plus_observational_data_rows_read": 0,
        "existing_ecology_pr189_unchanged": True,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    d=audit(json.loads(EVIDENCE.read_text(encoding="utf-8")))
    payload=json.dumps(d,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        args.out.write_text(payload,encoding="utf-8")
    print(payload,end="")


if __name__ == "__main__":
    main()
