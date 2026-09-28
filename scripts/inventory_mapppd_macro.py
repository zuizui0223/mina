#!/usr/bin/env python3
"""Inventory APBP/MAPPPD temporal coverage before macroecological modeling."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr

PINNED_MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"


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


def _int(value) -> int:
    return int(value) if pd.notna(value) else 0


def inventory(root: Path) -> dict[str, object]:
    data = root / "data"
    sites = _load(data / "sites.rda", "sites")
    species = _load(data / "species.rda", "species")
    site_species = _load(data / "site_species.rda", "site_species")
    obs = _load(data / "penguin_obs.rda", "penguin_obs")

    nest = obs[(obs["type"] == "nests") & obs["count"].notna()].copy()
    nest["year"] = pd.to_numeric(nest["year"], errors="coerce")

    lookup = species.set_index("species_id").to_dict(orient="index")
    species_summary: list[dict[str, object]] = []

    for species_id in sorted(site_species["species_id"].dropna().unique()):
        links = site_species[site_species["species_id"] == species_id]
        sub = nest[nest["species_id"] == species_id]

        years_by_site = (
            sub.dropna(subset=["year"])
            .groupby("site_id")["year"]
            .agg(lambda s: sorted(set(int(v) for v in s)))
        )

        n_years = years_by_site.map(len)
        spans = years_by_site.map(
            lambda ys: max(ys) - min(ys) if ys else 0
        )

        info = lookup.get(species_id, {})
        species_summary.append(
            {
                "species_id": str(species_id),
                "common_name": str(info.get("common_name", "")),
                "genus": str(info.get("genus", "")),
                "species": str(info.get("species", "")),
                "known_breeding_sites": int(links["site_id"].nunique()),
                "nest_count_records": int(len(sub)),
                "sites_with_nest_counts": int(sub["site_id"].nunique()),
                "sites_ge_2_years": int((n_years >= 2).sum()),
                "sites_ge_5_years": int((n_years >= 5).sum()),
                "sites_ge_10_years": int((n_years >= 10).sum()),
                "sites_ge_20_years": int((n_years >= 20).sum()),
                "sites_span_ge_10y": int((spans >= 10).sum()),
                "sites_span_ge_20y": int((spans >= 20).sum()),
                "sites_span_ge_30y": int((spans >= 30).sum()),
                "sites_ge5_and_span_ge10": int(
                    ((n_years >= 5) & (spans >= 10)).sum()
                ),
                "sites_ge10_and_span_ge20": int(
                    ((n_years >= 10) & (spans >= 20)).sum()
                ),
            }
        )

    richness = site_species.groupby("site_id")["species_id"].nunique()
    years = pd.to_numeric(obs["year"], errors="coerce").dropna()

    accuracy = (
        nest["accuracy"]
        .fillna("NA")
        .astype(str)
        .value_counts(dropna=False)
        .sort_index()
    )
    vantage = (
        nest["vantage"]
        .fillna("NA")
        .astype(str)
        .value_counts(dropna=False)
        .sort_index()
    )

    candidate = sum(x["sites_ge5_and_span_ge10"] for x in species_summary)
    strict = sum(x["sites_ge10_and_span_ge20"] for x in species_summary)

    return {
        "schema_version": 1,
        "inventory_id": "mina-mapppd-macro-inventory-v1",
        "mapppdr_commit": PINNED_MAPPPDR_COMMIT,
        "total_sites": int(len(sites)),
        "total_site_species_links": int(len(site_species)),
        "total_observation_records": int(len(obs)),
        "total_nest_count_records": int(len(nest)),
        "observation_year_min": int(years.min()) if len(years) else None,
        "observation_year_max": int(years.max()) if len(years) else None,
        "regions": int(sites["region"].nunique(dropna=True)),
        "ccamlr_units": int(sites["ccamlr_id"].nunique(dropna=True)),
        "site_species_richness": {
            "sites_with_1_species": int((richness == 1).sum()),
            "sites_with_2_species": int((richness == 2).sum()),
            "sites_with_3plus_species": int((richness >= 3).sum()),
            "max_species_per_site": int(richness.max()) if len(richness) else 0,
        },
        "species_summary": species_summary,
        "nest_accuracy_counts": {
            str(k): int(v) for k, v in accuracy.items()
        },
        "nest_vantage_counts": {
            str(k): int(v) for k, v in vantage.items()
        },
        "candidate_trend_gate": {
            "definition": (
                "at least 5 distinct nest-count years spanning at least 10 years"
            ),
            "total_site_species_units": int(candidate),
        },
        "stricter_trend_gate": {
            "definition": (
                "at least 10 distinct nest-count years spanning at least 20 years"
            ),
            "total_site_species_units": int(strict),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapppdr-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    result = inventory(args.mapppdr_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
