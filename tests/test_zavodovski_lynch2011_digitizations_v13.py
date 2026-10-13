"""Only synthetic polygon inputs; no original Lynch biological rows."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pytest
pytest.importorskip("requests")
pytest.importorskip("shapefile")
pytest.importorskip("shapely")
pytest.importorskip("pyproj")
from shapely.geometry import box, GeometryCollection
import compare_zavodovski_lynch2011_digitizations_v13 as m


def test_fixed_species_schema_mapping():
    assert m.ALLOWED_LABELS == {"CPE": "chinstrap", "MPE": "macaroni"}
    assert m.jaccard(box(0, 0, 2, 2), box(0, 0, 2, 2)) == 1
    assert m.jaccard(box(0, 0, 2, 2), box(3, 0, 4, 2)) == 0


def test_alternate_2011_baseline_can_change_overlap():
    old = {(2011, "chinstrap"):box(0,0,2,2),(2011,"macaroni"):box(5,0,6,1),
           (2016,"chinstrap"):box(1,0,2,2),
           (2016,"macaroni"):box(5,0,6,1).union(box(0,0,1,1)),
           (2011,"cloud"):GeometryCollection(),(2016,"cloud"):GeometryCollection()}
    old_lynch={"chinstrap":box(3,3,4,4),"macaroni":box(5,0,6,1)}
    v=m.comparison(old,old_lynch)
    assert v["direct_2011_E"] == 1
    assert v["lynch_2011_E"] == 0
