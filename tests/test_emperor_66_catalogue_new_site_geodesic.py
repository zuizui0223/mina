"""Tests of literal 2024 colony coordinates versus pinned 66-site catalogue.

No geodesic distance is a penguin swimming route, no listed old colony
implies that colony was inhabited in the new site's first positive year.
"""
import csv
import importlib.util
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "emperor_66_geometry",
    ROOT / "scripts/audit_emperor_2024_new_sites_against_66_catalogue.py",
)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

RESULT = json.loads(
    (ROOT / "results/EMPEROR_66_CATALOGUE_NEWLY_REPORTED_SITES_GEODESIC_V1.json")
    .read_text(encoding="utf8")
)
FOUR = json.loads(
    (ROOT / "external/EMPEROR_FRETWELL_2024_SITE_DETECTION_EVIDENCE_V1.json")
    .read_text(encoding="utf8")
)


def test_published_geodesic_result_is_only_roster_support():
    assert RESULT["roster_size"] == 66
    assert RESULT["reported_site_count"] == 4
    assert RESULT["sites_beyond_100km_nearest_catalogue"] == 2
    assert RESULT["sites_within_414km_nearest_catalogue"] == 4
    assert RESULT["sites_with_repeated_surveyed_prenatal_zero"] == 0
    assert RESULT["new_causal_hypothesis_tested"] is False
    assert RESULT["fixed_catalogue_not_proven_historically_synchronous"]


def test_site_specific_names_and_approximate_nearest_distances():
    expected = {
        "LAZAREV_NORTH": ("Lazarev", 54.244),
        "VERLEGER_POINT": ("Cruzen Island", 124.721),
        "VANHOEFFEN": ("Karelin Bay", 63.227),
        "GIPPS_ICE_RISE": ("Dolleman", 215.343),
    }
    assert set(x["reported_site_id"] for x in RESULT["new_reported_sites"]) == set(expected)
    for row in RESULT["new_reported_sites"]:
        name, km = expected[row["reported_site_id"]]
        near = row["nearest_published_catalogue_site"]
        assert near["existing_catalogue_name"] == name
        assert math.isclose(near["geodesic_km"], km, abs_tol=.02)
        assert not row["prior_repeated_surveyed_negative_verified"]
        assert not row["nearest_site_verified_actively_breeding_same_year"]
        assert not row["nearest_site_current_fast_ice_accessibility_verified"]


def test_rounded_source_distance_not_validated_movement_path():
    assert math.isclose(M.haversine_km(-69.38,14.64,-69.7504,15.5493),
                        54.24407874551139, abs_tol=.001)
    assert M.haversine_km(-70,179.8,-70,-179.8) < 20
    assert M.haversine_km(-70,0,-70,0) == 0


def test_source_catalogue_fails_closed_when_sha_not_pinned():
    tiny = ("site_id,site_name,latitude,longitude\n"
            "X,Place,-68.0,50.0\n").encode()
    try:
        M.load_catalogue(tiny)
    except ValueError as err:
        assert "GIT_BLOB_SHA_MISMATCH" in str(err)
    else:
        raise AssertionError("Source checksum mismatch was not rejected")
    sites = M.load_catalogue(tiny, strict_full_roster=False)
    assert sites == [{"id":"X","name":"Place","lat":-68,"lon":50}]


def test_synthetic_choice_set_does_not_infer_success():
    sites=[{"id":str(i),"name":str(i),"lat":-60,"lon":i*5} for i in range(2)]
    tiny = {"four_newly_reported_sites":[
      {"id":n,"lat":-60,"lon":2+i,"first_reported_positive_year":2018,
       "repeated_prior_confirmed_absence_at_new_site":False}
      for i,n in enumerate("ABCD")]}
    outcome = M.audit(sites,tiny,expected_catalogue_size=2)
    assert outcome["reported_site_count"] == 4
    assert outcome["not_evidence_of_initial_colonization_or_actual_migration"] is True
    assert outcome["sites_with_repeated_surveyed_prenatal_zero"] == 0
