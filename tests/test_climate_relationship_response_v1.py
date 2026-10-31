"""Numerical contracts: no camera replication, common cohorts, no future leakage."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PATH = Path(__file__).parents[1] / 'research/climate-penguin/work/relationship_response_v1/analyze.py'


@pytest.fixture
def mod():
    assert PATH.exists(), 'same-cohort response implementation is not yet present'
    spec = importlib.util.spec_from_file_location('relationship_response', PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_common_complete_camera_set_and_no_missing_as_zero(mod):
    rows = pd.DataFrame({
        'source_row_1based': [1, 2, 3, 4], 'species': ['Adelie'] * 4,
        'cam': ['A', 'A', 'B', 'C'], 'season_start_year': [2015] * 4,
        'settlement': [10., 14., 50., 60.], 'tmean_9': [1., 1., 2., 3.],
        'near_sic_mean_month9': [20., 20., 10., 0.],
        'ocean_m9_surface_salinity': [34., 34., np.nan, 33.],
        'ocean_m9_surface_potential_temperature_c': [-1., -1., 0., 1.],
        'appendix_range_consistent': [True, True, True, False],
    })
    a = mod.prepare_cohort(rows)
    assert a.cam.tolist() == ['A', 'C']
    assert a.y.tolist() == [12., 60.]
    assert a.camera_rows.tolist() == [2, 1]
    assert a.ice10.tolist() == [2., 0.]
    assert mod.prepare_cohort(rows, appendix=True).cam.tolist() == ['A']


def test_duplicate_source_row_rejected(mod):
    with pytest.raises(ValueError, match='duplicate'):
        mod.prepare_cohort(pd.DataFrame({'source_row_1based': [1, 1]}))


def test_within_site_slope_not_between_site_confounding(mod):
    d = pd.DataFrame({'cam': ['A'] * 3 + ['B'] * 3,
                      'year': [1, 2, 3] * 2,
                      'x': [0., 2., 1., 10., 12., 11.],
                      'y': [0., 4., 2., -20., -16., -18.]})
    b, details = mod.fe_fit(d, ['x'], 'site')
    assert b[0] == pytest.approx(2.)
    assert details['residual_df'] == 3
    summary = mod.describe_relationship(d, 'x')
    assert summary['within_r'] == pytest.approx(1.)
    assert summary['between_r'] == pytest.approx(-1.)


def test_climate_absorbed_by_year_is_flagged_not_zero_effect(mod):
    d = pd.DataFrame({'cam': ['A'] * 3 + ['B'] * 3,
                      'year': [1, 2, 3] * 2,
                      'x': [1., 2., 3.] * 2,
                      'y': [2., 4., 6., 3., 5., 7.]})
    b, details = mod.fe_fit(d, ['x'], 'site_year')
    assert b is None
    assert details['status'] == 'exposure_not_identified'


def test_forward_folds_exclude_future_and_new_sites(mod):
    d = pd.DataFrame({'cam': ['A', 'A', 'A', 'B', 'A'],
                      'year': [2012, 2013, 2015, 2015, 2020],
                      'y': [1., 2., 3., 4., 9999.]})
    train, test, new = mod.forward_fold(d, 2015)
    assert train.year.tolist() == [2012, 2013]
    assert test.cam.tolist() == ['A']
    assert test.y.tolist() == [3.]
    assert new == 1


def test_ridge_uses_train_scaling_and_fixed_prediction_function(mod):
    train = pd.DataFrame({'cam': ['A'] * 4, 'year': [2011, 2012, 2013, 2014],
                          'x': [0., 1., -1., 2.], 'y': [1., 4., 0., 8.]})
    small = pd.DataFrame({'cam': ['A'], 'year': [2015], 'x': [1.]})
    large = pd.DataFrame({'cam': ['A', 'A'], 'year': [2015, 2015], 'x': [1., 10000.]})
    p1, info1 = mod.predict_ridge(train, small, ['x'])
    p2, info2 = mod.predict_ridge(train, large, ['x'])
    assert p1[0] == pytest.approx(p2[0])
    assert info1['training_means'] == info2['training_means']
    assert info1['training_means'] == [0.5]
    assert info2['outside_training_range'].tolist() == [False, True]


def test_ridge_baseline_recovers_site_and_time_without_environment(mod):
    train = pd.DataFrame({'cam': ['A'] * 3 + ['B'] * 3,
                          'year': [2011, 2012, 2013] * 2,
                          'y': [10., 12., 14., 30., 32., 34.]})
    test = pd.DataFrame({'cam': ['A', 'B'], 'year': [2014, 2014]})
    prediction, _ = mod.predict_ridge(train, test, [])
    assert prediction == pytest.approx([16., 36.])
