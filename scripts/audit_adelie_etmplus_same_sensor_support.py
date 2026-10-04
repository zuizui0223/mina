#!/usr/bin/env python3
"""Outcome-blind same-sensor Landsat-7 ETM+ support audit for Adelie footprint change."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import pandas as pd
import requests


def _cloud(item: dict) -> float:
    value = item.get("properties", {}).get("eo:cloud_cover")
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def _date_parts(item: dict):
    raw = item.get("properties", {}).get("datetime") or item.get("properties", {}).get("start_datetime")
    if not raw:
        return None, None
    text = str(raw)
    try:
        return int(text[:4]), int(text[5:7])
    except Exception:
        return None, None


def search_stac(session, endpoint, collection, lon, lat, start, end, cap=500):
    url = endpoint.rstrip("/") + "/search"
    payload = {
        "collections": [collection],
        "intersects": {"type": "Point", "coordinates": [float(lon), float(lat)]},
        "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z",
        "limit": 100,
    }
    items = []
    next_url, method, body = url, "POST", payload
    for _ in range(20):
        for attempt in range(5):
            try:
                resp = session.post(next_url, json=body, timeout=60) if method == "POST" else session.get(next_url, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        items.extend(data.get("features", []))
        if len(items) >= cap:
            return items[:cap], False
        nxt = next((x for x in data.get("links", []) if x.get("rel") == "next" and x.get("href")), None)
        if not nxt:
            return items, True
        next_url = nxt["href"]
        method = str(nxt.get("method", "GET")).upper()
        body = nxt.get("body") if method == "POST" else None
    return items, False


def summarize(items, months, platform="LANDSAT_7"):
    rows = []
    for item in items:
        props = item.get("properties", {}) or {}
        if str(props.get("platform", "")) != platform:
            continue
        year, month = _date_parts(item)
        if year is None or month not in months:
            continue
        rows.append((year, _cloud(item)))

    def count(threshold):
        kept = [r for r in rows if not math.isnan(r[1]) and r[1] <= threshold]
        return len(kept), len({r[0] for r in kept})

    n80, y80 = count(80)
    n50, y50 = count(50)
    return {
        "summer_scenes_total": len(rows),
        "summer_distinct_years_total": len({r[0] for r in rows}),
        "scenes_cloud_le_80": n80,
        "years_cloud_le_80": y80,
        "scenes_cloud_le_50": n50,
        "years_cloud_le_50": y50,
    }


def build_roster(forcing_csv: Path, atlas_csv: Path, expected_sites: int):
    units = pd.read_csv(forcing_csv)
    forbidden = [c for c in units.columns if c.lower() in {"count", "abundance", "population_trend", "n_eff", "kappa"}]
    if forbidden:
        raise ValueError(f"forbidden demographic columns: {forbidden}")
    ad = units.loc[units["species_id"].astype(str).eq("ADPE"), ["site_id"]].drop_duplicates()
    if len(ad) != expected_sites:
        raise ValueError(f"Adelie site drift: {len(ad)} != {expected_sites}")
    atlas = pd.read_csv(atlas_csv)
    coord = atlas[["site_id", "site_name", "region", "latitude", "longitude"]].drop_duplicates("site_id")
    roster = ad.merge(coord, on="site_id", how="left", validate="1:1")
    if roster[["latitude", "longitude"]].isna().any().any():
        raise ValueError("missing coordinates")
    return roster.sort_values("site_id").reset_index(drop=True)


def _passes(q: dict, rule: dict, suffix: int) -> bool:
    return (
        q[f"scenes_cloud_le_{suffix}"] >= int(rule[f"per_epoch_min_scenes_cloud_le_{suffix}"])
        and q[f"years_cloud_le_{suffix}"] >= int(rule[f"per_epoch_min_distinct_years_cloud_le_{suffix}"])
    )


def audit(forcing_csv, atlas_csv, contract_path):
    c = json.loads(Path(contract_path).read_text(encoding="utf-8"))
    roster = build_roster(Path(forcing_csv), Path(atlas_csv), int(c["candidate_roster"]["expected_sites"]))
    session = requests.Session()
    session.headers.update({"User-Agent": "mina-adelie-etmplus-same-sensor-support/1.0"})
    endpoint = c["landsat"]["stac_endpoint"]
    collection = c["landsat"]["collection"]
    platform = c["landsat"]["platform"]
    months = set(map(int, c["season_months"]))
    primary_rule = c["support_rules"]["primary"]
    strong_rule = c["support_rules"]["strong"]

    rows = []
    for i, site in roster.iterrows():
        flat = site.to_dict()
        summaries = {}
        for epoch_name, epoch in c["epochs"].items():
            items, complete = search_stac(
                session,
                endpoint,
                collection,
                float(site.longitude),
                float(site.latitude),
                epoch["start"],
                epoch["end"],
            )
            q = summarize(items, months, platform)
            q["catalog_complete"] = bool(complete)
            summaries[epoch_name] = q
            for key, value in q.items():
                flat[f"{epoch_name}__{key}"] = value
            time.sleep(0.03)

        primary = all(_passes(q, primary_rule, 80) for q in summaries.values())
        strong = all(_passes(q, strong_rule, 50) for q in summaries.values())
        flat["primary_same_sensor_support"] = bool(primary)
        flat["strong_same_sensor_support"] = bool(strong)
        rows.append(flat)
        print(f"[{i+1}/{len(roster)}] {site.site_id}: primary={primary} strong={strong}", flush=True)

    out = pd.DataFrame(rows)
    by_region = []
    for region, g in out.groupby("region", dropna=False):
        by_region.append({
            "region": str(region),
            "n_sites": int(len(g)),
            "primary_support_sites": int(g["primary_same_sensor_support"].sum()),
            "strong_support_sites": int(g["strong_same_sensor_support"].sum()),
        })

    receipt = {
        "schema_version": 1,
        "result_id": "mina-paper2-adelie-etmplus-same-sensor-support-v1-result",
        "contract_id": c["contract_id"],
        "candidate_sites": int(len(out)),
        "primary_support_sites": int(out["primary_same_sensor_support"].sum()),
        "strong_support_sites": int(out["strong_same_sensor_support"].sum()),
        "failed_primary_sites": out.loc[~out["primary_same_sensor_support"], "site_id"].astype(str).tolist(),
        "failed_strong_sites": out.loc[~out["strong_same_sensor_support"], "site_id"].astype(str).tolist(),
        "by_region": by_region,
        "decision": {
            "same_sensor_route_feasible": bool(out["primary_same_sensor_support"].sum() >= 20),
            "minimum_sites_for_route": 20,
            "demographic_magnitudes_opened": False
        },
        "boundary": [
            "Metadata support only; no demographic magnitude or trend is used.",
            "The late epoch is SLC-off and requires a separately frozen paired-pixel support gate.",
            "Scan gaps are treated as missing pixels and cannot be classified as non-colony.",
            "Passing this audit does not validate the published guano classifier."
        ]
    }
    return out, receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--forcing-csv", required=True, type=Path)
    p.add_argument("--atlas-csv", required=True, type=Path)
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--out-csv", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()
    table, receipt = audit(a.forcing_csv, a.atlas_csv, a.contract)
    a.out_csv.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(a.out_csv, index=False)
    a.out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
