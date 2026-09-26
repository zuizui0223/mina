"""Conservative long-term island community reassembly from APBP/MAPPPD counts."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median

FOCAL_SPECIES = ("Adelie", "Chinstrap", "Gentoo")
ISLANDS = ("Biscoe", "Dream", "Torgersen")
TRAITS = {
    "bill_length_mm": "Culmen Length (mm)",
    "bill_depth_mm": "Culmen Depth (mm)",
    "flipper_length_mm": "Flipper Length (mm)",
    "body_mass_g": "Body Mass (g)",
}


def _read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def canonical_species(text: str) -> str | None:
    lower = text.lower()
    if "adel" in lower:
        return "Adelie"
    if "chinstrap" in lower or "antarcticus" in lower:
        return "Chinstrap"
    if "gentoo" in lower or "papua" in lower:
        return "Gentoo"
    return None


def canonical_island(site_name: str) -> str | None:
    lower = site_name.lower()
    for island in ISLANDS:
        if island.lower() in lower:
            return island
    return None


def species_trait_centroids(raw_palmer_csv: str | Path) -> dict[str, dict[str, float]]:
    """Sex-balanced species trait centroids from the pinned Palmer raw table."""
    rows = _read_csv(raw_palmer_csv)
    out: dict[str, dict[str, float]] = {}
    for species in FOCAL_SPECIES:
        subset = [
            row
            for row in rows
            if canonical_species(row.get("Species", "")) == species
            and row.get("Sex") in {"FEMALE", "MALE"}
        ]
        trait_values: dict[str, float] = {}
        for short, column in TRAITS.items():
            sex_means = []
            for sex in ("FEMALE", "MALE"):
                values = [
                    float(row[column])
                    for row in subset
                    if row["Sex"] == sex and _finite(row.get(column))
                ]
                if not values:
                    raise ValueError(f"missing {sex} {species} values for {column}")
                sex_means.append(sum(values) / len(values))
            trait_values[short] = sum(sex_means) / 2.0
        out[species] = trait_values
    return out


def _join_metadata(
    sites_csv: str | Path,
    species_csv: str | Path,
) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    sites = {row["site_id"]: row for row in _read_csv(sites_csv)}
    species_lookup: dict[str, str] = {}
    for row in _read_csv(species_csv):
        label = canonical_species(
            " ".join(
                [
                    row.get("common_name", ""),
                    row.get("genus", ""),
                    row.get("species", ""),
                ]
            )
        )
        if label is not None:
            species_lookup[row["species_id"]] = label
    return sites, species_lookup


def site_year_species_counts(
    observations_csv: str | Path,
    sites_csv: str | Path,
    species_csv: str | Path,
) -> list[dict[str, object]]:
    """Return one nest-count estimate per site/species/year.

    Positive presence-only records remain missing. Explicit nest absence
    (presence == 0) may contribute a zero. Multiple numeric surveys are
    summarized by the median, avoiding outcome-dependent selection.
    """
    sites, species_lookup = _join_metadata(sites_csv, species_csv)
    grouped: dict[tuple[str, str, int], list[float]] = defaultdict(list)
    explicit_absence: set[tuple[str, str, int]] = set()

    for row in _read_csv(observations_csv):
        if not str(row.get("type", "")).lower().startswith("nest"):
            continue
        site = sites.get(row.get("site_id", ""))
        species = species_lookup.get(row.get("species_id", ""))
        if site is None or species is None:
            continue
        island = canonical_island(site.get("site_name", ""))
        if island is None:
            continue
        try:
            year = int(float(row["year"]))
        except (KeyError, TypeError, ValueError):
            continue
        key = (row["site_id"], species, year)
        if _finite(row.get("count")):
            value = float(row["count"])
            if value < 0:
                raise ValueError("negative count")
            grouped[key].append(value)
        elif str(row.get("presence", "")).strip() in {"0", "0.0"}:
            explicit_absence.add(key)

    output: list[dict[str, object]] = []
    all_keys = set(grouped) | explicit_absence
    for site_id, species, year in sorted(all_keys, key=lambda x: (x[2], x[0], x[1])):
        values = grouped.get((site_id, species, year), [])
        if values:
            count = float(median(values))
            source = "median_numeric_nest_count"
        else:
            count = 0.0
            source = "explicit_nest_absence"
        site = sites[site_id]
        output.append(
            {
                "site_id": site_id,
                "site_name": site["site_name"],
                "island": canonical_island(site["site_name"]),
                "species": species,
                "year": year,
                "count": count,
                "source": source,
                "n_numeric_surveys": len(values),
            }
        )
    return output


def island_year_counts(
    site_counts: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Aggregate to islands without silently imputing unobserved species."""
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in site_counts:
        groups[(str(row["island"]), int(row["year"]))].append(row)

    included: list[dict[str, object]] = []
    excluded: list[dict[str, object]] = []
    for (island, year), rows in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1])):
        by_species: dict[str, float] = {}
        for species in FOCAL_SPECIES:
            values = [float(row["count"]) for row in rows if row["species"] == species]
            if values:
                by_species[species] = sum(values)
        missing = [species for species in FOCAL_SPECIES if species not in by_species]
        sites = sorted({str(row["site_id"]) for row in rows})
        if missing:
            excluded.append(
                {
                    "island": island,
                    "year": year,
                    "reason": "species_observation_incomplete",
                    "missing_species": missing,
                    "site_coverage": sites,
                }
            )
            continue
        total = sum(by_species.values())
        if total <= 0:
            excluded.append(
                {
                    "island": island,
                    "year": year,
                    "reason": "nonpositive_total_count",
                    "site_coverage": sites,
                }
            )
            continue
        included.append(
            {
                "island": island,
                "year": year,
                "counts": by_species,
                "relative_abundance": {
                    species: by_species[species] / total for species in FOCAL_SPECIES
                },
                "total_count": total,
                "site_coverage": sites,
            }
        )
    return included, excluded


def add_community_traits(
    panel: list[dict[str, object]],
    centroids: dict[str, dict[str, float]],
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in panel:
        p = row["relative_abundance"]
        cwm = {
            trait: sum(
                float(p[species]) * float(centroids[species][trait])
                for species in FOCAL_SPECIES
            )
            for trait in TRAITS
        }
        shannon = -sum(
            float(p[species]) * math.log(float(p[species]))
            for species in FOCAL_SPECIES
            if float(p[species]) > 0
        )
        out.append(
            {
                **row,
                "community_weighted_traits": cwm,
                "effective_species_diversity": math.exp(shannon),
            }
        )
    return out


def transitions(
    panel: list[dict[str, object]],
    centroids: dict[str, dict[str, float]],
) -> list[dict[str, object]]:
    by_island: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in panel:
        by_island[str(row["island"])].append(row)
    out: list[dict[str, object]] = []
    for island, rows in sorted(by_island.items()):
        rows = sorted(rows, key=lambda row: int(row["year"]))
        for before, after in zip(rows, rows[1:]):
            p0 = before["relative_abundance"]
            p1 = after["relative_abundance"]
            turnover = 0.5 * sum(
                abs(float(p1[s]) - float(p0[s])) for s in FOCAL_SPECIES
            )
            delta = {
                trait: float(after["community_weighted_traits"][trait])
                - float(before["community_weighted_traits"][trait])
                for trait in TRAITS
            }
            replacement = {
                trait: sum(
                    (float(p1[s]) - float(p0[s])) * float(centroids[s][trait])
                    for s in FOCAL_SPECIES
                )
                for trait in TRAITS
            }
            identity_error = max(abs(delta[t] - replacement[t]) for t in TRAITS)
            coverage_stable = before["site_coverage"] == after["site_coverage"]
            out.append(
                {
                    "island": island,
                    "from_year": int(before["year"]),
                    "to_year": int(after["year"]),
                    "year_gap": int(after["year"]) - int(before["year"]),
                    "relative_abundance_turnover": turnover,
                    "delta_cwm": delta,
                    "replacement_component": replacement,
                    "replacement_identity_max_abs_error": identity_error,
                    "site_coverage_stable": coverage_stable,
                    "primary_eligible": bool(coverage_stable),
                }
            )
    return out


def analyze_longterm(
    palmer_raw: str | Path,
    sites_csv: str | Path,
    species_csv: str | Path,
    observations_csv: str | Path,
) -> dict[str, object]:
    centroids = species_trait_centroids(palmer_raw)
    site_counts = site_year_species_counts(observations_csv, sites_csv, species_csv)
    panel, excluded = island_year_counts(site_counts)
    panel = add_community_traits(panel, centroids)
    change = transitions(panel, centroids)
    return {
        "schema_version": 1,
        "analysis_id": "mina-longterm-island-community-reassembly-v1",
        "status": "longterm_data_opened_under_frozen_rules",
        "trait_centroids": centroids,
        "site_year_species_count_rows": len(site_counts),
        "island_year_panel": panel,
        "excluded_island_years": excluded,
        "transitions": change,
        "primary_transition_count": sum(bool(row["primary_eligible"]) for row in change),
        "rules": {
            "count_type": "nests/breeding pairs only",
            "positive_presence_without_count": "missing",
            "explicit_nest_absence": "zero",
            "within_site_species_year_replicates": "median",
            "missing_species": "exclude island-year; never silently zero",
            "primary_transition_requires_identical_site_coverage": True,
            "historical_within_species_trait_change_inferred": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--palmer-raw", required=True, type=Path)
    parser.add_argument("--sites", required=True, type=Path)
    parser.add_argument("--species", required=True, type=Path)
    parser.add_argument("--observations", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = analyze_longterm(
        args.palmer_raw, args.sites, args.species, args.observations
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
