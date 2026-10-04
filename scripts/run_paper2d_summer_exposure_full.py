#!/usr/bin/env python3
"""Full outcome-blind A_available measurement using the frozen summer-exposure metric."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import rasterio

try:
    from scripts.recover_paper2d_summer_exposure_beaufort import (
        AEI_MD5,
        MIN_VALID_OBS,
        PRIMARY_THRESHOLD,
        SENSITIVITY_THRESHOLD,
        RES_M,
        accumulate,
        fraction_at_threshold,
        grid_for_site,
        md5,
        project_aei_support,
    )
except ModuleNotFoundError:
    from recover_paper2d_summer_exposure_beaufort import (
        AEI_MD5,
        MIN_VALID_OBS,
        PRIMARY_THRESHOLD,
        SENSITIVITY_THRESHOLD,
        RES_M,
        accumulate,
        fraction_at_threshold,
        grid_for_site,
        md5,
        project_aei_support,
    )


EXPECTED_PASSING_PHYSICAL_SITES = 77


def frozen_sites(sites: pd.DataFrame) -> pd.DataFrame:
    x = sites[sites["site_pass"].astype(bool)].copy()
    if len(x) != EXPECTED_PASSING_PHYSICAL_SITES:
        raise ValueError(f"frozen passing-site roster drift: {len(x)} != {EXPECTED_PASSING_PHYSICAL_SITES}")
    if x["site_id"].astype(str).nunique() != EXPECTED_PASSING_PHYSICAL_SITES:
        raise ValueError("passing roster contains duplicate physical site_id")
    return x.sort_values("site_id").reset_index(drop=True)


def shard(frame: pd.DataFrame, shard_index: int, n_shards: int) -> pd.DataFrame:
    if not 0 <= shard_index < n_shards:
        raise ValueError("invalid shard index")
    return frame.loc[[i % n_shards == shard_index for i in range(len(frame))]].reset_index(drop=True)


def any_fraction(valid, exposed, paired) -> float:
    return float((paired & (valid > 0) & (exposed > 0)).sum() / paired.sum())


def measure_site(site: pd.Series, scenes: pd.DataFrame, aei) -> dict:
    sid = str(site["site_id"])
    local = scenes[scenes["site_id"].astype(str) == sid].copy()
    if set(local["epoch"].astype(str)) != {"early", "late"}:
        raise ValueError(f"{sid}: incomplete frozen epoch scene roster")

    transform, shape, circle = grid_for_site(float(site["longitude"]), float(site["latitude"]))
    support = project_aei_support(aei, transform, shape, circle)
    if int(support.sum()) <= 0:
        raise ValueError(f"{sid}: no projected AEI support")

    arrays = {}
    for epoch in ("early", "late"):
        rows = local[local["epoch"].astype(str) == epoch]
        valid, exposed, _ = accumulate(rows, support, transform, shape)
        arrays[epoch] = (valid, exposed)

    ev, ee = arrays["early"]
    lv, le = arrays["late"]
    paired = support & (ev >= MIN_VALID_OBS) & (lv >= MIN_VALID_OBS)
    n = int(paired.sum())
    if n <= 0:
        raise ValueError(f"{sid}: zero paired observable support")

    out = {
        "site_id": sid,
        "site_name": str(site["site_name"]),
        "region": str(site["region"]),
        "latitude": float(site["latitude"]),
        "longitude": float(site["longitude"]),
        "early_window_start": int(site["early_window_start"]),
        "early_window_end": int(site["early_window_end"]),
        "late_window_start": int(site["late_window_start"]),
        "late_window_end": int(site["late_window_end"]),
        "early_scene_count": int((local["epoch"].astype(str) == "early").sum()),
        "late_scene_count": int((local["epoch"].astype(str) == "late").sum()),
        "aei_support_cells": int(support.sum()),
        "paired_observable_cells": n,
        "paired_observable_area_ha": n * RES_M * RES_M / 10000.0,
    }
    sep = (
        (out["late_window_start"] + out["late_window_end"]) / 2.0
        - (out["early_window_start"] + out["early_window_end"]) / 2.0
    )
    if sep <= 0:
        raise ValueError(f"{sid}: nonpositive epoch midpoint separation")
    out["epoch_midpoint_separation_years"] = float(sep)

    for label, threshold in (("p50", PRIMARY_THRESHOLD), ("p67", SENSITIVITY_THRESHOLD)):
        ef = fraction_at_threshold(ev, ee, paired, threshold)
        lf = fraction_at_threshold(lv, le, paired, threshold)
        delta = lf - ef
        out[f"early_{label}_fraction"] = ef
        out[f"late_{label}_fraction"] = lf
        out[f"delta_{label}"] = delta
        out[f"rate_{label}_per_year"] = delta / sep

    ea = any_fraction(ev, ee, paired)
    la = any_fraction(lv, le, paired)
    out["early_any_fraction"] = ea
    out["late_any_fraction"] = la
    out["delta_any"] = la - ea
    out["technical_error"] = None
    return out


def run_shard(sites_csv: Path, scenes_csv: Path, aei_raster: Path, shard_index: int, n_shards: int):
    if md5(aei_raster) != AEI_MD5:
        raise ValueError("AEI raster md5 drift")
    sites = frozen_sites(pd.read_csv(sites_csv))
    scenes = pd.read_csv(scenes_csv)
    local_sites = shard(sites, shard_index, n_shards)
    rows = []
    with rasterio.open(aei_raster) as aei:
        for _, site in local_sites.iterrows():
            try:
                row = measure_site(site, scenes, aei)
            except Exception as exc:
                row = {
                    "site_id": str(site["site_id"]),
                    "site_name": str(site["site_name"]),
                    "region": str(site["region"]),
                    "latitude": float(site["latitude"]),
                    "longitude": float(site["longitude"]),
                    "technical_error": repr(exc),
                }
            rows.append(row)
            print(f"shard {shard_index}/{n_shards} {row['site_id']}: error={row.get('technical_error')}", flush=True)

    frame = pd.DataFrame(rows)
    summary = {
        "schema_version": 1,
        "result_id": f"mina-paper2d-summer-exposure-shard-{shard_index}-v1",
        "shard_index": shard_index,
        "n_shards": n_shards,
        "sites_in_shard": int(len(frame)),
        "successful_sites": int(frame["technical_error"].isna().sum()),
        "technical_errors": int(frame["technical_error"].notna().sum()),
        "demographic_magnitudes_opened": False,
    }
    return summary, frame


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sites-csv", required=True, type=Path)
    p.add_argument("--scenes-csv", required=True, type=Path)
    p.add_argument("--aei-raster", required=True, type=Path)
    p.add_argument("--shard-index", required=True, type=int)
    p.add_argument("--n-shards", required=True, type=int)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-csv", required=True, type=Path)
    a = p.parse_args()

    summary, frame = run_shard(
        a.sites_csv, a.scenes_csv, a.aei_raster, a.shard_index, a.n_shards
    )
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    frame.to_csv(a.out_csv, index=False)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary["technical_errors"]:
        raise SystemExit("Full summer-exposure shard contains technical errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
