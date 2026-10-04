#!/usr/bin/env python3
"""Outcome-blind STAC metadata support audit for dynamic Antarctic breeding habitat."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

DEFAULT_CONTRACT = Path("contracts/ANTARCTIC_ISLAND_ECOLOGY_PAPER2_STAC_SUPPORT_V1.json")


def _cloud(item: dict) -> float:
    value = item.get("properties", {}).get("eo:cloud_cover")
    try:
        value = float(value)
    except (TypeError, ValueError):
        return math.nan
    return value


def _year_month(item: dict) -> tuple[int | None, int | None]:
    raw = item.get("properties", {}).get("datetime") or item.get("properties", {}).get("start_datetime")
    if not raw or len(str(raw)) < 7:
        return None, None
    text = str(raw)
    try:
        return int(text[:4]), int(text[5:7])
    except ValueError:
        return None, None


def _search_items(
    session: requests.Session,
    endpoint: str,
    collection: str,
    lon: float,
    lat: float,
    start: str,
    end: str,
    timeout: int = 60,
    max_pages: int = 20,
) -> tuple[list[dict], bool]:
    url = endpoint.rstrip("/") + "/search"
    payload = {
        "collections": [collection],
        "intersects": {"type": "Point", "coordinates": [float(lon), float(lat)]},
        "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z",
        "limit": 100,
    }
    items: list[dict] = []
    method = "POST"
    next_url = url
    next_payload = payload
    max_items = 500
    for page in range(max_pages):
        for attempt in range(5):
            try:
                if method == "POST":
                    response = session.post(next_url, json=next_payload, timeout=timeout)
                else:
                    response = session.get(next_url, timeout=timeout)
                response.raise_for_status()
                body = response.json()
                break
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        items.extend(body.get("features", []))
        if len(items) >= max_items:
            return items[:max_items], False
        nxt = None
        for link in body.get("links", []):
            if link.get("rel") == "next" and link.get("href"):
                nxt = link
                break
        if not nxt:
            return items, True
        next_url = nxt["href"]
        method = str(nxt.get("method", "GET")).upper()
        next_payload = nxt.get("body") if method == "POST" else None
    return items, False


def _search_with_fallback(
    session: requests.Session,
    catalogs: list[dict],
    lon: float,
    lat: float,
    start: str,
    end: str,
) -> tuple[list[dict], str, bool]:
    errors = []
    for catalog in catalogs:
        try:
            items, complete = _search_items(
                session,
                str(catalog["endpoint"]),
                str(catalog["collection"]),
                lon,
                lat,
                start,
                end,
            )
            return items, str(catalog["name"]), complete
        except Exception as exc:
            errors.append(f'{catalog.get("name")}: {type(exc).__name__}: {exc}')
    raise RuntimeError("all STAC catalogs failed: " + " | ".join(errors))


def summarize_items(items: Iterable[dict], allowed_months: set[int]) -> dict:
    rows = []
    platforms = set()
    for item in items:
        year, month = _year_month(item)
        if year is None or month not in allowed_months:
            continue
        cloud = _cloud(item)
        platform = item.get("properties", {}).get("platform")
        if platform:
            platforms.add(str(platform))
        rows.append((year, cloud))

    def stat(threshold: float) -> tuple[int, int]:
        kept = [(y, c) for y, c in rows if not math.isnan(c) and c <= threshold]
        return len(kept), len({y for y, _ in kept})

    n80, y80 = stat(80)
    n50, y50 = stat(50)
    n20, y20 = stat(20)
    all_years = sorted({y for y, _ in rows})
    return {
        "summer_scenes_total": len(rows),
        "summer_distinct_years_total": len(all_years),
        "summer_first_year": min(all_years) if all_years else None,
        "summer_last_year": max(all_years) if all_years else None,
        "scenes_cloud_le_80": n80,
        "years_cloud_le_80": y80,
        "scenes_cloud_le_50": n50,
        "years_cloud_le_50": y50,
        "scenes_cloud_le_20": n20,
        "years_cloud_le_20": y20,
        "platforms": ";".join(sorted(platforms)),
    }


def _support(summary: dict, scene_key: str, year_key: str, min_scenes: int, min_years: int) -> bool:
    return int(summary.get(scene_key, 0)) >= min_scenes and int(summary.get(year_key, 0)) >= min_years


def build_site_roster(forcing_csv: Path, atlas_csv: Path, expected_units: int, expected_sites: int) -> pd.DataFrame:
    units = pd.read_csv(forcing_csv)
    if len(units) != expected_units:
        raise ValueError(f"forcing unit drift: {len(units)} != {expected_units}")
    forbidden = [c for c in units.columns if c.lower() in {"count", "abundance", "n_eff", "population_trend"}]
    if forbidden:
        raise ValueError(f"forbidden demographic fields present: {forbidden}")
    atlas = pd.read_csv(atlas_csv)
    coord = atlas[["site_id", "site_name", "latitude", "longitude"]].drop_duplicates("site_id")

    roster = (
        units.groupby("site_id", as_index=False)
        .agg(
            species_ids=("species_id", lambda x: ";".join(sorted(set(map(str, x))))),
            region=("region", "first"),
            first_record_season=("first_observed_season", "min"),
            last_record_season=("last_observed_season", "max"),
            n_site_species_units=("unit_id", "nunique"),
        )
        .merge(coord, on="site_id", how="left", validate="1:1")
    )
    if len(roster) != expected_sites:
        raise ValueError(f"site roster drift: {len(roster)} != {expected_sites}")
    if roster[["latitude", "longitude"]].isna().any().any():
        raise ValueError("missing site coordinates")
    return roster.sort_values("site_id").reset_index(drop=True)


def audit(forcing_csv: Path, atlas_csv: Path, contract_path: Path) -> tuple[pd.DataFrame, dict]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    expected_units = int(contract["site_roster"]["expected_site_species_units"])
    expected_sites = int(contract["site_roster"]["expected_distinct_sites"])
    roster = build_site_roster(forcing_csv, atlas_csv, expected_units, expected_sites)

    landsat_catalogs = list(contract["stac"]["landsat_catalogs"])
    sentinel_catalogs = list(contract["stac"]["sentinel_catalogs"])
    months = set(map(int, contract["season_filter"]["months"]))
    epochs = contract["epochs"]

    p_rule = contract["metadata_support_rules"]["primary_longitudinal"]
    s_rule = contract["metadata_support_rules"]["strong_longitudinal"]
    v_rule = contract["metadata_support_rules"]["sentinel_validation"]

    session = requests.Session()
    session.headers.update({"User-Agent": "mina-antarctic-island-ecology-stac-audit/1.0"})

    output_rows = []
    for idx, row in roster.iterrows():
        epoch_summaries = {}
        for name in ("early_landsat", "middle_landsat", "late_landsat"):
            start, end = epochs[name]
            items, provider, complete = _search_with_fallback(
                session, landsat_catalogs, row.longitude, row.latitude, start, end
            )
            epoch_summaries[name] = summarize_items(items, months)
            epoch_summaries[name]["catalog_provider"] = provider
            epoch_summaries[name]["catalog_complete"] = bool(complete)
            time.sleep(0.05)
        start, end = epochs["late_sentinel"]
        items, provider, complete = _search_with_fallback(
            session, sentinel_catalogs, row.longitude, row.latitude, start, end
        )
        epoch_summaries["late_sentinel"] = summarize_items(items, months)
        epoch_summaries["late_sentinel"]["catalog_provider"] = provider
        epoch_summaries["late_sentinel"]["catalog_complete"] = bool(complete)
        time.sleep(0.05)

        early = epoch_summaries["early_landsat"]
        late = epoch_summaries["late_landsat"]
        sent = epoch_summaries["late_sentinel"]

        primary = (
            _support(
                early, "scenes_cloud_le_80", "years_cloud_le_80",
                p_rule["per_epoch_min_scenes_scene_cloud_le_80"],
                p_rule["per_epoch_min_distinct_years_scene_cloud_le_80"],
            )
            and _support(
                late, "scenes_cloud_le_80", "years_cloud_le_80",
                p_rule["per_epoch_min_scenes_scene_cloud_le_80"],
                p_rule["per_epoch_min_distinct_years_scene_cloud_le_80"],
            )
        )
        strong = (
            _support(
                early, "scenes_cloud_le_50", "years_cloud_le_50",
                s_rule["per_epoch_min_scenes_scene_cloud_le_50"],
                s_rule["per_epoch_min_distinct_years_scene_cloud_le_50"],
            )
            and _support(
                late, "scenes_cloud_le_50", "years_cloud_le_50",
                s_rule["per_epoch_min_scenes_scene_cloud_le_50"],
                s_rule["per_epoch_min_distinct_years_scene_cloud_le_50"],
            )
        )
        validation = _support(
            sent, "scenes_cloud_le_80", "years_cloud_le_80",
            v_rule["min_scenes_scene_cloud_le_80"],
            v_rule["min_distinct_years_scene_cloud_le_80"],
        )

        flat = row.to_dict()
        for name, summary in epoch_summaries.items():
            for key, value in summary.items():
                flat[f"{name}__{key}"] = value
        flat["primary_longitudinal_metadata_support"] = bool(primary)
        flat["strong_longitudinal_metadata_support"] = bool(strong)
        flat["sentinel_validation_metadata_support"] = bool(validation)
        output_rows.append(flat)
        print(f"[{idx+1}/{len(roster)}] {row.site_id}: primary={primary} strong={strong} sentinel={validation}", flush=True)

    out = pd.DataFrame(output_rows)
    by_region = []
    for region, local in out.groupby("region", dropna=False):
        by_region.append({
            "region": str(region),
            "n_sites": int(len(local)),
            "primary_support_sites": int(local["primary_longitudinal_metadata_support"].sum()),
            "strong_support_sites": int(local["strong_longitudinal_metadata_support"].sum()),
            "sentinel_validation_sites": int(local["sentinel_validation_metadata_support"].sum()),
        })
    receipt = {
        "schema_version": 1,
        "result_id": "mina-antarctic-island-ecology-paper2-stac-support-result-v1",
        "contract_id": contract["contract_id"],
        "n_sites": int(len(out)),
        "primary_support_sites": int(out["primary_longitudinal_metadata_support"].sum()),
        "strong_support_sites": int(out["strong_longitudinal_metadata_support"].sum()),
        "sentinel_validation_sites": int(out["sentinel_validation_metadata_support"].sum()),
        "all_primary_support": bool(out["primary_longitudinal_metadata_support"].all()),
        "by_region": by_region,
        "failed_primary_sites": out.loc[~out["primary_longitudinal_metadata_support"], "site_id"].astype(str).tolist(),
        "failed_strong_sites": out.loc[~out["strong_longitudinal_metadata_support"], "site_id"].astype(str).tolist(),
        "failed_sentinel_validation_sites": out.loc[~out["sentinel_validation_metadata_support"], "site_id"].astype(str).tolist(),
        "boundary": [
            "This receipt uses remote-sensing metadata only and contains no demographic outcome.",
            "Scene-level cloud cover is not local pixel quality.",
            "Catalog searches are capped at 500 items per site-epoch; counts from truncated searches are lower bounds, but passing support remains valid because thresholds are monotone.",
            "No habitat-change estimate is computed at this stage.",
            "Pixel-level cloud, snow/ice, coastline and terrain QA remains mandatory before any outcome join."
        ],
    }
    return out, receipt


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--forcing-csv", required=True, type=Path)
    p.add_argument("--atlas-csv", required=True, type=Path)
    p.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    p.add_argument("--out-csv", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    args = p.parse_args()

    table, receipt = audit(args.forcing_csv, args.atlas_csv, args.contract)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out_csv, index=False)
    args.out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
