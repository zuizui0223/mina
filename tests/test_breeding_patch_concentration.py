import numpy as np

from mina.breeding_patch_concentration import (
    _effective_number_batch,
    _slope_batch,
)


def test_effective_number_equal_counts_equals_component_count():
    matrix = np.asarray(
        [
            [
                [10.0, 5.0],
                [10.0, 5.0],
                [10.0, 5.0],
            ]
        ]
    )
    out = _effective_number_batch(matrix)
    assert np.allclose(out, [[3.0, 3.0]])


def test_effective_number_detects_concentration():
    matrix = np.asarray(
        [
            [
                [5.0, 10.0],
                [5.0, 0.0],
            ]
        ]
    )
    out = _effective_number_batch(matrix)
    assert np.isclose(out[0, 0], 2.0)
    assert np.isclose(out[0, 1], 1.0)


def test_slope_batch_recovers_linear_trend():
    years = np.asarray([2000, 2001, 2002, 2003])
    values = np.asarray(
        [
            [4.0, 3.0, 2.0, 1.0],
            [1.0, 1.5, 2.0, 2.5],
        ]
    )
    slopes = _slope_batch(values, years)
    assert np.allclose(slopes, [-1.0, 0.5])
