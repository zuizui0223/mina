#!/usr/bin/env python3
"""SMP spatial-recovery hysteresis V2.

V2 replaces the failed circular phase null with a non-circular common-shift
null. One integer-year shift is shared by every spell in the same physical
MasterSite phase block, preserving relative event geometry and local covariance.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.gate_smp_master_site_support_v1 import _norm
from scripts.run_smp_spatial_recovery_hysteresis_v1 import (
    H_from_years,
    build_panel_cache,
    hierarchical_means,
    prepare_count_frame,
    sign_flip_test,
    species_bootstrap,
    spell_effect,
)


SEED = 20261005
SHIFT_B = 20000


def spell_weights(frame: pd.DataFrame) -> np.ndarray:
    """Return linear weights reproducing spell->SiteID->MasterSite->species->T."""
    f = frame.reset_index(drop=True).copy()
    species_names = sorted(f["species"].astype(str).unique())
    n_species = len(species_names)
    if n_species <= 0:
        raise ValueError("no species")

    weights = np.zeros(len(f), float)
    for species, gs in f.groupby("species", sort=True):
        masters = sorted(gs["master_site_key"].astype(str).unique())
        for master, gm in gs.groupby("master_site_key", sort=True):
            sites = sorted(gm["site_id"].astype(str).unique())
            for site, gi in gm.groupby("site_id", sort=True):
                w = (
                    1.0 / n_species
                    / len(masters)
                    / len(sites)
                    / len(gi)
                )
                weights[gi.index.to_numpy(int)] = w
    if not np.isclose(weights.sum(), 1.0):
        raise AssertionError(f"spell weights do not sum to 1: {weights.sum()}")
    return weights


def group_metadata(spells: list[dict]) -> dict[str, dict]:
    out = {}
    for sp in spells:
        gid = str(sp["shift_group_id"])
        shifts = tuple(int(v) for v in sp["eligible_common_shifts"])
        if len(shifts) < 3:
            raise ValueError("V2 spell has fewer than 3 frozen common shifts")
        meta = (str(sp["master_site_key"]), int(sp["phase_block_start"]), int(sp["phase_block_end"]), shifts)
        if gid in out and out[gid]["signature"] != meta:
            raise ValueError(f"inconsistent V2 shift-group metadata: {gid}")
        out[gid] = {
            "signature": meta,
            "shifts": shifts,
        }
    return out


def precompute_shift_H(spells: list[dict], cache: dict) -> dict:
    """Precompute H for every spell under every frozen group shift."""
    values = {}
    for i, sp in enumerate(spells):
        panel_key = (
            str(sp["species"]),
            _norm(sp["master_site"]),
            str(sp["unit"]),
        )
        mat = cache[panel_key]
        site = str(sp["site_id"])
        years0 = [
            int(sp["abandon_from"]),
            int(sp["abandon_to"]),
            int(sp["recolonize_from"]),
            int(sp["recolonize_to"]),
        ]
        gid = str(sp["shift_group_id"])
        for k in (int(v) for v in sp["eligible_common_shifts"]):
            ys = [y + k for y in years0]
            values[(i, gid, k)] = H_from_years(mat, site, *ys)
    return values


def noncircular_common_shift_null(
    observed_rows: pd.DataFrame,
    spells: list[dict],
    cache: dict,
    *,
    B: int = SHIFT_B,
    seed: int = SEED,
) -> dict:
    frame = observed_rows.reset_index(drop=True).copy()
    if len(frame) != len(spells):
        raise ValueError("observed spell row/order mismatch")
    weights = spell_weights(frame)
    groups = group_metadata(spells)
    hlookup = precompute_shift_H(spells, cache)
    members = defaultdict(list)
    for i, sp in enumerate(spells):
        members[str(sp["shift_group_id"])].append(i)

    T_obs = float(np.sum(weights * frame["H"].to_numpy(float)))
    # Cross-check the optimized linear statistic against the canonical hierarchy.
    canonical = float(hierarchical_means(frame)["T"])
    if not np.isclose(T_obs, canonical):
        raise AssertionError((T_obs, canonical))

    rng = np.random.default_rng(int(seed))
    T_null = np.empty(int(B), float)
    gids = sorted(groups)
    for r in range(int(B)):
        total = 0.0
        for gid in gids:
            k = int(rng.choice(groups[gid]["shifts"]))
            for i in members[gid]:
                total += weights[i] * hlookup[(i, gid, k)]
        T_null[r] = total

    median = float(np.median(T_null))
    p = float((1 + np.sum(T_null >= T_obs)) / (len(T_null) + 1))
    return {
        "simulations": int(B),
        "seed": int(seed),
        "shift_groups": int(len(gids)),
        "median_T": median,
        "q025": float(np.quantile(T_null, 0.025)),
        "q975": float(np.quantile(T_null, 0.975)),
        "delta_shift_observed_minus_median": float(T_obs - median),
        "upper_tail_p": p,
    }


def run(
    input_path: Path,
    structural_json: Path,
    v2_support_json: Path,
    *,
    assume_whole_colony_extract: bool = False,
) -> tuple[dict, pd.DataFrame]:
    structural = json.loads(structural_json.read_text(encoding="utf-8"))
    support = json.loads(v2_support_json.read_text(encoding="utf-8"))
    if structural.get("analysis_id") != "mina-smp-spatial-recovery-structure-v1":
        raise ValueError("V2 requires identity-resolved spatial-recovery structure")
    if not structural.get("decision", {}).get("structural_gate_passed"):
        raise ValueError("identity-resolved structural gate did not pass")
    if support.get("analysis_id") != "mina-smp-spatial-recovery-hysteresis-support-v2":
        raise ValueError("V2 requires V2 state-only shift support")
    if not support.get("decision", {}).get("v2_magnitude_execution_support_passed"):
        raise ValueError("V2 state-only shift support gate did not pass")

    zero = support.get("zero_semantics_confirmation", {}) or {}
    for key in (
        "row_with_direct_count_zero_is_surveyed_nil",
        "absent_site_year_row_is_not_zero",
        "estimated_or_imputed_zero_excluded_from_primary",
    ):
        if zero.get(key) is not True:
            raise ValueError(f"V2 requires provider-confirmed zero semantics: {key}")

    spells = list(support["completed_spells"])
    x = prepare_count_frame(
        input_path,
        assume_whole_colony_extract=assume_whole_colony_extract,
    )
    cache = build_panel_cache(x, structural, spells)

    rows = []
    for sp in spells:
        key = (str(sp["species"]), _norm(sp["master_site"]), str(sp["unit"]))
        eff = spell_effect(cache[key], str(sp["site_id"]), sp)
        rows.append({**sp, **eff})
    frame = pd.DataFrame(rows)

    hier = hierarchical_means(frame)
    vals = hier["species"]["species_mean_H"].to_numpy(float)
    sign = sign_flip_test(vals)
    ci = species_bootstrap(vals)
    shift = noncircular_common_shift_null(frame, spells, cache)

    T = float(hier["T"])
    supported = bool(
        T > 0
        and sign["one_sided_p"] <= 0.05
        and shift["delta_shift_observed_minus_median"] > 0
        and shift["upper_tail_p"] <= 0.05
    )

    result = {
        "schema_version": 2,
        "analysis_id": "mina-smp-spatial-recovery-hysteresis-effect-v2",
        "status": "first_and_only_v2_magnitude_execution",
        "spell_count": int(len(frame)),
        "macro": {
            "primary_T_species_balanced_mean_H": T,
            "species_count": int(len(vals)),
            "species_positive_H": int(np.sum(vals > 0)),
            "species_sign_flip": sign,
            "species_bootstrap_95": ci,
            "noncircular_common_shift_null": shift,
            "supported": supported,
            "site_means": hier["site"].to_dict(orient="records"),
            "master_means": hier["master"].to_dict(orient="records"),
            "species_means": hier["species"].to_dict(orient="records"),
        },
        "decision": {
            "spatial_recovery_hysteresis_v2_supported": supported,
            "requires_sign_flip_and_noncircular_common_shift_null": True,
        },
        "boundary": [
            "V2 support establishes event-aligned threshold asymmetry beyond non-circular phase/trajectory structure, not a unique social mechanism.",
            "No circular wrapping is used.",
            "All spells in one physical MasterSite phase block share one null shift.",
            "Time-varying habitat and other mechanisms remain possible.",
        ],
    }
    return result, frame


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--structural-json", required=True, type=Path)
    p.add_argument("--v2-support-json", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-spells-csv", required=True, type=Path)
    p.add_argument("--assume-whole-colony-extract", action="store_true")
    a = p.parse_args()
    result, frame = run(
        a.input,
        a.structural_json,
        a.v2_support_json,
        assume_whole_colony_extract=a.assume_whole_colony_extract,
    )
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    frame.to_csv(a.out_spells_csv, index=False)
    print(json.dumps({
        "spell_count": result["spell_count"],
        "decision": result["decision"],
        "macro": {
            k: v for k, v in result["macro"].items()
            if k not in {"site_means", "master_means", "species_means"}
        },
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
