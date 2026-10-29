#!/usr/bin/env python3
"""Outcome-blind STAC SCENE inventory for Palmer islands.

Catalogue items do NOT imply locally visible land, vegetation, or historic
colony footprint. No reflectance, imagery, or ecology outcome is accessed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

# Pooled area covers Litchfield, Humble, Torgersen; not a colony footprint.
BBOX = [-64.125, -64.810, -64.035, -64.740]
SITES = {
    "LITC": {"name": "Litchfield", "longitude": -64.0919, "latitude": -64.7708},
    "HUMB": {"name": "Humble", "longitude": -64.0875, "latitude": -64.7647},
    "TORG": {"name": "Torgersen", "longitude": -64.0741, "latitude": -64.7731},
}
SOURCES = {
    "landsat": {
        "url": "https://planetarycomputer.microsoft.com/api/stac/v1/search",
        "collection": "landsat-c2-l2", "start": 1986, "resolution_m": 30,
    },
    "sentinel": {
        "url": "https://earth-search.aws.element84.com/v1/search",
        "collection": "sentinel-2-l2a", "start": 2016, "resolution_m": 10,
    },
}
FIELDS = ["source", "year", "season_start_year", "status", "scenes", "distinct_dates",
          "scene_cloud_under_20", "min_scene_cloud", "page_count", "error"]
ITEM_FIELDS = ["source", "year", "id", "datetime", "platform", "scene_cloud", "collection"]


def queries(first_year: int, last_year: int, source_names: tuple[str, ...]):
    for source in source_names:
        conf = SOURCES[source]
        for year in range(max(conf["start"], first_year), last_year + 1):
            # Austral late summer in calendar year Y belongs to season Y-1/Y.
            yield source, year, {
                "collections": [conf["collection"]], "bbox": BBOX,
                "datetime": f"{year}-02-01T00:00:00Z/{year}-03-31T23:59:59Z",
                "limit": 100,
            }


def read_page(url: str, body: dict | None, *, method: str = "POST", attempts: int = 3):
    data = json.dumps(body, separators=(",", ":")).encode() if body is not None else None
    error = None
    for attempt in range(attempts):
        try:
            req = Request(
                url, data=data if method.upper() == "POST" else None,
                headers={
                    "Accept": "application/geo+json, application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "mina-palmer-p0-source-audit/1.0",
                }, method=method.upper(),
            )
            with urlopen(req, timeout=35) as resp:
                raw = resp.read()
            obj = json.loads(raw)
            if not isinstance(obj, dict) or not isinstance(obj.get("features"), list):
                raise ValueError("no valid FeatureCollection features list")
            return obj, raw
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            error = exc
            if isinstance(exc, HTTPError) and exc.code not in (408, 429, 500, 502, 503, 504):
                break
            if attempt < attempts - 1:
                time.sleep(min(2 ** attempt, 4))
    raise RuntimeError(f"source failure ({type(error).__name__}: {error})")


def item_record(source: str, year: int, feature: dict) -> dict:
    props = feature.get("properties") or {}
    cloud = props.get("eo:cloud_cover")
    try:
        cloud = float(cloud) if cloud is not None else None
        if cloud is not None and not 0 <= cloud <= 100:
            cloud = None
    except (ValueError, TypeError):
        cloud = None
    return {
        "source": source, "year": year, "id": feature.get("id", ""),
        "datetime": props.get("datetime") or props.get("start_datetime") or "",
        "platform": props.get("platform", ""), "scene_cloud": cloud,
        "collection": feature.get("collection", ""),
    }


def next_spec(payload: dict, current_url: str, current_body: dict | None):
    links = [x for x in payload.get("links", []) if x.get("rel") == "next"]
    if not links:
        return None
    if len(links) != 1:
        raise ValueError("ambiguous STAC pagination")
    link = links[0]
    url = urljoin(current_url, link["href"])
    method = link.get("method", "GET").upper()
    if method not in ("GET", "POST") or urlparse(url).netloc != urlparse(current_url).netloc:
        raise ValueError("untrusted pagination target")
    body = link.get("body") if method == "POST" else None
    if method == "POST" and link.get("merge") and current_body:
        body = {**current_body, **(body or {})}
    if method == "POST" and not isinstance(body, dict):
        raise ValueError("POST pagination missing body")
    return url, body, method


def audit_query(source: str, year: int, query: dict, *, fetcher=read_page):
    url, body, method = SOURCES[source]["url"], query, "POST"
    items_by_id, receipts, seen = {}, [], set()
    pages = 0
    error = ""
    try:
        while True:
            key = (url, method, json.dumps(body, sort_keys=True))
            if key in seen or pages >= 30:
                raise ValueError("pagination loop/overlength")
            seen.add(key)
            page, raw = fetcher(url, body, method=method)
            pages += 1
            receipts.append(hashlib.sha256(raw).hexdigest())
            for feature in page["features"]:
                if not isinstance(feature, dict) or not feature.get("id"):
                    raise ValueError("missing item ID")
                r = item_record(source, year, feature)
                if r["collection"] and r["collection"] != SOURCES[source]["collection"]:
                    raise ValueError("item collection mismatch")
                if not r["datetime"].startswith(str(year) + "-"):
                    raise ValueError("image year mismatch")
                if r["datetime"][5:7] not in ("02", "03"):
                    raise ValueError("image month outside fixed window")
                items_by_id[r["id"]] = r
            nxt = next_spec(page, url, body)
            if nxt is None:
                break
            url, body, method = nxt
    except Exception as exc:
        error = f"{type(exc).__name__}: {str(exc)[:220]}"
    items = sorted(items_by_id.values(), key=lambda r: (r["datetime"], r["id"]))
    clouds = [r["scene_cloud"] for r in items if r["scene_cloud"] is not None]
    summary = {
        "source": source, "year": year, "season_start_year": year - 1,
        "status": "error" if error else "ok", "scenes": len(items),
        "distinct_dates": len({r["datetime"][:10] for r in items}),
        "scene_cloud_under_20": sum(v < 20 for v in clouds),
        "min_scene_cloud": round(min(clouds), 3) if clouds else "",
        "page_count": pages, "error": error,
    }
    return summary, items, {"source": source, "year": year, "sha256_pages": receipts}


def period_support(rows: list[dict], source: str, first: int, last: int):
    rows = [r for r in rows if r["source"] == source and first <= r["year"] <= last]
    ok = [r for r in rows if r["status"] == "ok"]
    return {
        "requested_years": len(rows), "complete_catalog_years": len(ok),
        "years_with_scene": sum(r["scenes"] > 0 for r in ok),
        "years_without_scene": sum(r["scenes"] == 0 for r in ok),
        "failed_years": len(rows) - len(ok),
        "total_catalog_scenes": sum(r["scenes"] for r in ok),
        "supports_3_calendar_years_at_scene_level":
            sum(r["scenes"] > 0 for r in ok) >= 3,
    }


def csv_write(path: Path, rows: list[dict], columns: list[str]):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--first", type=int, default=1986)
    ap.add_argument("--last", type=int, default=2026)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", type=Path, default=Path("palmer_stac_source_audit"))
    args = ap.parse_args(argv)
    if not 1984 <= args.first <= args.last <= 2100 or not 1 <= args.workers <= 8:
        ap.error("invalid years or workers")
    args.out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    qs = list(queries(args.first, args.last, ("landsat", "sentinel")))
    parts = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(audit_query, *q): (q[0], q[1]) for q in qs}
        for future in as_completed(futures):
            source, year = futures[future]
            try:
                parts.append(future.result())
            except Exception as exc:
                parts.append(({
                    "source": source, "year": year, "season_start_year": year - 1,
                    "status": "error", "scenes": 0, "distinct_dates": 0,
                    "scene_cloud_under_20": 0, "min_scene_cloud": "",
                    "page_count": 0, "error": f"unhandled: {type(exc).__name__}: {exc}",
                }, [], {"source": source, "year": year, "sha256_pages": []}))
    parts.sort(key=lambda p: (p[0]["source"], p[0]["year"]))
    years = [p[0] for p in parts]
    items = [item for p in parts for item in p[1]]
    csv_write(args.out / "catalog_years.csv", years, FIELDS)
    csv_write(args.out / "catalog_items.csv", items, ITEM_FIELDS)
    checks = {
        "schema_version": 1, "start_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "intent": "scene catalog availability only; NOT plant-cover or clear-pixel observation",
        "region_bbox": BBOX, "site_centroids": SITES,
        "fixed_calendar_months": [2, 3],
        "breeding_season_alignment": "calendar Feb-Mar Y follows breeding season Y-1",
        "providers": SOURCES,
        "litchfield_event": {
            "last_positive_breeding_season": 2006,
            "first_zero_breeding_season": 2007,
            "last_positive_postseason_imagery_year": 2007,
            "first_zero_postseason_imagery_year": 2008,
            "landsat_pre_catalog": period_support(years, "landsat", args.first, 2007),
            "landsat_post_catalog": period_support(years, "landsat", 2008, args.last),
            "sentinel_post_catalog": period_support(years, "sentinel", 2016, args.last),
        },
        "source_status": dict(Counter(r["status"] for r in years)),
        "response_page_sha256": [p[2] for p in parts],
        "limitations": [
            "Scenes intersect pooled regional bbox, not a historic colony polygon",
            "Scene cloud percentage is not verified clear land at Litchfield",
            "No reflectance pixels or vegetation cover were measured",
            "Historic polygon coordinates and verified never-occupied controls remain missing",
            "Three catalog years are NOT three clear, georeferenced colony-years",
        ],
    }
    (args.out / "checks.json").write_text(
        json.dumps(checks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    errors = sum(r["status"] != "ok" for r in years)
    print(f"Queried {len(years)} source-years; errors={errors}; scenes={len(items)}")
    for source in ("landsat", "sentinel"):
        sr = [r for r in years if r["source"] == source]
        good = [r for r in sr if r["status"] == "ok"]
        print(f"{source}: successful={len(good)}/{len(sr)}; years_with_scene={sum(r['scenes'] > 0 for r in good)}")
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
