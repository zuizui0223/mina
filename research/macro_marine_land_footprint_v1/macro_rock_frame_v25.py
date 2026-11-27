"""V25 fixed coastal rock opportunity inventory, not an occupancy model."""
import csv,hashlib,io,json,math,pathlib,statistics,sys,urllib.request,zipfile
from collections import Counter,defaultdict
import numpy as np
import shapely as sh
import pyogrio
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from scipy.ndimage import distance_transform_edt
from urllib.parse import urlparse
from pyproj import CRS,Transformer,Geod

root=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
SP=('ADPE','CHPE','GEPE');RADII=(250,1000,5000)
BASE='https://www.penguinmap.com/api/v1/'
SOURCES={'release':('release/?format=json','8f676f6498b1bc79708a67fb05d4ac8ee73249444e85402af87f6a3c64280a65'),'sites':('sites/?format=csv','36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34'),'p1':('observations/?format=csv&page_size=5000&page=1','cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075'),'p2':('observations/?format=csv&page_size=5000&page=2','c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3')}
NZ='manaakiwhenua2021aerial'
def dump(name,obj): (out/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def read(raw):
    d=csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline=''))
    assert d.fieldnames and len(d.fieldnames)==len(set(d.fieldnames))
    r=list(d);assert all(None not in x for x in r)
    return r
def table(name,rows):
    if not rows:return
    with (out/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def get(url,pin,maxbytes=20000000):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'mina-source-audit/1.0'}),timeout=70) as f:
        b=f.read(maxbytes+1)
    assert 0<len(b)<=maxbytes and hashlib.sha256(b).hexdigest()==pin,(url,len(b),hashlib.sha256(b).hexdigest())
    return b
raw={k:get(BASE+p,s) for k,(p,s) in SOURCES.items()}
release=json.loads(raw['release']);assert release['version']=='5.0' and release['release_date']=='2026-10-21' and release['license'].startswith('CC BY 4.0')
sites=read(raw['sites']);p1=read(raw['p1']);p2=read(raw['p2'])
assert len(sites)==729 and len(p1)==5000 and len(p2)==487 and int(p1[-1]['id'])+1==int(p2[0]['id'])
S={x['site_id']:x for x in sites};assert len(S)==729 and all(x['mapppd_version']=='5.0' and x['region'] and x['site_name'] for x in sites)
obs=p1+p2;assert len({x['id'] for x in obs})==5487
grp=defaultdict(list);flags=Counter();zero_flags=Counter()
def number(v):
    try:
        x=float(v.replace(',','').strip())
        return x if math.isfinite(x) and 0<=x<1e10 else None
    except (ValueError,AttributeError):return None
def known(x):return x.strip().casefold() not in ('','unknown','na','n/a','none','null','unspecified','-','not specified')
for x in obs:
    assert x['site_id'] in S and x['site_name']==S[x['site_id']]['site_name'] and x['mapppd_version']=='5.0'
    if x['species_id'] not in SP or x['type']!='nests':continue
    flags[x['presence']]+=1
    n=number(x['count'])
    if n==0:zero_flags[x['presence']]+=1
    try:y=int(x['season'])
    except ValueError:continue
    if str(y)!=x['season'] or not 1890<=y<=2026 or x['presence']!='1' or n is None:continue
    grp[(x['site_id'],x['species_id'],y)].append({**x,'year':y,'n':n})
valid={k:v[0] for k,v in grp.items() if len(v)==1}
dup={k:v for k,v in grp.items() if len(v)>1}
assert len(dup)==426 and sum(map(len,dup.values()))==1022,(len(dup),sum(map(len,dup.values())))
pairs=[]
for (sid,sp,y),a in valid.items():
    b=valid.get((sid,sp,y+1))
    if b and a['citekey'].strip() and a['citekey']==b['citekey'] and a['vantage'].strip() and a['vantage']==b['vantage']:
        pairs.append((sid,sp,y,a,b))
assert len(pairs)==771 and len({x[0] for x in pairs})==95 and len({S[x[0]]['region'] for x in pairs})==11 and Counter(x[1] for x in pairs)=={'ADPE':414,'CHPE':152,'GEPE':205}
pre=defaultdict(set)
for sid,sp,y,a,b in pairs:pre[sp,S[sid]['region'],y].add(sid)
assert sum(len(v)>=5 for v in pre.values())==54
domain={sid for sid,sp,y in valid if float(S[sid]['latitude'])<=-60}
assert all(-90<=float(S[s]['latitude'])<=-60 and -180<=float(S[s]['longitude'])<=180 for s in domain)

# Original source URLs from the BAS catalogue's exact download links.
BAS={
 'rock':('https://ramadda.data.bas.ac.uk/repository/entry/get/add_rockoutcrop_landsat_v7.3.zip?entryid=synth%3A178ec50d-1ffb-42a4-a4a3-1145419da2bb%3AL2FkZF9yb2Nrb3V0Y3JvcF9sYW5kc2F0X3Y3LjMuemlw',75000000),
 'coast':('https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_line_v7_12.shp.zip?entryid=synth%3Adbaf29f5-c8dc-4e79-aeb1-1df316e951ec%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfbGluZV92N18xMi5zaHAuemlw',85000000),
 'plant':('https://figshare.com/ndownloader/files/43483098',15000000)}
receipt={}
def source(name):
    url,cap=BAS[name]
    req=urllib.request.Request(url,headers={'User-Agent':'mina-source-audit/1.0'})
    with urllib.request.urlopen(req,timeout=100) as f:
        b=f.read(cap+1)
        resolved=f.geturl()
    assert 0<len(b)<=cap and b.startswith(b'PK'),(name,len(b))
    sha=hashlib.sha256(b).hexdigest()
    if name=='plant':assert len(b)==5414267 and sha=='7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236'
    folder=root/name;folder.mkdir(parents=True,exist_ok=True)
    (folder/'original.zip').write_bytes(b)
    z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
    assert sum(i.file_size for i in z.infolist())<1500000000
    for m in z.infolist():
        p=pathlib.PurePosixPath(m.filename)
        assert not p.is_absolute() and '..' not in p.parts
        if m.is_dir():continue
        dst=folder.joinpath(*p.parts);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read(m))
    files=[p for p in folder.rglob('*.shp') if '__MACOSX' not in p.parts and not p.name.startswith('._')]
    assert len(files)==1,(name,[str(p) for p in files])
    df=pyogrio.read_dataframe(files[0])
    assert CRS.from_user_input(df.crs).equals(CRS.from_epsg(3031)),(name,df.crs)
    rec={'url':url,'resolved_host':urlparse(resolved).hostname,'sha256':sha,'bytes':len(b),'features':len(df),'crs':'EPSG:3031','fields':list(df.columns),'geometry_types':dict(Counter(str(x) for x in df.geometry.geom_type))}
    receipt[name]=rec;print('SOURCE_V25='+json.dumps({name:rec}),flush=True)
    return df
def check_polygon(df,name):
    a=np.asarray(df.geometry.array,dtype=object)
    bad=~sh.is_valid(a)|sh.is_empty(a)|sh.is_missing(a)|~np.isin(sh.get_type_id(a),[3,6])
    areas=np.nan_to_num(sh.area(a),nan=0.0)
    assert np.all(areas>=0) and areas.sum()>0
    f=float(areas[bad].sum()/areas.sum())
    receipt[name].update(invalid_n=int(bad.sum()),invalid_area_fraction=f,source_polygon_sum_m2=float(areas.sum()))
    assert f<=.005,(name,'invalid area fraction',f)
    return a[~bad]
rock=source('rock');coast=source('coast');plant=source('plant')
rocks=check_polygon(rock,'rock')
assert 'surface' in coast.columns
types=coast['surface'].astype(str).str.strip().str.lower()
receipt['coast']['surface_counts']=dict(Counter(types))
allowed={'ice coastline','rock coastline'}
assert allowed<=set(types)
coasts=np.asarray(coast.loc[types.isin(allowed)].geometry.array,dtype=object)
assert np.all(sh.is_valid(coasts)&~sh.is_empty(coasts)&np.isin(sh.get_type_id(coasts),[1,5]))
assert 'Vegetation' in plant.columns
assert dict(Counter(plant['Vegetation']))=={'Vegetation':58740,'Lichen':24876,'Snow Algae':3775}
plants=check_polygon(plant.loc[plant['Vegetation'].isin(['Vegetation','Lichen'])],'plant')
dump('sources.json',receipt)
# Fixed EPSG3031 raster. all_touched means detected intersection, NOT cover fraction.
N=7000;D=1000;MIN=-3500000;MAX=3500000
transform=from_origin(MIN,MAX,D,D)
def mask(g):
    bounds=sh.total_bounds(g)
    assert np.all(np.isfinite(bounds)) and min(bounds[0],bounds[1])>=MIN and max(bounds[2],bounds[3])<=MAX,(bounds,'fixed grid bounds')
    return rasterize(((v,1) for v in g),out_shape=(N,N),transform=transform,fill=0,dtype='uint8',all_touched=True).astype(bool)
rm=mask(rocks);cm=mask(coasts);pm=mask(plants)
assert rm.any() and cm.any() and pm.any()
print('RASTERIZED='+json.dumps({'rock':int(rm.sum()),'coast':int(cm.sum()),'plant':int(pm.sum())}),flush=True)
# Distance to hit coastal cell centers, not exact distance to a vector coastline.
coastal=distance_transform_edt(~cm,sampling=D)
proj=Transformer.from_crs(4326,3031,always_xy=True)
inv=Transformer.from_crs(3031,4326,always_xy=True)
_,rr=proj.transform(0,-60);rr=abs(rr)
xx=MIN+(np.arange(N)+.5)*D; yy=MAX-(np.arange(N)+.5)*D
domainmask=(yy[:,None]**2+xx[None,:]**2)<=rr**2
assert rm[domainmask].any()
# Grid grouping with explicit source-registered points. No nearest rock snapping.
modern={sp:{sid for (sid,s,y),x in valid.items() if s==sp and sid in domain and 2017<=y<=2023 and x['n']>0} for sp in SP}
groups={'known':domain,'modern':set.union(*modern.values()),**{s:modern[s] for s in SP}}
assert {k:len(v) for k,v in groups.items()}=={'known':594,'modern':212,'ADPE':41,'CHPE':137,'GEPE':57}
def tile_for(x,y):
    c=math.floor((x-MIN)/10000);r=math.floor((MAX-y)/10000)
    assert 0<=c<N//10 and 0<=r<N//10
    return r*(N//10)+c
sitetiles={}
for sid in sorted(domain):
    x,y=proj.transform(float(S[sid]['longitude']),float(S[sid]['latitude']))
    sitetiles[sid]=tile_for(x,y)
def weighted_mean(rows,key,weight='rock_pixels'):
    n=sum(r[weight] for r in rows)
    return sum(r[key]*r[weight] for r in rows)/n if n else None
def summarize(tile,ss):
    observed={sitetiles[s] for s in ss}
    covered=observed&tile.keys()
    v=[tile[k] for k in sorted(covered)]
    bg=list(tile.values())
    byblock=defaultdict(list)
    for r in bg:byblock[r['block']].append(r)
    def describe(rr):
        return {'tiles':len(rr),'blocks':len({x['block'] for x in rr}),'mean_rock_pixels':statistics.mean(x['rock_pixels'] for x in rr) if rr else None,'vegetation_tile_fraction':statistics.mean(x['has_plant'] for x in rr) if rr else None,'plant_rock_pixel_fraction':sum(x['plant_rock_pixels'] for x in rr)/sum(x['rock_pixels'] for x in rr) if rr else None}
    return {'source_sites':len(ss),'source_distinct_tiles':len(observed),'inside_sites':sum(sitetiles[s] in tile for s in ss),'inside_tiles':len(covered),'observed':describe(v),'block_expected_vegetation_tile_fraction':statistics.mean(weighted_mean(byblock[r['block']],'has_plant') for r in v) if v else None,'block_expected_rock_pixel_plant_fraction':statistics.mean(weighted_mean(byblock[r['block']],'plant_rock_fraction') for r in v) if v else None,'observed_equal_tile_plant_rock_fraction':statistics.mean(r['plant_rock_fraction'] for r in v) if v else None}
alltiles=[];summaries=[]
for band in (1,5,10):
    hit=rm&domainmask&(coastal<=band*1000)
    r,c=np.nonzero(hit);assert len(r)>0
    width=N//10;idx=(r//10)*width+c//10
    bc=np.bincount(idx,minlength=width**2)
    br=np.bincount(idx,weights=r,minlength=width**2);bcol=np.bincount(idx,weights=c,minlength=width**2)
    bp=np.bincount(idx,weights=pm[r,c].astype(int),minlength=width**2)
    tile={}
    for k in np.flatnonzero(bc):
        count=int(bc[k]);pcount=int(bp[k])
        x=MIN+(bcol[k]/count+.5)*D;y=MAX-(br[k]/count+.5)*D
        lon,lat=inv.transform(x,y)
        block=f'{math.floor(x/250000)}:{math.floor(y/250000)}'
        row={'band_km':band,'tile':int(k),'tile_x':int(k%width),'tile_y':int(k//width),'x':x,'y':y,'lon':lon,'lat':lat,'block':block,'rock_pixels':count,'plant_rock_pixels':pcount,'has_plant':int(pcount>0),'plant_rock_fraction':pcount/count,**{f'recorded_{name}':int(k in {sitetiles[s] for s in ss}) for name,ss in groups.items()}}
        assert 0<=pcount<=count<=100
        tile[int(k)]=row
    assert sum(t['rock_pixels'] for t in tile.values())==len(r)
    summary={'coastal_band_km':band,'mapped_rock_hit_pixels':len(r),'opportunity_tiles':len(tile),'spatial_blocks':len({x['block'] for x in tile.values()}),'mapped_plant_rock_pixels':int(bp.sum()),'opportunity_plant_tile_fraction':statistics.mean(x['has_plant'] for x in tile.values()),'opportunity_rock_pixel_plant_fraction':float(bp.sum()/len(r)),'groups':{k:summarize(tile,v) for k,v in groups.items()}}
    summaries.append(summary);alltiles.extend(tile.values())
    print('COASTAL_FRAME='+json.dumps(summary),flush=True)
assert all(summaries[i]['mapped_rock_hit_pixels']<=summaries[i+1]['mapped_rock_hit_pixels'] and summaries[i]['opportunity_tiles']<=summaries[i+1]['opportunity_tiles'] for i in range(2))
table('opportunity_tiles.csv',alltiles)
table('site_tiles.csv',[{'site_id':sid,'tile':k,**{f'recorded_{g}':int(sid in v) for g,v in groups.items()}} for sid,k in sitetiles.items()])
result={'status':'EXECUTED_CONTINENTAL_MAPPED_ROCK_FRAME','source_receipts':receipt,'all_rock_hit_pixels_south60':int((rm&domainmask).sum()),'summaries':summaries,'limits':'all-touched 1km detection pixels, not rock area; no terrain, snow, survey absence or walking access; static mapped geography'}
dump('result.json',result);print('V25_GEOGRAPHY='+json.dumps(result),flush=True)
