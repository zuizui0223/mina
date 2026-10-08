#!/usr/bin/env python3
"""Independent published-centroid discordance audit, never penguin migration.

First reference: LaRue et al 2024 original site table pinned at
davidiles/EMPE_Global@13f71112da43c1fd082273677757b41c550457ed
data/colony_attributes.csv (LEDD row).
Second reference: Fretwell et al 2021 Table 2 DOI 10.1002/rse2.176.
No physical ice pixel values are read and no biological outcome is fitted.
"""
import argparse
import csv
import json
import math
from pathlib import Path

FRETWELL = (-74.272, -131.243)
EXPECTED_LARUE = (-74.228, -130.784)
RADII_KM = (1, 3, 5)


def haversine_km(lat1, lon1, lat2, lon2):
    p = math.pi / 180
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    z = math.sin(dlat / 2)**2 + math.cos(lat1*p) * math.cos(lat2*p) * math.sin(dlon/2)**2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(max(0, z))))


def source_row(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as fp:
        allrows = list(csv.DictReader(fp))
    rows = [r for r in allrows if r.get("site_id") == "LEDD"]
    if len(rows) != 1 or rows[0].get("site_name") != "Ledda Bay":
        raise ValueError("Pinned LaRue site roster lacks one unambiguous Ledda record")
    coords = float(rows[0]["lat"]), float(rows[0]["lon"])
    if coords != EXPECTED_LARUE:
        raise ValueError("Frozen LaRue centroid no longer matches exact author site table")
    return coords, len(allrows)


def report(first, second=FRETWELL):
    d = haversine_km(*first, *second)
    return {
        "status": "COORDINATE_DISAGREEMENT_PRE_PHYSICAL_VALUE_CONTEXT",
        "source_1": {"citation": "LaRue et al 2024 author colony_attributes.csv", "coordinates": list(first)},
        "source_2": {"citation": "Fretwell et al 2021 Table 2", "coordinates": list(second)},
        "center_distance_km": d,
        "frozen_radii_km": list(RADII_KM),
        "radii_disjoint_at_both_centroids": {str(r): d > 2*r for r in RADII_KM},
        "both_5km_buffers_cannot_cover_same_physical_patch": d > 10,
        "fixed_fraser_comparators": {"2011_preimage_index":16, "2014_preimage_index":18},
        "permitted_next_operation": "same dates and radii at BOTH coordinates as a separately predeclared sensitivity; do not optimize site locations using ice values",
        "true_colony_movement_confirmed": False,
        "year_specific_nesting_footprints_confirmed": False,
        "external_ice_pixel_values_read": 0,
        "new_penguin_responses_read": 0,
        "new_causal_claim": False,
        "PR189_frozen": True
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--author-csv", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    first, n = source_row(args.author_csv)
    result = report(first)
    result["original_author_colony_roster_rows"] = n
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("LEDD_TWO_PUBLISHED_CENTROIDS_KM", round(result["center_distance_km"], 3))
    print("BOTH_5KM_BUFFERS_DISJOINT", result["both_5km_buffers_cannot_cover_same_physical_patch"])
    print("NO_TRUE_MOVEMENT_OR_CAUSAL_RESULT")


if __name__ == "__main__":
    main()
