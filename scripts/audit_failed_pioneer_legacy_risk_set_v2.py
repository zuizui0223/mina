#!/usr/bin/env python3
"""Can public Cox-2024 lone nest data distinguish physical legacies after FAILED
nesting from successful public information and static habitat preferences?

Strict structural support and source taxonomy only: does NOT inspect 2022
outcomes or estimate an ecological effect. No counterfactual unsampled patches
are manufactured. Full identity via Git blob SHA for both original CSV files.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
from io import StringIO
import json
from pathlib import Path

SOURCE_GIT_BLOBS = {
    "locations": "9e2dbe1426e47d6cf2dfc84110e8204c7ba92329",
    "outcomes": "a21648a25b12f42759ca5d5bd011ec32c36d3dfc",
}
SOURCE_COMMIT = "04517cedac18950408abd4d0b510f4aae3447f05"


def verified_source(path, expected_blob):
    b = Path(path).read_bytes()
    git_hash = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if git_hash != expected_blob:
        raise ValueError("Frozen public author source blob mismatch")
    try:
        t = b.decode("utf-8-sig")
    except UnicodeDecodeError:
        t = b.decode("cp1252")
    return list(csv.DictReader(StringIO(t)))


def nest_id(v):
    s = str(v or "").strip().lower()
    if s.startswith("solo") and s[4:].isdigit():
        return int(s[4:])
    return None


def coverage(locations, outcomes, strict=True):
    sites = {}
    for row in locations:
        k = nest_id(row.get("nestid"))
        if k is None or k in sites:
            raise ValueError("Missing, duplicate or unexpected original GPS site ID")
        lat = float(row["latitude"])
        lon = float(row["longitude"])
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError("Invalid GPS coordinates")
        sites[k] = (lat, lon)

    result_outcomes = {}
    n_footer = 0
    for row in outcomes:
        k = nest_id(row.get("nestid"))
        if k is None:
            n_footer += 1
            continue
        if k in result_outcomes:
            raise ValueError("Duplicate outcome nest")
        result_outcomes[k] = row
    if set(sites) != set(result_outcomes):
        raise ValueError("Can't join GPS to 2021 outcome exact nest ID")
    if strict and (len(sites) != 50 or set(sites) != set(range(1, 51)) or n_footer != 3):
        raise ValueError("Original 50 monitored solitary nest source changed")

    code = Counter(str(row["breeder"]).strip() for row in result_outcomes.values())
    if set(code) != {"0", "1"}:
        raise ValueError("Original breeder code outside the known 0/1 source schema")
    direct_cr = Counter()
    for row in result_outcomes.values():
        s = str(row.get("cr_confirm","")).strip().lower()
        b = str(row["breeder"]).strip()
        if b == "0" and s not in ("","na","nan"):
            raise ValueError("Nonbreeder with unexpected direct crèche output")
        if s not in ("","na","nan"):
            n = float(s)
            if n < 0 or n > 2 or int(n) != n:
                raise ValueError("Invalid direct crèche observation count")
            if b == "1":
                direct_cr["confirmed_positive" if n > 0 else "not_confirmed"] += 1
        elif b == "1":
            direct_cr["missing_crèche_code"] += 1
    if strict and (code["1"],code["0"]) != (37,13):
        raise ValueError("Source 2021 breeder roster counts changed")

    return {
        "status": "SOURCE_STRUCTURAL_RISK_SET_AUDIT_NO_H1_CAUSAL_SUPPORT",
        "public_author_release_commit": SOURCE_COMMIT,
        "source_original_nest_site_count": len(sites),
        "source_nest_location_outcome_identical_ids": len(sites),
        "source_outcome_nonbiological_footer_rows": n_footer,
        "source_breeder_codes": dict(code),
        "source_crèche_direct_observation_codes_in_breeders": dict(direct_cr),
        "sites_with_confirmed_original_positive_nest_identification": len(sites),
        "independently_sampled_physically_available_never_used_patches": 0,
        "independently_sampled_never_used_patches_are_absent_from_source": True,
        "nonbreeder_zero_is_not_failed_egg_laying_attempt": True,
        "absence_of_crèche_confirmation_not_verified_failure": True,
        "matched_failed_vs_never_used_risk_set_constructible": False,
        "prior_nest_legacy_exposure_independent_of_site_quality": False,
        "H1_failed_pioneer_vs_H3_static_habitat_identifiable": False,
        "genuine_2022_first_breeder_origin_source_available_here": False,
        "no_2022_or_later_penguin_outcome_rows_opened": True,
        "causal_effect_or_new_novel_mechanism_fitted": False,
        "frozen_Ecology_PR189_changed": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--locations",type=Path,required=True)
    ap.add_argument("--outcomes",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args = ap.parse_args()
    z = coverage(
        verified_source(args.locations,SOURCE_GIT_BLOBS["locations"]),
        verified_source(args.outcomes,SOURCE_GIT_BLOBS["outcomes"]),
    )
    args.out.write_text(json.dumps(z,indent=2)+"\n",encoding="utf8")
    print("FAILED_PIONEER_SOURCE",z["status"])
    print("ORIGINAL_SITE_N",z["source_original_nest_site_count"])
    print("ORIGINAL_BREEDING",z["source_breeder_codes"])
    print("CR_CODES",z["source_crèche_direct_observation_codes_in_breeders"])
    print("NEVER_USED_INDEPENDENT_PATCH_N",z["independently_sampled_physically_available_never_used_patches"])
    print("UNSUCCESSFUL_PHYSICAL_LEGACY_CAUSAL_EFFECT",False)


if __name__ == "__main__":
    main()
