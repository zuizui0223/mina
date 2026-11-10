"""Delete each camera from every frozen salinity specification; no p-value selection."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'outputs/relationship_response_v1/cohort.csv'
BASE = ROOT / 'outputs/salinity_sensitivity_v1/specifications.csv'
OUT = ROOT / 'outputs/salinity_site_influence_v1'
CONTROLS = {'none': [], 'ice': ['ice10'], 'ice_water': ['ice10', 'waterC'],
            'ice_water_air': ['ice10', 'waterC', 'airC']}


def estimate(a, mode, controls):
    z = pd.get_dummies(a.cam, dtype=float).to_numpy()
    if mode == 'site_year':
        z = np.column_stack([z, pd.get_dummies(a.year, drop_first=True, dtype=float)])
    if controls:
        z = np.column_stack([z, a[controls].to_numpy()])
    v = a[['salt01', 'y']].to_numpy()
    residual = v - z @ np.linalg.lstsq(z, v, rcond=None)[0]
    design = np.column_stack([z, a.salt01])
    rank = np.linalg.matrix_rank(design)
    assert rank == np.linalg.matrix_rank(z) + 1, 'Salt not identifiable'
    assert len(a) > rank, 'No residual degrees of freedom'
    xx, yy = (residual ** 2).sum(axis=0)
    assert min(xx, yy) > 1e-12
    r = float(np.corrcoef(residual.T)[0, 1])
    beta = float(residual[:, 0] @ residual[:, 1] / xx)
    # Separate full-design pseudoinverse fit, including its residual sum of squares.
    full = sm.OLS(a.y.to_numpy(), design).fit()
    reduced = sm.OLS(a.y.to_numpy(), z).fit()
    assert np.isclose(beta, full.params[-1], atol=1e-8)
    assert np.isclose(r*r, (reduced.ssr-full.ssr)/reduced.ssr, atol=1e-8)
    return dict(partial_r=r, coefficient_per_01=beta, n=len(a), sites=a.cam.nunique(),
                years=a.year.nunique(), residual_df=len(a)-rank)


def main():
    OUT.mkdir(exist_ok=True)
    d = pd.read_csv(SRC)
    baseline = pd.read_csv(BASE)
    assert not d.duplicated(['scope', 'species', 'cam', 'year']).any()
    assert np.isfinite(d[['salt01','y','airC','ice10','waterC']]).all().all()
    rows, summaries = [], []
    for b in baseline.to_dict('records'):
        a = d[(d.scope == b['scope']) & (d.species == b['species'])]
        keys = {k: b[k] for k in ['scope','species','mode','controls']}
        full = estimate(a, b['mode'], CONTROLS[b['controls']])
        assert np.isclose(full['partial_r'], b['partial_r'], atol=1e-10)
        assert np.isclose(full['coefficient_per_01'], b['coefficient_per_01'], atol=1e-8)
        fits = []
        for cam in sorted(a.cam.unique()):
            q = estimate(a[a.cam != cam], b['mode'], CONTROLS[b['controls']])
            q.update(keys, deleted_cam=cam, removed_rows=int((a.cam == cam).sum()))
            fits.append(q)
        rows.extend(fits)
        low = min(fits, key=lambda x: x['partial_r'])
        high = max(fits, key=lambda x: x['partial_r'])
        summaries.append(dict(**keys, **full, delete_min=low['partial_r'],
                              delete_max=high['partial_r'], min_deleted_cam=low['deleted_cam'],
                              max_deleted_cam=high['deleted_cam'],
                              sign_reversals=sum(q['partial_r']*full['partial_r'] < 0 for q in fits)))
    pd.DataFrame(rows).to_csv(OUT/'site_deletions.csv', index=False)
    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT/'summary.csv', index=False)
    assert len(summary) == 48
    manifest = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [SRC, BASE, Path(__file__)]}
    (OUT/'validation.json').write_text(json.dumps(dict(inputs=manifest, specifications=48,
        site_deletion_fits=len(rows), full_design_checks=len(rows)+48,
        baseline_matches=48, status='passed',
        limits='Deletion ranges are not confidence intervals; cameras need not be independent colonies.'),
        indent=2)+'\n', encoding='utf-8')
    print(summary[(summary.scope=='all_source_labels') & (summary.controls=='ice_water_air')].to_string(index=False))


if __name__ == '__main__':
    main()
