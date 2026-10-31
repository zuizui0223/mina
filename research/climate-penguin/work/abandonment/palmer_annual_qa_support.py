#!/usr/bin/env python3
"""Outcome-blind annual local Landsat QA support around fixed Palmer coordinates.

Checks whether the *same predeclared 25 geographic sample positions* are ever
QA-clear non-water non-snow in >=3 distinct austral late summers both before and
after Litchfield's observed zero transition. These positions are NOT verified
colony polygons; the output is a satellite feasibility gate, NOT vegetation
cover, species occupancy, or a causal event-study result.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("palmer_p0_stac", HERE / "palmer_abandonment_stac_inventory.py")
_catalog = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_catalog)

# Prespecified grid in EPSG:3031, offsets in metres about site reference point.
OFFSETS_M = (-80, -40, 0, 40, 80)
SITES = ("LITC", "HUMB", "TORG")
LAST_POSITIVE_IMAGE_YEAR = 2007  # breeding season 2006 -> Feb-Mar 2007
FIRST_ZERO_IMAGE_YEAR = 2008      # breeding season 2007 -> Feb-Mar 2008
BAD_LANDSAT_QA_BITS = (0, 1, 2, 3, 4, 5, 7)
SCENE_FIELDS = (
    "site_id", "image_year", "breeding_season_start_year", "item_id", "date",
    "scene_cloud_pct", "status", "clear_position_count", "clear_25_bit_mask",
    "error",
)
YEAR_FIELDS = (
    "site_id", "image_year", "breeding_season_start_year", "catalog_status",
    "candidate_scene_count", "successful_qa_reads", "failed_qa_reads",
    "scenes_with_clear_positions", "distinct_clear_dates",
    "clear_positions_union", "clear_25_bit_mask",
)


def qa_clear_nonwater_nonsnow(value: int, platform: str) -> bool:
    # Bit 2 (high-confidence cirrus) applies to Landsat 8/9. In pre-2013
    # Landsat 5/7 it is not a cirrus flag, but conservatively reject if set.
    return not any(value & (1 << b) for b in BAD_LANDSAT_QA_BITS)


def popcount(mask: int) -> int:
    return int(mask).bit_count()


def read_fixed_point_mask(ds, loc: dict, transformer_cls=None) -> int:
    """Sample the same ordered 25 physical points in each native raster."""
    if transformer_cls is None:
        from pyproj import Transformer
        transformer_cls = Transformer
    to_polar = transformer_cls.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    to_native = transformer_cls.from_crs("EPSG:3031", ds.crs, always_xy=True)
    cx, cy = to_polar.transform(loc["longitude"], loc["latitude"])
    pts = [
        to_native.transform(cx + dx, cy + dy)
        for dy in OFFSETS_M for dx in OFFSETS_M
    ]
    mask = 0
    for i, sample in enumerate(ds.sample(pts, masked=True)):
        masked = getattr(sample, "mask", False)
        if bool(masked.any()) if hasattr(masked, "any") else bool(masked):
            continue
        if qa_clear_nonwater_nonsnow(int(sample[0]), ""):
            mask |= (1 << i)
    return mask


def temporal_support(rows: list[dict], *, before_end=2007, after_start=2008):
    """Compute same-position support across distinct calendar-year *unions*."""
    by_site = {}
    for site in SITES:
        site_rows = [r for r in rows if r["site_id"] == site]
        pre = [r for r in site_rows if int(r["image_year"]) <= before_end]
        post = [r for r in site_rows if int(r["image_year"]) >= after_start]
        def usable_years(subset):
            return [r for r in subset if int(r["clear_positions_union"]) > 0]
        pre_ok, post_ok = usable_years(pre), usable_years(post)
        # Counts are years in which that *specific* fixed point was clear at least once.
        pre_counts = [sum(bool(int(r["clear_25_bit_mask"]) & (1 << bit)) for r in pre_ok)
                      for bit in range(25)]
        post_counts = [sum(bool(int(r["clear_25_bit_mask"]) & (1 << bit)) for r in post_ok)
                       for bit in range(25)]
        same_pos_3 = sum(a >= 3 and b >= 3 for a, b in zip(pre_counts, post_counts))
        by_site[site] = {
            "pre_summers_with_any_clear_fixed_position": len(pre_ok),
            "post_summers_with_any_clear_fixed_position": len(post_ok),
            "same_fixed_positions_with_3_pre_and_3_post_clear_summers": same_pos_3,
            "pre_years_failed_original_qa_read": sum(int(r["failed_qa_reads"]) > 0 for r in pre),
            "post_years_failed_original_qa_read": sum(int(r["failed_qa_reads"]) > 0 for r in post),
            "pre_years_without_catalog_scenes": sum(int(r["candidate_scene_count"]) == 0 and
                                                     r["catalog_status"] == "ok" for r in pre),
            "post_years_without_catalog_scenes": sum(int(r["candidate_scene_count"]) == 0 and
                                                      r["catalog_status"] == "ok" for r in post),
        }
    return by_site


def run(first: int, last: int, out: Path) -> int:
    import planetary_computer
    import rasterio
    out.mkdir(parents=True, exist_ok=True)
    failures = 0
    scene_rows: list[dict] = []
    annual_rows: list[dict] = []
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      GDAL_HTTP_MAX_RETRY="2", GDAL_HTTP_RETRY_DELAY="1"):
        for year in range(first, last + 1):
            try:
                items = _catalog_fetch(year)
                catalogue_error = ""
            except Exception as exc:
                items, catalogue_error = [], f"{type(exc).__name__}: {str(exc)[:180]}"
                failures += 1
            accum = {site: {"n_ok": 0, "n_fail": 0, "n_any": 0,
                            "dates": set(), "mask": 0} for site in SITES}
            for item in items:
                props = item.get("properties") or {}
                asset = (item.get("assets") or {}).get("qa_pixel")
                common = {
                    "image_year": year, "breeding_season_start_year": year - 1,
                    "item_id": item.get("id", ""), "date": (props.get("datetime") or "")[:10],
                    "scene_cloud_pct": props.get("eo:cloud_cover", ""),
                }
                try:
                    if not asset or not asset.get("href"):
                        raise ValueError("qa_pixel asset missing")
                    signed = planetary_computer.sign(asset["href"])
                    with rasterio.open(signed) as ds:
                        for site in SITES:
                            try:
                                mask = read_fixed_point_mask(ds, _catalog.SITES[site])
                                acc = accum[site]
                                acc["n_ok"] += 1
                                acc["n_any"] += int(mask != 0)
                                acc["mask"] |= mask
                                if mask:
                                    acc["dates"].add(common["date"])
                                scene_rows.append({**common, "site_id": site, "status": "ok",
                                                   "clear_position_count": popcount(mask),
                                                   "clear_25_bit_mask": mask, "error": ""})
                            except Exception as exc:
                                accum[site]["n_fail"] += 1
                                failures += 1
                                scene_rows.append({**common, "site_id": site, "status": "error",
                                                   "clear_position_count": "",
                                                   "clear_25_bit_mask": "",
                                                   "error": f"{type(exc).__name__}: {str(exc)[:180]}"})
                except Exception as exc:
                    for site in SITES:
                        accum[site]["n_fail"] += 1
                        failures += 1
                        scene_rows.append({**common, "site_id": site, "status": "error",
                                           "clear_position_count": "", "clear_25_bit_mask": "",
                                           "error": f"{type(exc).__name__}: {str(exc)[:180]}"})
            for site in SITES:
                a = accum[site]
                annual_rows.append({
                    "site_id": site, "image_year": year,
                    "breeding_season_start_year": year - 1,
                    "catalog_status": "error" if catalogue_error else "ok",
                    "candidate_scene_count": len(items), "successful_qa_reads": a["n_ok"],
                    "failed_qa_reads": a["n_fail"], "scenes_with_clear_positions": a["n_any"],
                    "distinct_clear_dates": len(a["dates"]),
                    "clear_positions_union": popcount(a["mask"]),
                    "clear_25_bit_mask": a["mask"],
                })
            # Persist at every year, including if the runner is interrupted later.
            _write_csv(out / "local_qa_scenes.csv", scene_rows, SCENE_FIELDS)
            _write_csv(out / "local_qa_years.csv", annual_rows, YEAR_FIELDS)
            print(f"YEAR {year} scenes={len(items)} read={sum(accum[s]['n_ok'] for s in SITES)}"
                  f" errors={catalogue_error or sum(accum[s]['n_fail'] for s in SITES)}"
                  f" LITC_clear_positions={popcount(accum['LITC']['mask'])}", flush=True)
    summary = {
        "schema_version": 1, "status": "complete_with_errors" if failures else "complete",
        "query": "original Landsat C2 L2 QA_PIXEL at each fixed Feb-Mar scene",
        "first_calendar_image_year": first, "last_calendar_image_year": last,
        "last_positive_image_year": LAST_POSITIVE_IMAGE_YEAR,
        "first_observed_zero_image_year": FIRST_ZERO_IMAGE_YEAR,
        "sites": list(SITES), "grid_offsets_m": list(OFFSETS_M),
        "candidate_scenes_all": sum(r["candidate_scene_count"] for r in annual_rows
                                     if r["site_id"] == SITES[0]),
        "source_qa_errors": failures,
        "site_annual_support": temporal_support(annual_rows),
        "limitations": [
            "Sample grid is a fixed 160m neighborhood around MAPPPD island point, not georeferenced colony polygons.",
            "Landsat C2L2 QA clear non-water non-snow is not verified plant cover or guano.",
            "Same fixed coordinate may map to different native raster pixels across scenes.",
            "Only February–March available images; images can miss the moment of nest cessation.",
            "Catalog 0 scenes is unavailable imagery, not 0 vegetation; asset read errors are recorded.",
            "Three clear summers per fixed sample point do not satisfy the independent colony-polygon gate.",
            "Image-years 2007 and 2008 correspond to breeding seasons 2006 and 2007.",
            "Do not infer warming, greening, habitat vacancy or causal abandonment effects from QA.",
        ],
    }
    (out / "checks.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["site_annual_support"], indent=2), flush=True)
    return 2 if failures else 0


def _write_csv(path: Path, rows: list[dict], fields) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        wr = csv.DictWriter(handle, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)


def _catalog_fetch(year: int) -> list[dict]:
    from importlib.util import spec_from_file_location, module_from_spec
    path = HERE / "palmer_landsat_local_qa_pilot.py"
    spec = spec_from_file_location("qa_pilot", path)
    pilot = module_from_spec(spec)
    spec.loader.exec_module(pilot)
    return pilot.fetch_all(year)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--first", type=int, default=1986)
    ap.add_argument("--last", type=int, default=2026)
    ap.add_argument("--out", type=Path, default=Path("palmer_annual_qa"))
    args = ap.parse_args()
    if args.first > 2007 or args.last < 2008 or args.last > 2026 or args.first < 1986:
        ap.error("must include both sides of 2007/2008 transition, stay within fixed 1986-2026")
    return run(args.first, args.last, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
