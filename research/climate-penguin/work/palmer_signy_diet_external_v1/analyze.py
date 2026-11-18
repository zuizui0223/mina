"""Source-pinned, retrospective Palmer–Signy diet comparison.

Climate replication is by season within region. Published Palmer stomach
means are not individual observations and are never expanded to n rows.
"""
from pathlib import Path
import argparse
import hashlib
import io
import itertools
import json
import math
import urllib.request
import zipfile

import numpy as np
import pandas as pd
from scipy.stats import t


ROOT = Path(__file__).resolve().parents[2]
SIGNY_YEARS = list(range(2001, 2010))
PALMER_YEARS = list(range(2009, 2015))
SIGNY_SOURCES = {
    'Adelie': ('eb421e6d-b93b-4174-904b-9a7b0b401403', 'ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d'),
    'Gentoo': ('fb9bd975-e6fe-406c-84be-01e57d612b5e', '6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902'),
}
ICE_SHA256 = 'b21b10743f3a56281d0cf62f55988823f55b645b6d3fbb1bf7c2d366dff1b3ae'


def summarize_signy(raw, species, years):
    if raw.duplicated(['DATE', 'RECORD_ID']).any():
        raise ValueError('duplicate stomach source keys')
    frame = raw.copy()
    dates = pd.to_datetime(frame.DATE, format='%Y-%m-%d')
    if not dates.dt.month.isin([11, 12, 1, 2, 3, 4]).all():
        raise ValueError('unexpected stomach sampling season')
    frame['year'] = dates.dt.year - (dates.dt.month <= 4).astype(int)
    frame = frame[frame.year.isin(years)].copy()
    cols = ['FISH_MASS_g', 'CRUSTACEAN_MASS_g', 'CEPHALOPOD_MASS_g', 'OTHER_FOOD_MASS_g', 'TOTAL_MASS_g', 'EUPHAUSIA_SUPERBA_MASS_g']
    frame[cols] = frame[cols].apply(pd.to_numeric, errors='coerce')
    fish, crust, ceph, other, total, krill = [frame[c] for c in cols]
    food = fish + crust + ceph + other
    legacy = (fish.ge(0) & crust.ge(0) & total.gt(0) & (fish + crust).gt(0)
              & (fish + crust).le(total * 1.05 + .05)
              & (krill.isna() | krill.le(crust * 1.05 + .05)))
    valid = legacy & ceph.ge(0) & other.ge(0) & food.gt(0) & food.le(total * 1.05 + .05)
    frame['fish_food'] = fish / food
    frame['fish_total'] = fish / total
    frame['legacy_fish_crustacean'] = fish / (fish + crust)
    records = []
    for year in years:
        good = frame[valid & frame.year.eq(year)]
        if good.empty:
            raise ValueError(f'no valid stomachs for {species} {year}')
        records.append({
            'region': 'Signy', 'species': species, 'year': year,
            'n_source_stomachs': int(frame.year.eq(year).sum()),
            'n_stomachs': len(good), 'fish_food_mean': float(good.fish_food.mean()),
            'fish_total_mean': float(good.fish_total.mean()),
            'legacy_fish_crustacean_mean': float(good.legacy_fish_crustacean.mean()),
        })
    audit = {
        'species': species, 'n_source': len(frame), 'n_valid': int(valid.sum()),
        'n_excluded': int((~valid).sum()), 'legacy_n_valid': int(legacy.sum()),
        'excluded_keys': frame.loc[~valid, ['DATE', 'RECORD_ID']].astype(str).to_dict('records'),
        'food_total_mass_absolute_difference_max_g': float((food[valid] - total[valid]).abs().max()),
    }
    return pd.DataFrame(records), audit


def annual_ice(raw, sites, years):
    frame = raw[raw.site_id.isin(sites) & raw.year.isin(years) & raw.inner_km.eq(0) & raw.month.isin([8, 9, 10, 11])].copy()
    if frame.duplicated(['site_id', 'year', 'month']).any():
        raise ValueError('duplicate monthly ice keys')
    records = []
    for site in sites:
        for year in years:
            group = frame[frame.site_id.eq(site) & frame.year.eq(year)]
            if len(group) != 4 or set(group.month) != {8, 9, 10, 11}:
                raise ValueError(f'four months required: {site} {year}')
            if not group.complete_month.astype(str).str.lower().eq('true').all():
                raise ValueError(f'incomplete month: {site} {year}')
            if not (group.days.eq(group.expected_days) & group.supported_days.eq(group.expected_days)).all():
                raise ValueError(f'incomplete supported days: {site} {year}')
            values = group.sic_mean.to_numpy(dtype=float)
            if not (np.isfinite(values).all() and ((values >= 0) & (values <= 100)).all()):
                raise ValueError('invalid SIC')
            records.append({'site_id': site, 'year': year, 'sic_aug_nov': float(values.mean())})
    return pd.DataFrame(records)


def palmer_means(raw):
    frame = raw.rename(columns={'season_start_year': 'year'}).copy()
    expected = {(species, year) for species in ['Adelie', 'Gentoo'] for year in PALMER_YEARS}
    if len(frame) != 12 or set(zip(frame.species, frame.year)) != expected:
        raise ValueError('unexpected Palmer species-season cohort')
    fish = pd.to_numeric(frame.fish_mean_pct, errors='coerce')
    if not (np.isfinite(fish).all() and fish.between(0, 100).all()):
        raise ValueError('invalid published fish percentage')
    result = frame[['species', 'year']].copy()
    result['fish_food_mean'] = fish / 100
    result['region'] = 'Palmer'
    return result


def regional_ice(annual, sites):
    frame = annual[annual.site_id.isin(sites)]
    records = []
    for year, group in frame.groupby('year'):
        if len(group) != len(sites) or set(group.site_id) != set(sites):
            raise ValueError('regional proxy support is incomplete or duplicated')
        records.append({'year': int(year), 'sic_aug_nov': float(group.sic_aug_nov.mean())})
    return pd.DataFrame(records)


def exact_permutation(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    xc, yc = x - x.mean(), y - y.mean()
    norm = np.linalg.norm(xc) * np.linalg.norm(yc)
    if not norm:
        return {'n_permutations': math.factorial(len(x)), 'extreme_count': None, 'p_exact': None}
    observed = float(xc @ yc / norm)
    indices = np.array(list(itertools.permutations(range(len(x)))), dtype=np.int16)
    permuted = (xc[indices] @ yc) / norm
    extreme = int(np.count_nonzero(np.abs(permuted) >= abs(observed) - 1e-12))
    return {'n_permutations': len(indices), 'extreme_count': extreme, 'p_exact': extreme / len(indices)}


def describe(frame):
    frame = frame.sort_values('year')
    x, y = frame.sic_aug_nov.to_numpy(float), frame.distance.to_numpy(float)
    years = frame.year.to_numpy(float)
    design = np.column_stack([np.ones(len(x)), x / 10])
    coef = np.linalg.lstsq(design, y, rcond=None)[0]
    resid = y - design @ coef
    inverse = np.linalg.inv(design.T @ design)
    leverage = np.einsum('ij,jk,ik->i', design, inverse, design)
    meat = design.T @ (((resid / (1 - leverage)) ** 2)[:, None] * design)
    covariance = inverse @ meat @ inverse
    radius = float(t.ppf(.975, len(x) - 2) * np.sqrt(covariance[1, 1]))
    r = float(np.corrcoef(x, y)[0, 1])
    loo = [float(np.corrcoef(np.delete(x, i), np.delete(y, i))[0, 1]) for i in range(len(x))]
    trend = np.column_stack([np.ones(len(x)), years - years.mean()])
    xr = x - trend @ np.linalg.lstsq(trend, x, rcond=None)[0]
    yr = y - trend @ np.linalg.lstsq(trend, y, rcond=None)[0]
    circular = [float(np.corrcoef(x, np.roll(y, i))[0, 1]) for i in range(len(x))]
    return {
        'n_seasons': len(x), 'years': [int(z) for z in years],
        'mean_distance': float(y.mean()), 'min_distance': float(y.min()), 'max_distance': float(y.max()),
        'sic_min': float(x.min()), 'sic_max': float(x.max()), 'pearson_r': r,
        'slope_per_10pp': float(coef[1]), 'intercept': float(coef[0]),
        'hc3_slope_95_low': float(coef[1] - radius), 'hc3_slope_95_high': float(coef[1] + radius),
        'leave_one_season_r_min': min(loo), 'leave_one_season_r_max': max(loo),
        'leave_one_season_r': dict(zip([str(int(z)) for z in years], loo)),
        'detrended_r': float(np.corrcoef(xr, yr)[0, 1]),
        'first_difference_r': float(np.corrcoef(np.diff(x), np.diff(y))[0, 1]),
        'circular_extreme_count': sum(abs(z) >= abs(r) - 1e-12 for z in circular),
        'circular_denominator': len(x), **exact_permutation(x, y),
    }


def transport(train, target):
    coef = np.linalg.lstsq(np.column_stack([np.ones(len(train)), train.sic_aug_nov]), train.distance, rcond=None)[0]
    result = target.copy()
    result['predicted_distance'] = coef[0] + coef[1] * result.sic_aug_nov
    result['training_mean_prediction'] = float(train.distance.mean())
    result['in_training_ice_range'] = result.sic_aug_nov.between(train.sic_aug_nov.min(), train.sic_aug_nov.max())
    result['prediction_in_response_range'] = result.predicted_distance.between(0, 1)
    result['model_absolute_error'] = (result.predicted_distance - result.distance).abs()
    result['training_mean_absolute_error'] = (result.training_mean_prediction - result.distance).abs()
    scores = {}
    for name, selected in [('all_target_seasons', result), ('within_training_ice_range', result[result.in_training_ice_range])]:
        scores[name] = {
            'n': len(selected), 'model_mae': float(selected.model_absolute_error.mean()),
            'training_mean_mae': float(selected.training_mean_absolute_error.mean()),
            'model_rmse': float(np.sqrt(((selected.predicted_distance - selected.distance) ** 2).mean())),
            'training_mean_rmse': float(np.sqrt(((selected.training_mean_prediction - selected.distance) ** 2).mean())),
        }
    scores['training_intercept'] = float(coef[0])
    scores['training_slope_per_10pp'] = float(coef[1] * 10)
    return result, scores


def acquire_signy(directory):
    directory.mkdir(parents=True, exist_ok=True)
    manifest = []
    for species, (uid, expected) in SIGNY_SOURCES.items():
        path = directory / f'{species}_diet_summary.csv'
        url = f'https://ramadda.data.bas.ac.uk/repository/entry/show?entryid={uid}&output=zip.tree'
        if not path.exists():
            with urllib.request.urlopen(url, timeout=90) as response:
                archive = zipfile.ZipFile(io.BytesIO(response.read()))
            member = next(x for x in archive.namelist() if x.endswith('_diet_summary.csv'))
            path.write_bytes(archive.read(member))
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'changed source hash: {species}')
        manifest.append({'species': species, 'doi': '10.5285/' + uid, 'url': url, 'summary_sha256': actual})
    return manifest


def run(source_dir, palmer_table, out):
    out.mkdir(parents=True, exist_ok=True)
    manifest = acquire_signy(source_dir)
    signy_parts, audits = [], []
    for species in SIGNY_SOURCES:
        part, audit = summarize_signy(pd.read_csv(source_dir / f'{species}_diet_summary.csv'), species, SIGNY_YEARS)
        signy_parts.append(part); audits.append(audit)
    signy_species = pd.concat(signy_parts, ignore_index=True)
    palmer = pd.read_csv(palmer_table)
    palmer_species = palmer_means(palmer)
    source_hash = hashlib.sha256(palmer_table.read_bytes()).hexdigest()
    manifest.append({'region': 'Palmer', 'doi': '10.1002/ece3.4445', 'table': 'Table 1', 'derived_csv_sha256': source_hash,
                     'unit': 'published per-stomach percentage means; no individual reconstruction'})
    icepath = ROOT / 'outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv'
    ice_hash = hashlib.sha256(icepath.read_bytes()).hexdigest()
    if ice_hash != ICE_SHA256:
        raise ValueError('changed monthly sea-ice input')
    ice = pd.read_csv(icepath)
    sgice = annual_ice(ice, ['GOPT'], SIGNY_YEARS)
    paice = annual_ice(ice, ['BISC', 'LITC'], PALMER_YEARS)
    regional = regional_ice(paice, ['BISC', 'LITC'])
    manifest.append({'source': 'OSI SAF derived 0-100 km August-November monthly SIC', 'path': str(icepath.relative_to(ROOT)), 'sha256': ice_hash})
    annual_frames, summaries, sensitivity = [], {}, []
    for region, species, exposure in [('Signy', signy_species, sgice), ('Palmer', palmer_species, regional)]:
        wide = species.pivot(index='year', columns='species', values='fish_food_mean').reset_index()
        wide['signed_gap'] = wide.Gentoo - wide.Adelie
        wide['distance'] = wide.signed_gap.abs()
        wide['region'] = region
        wide = wide.merge(exposure[['year', 'sic_aug_nov']], on='year', validate='one_to_one').sort_values('year')
        annual_frames.append(wide)
        summaries[region] = describe(wide)
    annual = pd.concat(annual_frames, ignore_index=True)
    for proxy in ['BISC', 'LITC']:
        alternative = annual[annual.region.eq('Palmer')].drop(columns='sic_aug_nov').merge(paice[paice.site_id.eq(proxy)], on='year', validate='one_to_one')
        sensitivity.append({'scope': 'Palmer_proxy', 'variant': proxy, **describe(alternative)})
    for metric in ['fish_total_mean', 'legacy_fish_crustacean_mean']:
        alternative = signy_species.pivot(index='year', columns='species', values=metric).reset_index()
        alternative['distance'] = (alternative.Gentoo - alternative.Adelie).abs()
        alternative = alternative.merge(sgice[['year', 'sic_aug_nov']], on='year', validate='one_to_one')
        sensitivity.append({'scope': 'Signy_denominator', 'variant': metric, **describe(alternative)})
    transported, scores = transport(annual_frames[0], annual_frames[1])
    summary = {
        'status': 'computed; independent verification recorded in VALIDATION.json', 'analysis_date': '2026-11-06',
        'estimand': 'absolute gentoo-Adelie difference in equal-stomach mean fish fraction among recovered food',
        'n_regions': 2, 'n_region_seasons': 15, 'n_unique_calendar_start_years': 14,
        'regions': summaries, 'transport': scores, 'source_audit': audits,
        'palmer_scope': 'different colonies within Palmer region; year means from published Table 1',
        'inference_scope': 'exploratory; exact p assumes exchangeable years; no project-wide multiplicity correction; no pooled independent 15-season claim',
        'sensitivity': sensitivity,
    }
    signy_species.to_csv(out / 'signy_species_seasons.csv', index=False)
    palmer_species.to_csv(out / 'palmer_species_seasons.csv', index=False)
    annual.to_csv(out / 'annual_pair_comparison.csv', index=False)
    effect_columns = ['n_seasons', 'mean_distance', 'pearson_r', 'slope_per_10pp',
                      'hc3_slope_95_low', 'hc3_slope_95_high', 'p_exact',
                      'leave_one_season_r_min', 'leave_one_season_r_max', 'detrended_r']
    pd.DataFrame([{'region': region, **{k: result[k] for k in effect_columns}}
                  for region, result in summaries.items()]).to_csv(out / 'region_effects.csv', index=False)
    pd.concat([sgice, paice]).to_csv(out / 'annual_ice_proxies.csv', index=False)
    selected = ice[(ice.site_id.eq('GOPT') & ice.year.isin(SIGNY_YEARS) | ice.site_id.isin(['BISC', 'LITC']) & ice.year.isin(PALMER_YEARS)) & ice.inner_km.eq(0)].sort_values(['site_id', 'year', 'month'])
    selected.to_csv(out / 'monthly_ice_source_subset.csv', index=False)
    transported.to_csv(out / 'signy_to_palmer_transport.csv', index=False)
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (out / 'source_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'regions': summaries, 'transport': scores, 'source_audit': audits}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--palmer-table', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT / 'outputs/palmer_signy_diet_external_v1')
    args = parser.parse_args()
    run(args.source_dir, args.palmer_table, args.out)
