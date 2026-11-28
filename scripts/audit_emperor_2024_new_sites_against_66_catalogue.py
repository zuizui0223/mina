"""Reproducible descriptive 4 x 66 old-roster geodesic support audit.

The CSV is an *author-linked published model catalogue*, not a universe of
historically breeding and surveyed penguin colony locations; names may include
relocated or formerly extinct sites. The four 'newly reported' 2024 satellite
locations are published observations, NOT proven first colonizations.

No future response rows, bird movements, 2022 colony extinction statuses,
nest outcome model, or ice-passage measures are loaded.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRETWELL_EVIDENCE = (
    REPO_ROOT / "external/EMPEROR_FRETWELL_2024_SITE_DETECTION_EVIDENCE_V1.json"
)
SOURCE_COMMIT = "8254f7014dd749e5497165ab854b7f76b276e791"
SOURCE_GIT_BLOB_SHA = "ea164db21c3b7c873f425b57e43c745737aafbea"
SOURCE_RAW = (
    "https://raw.githubusercontent.com/bilgecansen/Emperor_dispersal/"
    + SOURCE_COMMIT + "/data/empe_sitesNewNB.csv"
)
EARTH_RADIUS_KM = 6371.0088


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def load_catalogue(raw: bytes, *, strict_full_roster: bool = True) -> list[dict]:
    if strict_full_roster and git_blob_sha(raw) != SOURCE_GIT_BLOB_SHA:
        raise ValueError("AUTHOR_CATALOGUE_GIT_BLOB_SHA_MISMATCH")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    expected = {"site_id", "site_name", "latitude", "longitude"}
    if not expected.issubset(reader.fieldnames or []):
        raise ValueError("required location fields absent")
    locations = []
    for row in reader:
        lat, lon = float(row["latitude"]), float(row["longitude"])
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError("out of range published coordinates")
        id_ = row["site_id"]
        if not id_:
            raise ValueError("blank site id")
        locations.append({
            "id": id_, "name": row["site_name"],
            "lat": lat, "lon": lon,
        })
    if len({x["id"] for x in locations}) != len(locations):
        raise ValueError("duplicate source catalogue identifier")
    if strict_full_roster and len(locations) != 66:
        raise ValueError("expected 66 frozen candidate sites")
    return locations


def haversine_km(lat1, lon1, lat2, lon2):
    vals = [lat1, lon1, lat2, lon2]
    if not all(math.isfinite(v) for v in vals):
        raise ValueError("non-finite coordinates")
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    lat1, lat2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin(dlat/2)**2
         + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2)
    return EARTH_RADIUS_KM*2*math.asin(min(1.0, math.sqrt(max(0., a))))


def audit(
    catalogue: list[dict], published: dict,
    *, expected_catalogue_size: int = 66
) -> dict:
    if len(catalogue) != expected_catalogue_size:
        raise ValueError("catalogue size differs from frozen audit grain")
    four = published["four_newly_reported_sites"]
    if len(four) != 4 or len({x["id"] for x in four}) != 4:
        raise ValueError("2024 four-site published identity changed")
    out = []
    for item in four:
        distances = [
            {
                "existing_catalogue_id": c["id"],
                "existing_catalogue_name": c["name"],
                "geodesic_km": haversine_km(
                    item["lat"], item["lon"], c["lat"], c["lon"]
                ),
            }
            for c in catalogue
        ]
        distances.sort(key=lambda x: (x["geodesic_km"], x["existing_catalogue_id"]))
        out.append({
            "reported_site_id": item["id"],
            "first_published_satellite_positive_year":
                item["first_reported_positive_year"],
            "prior_repeated_surveyed_negative_verified":
                item["repeated_prior_confirmed_absence_at_new_site"],
            "nearest_published_catalogue_site": distances[0],
            "nearest_three_catalogue_sites": distances[:3],
            "nearest_within_100_km": distances[0]["geodesic_km"] <= 100.0,
            "nearest_within_414_km": distances[0]["geodesic_km"] <= 414.0,
            "nearest_site_verified_actively_breeding_same_year": False,
            "nearest_site_current_fast_ice_accessibility_verified": False,
        })
    return {
        "audit": "retrospective_66_published_site_catalogue_vs_4_2024_newly_reported_site_coordinates",
        "source_catalogue_git_sha": SOURCE_COMMIT,
        "source_catalogue_blob_sha": SOURCE_GIT_BLOB_SHA,
        "roster_size": len(catalogue),
        "reported_site_count": len(out),
        "nearest_great_circle_distance_definition":
            "WGS84/geographic-degrees Haversine on 6371.0088km sphere; approximate",
        "new_reported_sites": out,
        "sites_beyond_100km_nearest_catalogue": sum(
            not x["nearest_within_100_km"] for x in out
        ),
        "sites_within_414km_nearest_catalogue": sum(
            x["nearest_within_414_km"] for x in out
        ),
        "sites_with_repeated_surveyed_prenatal_zero": sum(
            x["prior_repeated_surveyed_negative_verified"] for x in out
        ),
        "inferred_mean_dispersal_414km_is_not_maximum": True,
        "fixed_catalogue_not_proven_historically_synchronous": True,
        "not_evidence_of_initial_colonization_or_actual_migration": True,
        "not_proof_of_social_attraction_or_ice_access": True,
        "new_external_penguin_response_rows_opened": 0,
        "new_causal_hypothesis_tested": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalogue-csv", type=Path, help="Offline pinned CSV")
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    if args.catalogue_csv:
        raw = args.catalogue_csv.read_bytes()
    else:
        req = urllib.request.Request(
            SOURCE_RAW, headers={"User-Agent": "mina-public-geodesic-audit"}
        )
        with urllib.request.urlopen(req, timeout=40) as handle:
            raw = handle.read(50000)
    names = load_catalogue(raw)
    source = json.loads(FRETWELL_EVIDENCE.read_text(encoding="utf-8"))
    result = audit(names, source)
    data = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(data, encoding="utf-8")
    print(data, end="")


if __name__ == "__main__":
    main()
