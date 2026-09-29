from mina.chick_key_audit import audit_rows


def test_nonoutcome_key_audit_distinguishes_duplicate_semantics():
    rows = [
        {
            "study_name": "S1",
            "time": "2001-01-10T00:00:00Z",
            "island": "LIT",
            "colony_code": "8.0",
            "season": 2000,
            "adult_pairs": 12.0,
            "census_time": "A",
        },
        {
            "study_name": "S2",
            "time": "2001-01-11T00:00:00Z",
            "island": "LIT",
            "colony_code": "8.0",
            "season": 2000,
            "adult_pairs": 12.0,
            "census_time": "B",
        },
        {
            "study_name": "S1",
            "time": "2001-01-10T00:00:00Z",
            "island": "HUM",
            "colony_code": "2.0",
            "season": 2000,
            "adult_pairs": 30.0,
            "census_time": "A",
        },
    ]
    out = audit_rows(rows)
    assert out["outcome_column_accessed"] is False
    assert out["coarse_duplicate_key_count"] == 1
    group = out["coarse_duplicate_groups"][0]
    assert group["key"]["island"] == "LIT"
    assert group["same_adult_pair_count"] is True
    assert group["n_distinct_study_names"] == 2
    assert group["n_distinct_times"] == 2
    assert out["candidate_key_collisions"]["coarse"]["n_duplicate_keys"] == 1
    assert out["candidate_key_collisions"]["plus_study"]["n_duplicate_keys"] == 0
    assert out["candidate_key_collisions"]["full_nonoutcome"]["n_duplicate_keys"] == 0
