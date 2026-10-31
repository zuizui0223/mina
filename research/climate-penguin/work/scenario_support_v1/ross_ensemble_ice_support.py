"""Ice support over all retained location draws; no movement-effect inference."""
from pathlib import Path
import argparse,hashlib,io,json,time
from functools import lru_cache
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
import xarray as xr
from pointblue_stream import Blocks

p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--ice-root',type=Path,required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'ross_ensemble_ice_v1';out.mkdir(exist_ok=True)
manifest=json.loads((root/'pointblue_full_positions_v1/acquisition_manifest.json').read_text());assert manifest['status']=='complete'
files={};missing=set();grids={};summaries=[];selected=0;read_rows=0;started=time.monotonic()
def xyz(lon,lat):
    lon=np.asarray(lon,dtype=np.float64);lat=np.asarray(lat,dtype=np.float64)
    a=np.radians(lon);b=np.radians(lat);return np.column_stack([np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)])
@lru_cache(maxsize=220)
def layer(product,day):
    date=pd.Timestamp(day)
    if product=='sic':folder='osi_concentration';name=f'ice_conc_sh_ease2-250_cdr-v3p1_{date:%Y%m%d}1200.nc'
    else:folder='return_drift';name=f'ice_drift_sh_ease2-750_cdr-v1p0_24h-{date:%Y%m%d}1200.nc'
    path=args.ice_root/folder/name
    if not path.exists():missing.add(f'{folder}/{name}');return None
    files[f'{folder}/{name}']=hashlib.sha256(path.read_bytes()).hexdigest()
    with xr.open_dataset(path) as d:
        assert pd.Timestamp(d.time.values[0])==date+pd.Timedelta(hours=12)
        coordinates=np.column_stack([d.lon.values.ravel(),d.lat.values.ravel()])
        if product not in grids:
            valid=np.isfinite(coordinates).all(axis=1);index=np.flatnonzero(valid)
            grids[product]=(coordinates,index,cKDTree(xyz(coordinates[valid,0],coordinates[valid,1])))
        else:assert np.allclose(grids[product][0],coordinates,equal_nan=True)
        names=['status_flag','ice_conc'] if product=='sic' else ['status_flag','dX','dY','t0','t1']
        a={v:d[v].values[0].ravel().copy() for v in names}
        a['bounds']=d.time_bnds.values[0].copy()
        return a

# Establish both spherical nearest-cell grids from a known archived date.
assert layer('sic','2017-10-01') is not None and layer('drift','2017-10-01') is not None
for b in manifest['blocks']:
    path=args.cache/b['file'];assert path.stat().st_size==b['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==b['sha256']
with io.BufferedReader(Blocks([args.cache/b['file'] for b in manifest['blocks']]),buffer_size=1024*1024) as stream:
    for chunk,d in enumerate(pd.read_csv(stream,chunksize=250000)):
        read_rows+=len(d)
        # This retains the previous full-file audit's exact seasonal mask.
        t=pd.to_datetime(d.time1,utc=True,errors='raise');end=pd.to_datetime(d.time2,utc=True,errors='raise')
        keep=t.dt.month.isin([9,10]) & ~t.dt.dayofyear.between(229,269) & ~d.inserted
        keep &= np.isfinite(d.lon)&np.isfinite(d.lat)&d.lon.between(-180,360)&d.lat.between(-90,90)&(end>t)
        if not keep.any():continue
        d=d.loc[keep].reset_index(drop=True);t=t[keep].reset_index(drop=True);end=end[keep].reset_index(drop=True)
        selected+=len(d);mid=t+(end-t)/2
        d['sic_day']=mid.dt.strftime('%Y-%m-%d')
        # At exactly noon use the window beginning at that noon, consistent with half-open bounds.
        d['drift_day']=(mid+pd.Timedelta(hours=12)).dt.strftime('%Y-%m-%d')
        for product in ['sic','drift']:
            coordinates,index,tree=grids[product]
            chord,k=tree.query(xyz(d.lon.to_numpy(),d.lat.to_numpy()),workers=1)
            d[product+'_cell']=index[k]
            d[product+'_distance_km']=2*6371.0088*np.arcsin(np.clip(chord/2,0,1))
        d['draws']=1;d['sic_valid']=0;d['sic_under15']=0;d['sic_sum']=0.
        d['drift_valid']=0;d['drift_nominal']=0;d['drift_noice']=0;d['drift_wind']=0
        d['drift_cached']=0;d['drift_overlap_half']=0;d['drift_overlap_sum']=0.;d['source_land_flag']=d.filterLand.astype(int)
        for day,inds in d.groupby('sic_day').groups.items():
            a=layer('sic',day)
            if a is None:continue
            k=d.loc[inds,'sic_cell'].to_numpy();flag=a['status_flag'][k];value=a['ice_conc'][k]
            valid=np.isfinite(flag)&np.isfinite(value)&((np.nan_to_num(flag).astype(int)&3)==0)
            assert np.all((value[valid]>=0)&(value[valid]<=100))
            midpoint=mid.iloc[inds].dt.tz_localize(None).to_numpy()
            assert ((midpoint>=a['bounds'][0])&(midpoint<a['bounds'][1])).all()
            d.loc[inds,'sic_valid']=valid.astype(int);d.loc[inds,'sic_under15']=(valid&(value<15)).astype(int)
            d.loc[inds,'sic_sum']=np.where(valid,value,0.)
        for day,inds in d.groupby('drift_day').groups.items():
            a=layer('drift',day)
            if a is None:continue
            k=d.loc[inds,'drift_cell'].to_numpy();flag=a['status_flag'][k]
            good=np.isin(flag,[20,21,22,30])&np.isfinite(a['dX'][k])&np.isfinite(a['dY'][k])
            midpoint=mid.iloc[inds].dt.tz_localize(None).to_numpy()
            assert ((midpoint>=a['bounds'][0])&(midpoint<a['bounds'][1])).all()
            t0=a['t0'][k];t1=a['t1'][k];start=t.iloc[inds].dt.tz_localize(None).to_numpy();stop=end.iloc[inds].dt.tz_localize(None).to_numpy()
            timed=~np.isnat(t0)&~np.isnat(t1)&(t1>t0)
            overlap=np.maximum(0.,(np.minimum(stop,t1)-np.maximum(start,t0))/np.timedelta64(1,'s'))
            fraction=np.where(timed,overlap/((stop-start)/np.timedelta64(1,'s')),0.)
            assert np.all((fraction>=0)&(fraction<=1))
            d.loc[inds,'drift_cached']=1;d.loc[inds,'drift_valid']=good.astype(int)
            d.loc[inds,'drift_nominal']=(good&(flag==30)).astype(int)
            d.loc[inds,'drift_noice']=(flag==2).astype(int);d.loc[inds,'drift_wind']=np.isin(flag,[23,24,25]).astype(int)
            d.loc[inds,'drift_overlap_half']=(good&timed&(fraction>=.5)).astype(int)
            d.loc[inds,'drift_overlap_sum']=np.where(good&timed,fraction,0.)
        counts=['draws','sic_valid','sic_under15','sic_sum','drift_cached','drift_valid','drift_nominal','drift_noice','drift_wind','drift_overlap_half','drift_overlap_sum','source_land_flag']
        agg={c:'sum' for c in counts};agg.update(sic_distance_km='max',drift_distance_km='max')
        summaries.append(d.groupby(['bird_fn','season','time1','time2','sic_day','drift_day']).agg(agg).reset_index())
        if chunk%10==0:
            progress=dict(chunks=chunk+1,source_rows=read_rows,selected_draws=selected,elapsed_seconds=round(time.monotonic()-started,1))
            (out/'progress.json').write_text(json.dumps(progress,indent=2)+'\n');print(json.dumps(progress),flush=True)
intervals=pd.concat(summaries).groupby(['bird_fn','season','time1','time2','sic_day','drift_day']).agg(agg).reset_index()
assert intervals.draws.sum()==selected
for c in ['sic_valid','sic_under15','drift_cached','drift_valid','drift_nominal','drift_noice','drift_wind','drift_overlap_half','source_land_flag']:
    assert intervals[c].between(0,intervals.draws).all();intervals[c+'_fraction']=intervals[c]/intervals.draws
intervals['mean_sic_when_valid']=intervals.sic_sum/intervals.sic_valid.replace(0,np.nan)
intervals.to_csv(out/'interval_support.csv.gz',index=False)
trip=intervals.groupby(['bird_fn','season']).agg(intervals=('draws','size'),draws=('draws','sum'),
    mean_valid_drift_fraction=('drift_valid_fraction','mean'),mean_nominal_drift_fraction=('drift_nominal_fraction','mean'),
    mean_overlap_half_fraction=('drift_overlap_half_fraction','mean'),mean_low_sic_fraction=('sic_under15_fraction','mean'),
    intervals_any_drift=('drift_valid',lambda x:int(x.gt(0).sum())),intervals_all_draws_drift=('drift_valid_fraction',lambda x:int(x.eq(1).sum())),
    intervals_majority_drift=('drift_valid_fraction',lambda x:int(x.ge(.5).sum()))).reset_index()
trip.to_csv(out/'trip_support.csv',index=False)
expected=pd.read_csv(root/'pointblue_full_positions_v1/trip_support.csv')
assert selected==expected.late_selected_rows.sum() and len(trip)==expected.late_selected_rows.gt(0).sum()
receipt=dict(status='ensemble_environment_support_not_transport_effect',source_rows=read_rows,selected_draws=selected,
    intervals=len(intervals),bird_years=len(trip),birds=trip.bird_fn.nunique(),
    intervals_any_drift=int(intervals.drift_valid.gt(0).sum()),intervals_majority_drift=int(intervals.drift_valid_fraction.ge(.5).sum()),
    intervals_all_draws_drift=int(intervals.drift_valid_fraction.eq(1).sum()),
    interval_mean_drift_support=float(intervals.drift_valid_fraction.mean()),
    max_sic_grid_distance_km=float(intervals.sic_distance_km.max()),max_drift_grid_distance_km=float(intervals.drift_distance_km.max()),
    raw_ice_hashes=files,missing_files=sorted(missing),
    limits=['Midpoint-based temporal support, not validated observation timing',
            'Spherical nearest cell; never nearest-valid replacement',
            'Draw fractions express model-location support, not probabilities of biological effects',
            'filterLand counted separately; fixed endpoints and equinox restrictions remain',
            'No projection onto bird movement, assistance inference or new arrival estimate'])
(out/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='raw_ice_hashes'}),flush=True)
