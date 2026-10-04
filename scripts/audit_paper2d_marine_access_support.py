#!/usr/bin/env python3
"""Outcome-blind archive-support audit for Paper 2D marine accessibility."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
from pathlib import Path

import pandas as pd
import requests

BASE = "https://noaadata.apps.nsidc.org/NOAA/G02135/south/monthly/geotiff"
MONTHS = {1: "01_Jan", 11: "11_Nov", 12: "12_Dec"}
VERSION = "v4.0"
TIMEOUT = 30


def file_url(year: int, month: int) -> str:
    label = MONTHS[int(month)]
    return (
        f"{BASE}/{label}/"
        f"S_{int(year):04d}{int(month):02d}_concentration_{VERSION}.tif"
    )


def required_year_months(units: pd.DataFrame) -> set[tuple[int, int]]:
    cols = {
        "early_window_start", "early_window_end",
        "late_window_start", "late_window_end",
    }
    missing = cols - set(units.columns)
    if missing:
        raise ValueError(f"optical catalog missing {sorted(missing)}")
    out: set[tuple[int, int]] = set()
    for row in units.itertuples(index=False):
        for prefix in ("early", "late"):
            start = int(getattr(row, f"{prefix}_window_start"))
            end = int(getattr(row, f"{prefix}_window_end"))
            for year in range(start, end + 1):
                for month in MONTHS:
                    out.add((year, month))
    return out


def probe(url: str) -> dict:
    try:
        r = requests.get(
            url,
            headers={"Range": "bytes=0-1023", "User-Agent": "mina-paper2d-marine-support/1.0"},
            timeout=TIMEOUT,
        )
        ok = r.status_code in {200, 206} and len(r.content) > 0
        return {
            "url": url,
            "status_code": int(r.status_code),
            "bytes_received": int(len(r.content)),
            "ok": bool(ok),
            "error": None,
        }
    except Exception as exc:
        return {
            "url": url,
            "status_code": None,
            "bytes_received": 0,
            "ok": False,
            "error": repr(exc),
        }


def unit_support(units: pd.DataFrame, probes: dict[tuple[int, int], dict]) -> pd.DataFrame:
    rows = []
    for row in units.itertuples(index=False):
        out = row._asdict()
        epoch_ok = {}
        for prefix in ("early", "late"):
            start = int(getattr(row, f"{prefix}_window_start"))
            end = int(getattr(row, f"{prefix}_window_end"))
            ym = [(year, month) for year in range(start, end + 1) for month in MONTHS]
            ok = sum(bool(probes[p]["ok"]) for p in ym)
            complete_years = sum(
                all(probes[(year, month)]["ok"] for month in MONTHS)
                for year in range(start, end + 1)
            )
            frac = ok / len(ym) if ym else 0.0
            out[f"{prefix}_marine_required_months"] = len(ym)
            out[f"{prefix}_marine_available_months"] = ok
            out[f"{prefix}_marine_available_fraction"] = frac
            out[f"{prefix}_marine_complete_years"] = complete_years
            epoch_ok[prefix] = frac >= 0.90 and complete_years >= 3
        out["marine_archive_support"] = bool(epoch_ok["early"] and epoch_ok["late"])
        rows.append(out)
    return pd.DataFrame(rows)


def audit(optical_csv: Path, workers: int = 12):
    units = pd.read_csv(optical_csv)
    if len(units) != 107:
        raise ValueError(f"frozen optical unit roster drift: {len(units)} != 107")
    forbidden = {"count", "abundance", "trend", "kappa", "delta_kappa", "n_eff"}
    present = forbidden.intersection({c.lower() for c in units.columns})
    if present:
        raise ValueError(f"forbidden demographic fields present: {sorted(present)}")

    required = sorted(required_year_months(units))
    results: dict[tuple[int, int], dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {
            pool.submit(probe, file_url(year, month)): (year, month)
            for year, month in required
        }
        for fut in concurrent.futures.as_completed(futs):
            results[futs[fut]] = fut.result()

    supported = unit_support(units, results)
    failed_files = [
        {"year": y, "month": m, **results[(y, m)]}
        for y, m in required if not results[(y, m)]["ok"]
    ]
    supported_n = int(supported["marine_archive_support"].sum())
    result = {
        "schema_version": 1,
        "result_id": "mina-paper2d-marine-access-support-v1",
        "dataset": {
            "id": "G02135",
            "version": 4,
            "doi": "10.7265/a98x-0f50",
            "product": "south monthly concentration GeoTIFF",
            "months": sorted(MONTHS),
        },
        "archive": {
            "unique_year_month_files_required": len(required),
            "available_files": len(required) - len(failed_files),
            "failed_files": failed_files,
        },
        "units": {
            "candidate": int(len(supported)),
            "supported": supported_n,
            "supported_fraction": supported_n / len(supported),
            "species_supported": {
                str(sp): int(g["marine_archive_support"].sum())
                for sp, g in supported.groupby("species_id")
            },
            "regions_with_supported_units": int(
                supported.loc[supported["marine_archive_support"], "region"].nunique()
            ),
        },
        "decision": {
            "archive_support_gate_passed": bool(
                supported_n / len(supported) >= 0.80
                and supported.loc[supported["marine_archive_support"], "species_id"].nunique() >= 2
                and supported.loc[supported["marine_archive_support"], "region"].nunique() >= 2
            ),
            "demographic_magnitudes_opened": False,
            "marine_values_computed": False,
        },
        "boundary": [
            "This audit tests public archive availability only.",
            "It does not compute sea-ice distance or use penguin count magnitudes.",
        ],
    }
    probe_frame = pd.DataFrame([
        {"year": y, "month": m, **results[(y, m)]}
        for y, m in required
    ]).sort_values(["year", "month"])
    return result, supported, probe_frame


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--optical-csv", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-units-csv", required=True, type=Path)
    p.add_argument("--out-files-csv", required=True, type=Path)
    args = p.parse_args()
    result, units, files = audit(args.optical_csv)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    units.to_csv(args.out_units_csv, index=False)
    files.to_csv(args.out_files_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
