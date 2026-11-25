"""Synthetic NOAA camera observation and official Zenodo manifest feasibility."""
import importlib.util
from pathlib import Path
import pytest

SRC=Path(__file__).resolve().parents[1]/"scripts/audit_noaa_zenodo_visitor_to_first_egg_source_v19.py"
spec=importlib.util.spec_from_file_location("p_vis",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_cameras_are_selected_nests_not_all_penguin_arrivals():
    z=m.evaluate()
    f=z["identifiability_flags"]
    assert f["NOAA_camera_focal_selected_after_two_adults"]
    assert f["NOAA_focal_attendance_unknown_day_is_not_unseen_immigrant"]
    assert f["Zenodo_nonbreeders_not_followed_to_individual_first_egg"]
    assert f["Zenodo_2016_17_2_stations_both_King_George_Island"]
    assert not f["observed_all_arrivals_denominator"]
    assert not f["matched_individual_visit_to_own_egg"]
    assert not z["proposed_visitor_to_breeding_probability_denominator_available"]
    assert z["NOAA_cam_source_bird_records_loaded"]==0
    assert z["Zenodo_tracking_source_bird_records_loaded"]==0

def test_noaa_4_and_5_are_not_numbers_of_attending_penguin_adults():
    assert m.classify_attendance_maxn(4)=="CRECHE_TERMINAL_EVENT_NOT_ADULT_COUNT"
    assert m.classify_attendance_maxn(5)=="CONFIRMED_NEST_FAILURE_TERMINAL_EVENT_NOT_ADULT_COUNT"
    assert m.classify_attendance_maxn(0)=="NO_ADULT_VISIBLE_AT_SELECTED_NEST"
    assert m.classify_attendance_maxn(None)=="UNKNOWN_OR_MISSING_ATTENDANCE"
    assert m.classify_attendance_maxn(3)=="HOLD_UNDOCUMENTED_CODE"

def test_official_zenodo_manifest_checksum_without_telemetry_read():
    x={"id":5036339,"files":[{"key":"data.csv","size":5810000,
                "checksum":"md5:d4ca95fd92096e58ffbffff84250d669"}]}
    z=m.evaluate(x)
    assert z["source_access_Zenodo_metadata"]=="VERIFIED_OFFICIAL_MANIFEST_CHECKSUM_ONLY"
    assert z["Zenodo_official_file_manifest"][0]["MD5_matches_published_data_csv"]
    assert z["observed_penguin_eggs_matched_across_sources"]==0
    assert z["Ecology_PR189_scientific_freeze_preserved"]

def test_publisher_md5_mismatch_must_fail_not_silent():
    with pytest.raises(ValueError,match="MD5"):
        m.validate_zenodo_record({"id":5036339,"files":[
            {"key":"data.csv","checksum":"md5:"+"0"*32}]})

def test_no_accidental_identity_join_with_nonbreeder_at_sea():
    z=m.evaluate()
    assert not z["identifiability_flags"]["new_causal_source_supply_or_reproductive_constraint_test"]
    assert not z["proposed_visitor_to_breeding_probability_numerator_available"]
    assert z["official_USAP_PR142_not_unlocked"]
