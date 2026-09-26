import csv
from pathlib import Path

from mina.longterm import (
    add_community_traits,
    island_year_counts,
    site_year_species_counts,
    transitions,
)


def _write(path: Path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def test_explicit_absence_and_missing_species_are_distinct(tmp_path):
    sites = tmp_path / "sites.csv"
    species = tmp_path / "species.csv"
    obs = tmp_path / "obs.csv"
    _write(sites, ["site_id", "site_name"], [["s1", "Dream Island colony"]])
    _write(
        species,
        ["species_id", "common_name", "genus", "species"],
        [
            ["a", "Adelie", "Pygoscelis", "adeliae"],
            ["c", "Chinstrap", "Pygoscelis", "antarcticus"],
            ["g", "Gentoo", "Pygoscelis", "papua"],
        ],
    )
    _write(
        obs,
        ["site_id", "species_id", "year", "type", "presence", "count"],
        [
            ["s1", "a", 2000, "nests", 1, 100],
            ["s1", "a", 2000, "nests", 1, 120],
            ["s1", "c", 2000, "nests", 0, ""],
            # Gentoo intentionally unobserved.
        ],
    )
    counts = site_year_species_counts(obs, sites, species)
    adelie = next(row for row in counts if row["species"] == "Adelie")
    chinstrap = next(row for row in counts if row["species"] == "Chinstrap")
    assert adelie["count"] == 110
    assert chinstrap["count"] == 0
    panel, excluded = island_year_counts(counts)
    assert panel == []
    assert excluded[0]["missing_species"] == ["Gentoo"]


def test_cwm_change_equals_replacement_component():
    panel = [
        {
            "island": "Dream",
            "year": 2000,
            "counts": {"Adelie": 80.0, "Chinstrap": 20.0, "Gentoo": 0.0},
            "relative_abundance": {"Adelie": 0.8, "Chinstrap": 0.2, "Gentoo": 0.0},
            "total_count": 100.0,
            "site_coverage": ["s1"],
        },
        {
            "island": "Dream",
            "year": 2001,
            "counts": {"Adelie": 20.0, "Chinstrap": 20.0, "Gentoo": 60.0},
            "relative_abundance": {"Adelie": 0.2, "Chinstrap": 0.2, "Gentoo": 0.6},
            "total_count": 100.0,
            "site_coverage": ["s1"],
        },
    ]
    centroids = {
        "Adelie": {"bill_length_mm": 1, "bill_depth_mm": 1, "flipper_length_mm": 1, "body_mass_g": 1},
        "Chinstrap": {"bill_length_mm": 2, "bill_depth_mm": 2, "flipper_length_mm": 2, "body_mass_g": 2},
        "Gentoo": {"bill_length_mm": 4, "bill_depth_mm": 4, "flipper_length_mm": 4, "body_mass_g": 4},
    }
    enriched = add_community_traits(panel, centroids)
    change = transitions(enriched, centroids)[0]
    assert change["primary_eligible"] is True
    assert change["relative_abundance_turnover"] == 0.6
    assert change["replacement_identity_max_abs_error"] < 1e-12
