"""Source-only ERA5 2m-air-temperature exposure for 40 frozen MAPPPD sites.

The script is frozen before fetching temperature outcome values. No ecological
response model, statistical significance or anthropogenic attribution is fit.
Open-Meteo explicitly selects ERA5 (never the time-spliced "best_match").
"""
from __future__ import annotations

import argparse
import calendar
import csv
import datetime as dt
import gzip
import hashlib
import json
import math
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs/climate_penguin/daily_ice_locations.csv"
API = "https://archive-api.open-meteo.com/v1/archive"
FIRST, LAST = 1991, 2020
MODEL = "era5"
VAR = "temperature_2m_mean"
SELECTED = [8, 9, 10, 11]
HEADERS = {"User-Agent": "mina-penguin-macroclimate-source/1.0 (research-data-audit)"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_sites():
    with SOURCE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    selected = sorted((r for r in rows if r["cohort"] == "macro_40"), key=lambda r: r["location_id"])
    assert len(selected) == len({r["site_id"] for r in selected}) == 40
    assert len({r["location_id"] for r in selected}) == 40
    return selected


def monthly_series(dates, values):
    assert len(dates) == len(values)
    assert len(set(dates)) == len(dates)
    assert dates[0] == "1991-01-01" and dates[-1] == "2020-12-31"
    assert len(dates) == (dt.date(2020, 12, 31) - dt.date(1991, 1, 1)).days + 1
    accum = defaultdict(list)
    for stamp, x in zip(dates, values):
        yy, mm, dd = (int(v) for v in stamp.split("-"))
        assert FIRST <= yy <= LAST and 1 <= mm <= 12
        if x is not None:
            value = float(x)
            assert math.isfinite(value) and -100 <= value <= 50
            accum[yy, mm].append(value)
    rows = []
    for y in range(FIRST, LAST + 1):
        for m in range(1, 13):
            vals = accum[y, m]
            expected = calendar.monthrange(y, m)[1]
            ok = len(vals) / expected >= .95
            rows.append({
                "year": y, "month": m, "expected_days": expected,
                "valid_days": len(vals), "complete_month": ok,
                "air2m_mean_c": round(statistics.mean(vals), 6) if ok else None,
            })
    return rows


def slope_by_year(pairs):
    if len(pairs) < 2:
        return None
    mx = statistics.mean(x for x, _ in pairs)
    my = statistics.mean(y for _, y in pairs)
    den = sum((x - mx)**2 for x, _ in pairs)
    if den == 0:
        return None
    return sum((x - mx)*(y - my) for x, y in pairs)/den * 10


def fetch_batch(batch, attempts=3):
    params = {
        "latitude": ",".join(str(r["latitude"]) for r in batch),
        "longitude": ",".join(str(r["longitude"]) for r in batch),
        "start_date": f"{FIRST}-01-01",
        "end_date": f"{LAST}-12-31",
        "daily": VAR,
        "models": MODEL,
        "timezone": "UTC",
        "temperature_unit": "celsius",
        "elevation": "nan",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    last_error = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=120) as response:
                assert response.status == 200
                raw = response.read()
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, list):
                payload = [payload]
            if len(payload) != len(batch):
                raise RuntimeError(f"Expected {len(batch)} location payloads, got {len(payload)}")
            if any("daily" not in item for item in payload):
                raise RuntimeError("Source did not return required ERA5 daily payload")
            return url, raw, payload
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, ValueError, RuntimeError) as ex:
            last_error = ex
            if attempt < attempts - 1:
                print(f"Retrying after source download error: {type(ex).__name__} {str(ex)[:150]}", flush=True)
                time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"ERA5 fetch source gate failed: {last_error}")


def write_csv(path, rows):
    if not rows:
        raise ValueError("No rows to save")
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", choices=["pilot", "full"], default="pilot")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    sites = read_sites()
    if args.mode == "pilot":
        # Chosen by fixed pre-download coastal geographical coverage, not effect sizes.
        selected_ids = ("ADAR", "ARDL", "BECH")
        sites = [r for r in sites if r["site_id"] in selected_ids]
        assert len(sites) == 3
    source_sha = sha256(SOURCE.read_bytes())
    raw_receipts, monthly, annual, trends, grids = [], [], [], [], []
    for at in range(0, len(sites), 5):
        batch = sites[at:at + 5]
        url, raw, objs = fetch_batch(batch)
        batch_hash = sha256(raw)
        archive = args.output / f"raw_era5_batch_{at // 5:02d}.json.gz"
        with gzip.open(archive, "wb") as f:
            f.write(raw)
        raw_receipts.append({
            "request_number": at // 5, "source_sha256": batch_hash,
            "uncompressed_bytes": len(raw), "batch_site_ids": [z["site_id"] for z in batch],
            "query_url": url, "output": archive.name,
        })
        for site, item in zip(batch, objs):
            assert item.get("timezone") in {"GMT", "UTC"}
            assert item.get("utc_offset_seconds") == 0
            assert item.get("daily_units", {}).get(VAR) in {"°C", "C"}
            source_daily = item["daily"]
            points = monthly_series(source_daily["time"], source_daily[VAR])
            coords = {
                "site_id": site["site_id"],
                "location_id": site["location_id"],
                "requested_latitude": float(site["latitude"]),
                "requested_longitude": float(site["longitude"]),
                "returned_grid_latitude": item.get("latitude"),
                "returned_grid_longitude": item.get("longitude"),
                "returned_grid_elevation": item.get("elevation"),
                "source_batch": at // 5,
            }
            grids.append(coords)
            for p in points:
                monthly.append({**coords, **p})
            for y in range(FIRST, LAST + 1):
                a = [p for p in points if p["year"] == y]
                for window, months in [("full_year", list(range(1, 13))), ("aug_nov", SELECTED)]:
                    b = [p for p in a if p["month"] in months]
                    complete = all(p["complete_month"] for p in b)
                    annual.append({
                        "site_id": site["site_id"], "location_id": site["location_id"],
                        "year": y, "window": window, "complete_window": complete,
                        "air2m_mean_c": round(statistics.mean(p["air2m_mean_c"] for p in b), 6) if complete else None,
                        "note": "Equal-month mean; not daily-duration weighted, no warming attribution.",
                    })
            for window, months in [("full_year", list(range(1, 13))), ("aug_nov", SELECTED), *[(f"month_{m}", [m]) for m in SELECTED]]:
                for lo, hi, minimum in [(1991, 2020, 25), (2011, 2020, 8)]:
                    selected = []
                    for y in range(lo, hi + 1):
                        records = [p for p in points if p["year"] == y and p["month"] in months]
                        if len(records) != len(months) or not all(p["complete_month"] for p in records):
                            continue
                        selected.append((y, statistics.mean(p["air2m_mean_c"] for p in records)))
                    trends.append({
                        "site_id": site["site_id"], "location_id": site["location_id"],
                        "window": window, "start_year": lo, "end_year": hi,
                        "n_complete_years": len(selected),
                        "minimum_years": minimum,
                        "slope_c_per_decade": round(slope_by_year(selected), 8) if len(selected) >= minimum else None,
                        "status": "descriptive_only" if len(selected) >= minimum else "incomplete_support",
                    })
        print(f"ERA5 source batch {1 + at // 5}, sites={len(batch)}, bytes={len(raw)}, sha256={batch_hash}", flush=True)
        time.sleep(1)

    write_csv(args.output / "era5_grid_support.csv", grids)
    write_csv(args.output / "era5_monthly_1991_2020.csv", monthly)
    write_csv(args.output / "era5_year_windows_1991_2020.csv", annual)
    write_csv(args.output / "era5_site_trends_v1.csv", trends)
    results = {}
    for window in ("full_year", "aug_nov", *(f"month_{m}" for m in SELECTED)):
        eligible = [t for t in trends if t["window"] == window and t["start_year"] == 1991 and t["slope_c_per_decade"] is not None]
        vals = [t["slope_c_per_decade"] for t in eligible]
        results[window] = {
            "n_sites": len(vals),
            "positive": sum(v > 0 for v in vals),
            "negative": sum(v < 0 for v in vals),
            "median_c_per_decade": round(statistics.median(vals), 7) if vals else None,
            "mean_c_per_decade": round(statistics.mean(vals), 7) if vals else None,
        }
    receipt = {
        "schema": 1, "status": "source_only_not_attribution",
        "mode": args.mode,
        "dataset": "Open-Meteo Historical Weather API, ERA5 2m mean air temperature",
        "model": MODEL, "source": API, "start_date": "1991-01-01", "end_date": "2020-12-31",
        "source_sites_sha256": source_sha, "sites": len(sites),
        "independent_grid_count": len({(g["returned_grid_latitude"], g["returned_grid_longitude"]) for g in grids}),
        "n_monthly_rows": len(monthly), "n_year_window_rows": len(annual),
        "source_receipts": raw_receipts,
        "trend_descriptive": results,
        "not_measured": ["field_observed_air_temperature", "climate_change_attribution", "breeding_response", "ecological_causality"],
    }
    (args.output / "era5_warming_source_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("ERA5_WARMING_SOURCE_RECEIPT=" + json.dumps({
        "status": receipt["status"], "sites": receipt["sites"], "grid_count": receipt["independent_grid_count"],
        "trend_descriptive": results,
    }, ensure_ascii=False), flush=True)
    if any(v["n_sites"] != len(sites) for v in results.values()):
        raise RuntimeError("Strict 25-year support gate failed; inspect uploaded source artifacts.")


if __name__ == "__main__":
    main()
