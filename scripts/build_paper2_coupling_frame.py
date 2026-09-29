#!/usr/bin/env python3
"""Build the outcome-blind Paper 2 shared-forcing coupling predictor frame."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _zscore(values: pd.Series) -> pd.Series:
    sd = float(values.std(ddof=1))
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError("cannot standardize a constant/nonfinite predictor")
    return (values - float(values.mean())) / sd


def build_primary_coupling_frame(
    forcing_units: pd.DataFrame,
    forcing_result: dict,
    hierarchy: pd.DataFrame,
    terrain: pd.DataFrame,
    *,
    standardize: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """Join frozen outcome-blind inputs and fail closed on uncovered AEI sites."""
    eligibility = forcing_result["decision"]["modeling_eligibility_by_species"]
    selected_units: list[str] = []
    selected_level: dict[str, str] = {}
    for species_id, decision in eligibility.items():
        selected_units.extend(str(v) for v in decision["covered_units"])
        selected_level[str(species_id)] = str(decision["level"])

    target = forcing_units[
        forcing_units["unit_id"].astype(str).isin(set(selected_units))
    ].copy()
    if len(target) != len(set(selected_units)):
        raise ValueError(
            f"forcing unit coverage drift: {len(target)} != {len(set(selected_units))}"
        )

    hcols = [
        "site_id",
        "mapped_ice_free_pixel_count_2000m",
        "mapped_ice_free_area_ha_2000m",
        "tier2_richness_2000m",
    ]
    tcols = ["site_id", "elevation_relief_p90_p10_m_2000m"]
    merged = target.merge(
        hierarchy[hcols],
        on="site_id",
        how="left",
        validate="many_to_one",
    ).merge(
        terrain[tcols],
        on="site_id",
        how="left",
        validate="many_to_one",
    )

    pixel_count = pd.to_numeric(
        merged["mapped_ice_free_pixel_count_2000m"], errors="coerce"
    )
    covered = pixel_count > 0
    uncovered_units = sorted(merged.loc[~covered, "unit_id"].astype(str).tolist())

    primary = merged.loc[covered].copy()
    for col in (
        "mapped_ice_free_area_ha_2000m",
        "tier2_richness_2000m",
        "elevation_relief_p90_p10_m_2000m",
    ):
        primary[col] = pd.to_numeric(primary[col], errors="coerce")
    complete = primary[
        [
            "mapped_ice_free_area_ha_2000m",
            "tier2_richness_2000m",
            "elevation_relief_p90_p10_m_2000m",
        ]
    ].notna().all(axis=1)
    primary = primary.loc[complete].copy()

    primary["A_raw"] = np.log1p(primary["mapped_ice_free_area_ha_2000m"])
    primary["H_raw"] = primary["tier2_richness_2000m"].astype(float)
    primary["R_raw"] = np.log1p(primary["elevation_relief_p90_p10_m_2000m"])

    if standardize:
        for raw, out in (("A_raw", "A"), ("H_raw", "H"), ("R_raw", "R")):
            primary[out] = primary.groupby("species_id")[raw].transform(_zscore)
    else:
        primary["A"] = primary["A_raw"]
        primary["H"] = primary["H_raw"]
        primary["R"] = primary["R_raw"]
    primary["AH"] = primary["A"] * primary["H"]

    def forcing_group(row: pd.Series) -> str:
        level = selected_level[str(row["species_id"])]
        if level == "ccamlr":
            value = row["ccamlr_id"]
        elif level == "apbp_region":
            value = row["region"]
        elif level == "species_wide":
            value = row["species_id"]
        else:
            raise ValueError(f"unsupported forcing level: {level}")
        if pd.isna(value) or not str(value).strip():
            raise ValueError(
                f"missing forcing-group label for {row['unit_id']} at {level}"
            )
        return str(value)

    primary["forcing_group"] = primary.apply(forcing_group, axis=1)
    primary = primary.sort_values(["species_id", "unit_id"]).reset_index(drop=True)

    audit = {
        "eligible_coupling_units": int(len(target)),
        "predictor_complete_units": int(len(primary)),
        "uncovered_breeding_option_units": uncovered_units,
        "predictor_complete_by_species": {
            str(k): int(v)
            for k, v in primary["species_id"].value_counts().sort_index().items()
        },
        "forcing_level_by_species": selected_level,
        "coverage_rule": (
            "mapped_ice_free_pixel_count_2000m <= 0 is missing coverage, "
            "not an ecological zero"
        ),
        "no_demographic_magnitudes_opened": True,
    }
    return primary, audit


def _vif(X: np.ndarray, j: int) -> float:
    y = X[:, j]
    others = np.delete(X, j, axis=1)
    beta = np.linalg.lstsq(others, y, rcond=None)[0]
    resid = y - others @ beta
    sst = float(((y - y.mean()) ** 2).sum())
    if sst <= 0:
        return float("inf")
    r2 = 1.0 - float((resid**2).sum()) / sst
    return float(1.0 / (1.0 - r2)) if r2 < 1.0 else float("inf")


def design_diagnostics(frame: pd.DataFrame) -> dict:
    """Check whether A x H is structurally aliased with main effects/geography."""
    out: dict[str, dict] = {}
    for species_id, local in frame.groupby("species_id", sort=True):
        local = local.copy()
        group_dummies = pd.get_dummies(
            local["forcing_group"].astype(str),
            drop_first=True,
            dtype=float,
        )
        columns = ["A", "H", "R", "AH"]
        X = np.column_stack(
            [
                np.ones(len(local)),
                local[columns].to_numpy(float),
                group_dummies.to_numpy(float),
            ]
        )
        names = ["intercept", *columns, *[f"group:{c}" for c in group_dummies.columns]]
        rank = int(np.linalg.matrix_rank(X))
        vifs = {
            names[j]: _vif(X, j)
            for j in range(1, X.shape[1])
        }
        by_group = {}
        for group, g in local.groupby("forcing_group", sort=True):
            by_group[str(group)] = {
                "n": int(len(g)),
                **{
                    f"sd_{col}": float(g[col].std(ddof=1))
                    for col in ("A", "H", "R", "AH")
                },
            }
        out[str(species_id)] = {
            "n": int(len(local)),
            "n_columns": int(X.shape[1]),
            "rank": rank,
            "full_rank": bool(rank == X.shape[1]),
            "condition_number": float(np.linalg.cond(X)),
            "vif": vifs,
            "max_vif": float(max(vifs.values())) if vifs else 1.0,
            "correlations": local[columns].corr().to_dict(),
            "within_forcing_group": by_group,
        }
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--forcing-units", required=True, type=Path)
    p.add_argument("--forcing-result", required=True, type=Path)
    p.add_argument("--hierarchy", required=True, type=Path)
    p.add_argument("--terrain", required=True, type=Path)
    p.add_argument("--out-csv", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()

    forcing = pd.read_csv(a.forcing_units)
    hierarchy = pd.read_csv(a.hierarchy)
    terrain = pd.read_csv(a.terrain)
    result = json.loads(a.forcing_result.read_text(encoding="utf-8"))
    frame, audit = build_primary_coupling_frame(
        forcing, result, hierarchy, terrain
    )
    diagnostics = design_diagnostics(frame)
    payload = {
        "schema_version": 1,
        "audit_id": "mina-paper2-coupling-frame-audit-v1",
        **audit,
        "design_diagnostics": diagnostics,
        "interaction_design_estimable": bool(
            all(
                d["full_rank"]
                and d["max_vif"] < 10.0
                and d["condition_number"] < 10.0
                for d in diagnostics.values()
            )
        ),
    }
    a.out_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(a.out_csv, index=False)
    a.out_json.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
