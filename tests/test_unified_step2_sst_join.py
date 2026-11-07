import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"research/network_concentration_unified_v1"))
import join_oisst_uk as m

def test_wrapping():
    assert m.km(50,-1,50,359)<1e-6

def test_complete_fixed_cell():
    lat=np.array([50,50.25]);lon=np.array([359,359.25])
    ts={f"{y}-{month:02d}":i for i,(y,month) in enumerate(
        [(2000,3),(2000,4),(2000,5),(2016,3),(2016,4),(2016,5)])}
    grid=np.full((6,2,2),np.nan)
    grid[:,0,0]=[10,11,12,13,14,15]
    v,s=m.sample(50,-1,2000,2016,lat,lon,ts,grid)
    assert s=="verified" and np.isclose(v[0],11) and np.isclose(v[1],14)
    grid[4,0,0]=np.nan
    assert m.sample(50,-1,2000,2016,lat,lon,ts,grid)[0] is None
