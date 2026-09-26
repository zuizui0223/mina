import csv

from mina.longterm import (
    add_community_traits,
    island_year_counts,
    site_year_species_matrix,
    transitions,
)


def _write(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def test_structural_zero_differs_from_missing_known_breeder(tmp_path):
    sites = tmp_path / "sites.csv"
    species = tmp_path / "species.csv"
    site_species = tmp_path / "site_species.csv"
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
    # Adelie and Chinstrap are known breeders; Gentoo is not.
    _write(site_species, ["site_id", "species_id"], [["s1", "a"], ["s1", "c"]])
    _write(
        obs,
        ["site_id", "species_id", "year", "type", "presence", "count"],
        [
            ["s1", "a", 2000, "nests", 1, 100],
            ["s1", "a", 2000, "nests", 1, 120],
            # Chinstrap is a known breeder but has no 2000 observation.
            # Gentoo is not a known breeder and should be structural zero.
        ],
    )

    matrix = site_year_species_matrix(obs, sites, species, site_species)
    by_species = {row["species"]: row for row in matrix}
    assert by_species["Adelie"]["count"] == 110
    assert by_species["Chinstrap"]["count"] is None
    assert by_species["Chinstrap"]["source"] == "missing_known_breeder"
    assert by_species["Gentoo"]["count"] == 0
    assert by_species["Gentoo"]["source"] == "structural_zero_not_known_breeder"

    panel, excluded = island_year_counts(matrix)
    assert panel == []
    assert excluded[0]["reason"] == "known_breeder_missing_at_observed_site"


def test_explicit_absence_completes_known_breeder(tmp_path):
    sites = tmp_path / "sites.csv"
    species = tmp_path / "species.csv"
    site_species = tmp_path / "site_species.csv"
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
    _write(site_species, ["site_id", "species_id"], [["s1", "a"], ["s1", "c"]])
    _write(
        obs,
        ["site_id", "species_id", "year", "type", "presence", "count"],
        [
            ["s1", "a", 2000, "nests", 1, 100],
            ["s1", "c", 2000, "nests", 0, ""],
        ],
    )

    matrix = site_year_species_matrix(obs, sites, species, site_species)
    panel, excluded = island_year_counts(matrix)
    assert excluded == []
    assert panel[0]["counts"] == {
        "Adelie": 100.0,
        "Chinstrap": 0.0,
        "Gentoo": 0.0,
    }


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
        "Adelie": {
            "bill_length_mm": 1,
            "bill_depth_mm": 1,
            "flipper_length_mm": 1,
            "body_mass_g": 1,
        },
        "Chinstrap": {
            "bill_length_mm": 2,
            "bill_depth_mm": 2,
            "flipper_length_mm": 2,
            "body_mass_g": 2,
        },
        "Gentoo": {
            "bill_length_mm": 4,
            "bill_depth_mm": 4,
            "flipper_length_mm": 4,
            "body_mass_g": 4,
        },
    }
    enriched = add_community_traits(panel, centroids)
    change = transitions(enriched, centroids)[0]
    assert change["primary_eligible"] is True
    assert abs(change["relative_abundance_turnover"] - 0.6) < 1e-12
    assert change["replacement_identity_max_abs_error"] < 1e-12
