from __future__ import annotations

import csv
from pathlib import Path

from mina.small_group_reproductive_success_v2 import (
    build_groups,
    conditional_size_effect,
    source_paired_rows,
    study_start_year,
)


def _write(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def test_study_name_is_season_key():
    assert study_start_year("PAL9697") == 1996
    assert study_start_year("PAL0102") == 2001
    assert study_start_year("bad") is None


def test_source_pairing_uses_independent_adult_denominator(tmp_path: Path):
    adult = tmp_path / "adult.csv"
    chick = tmp_path / "chick.csv"
    _write(
        adult,
        ["study_name","time","island_name","colony_code","num_breeding_pairs"],
        [
            {"study_name":"PAL9798","time":"1997-11-01","island_name":"CHR","colony_code":"1","num_breeding_pairs":10},
            {"study_name":"PAL9798","time":"1997-11-01","island_name":"CHR","colony_code":"2","num_breeding_pairs":20},
            {"study_name":"PAL9798","time":"1997-11-01","island_name":"CHR","colony_code":"3","num_breeding_pairs":30},
            {"study_name":"PAL9798","time":"1997-11-01","island_name":"CHR","colony_code":"4","num_breeding_pairs":40},
        ],
    )
    _write(
        chick,
        ["study_name","time","island_name","colony_code","num_breeding_pairs","num_chicks","census_time"],
        [
            # Calendar-derived season says 1996, but study_name says 1997.
            {"study_name":"PAL9798","time":"1997-01-20","island_name":"CHR","colony_code":"1","num_breeding_pairs":1,"num_chicks":5,"census_time":"1200"},
            {"study_name":"PAL9798","time":"1998-01-20","island_name":"CHR","colony_code":"2","num_breeding_pairs":1,"num_chicks":15,"census_time":"1200"},
            {"study_name":"PAL9798","time":"1998-01-20","island_name":"CHR","colony_code":"3","num_breeding_pairs":1,"num_chicks":30,"census_time":"1200"},
            {"study_name":"PAL9798","time":"1998-01-20","island_name":"CHR","colony_code":"4","num_breeding_pairs":1,"num_chicks":50,"census_time":"1200"},
        ],
    )
    rows, diag = source_paired_rows(chick, adult)
    assert [r["pairs"] for r in rows] == [10.0,20.0,30.0,40.0]
    assert diag["date_conflict_rows"] == 1
    groups = build_groups(rows)
    assert len(groups) == 1
    assert groups[0]["study_name"] == "PAL9798"


def test_effect_is_positive_when_chicks_shift_to_larger_groups():
    rows = []
    for island, study in (("CHR","PAL0001"),("COR","PAL0001"),("CHR","PAL0102"),("COR","PAL0102")):
        pairs = [10.0,20.0,40.0,80.0]
        rates = [0.4,0.6,0.9,1.2]
        for i,(n,r) in enumerate(zip(pairs,rates)):
            rows.append({
                "island":island,
                "study_name":study,
                "colony_code":str(i),
                "pairs":n,
                "chicks":float(round(n*r)),
                "date_conflict":False,
                "biologically_inconsistent_ratio":False,
            })
    groups = build_groups(rows)
    assert all(float(g["score"]) > 0 for g in groups)
    effect = conditional_size_effect(groups)
    assert effect["beta_per_within_group_sd_log1p_pairs"] > 0
    assert effect["multiplicative_per_pair_success_per_1sd_larger_group"] > 1
