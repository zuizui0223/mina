"""Acquire September 2015-2020 for both existing scenario branches and grids."""
from pathlib import Path
import sys
import hashlib
import json
import numpy as np
import pandas as pd
import xarray as xr
import dask

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/cmip6_projection_v1'))
from extract import open_store,coordinates,normalize_values

SOURCE=ROOT/'outputs/cmip6_projection_v1'
OUT=ROOT/'outputs/scenario_support_v1/recent_monthly'
OUT.mkdir(parents=True,exist_ok=True)
selected=pd.read_csv(SOURCE/'selected_stores.csv')
selected=selected[selected.experiment_id.isin(['ssp245','ssp585'])]
assert len(selected)==18
records=[]
for row in selected.itertuples(index=False):
    stem=f'{row.source_id}_{row.member_id}_{row.variable_id}_{row.experiment_id}'
    dest=OUT/(stem+'.csv')
    meta=OUT/(stem+'.json')
    support_path=SOURCE/f'support_{row.source_id}_{row.member_id}_{row.variable_id}.csv'
    support=pd.read_csv(support_path)
    identity=dict(zstore=row.zstore,years=list(range(2015,2021)),month=9,
                  support_sha256=hashlib.sha256(support_path.read_bytes()).hexdigest(),
                  code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if dest.exists() and meta.exists():
        saved=json.loads(meta.read_text())
        if saved.get('identity')==identity and saved.get('sha256')==hashlib.sha256(dest.read_bytes()).hexdigest():
            records.append(saved)
            print('CACHED',stem,flush=True)
            continue
    print('OPEN',stem,flush=True)
    ds,url=open_store(row)
    try:
        lat,lon,dims=coordinates(ds,row.variable_id)
        gy=support.grid_y.to_numpy(int); gx=support.grid_x.to_numpy(int)
        assert np.allclose(lat[gy,gx],support.grid_lat,atol=1e-6,rtol=0)
        assert np.allclose(lon[gy,gx],support.grid_lon,atol=1e-6,rtol=0)
        parent=ds.attrs.get('parent_variant_label')
        assert not parent or parent==row.member_id
        times=list(ds.time.values)
        indices=[i for i,t in enumerate(times) if 2015<=t.year<=2020 and t.month==9]
        assert [times[i].year for i in indices]==list(range(2015,2021))
        with dask.config.set(scheduler='threads',num_workers=4):
            a=ds[row.variable_id].isel(time=indices,**{
                dims[0]:xr.DataArray(gy,dims='location'),dims[1]:xr.DataArray(gx,dims='location')}).transpose('time','location').compute().values
        values,units=normalize_values(a,row.variable_id,ds[row.variable_id].attrs.get('units',''))
        assert values.shape==(6,106) and np.isfinite(values).all()
        out=pd.DataFrame([dict(source_id=row.source_id,member_id=row.member_id,variable_id=row.variable_id,
                  experiment_id=row.experiment_id,year=times[idx].year,month=9,location_id=loc,value=float(values[i,j]),units=units)
                  for i,idx in enumerate(indices) for j,loc in enumerate(support.location_id)])
        out.to_csv(dest,index=False)
        record=dict(identity=identity,source_id=row.source_id,member_id=row.member_id,variable_id=row.variable_id,
                    experiment_id=row.experiment_id,rows=len(out),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
                    calendar=ds.time.encoding.get('calendar'),source_units=ds[row.variable_id].attrs.get('units'),
                    parent_variant_label=parent,http_url=url)
        meta.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        records.append(record)
        print('SAVED',stem,len(out),flush=True)
    finally:
        ds.close()
    (OUT/'progress.json').write_text(json.dumps({'completed_stores':len(records),'expected_stores':18},indent=2)+'\n')
(OUT/'manifest.json').write_text(json.dumps({'status':'complete','stores':records,'total_values':sum(r['rows'] for r in records)},indent=2)+'\n')
print('COMPLETE',sum(r['rows'] for r in records),flush=True)
