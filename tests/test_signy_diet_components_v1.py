"""Ecological aggregation and accounting errors, not file-existence snapshots."""
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
import pytest

PATH = Path(__file__).parents[1] / 'research/climate-penguin/work/signy_diet_components_v1/analyze.py'


def analysis():
    assert PATH.exists(), 'Diet component analysis has not been implemented'
    spec = importlib.util.spec_from_file_location('diet_components', PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def raw_frame(fish, crust):
    n = len(fish)
    return pd.DataFrame({
        'DATE': ['2002-01-15'] * n, 'RECORD_ID': [f's{i}' for i in range(n)],
        'FISH_MASS_g': fish, 'CRUSTACEAN_MASS_g': crust,
        'CEPHALOPOD_MASS_g': [0.] * n, 'OTHER_FOOD_MASS_g': [0.] * n,
        'TOTAL_MASS_g': [f+c if np.isfinite(c) else 10. for f,c in zip(fish,crust)],
        'EUPHAUSIA_SUPERBA_MASS_g': crust,
    })


def test_frequency_times_conditional_fraction_is_equal_stomach_mean():
    mod = analysis()
    good, _ = mod.valid_stomachs(raw_frame([0., 2., 80.], [10., 8., 20.]), 'Gentoo', [2001])
    row = mod.annual_components(good).iloc[0]
    assert row.n_stomachs == 3
    assert row.n_positive_fish_mass == 2
    assert row.positive_mass_frequency == pytest.approx(2/3)
    assert row.conditional_fish_fraction == pytest.approx(.5)
    assert row.mean_fish_fraction == pytest.approx(1/3)
    assert row.mean_fish_mass_g == pytest.approx(82/3)
    assert row.mean_food_mass_g == pytest.approx(40.)


def test_no_positive_fish_has_undefined_conditional_mean():
    mod = analysis()
    good, _ = mod.valid_stomachs(raw_frame([0., 0.], [10., 20.]), 'Adelie', [2001])
    row = mod.annual_components(good).iloc[0]
    assert row.mean_fish_fraction == 0
    assert row.positive_mass_frequency == 0
    assert np.isnan(row.conditional_fish_fraction)
    with pytest.raises(ValueError, match='undefined'):
        mod.decompose(np.arange(3.), np.array([0., .5, 1.]), np.array([np.nan,.4,.5]))


def test_missing_mass_is_excluded_and_nonfood_is_not_denominator():
    mod = analysis()
    raw = raw_frame([1., 1.], [9., np.nan])
    raw['TOTAL_MASS_g'] = [20., 10.]
    raw['NON_FOOD_MASS_g'] = [10., 0.]
    good, audit = mod.valid_stomachs(raw, 'Gentoo', [2001])
    row = mod.annual_components(good).iloc[0]
    assert row.n_stomachs == 1
    assert row.mean_fish_fraction == pytest.approx(.1)
    assert audit['n_excluded'] == 1


def test_decomposition_reconstructs_values_and_slopes_with_covariation():
    mod = analysis()
    x = np.array([10.,20.,30.,40.])
    p = np.array([.2,.4,.5,.9])
    c = np.array([.1,.5,.2,.8])
    terms, summary = mod.decompose(x,p,c)
    assert np.allclose(terms.sum(axis=1) + p.mean()*c.mean(), p*c)
    assert summary['sum_component_slopes_per_10pp'] == pytest.approx(summary['mean_response_slope_per_10pp'])
    assert summary['covariation_mean'] != 0
    assert np.allclose(terms.sub(terms.mean()).sum(axis=1),p*c-(p*c).mean())


def test_constant_frequency_assigns_all_mean_slope_to_composition():
    mod = analysis()
    _, result = mod.decompose(np.arange(4.), np.full(4,.5), np.array([.1,.2,.4,.8]))
    slopes=result['component_slopes_per_10pp']
    assert slopes['frequency'] == pytest.approx(0.)
    assert slopes['covariation'] == pytest.approx(0.)
    assert slopes['composition'] == pytest.approx(result['mean_response_slope_per_10pp'])


def test_max_family_uses_joint_permutations_and_preserves_perfect_dependence():
    mod = analysis()
    x=np.arange(4.)
    result=mod.exact_component_family(x,{'p':x,'c':x[::-1]})
    assert result['n_permutations'] == 24
    for name in ('p','c'):
        assert result['components'][name]['p_exact'] == pytest.approx(2/24)
        assert result['components'][name]['p_max2'] == pytest.approx(2/24)
