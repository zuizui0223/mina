"""ERA5 regional September SWE, daily 00 UTC samples; not local nest snow."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json
import numpy as np
import pandas as pd
import requests,numcodecs
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'outputs/snow_grid_support_v1'
OUT=ROOT/'outputs/september_snow_v1'
URL='https://storage.googleapis.com/gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3'


def main():
    OUT.mkdir(exist_ok=True);cache=OUT/'daily';cache.mkdir(exist_ok=True)
    metadata=json.loads((SOURCE/'source_zmetadata.json').read_text())['metadata']
    support=pd.read_csv(SOURCE/'nearest_grid_snapshots.csv');support=support[support.date.str.startswith('2011')].copy()
    assert len(support)==106
    with np.load(SOURCE/'source_snapshots.npz') as z:
        lat=z['latitude'];lon=z['longitude']
    iy=np.array([int(np.flatnonzero(lat==v)[0]) for v in support.grid_lat]);ix=np.array([int(np.flatnonzero(lon==v)[0]) for v in support.grid_lon])
    def read(variable,index):
        r=requests.get(URL+'/'+variable+'/'+index,timeout=30);r.raise_for_status()
        desc=metadata[variable+'/.zarray'];assert desc['filters'] is None
        a=np.frombuffer(numcodecs.get_codec(desc['compressor']).decode(r.content),dtype=desc['dtype']).reshape(desc['chunks'])
        return a,hashlib.sha256(r.content).hexdigest()
    assert metadata['time/.zattrs']['units']=='hours since 1900-01-01 00:00:00'
    first=int(read('time','0')[0][0]);length=metadata['time/.zarray']['chunks'][0]
    dates=[f'{y}-09-{day:02d}T00:00:00' for y in range(2011,2022) for day in range(1,31)]
    indices=[int((np.datetime64(d)-np.datetime64('1900-01-01T00:00:00'))/np.timedelta64(1,'h'))-first for d in dates]
    time_checks={str(k):read('time',str(k)) for k in sorted(set(i//length for i in indices))}
    for date,idx in zip(dates,indices):
        actual=int(time_checks[str(idx//length)][0][idx%length])
        assert np.datetime64('1900-01-01T00:00:00')+np.timedelta64(actual,'h')==np.datetime64(date)
    identity=dict(url=URL,support_sha256=hashlib.sha256((SOURCE/'nearest_grid_snapshots.csv').read_bytes()).hexdigest(),
                  metadata_sha256=hashlib.sha256((SOURCE/'source_zmetadata.json').read_bytes()).hexdigest(),
                  code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    def fetch(pair):
        date,idx=pair;dest=cache/(date[:10]+'.json')
        if dest.exists():
            saved=json.loads(dest.read_text())
            if saved.get('identity')==identity:return saved
        error=None
        for attempt in range(2):
            try:
                a,sha=read('snow_depth',f'{idx}.0.0');values=a[0,iy,ix]
                assert np.isfinite(values).all() and (values>=0).all()
                result=dict(date=date,time_index=idx,source_chunk_sha256=sha,identity=identity,values=values.tolist(),status='ok')
                dest.write_text(json.dumps(result)+'\n');return result
            except Exception as exc:error=f'{type(exc).__name__}: {exc}'
        return dict(date=date,status='failed',error=error)
    results=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs=[pool.submit(fetch,pair) for pair in zip(dates,indices)]
        for job in as_completed(jobs):
            results.append(job.result())
            if len(results)%30==0:
                print('COMPLETED',len(results),'/',len(dates),flush=True)
                (OUT/'progress.json').write_text(json.dumps(dict(completed=len(results),expected=len(dates),failed=sum(r['status']!='ok' for r in results)))+'\n')
    results=sorted(results,key=lambda r:r['date'])
    failed=[r for r in results if r['status']!='ok']
    (OUT/'failures.json').write_text(json.dumps(failed,indent=2)+'\n')
    rows=[]
    for r in results:
        if r['status']!='ok':continue
        for site,value in zip(support.to_dict('records'),r['values']):
            rows.append(dict(location_id=site['location_id'],date=r['date'],year=int(r['date'][:4]),
                grid_lat=site['grid_lat'],grid_lon=site['grid_lon'],land_fraction=site['land_fraction'],snow_water_equivalent_m=value))
    daily=pd.DataFrame(rows);daily.to_csv(OUT/'daily_points.csv.gz',index=False)
    monthly=daily.groupby(['location_id','year','grid_lat','grid_lon','land_fraction'],as_index=False).agg(
        days=('date','nunique'),september_00utc_mean_swe_m=('snow_water_equivalent_m','mean'),
        minimum_swe_m=('snow_water_equivalent_m','min'),maximum_swe_m=('snow_water_equivalent_m','max'))
    monthly['complete']=monthly.days.eq(30)
    monthly.loc[~monthly.complete,['september_00utc_mean_swe_m','minimum_swe_m','maximum_swe_m']]=np.nan
    monthly.to_csv(OUT/'september_summary.csv',index=False)
    (OUT/'manifest.json').write_text(json.dumps(dict(status='complete' if not failed else 'incomplete',identity=identity,
        expected_dates=330,successful_dates=330-len(failed),daily_rows=len(daily),monthly_rows=len(monthly),
        complete_months=int(monthly.complete.sum()),time_chunk_sha256={k:v[1] for k,v in time_checks.items()},
        units='m water equivalent',sampling='daily 00 UTC; not full hourly monthly mean',
        limitations=['Regional grid context; local nest snow and permanent ice not separated','Mixed land/ocean cells retained with land fraction, not classified as snow-free']),indent=2)+'\n')
    print('FINISHED',len(daily),'rows; failures',len(failed),flush=True)


if __name__=='__main__':main()
