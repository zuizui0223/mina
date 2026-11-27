"""V29 direct daily native DEEP-AA P100 at fixed opportunity centroids; no biological fitting."""
import calendar,csv,hashlib,io,json,math,pathlib,re,sys,zipfile,datetime
from collections import Counter,defaultdict
import numpy as np
from netCDF4 import Dataset
from pyproj import CRS,Geod,Proj,Transformer
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix

frame,oldatlas,oldwinter,source,out=map(pathlib.Path,sys.argv[1:6]);out.mkdir(parents=True,exist_ok=True)
YEARS=tuple(range(2004,2011))+tuple(range(2013,2019));MONTHS=(6,7,8,9,10)
KEYS=[(y,m) for y in YEARS for m in MONTHS]
PINS={'frame':'13bfe5866a27f6fbfad681ed4a44d834f6019c663f94193e1039e96b81c22060','atlas':'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a','winter':'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8','source':'b05a36aa4e775d69c06e2ffa897a8de8a20318b65f6478298167f73cc9f7c3f9'}
def digest(p,alg='sha256'):
    h=hashlib.new(alg)
    with p.open('rb') as f:
        for b in iter(lambda:f.read(2**21),b''):h.update(b)
    return h.hexdigest()
def csvmember(p,pin,name):
    assert digest(p)==pin,(p,'digest')
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        names=[n for n in z.namelist() if pathlib.PurePosixPath(n).name==name];assert len(names)==1,(name,names)
        return list(csv.DictReader(io.StringIO(z.read(names[0]).decode('utf-8-sig'))))
def write(name,rows):
    assert rows
    with (out/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def dump(name,obj):(out/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
tiles=[r for r in csvmember(frame,PINS['frame'],'opportunity_tiles.csv') if r['band_km']=='5']
old=csvmember(oldatlas,PINS['atlas'],'panantarctic_595_site_inventory.csv')
ref=csvmember(oldwinter,PINS['winter'],'winter_595.csv')
assert len(tiles)==1722 and len(old)==595 and len(ref)==21420
assert len({r['tile'] for r in tiles})==1722 and len({r['site_id'] for r in old})==595
oldby={r['site_id']:r for r in old}
ref=[r for r in ref if float(r['radius_km'])==100 and int(r['season']) in YEARS]
assert len(ref)==595*13 and len({(r['site_id'],r['season']) for r in ref})==len(ref)
for r in ref:
    a=oldby[r['site_id']]
    assert abs(float(r['colony_lat'])-float(a['latitude']))<1e-6 and abs(float(r['colony_lon'])-float(a['longitude']))<1e-6 and r['source_region']==a['source_region']
places=[{'kind':'tile','id':r['tile'],'lat':float(r['lat']),'lon':float(r['lon'])} for r in tiles]+[{'kind':'old_QA','id':r['site_id'],'lat':float(r['latitude']),'lon':float(r['longitude'])} for r in old]
assert digest(source)==PINS['source'] and digest(source,'md5')=='f3f958389cc5e67ac1c4e3a6ee164318'
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    ll=[n for n in z.namelist() if pathlib.PurePosixPath(n).name.lower()=='lonlat.nc'];assert len(ll)==1
    byday={}
    for name in z.namelist():
        if not name.lower().endswith('.nc') or name==ll[0]:continue
        m=re.search(r'(?<!\d)(20(?:0\d|1\d|2[012])\d{4})(?!\d)',pathlib.PurePosixPath(name).name)
        assert m,name
        day=datetime.datetime.strptime(m.group(1),'%Y%m%d').date()
        assert day not in byday
        byday[day]=name
    source_months=Counter((d.year,d.month) for d in byday)
    coverage=[{'year':y,'month':m,'daily_files':source_months[y,m],'calendar_days':calendar.monthrange(y,m)[1]} for y,m in KEYS]
    manifest={'sha256':PINS['source'],'md5':'f3f958389cc5e67ac1c4e3a6ee164318','source_days':len(byday),'first':min(byday).isoformat(),'last':max(byday).isoformat(),'fixed_months':coverage}
    dump('source_manifest.json',manifest)
    print('V29_SOURCE='+json.dumps({'days':len(byday),'first':manifest['first'],'last':manifest['last'],'fixed_months':len(coverage),'fixed_days':sum(x['daily_files'] for x in coverage),'failed_months':[x for x in coverage if x['daily_files']<.8*x['calendar_days']]}),flush=True)
    assert all(x['daily_files']>=.8*x['calendar_days'] for x in coverage),'SOURCE_HOLD: fixed calendar-month support'
    with Dataset('memory.nc','r',memory=z.read(ll[0])) as f:
        lat=np.ma.asarray(f.variables['Lat'][:],dtype=float).filled(np.nan)
        lon=np.ma.asarray(f.variables['Lon'][:],dtype=float).filled(np.nan)
    assert lat.shape==lon.shape==(1264,1328)
    la=lat.ravel();lo=((lon.ravel()+180)%360)-180
    mask=np.isfinite(la)&np.isfinite(lo)&(la>=-90)&(la<=-50)
    trueidx=np.flatnonzero(mask);assert len(trueidx)>=800000
    tf=Transformer.from_crs(4326,3412,always_xy=True)
    x,y=tf.transform(lo[trueidx],la[trueidx]);tree=cKDTree(np.column_stack([x,y]))
    gd=Geod(ellps='WGS84');pj=Proj(CRS.from_epsg(3412))
    memb=[];weights=[];geom=[]
    for r in places:
        x0,y0=tf.transform(r['lon'],r['lat'])
        ids=trueidx[np.asarray(tree.query_ball_point([x0,y0],155000),dtype=np.int64)]
        if len(ids):
            _,_,d=gd.inv(np.full(len(ids),r['lon']),np.full(len(ids),r['lat']),lo[ids],la[ids]);ids=ids[np.asarray(d)<=100000]
        if len(ids)<80:ids=np.array([],dtype=np.int64)
        factors=np.asarray(pj.get_factors(lo[ids],la[ids]).areal_scale,dtype=float) if len(ids) else np.array([])
        assert np.all(np.isfinite(factors)&(factors>0))
        w=1/factors
        memb.append(ids);weights.append(w)
        geom.append({**r,'native_pixels':len(ids),'nominal_buffer_km2':float(w.sum()*6.25**2),'supported_geometry':int(len(ids)>=80)})
    write('geometry.csv',geom)
    supported=[r for r in geom if r['supported_geometry']]
    print('V29_GEOMETRY='+json.dumps({'tile_supported':sum(r['kind']=='tile' for r in supported),'old_QA_supported':sum(r['kind']=='old_QA' for r in supported)}),flush=True)
    assert sum(r['kind']=='old_QA' for r in supported)==595
    # Compress sparse memberships to used native pixels only; no geographic interpolation.
    allidx=np.unique(np.concatenate(memb));n=len(places)
    indptr=np.concatenate(([0],np.cumsum([len(v) for v in memb]))).astype(np.int64)
    indices=np.searchsorted(allidx,np.concatenate(memb))
    W=csr_matrix((np.concatenate(weights),indices,indptr),shape=(n,len(allidx)))
    assert np.allclose(np.asarray(W.sum(axis=1)).ravel(),np.array([w.sum() for w in weights]),atol=1e-9)
    days=sorted(d for d in byday if (d.year,d.month) in KEYS)
    checkdays={days[0],days[len(days)//2],days[-1]};checktiles=[0,len(tiles)//2,len(tiles)-1,len(tiles),len(places)-1]
    sums=np.zeros((n,len(KEYS)));counts=np.zeros((n,len(KEYS)),dtype=int)
    mi={k:i for i,k in enumerate(KEYS)};categories=Counter();checkcount=0;maxerr=0.
    for j,day in enumerate(days):
        with Dataset('day.nc','r',memory=z.read(byday[day])) as f:
            arr=np.ma.asarray(f.variables['Map'][:],dtype=float).filled(np.nan)
        assert arr.shape==(1264,1328)
        raw=arr.ravel();v=raw[allidx]
        valid=np.isfinite(v)&(v!=-999)
        vv=v[valid];assert np.all(vv==np.trunc(vv)) and not ((vv<0)&~np.isin(vv,[-1,-2,-100])).any()
        integer=np.zeros(len(v),dtype=np.int64);integer[valid]=vv.astype(np.int64)
        coast=valid&(integer>0)&(integer%2==0)
        for k,c in [('land_or_missing',~valid),('coastal',coast),('oceanic',valid&(integer>0)&(integer%2==1)),('zero',valid&(integer==0)),('landfast',valid&(integer==-100)),('open_sea',valid&(integer==-2)),('other_open',valid&(integer==-1))]:categories[k]+=int(c.sum())
        denom=W@valid.astype(float);numer=W@coast.astype(float)
        ok=denom>0;ratio=np.divide(numer,denom,out=np.zeros(n),where=ok)
        assert np.all((ratio>=-1e-12)&(ratio<=1+1e-12))
        k=mi[day.year,day.month];sums[ok,k]+=ratio[ok];counts[ok,k]+=1
        if day in checkdays:
            for i in checktiles:
                p=raw[memb[i]];m=np.isfinite(p)&(p!=-999);q=p[m];w=weights[i][m]
                if w.sum()>0:
                    direct=float(w[(q>0)&(q.astype(np.int64)%2==0)].sum()/w.sum())
                    err=abs(direct-ratio[i]);assert err<1e-11;maxerr=max(maxerr,err)
                else:assert not ok[i]
                checkcount+=1
        if (j+1)%153==0 or j+1==len(days):print('V29_DAILY='+json.dumps({'done':j+1,'total':len(days),'last_day':day.isoformat()}),flush=True)
assert sum(categories.values())==len(days)*len(allidx)
monthly=[];win=[];montharr=np.full(sums.shape,np.nan)
for j,(y,m) in enumerate(KEYS):
    cal=calendar.monthrange(y,m)[1]
    ok=counts[:,j]>=.8*cal
    montharr[ok,j]=sums[ok,j]/counts[ok,j]
    assert (counts[:,j]<=source_months[y,m]).all()
for i,r in enumerate(places):
    for j,(y,m) in enumerate(KEYS):
        v=montharr[i,j]
        monthly.append({'kind':r['kind'],'id':r['id'],'year':y,'month':m,'valid_days':int(counts[i,j]),'calendar_days':calendar.monthrange(y,m)[1],'p100_fraction':float(v) if math.isfinite(v) else None})
    for j,y in enumerate(YEARS):
        v=montharr[i,5*j:5*j+5];nvalid=int(np.isfinite(v).sum())
        win.append({'kind':r['kind'],'id':r['id'],'year':y,'n_valid_months':nvalid,'p100_winter_fraction':float(v.mean()) if nvalid==5 else None,'p100_aug_oct_fraction':float(v[2:].mean()) if nvalid==5 else None})
write('monthly.csv',monthly);write('winter.csv',win)
wi={(r['id'],r['year']):r for r in win if r['kind']=='old_QA'}
oldchecks=0;missingchecks=0;oldmax=0.;mismatches=[]
for r in ref:
    a=wi[r['site_id'],int(r['season'])]
    oldvalue=r['direct_DEEPAA_coastal_polynya_fraction'];new=a['p100_winter_fraction']
    if oldvalue=='' or oldvalue.lower()=='nan':
        if new is not None:mismatches.append({'id':r['site_id'],'year':r['season'],'old':None,'new':new})
        else:missingchecks+=1
    elif new is None:mismatches.append({'id':r['site_id'],'year':r['season'],'old':float(oldvalue),'new':None})
    else:
        err=abs(float(oldvalue)-new);oldmax=max(oldmax,err);oldchecks+=1
        if err>1e-9:mismatches.append({'id':r['site_id'],'year':r['season'],'old':float(oldvalue),'new':new,'abs_difference':err})
assert len(win)==(1722+595)*13 and len(monthly)==(1722+595)*65
tilecomplete=sum(np.isfinite(montharr[i]).all() for i in range(len(tiles)))
res={'status':'EXECUTED_NATIVE_P100' if not mismatches else 'SOURCE_REPRODUCTION_HOLD','frame_tiles':len(tiles),'tile_geometry_support':sum(r['kind']=='tile' for r in supported),'complete_13winter_tiles':int(tilecomplete),'source_days_used':len(days),'native_pixels_used':len(allidx),'categories_over_used_pixel_days':dict(categories),'direct_arithmetic_checks':checkcount,'direct_max_error':maxerr,'archived_old_numeric_checks':oldchecks,'archived_old_missing_checks':missingchecks,'archived_old_max_abs_error_fraction':oldmax,'old_mismatch_count':len(mismatches),'mismatch_first_20':mismatches[:20]}
dump('result.json',res)
print('V29_EXTRACT='+json.dumps(res),flush=True)
if mismatches:raise SystemExit('SOURCE_REPRODUCTION_HOLD')
