from pathlib import Path
import pandas as pd,numpy as np,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
p=pd.read_csv(OUT/'extended_analysis_cohort.csv');o=pd.read_csv(OUT/'ocean_monthly_2011_2021.csv')
variables=['surface_salinity','surface_potential_temperature_c','mixed_layer_depth_m']
for month in [8,9,10,11]:
    x=o[o.month==month][['location_id','year','grid_within_25km']+variables].copy()
    x.loc[~x.grid_within_25km,variables]=np.nan
    x=x.drop(columns='grid_within_25km').rename(columns={'year':'season_start_year',**{v:f'ocean_m{month}_{v}' for v in variables}})
    p=p.merge(x,on=['location_id','season_start_year'],how='left',validate='many_to_one')
assert len(p)==288
p.to_csv(OUT/'behavior_ocean_join.csv',index=False)
cols=[f'ocean_m{m}_{v}' for m in [8,9,10,11] for v in variables]
status={'source_rows':288,'rows_complete_all_4_months_3_variables':int(p[cols].notna().all(axis=1).sum()),'season_alignment':'original_csv_labels_provisional','direct_observation':False}
(OUT/'behavior_ocean_join_checks.json').write_text(json.dumps(status,indent=2));print(status)
