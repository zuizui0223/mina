"""Published mainland coast-vs-hillside structural-control audit for PR #192.

Uses Table 1 from Kim et al. 2026 doi:10.1002/jgo2.70001,
two directly published nest counts and a known 2019 flood. Not an
individual movement assay or an independent island metapopulation replicate.
All outputs descriptive and post-publication.
"""
import argparse
import json

PUBLICATION_DOI = "https://doi.org/10.1002/jgo2.70001"
SCAR_FEATURE = "https://data.aad.gov.au/aadc/gaz/scar/display_name.cfm?gaz_id=139782"
COUNTS = {
    "2017/18": {"coastal": 1971, "higher": 576},
    "2019/20": {"coastal": 1863, "higher": 643},
}


def effective_two_units(a, b):
    n = a + b
    return n * n / (a * a + b * b)


def audit():
    prior, post = COUNTS["2017/18"], COUNTS["2019/20"]
    a, b = prior["coastal"], prior["higher"]
    c, d = post["coastal"], post["higher"]
    n0, n1 = a + b, c + d
    coast_change = c - a
    higher_change = d - b
    return {
        "id": "edmonson-continental-headland-published-nest-reallocation-v1",
        "date": "2026-10-08",
        "study": PUBLICATION_DOI,
        "geography": SCAR_FEATURE,
        "location_class": "continental_antarctic_coastal_headland_not_island",
        "external_2019_event": "wave-driven beach erosion and stranded icebergs February 2019",
        "2017_coastal": a, "2019_coastal": c,
        "2017_higher": b, "2019_higher": d,
        "2017_total": n0, "2019_total": n1,
        "coastal_absolute_change": coast_change,
        "higher_absolute_change": higher_change,
        "total_absolute_change": n1 - n0,
        "coastal_fraction_change": coast_change / a,
        "higher_fraction_change_start_denominator": higher_change / b,
        "higher_fraction_change_published_table": .1042,
        "higher_fraction_change_final_denominator": higher_change / d,
        "total_fraction_change": (n1 - n0) / n0,
        "higher_gain_over_coastal_loss": higher_change / -coast_change,
        "coastal_share_2017": a / n0,
        "coastal_share_2019": c / n1,
        "inverse_simpson_E2_2017": effective_two_units(a, b),
        "inverse_simpson_E2_2019": effective_two_units(c, d),
        "inverse_simpson_E2_relative_change": effective_two_units(c, d) / effective_two_units(a, b) - 1,
        "published_hill_percent_mismatch": abs(higher_change / b - .1042) > .01,
        "published_hill_percent_matches_final_denominator": abs(higher_change / d - .1042) < 0.0001,
        "status": "PUBLISHED_POST_OUTCOME_DESCRIPTIVE_CONTROL_ONLY",
        "inferences": {
            "within_site_count_reallocation_observed": True,
            "same_individuals_moved_coastal_to_hill": "NOT_OBSERVED",
            "cross_island_emigration_effect": "NOT_IDENTIFIED",
            "island_vs_continent_effect": "NOT_IDENTIFIED",
            "independent_nest_geometry_effect_from_published_study": "DESCRIBED_IN_PRIOR_ART",
            "beaufort_source_capacity_rescue_causality": "NOT_TESTED",
        },
        "note": (
            "The 2026 publication itself reports the within-site changes. "
            "Its stated +10.42% for higher ground uses the final-year denominator "
            "67/643, whereas start-year changes on other rows use 2017. "
            "The correct base-2017 higher-ground percent is +11.63%. "
            "The 67 hillside gain is 62% of the 108 coastal loss arithmetically, "
            "not evidence of 67 transferred pairs."
        ),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=str)
    args = p.parse_args()
    text = json.dumps(audit(), indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf8") as f:
            f.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
