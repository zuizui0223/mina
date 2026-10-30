"""Verify saved NDVI summaries, native samples and count-pair calculations."""
from pathlib import Path
import json,hashlib
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];p=ROOT/'outputs/vegetation_annual_ndvi_v1'
a=pd.read_csv(p/'checked_support.csv');pair=pd.read_csv(p/'same_pixel_changes.csv');counts=pd.read_csv(p/'ndvi_count_pairs.csv');native=pd.read_csv(p/'offset_native_checks.csv')
for r in a.itertuples():
 f=p/r.checked_file;assert hashlib.sha256(f.read_bytes()).hexdigest()==r.sha256
 with np.load(f) as z:
  n=np.isfinite(z['daily_ndvi']).sum(axis=0);assert np.array_equal(n,z['valid_dates'])
  assert np.array_equal(np.isfinite(z['annual_median']),n>=2)
  for i,j in zip(*np.where(n>=2)):
   vals=z['daily_ndvi'][:,i,j];vals=vals[np.isfinite(vals)]
   assert np.isclose(np.median(vals),z['annual_median'][i,j])
   assert np.isclose(np.quantile(vals,.75)-np.quantile(vals,.25),z['daily_iqr'][i,j])
for r in native.itertuples():
 f=p/'native'/f'{r.scene_id}_{r.band}.npz';assert hashlib.sha256(f.read_bytes()).hexdigest()==r.array_sha256
 with np.load(f) as z:assert np.array_equal(z['cog'][z['valid']],z['original'][z['valid']])
for r in pair.itertuples():
 with np.load(p/'checked_arrays'/f'{r.site_id}_{r.first_year}.npz') as l,np.load(p/'checked_arrays'/f'{r.site_id}_{r.last_year}.npz') as h:
  x=l['annual_median'];y=h['annual_median'];v=np.isfinite(x)&np.isfinite(y);assert v.sum()==r.common_pixels;assert np.isclose(np.median(y[v]-x[v]),r.median_pixel_ndvi_change)
assert np.allclose((np.log1p(counts.end_count)-np.log1p(counts.start_count))/(counts.end_season-counts.start_season),counts.annual_log1p_count_change)
check=dict(site_years=len(a),sites=a.site_id.nunique(),same_pixel_pairs=len(pair),pairs_100_pixels=int((pair.common_pixels>=100).sum()),sites_100_pixels=pair.loc[pair.common_pixels>=100,'site_id'].nunique(),native_band_checks=len(native),count_pairs=len(counts),all_numerical_checks_passed=True,vegetation_classification_validated=False,causal_effect_estimated=False,p_values_reported=False)
(p/'validation.json').write_text(json.dumps(check,indent=2)+'\n');print(check)
