#!/usr/bin/env python3
"""Post-hoc MAPPPD diagnostic: intensification versus zero-to-positive expansion.

This is hypothesis generation only. It reuses the frozen regional panel roster
and observation calibration and introduces no p-value or tuned threshold.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.test_mapppd_regional_concentration import (
    build_support,
    load_rda,
)
from scripts.run_paper2_real_v3_fit import (
    build_frozen_real_records,
    calibrate_observation,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
)
from scripts.simulate_paper2_integrated_recovery import collapse_same_season


PINNED = "88c73a507e0921b2541c218c71eaf16721bc6502"


def transition_rows(panel: dict, collapsed: pd.DataFrame) -> list[dict]:
    sp = panel["species_id"]
    roster = [str(x) for x in panel["retained_sites"]]
    seasons = [int(x) for x in panel["complete_seasons"]]

    x = collapsed[
        collapsed["species_id"].astype(str).eq(sp)
        & collapsed["site_id"].astype(str).isin(roster)
        & collapsed["season"].isin(seasons)
    ].copy()
    x["adjusted_count"] = np.maximum(np.expm1(x["state_hat"].to_numpy(float)), 0.0)

    expected = len(roster) * len(seasons)
    if len(x) != expected:
        raise ValueError(
            f"incomplete frozen panel: {sp} {panel['region']} {len(x)} != {expected}"
        )

    mat = (
        x.pivot(index="season", columns="site_id", values="adjusted_count")
        .reindex(index=seasons, columns=roster)
    )
    if mat.isna().any().any():
        raise ValueError("missing frozen panel cell")

    rows = []
    for a, b in zip(seasons[:-1], seasons[1:]):
        if int(b) - int(a) != 1:
            continue
        before = mat.loc[a].to_numpy(float)
        after = mat.loc[b].to_numpy(float)
        n0 = float(before.sum())
        n1 = float(after.sum())
        if not (n1 > n0):
            continue

        gain = np.maximum(after - before, 0.0)
        occupied = before > 0.0
        empty = before == 0.0
        zero_to_positive = empty & (after > 0.0)

        existing_gain = float(gain[occupied].sum())
        expansion_gain = float(gain[zero_to_positive].sum())
        gross = existing_gain + expansion_gain

        rows.append({
            "species_id": sp,
            "region": str(panel["region"]),
            "season_t": int(a),
            "season_t1": int(b),
            "total_t": n0,
            "total_t1": n1,
            "net_total_change": float(n1 - n0),
            "n_retained_sites": int(len(roster)),
            "n_occupied_sites_t": int(occupied.sum()),
            "n_exact_zero_sites_t": int(empty.sum()),
            "n_zero_to_positive_sites": int(zero_to_positive.sum()),
            "gross_existing_gain": existing_gain,
            "gross_expansion_gain": expansion_gain,
            "gross_positive_gain": gross,
            "intensification_fraction": (
                existing_gain / gross if gross > 0 else None
            ),
            "expansion_fraction": (
                expansion_gain / gross if gross > 0 else None
            ),
        })
    return rows


def summarize(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {
            "positive_total_transitions": 0,
            "with_exact_zero_site_at_t": 0,
            "with_zero_to_positive_site": 0,
            "gross_existing_gain": 0.0,
            "gross_expansion_gain": 0.0,
            "gross_positive_gain": 0.0,
            "intensification_fraction": None,
            "expansion_fraction": None,
        }
    ge = float(frame["gross_existing_gain"].sum())
    gx = float(frame["gross_expansion_gain"].sum())
    gg = ge + gx
    return {
        "positive_total_transitions": int(len(frame)),
        "with_exact_zero_site_at_t": int((frame["n_exact_zero_sites_t"] > 0).sum()),
        "with_zero_to_positive_site": int((frame["n_zero_to_positive_sites"] > 0).sum()),
        "gross_existing_gain": ge,
        "gross_expansion_gain": gx,
        "gross_positive_gain": gg,
        "intensification_fraction": ge / gg if gg > 0 else None,
        "expansion_fraction": gx / gg if gg > 0 else None,
        "median_transition_intensification_fraction": (
            float(frame["intensification_fraction"].dropna().median())
            if frame["intensification_fraction"].notna().any() else None
        ),
    }


def run(root: Path) -> tuple[dict, pd.DataFrame]:
    obs = load_rda(root / "data" / "penguin_obs.rda", "penguin_obs")
    sites = load_rda(root / "data" / "sites.rda", "sites")

    metadata = build_frozen_observation_metadata(obs)
    support = build_support(metadata, sites)
    eligible = [x for x in support if x["eligible"]]

    records = build_frozen_real_records(obs)
    cal = calibrate_observation(records)
    collapsed = collapse_same_season(
        records,
        delta_image=float(cal["delta_image"]),
        sigma1=float(cal["accuracy"]["1"]["sigma"]),
        sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
    )

    transitions = []
    for panel in eligible:
        transitions.extend(transition_rows(panel, collapsed))
    frame = pd.DataFrame(transitions)

    panels = []
    if not frame.empty:
        for (sp, region), g in frame.groupby(["species_id", "region"], sort=True):
            panels.append({
                "species_id": str(sp),
                "region": str(region),
                **summarize(g.reset_index(drop=True)),
            })

    # Context subset: panels whose first-to-last abundance trend is increasing.
    panel_direction = {}
    for panel in eligible:
        sp = panel["species_id"]
        roster = panel["retained_sites"]
        seasons = panel["complete_seasons"]
        x = collapsed[
            collapsed["species_id"].astype(str).eq(sp)
            & collapsed["site_id"].astype(str).isin(roster)
            & collapsed["season"].isin(seasons)
        ].copy()
        x["adjusted_count"] = np.maximum(np.expm1(x["state_hat"].to_numpy(float)), 0.0)
        totals = x.groupby("season")["adjusted_count"].sum().reindex(seasons)
        panel_direction[(str(sp), str(panel["region"]))] = (
            "increase" if float(totals.iloc[-1]) > float(totals.iloc[0])
            else "decline" if float(totals.iloc[-1]) < float(totals.iloc[0])
            else "flat"
        )

    increasing_keys = {k for k, v in panel_direction.items() if v == "increase"}
    if frame.empty:
        inc = frame.copy()
    else:
        mask = [
            (str(r.species_id), str(r.region)) in increasing_keys
            for r in frame.itertuples(index=False)
        ]
        inc = frame.loc[mask].copy()

    result = {
        "schema_version": 1,
        "result_id": "mina-mapppd-intensification-before-expansion-diagnostic-v1",
        "status": "posthoc_hypothesis_generation_only",
        "source": {"mapppdr_commit": PINNED},
        "all_positive_growth_transitions": summarize(frame),
        "first_to_last_increasing_panel_transitions": summarize(inc),
        "panel_summaries": panels,
        "panel_direction": [
            {"species_id": k[0], "region": k[1], "first_to_last_direction": v}
            for k, v in sorted(panel_direction.items())
        ],
        "boundary": [
            "Exact adjusted zero is the only empty-site definition; no low-count threshold is used.",
            "Gross positive gains can exceed net panel growth when some sites decline concurrently.",
            "No null model or p-value is attached.",
            "This output can generate but cannot confirm an intensification-before-expansion hypothesis."
        ],
        "stop_rule": "No threshold, null, lag, panel subset, or alternative allocation metric is opened after this result."
    }
    return result, frame


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-csv", required=True, type=Path)
    a = p.parse_args()
    result, frame = run(a.mapppdr_dir)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    frame.to_csv(a.out_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
