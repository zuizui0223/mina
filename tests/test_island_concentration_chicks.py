import numpy as np
from mina.island_concentration_chicks import _fit_observed

def test_fit_observed_has_finite_concentration_beta():
    rows=[]
    wiggle=[0.0,0.3,-0.2,0.4,-0.1,0.2]
    for island,offset in [("A",0.0),("B",0.15)]:
        for j,year in enumerate(range(2000,2006)):
            c=wiggle[j]+offset*(1 if j%2==0 else -1)
            rows.append({
                "island":island,"year":year,"adult_pairs":100+j+3*offset,
                "total_chicks":120+8*j-15*c,
                "effective_colony_number":3.0,
                "largest_colony_share":0.5,
                "concentration":c,
                "chick_rate":1.2
            })
    out=_fit_observed(rows,"concentration")
    assert np.isfinite(out["beta"])
