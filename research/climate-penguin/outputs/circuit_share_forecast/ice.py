from pathlib import Path
from datetime import date
import numpy as np,pandas as pd,netCDF4 as nc
# Extract a season mean on the native grid. Mask cells without all daily values.
from calendar import monthrange
from glob import glob
root=Path('work/climate_penguin/osi_concentration')
out=Path('work/circuit_share');out.mkdir(parents=True,exist_ok=True)
for year in range(1991,2021):
    dst=out/f'sic_{year}.npy'
    if dst.exists():continue
    month_means=[]
    for month in (8,9,10):
        paths=sorted(root.glob(f'ice_conc*_{year}{month:02d}*1200.nc'))
        assert len(paths)==monthrange(year,month)[1]
        daily=[]
        for path in paths:
            with nc.Dataset(path) as ds:
                a=ds['ice_conc'][0].filled(np.nan);flags=ds['status_flag'][0].filled(3).astype(int)
                a[(flags&3)!=0]=np.nan
                daily.append(a)
                if not (out/'grid.npz').exists():np.savez(out/'grid.npz',lat=ds['lat'][:].data,lon=ds['lon'][:].data)
        month_means.append(np.mean(daily,axis=0))
    np.save(dst,np.mean(month_means,axis=0))
print('completed 30 years')
