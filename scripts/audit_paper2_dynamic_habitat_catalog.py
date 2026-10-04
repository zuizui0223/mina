#!/usr/bin/env python3
"""Outcome-blind optical-catalog support audit for Antarctic island-ecology Paper 2.

This script reads only the already-frozen support/atlas artifacts. It never reads
penguin count magnitudes or any derived demographic outcome.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


EARTH_SEARCH = "https://earth-search.aws.element84.com/v1/search"
LANDSAT_COLLECTION = "landsat-c2-l2"
SENTINEL_COLLECTION = "sentinel-2-l2a"
OPTICAL_MONTHS = {10, 11, 12, 1, 2, 3}
EXPECTED_UNITS = 107
EXPECTED_SITES = 88
MIN_DATES = 3
MIN_SEASONS = 2


@dataclass(frozen=True)
class Window:
    name: str
    collection: str
    start: str
    end: str


WINDOWS = (
    Window("early_landsat", LANDSAT_COLLECTION, "1984-01-01", "1994-12-31"),
    Window("late_landsat", LANDSAT_COLLECTION, "2018-01-01", "2025-12-31"),
    Window("sentinel2_validation", SENTINEL_COLLECTION, "2018-01-01", "2025-12-31"),
)


def austral_season(dt: datetime) -> int:
    """Return ending-year label for an austral July-June season."""
    return dt.year + 1 if dt.month >= 7 else dt.year


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _safe_float(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def summarize_features(features: Iterable[dict]) -> dict:
    """Summarize catalog features after frozen austral optical-season filtering."""
    kept = []
    seen_ids = set()
    for feature in features:
        fid = str(feature.get("id", ""))
        if fid and fid in seen_ids:
            continue
        if fid:
            seen_ids.add(fid)
        props = feature.get("properties", {}) or {}
        dt = _parse_datetime(props.get("datetime") or props.get("start_datetime"))
        if dt is None or dt.month not in OPTICAL_MONTHS:
            continue
        kept.append((feature, dt))

    dates = sorted({dt.date().isoformat() for _, dt in kept})
    seasons = sorted({austral_season(dt) for _, dt in kept})
    years = sorted({dt.year for _, dt in kept})
    clouds = [
        x for x in (_safe_float((f.get("properties", {}) or {}).get("eo:cloud_cover")) for f, _ in kept)
        if x is not None
    ]
    platforms = sorted(
        {
            str((f.get("properties", {}) or {}).get("platform"))
            for f, _ in kept
            if (f.get("properties", {}) or {}).get("platform")
        }
    )
    passes = len(dates) >= MIN_DATES and len(seasons) >= MIN_SEASONS
    return {
        "n_items_summer": len(kept),
        "n_distinct_dates": len(dates),
        "n_austral_seasons": len(seasons),
        "n_calendar_years": len(years),
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None,
        "median_cloud_cover": float(pd.Series(clouds).median()) if clouds else None,
        "min_cloud_cover": min(clouds) if clouds else None,
        "platforms": ";".join(platforms),
        "passes_catalog_gate": bool(passes),
    }


def build_site_seed(
    forcing_csv: Path,
    habitat_csv: Path,
    expected_units: int = EXPECTED_UNITS,
    expected_sites: int = EXPECTED_SITES,
) -> pd.DataFrame:
    """Collapse frozen site-species timing rows to an 88-site support-only roster."""
    forcing = pd.read_csv(forcing_csv)
    habitat = pd.read_csv(habitat_csv)

    forbidden = {
        "count",
        "abundance",
        "trend",
        "effective_component",
        "kappa",
        "delta_kappa",
        "concentration_p",
    }
    lower_cols = {str(c).lower() for c in forcing.columns} | {str(c).lower() for c in habitat.columns}
    exact_bad = forbidden & lower_cols
    if exact_bad:
        raise ValueError(f"Outcome-like columns present in audit inputs: {sorted(exact_bad)}")

    if len(forcing) != expected_units:
        raise ValueError(f"Frozen support-unit drift: {len(forcing)} != {expected_units}")
    if forcing["site_id"].nunique() != expected_sites:
        raise ValueError(
            f"Frozen site-roster drift: {forcing['site_id'].nunique()} != {expected_sites}"
        )

    required_hab = {
        "site_id", "site_name", "region", "ccamlr_id", "latitude", "longitude",
        "mapped_ice_free_area_ha_2000m",
    }
    missing = required_hab - set(habitat.columns)
    if missing:
        raise ValueError(f"Missing habitat metadata columns: {sorted(missing)}")

    rows = []
    h = habitat.drop_duplicates("site_id").set_index("site_id")
    for site_id, local in forcing.groupby("site_id", sort=True):
        if site_id not in h.index:
            raise ValueError(f"Site missing from frozen habitat atlas: {site_id}")
        meta = h.loc[site_id]
        species = sorted({str(v) for v in local["species_id"].dropna()})
        rows.append(
            {
                "site_id": site_id,
                "site_name": meta["site_name"],
                "species_ids": ";".join(species),
                "n_species": len(species),
                "region": meta["region"],
                "ccamlr_id": meta["ccamlr_id"],
                "latitude": float(meta["latitude"]),
                "longitude": float(meta["longitude"]),
                "first_record_season": int(local["first_observed_season"].min()),
                "last_record_season": int(local["last_observed_season"].max()),
                "n_site_species_units": int(len(local)),
                "mapped_ice_free_area_ha_2000m": _safe_float(meta["mapped_ice_free_area_ha_2000m"]),
                "high_latitude_gt65": bool(abs(float(meta["latitude"])) > 65.0),
            }
        )
    out = pd.DataFrame(rows).sort_values("site_id").reset_index(drop=True)
    if len(out) != expected_sites:
        raise ValueError(f"Collapsed site-roster drift: {len(out)} != {expected_sites}")
    return out


def make_session() -> requests.Session:
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
        raise_on_status=False,
    )
    s = requests.Session()
    s.headers.update({"User-Agent": "mina-outcome-blind-catalog-audit/1.0"})
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


def _next_request(link: dict, fallback_body: dict) -> tuple[str, str, dict | None]:
    href = link.get("href")
    if not href:
        raise RuntimeError("STAC next link missing href")
    method = str(link.get("method", "GET")).upper()
    body = link.get("body")
    if method == "POST":
        if body is None:
            body = fallback_body
        return method, href, body
    return method, href, None


def search_stac(
    session: requests.Session,
    *,
    collection: str,
    lon: float,
    lat: float,
    start: str,
    end: str,
    max_pages: int = 30,
) -> list[dict]:
    body = {
        "collections": [collection],
        "intersects": {"type": "Point", "coordinates": [lon, lat]},
        "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z",
        "limit": 100,
    }
    method, url, payload = "POST", EARTH_SEARCH, body
    features: list[dict] = []
    seen_pages = set()

    for _ in range(max_pages):
        key = (method, url, json.dumps(payload, sort_keys=True) if payload is not None else "")
        if key in seen_pages:
            break
        seen_pages.add(key)

        if method == "POST":
            resp = session.post(url, json=payload, timeout=60)
        else:
            resp = session.get(url, timeout=60)
        if not resp.ok:
            raise RuntimeError(f"STAC query failed: HTTP {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        features.extend(data.get("features", []))
        next_links = [x for x in data.get("links", []) if x.get("rel") == "next"]
        if not next_links:
            return features
        method, url, payload = _next_request(next_links[0], body)

    raise RuntimeError(f"STAC pagination exceeded max_pages={max_pages}")


def audit_site(session: requests.Session, row: pd.Series, sleep_seconds: float = 0.0) -> dict:
    base = row.to_dict()
    for window in WINDOWS:
        feats = search_stac(
            session,
            collection=window.collection,
            lon=float(row["longitude"]),
            lat=float(row["latitude"]),
            start=window.start,
            end=window.end,
        )
        summary = summarize_features(feats)
        for key, value in summary.items():
            base[f"{window.name}_{key}"] = value
        if sleep_seconds:
            time.sleep(sleep_seconds)

    base["primary_dynamic_habitat_eligible"] = bool(
        base["early_landsat_passes_catalog_gate"]
        and base["late_landsat_passes_catalog_gate"]
    )
    base["sentinel_validation_eligible"] = bool(
        base["sentinel2_validation_passes_catalog_gate"]
    )
    return base


def species_site_counts(frame: pd.DataFrame, mask_col: str) -> dict[str, int]:
    selected = frame[frame[mask_col].astype(bool)]
    out = {}
    for sp in ("ADPE", "CHPE", "GEPE"):
        out[sp] = int(selected["species_ids"].fillna("").str.split(";").apply(lambda xs: sp in xs).sum())
    return out


def summarize_audit(frame: pd.DataFrame) -> dict:
    primary = frame[frame["primary_dynamic_habitat_eligible"].astype(bool)]
    validated = primary[primary["sentinel_validation_eligible"].astype(bool)]
    species_counts = species_site_counts(frame, "primary_dynamic_habitat_eligible")
    feasibility = bool(
        len(primary) >= 30
        and primary["region"].nunique() >= 3
        and all(species_counts.get(sp, 0) >= 10 for sp in ("ADPE", "CHPE", "GEPE"))
        and len(validated) >= 20
        and validated["region"].nunique() >= 2
    )
    return {
        "schema_version": 1,
        "result_id": "mina-paper2-dynamic-habitat-catalog-audit-v1",
        "audit_date": "2026-10-04",
        "source_roster": {
            "site_species_units": EXPECTED_UNITS,
            "distinct_sites": EXPECTED_SITES,
            "high_latitude_gt65_sites": int(frame["high_latitude_gt65"].astype(bool).sum()),
        },
        "window_support": {
            w.name: {
                "sites_passing": int(frame[f"{w.name}_passes_catalog_gate"].astype(bool).sum()),
                "sites_failing": int((~frame[f"{w.name}_passes_catalog_gate"].astype(bool)).sum()),
            }
            for w in WINDOWS
        },
        "primary_dynamic_habitat": {
            "eligible_sites": int(len(primary)),
            "eligible_fraction": float(len(primary) / len(frame)),
            "regions": int(primary["region"].nunique()),
            "sites_by_species_presence": species_counts,
        },
        "sentinel_validation": {
            "primary_sites_with_validation": int(len(validated)),
            "regions": int(validated["region"].nunique()),
        },
        "program_feasibility_gate_passed": feasibility,
        "decision_rule": {
            "minimum_primary_sites": 30,
            "minimum_primary_regions": 3,
            "minimum_primary_sites_representing_each_species": 10,
            "minimum_primary_sites_with_sentinel_validation": 20,
            "minimum_validation_regions": 2,
        },
        "boundary": [
            "Catalog availability is not pixel-level image validity.",
            "No cloud-cover threshold is used for site inclusion in this audit.",
            "No penguin count magnitude, population trend, effective-component number, or concentration outcome was read.",
            "A separate solar-geometry and pixel-QA gate is required before estimating habitat change."
        ],
        "failed_primary_site_ids": sorted(
            frame.loc[~frame["primary_dynamic_habitat_eligible"].astype(bool), "site_id"].astype(str).tolist()
        ),
    }


def run(args) -> dict:
    seed = build_site_seed(args.forcing_csv, args.habitat_csv)
    args.out_seed.parent.mkdir(parents=True, exist_ok=True)
    seed.to_csv(args.out_seed, index=False)

    session = make_session()
    audited = []
    for idx, row in seed.iterrows():
        print(f"[{idx+1}/{len(seed)}] {row['site_id']} {row['site_name']}", flush=True)
        audited.append(audit_site(session, row, sleep_seconds=args.sleep_seconds))

    frame = pd.DataFrame(audited).sort_values("site_id").reset_index(drop=True)
    frame.to_csv(args.out_csv, index=False)
    result = summarize_audit(frame)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--forcing-csv", type=Path, required=True)
    p.add_argument("--habitat-csv", type=Path, required=True)
    p.add_argument("--out-seed", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--sleep-seconds", type=float, default=0.02)
    args = p.parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
