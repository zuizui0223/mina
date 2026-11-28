"""V31 land-sea support audit; two original ERA5 snapshots, not a snow season."""
import csv,io,json,hashlib,pathlib,sys,zipfile,urllib.request,statistics
import numpy as np
import numcodecs
from pyproj import Geod
frame,terrain,marine,out=map(pathlib.Path,sys.argv[1:5]);out.mkdir(parents=True,exist_ok=True)
def read(p,h,n):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        a=[s for s in z.namelist() if pathlib.PurePosixPath(s).name==n];assert len(a)==1
        return list(csv.DictReader(io.StringIO(z.read(a[0]).decode('utf-8-sig'))))
tiles=[r for r in read(frame,'13bfe5866a27f6fbfad681ed4a44d834f6019c663f94193e1039e96b81c22060','opportunity_tiles.csv') if r['band_km']=='5']
terr={r['tile']:r for r in read(terrain,'531b94c8f38b4117d54bb9f3de0f293fdcf3120d1a7f991fb7eb8926e4536511','terrain_tiles.csv')}
mar={r['tile']:r for r in read(marine,'5f883169cc78726d80f17a9427738a28da87a139233e049fe9201b83795e765f','shared_aug_oct_tiles.csv')}
assert len(tiles)==len(terr)==1722 and len(mar)==1525
url='https://storage.googleapis.com/gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3'
def get(path):
    with urllib.request.urlopen(url+'/'+path,timeout=75) as f:b=f.read(30000001)
    assert 0<len(b)<=30000000
    return b
raw=get('.zmetadata');meta=json.loads(raw)['metadata'];receipts={}
def chunk(v,index):
    b=get(v+'/'+index);d=meta[v+'/.zarray'];assert d['filters'] is None
    a=np.frombuffer(numcodecs.get_codec(d['compressor']).decode(b),dtype=d['dtype']).reshape(d['chunks'])
    receipts[v+'/'+index]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
    return a
assert meta['snow_depth/.zattrs']['units']=='m of water equivalent'
assert meta['time/.zattrs']['units']=='hours since 1900-01-01 00:00:00'
lat=chunk('latitude','0');lon=chunk('longitude','0')
assert len(lat)==721 and len(lon)==1440
dates=['2011-09-01T00:00:00','2020-09-01T00:00:00']
first=int(chunk('time','0')[0]);length=meta['time/.zarray']['chunks'][0]
idx=[]
for date in dates:
    hour=int((np.datetime64(date)-np.datetime64('1900-01-01T00:00:00'))/np.timedelta64(1,'h'))
    i=hour-first;assert int(chunk('time',str(i//length))[i%length])==hour;idx.append(i)
a={v:np.stack([chunk(v,f'{i}.0.0')[0] for i in idx]) for v in ('land_sea_mask','snow_depth')}
assert all(x.shape==(2,721,1440) and np.isfinite(x).all() for x in a.values())
assert np.array_equal(a['land_sea_mask'][0],a['land_sea_mask'][1])
assert a['land_sea_mask'].min()>=-1e-3 and a['land_sea_mask'].max()<=1.001
g=Geod(ellps='WGS84');rows=[]
for r in tiles:
    t=r['tile'];x,y=float(r['lon']),float(r['lat'])
    j=int(np.argmin(abs(lat-y)));k=int(np.argmin(abs((lon-x+180)%360-180)))
    d=g.inv(x,y,float(lon[k]),float(lat[j]))[2]/1000
    r={**r,'grid_y':j,'grid_x':k,'grid_lat':float(lat[j]),'grid_lon':float(lon[k]),'distance_km':float(d),'land_fraction':float(a['land_sea_mask'][0,j,k]),'swe_2011_m':float(a['snow_depth'][0,j,k]),'swe_2020_m':float(a['snow_depth'][1,j,k]),'marine_complete':int(t in mar),'terrain_complete':int(terr[t]['terrain_complete'])}
    rows.append(r)
def summary(rr):
    return {'tiles':len(rr),'unique_era5_cells':len({(r['grid_y'],r['grid_x']) for r in rr}),'majority_land_tiles':sum(r['land_fraction']>=.5 for r in rr),'majority_land_cells':len({(r['grid_y'],r['grid_x']) for r in rr if r['land_fraction']>=.5}),'majority_land_blocks':len({r['block'] for r in rr if r['land_fraction']>=.5}),'land_gt03_tiles':sum(r['land_fraction']>.3 for r in rr),'zero_land_tiles':sum(r['land_fraction']<=1e-6 for r in rr),'median_land_fraction':statistics.median(r['land_fraction'] for r in rr) if rr else None,'max_distance_km':max(r['distance_km'] for r in rr) if rr else None}
joint=[r for r in rows if r['marine_complete'] and r['terrain_complete']];assert len(joint)==1323
res={'status':'EXECUTED_ERA5_LAND_SUPPORT_AUDIT','source_url':url,'metadata_sha256':hashlib.sha256(raw).hexdigest(),'chunk_receipts':receipts,'snapshots':dates,'all':summary(rows),'marine':summary([r for r in rows if r['marine_complete']]),'marine_terrain':summary(joint),'groups':{k:summary([r for r in joint if int(r['recorded_'+k])]) for k in ('modern','ADPE','CHPE','GEPE')},'limits':'0.25deg nearest grid, water equivalent, two snapshots, no seasonal snow or melt, no true local nest snow, no relocation, no fit.'}
with (out/'snow_support.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'receipt.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
print('V31_SNOW='+json.dumps(res),flush=True)
