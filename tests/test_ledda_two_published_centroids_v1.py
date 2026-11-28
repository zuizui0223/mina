import csv
import importlib.util
from pathlib import Path
import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/audit_ledda_two_published_centroids_v1.py"
spec = importlib.util.spec_from_file_location("two_ledda", PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def make_csv(p, records):
    with p.open("w", newline="", encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=("site_id","site_name","lat","lon"))
        w.writeheader()
        w.writerows(records)


def test_source_consistency_requires_exact_pinned_ledda(tmp_path):
    file=tmp_path/"sites.csv"
    make_csv(file,[{"site_id":"LEDD","site_name":"Ledda Bay","lat":-74.228,"lon":-130.784}])
    assert m.source_row(file)==((-74.228,-130.784),1)
    make_csv(file,[{"site_id":"LEDD","site_name":"Ledda Bay","lat":-74.2,"lon":-130.784}])
    with pytest.raises(ValueError):
        m.source_row(file)


def test_disjoint_radii_and_no_false_colony_migration():
    r=m.report(m.EXPECTED_LARUE)
    assert 14 < r["center_distance_km"] < 16
    assert all(r["radii_disjoint_at_both_centroids"].values())
    assert r["both_5km_buffers_cannot_cover_same_physical_patch"]
    assert not r["true_colony_movement_confirmed"]
    assert not r["year_specific_nesting_footprints_confirmed"]
    assert not r["new_causal_claim"]
    assert r["external_ice_pixel_values_read"] == 0


def test_identical_centroids_do_not_prove_different_patches():
    r=m.report(m.EXPECTED_LARUE,second=m.EXPECTED_LARUE)
    assert r["center_distance_km"]==0
    assert not any(r["radii_disjoint_at_both_centroids"].values())
