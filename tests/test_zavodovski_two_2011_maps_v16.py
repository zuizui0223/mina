"""All geometries fictitious: test the paired-map estimand, not animals."""
import sys
from pathlib import Path
import pytest
pytest.importorskip("requests")
pytest.importorskip("shapely")
pytest.importorskip("shapefile")
pytest.importorskip("pyproj")
from shapely.geometry import GeometryCollection, box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from compare_zavodovski_two_2011_maps_v16 import audit_maps, agreement, safe_ratio


def mock_maps():
    macaroni_early = box(4,0,5,1)
    gain = box(0,0,1,1)
    return {
        (2011,"chinstrap"): box(0,0,2,2),
        (2011,"macaroni"): macaroni_early,
        (2011,"cloud"): GeometryCollection(),
        (2016,"chinstrap"): box(1,0,2,2),
        (2016,"macaroni"): macaroni_early.union(gain),
        (2016,"cloud"): GeometryCollection()
    }, {
        "CHPE": box(2,0,3,1),
        "MCPE": macaroni_early,
        "MIXED": box(0,0,.25,1)
    }


def test_same_support_alternate_2011_changes_apparent_exchange():
    maps, historic=mock_maps()
    o=audit_maps(maps,historic)
    both=o["same_support_alternative_2011_digitization"]
    assert both["all_support_revised_E_check"] == 1
    assert both["nonmixed_support_revised_2011"]["E"] == 1
    assert both["nonmixed_support_historic_2011"]["E"] == 0
    assert o["apparent_gain_outside_historic_definite_or_possible_macaroni"]["fraction_gain_outside_historic_MCPE_and_MIXED"] == .75
    assert o["historic_mixed_within_support_m2"] == .25
    assert o["historical_mixed_not_assigned_to_a_species"] is True


def test_jaccard_has_no_zero_denominator_fiction():
    assert safe_ratio(0,0) is None
    o=agreement(box(0,0,1,1), box(0,0,1,1), box(0,0,1,1))
    assert o["jaccard"] == 1
    assert o["fraction_revised_in_historic"] == 1


def test_cloud_excludes_contaminated_part_for_both_maps():
    direct,historic=mock_maps()
    direct[2011,"cloud"]=box(0,0,.5,1)
    o=audit_maps(direct,historic)
    assert o["same_support_alternative_2011_digitization"]["all_support_revised_E_check"] == 1
    assert o["historic_mixed_within_support_m2"] == 0
