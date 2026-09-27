import math

import numpy as np

from mina.hierarchical_variability import (
    colony_roster_audit,
    covariance_synchrony,
    nested_raw_decomposition,
    wang_loreau_raw,
)


def test_wang_loreau_identical_series_are_synchronous():
    result = wang_loreau_raw(
        {
            "a": np.asarray([1.0, 2.0, 3.0, 4.0]),
            "b": np.asarray([1.0, 2.0, 3.0, 4.0]),
        }
    )
    assert math.isclose(result["beta_spatial"], 1.0, abs_tol=1e-12)
    assert math.isclose(result["phi_synchrony"], 1.0, abs_tol=1e-12)


def test_covariance_synchrony_beta_phi_identity():
    result = covariance_synchrony(
        {
            "a": np.asarray([-1.0, 0.0, 1.0, 2.0]),
            "b": np.asarray([2.0, 1.0, 0.0, 0.0]),
        }
    )
    assert result["beta_spatial"] > 1.0
    assert 0.0 < result["phi_synchrony"] < 1.0
    assert math.isclose(
        result["beta_spatial"] * result["phi_synchrony"],
        1.0,
        abs_tol=1e-12,
    )


def test_nested_scale_transition_multiplies_exactly():
    rows = []
    values = {
        "A": {
            "1": [8.0, 7.0, 6.0, 5.0],
            "2": [2.0, 3.0, 4.0, 4.0],
        },
        "B": {
            "1": [6.0, 5.0, 4.0, 3.0],
            "2": [3.0, 4.0, 5.0, 5.0],
        },
    }
    for island, colonies in values.items():
        for code, series in colonies.items():
            for year, count in zip(range(2000, 2004), series):
                rows.append(
                    {
                        "island": island,
                        "year": year,
                        "colony_code": code,
                        "breeding_pairs": count,
                    }
                )
    audit = {
        island: {
            "roster_stable": True,
            "intersection_codes": sorted(colonies),
        }
        for island, colonies in values.items()
    }
    result = nested_raw_decomposition(
        rows,
        ("A", "B"),
        tuple(range(2000, 2004)),
        audit,
    )
    assert math.isclose(
        result["beta_total_subcolony_to_archipelago"],
        result["beta_within_islands"] * result["beta_among_islands"],
        abs_tol=1e-12,
    )
    assert result["multiplicative_identity_error"] < 1e-12


def test_roster_audit_detects_code_change():
    rows = []
    for year in (2000, 2001, 2002):
        for code in ("1", "2"):
            rows.append(
                {
                    "island": "COR",
                    "year": year,
                    "colony_code": code,
                    "breeding_pairs": 1.0,
                }
            )
    for year in (2000, 2001):
        for code in ("1", "2"):
            rows.append(
                {
                    "island": "CHR",
                    "year": year,
                    "colony_code": code,
                    "breeding_pairs": 1.0,
                }
            )
    rows.append(
        {
            "island": "CHR",
            "year": 2002,
            "colony_code": "1",
            "breeding_pairs": 1.0,
        }
    )
    audit = colony_roster_audit(rows)
    assert audit["COR"]["roster_stable"] is True
    assert audit["CHR"]["roster_stable"] is False
    assert audit["CHR"]["change_years"] == [2002]
