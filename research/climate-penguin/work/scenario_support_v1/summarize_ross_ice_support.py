"""Summarize retained location ensembles without treating draws as replicates."""
from pathlib import Path
import hashlib
import json
import pandas as pd

out = Path(__file__).resolve().parents[2] / 'outputs' / 'ross_ensemble_ice_v1'
d = pd.read_csv(out / 'interval_support.csv.gz')
assert d.draws.eq(500).all()
d['month'] = pd.to_datetime(d.time1, utc=True).dt.month
d['year'] = pd.to_datetime(d.time1, utc=True).dt.year
cols = ['sic_valid', 'sic_under15', 'drift_valid', 'drift_nominal',
        'drift_wind', 'drift_noice', 'drift_overlap_half']

def summarize(g):
    result = dict(intervals=len(g), birds=g.bird_fn.nunique(),
                  bird_years=len(g[['bird_fn', 'season']].drop_duplicates()),
                  any_drift=int(g.drift_valid.gt(0).sum()),
                  majority_drift=int(g.drift_valid_fraction.ge(.5).sum()),
                  all_draws_drift=int(g.drift_valid_fraction.eq(1).sum()))
    result.update({c: float(g[c + '_fraction'].mean()) for c in cols})
    return result

for keys, name in [(['month'], 'monthly_support.csv'),
                   (['year', 'month'], 'year_month_support.csv')]:
    records = []
    for key, g in d.groupby(keys):
        key = key if isinstance(key, tuple) else (key,)
        records.append(dict(zip(keys, key), **summarize(g)))
    pd.DataFrame(records).to_csv(out / name, index=False)

metadata = dict(
    source_sha256=hashlib.sha256((out / 'interval_support.csv.gz').read_bytes()).hexdigest(),
    aggregation='Equal-weight interval means; all intervals have 500 model location draws',
    independence='Intervals, draws and bird-years are not independent biological replicates',
    overall=summarize(d))
(out / 'summary_validation.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(json.dumps(metadata))
