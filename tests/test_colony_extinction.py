from pathlib import Path

from mina.colony_extinction import (
    _trajectories,
    exchangeability_test,
    risk_sets,
)


def _write(tmp_path: Path) -> Path:
    path = tmp_path / "census.csv"
    rows = [
        "study_name,time,island_name,colony_code,num_breeding_pairs",
        "S,1991-11-01T00:00:00Z,CHR,1.0,1",
        "S,1991-11-01T00:00:00Z,CHR,1.1,12",
        "S,1991-11-01T00:00:00Z,CHR,2.0,20",
        "S,1992-11-01T00:00:00Z,CHR,1.0,0",
        "S,1992-11-01T00:00:00Z,CHR,1.1,10",
        "S,1992-11-01T00:00:00Z,CHR,2.0,18",
        "S,1993-11-01T00:00:00Z,CHR,1.0,0",
        "S,1993-11-01T00:00:00Z,CHR,1.1,0",
        "S,1993-11-01T00:00:00Z,CHR,2.0,15",
        "S,1994-11-01T00:00:00Z,CHR,1.0,0",
        "S,1994-11-01T00:00:00Z,CHR,1.1,8",
        "S,1994-11-01T00:00:00Z,CHR,2.0,14",
        "S,1995-11-01T00:00:00Z,CHR,1.0,0",
        "S,1995-11-01T00:00:00Z,CHR,1.1,7",
        "S,1995-11-01T00:00:00Z,CHR,2.0,13",
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


def test_fractional_colony_codes_are_distinct(tmp_path: Path) -> None:
    path = _write(tmp_path)
    traj = _trajectories(path)
    assert ("CHR", "1.0") in traj
    assert ("CHR", "1.1") in traj
    assert traj[("CHR", "1.0")][1991] == 1
    assert traj[("CHR", "1.1")][1991] == 12


def test_primary_event_requires_durable_zero_and_two_followups(tmp_path: Path) -> None:
    path = _write(tmp_path)
    sets = risk_sets(path)
    first = sets[("CHR", 1992)]
    status = {row["colony_code"]: row["event"] for row in first}
    assert status["1.0"] is True
    assert status["1.1"] is False
    # 1.1 is zero in 1993 but reappears in 1994, so it is not durable.
    later = sets[("CHR", 1993)]
    status_later = {row["colony_code"]: row["event"] for row in later}
    assert status_later["1.1"] is False


def test_exchangeability_detects_small_event_in_synthetic_panel(tmp_path: Path) -> None:
    path = _write(tmp_path)
    result = exchangeability_test(risk_sets(path), permutations=999, seed=7)
    assert result["observed_contrast"] < 0
    assert result["n_events"] == 1
