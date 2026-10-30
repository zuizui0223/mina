"""Check saved joins directly against source grids at first/last point per tag."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
import xarray as xr
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/chinstrap_winter_v1'
parser=argparse.ArgumentParser();parser.add_argument('--raw-root',type=Path,required=True);args=parser.parse_args()
d=pd.read_csv(OUT/'route_ice_support.csv');same=d[d.day_offset.eq(0)].sort_values(['PTT','point_day'])
sample=pd.concat([same.groupby('PTT').head(1),same.groupby('PTT').tail(1)]).drop_duplicates(['PTT','point_day'])
checks=0
for r in sample.itertuples():
    stamp=pd.Timestamp(r.ice_day).strftime('%Y%m%d')
    for product,folder,filename in [('sic','osi_concentration',f'ice_conc_sh_ease2-250_cdr-v3p1_{stamp}1200.nc'),('drift','return_drift',f'ice_drift_sh_ease2-750_cdr-v1p0_24h-{stamp}1200.nc')]:
        with xr.open_dataset(args.raw_root/folder/filename) as ds:
            match=np.isclose(ds.lat.values,getattr(r,product+'_grid_lat'),atol=1e-7,rtol=0)&np.isclose(ds.lon.values,getattr(r,product+'_grid_lon'),atol=1e-7,rtol=0)
            assert match.sum()==1
            flag=float(ds.status_flag.values[0][match][0]);assert flag==getattr(r,product+'_flag')
            if product=='sic':assert np.isclose(float(ds.ice_conc.values[0][match][0]),r.sic_percent,atol=1e-8)
            else:assert flag in [2,3]
        checks+=1
assert len(d)==114 and len(same)==38
assert same.drift_status.eq('satellite_vector').sum()==0
assert same.drift_flag.eq(2).sum()==36 and same.drift_flag.eq(3).sum()==2
assert same.sic_percent.lt(15).sum()==32
result={'passed':True,'source_grid_spot_checks':checks,'checked_point_days':len(sample),'all_summary_rows_checked':len(same),
        'scope':'independent source-cell value and flag checks; not trajectory accuracy validation'}
(OUT/'route_ice_independent_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
