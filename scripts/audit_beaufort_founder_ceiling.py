"""Conditional upper-bound audit for a Beaufort north-shore penguin colony.

An official plan reports two breeding pairs, three chicks and 10–15
nonbreeders in *January 1995*, i.e. the 1994/95 breeding season.
The 525-pair observation is the 2005/06 season (start year 2005).

This is arithmetic identifiability and sensitivity, NOT immigration inference.
All reproduction and survival assumptions deliberately maximize local growth.
Does not access mark-resight records.
"""
from __future__ import annotations

import argparse
import json
import math
from typing import Any

SOURCE_ASPA = (
    "https://www.env.go.jp/nature/nankyoku/kankyohogo/database/"
    "jyouyaku/aspa/aspa_pdf_en/Measure5_ASPA105.pdf"
)
SOURCE_KAPPES = "https://doi.org/10.1111/1365-2656.13422"
SOURCE_LARUE = "https://doi.org/10.1371/journal.pone.0060568"
SOURCE_PRIOR_ART = "https://doi.org/10.1093/ornithapp/duac014"

RECORDS = {
    "1994/95": {"season_start": 1994, "pairs": 2,
                "chicks_observed": 3, "nonbreeders_range": [10, 15]},
    "2005/06": {"season_start": 2005, "pairs": 525},
    "2008/09": {"season_start": 2008, "pairs": 677},
    "2013/14": {"season_start": 2013, "pairs": 989},
}


def closed_pairs_upper(
    until_year: int = 2005,
    first_breeding_age: int = 3,
    initial_pairs_1994: float = 2.0,
    observed_chicks_1994: float = 3.0,
    initial_nonbreeders: float = 15.0,
    max_chicks_per_pair: float = 2.0,
    unseen_breeding_pair_equivalents_1995: float = 0.0,
    age2_fraction: float = 0.0,
) -> dict[int, float]:
    """Optimistic closed-population model using breeding-season START years.

    1994/95 (January 1995) has TWO observed breeding pairs, exactly the
    three observed chicks credited as fully fledged. In 1995/96, up to all
    15 initially recorded nonbreeders can join as 7.5 pair-equivalents.
    No previous unobserved cohorts are present under this conditional null.
    All adults persist forever; each pair raises 2 chicks per year,
    every fledged chick survives, mates locally, and breeds at earliest
    permitted age. These half-pair values are arithmetic upper bounds,
    not literal realized whole pairs.

    Age-2 breeding is explicitly counterfactual: Kappes et al. (2021)
    recorded earliest breeding at age 3 for Ross Adélies. Setting a positive
    age2_fraction splits a birth cohort between age 2 and age 3 once each;
    no individual recruits twice.
    """
    scalars = (initial_pairs_1994, observed_chicks_1994, initial_nonbreeders,
               max_chicks_per_pair, unseen_breeding_pair_equivalents_1995)
    if any(not math.isfinite(x) or x < 0 for x in scalars):
        raise ValueError("counts and upper-limit assumptions must be finite nonnegative")
    if first_breeding_age < 2 or until_year < 1994:
        raise ValueError("invalid age or date")
    if not math.isfinite(age2_fraction) or not (0 <= age2_fraction <= 1):
        raise ValueError("age2_fraction must be in [0, 1]")
    if age2_fraction and first_breeding_age != 3:
        raise ValueError("age2 sensitivity is only defined around an age-3 reference")

    pairs = {1994: float(initial_pairs_1994)}
    chicks = {1994: float(observed_chicks_1994)}
    for year in range(1995, until_year + 1):
        continuing = pairs[year - 1]
        if year == 1995:
            continuing += initial_nonbreeders / 2
            continuing += unseen_breeding_pair_equivalents_1995

        if first_breeding_age == 3 and age2_fraction > 0:
            newly_recruited = (
                age2_fraction * chicks.get(year - 2, 0)
                + (1 - age2_fraction) * chicks.get(year - 3, 0)
            ) / 2
        else:
            newly_recruited = chicks.get(year - first_breeding_age, 0) / 2

        pairs[year] = continuing + newly_recruited
        chicks[year] = pairs[year] * max_chicks_per_pair
    return pairs


def unseen_pair_equivalents_needed(target: float, year: int,
                                   first_breeding_age: int = 3) -> float:
    """Equivalent pre-existing pairs missed at 1995, not immigrants inferred."""
    base = closed_pairs_upper(year, first_breeding_age=first_breeding_age)[year]
    one = closed_pairs_upper(
        year, first_breeding_age=first_breeding_age,
        unseen_breeding_pair_equivalents_1995=1
    )[year]
    gain = one - base
    if gain <= 0:
        return float("inf")
    return max(0.0, (target - base) / gain)


def required_counterfactual_age2_fraction(target: float, year: int) -> float | None:
    """Share of chicks unrealistically recruiting at age 2 required to close gap."""
    def f(q):
        return closed_pairs_upper(year, age2_fraction=q)[year]

    if f(0) >= target:
        return 0.0
    if f(1) < target:
        return None
    low, high = 0.0, 1.0
    for _ in range(90):
        middle = (low + high) / 2
        if f(middle) < target:
            low = middle
        else:
            high = middle
    return high


def audit() -> dict[str, Any]:
    optimistic = closed_pairs_upper(until_year=2013)
    maximum_birth_sensitivity = closed_pairs_upper(
        until_year=2005, observed_chicks_1994=4
    )
    age4 = closed_pairs_upper(until_year=2005, first_breeding_age=4)
    initial_founders = unseen_pair_equivalents_needed(525, 2005)
    return {
        "schema_version": 2,
        "audit_id": "beaufort-north-cohort-ceiling-season-aligned-v2",
        "status": "CONDITIONAL_ARITHMETIC_NOT_ESTIMATED_IMMIGRANT_NUMBER",
        "original_season_alignment_error_corrected": (
            "January 1995 = 1994/95; 525 pairs = 2005/06, start year 2005"
        ),
        "sources": {
            "north_shore_records": SOURCE_ASPA,
            "age3_no_age2_observed_ross_study": SOURCE_KAPPES,
            "larue_ne_2004_separate_spatial_crosswalk_required": SOURCE_LARUE,
            "prior_art_age_structured_immigration": SOURCE_PRIOR_ART,
        },
        "observed_north_shore_records": RECORDS,
        "perfect_survival_two_chicks_every_season": True,
        "first_season_pairs": 2,
        "initial_chicks_1994_credited_fledged": 3,
        "max_observed_nonbreeders_credited_as_1995_breeders": 15,
        "max_1995_breeding_pair_equivalents_including_1994_pairs": 9.5,
        "age3_model": {
            "pairs_2004_05": optimistic[2004],
            "pairs_2005_06": optimistic[2005],
            "pairs_2006_07_extra_season": optimistic[2006],
            "observed_2005_06": 525,
            "shortfall_2005_06_pair_equivalents": 525 - optimistic[2005],
            "same_site_2004_05_laRue_count_if_verified": 460,
            "counterfactual_2004_05_shortfall_if_site_matched": 460 - optimistic[2004],
        },
        "sensitivity": {
            "four_initial_chicks_instead_of_three_2005_06":
                maximum_birth_sensitivity[2005],
            "first_breed_age4_2005_06": age4[2005],
            "earliest_1995_unseen_pair_equivalents_needed_for_525":
                initial_founders,
            "ceil_unseen_whole_adults_required_under_perfect_case":
                math.ceil(2 * initial_founders),
            "unseen_founders_are_possible_not_estimated": True,
            "counterfactual_min_age2_recruit_share_to_reach_525_in_2005":
                required_counterfactual_age2_fraction(525, 2005),
            "counterfactual_min_age2_recruit_share_to_reach_525_in_2006":
                required_counterfactual_age2_fraction(525, 2006),
        },
        "falsifiability_and_limitations": [
            "The 1995 visit is NOT a verified exhaustive age/sex census.",
            "Unobserved pre-1995 birth cohorts can recruit after 1995.",
            "Adult movements from Beaufort south colony are within-island, "
            "not evidence of inter-island exchange.",
            "First-time settlers from Ross and other islands are not origin-tagged.",
            "LaRue 2004 northeast and ASPA northwestern labels require spatial "
            "footprint identity audit before merging counts.",
            "The upper bound assumes observed chicks all fledged and all juveniles "
            "and adults survive, which is biologically implausible.",
            "Age-structured immigration inference from abundance is prior art "
            "(Herman and Lynch 2022) and is not newly discovered here.",
        ],
        "decisions": {
            "closed_given_complete_1994_95_roster_and_age3": "CONTRADICTED",
            "actual_external_immigration_necessary": "NOT_IDENTIFIED",
            "within_vs_between_island_origins": "NOT_IDENTIFIED",
            "minimum_immigrants_inferred": False,
            "rescue_effect_in_neighbor_islands_inferred": False,
            "previously_frozen_pr189_unchanged": True,
            "new_individual_outcomes_opened": 0,
        },
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", help="optional report path")
    args = p.parse_args()
    payload = json.dumps(audit(), ensure_ascii=False, indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fp:
            fp.write(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
