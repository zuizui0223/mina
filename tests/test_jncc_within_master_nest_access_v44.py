"""Synthetic checks of cross-species survey metadata matching."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_jncc_within_master_nest_access_v44 as audit


def mock_panel(species, unit="AON", year=2000, lat=56.0):
    key = (species, "Scotland", "example_master", unit)
    rows = [
        ({"species": species, "country": "Scotland", "master": "example_master",
          "unit": unit, "year_2000": year, "year_recent": 2018,
          "lat": lat, "lon": -5.0, "site_id": str(j)}, {})
        for j in (1, 2, 3)
    ]
    return audit.source_panel_info(key, rows)


def test_all_original_species_have_one_independent_trait_assignment():
    assert len(audit.TRAITS) == 17
    assert len(audit.ACCESSIBLE) == 10
    assert len(audit.CLIFF) == 2
    assert len(audit.UNCERTAIN) == 5


def test_matching_units_times_and_locations_are_eligible():
    a = mock_panel("Common Tern")
    b = mock_panel("Black-legged Kittiwake")
    q = audit.pair_quality(a, b)
    assert q["source_metadata_primary_pair"]
    assert q["overlapping_original_Site_ID_n"] == 3


def test_different_count_units_do_not_match():
    a = mock_panel("Common Tern", unit="AON")
    b = mock_panel("Common Guillemot", unit="IND")
    assert not audit.pair_quality(a, b)["source_metadata_primary_pair"]


def test_different_calendar_years_or_far_geography_are_ineligible():
    a = mock_panel("Common Tern")
    b = mock_panel("Black-legged Kittiwake", year=2003)
    assert not audit.pair_quality(a, b)["source_metadata_primary_pair"]
    c = mock_panel("Black-legged Kittiwake", lat=58.0)
    assert not audit.pair_quality(a, c)["source_metadata_primary_pair"]
