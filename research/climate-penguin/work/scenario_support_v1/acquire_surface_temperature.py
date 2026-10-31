"""Acquire September CMIP6 tos on existing salinity cells and members.

No biological prediction: tos and reanalysis surface potential temperature
require an explicit compatibility assessment before model application.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import dask
import numpy as np
import pandas as pd
import xarray as xr

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/cmip6_projection_v1'))
from extract import open_store, coordinates
OUT=ROOT/'outputs/surface_temperature_projection_v1'
SOURCE=ROOT/'outputs/cmip6_projection_v1'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--catalog',type=Path,required=True)
    args=parser.parse_args()
    OUT.mkdir(exist_ok=True)
    base=pd.read_csv(SOURCE/'selected_stores.csv').query("variable_id=='sos'")
    candidates=[]
    for chunk in pd.read_csv(args.catalog,chunksize=50000):
        candidates.append(chunk[(chunk.variable_id=='tos')&(chunk.table_id=='Omon')])
    candidates=pd.concat(candidates)
    keys=['source_id','member_id','experiment_id','grid_label']
    selected=base[keys].merge(candidates,on=keys,validate='one_to_many')
    selected=selected.sort_values(['version','zstore']).drop_duplicates(keys,keep='last')
    assert len(selected)==9, 'Not all original model/member/experiment/grid combinations exist'
    selected=selected.sort_values(keys)
    selected.to_csv(OUT/'selected_stores.csv',index=False)
    records=[]
    for row in selected.itertuples(index=False):
        stem=f'{row.source_id}_{row.member_id}_{row.experiment_id}'
        dest=OUT/(stem+'.csv.gz');meta=OUT/(stem+'.json')
        sp=SOURCE/f'support_{row.source_id}_{row.member_id}_sos.csv'
        support=pd.read_csv(sp)
        years=list(range(2011,2015)) if row.experiment_id=='historical' else list(range(2015,2021))+list(range(2041,2061))+list(range(2081,2101))
        identity=dict(zstore=row.zstore,years=years,month=9,
                      support_sha256=hashlib.sha256(sp.read_bytes()).hexdigest(),
                      code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        if dest.exists() and meta.exists():
            saved=json.loads(meta.read_text())
            if saved['identity']==identity and saved['sha256']==hashlib.sha256(dest.read_bytes()).hexdigest():
                records.append(saved);print('CACHED',stem,flush=True);continue
        print('OPEN',stem,flush=True)
        ds,url=open_store(row)
        try:
            lat,lon,dims=coordinates(ds,'tos')
            gy=support.grid_y.to_numpy(int);gx=support.grid_x.to_numpy(int)
            assert np.allclose(lat[gy,gx],support.grid_lat,atol=1e-6,rtol=0)
            assert np.allclose(lon[gy,gx],support.grid_lon,atol=1e-6,rtol=0)
            parent=ds.attrs.get('parent_variant_label')
            assert row.experiment_id=='historical' or parent==row.member_id
            times=list(ds.time.values)
            indices=[i for i,t in enumerate(times) if t.year in years and t.month==9]
            assert [times[i].year for i in indices]==years
            with dask.config.set(scheduler='threads',num_workers=4):
                values=ds.tos.isel(time=indices,**{
                    dims[0]:xr.DataArray(gy,dims='location'),
                    dims[1]:xr.DataArray(gx,dims='location')}).transpose('time','location').compute().values.astype(float)
            unit=ds.tos.attrs.get('units','')
            if unit in ['K','kelvin']: values-=273.15
            else: assert unit in ['degC','degrees_C','degree_Celsius','degrees_Celsius'],unit
            assert values.shape==(len(years),106) and np.isfinite(values).all()
            assert values.min()>-5 and values.max()<45
            pd.DataFrame([dict(source_id=row.source_id,member_id=row.member_id,
                experiment_id=row.experiment_id,variable_id='tos',year=times[idx].year,
                month=9,location_id=loc,value=float(values[i,j]),units='degC')
                for i,idx in enumerate(indices) for j,loc in enumerate(support.location_id)]).to_csv(dest,index=False)
            rec=dict(identity=identity,rows=values.size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
                     source_units=unit,variable_attributes=dict(ds.tos.attrs),
                     calendar=ds.time.encoding.get('calendar'),parent_variant_label=parent,
                     http_url=url,source_id=row.source_id,member_id=row.member_id,experiment_id=row.experiment_id)
            meta.write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
            records.append(rec)
            print('SAVED',stem,values.size,flush=True)
        finally:ds.close()
        (OUT/'progress.json').write_text(json.dumps({'completed':len(records),'expected':9})+'\n')
    (OUT/'manifest.json').write_text(json.dumps(dict(status='arrays_acquired_not_biological_prediction',
        catalog_sha256=hashlib.sha256(args.catalog.read_bytes()).hexdigest(),
        total_values=sum(r['rows'] for r in records),stores=records),indent=2)+'\n',encoding='utf-8')
    print('COMPLETE',len(records),flush=True)


if __name__=='__main__':main()
