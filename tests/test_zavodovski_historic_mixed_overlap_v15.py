import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import pytest
pytest.importorskip("requests")
pytest.importorskip("shapely")
pytest.importorskip("shapefile")
pytest.importorskip("pyproj")
from shapely.geometry import box,GeometryCollection
from mixed_zavodovski_2011_historical_overlap_v15 import mixed_overlay

def test_mixed_never_forced_into_pure_species():
    ds={(2011,"chinstrap"):box(0,0,2,2),
        (2016,"chinstrap"):box(1,0,2,2),
        (2011,"macaroni"):box(3,0,4,1),
        (2016,"macaroni"):box(3,0,4,1).union(box(0,0,1,1)),
        (2011,"cloud"):GeometryCollection(), (2016,"cloud"):GeometryCollection()}
    hist={"CHPE":box(1,0,2,1),"MCPE":box(3,0,4,1),"MIXED":box(0,0,1,1)}
    r=mixed_overlay(ds,hist)
    assert r["mac_gain_on_historic_mixed_fraction"]==1
    assert r["apparent_C_to_M_overlap_on_historic_mixed_fraction"]==1
    assert r["direct_original_E"]==1
