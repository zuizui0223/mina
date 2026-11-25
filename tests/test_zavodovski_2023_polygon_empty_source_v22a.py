import sys
from pathlib import Path
import pytest
pytest.importorskip("requests")
pytest.importorskip("shapely")
pytest.importorskip("shapefile")
pytest.importorskip("pyproj")
import shapefile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_zavodovski_2023_polygon_empty_source_v22a import inspect_polygon_shape_records


def test_original_source_null_record_counted_not_a_polygon(tmp_path):
    path=tmp_path/"test_polygon.shp"
    w=shapefile.Writer(str(path),shapeType=shapefile.POLYGON)
    w.field("id","N",size=10)
    w.poly([[(0,0),(0,10),(10,10),(10,0),(0,0)]])
    w.record(1)
    w.null()
    w.record(2)
    w.close()
    x=inspect_polygon_shape_records(path)
    assert x["original_record_count"]==2
    assert x["original_zero_vertex_record_count"]==1
    assert x["original_nonempty_shape_records"]==1
    assert x["nest_point_rows_opened"]==0
