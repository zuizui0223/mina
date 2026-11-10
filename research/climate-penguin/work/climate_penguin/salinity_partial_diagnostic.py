from pathlib import Path
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
d=pd.read_csv(OUT/'behavior_ocean_join.csv');rows=[]
for species,g in d.groupby('species'):
    cols=['ocean_m9_surface_salinity','ocean_m9_surface_potential_temperature_c','near_sic_mean_month9','settlement']
    a=g.dropna(subset=cols).groupby(['cam','season_start_year'])[cols].mean().reset_index()
    X=pd.get_dummies(a[['cam','season_start_year']].astype(str),drop_first=True,dtype=float).to_numpy()
    X=np.column_stack([np.ones(len(a)),X,a[cols[1:3]].to_numpy()])
    y=a[[cols[0],'settlement']].to_numpy();res=y-X@np.linalg.lstsq(X,y,rcond=None)[0]
    rows.append({'species':species,'code_seasons':len(a),'codes':a.cam.nunique(),'residual_df':len(a)-np.linalg.matrix_rank(X),'partial_salinity_settlement_r':np.corrcoef(res.T)[0,1],'controls':'geographic_code + nominal_year + surface_potential_temperature + nearby_SIC','causal':False})
pd.DataFrame(rows).to_csv(OUT/'salinity_partial_correlation_diagnostic.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
