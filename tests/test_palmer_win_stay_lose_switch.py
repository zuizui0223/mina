from __future__ import annotations

import math

import pytest

from mina.win_stay_lose_switch import (
    build_p1_panel,
    build_p2_performance,
    fit_hinge,
)


def adults_fixture():
    rows=[]
    for island,base in (("A",10),("B",20),("C",30)):
        for colony,mult in (("1",1.0),("2",2.0),("3",3.0)):
            for year in (2000,2001,2002):
                rows.append({
                    "island":island,
                    "colony":colony,
                    "year":year,
                    "adult_pairs":float(base*mult + (year-2000)),
                })
    return rows


def test_p1_poor_breeder_share_is_pair_weighted():
    adults=adults_fixture()
    performance=[
        {"island":"A","colony":"1","season":2000,"state":-1.0},
        {"island":"A","colony":"2","season":2000,"state":+0.5},
        {"island":"A","colony":"3","season":2000,"state":-0.2},
    ]
    panel=build_p1_panel(adults,performance)
    assert len(panel)==1
    # matched pairs at t: 10 + 20 + 30, poor colonies 1 and 3.
    assert panel[0]["poor_share"] == pytest.approx(40/60)
    assert panel[0]["matched_coverage"] == pytest.approx(1.0)
    expected=math.log1p(66)-math.log1p(63)
    assert panel[0]["island_growth"] == pytest.approx(expected)


def test_p2_island_performance_is_centered_within_season():
    adults=adults_fixture()
    chicks=[
        {"island":"A","colony":"1","season":2000,"chicks":8.0},
        {"island":"A","colony":"2","season":2000,"chicks":16.0},
        {"island":"A","colony":"3","season":2000,"chicks":24.0},
        {"island":"B","colony":"1","season":2000,"chicks":8.0},
        {"island":"B","colony":"2","season":2000,"chicks":8.0},
        {"island":"B","colony":"3","season":2000,"chicks":8.0},
        {"island":"C","colony":"1","season":2000,"chicks":20.0},
        {"island":"C","colony":"2","season":2000,"chicks":40.0},
        {"island":"C","colony":"3","season":2000,"chicks":60.0},
    ]
    perf=build_p2_performance(adults,chicks)
    assert len(perf)==3
    states=[r["island_state"] for r in perf]
    assert sum(states)/len(states) == pytest.approx(0.0,abs=1e-12)
    assert sum((x)**2 for x in states)/(len(states)-1) == pytest.approx(1.0)


def test_hinge_recovers_stronger_negative_side_slope():
    panel=[]
    for colony,offset in (("1",0.3),("2",-0.2),("3",0.1)):
        for season,state in enumerate((-1.5,-0.5,0.5,1.5),start=2000):
            sminus=min(state,0.0)
            splus=max(state,0.0)
            # beta_loss=0.8, beta_win=0.2 plus colony fixed effect.
            y=offset+0.8*sminus+0.2*splus
            panel.append({
                "island":"A","colony":colony,"season":season,
                "state":state,"relative_growth":y,"zsize":0.0,
            })
    fit=fit_hinge(panel)
    assert fit["beta_loss"] == pytest.approx(0.8)
    assert fit["beta_win"] == pytest.approx(0.2)
    assert fit["delta"] == pytest.approx(0.6)


if __name__=="__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))
