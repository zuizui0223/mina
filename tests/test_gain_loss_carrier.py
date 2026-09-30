from __future__ import annotations

import pytest

from mina.gain_loss_carrier import (
    gain_loss_panel,
    holm_two,
)


def _adults() -> list[dict[str, object]]:
    rows=[]
    series={
        "1":[10,12,18],
        "2":[20,18,12],
        "3":[30,31,31],
    }
    for colony,counts in series.items():
        for year,count in zip((2000,2001,2002),counts):
            rows.append({
                "island":"TOR",
                "colony":colony,
                "year":year,
                "adult_pairs":float(count),
            })
    return rows


def _performance() -> list[dict[str, object]]:
    return [
        {"island":"TOR","colony":"1","season":2000,"state":1.0,"total_chicks":30.0},
        {"island":"TOR","colony":"2","season":2000,"state":-1.0,"total_chicks":30.0},
        {"island":"TOR","colony":"3","season":2000,"state":0.0,"total_chicks":30.0},
    ]


def test_gain_loss_decomposition_reconstructs_relative_log_growth() -> None:
    panel=gain_loss_panel(_adults(),_performance())
    assert len(panel)==3
    for row in panel:
        reconstructed=(
            float(row["gain_relative"])
            + float(row["loss_avoidance_relative"])
        )
        assert reconstructed == pytest.approx(float(row["relative_growth"]))


def test_positive_net_addition_is_strict_count_lower_bound() -> None:
    panel=gain_loss_panel(_adults(),_performance())
    lookup={str(r["colony"]):r for r in panel}
    assert lookup["1"]["lplus_pairs"] == 6.0
    assert lookup["2"]["lplus_pairs"] == 0.0
    assert lookup["3"]["lplus_pairs"] == 0.0


def test_holm_two_adjusts_smaller_and_larger_monotonically() -> None:
    a,b=holm_two(0.01,0.04)
    assert a == pytest.approx(0.02)
    assert b == pytest.approx(0.04)

    a,b=holm_two(0.04,0.01)
    assert a == pytest.approx(0.04)
    assert b == pytest.approx(0.02)


def test_minimum_prior_size_filters_outcome_interval_start() -> None:
    adults=_adults()
    performance=_performance()
    panel=gain_loss_panel(
        adults,
        performance,
        minimum_prior_size=20.0,
    )
    assert {str(r["colony"]) for r in panel} == {"3"}
