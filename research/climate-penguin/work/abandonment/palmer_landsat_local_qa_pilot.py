#!/usr/bin/env python3
"""Read real Landsat C2 QA_PIXEL at fixed Palmer point-neighborhood grids.

NOT verified sub-colony polygons, a vegetation analysis, or an island-level
land-cover map. Failed original asset reads remain unknown, never zero land.
"""
from __future__ import annotations
import argparse
import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "stac_catalog", ROOT / "palmer_abandonment_stac_inventory.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
BITS_BAD = tuple(1 << i for i in (0, 1, 3, 4, 5, 7))
GRID_M = (-80, -40, 0, 40, 80)
YEARS = (2007, 2008, 2012)  # last positive; first zero; later zero


def clear_land_qa(qa: int) -> bool:
    return all((qa & bit) == 0 for bit in BITS_BAD)


def build_source_query(year, month=None):
    from calendar import monthrange
    source = "landsat"
    query = next(q for s, y, q in mod.queries(year, year, (source,)))
    if month is not None:
        final_day = monthrange(year, month)[1]
        query["datetime"] = (
            f"{year}-{month:02d}-01T00:00:00Z/"
            f"{year}-{month:02d}-{final_day:02d}T23:59:59Z"
        )
    return query


def fetch_all(year, month=None):
    source = "landsat"
    query = build_source_query(year, month)
    url = mod.SOURCES[source]["url"]
    body, method = query, "POST"
    items, seen = {}, set()
    while True:
        key = (url, method, json.dumps(body, sort_keys=True))
        if key in seen or len(seen) >= 30:
            raise ValueError("pagination cycle")
        seen.add(key)
        obj, _ = mod.read_page(url, body, method=method)
        for feat in obj["features"]:
            items[feat["id"]] = feat
        next_page = mod.next_spec(obj, url, body)
        if next_page is None:
            break
        url, body, method = next_page
    return sorted(items.values(), key=lambda x: (x["properties"]["datetime"], x["id"]))


def sample_site(dataset, loc):
    from pyproj import Transformer
    to_3031 = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    to_native = Transformer.from_crs("EPSG:3031", dataset.crs, always_xy=True)
    center = to_3031.transform(loc["longitude"], loc["latitude"])
    points = [to_native.transform(center[0] + dx, center[1] + dy)
              for dx in GRID_M for dy in GRID_M]
    native = sorted({(r, c) for x, y in points for r, c in [dataset.index(x, y)]
                     if 0 <= r < dataset.height and 0 <= c < dataset.width})
    total, nonfill, clear, cloud, snow, water = len(native), 0, 0, 0, 0, 0
    for pixel in dataset.sample((dataset.xy(row, col) for row, col in native), masked=True):
        mask = getattr(pixel, "mask", False)
        if bool(mask.any()) if hasattr(mask, "any") else bool(mask):
            continue
        qa = int(pixel[0])
        if qa & 1:
            continue
        nonfill += 1
        clear += int(clear_land_qa(qa))
        cloud += int(bool(qa & ((1 << 1) | (1 << 3) | (1 << 4))))
        snow += int(bool(qa & (1 << 5)))
        water += int(bool(qa & (1 << 7)))
    return {
        "sampled_native_pixels": total,
        "nonfill": nonfill, "qa_clear_nonwater_nonsnow": clear,
        "cloud_or_shadow": cloud, "snow": snow, "water": water,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("qa_pilot"))
    parser.add_argument("--years", type=int, nargs="+", default=list(YEARS))
    parser.add_argument("--month", type=int, choices=range(1, 13))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    import rasterio
    import planetary_computer
    rows = []
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        GDAL_HTTP_MAX_RETRY="2", GDAL_HTTP_RETRY_DELAY="1",
    ):
        for year in args.years:
            for feature in fetch_all(year, args.month):
                asset = feature.get("assets", {}).get("qa_pixel")
                for site, loc in mod.SITES.items():
                    row = {
                        "site_id": site, "year": year, "item_id": feature["id"],
                        "date": feature["properties"]["datetime"][:10],
                        "scene_cloud": feature["properties"].get("eo:cloud_cover", ""),
                        "status": "error", "error": "",
                    }
                    try:
                        if asset is None or "href" not in asset:
                            raise ValueError("qa_pixel asset missing")
                        url = planetary_computer.sign(asset["href"])
                        with rasterio.open(url) as ds:
                            row.update(sample_site(ds, loc))
                            row["status"] = "ok"
                    except Exception as exc:
                        row["error"] = f"{type(exc).__name__}: {str(exc)[:190]}"
                    rows.append(row)
            print("year", year, "sample rows", sum(r["year"] == year for r in rows), flush=True)
    fields = [
        "site_id", "year", "item_id", "date", "scene_cloud", "status",
        "sampled_native_pixels", "nonfill", "qa_clear_nonwater_nonsnow",
        "cloud_or_shadow", "snow", "water", "error",
    ]
    with (args.out / "local_qa.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    results = {
        site: {
            str(year): {
                "scenes": sum(r["site_id"] == site and r["year"] == year for r in rows),
                "qa_read_success": sum(r["site_id"] == site and r["year"] == year and
                                       r["status"] == "ok" for r in rows),
                "scenes_any_qa_clear_land": sum(
                    r["site_id"] == site and r["year"] == year and
                    r.get("qa_clear_nonwater_nonsnow", 0) > 0 for r in rows),
            } for year in args.years
        } for site in mod.SITES
    }
    checks = {
        "years": args.years, "calendar_months": [args.month] if args.month else [2, 3],
        "site_codes": list(mod.SITES), "sample_offsets_m": GRID_M,
        "rule": "QA_PIXEL bits 0 fill,1 dilated cloud,3 cloud,4 shadow,5 snow,7 water all OFF",
        "results": results,
        "limitations": [
            "5x5 metric grid around registered point is not a historic colony polygon",
            "QA-valid land need not contain any vascular plants, mosses or lichens",
            "Different years can map coordinates onto different native pixel grids",
            "Landsat 7 after 2003 has SLC-off fill gaps; fill never counts as land",
            "Site-proximate QA is not evidence of vegetation change",
        ],
    }
    (args.out / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(results, indent=2), flush=True)
    return 2 if any(r["status"] != "ok" for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
