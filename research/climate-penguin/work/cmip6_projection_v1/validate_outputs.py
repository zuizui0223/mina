"""Offline audit of delivered arrays, coverage, pairing and independent arithmetic."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[2] / 'outputs/cmip6_projection_v1'
manifest=json.loads((OUT/'manifest.json').read_text())
metadata=json.loads((OUT/'source_metadata.json').read_text())
selected=pd.read_csv(OUT/'selected_stores.csv')
climate=pd.read_csv(OUT/'seasonal_climatologies.csv')
changes=pd.read_csv(OUT/'site_model_changes.csv')
ensemble=pd.read_csv(OUT/'site_model_ensemble.csv')
assert len(selected)==27 and len(metadata)==27 and manifest['failures']==[]
assert len(climate)==4770 and len(changes)==3816 and len(ensemble)==1272
assert climate.complete_years.eq(20).all() and ensemble.n_models.eq(3).all()
assert np.isfinite(climate.seasonal_mean).all() and np.isfinite(changes.change).all()
assert np.allclose(changes.change, changes.seasonal_mean-changes.baseline_1995_2014)
code_sha=hashlib.sha256((Path(__file__).parent/'extract.py').read_bytes()).hexdigest()
assert manifest['extraction_code_sha256']==code_sha
for row in metadata:
    assert row['cache_identity']['code_sha256']==code_sha
    assert 'support_sha256' in row['cache_identity']
    assert 'historical_identity_sha256' in row['cache_identity']
    assert row['grid_unchanged_vs_historical']
    if row['experiment_id']!='historical':
        assert row['parent_variant_label']==row['member_id']
monthly=pd.read_csv(OUT/'monthly_ACCESS-CM2_r1i1p1f1_siconc_ssp585.csv.gz')
monthly=monthly[(monthly.location_id=='loc000') & monthly.year.between(2081,2100)]
assert len(monthly)==80
weights=monthly.month.map({8:31,9:30,10:31,11:30})
independent=float((monthly.value*weights).sum()/(20*122))
expected=float(climate[(climate.source_id=='ACCESS-CM2')&(climate.variable_id=='siconc')&(climate.experiment_id=='ssp585')&(climate.period=='2081-2100')&(climate.location_id=='loc000')].seasonal_mean.iloc[0])
assert abs(independent-expected)<1e-10
result=dict(status='passed', checks=[
    '27 selected stores and 27 successful array reads',
    '4770 complete 20-year climatologies',
    '3816 paired historical/future changes',
    '1272 site ensembles, each with all 3 models',
    'all climatologies and changes finite',
    'all scenario parent members match selected historical member',
    'all cache identities include current extraction code and historical support provenance',
    'historical/scenario grids identical within 1e-6 degrees',
    'independent CSV day-weighted mean matches within 1e-10'],
    independent_recomputed_value=independent)
(OUT/'validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
