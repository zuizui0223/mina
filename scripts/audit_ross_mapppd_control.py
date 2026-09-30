#!/usr/bin/env python3
"""Audit Ross Island Adelie colony-size controls from pinned mapppdr data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr

PINNED_MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
TARGET_NAMES = ("Cape Royds", "Cape Bird", "Cape Crozier")


def _load(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        frame = result[expected]
    elif len(result) == 1:
        frame = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected} in {path}: {list(result)}")
    if not isinstance(frame, pd.DataFrame):
        raise TypeError(f"{expected} is not a data frame")
    return frame


def audit(root: Path, out_dir: Path) -> dict[str, object]:
    data = root / "data"
    sites = _load(data / "sites.rda", "sites")
    species = _load(data / "species.rda", "species")
    obs = _load(data / "penguin_obs.rda", "penguin_obs")

    candidates = sites[
        sites["site_name"].astype(str).str.contains(
            r"Royds|Bird|Crozier", case=False, regex=True
        )
    ].copy()
    out_dir.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(out_dir / "site_candidates.csv", index=False)

    common = species["common_name"].fillna("").astype(str).str.lower()
    adelie = species[
        common.str.contains("adel")
        | (
            (species["genus"].astype(str) == "Pygoscelis")
            & (species["species"].astype(str) == "adeliae")
        )
    ].copy()
    if len(adelie) != 1:
        raise ValueError(f"expected one Adelie row, observed {len(adelie)}")
    adelie.to_csv(out_dir / "adelie_species.csv", index=False)

    exact = candidates[candidates["site_name"].isin(TARGET_NAMES)].copy()
    exact.to_csv(out_dir / "exact_sites.csv", index=False)

    focal = obs[
        obs["site_id"].isin(exact["site_id"])
        & (obs["species_id"] == adelie.iloc[0]["species_id"])
    ].copy()
    focal.to_csv(out_dir / "ross_adelie_obs.csv", index=False)

    nests = focal[(focal["type"] == "nests") & focal["count"].notna()].copy()
    nests["year_numeric"] = pd.to_numeric(nests["year"], errors="coerce")
    nests.to_csv(out_dir / "ross_adelie_nest_counts.csv", index=False)

    coverage: dict[str, object] = {}
    for _, site in exact.iterrows():
        sid = site["site_id"]
        name = str(site["site_name"])
        local = nests[nests["site_id"] == sid].copy()
        years = sorted(set(int(x) for x in local["year_numeric"].dropna()))
        per_year = (
            local.groupby("year_numeric", dropna=True)
            .size()
            .sort_index()
            .to_dict()
        )
        coverage[name] = {
            "site_id": str(sid),
            "n_nest_count_records": int(len(local)),
            "year_min": min(years) if years else None,
            "year_max": max(years) if years else None,
            "distinct_years": len(years),
            "records_per_year": {str(int(k)): int(v) for k, v in per_year.items()},
            "accuracy_values": sorted(
                set(str(x) for x in local["accuracy"].dropna().unique())
            ),
            "vantage_values": sorted(
                set(str(x) for x in local["vantage"].dropna().unique())
            ),
        }

    common_years = None
    for name in TARGET_NAMES:
        local = nests[nests["site_id"] == exact.loc[exact["site_name"] == name, "site_id"].iloc[0]]
        years = set(int(x) for x in local["year_numeric"].dropna())
        common_years = years if common_years is None else common_years & years

    return {
        "schema_version": 1,
        "audit_id": "mina-ross-mapppd-colony-size-control-v1",
        "mapppdr_commit": PINNED_MAPPPDR_COMMIT,
        "penguin_obs_columns": list(obs.columns),
        "target_site_names": list(TARGET_NAMES),
        "name_match_candidates": candidates[
            ["site_id", "site_name"]
        ].astype(str).to_dict(orient="records"),
        "exact_site_count": int(len(exact)),
        "exact_sites": exact[["site_id", "site_name"]].astype(str).to_dict(orient="records"),
        "adelie_species_id": str(adelie.iloc[0]["species_id"]),
        "n_focal_observations": int(len(focal)),
        "n_focal_nest_counts": int(len(nests)),
        "coverage": coverage,
        "common_nest_count_years_all_three": sorted(common_years or []),
        "n_common_years_all_three": len(common_years or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapppdr-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.mapppdr_dir, args.out_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
