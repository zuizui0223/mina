import csv

from mina.network import (
    abundance_summaries,
    breeding_membership,
    community_panel,
    observed_nest_counts,
)


def _write(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def _tables(tmp_path):
    sites = tmp_path / "sites.csv"
    species = tmp_path / "species.csv"
    membership = tmp_path / "site_species.csv"
    obs = tmp_path / "obs.csv"

    analysis_sites = [
        ("TORG", "Torgersen Island"),
        ("LITC", "Litchfield Island"),
        ("HUMB", "Humble Island"),
        ("CHIS", "Christine Island"),
        ("CORM", "Cormorant Island"),
        ("DREA", "Dream Island"),
        ("BISC", "Biscoe Point"),
    ]
    _write(
        sites,
        ["site_id", "site_name"],
        analysis_sites,
    )
    _write(
        species,
        ["species_id", "common_name", "genus", "species"],
        [
            ["a", "adelie penguin", "Pygoscelis", "adeliae"],
            ["c", "chinstrap penguin", "Pygoscelis", "antarcticus"],
            ["g", "gentoo penguin", "Pygoscelis", "papua"],
        ],
    )
    _write(
        membership,
        ["site_id", "species_id"],
        [
            ["DREA", "a"],
            ["DREA", "c"],
            ["BISC", "a"],
            ["BISC", "g"],
            ["TORG", "a"],
            ["LITC", "a"],
            ["HUMB", "a"],
            ["CHIS", "a"],
            ["CORM", "a"],
        ],
    )
    return sites, species, membership, obs


def test_abundance_lane_keeps_partial_community_year(tmp_path):
    sites, species, membership_csv, obs = _tables(tmp_path)
    _write(
        obs,
        ["site_id", "species_id", "year", "type", "presence", "count"],
        [
            ["DREA", "a", 2000, "nests", 1, 100],
            # Chinstrap is a known breeder, but not counted in 2000.
            ["DREA", "a", 2001, "nests", 1, 90],
            ["DREA", "c", 2001, "nests", 1, 10],
        ],
    )
    observed, conflicts = observed_nest_counts(
        obs, sites, species, membership_csv
    )
    assert conflicts == []

    members = breeding_membership(membership_csv, species)
    summaries = abundance_summaries(observed, members)
    adelie = next(
        row for row in summaries
        if row["site_id"] == "DREA" and row["species"] == "Adelie"
    )
    assert adelie["n_observed_years"] == 2

    centroids = {
        "Adelie": {trait: 1.0 for trait in ("bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g")},
        "Chinstrap": {trait: 2.0 for trait in ("bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g")},
        "Gentoo": {trait: 4.0 for trait in ("bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g")},
    }
    panel, excluded = community_panel(observed, members, centroids)
    assert [row["year"] for row in panel if row["site_id"] == "DREA"] == [2001]
    assert any(
        row["site_id"] == "DREA"
        and row["year"] == 2000
        and row["reason"] == "known_breeder_missing_same_year_nest_count"
        for row in excluded
    )


def test_positive_count_missing_membership_is_conflict(tmp_path):
    sites, species, membership_csv, obs = _tables(tmp_path)
    _write(
        obs,
        ["site_id", "species_id", "year", "type", "presence", "count"],
        [["TORG", "g", 2000, "nests", 1, 5]],
    )
    _, conflicts = observed_nest_counts(obs, sites, species, membership_csv)
    assert len(conflicts) == 1
    assert conflicts[0]["species"] == "Gentoo"
