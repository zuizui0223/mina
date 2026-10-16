from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np

PATH = Path("scripts/analyze_ross_inverse_path_bounded_count_sensitivity.py")
SPEC = spec_from_file_location("ross_bounded", PATH)
MOD = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def test_observed_scale_threshold():
    k_obs = (MOD.C.sum() - MOD.B.sum()) / (MOD.A.sum() - MOD.B.sum())
    deltas = MOD.component_delta(k_obs)
    assert np.isclose(k_obs, 0.9696749043183291)
    assert np.isclose(deltas.max(), 0.22668807681956138, rtol=0, atol=1e-10)


def test_free_scale_threshold():
    k, delta = MOD.minimize_scale()
    assert np.isclose(k, 0.6513538961, atol=2e-7)
    assert np.isclose(delta, 0.1384340420, atol=2e-8)
