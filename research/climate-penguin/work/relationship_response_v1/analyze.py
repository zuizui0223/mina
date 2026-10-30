"""Exploratory September relationships and conditional historical prediction.

No coefficient, month, model or population is selected by its result. Historical
216-test results are not reopened. Settlement remains a nominal source day index.
Heldout-year environmental values are realized inputs, not real-time forecasts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'outputs/climate_penguin/behavior_ocean_join.csv'
MAPPING = {
    'airC': ('tmean_9', 1.0),
    'ice10': ('near_sic_mean_month9', 10.0),
    'salt01': ('ocean_m9_surface_salinity', 0.1),
    'waterC': ('ocean_m9_surface_potential_temperature_c', 1.0),
}
MODELS = {'B': [], 'I': ['airC', 'ice10'],
          'O': ['airC', 'waterC', 'salt01'],
          'J': ['airC', 'waterC', 'salt01', 'ice10']}
SPECIES = ['Adelie', 'Chinstrap', 'Gentoo']


def prepare_cohort(raw, appendix=False):
    if raw.source_row_1based.duplicated().any():
        raise ValueError('duplicate original source row')
    d = raw.copy()
    if appendix:
        # Accept the existing boolean column, never infer dates or replace labels.
        d = d[d.appendix_range_consistent.eq(True)]
    cols = [v[0] for v in MAPPING.values()] + ['settlement']
    d[cols] = d[cols].replace([np.inf, -np.inf], np.nan)
    d = d.dropna(subset=cols)
    if not d.season_start_year.eq(d.season_start_year.astype(int)).all():
        raise ValueError('noninteger season label')
    aggregation = {k: (v[0], 'mean') for k, v in MAPPING.items()}
    aggregation.update(y=('settlement', 'mean'), camera_rows=('settlement', 'size'),
                       source_rows=('source_row_1based', lambda s: '|'.join(map(str, sorted(s)))))
    a = d.groupby(['species', 'cam', 'season_start_year'], sort=True).agg(**aggregation).reset_index()
    a = a.rename(columns={'season_start_year': 'year'})
    for key, (_, scale) in MAPPING.items():
        a[key] /= scale
    return a


def nuisance(d, mode='site', levels=None, year_center=None):
    levels = sorted(d.cam.unique()) if levels is None else levels
    values = [np.ones(len(d))]
    values += [(d.cam.to_numpy() == site).astype(float) for site in levels[1:]]
    if mode == 'site_trend':
        center = d.year.mean() if year_center is None else year_center
        values += [d.year.to_numpy(dtype=float) - center]
    elif mode == 'site_year':
        values += [(d.year.to_numpy() == year).astype(float) for year in sorted(d.year.unique())[1:]]
    elif mode != 'site':
        raise ValueError('unknown nuisance mode')
    return np.column_stack(values)


def fe_fit(d, features, mode, weights=None):
    z = nuisance(d, mode)
    x = d[features].to_numpy(dtype=float)
    y = d.y.to_numpy(dtype=float)
    sw = np.ones(len(d)) if weights is None else np.sqrt(np.asarray(weights))
    if not np.isfinite(sw).all() or np.any(sw < 0) or not np.any(sw > 0):
        raise ValueError('invalid bootstrap weights')
    z, x, y = z * sw[:, None], x * sw[:, None], y * sw
    rx = x - z @ np.linalg.lstsq(z, x, rcond=None)[0]
    ry = y - z @ np.linalg.lstsq(z, y, rcond=None)[0]
    rank_z = np.linalg.matrix_rank(z)
    # Tolerance is relative to the original predictor scale, not machine noise
    # in a climate vector perfectly absorbed by the fixed effects.
    tolerance = max(1e-9, np.linalg.norm(x) * 1e-10)
    rank_x = np.linalg.matrix_rank(rx, tol=tolerance)
    df = int(np.count_nonzero(sw) - rank_z - rank_x)
    info = {'status': 'descriptive', 'residual_df': df,
            'exposure_rank': int(rank_x), 'nuisance_rank': int(rank_z)}
    if rank_x < len(features):
        info['status'] = 'exposure_not_identified'
        return None, info
    if df <= 0:
        info['status'] = 'no_residual_degrees_of_freedom'
        return None, info
    beta = np.linalg.lstsq(rx, ry, rcond=None)[0]
    # Full dummy regression supplies an independent algebraic cross-check.
    direct = np.linalg.lstsq(np.column_stack([z, x]), y, rcond=None)[0][-len(features):]
    if not np.allclose(beta, direct, rtol=1e-7, atol=1e-7):
        raise ValueError('fixed-effect residual and direct fit disagree')
    return beta, info


def correlation(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 2 or np.std(x) < 1e-9 or np.std(y) < 1e-9:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def describe_relationship(d, feature):
    between = d.groupby('cam')[[feature, 'y']].mean()
    within = d[[feature, 'y']] - d.groupby('cam')[[feature, 'y']].transform('mean')
    z = nuisance(d, 'site_year')
    xy = d[[feature, 'y']].to_numpy(dtype=float)
    adjusted = xy - z @ np.linalg.lstsq(z, xy, rcond=None)[0]
    ss_site = float(np.sum(within[feature] ** 2))
    return {'between_r': correlation(between[feature], between.y),
            'within_r': correlation(within[feature], within.y),
            'site_year_r': correlation(adjusted[:, 0], adjusted[:, 1]),
            'within_exposure_sd': float(within[feature].std(ddof=0)),
            'fraction_within_exposure_ss_retained_after_year':
                float(np.sum(adjusted[:, 0] ** 2) / ss_site) if ss_site > 1e-10 else np.nan}


def resample_coefficients(d, features, mode, cluster, repeats, rng):
    groups, inverse = np.unique(d[cluster].to_numpy(), return_inverse=True)
    values = []
    for _ in range(repeats):
        weights = np.bincount(rng.integers(0, len(groups), len(groups)), minlength=len(groups))[inverse]
        beta, _ = fe_fit(d, features, mode, weights)
        if beta is not None:
            values.append(beta)
    if not values:
        return None, 0
    return np.quantile(np.asarray(values), [.025, .975], axis=0), len(values)


def forward_fold(d, test_year):
    train = d[d.year < test_year].copy()
    all_test = d[d.year == test_year]
    test = all_test[all_test.cam.isin(train.cam)].copy()
    return train, test, len(all_test) - len(test)


def predict_ridge(train, test, features, alpha=1.0):
    if len(set(test.cam) - set(train.cam)):
        raise ValueError('new-site predictions require a separate transfer model')
    if train.year.max() >= test.year.min():
        raise ValueError('future data leaked into training')
    levels = sorted(train.cam.unique())
    center = float(train.year.mean())
    z = nuisance(train, 'site_trend', levels, center)
    z_test = nuisance(test, 'site_trend', levels, center)
    y = train.y.to_numpy(dtype=float)
    info = {'training_means': [], 'training_scales': [],
            'training_nuisance_rank': int(np.linalg.matrix_rank(z)),
            'outside_training_range': np.zeros(len(test), dtype=bool)}
    if not features:
        return z_test @ np.linalg.lstsq(z, y, rcond=None)[0], info
    raw = train[features].to_numpy(dtype=float)
    future = test[features].to_numpy(dtype=float)
    mean, sd = raw.mean(axis=0), raw.std(axis=0)
    sd = np.where(sd > 1e-10, sd, 1.0)
    x, x_test = (raw - mean) / sd, (future - mean) / sd
    rx = x - z @ np.linalg.lstsq(z, x, rcond=None)[0]
    ry = y - z @ np.linalg.lstsq(z, y, rcond=None)[0]
    beta = np.linalg.solve(rx.T @ rx + alpha * np.eye(len(features)), rx.T @ ry)
    nuisance_beta = np.linalg.lstsq(z, y - x @ beta, rcond=None)[0]
    info.update(training_means=mean.tolist(), training_scales=sd.tolist(),
                outside_training_range=((future < raw.min(axis=0)) | (future > raw.max(axis=0))).any(axis=1))
    return z_test @ nuisance_beta + x_test @ beta, info


def bootstrap_mean_difference(d, cluster, rng, repeats):
    grouped = d.groupby(cluster).delta.agg(['sum', 'count'])
    sampled = rng.integers(0, len(grouped), (repeats, len(grouped)))
    values = grouped['sum'].to_numpy()[sampled].sum(axis=1) / grouped['count'].to_numpy()[sampled].sum(axis=1)
    return np.quantile(values, [.025, .975])


def plot_relationships(cohort, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colors = {'Adelie': '#4b6cb7', 'Chinstrap': '#7f5a83', 'Gentoo': '#dd8245'}
    fig, axes = plt.subplots(2, 3, figsize=(11, 7), constrained_layout=True)
    for j, species in enumerate(SPECIES):
        d = cohort[cohort.species == species]
        for i, (feature, label) in enumerate([('ice10', 'September sea ice anomaly (10 percentage points)'),
                                             ('salt01', 'September salinity anomaly (0.1 product unit)')]):
            w = d[[feature, 'y']] - d.groupby('cam')[[feature, 'y']].transform('mean')
            ax = axes[i, j]
            ax.scatter(w[feature], w.y, s=27, alpha=.65, color=colors[species], edgecolor='white', linewidth=.3)
            if np.sum(w[feature] ** 2) > 0:
                b = float(np.sum(w[feature] * w.y) / np.sum(w[feature] ** 2))
                grid = np.linspace(w[feature].min(), w[feature].max(), 80)
                ax.plot(grid, b * grid, color=colors[species], linewidth=1.8)
            ax.axhline(0, color='#bbbbbb', lw=.6)
            ax.axvline(0, color='#bbbbbb', lw=.6)
            ax.set_title(f'{species} | n={len(d)}, sites={d.cam.nunique()}')
            ax.set_xlabel(label, fontsize=9)
            if j == 0:
                ax.set_ylabel('Settlement index anomaly')
            ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Within-site relationships on one common observation set\nExploratory marginal associations; source calendar origin remains unresolved', fontsize=12)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run(out, repeats=499):
    out.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(SOURCE)
    rng = np.random.default_rng(20261030)
    cohorts, relationships, coefficients, folds, predictions, supports = [], [], [], [], [], []
    for scope, appendix in [('all_source_labels', False), ('appendix_consistent', True)]:
        cohort = prepare_cohort(raw, appendix)
        cohort['scope'] = scope
        cohorts.append(cohort)
        for species, d in cohort.groupby('species'):
            common = dict(scope=scope, species=species, n=len(d), sites=d.cam.nunique(), years=d.year.nunique())
            supports.append({**common, 'camera_rows': int(d.camera_rows.sum()), 'first_year': int(d.year.min()), 'last_year': int(d.year.max())})
            for feature in MAPPING:
                relationships.append({**common, 'feature': feature, **describe_relationship(d, feature)})
            for mode in ['site', 'site_trend', 'site_year']:
                features = MODELS['J']
                beta, details = fe_fit(d, features, mode)
                intervals = {}
                if mode == 'site_year' and beta is not None:
                    for cluster in ['cam', 'year']:
                        intervals[cluster] = resample_coefficients(d, features, mode, cluster, repeats, rng)
                for j, feature in enumerate(features):
                    record = {**common, **details, 'mode': mode, 'feature': feature,
                              'coefficient': np.nan if beta is None else float(beta[j])}
                    for cluster, (limits, valid) in intervals.items():
                        record.update({f'{cluster}_resample_low': float(limits[0, j]) if limits is not None else np.nan,
                                       f'{cluster}_resample_high': float(limits[1, j]) if limits is not None else np.nan,
                                       f'{cluster}_valid_resamples': valid})
                    coefficients.append(record)
            for year in range(2015, 2021):
                train, test, excluded = forward_fold(d, year)
                status = 'evaluated'
                if test.empty or train.year.nunique() < 3 or len(train) <= np.linalg.matrix_rank(nuisance(train, 'site_trend')):
                    status = 'no_test_or_insufficient_training_variation'
                folds.append(dict(scope=scope, species=species, test_year=year, train_n=len(train),
                                  test_n=len(test), excluded_new_site_n=excluded, status=status,
                                  latest_train_year=int(train.year.max()) if len(train) else None))
                if status != 'evaluated':
                    continue
                for model, features in MODELS.items():
                    pred, information = predict_ridge(train, test, features)
                    for position, (_, row) in enumerate(test.iterrows()):
                        predictions.append(dict(scope=scope, species=species, cam=row.cam, year=year, model=model,
                                                observed=row.y, predicted=float(pred[position]),
                                                error=float(pred[position] - row.y),
                                                outside_training_range=bool(information['outside_training_range'][position]),
                                                latest_train_year=int(train.year.max())))
    co = pd.concat(cohorts, ignore_index=True)
    rel, coef, pred = pd.DataFrame(relationships), pd.DataFrame(coefficients), pd.DataFrame(predictions)
    metrics, paired_intervals, per_year = [], [], []
    for (scope, species), group in pred.groupby(['scope', 'species']):
        errors = group.assign(abs_error=abs(group.error)).pivot(index=['cam', 'year'], columns='model', values='abs_error')
        if errors.isna().any().any():
            raise ValueError('forward models evaluated on different observations')
        for model, model_rows in group.groupby('model'):
            delta = (errors[model] - errors['B']).rename('delta').reset_index()
            metrics.append(dict(scope=scope, species=species, model=model, n=len(model_rows),
                                sites=model_rows.cam.nunique(), years=model_rows.year.nunique(),
                                mae=float(abs(model_rows.error).mean()), rmse=float(np.sqrt(np.mean(model_rows.error ** 2))),
                                mae_difference_vs_B=float(delta.delta.mean()),
                                outside_training_range_n=int(model_rows.outside_training_range.sum())))
            for cluster in ['cam', 'year']:
                limits = bootstrap_mean_difference(delta, cluster, rng, repeats)
                paired_intervals.append(dict(scope=scope, species=species, model=model, cluster=cluster,
                                             mean_delta=float(delta.delta.mean()), low=float(limits[0]), high=float(limits[1]),
                                             n_clusters=delta[cluster].nunique(), repeats=repeats))
            for year, sub in delta.groupby('year'):
                per_year.append(dict(scope=scope, species=species, model=model, year=year, n=len(sub), mae_difference_vs_B=float(sub.delta.mean())))
    tables = {'cohort': co, 'support': pd.DataFrame(supports), 'relationships': rel, 'coefficients': coef,
              'forward_folds': pd.DataFrame(folds), 'forward_predictions': pred,
              'forward_metrics': pd.DataFrame(metrics), 'forward_paired_intervals': pd.DataFrame(paired_intervals),
              'forward_year_differences': pd.DataFrame(per_year)}
    for name, table in tables.items():
        table.to_csv(out / (name + '.csv'), index=False)
    plot_relationships(co[co.scope == 'all_source_labels'], out / 'within_site_relationships.png')
    result = {'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'source_rows': len(raw), 'common_cohort': supports, 'features': MAPPING, 'models': MODELS,
              'forward_years': list(range(2015, 2021)), 'ridge_alpha': 1.0,
              'all_forward_training_precedes_test': bool((pred.latest_train_year < pred.year).all()),
              'prediction_evaluation': 'chronological conditional hindcast using realized heldout-year September environments',
              'test_population': 'previously observed sites only; new-site exclusions recorded in forward_folds.csv',
              'environment_precedes_settlement_verified': False,
              'bootstrap_repeats': repeats, 'bootstrap_scope': 'site and year pairs bootstrap separately; not simultaneous two-way coverage',
              'bootstrap_selection': 'coefficient ranges condition on resamples retaining identifiable exposures and positive residual degrees of freedom',
              'inference_status': 'post-exploration descriptive and model evaluation; no confirmatory p-values',
              'calendar_origin_verified': False, 'causal_effect': False, 'biological_future_projection_validated': False,
              'complete_case_target': 'cameras with all four September inputs, averaged to species/geographic-code/season',
              'observation_units': 'one mean per species × geographic code × nominal season; not independent climate cells',
              'files_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.csv'))}}
    (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(pd.DataFrame(supports).to_string(index=False))
    print(rel[(rel.scope == 'all_source_labels') & rel.feature.isin(['ice10', 'salt01'])].to_string(index=False))
    print(tables['forward_metrics'].to_string(index=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'outputs/relationship_response_v1')
    parser.add_argument('--resamples', type=int, default=499)
    args = parser.parse_args()
    run(args.out, args.resamples)
