"""Exploratory block bootstrap and leave-one-year-out diagnostics, not causal CIs."""
from pathlib import Path
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
points=pd.concat([pd.read_csv(OUT/'exploratory_correlation_points.csv'),pd.read_csv(OUT/'ocean_correlation_points.csv')],ignore_index=True)
rng=np.random.default_rng(20261029);rows=[];loo=[]
def within(a):
    w=a[['x','y']]-a.groupby('cam')[['x','y']].transform('mean')
    return float(w.x.corr(w.y)) if len(w)>2 else np.nan
for (species,predictor),g in points.groupby(['species','predictor']):
    assert not g.duplicated(['cam','season_start_year']).any()
    counts=g.groupby('cam').size();a=g[g.cam.isin(counts[counts>=2].index)].copy()
    w=a[['x','y']]-a.groupby('cam')[['x','y']].transform('mean')
    sufficient=pd.DataFrame({'cam':a.cam,'xx':w.x**2,'yy':w.y**2,'xy':w.x*w.y}).groupby('cam')[['xx','yy','xy']].sum().to_numpy()
    ix=rng.integers(0,len(sufficient),(2000,len(sufficient)));s=sufficient[ix].sum(axis=1)
    denom=np.sqrt(s[:,0]*s[:,1]);boot=s[denom>0,2]/denom[denom>0]
    full=within(a)
    drops=[]
    for dimension in ['cam','season_start_year']:
        values=[]
        for excluded in a[dimension].unique():
            r=within(a[a[dimension]!=excluded]);values.append(r)
            loo.append(dict(species=species,predictor=predictor,excluded_dimension=dimension,excluded_value=str(excluded),within_r=r))
        values=np.asarray(values);values=values[np.isfinite(values)]
        drops.append((float(values.min()),float(values.max())))
    rows.append(dict(species=species,predictor=predictor,code_seasons=len(a),geographic_codes=a.cam.nunique(),within_r=full,site_bootstrap_low=float(np.quantile(boot,.025)),site_bootstrap_high=float(np.quantile(boot,.975)),leave_site_min=drops[0][0],leave_site_max=drops[0][1],leave_year_min=drops[1][0],leave_year_max=drops[1][1],note='Exploratory site-block resampling; shared years and regional dependence not resolved'))
d=pd.DataFrame(rows);d.to_csv(OUT/'correlation_robustness_summary.csv',index=False)
pd.DataFrame(loo).to_csv(OUT/'correlation_leave_one_out.csv',index=False)
print(d[d.predictor.isin(['near_sic_mean_month9','ocean_m9_surface_salinity'])].drop(columns='note').to_string(index=False))
trends=[]
for species,g in points[points.predictor=='ocean_m9_surface_salinity'].groupby('species'):
    v=g[['x','y','season_start_year']]-g.groupby('cam')[['x','y','season_start_year']].transform('mean')
    z=v.season_start_year.to_numpy();den=z@z
    trends.append({'species':species,'salt_fixed_site_linear_slope_per_year':float(z@v.x/den),'settlement_index_fixed_site_linear_slope_per_year':float(z@v.y/den),'note':'descriptive nominal-year trends, not attribution'})
pd.DataFrame(trends).to_csv(OUT/'salinity_common_trend_diagnostic.csv',index=False)
