#!/usr/bin/env python3
"""Source-only 2019–2020 cross-variable anomaly check at 378 original marine cells.

Requires the *original* 588-site×28-year environmental CSV in Actions
artifact #13829236358. Never infer independent GLORYS or EN4 confirmation.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

p=argparse.ArgumentParser()
p.add_argument('--original-588-csv',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
args=p.parse_args()
x=pd.read_csv(args.original_588_csv)
assert len(x)==588*28 and x.site_id.nunique()==588
assert x.year.nunique()==28 and set(x.year)==set(range(1993,2021))
keys=['GLORYS_cell_y','GLORYS_cell_x']
variables={'salinity':'mean_GLORYS_salinity','temperature':'mean_GLORYS_thetao_C','sea_ice':'mean_source_SIC_pp'}
g=x.groupby(keys+['year'],as_index=False).agg(**{k:(v,'mean') for k,v in variables.items()})
assert len(g)==378*28 and g.groupby(keys).year.nunique().eq(28).all()
table=[];results={}
for variable in variables:
    grid=g.pivot(index=keys,columns='year',values=variable)
    base=grid.loc[:,1993:2018]
    mean=base.mean(axis=1);sd=base.std(axis=1,ddof=0)
    for year in (2019,2020):
        v=grid[year]-mean
        z=v/sd.replace(0,np.nan)
        summary={'n_original_cells':len(v),'n_negative':int((v<0).sum()),
          'n_positive':int((v>0).sum()),
          'median_anomaly':float(v.median()),'mean_anomaly':float(v.mean()),
          'n_less_than_minus_2_prior_SD':int((z<(-2)).sum()),
          'n_more_than_plus_2_prior_SD':int((z>2).sum())}
        results[f'{variable}_{year}']=summary
        table.extend({'cell_y':key[0],'cell_x':key[1],'variable':variable,'year':year,
            'baseline_1993_2018':float(m),'delta':float(d),'standardized_anomaly':float(a)}
            for key,m,d,a in zip(grid.index,mean,v,z))
assert results['salinity_2019']['n_negative']==368
assert results['salinity_2020']['n_negative']==363
assert results['salinity_2019']['n_less_than_minus_2_prior_SD']==239
assert results['salinity_2020']['n_less_than_minus_2_prior_SD']==310
assert results['temperature_2020']['n_less_than_minus_2_prior_SD']==11
assert results['sea_ice_2020']['n_less_than_minus_2_prior_SD']==8
args.out.mkdir(parents=True,exist_ok=True)
pd.DataFrame(table).to_csv(args.out/'source_cell_variable_year_anomalies.csv',index=False)
result={'status':'POST_RESULT_SAME_SOURCE_CROSSVARIABLE_QA',
        'original_source_environmental_rows':len(x),
        'unique_ocean_GLORYS_cells':378,
        'negative_controls':'GLORYS sea-surface temperature and OSI SAF original nearshore SIC',
        'baseline':'each source wet cell 1993–2018 mean and population SD',
        'results':results,
        'interpretation':'Reanalysis-salinity anomaly is unusually geographically widespread compared with original measured thermal/ice values; this neither proves an artifact nor validates a real pan-Antarctic freshening event.',
        'not_in_situ_independent':True,'not_an_independent_cell_level_significance_test':True}
(args.out/'GLORYS_2019_2020_CROSSVARIABLE_SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
