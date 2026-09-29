import numpy as np

from mina.neutral_attrition import _multinomial_varying_probs


def test_vectorized_multinomial_preserves_total_and_absorbing_zero():
    rng = np.random.default_rng(7)
    probs = np.asarray([
        [0.0, 0.25, 0.75],
        [0.5, 0.5, 0.0],
        [0.0, 1.0, 0.0],
    ])
    out = _multinomial_varying_probs(rng, 20, probs)
    assert np.all(np.sum(out, axis=1) == 20)
    assert out[0, 0] == 0
    assert out[1, 2] == 0
    assert out[2, 0] == 0 and out[2, 2] == 0
    assert out[2, 1] == 20
