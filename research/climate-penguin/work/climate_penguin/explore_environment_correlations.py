"""Descriptive between/within-location correlations. No p values or causal claims."""
from pathlib import Path
import pandas as pd,numpy as np,argparse
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
ap=argparse.ArgumentParser();ap.add_argument('--input',default='extended_analysis_cohort.csv');ap.add_argument('--prefix',default='exploratory');ap.add_argument('--predictors',nargs='+',default=['spgmedian','near_sic_mean_month9','far_sic_mean_month9','edge_distance_km','drift_m9_east_km_day','drift_m9_north_km_day']);args=ap.parse_args()
p=pd.read_csv(OUT/args.input)
predictors=args.predictors
p.loc[p.drift_m9_coverage_fraction.lt(.8)|p.drift_m9_n_supported_days.isna(),['drift_m9_east_km_day','drift_m9_north_km_day']]=np.nan
rows=[];points=[]
for species,g in p.groupby('species'):
    for x in predictors:
        a=g.dropna(subset=[x,'settlement']).groupby(['cam','season_start_year']).agg(x=(x,'mean'),y=('settlement','mean'),camera_records=('settlement','size')).reset_index()
        # No source-year validation is implied by matching nominal season labels.
        a['species']=species;a['predictor']=x;points.append(a)
        b=a.groupby('cam')[['x','y']].mean()
        repeated=a[a.cam.isin(a.groupby('cam').size().loc[lambda z:z>=2].index)].copy()
        w=repeated[['x','y']]-repeated.groupby('cam')[['x','y']].transform('mean')
        design=pd.get_dummies(repeated[['cam','season_start_year']].astype(str),drop_first=True,dtype=float)
        X=np.column_stack([np.ones(len(repeated)),design.to_numpy()]);v=repeated[['x','y']].to_numpy()
        residual=v-X@np.linalg.lstsq(X,v,rcond=None)[0] if len(v) else np.empty((0,2))
        df=len(v)-np.linalg.matrix_rank(X) if len(v) else 0
        r=float(np.corrcoef(residual.T)[0,1]) if df>2 and np.all(np.std(residual,axis=0)>1e-9) else np.nan
        rows.append(dict(species=species,predictor=x,camera_records=int(a.camera_records.sum()),code_seasons=len(a),geographic_codes=a.cam.nunique(),between_location_r=b.x.corr(b.y),within_location_r=w.x.corr(w.y),location_year_adjusted_r=r,adjusted_residual_df=df,nominal_season_alignment=True,causal_inference=False))
d=pd.DataFrame(rows);d.to_csv(OUT/(args.prefix+'_environment_correlations.csv'),index=False)
pd.concat(points,ignore_index=True).to_csv(OUT/(args.prefix+'_correlation_points.csv'),index=False)
print(d[['species','predictor','code_seasons','between_location_r','within_location_r','location_year_adjusted_r']].to_string(index=False))
