"""Expanded Palmer local-network abundance and community reassembly analysis.

The primary units are six true islands selected from outcome-blind APBP site
metadata within 20 km of Palmer Station. Biscoe Point is retained separately as
a non-island benchmark.

Two data lanes are kept separate:
1. species abundance: any valid site/species/year nest count can be used;
2. community composition: a site/year is used only when every focal species
   known to breed at that site has a numeric nest count or explicit absence.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median

from .longterm import FOCAL_SPECIES, TRAITS, canonical_species, species_trait_centroids

PRIMARY_ISLAND_SITES = (
    "TORG",
    "LITC",
    "HUMB",
    "CHIS",
    "CORM",
    "DREA",
)
BENCHMARK_SITES = ("BISC",)
ANALYSIS_SITES = PRIMARY_ISLAND_SITES + BENCHMARK_SITES


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


def _species_lookup(species_csv: str | Path) -> dict[str, str]:
    lookup: dict[str, str] = {}
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
            lookup[row["species_id"]] = label
    observed = set(lookup.values())
    missing = set(FOCAL_SPECIES) - observed
    if missing:
        raise ValueError(f"focal species missing from species table: {sorted(missing)}")
    return lookup


def _site_metadata(sites_csv: str | Path) -> dict[str, dict[str, str]]:
    result = {
        row["site_id"]: row
        for row in _read_csv(sites_csv)
        if row.get("site_id") in ANALYSIS_SITES
    }
    missing = set(ANALYSIS_SITES) - set(result)
    if missing:
        raise ValueError(f"analysis sites missing from sites table: {sorted(missing)}")
    return result


def breeding_membership(
    site_species_csv: str | Path,
    species_csv: str | Path,
) -> dict[str, set[str]]:
    lookup = _species_lookup(species_csv)
    result: dict[str, set[str]] = {site: set() for site in ANALYSIS_SITES}
    for row in _read_csv(site_species_csv):
        site = row.get("site_id", "")
        if site not in result:
            continue
        species = lookup.get(row.get("species_id", ""))
        if species is not None:
            result[site].add(species)
    return result


def observed_nest_counts(
    observations_csv: str | Path,
    sites_csv: str | Path,
    species_csv: str | Path,
    site_species_csv: str | Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Build one observed count per site/species/year.

    Numeric counts are summarized by their median. Explicit absence may produce
    zero. Positive count records for a species absent from APBP site_species are
    returned as membership conflicts and not silently reconciled.
    """
    sites = _site_metadata(sites_csv)
    species_lookup = _species_lookup(species_csv)
    members = breeding_membership(site_species_csv, species_csv)

    numeric: dict[tuple[str, str, int], list[float]] = defaultdict(list)
    explicit_absence: set[tuple[str, str, int]] = set()
    positive_presence: set[tuple[str, str, int]] = set()

    for row in _read_csv(observations_csv):
        site = row.get("site_id", "")
        if site not in ANALYSIS_SITES:
            continue
        if not str(row.get("type", "")).lower().startswith("nest"):
            continue
        species = species_lookup.get(row.get("species_id", ""))
        if species is None:
            continue
        try:
            year = int(float(row["year"]))
        except (KeyError, TypeError, ValueError):
            continue

        key = (site, species, year)
        presence = str(row.get("presence", "")).strip()
        if _finite(row.get("count")):
            value = float(row["count"])
            if value < 0:
                raise ValueError("negative nest count")
            numeric[key].append(value)
            if value > 0:
                positive_presence.add(key)
        elif presence in {"0", "0.0"}:
            explicit_absence.add(key)
        elif presence in {"1", "1.0"}:
            positive_presence.add(key)

    conflicts: list[dict[str, object]] = []
    for site, species, year in sorted(positive_presence):
        if species not in members.get(site, set()):
            conflicts.append(
                {
                    "site_id": site,
                    "site_name": sites[site]["site_name"],
                    "species": species,
                    "year": year,
                    "reason": "positive_nest_evidence_but_absent_from_site_species",
                }
            )

    output: list[dict[str, object]] = []
    keys = set(numeric) | explicit_absence
    for site, species, year in sorted(keys, key=lambda x: (x[0], x[1], x[2])):
        values = numeric.get((site, species, year), [])
        if values:
            count = float(median(values))
            source = "median_numeric_nest_count"
        else:
            count = 0.0
            source = "explicit_nest_absence"
        output.append(
            {
                "site_id": site,
                "site_name": sites[site]["site_name"],
                "site_role": (
                    "primary_true_island"
                    if site in PRIMARY_ISLAND_SITES
                    else "non_island_benchmark"
                ),
                "species": species,
                "year": year,
                "count": count,
                "source": source,
                "n_numeric_surveys": len(values),
            }
        )
    return output, conflicts


def abundance_summaries(
    observed_counts: list[dict[str, object]],
    membership: dict[str, set[str]],
) -> list[dict[str, object]]:
    by_series: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in observed_counts:
        by_series[(str(row["site_id"]), str(row["species"]))].append(row)

    output: list[dict[str, object]] = []
    for site in ANALYSIS_SITES:
        for species in FOCAL_SPECIES:
            rows = sorted(
                by_series.get((site, species), []),
                key=lambda row: int(row["year"]),
            )
            years = [int(row["year"]) for row in rows]
            counts = [float(row["count"]) for row in rows]
            known_breeder = species in membership.get(site, set())
            first_count = counts[0] if counts else None
            last_count = counts[-1] if counts else None
            log_ratio = None
            if first_count is not None and last_count is not None and first_count > 0 and last_count > 0:
                log_ratio = math.log(last_count / first_count)
            output.append(
                {
                    "site_id": site,
                    "site_role": (
                        "primary_true_island"
                        if site in PRIMARY_ISLAND_SITES
                        else "non_island_benchmark"
                    ),
                    "species": species,
                    "known_breeder": known_breeder,
                    "n_observed_years": len(rows),
                    "first_year": years[0] if years else None,
                    "last_year": years[-1] if years else None,
                    "calendar_span_years": years[-1] - years[0] if len(years) >= 2 else 0,
                    "first_count": first_count,
                    "last_count": last_count,
                    "net_count_change": (
                        last_count - first_count
                        if first_count is not None and last_count is not None
                        else None
                    ),
                    "log_last_over_first": log_ratio,
                    "observed_zero_years": [
                        int(row["year"]) for row in rows if float(row["count"]) == 0.0
                    ],
                    "descriptive_trajectory_eligible": len(rows) >= 5,
                    "trend_model_eligible": (
                        len(rows) >= 10 and (years[-1] - years[0] >= 8)
                        if len(years) >= 2
                        else False
                    ),
                }
            )
    return output


def community_panel(
    observed_counts: list[dict[str, object]],
    membership: dict[str, set[str]],
    centroids: dict[str, dict[str, float]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    observed: dict[tuple[str, str, int], float] = {
        (str(row["site_id"]), str(row["species"]), int(row["year"])): float(row["count"])
        for row in observed_counts
    }
    site_years: dict[str, set[int]] = defaultdict(set)
    for row in observed_counts:
        site_years[str(row["site_id"])].add(int(row["year"]))

    included: list[dict[str, object]] = []
    excluded: list[dict[str, object]] = []
    for site in ANALYSIS_SITES:
        for year in sorted(site_years.get(site, set())):
            known = membership.get(site, set())
            missing_known = [
                species
                for species in sorted(known)
                if (site, species, year) not in observed
            ]
            if missing_known:
                excluded.append(
                    {
                        "site_id": site,
                        "year": year,
                        "reason": "known_breeder_missing_same_year_nest_count",
                        "missing_species": missing_known,
                    }
                )
                continue

            counts = {
                species: (
                    observed[(site, species, year)]
                    if species in known
                    else 0.0
                )
                for species in FOCAL_SPECIES
            }
            total = sum(counts.values())
            if total <= 0:
                excluded.append(
                    {
                        "site_id": site,
                        "year": year,
                        "reason": "nonpositive_total_count",
                    }
                )
                continue

            relative = {
                species: counts[species] / total for species in FOCAL_SPECIES
            }
            cwm = {
                trait: sum(
                    relative[species] * centroids[species][trait]
                    for species in FOCAL_SPECIES
                )
                for trait in TRAITS
            }
            shannon = -sum(
                p * math.log(p) for p in relative.values() if p > 0
            )
            included.append(
                {
                    "site_id": site,
                    "site_role": (
                        "primary_true_island"
                        if site in PRIMARY_ISLAND_SITES
                        else "non_island_benchmark"
                    ),
                    "year": year,
                    "counts": counts,
                    "relative_abundance": relative,
                    "total_nests": total,
                    "effective_species_diversity": math.exp(shannon),
                    "community_weighted_traits": cwm,
                }
            )
    return included, excluded


def composition_transitions(
    panel: list[dict[str, object]],
    centroids: dict[str, dict[str, float]],
) -> list[dict[str, object]]:
    by_site: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in panel:
        by_site[str(row["site_id"])].append(row)
    output: list[dict[str, object]] = []
    for site, rows in sorted(by_site.items()):
        rows = sorted(rows, key=lambda row: int(row["year"]))
        for before, after in zip(rows, rows[1:]):
            p0 = before["relative_abundance"]
            p1 = after["relative_abundance"]
            turnover = 0.5 * sum(
                abs(float(p1[s]) - float(p0[s])) for s in FOCAL_SPECIES
            )
            delta_cwm = {
                trait: float(after["community_weighted_traits"][trait])
                - float(before["community_weighted_traits"][trait])
                for trait in TRAITS
            }
            replacement = {
                trait: sum(
                    (float(p1[s]) - float(p0[s])) * centroids[s][trait]
                    for s in FOCAL_SPECIES
                )
                for trait in TRAITS
            }
            output.append(
                {
                    "site_id": site,
                    "site_role": str(before["site_role"]),
                    "from_year": int(before["year"]),
                    "to_year": int(after["year"]),
                    "year_gap": int(after["year"]) - int(before["year"]),
                    "relative_abundance_turnover": turnover,
                    "delta_total_nests": float(after["total_nests"]) - float(before["total_nests"]),
                    "delta_cwm": delta_cwm,
                    "replacement_component": replacement,
                    "replacement_identity_max_abs_error": max(
                        abs(delta_cwm[t] - replacement[t]) for t in TRAITS
                    ),
                }
            )
    return output


def estimability_gate(
    summaries: list[dict[str, object]],
    panel: list[dict[str, object]],
) -> dict[str, object]:
    adelie = {
        str(row["site_id"]): row
        for row in summaries
        if row["species"] == "Adelie"
    }
    composition_years: dict[str, list[int]] = defaultdict(list)
    for row in panel:
        composition_years[str(row["site_id"])].append(int(row["year"]))

    by_site: dict[str, object] = {}
    for site in ANALYSIS_SITES:
        comp_years = sorted(composition_years.get(site, []))
        by_site[site] = {
            "site_role": (
                "primary_true_island"
                if site in PRIMARY_ISLAND_SITES
                else "non_island_benchmark"
            ),
            "adelie_n_observed_years": int(adelie[site]["n_observed_years"]),
            "adelie_trend_model_eligible": bool(adelie[site]["trend_model_eligible"]),
            "complete_composition_years": len(comp_years),
            "composition_first_year": comp_years[0] if comp_years else None,
            "composition_last_year": comp_years[-1] if comp_years else None,
            "composition_trajectory_eligible": len(comp_years) >= 5,
        }

    primary_adelie_trend_sites = [
        site
        for site in PRIMARY_ISLAND_SITES
        if by_site[site]["adelie_trend_model_eligible"]
    ]
    primary_composition_sites = [
        site
        for site in PRIMARY_ISLAND_SITES
        if by_site[site]["composition_trajectory_eligible"]
    ]
    return {
        "by_site": by_site,
        "primary_adelie_trend_sites": primary_adelie_trend_sites,
        "primary_composition_trajectory_sites": primary_composition_sites,
        "multi_island_adelie_trend_estimable": len(primary_adelie_trend_sites) >= 3,
        "multi_island_composition_reassembly_estimable": len(primary_composition_sites) >= 3,
    }


def analyze_network(
    palmer_raw: str | Path,
    sites_csv: str | Path,
    species_csv: str | Path,
    site_species_csv: str | Path,
    observations_csv: str | Path,
) -> dict[str, object]:
    centroids = species_trait_centroids(palmer_raw)
    membership = breeding_membership(site_species_csv, species_csv)
    observed, conflicts = observed_nest_counts(
        observations_csv,
        sites_csv,
        species_csv,
        site_species_csv,
    )
    if conflicts:
        raise ValueError(
            "APBP breeding-membership conflicts with positive nest evidence: "
            + json.dumps(conflicts, sort_keys=True)
        )
    summaries = abundance_summaries(observed, membership)
    panel, excluded = community_panel(observed, membership, centroids)
    transitions = composition_transitions(panel, centroids)
    gate = estimability_gate(summaries, panel)

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-local-network-stage2-v1",
        "status": "abundance_opened_under_frozen_stage2_rules",
        "primary_true_island_sites": list(PRIMARY_ISLAND_SITES),
        "benchmark_sites": list(BENCHMARK_SITES),
        "breeding_membership": {
            site: sorted(membership.get(site, set())) for site in ANALYSIS_SITES
        },
        "species_trait_centroids": centroids,
        "observed_nest_count_rows": observed,
        "abundance_summaries": summaries,
        "community_panel": panel,
        "excluded_community_site_years": excluded,
        "composition_transitions": transitions,
        "estimability_gate": gate,
        "rules": {
            "species_abundance_lane_requires_full_community": False,
            "community_lane_requires_all_known_breeders_same_year": True,
            "nonbreeder_is_structural_zero": True,
            "known_breeder_without_same_year_count_is_missing": True,
            "numeric_replicates_summary": "median",
            "explicit_absence_is_zero": True,
            "positive_count_vs_site_species_conflict": "fail_closed",
            "historical_within_species_trait_change_inferred": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--palmer-raw", required=True, type=Path)
    parser.add_argument("--sites", required=True, type=Path)
    parser.add_argument("--species", required=True, type=Path)
    parser.add_argument("--site-species", required=True, type=Path)
    parser.add_argument("--observations", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    result = analyze_network(
        args.palmer_raw,
        args.sites,
        args.species,
        args.site_species,
        args.observations,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
