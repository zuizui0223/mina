#!/usr/bin/env python3
"""Aggregate the frozen full-roster summer-exposure measurement."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

EXPECTED_SITES = 77
BEAU_EXPECTED_DELTA = 0.05559584239787286
BEAU_TOL = 1e-12


def aggregate(shard_dir: Path) -> tuple[dict, pd.DataFrame]:
    files = sorted(shard_dir.glob("summer_exposure_sites_shard*.csv"))
    if len(files) != 6:
        raise ValueError(f"expected 6 shard CSVs, found {len(files)}")
    x = pd.concat([pd.read_csv(p) for p in files], ignore_index=True)
    if len(x) != EXPECTED_SITES or x["site_id"].astype(str).nunique() != EXPECTED_SITES:
        raise ValueError(f"full roster drift: rows={len(x)}, sites={x['site_id'].nunique()}")
    if x["technical_error"].notna().any():
        bad = x.loc[x["technical_error"].notna(), ["site_id", "technical_error"]].to_dict("records")
        raise ValueError(f"technical errors in full measurement: {bad}")

    beau = x[x["site_id"].astype(str) == "BEAU"]
    if len(beau) != 1:
        raise ValueError("Beaufort missing/duplicated")
    beau_delta = float(beau.iloc[0]["delta_p50"])
    if abs(beau_delta - BEAU_EXPECTED_DELTA) > BEAU_TOL:
        raise ValueError(f"Beaufort metric drift: {beau_delta} != {BEAU_EXPECTED_DELTA}")

    by_region = {}
    for region, g in x.groupby("region"):
        by_region[str(region)] = {
            "sites": int(len(g)),
            "positive_delta_p50": int((g["delta_p50"] > 0).sum()),
            "negative_delta_p50": int((g["delta_p50"] < 0).sum()),
            "zero_delta_p50": int((g["delta_p50"] == 0).sum()),
            "median_delta_p50": float(g["delta_p50"].median()),
        }

    summary = {
        "schema_version": 1,
        "result_id": "mina-paper2d-summer-exposure-full-v1",
        "status": "outcome_blind_A_available_measurement",
        "measurement": "persistent summer-exposed fraction within paired observable current-AEI support",
        "sites": int(len(x)),
        "technical_errors": 0,
        "positive_delta_p50_sites": int((x["delta_p50"] > 0).sum()),
        "negative_delta_p50_sites": int((x["delta_p50"] < 0).sum()),
        "zero_delta_p50_sites": int((x["delta_p50"] == 0).sum()),
        "median_delta_p50": float(x["delta_p50"].median()),
        "q25_delta_p50": float(x["delta_p50"].quantile(0.25)),
        "q75_delta_p50": float(x["delta_p50"].quantile(0.75)),
        "median_rate_p50_per_year": float(x["rate_p50_per_year"].median()),
        "by_region": by_region,
        "beaufort_recovery_reproduced": True,
        "demographic_magnitudes_opened": False,
        "next_gate": "A_occupied guano-footprint measurement recovery remains required before the land-space decoupling test can be opened.",
        "boundary": [
            "These are terrestrial exposure measurements, not penguin demographic outcomes.",
            "Positive delta means more persistent summer exposure inside the fixed current AEI support; it does not by itself prove newly deglaciated nestable rock.",
            "The broad austral-summer metric is a frozen measurement state and is not yet a species-phenology-matched demographic predictor."
        ]
    }
    return summary, x.sort_values("site_id").reset_index(drop=True)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--shard-dir", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-csv", required=True, type=Path)
    a = p.parse_args()
    summary, x = aggregate(a.shard_dir)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    x.to_csv(a.out_csv, index=False)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
