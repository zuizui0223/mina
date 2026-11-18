"""Separate response origin from interval scale in existing scenario regressions."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'work/relationship_response_v1'))
from analyze import fe_fit

out = root / 'outputs/settlement_origin_refresh_v1'
out.mkdir(exist_ok=True)
source = root / 'outputs/relationship_response_v1/cohort.csv'
data = pd.read_csv(source)
frozen_path = root / 'outputs/four_environment_scenarios_v1/coefficients.csv'
frozen = pd.read_csv(frozen_path)
features = ['airC', 'ice10', 'salt01', 'waterC']
rows = []
for (scope, species), d in data.groupby(['scope', 'species']):
    for mode in ['site', 'site_year']:
        beta, _ = fe_fit(d, features, mode)
        reference = frozen[(frozen.scope == scope) & (frozen.species == species) & (frozen['mode'] == mode)]
        assert len(reference) == 1
        assert np.allclose(beta, reference[features].to_numpy()[0], atol=1e-9, rtol=1e-9)
        for label, scale, offset in [('global_offset', 1., 183.),
                                     ('different_scale', 2., 183.),
                                     ('site_offset', 1., d.cam.map({s: i * 7. for i, s in enumerate(sorted(d.cam.unique()))}).to_numpy())]:
            modified = d.copy()
            modified.y = d.y * scale + offset
            other, _ = fe_fit(modified, features, mode)
            error = float(np.max(np.abs(other - scale * beta)))
            assert np.allclose(other, scale * beta, atol=1e-9, rtol=1e-9)
            rows.append(dict(scope=scope, species=species, mode=mode,
                             transformation=label, maximum_coefficient_error=error))
        # Year-varying origins are absorbed only by the model with year effects.
        if mode == 'site_year':
            modified = d.copy()
            modified.y = d.y + (d.year - d.year.min()) ** 2
            other, _ = fe_fit(modified, features, mode)
            error = float(np.max(np.abs(other - beta)))
            assert np.allclose(other, beta, atol=1e-9, rtol=1e-9)
            rows.append(dict(scope=scope, species=species, mode=mode,
                             transformation='year_offset', maximum_coefficient_error=error))
pd.DataFrame(rows).to_csv(out / 'offset_invariance_checks.csv', index=False)
receipt = dict(status='passed', checks=len(rows), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
               frozen_coefficients_sha256=hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
               frozen_coefficient_rows_checked=len(frozen),
               maximum_coefficient_error=max(r['maximum_coefficient_error'] for r in rows),
               scope='Algebraic response transformation checks, not proof of date encoding or day units',
               conclusion='A fixed additive origin does not affect environmental slopes or beta times environmental change; unknown scale does.')
(out / 'offset_validation.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
