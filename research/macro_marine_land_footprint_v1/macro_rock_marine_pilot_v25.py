"""V25 marine pilot on independent coastal mapped-rock opportunity cells."""
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
Y=(1993,2008,2018);M=(8,9,10,11);ORDER=[(1993,9)]+[(y,m) for y in Y for m in M if (y,m)!=(1993,9)]
BASE='https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/conc_450a1_files/monthly'
cache=out.parent/'original_osi_pilot';cache.mkdir(exist_ok=True)
def download(key):
    y,m=key;name=f'ice_conc_sh_ease2-250_cdr-v3p1_{y:04d}{m:02d}.nc';url=f'{BASE}/{y}/{name}'
    assert pins[key]['publisher_url']==url
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'mina-source-audit/1.0'}),timeout=75) as f:
        b=f.read(25000001)
    sha=hashlib.sha256(b).hexdigest()
    assert len(b)<=25000000 and sha==pins[key]['sha256'],(key,sha,pins[key]['sha256'])
    path=cache/name;path.write_bytes(b)
    return key,path,sha
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    paths={key:(p,sha) for key,p,sha in ex.map(download,ORDER)}
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
values=np.full((len(tiles),12),np.nan)
for j,key in enumerate(ORDER):
    _,_,sic,valid,fingerprint=read_source(key);assert fingerprint==fp
    for i,ids in enumerate(frozen):
        if len(ids)<3:continue
        ok=valid[ids]
        if ok.mean()>=.8:values[i,j]=float(sic[ids[ok]].mean())
    print('V25_ICE_MONTH='+json.dumps({'year':key[0],'month':key[1],'sha256':paths[key][1],'supported_tiles':int(np.isfinite(values[:,j]).sum())}),flush=True)
complete=np.isfinite(values).all(axis=1);assert complete.any()
for i,r in enumerate(tiles):
    r['valid_months']=int(np.isfinite(values[i]).sum());r['native_wet_pixels']=len(frozen[i])
    r['sic12']=float(values[i].mean()) if complete[i] else None
    if complete[i]:
        assert 0<=r['sic12']<=100
        r['ice_bin']=min(4,int(r['sic12']//20))
    else:r['ice_bin']=None
eligible=[r for r in tiles if r['sic12'] is not None];bg=defaultdict(list)
for r in eligible:bg[r['block']].append(r)
def wm(rr,key):
    return sum(r['rock_pixels']*r[key] for r in rr)/sum(r['rock_pixels'] for r in rr)
def bins(rr,weight):
    counts=[sum(r[weight] if weight else 1 for r in rr if r['ice_bin']==i) for i in range(5)]
    n=sum(counts);return {'counts':counts,'fractions':[x/n for x in counts] if n else None}
summ={'status':'EXECUTED_12_SCENE_PILOT_NOT_CLIMATOLOGY','frame_tiles':len(tiles),'complete_tiles':len(eligible),'blocks':len(bg),'all_rock_hit_pixels':sum(r['rock_pixels'] for r in tiles),'supported_rock_hit_pixels':sum(r['rock_pixels'] for r in eligible),'opportunity_equal_tile_bins':bins(eligible,None),'opportunity_rock_pixel_weighted_bins':bins(eligible,'rock_pixels'),'opportunity_weighted_sic':wm(eligible,'sic12'),'groups':{},'original_months':ORDER}
for group in ('known','modern','ADPE','CHPE','GEPE'):
    total=[r for r in tiles if r['recorded_'+group]]
    obs=[r for r in total if r['sic12'] is not None]
    if not obs:
        summ['groups'][group]={'frame_observed_tiles':len(total),'complete_observed_tiles':0};continue
    exp_sic=statistics.mean(wm(bg[r['block']],'sic12') for r in obs)
    exp_bins=[statistics.mean(sum(q['rock_pixels'] for q in bg[r['block']] if q['ice_bin']==i)/sum(q['rock_pixels'] for q in bg[r['block']]) for r in obs) for i in range(5)]
    obs_sic=statistics.mean(r['sic12'] for r in obs)
    exp_plant=statistics.mean(wm(bg[r['block']],'has_plant') for r in obs)
    obs_plant=statistics.mean(r['has_plant'] for r in obs)
    assert abs(sum(exp_bins)-1)<1e-10
    summ['groups'][group]={'frame_observed_tiles':len(total),'complete_observed_tiles':len(obs),'blocks':len({r['block'] for r in obs}),'observed_mean_sic_pp':obs_sic,'same_block_expected_mean_sic_pp':exp_sic,'observed_minus_expected_sic_pp':obs_sic-exp_sic,'observed_bins':bins(obs,None),'expected_same_block_bin_fractions':exp_bins,'observed_plant_tile_fraction':obs_plant,'expected_same_block_plant_tile_fraction':exp_plant}
# Direct sums verify cohort and weighted-bin coverage.
assert sum(summ['opportunity_rock_pixel_weighted_bins']['counts'])==summ['supported_rock_hit_pixels']
for i,r in enumerate(tiles):
    r.update({f'sic_{y}_{m}':float(values[i,j]) if math.isfinite(values[i,j]) else None for j,(y,m) in enumerate(ORDER)})
with (out/'marine_tiles.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(tiles[0]));w.writeheader();w.writerows(tiles)
(out/'result.json').write_text(json.dumps(summ,indent=2,allow_nan=False)+'\n')
print('V25_MARINE='+json.dumps(summ),flush=True)
