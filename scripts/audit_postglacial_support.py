#!/usr/bin/env python3
"""Outcome-blind source-support audit for penguin settlement on newly exposed land.

CSV input contains no colony nest counts. Survey missingness and uncertain land
exposure are never converted to ecological absences or event years.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path

EXPOSURE_FIELDS = {"site_id", "species_id", "patch_id", "landmass_id",
                   "exposure_first_year", "exposure_last_year",
                   "prior_ice_verified", "icefree_verified", "spatial_match", "source_id"}
SURVEY_FIELDS = {"site_id", "species_id", "season", "state", "visited",
                 "effort_verified", "source_id"}
SPECIES = {"ADPE", "CHPE", "GEPE"}


def read_csv(path: str | Path, required: set[str]) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        if not rd.fieldnames or not required.issubset(rd.fieldnames):
            raise ValueError(f"{path}: missing {sorted(required-set(rd.fieldnames or []))}")
        return list(rd)


def yes(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def year(value: str) -> int:
    y = int(value)
    if not 1850 <= y <= 2150:
        raise ValueError("invalid year")
    return y


def audit(exposure: list[dict], survey: list[dict]) -> dict:
    # One unambiguous source-verified habitat patch per site x species.
    mapped: dict[tuple[str, str], dict] = {}
    excluded = defaultdict(int)
    for e in exposure:
        key = (e["site_id"].strip(), e["species_id"].strip())
        if not all(str(e.get(f, "")).strip() for f in ("site_id", "species_id", "patch_id", "landmass_id", "source_id")):
            raise ValueError("blank required exposure identity")
        if key in mapped:
            raise ValueError(f"duplicate/multiple exposure patch assignment for {key}")
        first, last = year(e["exposure_first_year"]), year(e["exposure_last_year"])
        if first > last:
            raise ValueError("exposure interval reversed")
        e = dict(e)
        e["exposure_last_year"] = last
        if key[1] not in SPECIES:
            excluded["outside_target_species"] += 1
        elif not yes(e["prior_ice_verified"]) or not yes(e["icefree_verified"]):
            excluded["no_verified_temporal_land_exposure"] += 1
        elif e["spatial_match"].strip().lower() != "exact":
            excluded["spatial_match_not_exact"] += 1
        else:
            mapped[key] = e

    observations: dict[tuple[str, str], dict[int, str]] = defaultdict(dict)
    for row in survey:
        key = (row["site_id"].strip(), row["species_id"].strip())
        if key not in mapped:
            continue
        if not row["source_id"].strip():
            raise ValueError("blank survey source identity")
        if not yes(row["visited"]) or not yes(row["effort_verified"]):
            excluded["unverified_visit_or_effort"] += 1
            continue
        state = row["state"].strip().upper()
        if state not in {"A", "P"}:
            excluded["missing_or_unknown_state"] += 1
            continue
        season = year(row["season"])
        if season < mapped[key]["exposure_last_year"]:
            excluded["before_confirmed_exposure"] += 1
            continue
        current = observations[key].get(season)
        if current is not None and current != state:
            raise ValueError(f"conflicting A/P observations: {key} {season}")
        observations[key][season] = state

    pairs = defaultdict(int)
    transitions = []
    landmass_by_event = defaultdict(set)
    for key, years in sorted(observations.items()):
        for t, state in sorted(years.items()):
            nxt = years.get(t+1)
            if nxt not in {"A", "P"}:
                continue  # no bridging missing years or NR
            name = state + "_to_" + nxt
            pairs[name] += 1
            if state == "A" and nxt == "P":
                e = mapped[key]
                transitions.append({"site_id":key[0],"species_id":key[1],
                                    "landmass_id":e["landmass_id"],
                                    "from_season":t,"to_season":t+1})
                landmass_by_event[e["landmass_id"]].add(key)

    eligible = {k for k, ys in observations.items() if len(ys) >= 2}
    landmasses = {mapped[k]["landmass_id"] for k in eligible}
    n_ap = pairs["A_to_P"]
    n_risk = pairs["A_to_A"] + n_ap
    # A support threshold, NOT a biological test or power guarantee.
    gates = {"landmasses_ge_5":len(landmasses)>=5,
             "site_species_ge_20":len(eligible)>=20,
             "verified_AP_ge_10":n_ap>=10,
             "AP_landmasses_ge_3":len(landmass_by_event)>=3,
             "A_risk_transitions_ge_30":n_risk>=30}
    return {"status":"source_support_only_no_ecological_effect_fitted",
            "input_exposure_rows":len(exposure), "input_survey_rows":len(survey),
            "verified_exposure_site_species":len(mapped),
            "observed_post_exposure_site_species_ge_2":len(eligible),
            "independent_landmass_labels_with_repeated_visits":len(landmasses),
            "consecutive_pairs":dict(sorted(pairs.items())),
            "A_risk_pairs":n_risk,
            "verified_A_to_P_events":transitions,
            "landmasses_with_A_to_P":len(landmass_by_event),
            "exclusion_counts":dict(sorted(excluded.items())),
            "support_gates":gates,
            "sample_support":"PASS" if all(gates.values()) else "HOLD",
            "warnings":["No record is not A; NR is not A.",
                        "One landmass cannot count as several independent island replicates.",
                        "No models, effects, p-values, or land-expansion causal attributions were estimated."]}


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--exposure-csv",required=True)
    p.add_argument("--survey-csv",required=True)
    p.add_argument("--out-json",required=True)
    a=p.parse_args()
    result=audit(read_csv(a.exposure_csv,EXPOSURE_FIELDS),
                 read_csv(a.survey_csv,SURVEY_FIELDS))
    Path(a.out_json).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out_json).write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps({"sample_support":result["sample_support"],
                      "verified_A_to_P_events":len(result["verified_A_to_P_events"])},sort_keys=True))


if __name__ == "__main__":
    main()
