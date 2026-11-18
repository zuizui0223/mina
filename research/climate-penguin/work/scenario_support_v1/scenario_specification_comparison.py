"""Compare frozen scenario specifications without treating them as random draws."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[2]
out = root / 'outputs/scenario_specification_comparison_v1'
out.mkdir(exist_ok=True)
paths = ['conditional_response_v1/conditional_summary.csv',
         'four_environment_scenarios_v1/summary.csv',
         'conditional_response_v1/validation.json',
         'four_environment_scenarios_v1/validation.json',
         'conditional_response_v1/climate_transformations.csv']
two, four = [pd.read_csv(root / 'outputs' / p) for p in paths[:2]]
v2, v4 = [json.loads((root / 'outputs' / p).read_text()) for p in paths[2:4]]
assert v2['inputs']['outputs/relationship_response_v1/cohort.csv'] == v4['input_sha256']['relationship_response_v1/cohort.csv']
climate = pd.read_csv(root / 'outputs' / paths[4])
members = climate[['source_id', 'member_id']].drop_duplicates()
assert not members.source_id.duplicated().any()
two = two.merge(members, on='source_id', validate='many_to_one')
keys = ['scope', 'species', 'mode', 'transform', 'source_id', 'member_id', 'experiment_id', 'period']
paired = two.merge(four, on=keys, suffixes=('_two', '_four'), validate='one_to_one', how='outer', indicator=True)
assert len(paired) == 288 and paired._merge.eq('both').all()
assert paired.species_sites.eq(paired.sites).all()
assert paired.invalid_ice_two.eq(paired.invalid_ice_four).all()
assert paired.mean_index_shift_two.isna().equals(paired.mean_index_shift_four.isna())
valid = paired.mean_index_shift_two.notna() & paired.mean_index_shift_four.notna()
paired['comparison_available'] = valid
paired['opposite_sign'] = pd.Series(pd.NA, index=paired.index, dtype='boolean')
paired.loc[valid, 'opposite_sign'] = (paired.loc[valid, 'mean_index_shift_two'] * paired.loc[valid, 'mean_index_shift_four']).lt(0)
paired['four_minus_two_days'] = paired.mean_index_shift_four - paired.mean_index_shift_two
paired.drop(columns='_merge').to_csv(out / 'paired_specifications.csv', index=False)
long = pd.concat([two.assign(response_model='air_ice').rename(columns={'species_sites':'sites'}),
                  four.assign(response_model='air_ice_salt_water')], ignore_index=True)
group = ['scope', 'species', 'experiment_id', 'period', 'transform']
rows = []
for key, a in long.groupby(group):
    assert len(a) == 12
    y = a.mean_index_shift.dropna()
    rows.append(dict(zip(group, key), planned_specifications=len(a), valid_specifications=len(y),
                     unavailable_specifications=int(a.mean_index_shift.isna().sum()),
                     negative=int(y.lt(0).sum()), zero=int(y.eq(0).sum()), positive=int(y.gt(0).sum()),
                     minimum_days=float(y.min()) if len(y) else np.nan,
                     maximum_days=float(y.max()) if len(y) else np.nan,
                     complete_support=len(y)==12,
                     direction='mixed' if y.lt(0).any() and y.gt(0).any() else
                         ('negative' if len(y) and y.lt(0).all() else 'positive' if len(y) and y.gt(0).all() else 'zero_or_unavailable')))
summary = pd.DataFrame(rows)
summary.to_csv(out / 'specification_ranges.csv', index=False)
fekeys = [k for k in keys if k != 'mode'] + ['response_model']
fe = long.pivot(index=fekeys, columns='mode', values='mean_index_shift').reset_index()
fe['comparison_available'] = fe[['site', 'site_year']].notna().all(axis=1)
fe['opposite_sign'] = pd.Series(pd.NA, index=fe.index, dtype='boolean')
mask = fe.comparison_available
fe.loc[mask, 'opposite_sign'] = (fe.loc[mask, 'site'] * fe.loc[mask, 'site_year']).lt(0)
fe.to_csv(out / 'year_adjustment_comparisons.csv', index=False)
receipt = dict(status='descriptive_specification_comparison', paired_rows=len(paired), valid_pairs=int(valid.sum()),
               model_sign_reversals=int(paired.opposite_sign.sum()),
               year_adjustment_pairs=len(fe), valid_year_adjustment_pairs=int(mask.sum()),
               year_adjustment_sign_reversals=int(fe.opposite_sign.sum()),
               range_groups=len(summary), input_sha256={p:hashlib.sha256((root/'outputs'/p).read_bytes()).hexdigest() for p in paths},
               limits=['Ranges are selected-specification ranges, not confidence or prediction intervals',
                       'Models and transformations are not probability-weighted samples',
                       'Day-scale interpretation supported by settlement_origin_refresh_v1; no absolute dates',
                       'Changes between models are not causal contributions of added variables',
                       'Invalid specifications retained; no direction claim from incomplete support'])
(out/'validation.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['input_sha256','limits']}))
print(summary[(summary.scope=='all_source_labels') & (summary['transform']=='bounded')].to_string(index=False))
