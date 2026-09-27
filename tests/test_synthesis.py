from pathlib import Path
from mina.synthesis import build

def test_frozen_synthesis_matches_receipts():
    root=Path(__file__).resolve().parents[1]/"results"
    x=build(root)
    assert abs(x["five_island_decline"]["pc1_variance_fraction"]-0.9640284642946518)<1e-12
    assert x["prospective_mechanism_tests"]["annual_seaice_duration"]["supported"] is False
    assert x["prospective_mechanism_tests"]["five_year_seaice_duration"]["supported"] is False
    assert x["prospective_mechanism_tests"]["october_snow_x_habitat"]["supported"] is False
    assert x["local_colony_state"]["effective_colony_number"]["supported"] is True
    assert x["local_colony_state"]["external_gt50_group_count"]["directional_supported"] is False
    assert x["local_colony_state"]["effective_colony_number"]["beta"]>0
    assert x["local_colony_state"]["external_gt50_group_count"]["beta"]<0
