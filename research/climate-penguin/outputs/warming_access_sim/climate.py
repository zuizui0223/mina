"""Extract Aug-Oct model climatologies on their native grids, by whole Zarr time chunk."""
from pathlib import Path
import hashlib, json
import cftime, fsspec, numpy as np, pandas as pd, zarr
out=Path('outputs/warming_access_sim')
cache=Path('work/warming_access_sim')
stores=pd.read_csv('work/mina-sync/research/climate-penguin/outputs/cmip6_projection_v1/selected_stores.csv')
rows=[]
for row in stores.query("variable_id=='siconc'").itertuples():
    url=row.zstore.replace('gs://','https://storage.googleapis.com/')
    dest=cache/f'{row.source_id}_{row.experiment_id}.npz'
    if not dest.exists():
        group=zarr.open_consolidated(fsspec.get_mapper(url,client_kwargs={'trust_env':True}),mode='r')
        time=group['time'];dates=cftime.num2date(time[:],time.attrs['units'],calendar=time.attrs.get('calendar','standard'))
        a=group['siconc']; assert a.attrs['units']=='%' and a.chunks[1:]==a.shape[1:]
        lat=group['latitude' if 'latitude' in group else 'lat'][:];lon=group['longitude' if 'longitude' in group else 'lon'][:]
        data={'lon':lon,'lat':lat}
        periods=[(1995,2014)] if row.experiment_id=='historical' else [(2041,2060),(2081,2100)]
        for lo,hi in periods:
            idx=np.array([i for i,d in enumerate(dates) if lo<=d.year<=hi and d.month in (8,9,10)])
            assert len(set((dates[i].year,dates[i].month) for i in idx))==len(idx)==60
            sums=np.zeros(a.shape[1:]);counts=np.zeros_like(sums)
            for chunk in np.unique(idx//a.chunks[0]):
                z=idx[idx//a.chunks[0]==chunk]; slab=a[int(z.min()):int(z.max()+1)][z-z.min()].astype(float)
                good=np.isfinite(slab)&(slab>=0)&(slab<=100.001);sums+=np.where(good,slab,0).sum(axis=0);counts+=good.sum(axis=0)
            data[str(lo)]=np.where(counts==60,sums/60,np.nan)
        np.savez_compressed(dest,**data)
    rows.append(dict(model=row.source_id,member=row.member_id,experiment=row.experiment_id,url=url,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
    print(dest,flush=True)
pd.DataFrame(rows).to_csv(out/'model_sources.csv',index=False)
