"""V26 fixed full 30-year seasonal sea ice on independent coastal opportunity cells."""
import csv, hashlib, io, json, math, pathlib, statistics, sys, urllib.request, zipfile, concurrent.futures
from collections import Counter,defaultdict
import numpy as np
import xarray as xr
from scipy.spatial import cKDTree
from pyproj import Geod

out=pathlib.Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
frame=pathlib.Path(sys.argv[1]);reference=pathlib.Path(sys.argv[2])
# Frame content digest supplied from the completed original workflow receipt.
assert hashlib.sha256(frame.read_bytes()).hexdigest()==sys.argv[4]
assert hashlib.sha256(reference.read_bytes()).hexdigest()=='58c9bacc331b8aefb35027ee248a09076cf96e4f71f681543444da1850347bd8'
def member(p,name):
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        names=[x for x in z.namelist() if pathlib.PurePosixPath(x).name==name]
        assert len(names)==1,(name,names)
        return z.read(names[0])
def rows(b):return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
geo=json.loads(member(frame,'result.json'))
assert geo['status']=='EXECUTED_CONTINENTAL_MAPPED_ROCK_FRAME'
tiles=[x for x in rows(member(frame,'opportunity_tiles.csv')) if int(x['band_km'])==5]
assert len(tiles)==geo['summaries'][1]['opportunity_tiles'] and len({r['tile'] for r in tiles})==len(tiles)
for x in tiles:
    for k in ('rock_pixels','plant_rock_pixels','has_plant','recorded_known','recorded_modern','recorded_ADPE','recorded_CHPE','recorded_GEPE'):x[k]=int(x[k])
    for k in ('lon','lat','plant_rock_fraction'):x[k]=float(x[k])
    assert x['rock_pixels']>0 and -90<=x['lat']<=-60.0+1e-6
receipts=json.loads(member(reference,'original_monthly_120_source_receipts.json'))
assert len(receipts)==120
pins={(int(x['year']),int(x['month'])):x for x in receipts};assert len(pins)==120
Y=tuple(range(1991,2021));M=(8,9,10,11);ORDER=[(1993,9)]+[(y,m) for y in Y for m in M if (y,m)!=(1993,9)]
BASE='https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/conc_450a1_files/monthly'
cache=out.parent/'original_osi_120';cache.mkdir(exist_ok=True)
def download(key):
    import time
    y,m=key;name=f'ice_conc_sh_ease2-250_cdr-v3p1_{y:04d}{m:02d}.nc';url=f'{BASE}/{y}/{name}'
    assert pins[key]['publisher_url']==url
    failures=[]
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'mina-source-audit/1.0'}),timeout=45) as f:
                b=f.read(25000001)
            sha=hashlib.sha256(b).hexdigest()
            if len(b)>25000000 or sha!=pins[key]['sha256']:
                raise ValueError(f'source SHA/size mismatch: {sha}')
            path=cache/name;path.write_bytes(b)
            return key,(path,sha),{'year':y,'month':m,'status':'verified','bytes':len(b),'sha256':sha,'failures':failures}
        except (OSError,TimeoutError,ValueError) as exc:
            msg=type(exc).__name__+': '+str(exc)
            failures.append(msg[:350])
            print('V26_DOWNLOAD_RETRY='+json.dumps({'year':y,'month':m,'attempt':attempt+1,'error':msg[:350]}),flush=True)
            if isinstance(exc,ValueError):break
            if attempt<2:time.sleep(3*(attempt+1))
    return key,None,{'year':y,'month':m,'status':'failed','failures':failures}
paths={};download_audit=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
    for key,value,receipt in ex.map(download,ORDER):
        download_audit.append(receipt)
        if value is not None:paths[key]=value
        # Incremental durable receipt, including partial source support.
        (out/'download_receipt.json').write_text(json.dumps(download_audit,indent=2)+'\n')
        if len(download_audit)%20==0:print('V26_DOWNLOAD_PROGRESS='+json.dumps({'done':len(download_audit),'verified':len(paths)}),flush=True)
print('V26_DOWNLOAD_FINAL='+json.dumps({'verified':len(paths),'failed':[r for r in download_audit if r['status']=='failed']}),flush=True)
assert len(paths)==120, 'SOURCE_HOLD: one or more pinned original files unavailable'
def read_source(key):
    p,sha=paths[key]
    with xr.open_dataset(p) as ds:
        assert ds.attrs['product_version']=='3.1'
        lat=np.asarray(ds['lat'].values).reshape(-1);lon=np.asarray(ds['lon'].values).reshape(-1)
        flag=np.asarray(ds['status_flag'].values[0]).reshape(-1);sic=np.asarray(ds['ice_conc'].values[0]).reshape(-1)
    assert len(lat)==len(lon)==len(flag)==len(sic)==432*432
    flagint=np.where(np.isfinite(flag),flag,32767).astype(np.int64)
    valid=np.isfinite(sic)&np.isfinite(flag)&((flagint&3)==0)&(sic>=0)&(sic<=100)
    fp=hashlib.sha256(np.ascontiguousarray(np.column_stack((lat,lon))).tobytes()).hexdigest()
    assert fp==pins[key]['native_grid_geo_sha256'],key
    return lat,lon,sic,valid,fp
def xyz(lon,lat):
    a=np.deg2rad(lon);b=np.deg2rad(lat);return np.column_stack((np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)))
lat,lon,sic,valid,fp=read_source(ORDER[0]);gd=Geod(ellps='WGS84')
flat=np.flatnonzero(np.isfinite(lat)&np.isfinite(lon));tree=cKDTree(xyz(lon[flat],lat[flat]))
cand=tree.query_ball_point(xyz(np.array([r['lon'] for r in tiles]),np.array([r['lat'] for r in tiles])),2*math.sin(101/(2*6371.0)))
frozen=[]
for r,ix in zip(tiles,cand):
    ids=flat[np.array(ix,dtype=int)]
    if len(ids):
        _,_,d=gd.inv(np.full(len(ids),r['lon']),np.full(len(ids),r['lat']),lon[ids],lat[ids])
        ids=ids[np.isfinite(d)&(d<=100000)&valid[ids]]
    frozen.append(ids)
values=np.full((len(tiles),len(ORDER)),np.nan)
for j,key in enumerate(ORDER):
    _,_,sic,valid,fingerprint=read_source(key);assert fingerprint==fp
    for i,ids in enumerate(frozen):
        if len(ids)<3:continue
        ok=valid[ids]
        if ok.mean()>=.8:values[i,j]=float(sic[ids[ok]].mean())
    print('V26_ICE_MONTH='+json.dumps({'year':key[0],'month':key[1],'sha256':paths[key][1],'supported_tiles':int(np.isfinite(values[:,j]).sum())}),flush=True)

assert len(tiles)==1722 and len(ORDER)==120 and len(paths)==120
# Keep all fixed cells, missingness, and original twelve-month check.
pilot=pathlib.Path(sys.argv[5]);assert hashlib.sha256(pilot.read_bytes()).hexdigest()=='00d2d66dc941c563afd7e185b7ab8b19733ce7bbae5f36f70044b50f19149459'
old={r['tile']:r for r in rows(member(pilot,'marine_tiles.csv'))}
assert set(old)=={r['tile'] for r in tiles}
max_diff=0.;pilot_checks=0
for i,r in enumerate(tiles):
    for j,(y,m) in enumerate(ORDER):
        if y not in (1993,2008,2018):continue
        v=values[i,j];prior=old[r['tile']][f'sic_{y}_{m}']
        if not prior:assert not np.isfinite(v)
        else:
            assert np.isfinite(v)
            d=abs(float(v)-float(prior));max_diff=max(max_diff,d)
            assert d<1e-6,(r['tile'],y,m,v,prior)
        pilot_checks+=1
assert pilot_checks==1722*12
years=np.array(Y)
annual=np.column_stack([np.where(np.isfinite(values[:,[ORDER.index((y,m)) for m in M]]).all(axis=1),values[:,[ORDER.index((y,m)) for m in M]].mean(axis=1),np.nan) for y in Y])
complete=np.isfinite(values).all(axis=1)
assert np.array_equal(complete,np.isfinite(annual).all(axis=1)) and complete.any()
x=years-years.mean()
def ice_bin(a):return min(4,int(a//20))
for i,r in enumerate(tiles):
    r['valid_months']=int(np.isfinite(values[i]).sum())
    r['native_wet_pixels']=len(frozen[i])
    r['complete_120']=int(complete[i])
    if complete[i]:
        v=annual[i];a=float(v[:10].mean());b=float(v[-10:].mean())
        r.update(sic30=float(v.mean()),early_sic=a,late_sic=b,delta_sic=b-a,trend_pp_decade=float(10*np.dot(x,v-v.mean())/np.dot(x,x)),annual_sd=float(v.std(ddof=1)),bin30=ice_bin(v.mean()),bin_early=ice_bin(a),bin_late=ice_bin(b))
    else:r.update({k:None for k in ('sic30','early_sic','late_sic','delta_sic','trend_pp_decade','annual_sd','bin30','bin_early','bin_late')})
eligible=[r for r in tiles if r['complete_120']]
bg=defaultdict(list)
for r in eligible:bg[r['block']].append(r)
def wm(rr,key):
    return math.fsum(r['rock_pixels']*r[key] for r in rr)/sum(r['rock_pixels'] for r in rr)
def bins(rr,key,weight=True):
    count=[sum(r['rock_pixels'] if weight else 1 for r in rr if r[key]==i) for i in range(5)]
    return {'counts':count,'fractions':[v/sum(count) for v in count] if sum(count) else None}
transition=np.zeros((5,5),dtype=np.int64)
for r in eligible:transition[r['bin_early'],r['bin_late']]+=r['rock_pixels']
early_bins=bins(eligible,'bin_early');late_bins=bins(eligible,'bin_late')
assert transition.sum(axis=1).tolist()==early_bins['counts'] and transition.sum(axis=0).tolist()==late_bins['counts']
def weighted_median(rr,k):
    z=sorted((r[k],r['rock_pixels']) for r in rr)
    half=sum(w for _,w in z)/2;total=0
    for v,w in z:
        total+=w
        if total>=half:return v
def physical(rr):
    return {'tiles':len(rr),'rock_pixels':sum(r['rock_pixels'] for r in rr),'blocks':len({r['block'] for r in rr}),**{k:wm(rr,k) for k in ('sic30','early_sic','late_sic','delta_sic','trend_pp_decade','annual_sd')},'weighted_median_trend':weighted_median(rr,'trend_pp_decade'),'tiles_decline':sum(r['delta_sic']<0 for r in rr),'tiles_increase':sum(r['delta_sic']>0 for r in rr),'rock_fraction_decline':sum(r['rock_pixels'] for r in rr if r['delta_sic']<0)/sum(r['rock_pixels'] for r in rr)}
summ={'status':'EXECUTED_FIXED_30YEAR_COASTAL_OPPORTUNITY_SIC','frame_tiles':len(tiles),'complete_tiles':len(eligible),'complete_rock_pixels':sum(r['rock_pixels'] for r in eligible),'frame_rock_pixels':sum(r['rock_pixels'] for r in tiles),'physical':physical(eligible),'opportunity_bins30':bins(eligible,'bin30'),'opportunity_bins_early':early_bins,'opportunity_bins_late':late_bins,'transition_rock_pixels':transition.tolist(),'groups':{},'original_months':ORDER,'pilot_QA':{'checks':pilot_checks,'max_absolute_difference_pp':max_diff}}
for group in ('known','modern','ADPE','CHPE','GEPE'):
    total=[r for r in tiles if r['recorded_'+group]]
    obs=[r for r in total if r['complete_120']]
    assert obs
    g={'frame_tiles':len(total),'complete_tiles':len(obs),'blocks':len({r['block'] for r in obs}),'metrics':{}}
    for k in ('sic30','delta_sic','trend_pp_decade','annual_sd','has_plant'):
        a=statistics.mean(r[k] for r in obs)
        diff=[r[k]-wm(bg[r['block']],k) for r in obs]
        dd=defaultdict(list)
        for r,v in zip(obs,diff):dd[r['block']].append(v)
        bm={b:statistics.mean(v) for b,v in dd.items()}
        lobo=[statistics.mean(v for r,v in zip(obs,diff) if r['block']!=b) for b in bm] if len(bm)>1 else []
        g['metrics'][k]={'observed':a,'expected':a-statistics.mean(diff),'difference':statistics.mean(diff),'equal_block_difference':statistics.mean(bm.values()),'blocks_positive':sum(v>0 for v in bm.values()),'blocks_negative':sum(v<0 for v in bm.values()),'lobo_min':min(lobo) if lobo else None,'lobo_max':max(lobo) if lobo else None}
    g['bins30_observed']=bins(obs,'bin30',False)
    summ['groups'][group]=g
# Store all rows, including absent native support. No source values replaced.
def write_csv(name,fields,records):
    with (out/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
write_csv('marine_tiles_30yr.csv',list(tiles[0]),tiles)
write_csv('monthly_120.csv',['tile','year','month','sic_pp'],({'tile':r['tile'],'year':y,'month':m,'sic_pp':float(values[i,j]) if np.isfinite(values[i,j]) else None} for i,r in enumerate(tiles) for j,(y,m) in enumerate(ORDER)))
write_csv('annual_30.csv',['tile','year','sic_pp'],({'tile':r['tile'],'year':y,'sic_pp':float(annual[i,j]) if np.isfinite(annual[i,j]) else None} for i,r in enumerate(tiles) for j,y in enumerate(Y)))
(out/'result.json').write_text(json.dumps(summ,indent=2,allow_nan=False)+'\n')
print('V26_RESULT='+json.dumps(summ),flush=True)
