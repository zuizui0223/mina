from pathlib import Path
import importlib.util
import sys
import pytest
pytest.importorskip('shapely', minversion='2.1')
from shapely.geometry import box, Point
from shapely.affinity import rotate

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'research/climate-penguin/work/abandonment/palmer_map_resolution.py'

def mod():
    assert SCRIPT.exists(), 'resolution gate implementation missing'
    sys.path.insert(0,str(SCRIPT.parent))
    spec=importlib.util.spec_from_file_location('resolution_gate',SCRIPT)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def test_large_but_thin_patch_is_ruled_out():
    r=mod().pixel_gate(box(0,0,9,100),10)
    assert r['ruled_out_by_disk']
    assert r['area_m2']>10**2

def test_rotation_does_not_make_thin_patch_resolvable():
    assert mod().pixel_gate(rotate(box(0,0,9,100),37),10)['ruled_out_by_disk']

def test_boundary_square_is_not_falsely_excluded():
    r=mod().pixel_gate(box(0,0,10,10),10)
    assert not r['ruled_out_by_disk']
    assert not r['native_grid_verified']

def test_necessary_condition_is_not_square_sufficiency():
    r=mod().pixel_gate(Point(0,0).buffer(5.2),10)
    assert not r['ruled_out_by_disk']
    assert r['decision']=='not_ruled_out__native_grid_and_groundtruth_required'

def test_invalid_geometry_or_pixel_size_rejected():
    m=mod()
    with pytest.raises(ValueError):m.pixel_gate(box(0,0,1,1),0)
    with pytest.raises(ValueError):m.pixel_gate(Point(0,0),10)

def test_source_sha_is_checked_before_drawing_ids(tmp_path):
    p=tmp_path/'wrong.pdf';p.write_bytes(b'%PDF-1.4 wrong version')
    with pytest.raises(ValueError,match='SHA'):
        mod().torgersen(p)
