"""Guard aggregation and exposure errors that would change this comparison."""
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
import pytest

PATH = Path(__file__).parents[1] / 'research/climate-penguin/work/palmer_signy_diet_external_v1/analyze.py'


def get_analysis():
    assert PATH.exists(), 'External-region diet analysis has not been implemented'
    spec = importlib.util.spec_from_file_location('palmer_signy_external', PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stomach_mean_excludes_nonfood_and_does_not_pool_mass():
    analysis = get_analysis()
    # Pooling fish mass would give 0.82; including non-food gives 0.475.
    # Correct individual food fractions are 0.1 and 0.9, averaging 0.5.
    raw = pd.DataFrame({
        'DATE': ['2001-12-31', '2002-01-05'], 'RECORD_ID': ['a', 'b'],
        'FISH_MASS_g': [1.0, 81.0], 'CRUSTACEAN_MASS_g': [9.0, 9.0],
        'CEPHALOPOD_MASS_g': [0.0, 0.0], 'OTHER_FOOD_MASS_g': [0.0, 0.0],
        'NON_FOOD_MASS_g': [10.0, 0.0], 'TOTAL_MASS_g': [20.0, 90.0],
        'EUPHAUSIA_SUPERBA_MASS_g': [9.0, 9.0],
    })
    got, audit = analysis.summarize_signy(raw, 'Adelie', [2001])
    assert got.iloc[0]['fish_food_mean'] == pytest.approx(0.5)
    assert got.iloc[0]['fish_total_mean'] == pytest.approx(0.475)
    assert got.iloc[0]['n_stomachs'] == 2
    assert audit['n_valid'] == 2


def test_missing_food_is_not_zero_and_source_keys_must_be_unique():
    analysis = get_analysis()
    raw = pd.DataFrame({
        'DATE': ['2001-12-31', '2002-01-05'], 'RECORD_ID': ['a', 'b'],
        'FISH_MASS_g': [1.0, 1.0], 'CRUSTACEAN_MASS_g': [9.0, np.nan],
        'CEPHALOPOD_MASS_g': [0.0, 0.0], 'OTHER_FOOD_MASS_g': [0.0, 0.0],
        'TOTAL_MASS_g': [10.0, 10.0], 'EUPHAUSIA_SUPERBA_MASS_g': [9.0, np.nan],
    })
    got, audit = analysis.summarize_signy(raw, 'Adelie', [2001])
    assert got.iloc[0]['n_stomachs'] == 1
    assert got.iloc[0]['fish_food_mean'] == pytest.approx(0.1)
    assert audit['n_excluded'] == 1
    with pytest.raises(ValueError, match='duplicate'):
        analysis.summarize_signy(pd.concat([raw, raw.iloc[[0]]]), 'Adelie', [2001])


def test_ice_requires_four_unique_complete_months_and_equal_weights():
    analysis = get_analysis()
    raw = pd.DataFrame({
        'site_id': ['BISC'] * 5, 'year': [2009] * 5,
        'month': [8, 9, 10, 11, 8], 'inner_km': [0, 0, 0, 0, 100],
        'complete_month': [True] * 5, 'sic_mean': [0.0, 0.0, 0.0, 100.0, 99.0],
        'days': [31, 30, 31, 30, 31],
        'supported_days': [31, 30, 31, 30, 31],
        'expected_days': [31, 30, 31, 30, 31],
    })
    got = analysis.annual_ice(raw, ['BISC'], [2009])
    assert got.iloc[0]['sic_aug_nov'] == pytest.approx(25.0)
    with pytest.raises(ValueError, match='four'):
        analysis.annual_ice(raw.drop(index=3), ['BISC'], [2009])
    with pytest.raises(ValueError, match='duplicate'):
        analysis.annual_ice(pd.concat([raw, raw.iloc[[0]]]), ['BISC'], [2009])
    bad = raw.copy(); bad.loc[0, 'complete_month'] = False
    with pytest.raises(ValueError, match='complete'):
        analysis.annual_ice(bad, ['BISC'], [2009])
    bad_days = raw.copy(); bad_days.loc[0, 'supported_days'] = 30
    with pytest.raises(ValueError, match='days'):
        analysis.annual_ice(bad_days, ['BISC'], [2009])


def test_published_means_use_start_year_without_expanding_stomachs():
    analysis = get_analysis()
    raw = pd.DataFrame([
        {'species': species, 'season_start_year': year, 'season_end_year': year + 1,
         'fish_mean_pct': 1.3, 'sample_n': 20}
        for species in ['Adelie', 'Gentoo'] for year in range(2009, 2015)
    ])
    got = analysis.palmer_means(raw)
    assert len(got) == 12
    assert set(got.year) == set(range(2009, 2015))
    assert np.allclose(got.fish_food_mean, 0.013)
    with pytest.raises(ValueError, match='cohort'):
        analysis.palmer_means(raw.iloc[:-1])
    invalid = raw.copy(); invalid.loc[0, 'fish_mean_pct'] = np.nan
    with pytest.raises(ValueError, match='fish'):
        analysis.palmer_means(invalid)


def test_region_average_is_per_proxy_not_per_stomach():
    analysis = get_analysis()
    source = pd.DataFrame({'site_id': ['BISC', 'LITC'], 'year': [2009, 2009], 'sic_aug_nov': [20.0, 40.0]})
    got = analysis.regional_ice(source, ['BISC', 'LITC'])
    assert got.iloc[0]['sic_aug_nov'] == pytest.approx(30.0)
    with pytest.raises(ValueError, match='proxy'):
        analysis.regional_ice(source.iloc[[0]], ['BISC', 'LITC'])


def test_transport_freezes_training_mean_and_flags_extrapolation():
    analysis = get_analysis()
    train = pd.DataFrame({'year': [1, 2, 3], 'sic_aug_nov': [10.0, 20.0, 30.0], 'distance': [0.1, 0.2, 0.3]})
    target = pd.DataFrame({'year': [4, 5], 'sic_aug_nov': [20.0, 40.0], 'distance': [0.01, 0.02]})
    got, score = analysis.transport(train, target)
    assert got['predicted_distance'].to_list() == pytest.approx([0.2, 0.4])
    assert got['training_mean_prediction'].to_list() == pytest.approx([0.2, 0.2])
    assert got['in_training_ice_range'].to_list() == [True, False]
    assert score['all_target_seasons']['model_mae'] == pytest.approx(0.285)
    assert score['all_target_seasons']['training_mean_mae'] == pytest.approx(0.185)
    assert score['within_training_ice_range']['n'] == 1


def test_exact_permutation_counts_years_not_stomachs():
    analysis = get_analysis()
    got = analysis.exact_permutation(np.arange(4.0), np.arange(4.0))
    assert got['n_permutations'] == 24
    assert got['extreme_count'] == 2
    assert got['p_exact'] == pytest.approx(2 / 24)
