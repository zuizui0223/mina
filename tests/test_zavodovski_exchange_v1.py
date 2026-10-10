"""All geometry below is fabricated; never a penguin observation."""
import importlib.util
from pathlib import Path
import pytest
from shapely.geometry import box

path = Path(__file__).resolve().parents[1] / 'scripts/zavodovski_exchange_v1.py'
spec = importlib.util.spec_from_file_location('zavodovski_exchange', path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_actual_spatial_overlap_partition_on_synthetic_rectangles():
    support = box(0, 0, 10, 10)
    x = mod.compute_exchange(box(0, 0, 2, 2), box(1, 0, 2, 2),
                             box(4, 0, 5, 1),
                             box(4, 0, 5, 1).union(box(0, 0, 1, 1)), support)
    assert x['chin_lost_area_m2'] == 2
    assert x['mac_gained_area_m2'] == 1
    assert x['mac_gain_on_chin_lost_m2'] == 1
    assert x['exchange_fraction_of_mac_gain'] == 1
    assert x['reciprocal_exchange_fraction_of_chin_loss'] == .5
    assert x['mac_gain_without_chin_at_start_m2'] == 0


def test_independent_increase_despite_chin_loss():
    x = mod.compute_exchange(box(0, 0, 2, 2), box(1, 0, 2, 2),
                             box(4, 0, 5, 1),
                             box(4, 0, 5, 1).union(box(8, 8, 9, 9)), box(0, 0, 10, 10))
    assert x['mac_gain_on_chin_lost_m2'] == 0
    assert x['mac_gain_without_chin_at_start_m2'] == 1
    assert x['exchange_fraction_of_mac_gain'] == 0


def test_shared_occupancy_must_not_be_misclassified_as_vacancy():
    x = mod.compute_exchange(box(0, 0, 2, 2), box(0, 0, 2, 2),
                             box(4, 0, 5, 1),
                             box(4, 0, 5, 1).union(box(0, 0, 1, 1)), box(0, 0, 10, 10))
    assert x['mac_gain_on_chin_lost_m2'] == 0
    assert x['mac_gain_on_persistent_chin_m2'] == 1


def test_missing_provenance_refuses_biological_opening():
    with pytest.raises(ValueError, match='STOP'):
        mod.audit_provenance({'observed_years': [2011, 2016]}, 2011, 2016)
    with pytest.raises(ValueError, match='dates'):
        mod.audit_provenance({'observed_years': [2011, 2020]}, 2011, 2016)


def test_no_gain_has_undefined_ratio_not_zero_effect():
    x = mod.compute_exchange(box(0, 0, 2, 2), box(1, 0, 2, 2),
                             box(4, 0, 5, 1), box(4, 0, 5, 1), box(0, 0, 10, 10))
    assert x['exchange_fraction_of_mac_gain'] is None
