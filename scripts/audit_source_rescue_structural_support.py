"""Source-retention feasibility audit of published Beaufort and frozen Ross counts.

No USAP-DC individual files or previously-unopened outcomes are accessed.
This audit tests panel eligibility, NOT the causal source-retention hypothesis.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

BEAUFORT_TABLE1 = {
    1958: (75670.3, None),
    1983: (107571.2, 34588),
    1993: (104637.3, None),
    2005: (127603.4, 52335),
    2010: (129029.5, 63760),
}
ROSS_COLS = (
    "Cape Royds", "Cape Bird South", "Cape Bird Middle", "Cape Bird North",
    "Cape Crozier West", "Cape Crozier East",
)


def published_beaufort():
    a05, b05 = BEAUFORT_TABLE1[2005]
    a10, b10 = BEAUFORT_TABLE1[2010]
    a83, _ = BEAUFORT_TABLE1[1983]
    return {
        "main_area_1983_to_2005_change": a05 / a83 - 1,
        "main_area_2005_to_2010_change": a10 / a05 - 1,
        "main_area_m2_gain_2005_to_2010": a10 - a05,
        "main_breeding_pairs_2005_to_2010_change": b10 / b05 - 1,
        "main_density_2005": b05 / a05,
        "main_density_2010": b10 / a10,
        "main_density_change": (b10 / a10) / (b05 / a05) - 1,
        "if_eligible_cohort_grew_like_pairs_probability_ratio_must_be_less_than": b05 / b10,
        "warning": "Published main-colony guano-envelope area and paired breeding counts only; cohort assumption hypothetical.",
    }


def audit_frozen_ross(csv_path: str | Path):
    path = Path(csv_path)
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ["year", *ROSS_COLS], "Unexpected published Ross roster/schema"
        rows = list(reader)
    assert len(rows) == len({int(r["year"]) for r in rows}), "Duplicate census years"
    assert rows, "No Ross counts"
    six = [[int(r[c]) for c in ROSS_COLS] for r in rows]
    if any(v < 0 for r in six for v in r):
        raise ValueError("negative counts in frozen Ross CSV")
    three = [[r[0], sum(r[1:4]), sum(r[4:6])] for r in six]
    ordered_years = sorted(int(r["year"]) for r in rows)
    if ordered_years != [int(r["year"]) for r in rows]:
        raise ValueError("years out of order")

    def reoccupation(mat):
        return sum(
            int(prev[i] == 0 and nxt[i] > 0)
            for prev, nxt in zip(mat[:-1], mat[1:])
            for i in range(len(prev))
        )

    return {
        "observed_years": len(rows),
        "start_year": ordered_years[0], "end_year": ordered_years[-1],
        "colony_years": len(rows) * 3,
        "positive_colony_years": sum(n > 0 for r in three for n in r),
        "zero_colony_years": sum(n == 0 for r in three for n in r),
        "six_component_years": len(rows) * 6,
        "positive_six_component_years": sum(n > 0 for r in six for n in r),
        "colony_zero_to_positive_observed_transitions": reoccupation(three),
        "six_component_zero_to_positive_observed_transitions": reoccupation(six),
        "min_colony_pairs": dict(zip(("Royds", "Bird", "Crozier"),
                                     (min(r[i] for r in three) for i in range(3)))),
        "note": "Only observed census transitions; missing calendar years do not certify absence.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ross-csv", help="Previously frozen 26-year CSV from PR #189; optional")
    parser.add_argument("--out", type=Path, help="Optional JSON output destination")
    args = parser.parse_args()
    report = {
        "kind": "previously_published_and_previously_exposed_structural_support_only",
        "source": "LaRue et al 2013 PLOS ONE Table 1",
        "beaufort": published_beaufort(),
        "no_new_individual_records_opened": True,
        "causal_export_or_rescue_estimated": False,
    }
    if args.ross_csv:
        report["ross"] = audit_frozen_ross(args.ross_csv)
        report["recipient_reoccupation_gate"] = (
            "FAIL_NO_EVENTS" if report["ross"]["colony_zero_to_positive_observed_transitions"] == 0
            else "EVENTS_PRESENT_NOT_CAUSAL_IDENTIFICATION"
        )
    else:
        report["recipient_reoccupation_gate"] = "NOT_EVALUATED_REQUIRES_FROZEN_ROSS_CSV"
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
