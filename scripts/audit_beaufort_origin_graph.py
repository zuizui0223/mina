"""Audit Beaufort north-shore colonization origin *evidence types*, not immigration.

Uses public literature/ASPA management-plan statements only.
Does NOT download or read band/resight individual records, estimate movement
probabilities, or touch the frozen Ross shock/recovery submission.

Run: python scripts/audit_beaufort_origin_graph.py [--out report.json]
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

SOURCES = {
    "aspa_2003": "https://documents.ats.aq/recatt/att155_e.pdf",
    "aspa_2015": "https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/aspa/aspa_pdf_en/Measure5_ASPA105.pdf",
    "larue_2013": "https://doi.org/10.1371/journal.pone.0060568",
    "lyver_2014": "https://doi.org/10.1371/journal.pone.0091188",
    "kappes_2021": "https://doi.org/10.1111/1365-2656.13422",
    "munilla_2016": "https://doi.org/10.1371/journal.pone.0147222",
    "herman_lynch_2022": "https://doi.org/10.1093/ornithapp/duac014",
    "banding_2021": "https://doi.org/10.15784/601443",
    "resight_2021": "https://doi.org/10.15784/601444",
}
NODES = ["BEAU_SOUTH", "BEAU_NORTH", "ROSS_ROYDS", "ROSS_BIRD", "ROSS_CROZIER"]

# All edges in this array are historical *sighting evidence*, NOT confirmed
# first reproduction or estimated movement. Banding locality need not be natal.
VISITATION_EDGES = [
    {
        "source": "BEAU_SOUTH", "destination": "ROSS_AGGREGATE",
        "observation": "Beaufort chick-banded birds seen at one or more Ross colonies",
        "source_mark_status": "near_fledging_chicks_at_cadwalader_south",
        "evidence_stage": "seen_visiting", "first_breeding_confirmed": False,
        "destination_subcolony_resolved": False,
        "source_citations": ["larue_2013", "aspa_2015"]
    },
    {
        "source": "BEAU_BANDED_SOURCE_SITE_UNVERIFIED", "destination": "BEAU_NORTH",
        "observation": "Several Beaufort-banded penguins seen at LaRue north-coast site",
        "source_mark_status": "reported_beaufort_banded; main_colony_banding_predominated",
        "evidence_stage": "seen_at_destination", "first_breeding_confirmed": False,
        "source_main_vs_north_mark_identity_verified": False,
        "site_identity_aspa_1995_vs_larue_2004_verified": False,
        "source_citations": ["larue_2013", "aspa_2015"]
    },
    *[
        {
            "source": src, "destination": "BEAU_NORTH",
            "observation": f"Penguins banded at {src} seen especially at north beach",
            "source_mark_status": "banding_locality_not_proven_natal_origin",
            "evidence_stage": "seen_at_destination", "first_breeding_confirmed": False,
            "source_citations": ["aspa_2015"]
        } for src in ("ROSS_ROYDS", "ROSS_BIRD", "ROSS_CROZIER")
    ],
]

STRUCTURAL_SUPPORT = {
    "north_1994_95_2_pairs_3_chicks": True,
    "north_subfossil_colony_deposits_reported": True,
    "north_ice_free_beach_at_1995_visit": True,
    "northern_beach_ice_free_suitability_series_before_1994": False,
    "verified_north_absence_with_survey_effort_before_1994": False,
    "georeferenced_aspa_north_1995_and_larue_northeast_2004_identity": False,
    "south_main_declined_over_1981_2000_trend": True,
    "local_main_colony_density_at_1995_colonization_timing": False,
    "source_origin_tagged_chicks_at_beaufort_south": True,
    "known_age_first_breeding_to_beaufort_north": False,
    "proven_natal_origin_of_ross_banded_visitors_to_north": False,
    "northern_beach_census_specific_detection_effort": False,
    "independent_north_nesting_capacity_time_series_pre_choice": False,
    "age_standardized_true_settled_emigrant_probability": False,
    "absolute_eligible_source_recruit_cohorts": False,
    "independent_receiver_reoccupation_events_and_immigrant_origins": False,
}

CLAIMS = {
    "south_to_north_confirmed_first_breeding": [
        "source_origin_tagged_chicks_at_beaufort_south",
        "known_age_first_breeding_to_beaufort_north",
        "northern_beach_census_specific_detection_effort",
    ],
    "ross_to_north_confirmed_first_breeding": [
        "proven_natal_origin_of_ross_banded_visitors_to_north",
        "known_age_first_breeding_to_beaufort_north",
        "northern_beach_census_specific_detection_effort",
    ],
    "newly_exposed_northern_capacity_triggers_colonization": [
        "northern_beach_ice_free_suitability_series_before_1994",
        "verified_north_absence_with_survey_effort_before_1994",
        "georeferenced_aspa_north_1995_and_larue_northeast_2004_identity",
    ],
    "main_colony_saturation_triggers_fission": [
        "local_main_colony_density_at_1995_colonization_timing",
        "known_age_first_breeding_to_beaufort_north",
    ],
    "north_options_reduce_true_interisland_export": [
        "independent_north_nesting_capacity_time_series_pre_choice",
        "age_standardized_true_settled_emigrant_probability",
        "absolute_eligible_source_recruit_cohorts",
    ],
    "beaufort_source_capacity_changes_receiver_reoccupation": [
        "independent_north_nesting_capacity_time_series_pre_choice",
        "age_standardized_true_settled_emigrant_probability",
        "independent_receiver_reoccupation_events_and_immigrant_origins",
    ],
}


def audit() -> dict:
    statuses = {
        claim: {
            "decision": "IDENTIFIABLE_FROM_INSPECTED_METADATA" if all(
                STRUCTURAL_SUPPORT[f] for f in fields
            ) else "HOLD_MISSING_REQUIRED_EVIDENCE",
            "required_fields": fields,
            "missing_fields": [f for f in fields if not STRUCTURAL_SUPPORT[f]],
        }
        for claim, fields in CLAIMS.items()
    }
    return {
        "schema_version": 4,
        "audit_id": "beaufort-origin-and-nesting-option-support-v4",
        "status": "LITERATURE_BASED_STRUCTURAL_AUDIT_NO_NEW_INDIVIDUAL_OUTCOMES",
        "date": "2026-10-08",
        "sources": SOURCES,
        "nodes": NODES,
        "evidence_edges_are_visits_not_breeding": VISITATION_EDGES,
        "structure_only_support": STRUCTURAL_SUPPORT,
        "candidate_claims": statuses,
        "explanation": (
            "The 1995 north settlement occurs during a 1981-2000 "
            "declining trend in the main colony; this weakens a naive "
            "increasing-main-population-fission story, but DOES NOT test "
            "local nesting crowding or prove the founders were immigrants. "
            "The early north coast was already described as ice-free with "
            "subfossil deposits; independent suitability onset dates and "
            "pre-1995 negative surveys are unavailable."
        ),
        "novelty_vetoes": [
            "Single vs multisource seabird colony founding: Munilla et al. 2016",
            "Demographic age-structured immigrant need inferred from abundance: Herman and Lynch 2022",
            "Beaufort chick-banded Ross visitation fraction decline: LaRue et al. 2013",
        ],
        "newly_opened_individual_resight_rows": 0,
        "confirmed_origin_to_north_first_breeding_events_from_inspected_sources": 0,
        "zero_confirmations_means_zero_true_events": False,
        "capacity_causes_network_rewiring": "NOT_TESTED",
        "paper_189_frozen_science_untouched": True,
        "pr_142_locked_protocol_untouched": True,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    result = json.dumps(audit(), indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(result, encoding="utf8")
    print(result, end="")


if __name__ == "__main__":
    main()
