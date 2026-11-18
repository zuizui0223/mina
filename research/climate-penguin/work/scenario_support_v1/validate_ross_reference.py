"""Independently check phase means against a fresh export of published RData."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--reexport', type=Path, required=True)
args = parser.parse_args()
out = Path(__file__).resolve().parents[2] / 'outputs/ross_phase_reference_v1'
raw = pd.read_csv(args.reexport)
saved = pd.read_csv(out / 'published_processed_table.csv.gz')
pd.testing.assert_frame_equal(raw, saved, check_dtype=False, rtol=1e-12, atol=1e-12)
pairs = pd.read_csv(out / 'trip_phase_pairs.csv')
checks = 0
for window, early, late in [('broad', (14, 22), (36, 43)), ('interior', (15, 21), (37, 42))]:
    p = pairs[pairs.window.eq(window)]
    assert len(p) == 146 and p.birdyear.nunique() == 146
    for row in p.itertuples():
        trip = raw[raw.birdyear.eq(row.birdyear)]
        for phase, bounds in [('early', early), ('late', late)]:
            values = trip.loc[trip.yearweek.between(*bounds), 'support5day'].dropna().to_numpy()
            expected = sum(values) / len(values) if len(values) else np.nan
            assert np.isclose(expected, getattr(row, phase + '_support'), equal_nan=True)
            count = getattr(row, phase + '_records')
            assert (np.isnan(count) and not len(values)) or count == len(values)
            checks += 1
result = dict(status='passed', source_rows=len(raw), paired_phase_checks=checks,
              fresh_rdata_export_sha256=hashlib.sha256(args.reexport.read_bytes()).hexdigest(),
              scope='Source-table equality and individual phase means/counts; not scientific identification')
(out / 'independent_validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
