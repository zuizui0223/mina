"""Upper bound on closed growth of Beaufort north-shore Adélie breeding pairs.

All inputs are published aggregate historical records or explicit sensitivity
assumptions. No individual encounter records, fitted survival or causal effects.
"""
from __future__ import annotations
import argparse
import json
from typing import Any

OBSERVED_ASPA105 = {
    "1995": {"pairs": 2, "nonbreeders_min": 10, "nonbreeders_max": 15, "chicks": 3},
    "2005/06": {"pairs": 525, "season_start": 2005, "season_end": 2006},
    "2008/09": {"pairs": 677, "season_start": 2008, "season_end": 2009},
    "2013/14": {"pairs": 989, "season_start": 2013, "season_end": 2014},
}
SOURCE_ASPA = "https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/aspa/aspa_pdf_en/Measure5_ASPA105.pdf"
SOURCE_KAPPES = "https://doi.org/10.1111/1365-2656.13422"
SOURCE_SCHMIDT = "https://doi.org/10.1038/s41598-021-94861-7"

def closed_pairs_upper(
    start_year: int = 1995, initial_pairs: float = 2.0,
    initial_unpaired_nonbreeders: float = 15.0,
    min_breeding_age: int = 3, max_chicks_per_pair: float = 2.0,
    until_year: int = 2014, age2_recruit_fraction: float = 0.0,
) -> dict[int, float]:
    """Max possible local pair counts under an *exhaustive* founder inventory.

    The 1995 15 nonbreeders are immediately converted into 7.5 pair equivalents
    AND all are allowed to lay and fledge 2 chicks already that season.
    Every adult and chick survives; each season retains all breeders; chicks
    acquire a local mate and first breed at the minimum age. This is therefore
    an intentionally excessive upper bound, not a population fit.

    age2_recruit_fraction is a deliberately counterfactual sensitivity only when
    min_breeding_age==3; Ross historical known-age records did not observe
    successful breeding before age 3.
    """
    if min_breeding_age < 2 or max_chicks_per_pair < 0 or until_year < start_year:
        raise ValueError("invalid demographic assumptions")
    if initial_pairs < 0 or initial_unpaired_nonbreeders < 0:
        raise ValueError("negative initial census")
    if not (0 <= age2_recruit_fraction <= 1):
        raise ValueError("age2 fraction out of [0,1]")
    if age2_recruit_fraction and min_breeding_age != 3:
        raise ValueError("age2 sensitivity only with age3 reference")
    f = float(max_chicks_per_pair) / 2.0
    initial_equiv = float(initial_pairs) + float(initial_unpaired_nonbreeders) / 2.0
    years = range(start_year, until_year + 1)
    n = {start_year: initial_equiv}
    for y in list(years)[1:]:
        incoming = 0.0
        if y - min_breeding_age in n:
            incoming += f * (1-age2_recruit_fraction) * n[y-min_breeding_age]
        if age2_recruit_fraction and y-2 in n:
            incoming += f * age2_recruit_fraction * n[y-2]
        n[y] = n[y-1] + incoming
    return n

def age2_fraction_required(target: float, end_year: int) -> float | None:
    """Smallest age-2 breeder share under all-other-perfection assumptions."""
    lo, hi = 0., 1.
    if closed_pairs_upper(until_year=end_year, age2_recruit_fraction=0)[end_year] >= target:
        return 0.
    if closed_pairs_upper(until_year=end_year, age2_recruit_fraction=1)[end_year] < target:
        return None
    for _ in range(100):
        mid = (lo+hi)/2
        n = closed_pairs_upper(until_year=end_year, age2_recruit_fraction=mid)[end_year]
        if n < target:
            lo = mid
        else:
            hi = mid
    return hi

def audit() -> dict[str, Any]:
    y2005, y2006 = (closed_pairs_upper(until_year=y)[y] for y in (2005, 2006))
    return {
       "audit_id": "beaufort-aspa105-closed-founder-max-demography-v1",
       "status": "conditional_arithmetic_bound_on_published_history_not_movement_identification",
       "source": SOURCE_ASPA,
       "age_first_breeding_support": SOURCE_KAPPES,
       "maximum_two_eggs_source": SOURCE_SCHMIDT,
       "source_site": "Beaufort north-shore site in the 2015 ASPA 105 plan ONLY",
       "published_records": OBSERVED_ASPA105,
       "generous_start_1995_breeding_pair_equivalents": 9.5,
       "assumptions": [
           "1995 two breeding pairs plus ALL fifteen observed nonbreeders exhaust founder inventory",
           "fifteen nonbreeders are paired and productive already in 1995",
           "every pair raises two chicks annually; perfect survival of chicks and adults",
           "all chicks find local mates and first breed at age three",
           "no emigrants, skipped breeding, competition, predation or spatial restriction",
           "no immigrant additions AND no previously born but uncounted future local recruits",
       ],
       "max_closed_pairs_2004_age3": closed_pairs_upper(until_year=2004)[2004],
       "max_closed_pairs_2005_age3": y2005,
       "max_closed_pairs_2006_age3": y2006,
       "observed_pairs_2005_06": 525,
       "closed_founder_ceiling_below_2005_06_even_if_assigned_to_2006": y2006 < 525,
       "gap_pairs_relative_to_age3_ceiling_if_2006": 525-y2006,
       "all_first_breed_age2_sensitivity_upper_2006": closed_pairs_upper(
           until_year=2006,min_breeding_age=2)[2006],
       "counterfactual_min_age2_share_to_reach_525_by_2006":
           age2_fraction_required(525,2006),
       "alternative_explanations": [
           "immigrants from established Beaufort main colony (within island)",
           "immigrants from Ross or other colonies (between islands)",
           "unobserved founding adults, pre-1995 born cohorts, or incomplete 1995 census",
           "nonmatching historic site/census definitions or season assignment",
           "breeding below age three, not observed in the historical Ross age study",
       ],
       "decision": {
           "strict_closed_known_1995_founder_model_age3": "FALSIFIED_CONDITIONALLY",
           "external_origin_proven": False,
           "within_versus_between_island_origins_identified": False,
           "source_rescue_consequence_identified": False,
           "new_individual_level_outcomes_opened": 0
       },
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",help="optional output JSON filename")
    args=parser.parse_args()
    result=json.dumps(audit(),indent=2,ensure_ascii=False)+"\n"
    if args.out:
        with open(args.out,"w",encoding="utf8") as f: f.write(result)
    print(result,end="")

if __name__=="__main__":
    main()
