import numpy as np
from mina.island_concentration_chicks import _fit_observed

def test_fit_observed_has_finite_concentration_beta():
    rows=[]
    for island,offset in [("A",0),("B",1)]:
        for year in range(2000,2006):
            c=(year-2000)/5+offset*0.1
            rows.append({
                "island":island,"year":year,"adult_pairs":100+year-2000,
                "total_chicks":120+20*c,"effective_colony_number":3.0,
                "largest_colony_share":0.5,"concentration":c,"chick_rate":1.2
            })
    out=_fit_observed(rows,"concentration")
    assert np.isfinite(out["beta"])
