"""Summarize direction as environmental exposure, with explicit support."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'ross_directional_exposure_v1'
src=out/'interval_exposure.csv.gz';d=pd.read_csv(src)
s=pd.read_csv(root/'ross_ensemble_ice_v1/interval_support.csv.gz')
keys=['bird_fn','season','time1','time2']
checks=d.merge(s[keys+['drift_valid','drift_nominal','drift_wind']],on=keys,validate='many_to_one')
mapping={'satellite':'drift_valid','nominal':'drift_nominal','wind':'drift_wind'}
lost={}
for label,col in mapping.items():
    g=checks[checks.product_class==label]
    assert (g.valid<=g[col]).all()
    lost[label]=int((g[col]-g.valid).sum())
    # Additional endpoint/time screening may legitimately reduce support; record it.
d['month']=pd.to_datetime(d.time1,utc=True).dt.month
records=[]
for threshold in [.5,1.]:
    a=d[d.support_fraction>=threshold]
    for key,g in a.groupby(['bird_fn','season','target','product_class','month']):
        records.append(dict(zip(['bird_fn','season','target','product_class','month'],key),
            threshold=threshold,intervals=len(g),mean_projected_km_day=g.projected_km_day.mean(),
            mean_radial_km_day=g.radial_km_day.mean(),
            mean_toward_fraction=g.toward_fraction_given_valid.mean()))
t=pd.DataFrame(records);t.to_csv(out/'trip_exposure.csv',index=False)
summary=t.groupby(['season','target','product_class','month','threshold']).agg(
    bird_years=('bird_fn','size'),intervals=('intervals','sum'),
    mean_projected_km_day=('mean_projected_km_day','mean'),
    median_projected_km_day=('mean_projected_km_day','median'),
    positive_bird_years=('mean_projected_km_day',lambda x:int(x.gt(0).sum()))).reset_index()
summary.to_csv(out/'summary.csv',index=False)
east=d[d.target=='CRZE'];west=d[d.target=='CRZW']
p=east.merge(west,on=keys+['product_class'],suffixes=('_east','_west'),validate='one_to_one')
assert p.valid_east.eq(p.valid_west).all()
v=dict(passed=True,exposure_rows=len(d),matched_crozier_endpoint_rows=len(p),
       maximum_crozier_endpoint_difference_km_day=float((p.projected_km_day_east-p.projected_km_day_west).abs().max()),
       additional_screening_losses=lost,
       source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
       aggregation='Equal interval means within bird-year; equal bird-year means within colony-season; not independent environmental replicates')
(out/'summary_validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v));print(summary[(summary.product_class=='satellite')&(summary.threshold==.5)].to_string(index=False))
