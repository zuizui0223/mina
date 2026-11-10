"""Observed positive-fish-mass frequency and conditional meal composition."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import itertools
import json
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
YEARS = list(range(2001, 2010))


def previous_analysis():
    path = ROOT / 'work/palmer_signy_diet_external_v1/analyze.py'
    spec = importlib.util.spec_from_file_location('external_diet', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_stomachs(raw, species, years):
    if raw.duplicated(['DATE', 'RECORD_ID']).any():
        raise ValueError('duplicate stomach keys')
    frame = raw.copy()
    dates = pd.to_datetime(frame.DATE, format='%Y-%m-%d')
    if not dates.dt.month.isin([11, 12, 1, 2, 3, 4]).all():
        raise ValueError('unexpected sampling season')
    frame['year'] = dates.dt.year - (dates.dt.month <= 4).astype(int)
    frame = frame[frame.year.isin(years)].copy()
    columns = ['FISH_MASS_g', 'CRUSTACEAN_MASS_g', 'CEPHALOPOD_MASS_g',
               'OTHER_FOOD_MASS_g', 'TOTAL_MASS_g', 'EUPHAUSIA_SUPERBA_MASS_g']
    frame[columns] = frame[columns].apply(pd.to_numeric, errors='coerce')
    f, c, ceph, other, total, krill = [frame[col] for col in columns]
    food = f + c + ceph + other
    valid = (np.isfinite(frame[columns[:-1]]).all(axis=1)
             & f.ge(0) & c.ge(0) & ceph.ge(0) & other.ge(0) & total.gt(0)
             & (f + c).gt(0) & (f + c).le(total*1.05 + .05)
             & (krill.isna() | krill.le(c*1.05 + .05))
             & food.gt(0) & food.le(total*1.05 + .05))
    frame['food_mass_g'] = food
    frame['fish_fraction'] = f / food
    frame['species'] = species
    audit = {'species': species, 'n_source': len(frame), 'n_valid': int(valid.sum()),
             'n_excluded': int((~valid).sum()),
             'excluded_keys': frame.loc[~valid, ['DATE', 'RECORD_ID']].to_dict('records')}
    return frame[valid].copy(), audit


def annual_components(stomachs):
    rows = []
    for (species, year), group in stomachs.groupby(['species', 'year']):
        positive = group[group.FISH_MASS_g.gt(0)]
        p = len(positive)/len(group)
        conditional = float(positive.fish_fraction.mean()) if len(positive) else np.nan
        mean = float(group.fish_fraction.mean())
        if len(positive) and not np.isclose(p*conditional, mean, rtol=1e-12, atol=1e-12):
            raise ValueError('component identity failed')
        rows.append({'species': species, 'year': int(year), 'n_stomachs': len(group),
                     'n_positive_fish_mass': len(positive), 'positive_mass_frequency': p,
                     'conditional_fish_fraction': conditional, 'mean_fish_fraction': mean,
                     'mean_fish_mass_g': float(group.FISH_MASS_g.mean()),
                     'mean_crustacean_mass_g': float(group.CRUSTACEAN_MASS_g.mean()),
                     'mean_food_mass_g': float(group.food_mass_g.mean())})
    return pd.DataFrame(rows)


def slope_per_10pp(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if not np.isfinite(x).all() or not np.isfinite(y).all() or np.ptp(x) == 0:
        raise ValueError('nonfinite values or constant exposure')
    return float(np.linalg.lstsq(np.column_stack([np.ones(len(x)), x/10]), y, rcond=None)[0][1])


def decompose(x, p, c):
    x, p, c = [np.asarray(values, float) for values in (x, p, c)]
    if not np.isfinite(p).all() or not np.isfinite(c).all():
        raise ValueError('undefined component; do not fill zero-positive seasons')
    if not ((p >= 0) & (p <= 1) & (c >= 0) & (c <= 1)).all():
        raise ValueError('component outside fraction range')
    P, C = p.mean(), c.mean()
    terms = pd.DataFrame({'frequency': C*(p-P), 'composition': P*(c-C),
                          'covariation': (p-P)*(c-C)})
    slopes = {name: slope_per_10pp(x, terms[name]) for name in terms}
    mean_slope = slope_per_10pp(x, p*c)
    if not np.allclose(terms.sum(axis=1) + P*C, p*c, rtol=1e-12, atol=1e-12):
        raise ValueError('value reconstruction failed')
    if not np.isclose(sum(slopes.values()), mean_slope, rtol=1e-12, atol=1e-12):
        raise ValueError('slope reconstruction failed')
    return terms, {'mean_frequency': float(P), 'mean_conditional_fraction': float(C),
                   'constant_product_of_means': float(P*C),
                   'mean_fish_fraction': float((p*c).mean()),
                   'covariation_mean': float(terms.covariation.mean()),
                   'component_slopes_per_10pp': slopes,
                   'sum_component_slopes_per_10pp': sum(slopes.values()),
                   'mean_response_slope_per_10pp': mean_slope,
                   'signed_slope_fraction': {k:v/mean_slope for k,v in slopes.items()} if abs(mean_slope)>1e-12 else None}


def exact_component_family(x, components):
    x = np.asarray(x, float)
    if not np.isfinite(x).all() or np.ptp(x) == 0:
        raise ValueError('invalid exposure')
    names = list(components)
    values = np.column_stack([components[name] for name in names]).astype(float)
    if not np.isfinite(values).all() or len(values) != len(x):
        raise ValueError('undefined component')
    xc = x-x.mean(); yc = values-values.mean(axis=0)
    norms = np.linalg.norm(xc)*np.linalg.norm(yc, axis=0)
    eligible = norms > 0
    indices = np.array(list(itertools.permutations(range(len(x)))), dtype=np.int16)
    observed = np.zeros(len(names))
    permuted = np.zeros((len(indices), len(names)))
    observed[eligible] = (xc @ yc[:, eligible]) / norms[eligible]
    permuted[:, eligible] = (xc[indices] @ yc[:, eligible]) / norms[eligible]
    maximum = np.max(np.abs(permuted), axis=1)
    results = {}
    for i, name in enumerate(names):
        if not eligible[i]:
            results[name] = {'status':'constant', 'r':None, 'p_exact':None, 'p_max2':None}
            continue
        raw = int(np.sum(np.abs(permuted[:, i]) >= abs(observed[i])-1e-12))
        adjusted = int(np.sum(maximum >= abs(observed[i])-1e-12))
        results[name] = {'status':'estimable', 'r':float(observed[i]),
                         'extreme_count':raw, 'max2_extreme_count':adjusted,
                         'p_exact':raw/len(indices), 'p_max2':adjusted/len(indices)}
    return {'n_permutations':len(indices), 'n_prespecified_components':len(names),
            'n_variable_components':int(eligible.sum()), 'components':results}


def association(frame, column, old):
    if np.ptp(frame[column]) == 0:
        return {'status':'constant', 'n_seasons':len(frame), 'pearson_r':None,
                'slope_per_10pp':0., 'mean_value':float(frame[column].mean())}
    result = old.describe(frame[['year', 'sic_aug_nov', column]].rename(columns={column:'distance'}))
    result['mean_value'] = result.pop('mean_distance')
    result['min_value'] = result.pop('min_distance')
    result['max_value'] = result.pop('max_distance')
    result['status'] = 'estimable'
    return result


def palmer_reference(source):
    source = source[source.prey_category.eq('fish')].copy()
    rows = []
    for row in source.itertuples():
        low_p, high_p = row.occurrence_rounding_lower_pct, row.occurrence_rounding_upper_pct
        if low_p <= 0:
            raise ValueError('undefined detection-conditioned reference ratio')
        rows.append({'species':row.species, 'year':row.season_start_year,
                     'reported_mean_fish_pct':row.mean_pct, 'reported_occurrence_pct':row.occurrence_pct,
                     'detection_conditioned_fish_fraction_reference':row.mean_pct/row.occurrence_pct,
                     'rounding_lower_fraction':row.mean_rounding_lower_pct/high_p,
                     'rounding_upper_fraction':min(1.,row.mean_rounding_upper_pct/low_p),
                     'scope':'assumes identical stomach set and zero fish fraction in nondetections; not positive-mass conditional fraction'})
    return pd.DataFrame(rows)


def run(source_dir, out):
    old = previous_analysis()
    manifest = old.acquire_signy(source_dir)
    parts, audits = [], []
    for species in ['Adelie','Gentoo']:
        raw = pd.read_csv(source_dir/f'{species}_diet_summary.csv')
        valid, audit = valid_stomachs(raw,species,YEARS)
        annual = annual_components(valid)
        prior, _ = old.summarize_signy(raw,species,YEARS)
        check = annual.merge(prior,on=['species','year'],validate='one_to_one')
        if not np.allclose(check.mean_fish_fraction,check.fish_food_mean,rtol=1e-12,atol=1e-12):
            raise ValueError('mean differs from completed external comparison')
        if not np.array_equal(check.n_stomachs_x,check.n_stomachs_y):
            raise ValueError('stomach cohort changed')
        parts.append(annual); audits.append(audit)
    icepath=ROOT/'outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv'
    ice_sha=hashlib.sha256(icepath.read_bytes()).hexdigest()
    if ice_sha != old.ICE_SHA256:
        raise ValueError('monthly SIC source changed')
    ice=old.annual_ice(pd.read_csv(icepath),['GOPT'],YEARS)
    annual=pd.concat(parts,ignore_index=True).merge(ice[['year','sic_aug_nov']],on='year',validate='many_to_one')
    gentoo=annual[annual.species.eq('Gentoo')].sort_values('year').reset_index(drop=True)
    if len(gentoo)!=9 or gentoo.n_stomachs.sum()!=73 or gentoo.n_positive_fish_mass.min()<1:
        raise ValueError('specified nine-season gentoo support is not complete')
    primary={'frequency':'positive_mass_frequency','composition':'conditional_fish_fraction'}
    family=exact_component_family(gentoo.sic_aug_nov,{key:gentoo[col] for key,col in primary.items()})
    associations={key:association(gentoo,col,old) for key,col in primary.items()}
    for key in primary:
        associations[key].update(family['components'][key])
    mean_association=association(gentoo,'mean_fish_fraction',old)
    terms,accounting=decompose(gentoo.sic_aug_nov,gentoo.positive_mass_frequency,gentoo.conditional_fish_fraction)
    terms.insert(0,'year',gentoo.year)
    terms['mean_fish_fraction']=gentoo.mean_fish_fraction
    terms['sic_aug_nov']=gentoo.sic_aug_nov
    leave_out=[]
    for year in YEARS:
        kept=gentoo[gentoo.year.ne(year)]
        _,result=decompose(kept.sic_aug_nov,kept.positive_mass_frequency,kept.conditional_fish_fraction)
        leave_out.append({'omitted_year':year,**result['component_slopes_per_10pp'],
                          'mean_response':result['mean_response_slope_per_10pp']})
    masses={col:{'mean_g':float(gentoo[col].mean()),'min_g':float(gentoo[col].min()),
                  'max_g':float(gentoo[col].max()),'pearson_r':float(np.corrcoef(gentoo.sic_aug_nov,gentoo[col])[0,1]),
                  'slope_g_per_10pp':slope_per_10pp(gentoo.sic_aug_nov,gentoo[col])}
            for col in ['mean_fish_mass_g','mean_crustacean_mass_g','mean_food_mass_g']}
    palmerpath=ROOT/'work/palmer_signy_diet_external_v1/sources/pickett2018_table1_long.csv'
    reference=palmer_reference(pd.read_csv(palmerpath))
    summary={'analysis_date':'2026-11-06','primary_species':'Gentoo','n_seasons':9,'n_stomachs':73,
             'definitions':{'frequency':'recorded fish wet mass > 0','composition':'equal-stomach fish fraction conditional on positive fish wet mass',
                            'food_denominator':'fish + crustaceans + cephalopods + other food'},
             'source_audit':audits,'component_associations':associations,'mean_response_association':mean_association,
             'permutation_family':family,'slope_accounting':accounting,'recovered_mass_descriptives':masses,
             'interpretation':'post hoc description of known association; no causal, individual-switching or energy-intake estimate',
             'palmer_reference_scope':'reported-detection reference only; occurrence definitions differ; no regional component tests'}
    manifest.extend([{'source':'monthly SIC','sha256':ice_sha,'path':str(icepath.relative_to(ROOT))},
                     {'source':'Palmer Table 1 long extraction','sha256':hashlib.sha256(palmerpath.read_bytes()).hexdigest(),'path':str(palmerpath.relative_to(ROOT))}])
    out.mkdir(parents=True,exist_ok=True)
    annual.to_csv(out/'species_season_components.csv',index=False)
    gentoo.to_csv(out/'gentoo_primary_nine_seasons.csv',index=False)
    terms.to_csv(out/'annual_accounting_terms.csv',index=False)
    pd.DataFrame(leave_out).to_csv(out/'leave_one_season_accounting.csv',index=False)
    reference.to_csv(out/'palmer_reported_detection_reference.csv',index=False)
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
    (out/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'component_associations':associations,'slope_accounting':accounting,'recovered_mass_descriptives':masses},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-dir',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=ROOT/'outputs/signy_diet_components_v1')
    args=parser.parse_args()
    run(args.source_dir,args.out)
