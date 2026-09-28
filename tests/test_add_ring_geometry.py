import importlib.util
from pathlib import Path

from shapely.geometry import Point


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_add_site_matching.py"
spec = importlib.util.spec_from_file_location("add_match", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

_build = module._esri_rings_to_geometry


def square(x0, y0, x1, y1):
    return [
        [x0, y0],
        [x1, y0],
        [x1, y1],
        [x0, y1],
        [x0, y0],
    ]


def test_single_ring_contains_interior():
    geom, _ = _build([square(0, 0, 10, 10)])
    assert geom.contains(Point(5, 5))


def test_orientation_does_not_change_shell():
    ring = square(0, 0, 10, 10)
    a, _ = _build([ring])
    b, _ = _build([list(reversed(ring))])
    assert a.equals(b)


def test_nested_ring_becomes_hole_regardless_orientation():
    outer = square(0, 0, 10, 10)
    inner = square(3, 3, 7, 7)
    geom, _ = _build([list(reversed(outer)), inner])
    assert geom.contains(Point(1, 1))
    assert not geom.contains(Point(5, 5))


def test_disjoint_rings_form_multipart_land():
    geom, _ = _build([
        square(0, 0, 10, 10),
        list(reversed(square(20, 20, 30, 30))),
    ])
    assert geom.contains(Point(5, 5))
    assert geom.contains(Point(25, 25))
