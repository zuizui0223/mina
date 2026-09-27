#!/usr/bin/env python3
"""Resolve MAPPPD coastal site points to SCAR ADD v7.12 land polygons."""
from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

SERVICE = (
    "https://services7.arcgis.com/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/"
    "High_resolution_vector_polygons_of_the_Antarctic_coastline/FeatureServer/1/query"
)
TOLERANCES_M = (50, 100, 250, 500, 1000, 2500, 5000)
USER_AGENT = "mina-island-reassembly/0.15 (+https://github.com/zuizui0223/mina)"


def _get(params: dict[str, object], retries: int = 4) -> dict:
    url = SERVICE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if "error" in payload:
                raise RuntimeError(json.dumps(payload["error"], sort_keys=True))
            return payload
        except Exception as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"SCAR query failed: {last!r}")


def query_point(lon: float, lat: float, distance_m: int) -> list[dict[str, object]]:
    params: dict[str, object] = {
        "where": "surface='land'",
        "geometry": f"{lon:.8f},{lat:.8f}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "FID,surface,Shape__Area",
        "returnGeometry": "false",
        "f": "json",
    }
    if distance_m > 0:
        params["distance"] = distance_m
        params["units"] = "esriSRUnit_Meter"
    payload = _get(params)
    return [feature["attributes"] for feature in payload.get("features", [])]


def query_fid(fid: int) -> dict[str, object]:
    payload = _get(
        {
            "where": f"FID={fid}",
            "outFields": "FID,surface,Shape__Area",
            "returnGeometry": "false",
            "f": "json",
        }
    )
    features = payload.get("features", [])
    if len(features) != 1:
        raise RuntimeError(f"FID {fid} returned {len(features)} features")
    return features[0]["attributes"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sites", required=True, type=Path)
    parser.add_argument("--direct-audit", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--meta", required=True, type=Path)
    args = parser.parse_args()

    with args.sites.open(encoding="utf-8-sig", newline="") as handle:
        sites = {row["site_id"]: row for row in csv.DictReader(handle)}
    with args.direct_audit.open(encoding="utf-8-sig", newline="") as handle:
        direct = list(csv.DictReader(handle))

    fid_cache: dict[int, dict[str, object]] = {}
    output = []
    resolution_counts = {"direct_0m": 0, "ambiguous": 0, "unresolved": 0, "query_error": 0}
    for tol in TOLERANCES_M:
        resolution_counts[f"within_{tol}m"] = 0

    for index, row in enumerate(direct, start=1):
        site = sites[row["site_id"]]
        try:
            if row["status"] == "unique_direct_land_match":
                fid = int(float(row["land_fid"]))
                if fid not in fid_cache:
                    fid_cache[fid] = query_fid(fid)
                attr = fid_cache[fid]
                status = "unique_land_match"
                tolerance = 0
                candidates = [attr]
                resolution_counts["direct_0m"] += 1
            else:
                candidates = []
                tolerance = None
                status = "unresolved"
                lat = float(site["latitude"])
                lon = float(site["longitude"])
                for tol in TOLERANCES_M:
                    candidates = query_point(lon, lat, tol)
                    if len(candidates) == 0:
                        continue
                    tolerance = tol
                    if len(candidates) == 1:
                        status = "unique_land_match"
                        resolution_counts[f"within_{tol}m"] += 1
                    else:
                        status = "ambiguous_land_match"
                        resolution_counts["ambiguous"] += 1
                    break
                if len(candidates) == 0:
                    resolution_counts["unresolved"] += 1

            if status == "unique_land_match":
                attr = candidates[0]
                fid = int(attr["FID"])
                area = float(attr["Shape__Area"])
                all_fids = str(fid)
                match_count = 1
            else:
                fid = ""
                area = ""
                all_fids = ";".join(
                    str(int(candidate["FID"])) for candidate in candidates
                )
                match_count = len(candidates)
            error = ""
        except Exception as exc:
            status = "query_error"
            tolerance = None
            fid = ""
            area = ""
            all_fids = ""
            match_count = 0
            error = repr(exc)
            resolution_counts["query_error"] += 1

        output.append(
            {
                "site_id": row["site_id"],
                "site_name": site["site_name"],
                "region": site["region"],
                "latitude": site["latitude"],
                "longitude": site["longitude"],
                "land_fid": fid,
                "land_area_m2": area,
                "assignment_tolerance_m": "" if tolerance is None else tolerance,
                "match_count_at_decision": match_count,
                "candidate_land_fids": all_fids,
                "status": status,
                "error": error,
            }
        )
        if index % 100 == 0:
            print(f"resolved={index}/{len(direct)}")

    unique = [row for row in output if row["status"] == "unique_land_match"]
    mainland_fid = None
    mainland_area = None
    if unique:
        largest = max(unique, key=lambda row: float(row["land_area_m2"]))
        mainland_fid = int(largest["land_fid"])
        mainland_area = float(largest["land_area_m2"])

    for row in output:
        if row["status"] != "unique_land_match":
            row["landmass_class"] = "unresolved"
        elif int(row["land_fid"]) == mainland_fid:
            row["landmass_class"] = "operational_antarctic_mainland"
        else:
            row["landmass_class"] = "island"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)

    meta = {
        "schema_version": 1,
        "tolerances_m": list(TOLERANCES_M),
        "resolution_counts": resolution_counts,
        "n_sites": len(output),
        "n_unique_assigned": sum(row["status"] == "unique_land_match" for row in output),
        "operational_mainland_fid": mainland_fid,
        "operational_mainland_area_m2": mainland_area,
        "n_island_sites": sum(row["landmass_class"] == "island" for row in output),
        "n_mainland_sites": sum(
            row["landmass_class"] == "operational_antarctic_mainland" for row in output
        ),
        "rule": "direct match, else first nonzero frozen tolerance; unique accepts, multiple is ambiguous and stops",
    }
    args.meta.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(meta, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
