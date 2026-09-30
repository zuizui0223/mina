from __future__ import annotations

import csv
from pathlib import Path

from mina.ross_carrier_schema import audit


def _write(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_location_gate_passes_without_overcalling_breeding_propensity(tmp_path: Path) -> None:
    resight = tmp_path / "resight.csv"
    _write(
        resight,
        ["BandNumber", "ResightDate", "Colony", "Note"],
        [
            {"BandNumber": "A1", "ResightDate": "2001-12-01", "Colony": "RO", "Note": ""},
            {"BandNumber": "A1", "ResightDate": "2002-12-01", "Colony": "RO", "Note": ""},
        ],
    )
    result = audit(resight)
    assert result["gates"]["stable_individual_identity"]
    assert result["gates"]["conditional_location_transition"]
    assert not result["gates"]["breeding_propensity_model"]


def test_breeding_propensity_requires_state_and_effort(tmp_path: Path) -> None:
    resight = tmp_path / "resight.csv"
    band = tmp_path / "band.csv"
    _write(
        resight,
        ["BirdID", "Season", "BreedingColony", "ReproductiveState", "SurveyEffort"],
        [
            {"BirdID": "A1", "Season": 2001, "BreedingColony": "RO", "ReproductiveState": "BR", "SurveyEffort": 10},
            {"BirdID": "A1", "Season": 2002, "BreedingColony": "RO", "ReproductiveState": "NB", "SurveyEffort": 12},
        ],
    )
    _write(
        band,
        ["BirdID", "BandingDate", "AgeAtBanding"],
        [{"BirdID": "A1", "BandingDate": "1998-12-01", "AgeAtBanding": 0}],
    )
    result = audit(resight, band)
    assert result["gates"]["known_age_filter"]
    assert result["gates"]["breeding_propensity_model"]


def test_missing_effort_blocks_breeding_propensity(tmp_path: Path) -> None:
    resight = tmp_path / "resight.csv"
    _write(
        resight,
        ["BandID", "Year", "Site", "BreedingStatus"],
        [{"BandID": "A1", "Year": 2001, "Site": "RO", "BreedingStatus": "BR"}],
    )
    result = audit(resight)
    assert result["gates"]["conditional_location_transition"]
    assert not result["gates"]["breeding_propensity_model"]
