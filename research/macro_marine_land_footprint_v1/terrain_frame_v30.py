"""V30: reconstruct frozen coastal rock frame and native 500m REMA terrain context."""
import csv,hashlib,io,json,math,pathlib,statistics,sys,urllib.request,zipfile
from collections import Counter,defaultdict
import numpy as np
import shapely as sh
import pyogrio
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.windows import from_bounds,Window
from scipy.ndimage import distance_transform_edt
from urllib.parse import urlparse
from pyproj import CRS,Transformer
root,out,frame,dem=map(pathlib.Path,sys.argv[1:5]);out.mkdir(parents=True,exist_ok=True)
def dump(name,obj):(out/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(2**21),b''):h.update(b)
    return h.hexdigest()
assert digest(frame)=='13bfe5866a27f6fbfad681ed4a44d834f6019c663f94193e1039e96b81c22060'
assert digest(dem)=='e19303a2fef417ed040823f4fcf9b263c4765db15677ca2942c03c4fdbbaaabc'
with zipfile.ZipFile(frame) as z:
    assert z.testzip() is None
    paths=[n for n in z.namelist() if pathlib.PurePosixPath(n).name=='opportunity_tiles.csv'];assert len(paths)==1
    tiles=[r for r in csv.DictReader(io.StringIO(z.read(paths[0]).decode('utf-8-sig'))) if r['band_km']=='5']
assert len(tiles)==1722 and len({r['tile'] for r in tiles})==1722
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
    if name=='rock':assert len(b)==40955252 and sha=='7eb0cae84016b758c98a61977c90d0a8c2c6450c4bf82433e08d03ef2e5a4a5a'
    if name=='coast':assert len(b)==47193783 and sha=='5d09ca9b23c726879bfea9e4f8d415fbc8c515d9bbffc9cfd3838ab5e98e2f3f'
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

rock=source('rock');coast=source('coast')
raw=np.asarray(rock.geometry.array,dtype=object)
assert len(raw)==366106 and np.all(~sh.is_empty(raw)&~sh.is_missing(raw)&np.isin(sh.get_type_id(raw),[3,6]))
bad=~sh.is_valid(raw);assert int(bad.sum())==14469
def polygon_parts(g):
    if g is None or g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    if g.geom_type in ('MultiPolygon','GeometryCollection'):return [p for a in g.geoms for p in polygon_parts(a)]
    return []
repaired=sh.make_valid(raw[bad],method='linework')
parts=np.asarray([p for g in repaired for p in polygon_parts(g)],dtype=object)
assert len(parts)==14469 and np.all(sh.is_valid(parts))
rockg=np.concatenate((raw[~bad],parts))
assert len(rockg)==366106
types=coast['surface'].astype(str).str.strip().str.lower()
assert dict(Counter(types))=={'ice coastline':8716,'rock coastline':25302,'ice rumples':62,'rock against ice shelf':684,'grounding line':1513,'ice shelf and front':565}
coastg=np.asarray(coast.loc[types.isin({'ice coastline','rock coastline'})].geometry.array,dtype=object)
assert np.all(sh.is_valid(coastg)&~sh.is_empty(coastg)&np.isin(sh.get_type_id(coastg),[1,5]))
N=7000;D=1000;MIN=-3500000;MAX=3500000
tf=from_origin(MIN,MAX,D,D)
def mask(g):
    return rasterize(((v,1) for v in g),out_shape=(N,N),transform=tf,fill=0,dtype='uint8',all_touched=True).astype(bool)
rm=mask(raw[~bad])|mask(parts)
maskhash=hashlib.sha256(rm.tobytes()).hexdigest()
assert maskhash=='f2a2a20b42056f9453388a80a1b999e810c411205b9ff5d6ade3f9c114119528' and int(rm.sum())==153991
cm=mask(coastg);coastal=distance_transform_edt(~cm,sampling=D)
proj=Transformer.from_crs(4326,3031,always_xy=True)
_,rad=proj.transform(0,-60);rad=abs(rad)
xx=MIN+(np.arange(N)+.5)*D;yy=MAX-(np.arange(N)+.5)*D
hit=rm&(yy[:,None]**2+xx[None,:]**2<=rad**2)&(coastal<=5000)
rr,cc=np.nonzero(hit);assert len(rr)==27911
ids=(rr//10)*700+cc//10
cells=defaultdict(list)
for t,r,c in zip(ids,rr,cc):cells[int(t)].append((int(r),int(c)))
assert set(cells)=={int(r['tile']) for r in tiles}
for r in tiles:
    q=cells[int(r['tile'])];n=len(q)
    assert n==int(r['rock_pixels'])
    assert abs(MIN+(statistics.mean(c for _,c in q)+.5)*D-float(r['x']))<1e-7
    assert abs(MAX-(statistics.mean(a for a,_ in q)+.5)*D-float(r['y']))<1e-7
dump('source_geometry.json',{'source_receipts':receipt,'rock_mask_sha256':maskhash,'coastal_hit_pixels':len(rr),'tiles':len(cells),'dem_sha256':digest(dem)})
print('V30_GEOMETRY='+json.dumps({'tiles':len(cells),'hit_pixels':len(rr),'mask_sha256':maskhash,'exact_tile_count_centroid_checks':1722*3}),flush=True)
tree=sh.STRtree(rockg);outrows=[]
def outward(src,bounds):
    w=from_bounds(*bounds,transform=src.transform)
    c0=math.floor(w.col_off)-1;r0=math.floor(w.row_off)-1
    c1=math.ceil(w.col_off+w.width)+1;r1=math.ceil(w.row_off+w.height)+1
    return Window(c0,r0,c1-c0,r1-r0)
with rasterio.open(dem) as src:
    assert src.crs.to_epsg()==3031 and src.count==1 and src.transform.a==500 and src.transform.e==-500 and src.transform.b==src.transform.d==0
    metadata={'crs':str(src.crs),'width':src.width,'height':src.height,'resolution':list(src.res),'nodata':src.nodata,'transform':list(src.transform),'vertical_reference':'WGS84 ellipsoid'}
    print('V30_DEM='+json.dumps(metadata),flush=True)
    for i,r in enumerate(tiles):
        tid=int(r['tile']);q=cells[tid];tr,tc=divmod(tid,700)
        minx=MIN+tc*10000;maxx=minx+10000;maxy=MAX-tr*10000;miny=maxy-10000
        cellboxes=sh.box([MIN+c*D for a,c in q],[MAX-(a+1)*D for a,c in q],[MIN+(c+1)*D for a,c in q],[MAX-a*D for a,c in q])
        cellunion=sh.union_all(cellboxes)
        idx=tree.query(cellunion,predicate='intersects')
        assert len(idx)>0
        clipped=sh.intersection(rockg[idx],cellunion)
        rockunion=sh.disjoint_subset_union_all(clipped)
        area=float(rockunion.area)
        assert math.isfinite(area) and -1e-6<=area<=len(q)*D**2+1e-3
        w=outward(src,(minx,miny,maxx,maxy));tx=src.window_transform(w)
        data=src.read(1,window=w,boundless=True,masked=True)
        a=np.ma.asarray(data,dtype=float).filled(np.nan)
        assert a.shape==(int(w.height),int(w.width))
        R,C=np.indices(a.shape)
        x=tx.c+(C+.5)*tx.a;y=tx.f+(R+.5)*tx.e
        c=np.floor((x-MIN)/D).astype(int);b=np.floor((MAX-y)/D).astype(int)
        local=(c>=tc*10)&(c<(tc+1)*10)&(b>=tr*10)&(b<(tr+1)*10)
        selected=np.zeros_like(local)
        selected[local]=hit[b[local],c[local]]
        # Rasterize native pixel intersection with original repaired rock polygons,
        # not actual nest elevation or a centroid substituted for the cell.
        rockhit=rasterize(((g,1) for g in rockg[idx]),out_shape=a.shape,transform=tx,fill=0,dtype='uint8',all_touched=True).astype(bool)
        selected&=rockhit
        valid=np.isfinite(a)&selected
        slope=np.full_like(a,np.nan)
        mid=np.isfinite(a[1:-1,1:-1])&np.isfinite(a[1:-1,:-2])&np.isfinite(a[1:-1,2:])&np.isfinite(a[:-2,1:-1])&np.isfinite(a[2:,1:-1])
        gx=(a[1:-1,2:]-a[1:-1,:-2])/1000;gy=(a[:-2,1:-1]-a[2:,1:-1])/1000
        slope[1:-1,1:-1]=np.where(mid,np.degrees(np.arctan(np.hypot(gx,gy))),np.nan)
        sv=selected&np.isfinite(slope)
        n=int(selected.sum());ne=int(valid.sum());ns=int(sv.sum())
        assert ns<=ne<=n
        ep=a[valid];sp=slope[sv];p10=float(np.quantile(ep,.1)) if ne else None;p90=float(np.quantile(ep,.9)) if ne else None
        ok=ne>=3 and ns>=3 and ne>=.5*n and ns>=.5*n
        outrows.append({**r,'rock_union_area_m2':area,'median_coastal_distance_km':statistics.median(float(coastal[u,v])/1000 for u,v in q),'native_selected_pixels':n,'valid_elevation_pixels':ne,'valid_slope_pixels':ns,'median_elevation_m_ellipsoid':float(np.median(ep)) if ne else None,'relief_p90_p10_m':p90-p10 if ne else None,'median_slope_deg':float(np.median(sp)) if ns else None,'terrain_complete':int(ok)})
        if (i+1)%300==0:print('V30_TERRAIN_PROGRESS='+str(i+1),flush=True)
with (out/'terrain_tiles.csv').open('w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(outrows[0]));wr.writeheader();wr.writerows(outrows)
complete=[r for r in outrows if r['terrain_complete']]
res={'status':'EXECUTED_FIXED_REMA_TERRAIN','frame_tiles':len(outrows),'terrain_complete_tiles':len(complete),'complete_blocks':len({r['block'] for r in complete}),'source_dem':metadata,'rock_union_area_km2':sum(r['rock_union_area_m2'] for r in outrows)/1e6,'zero_rock_area_tiles':sum(r['rock_union_area_m2']==0 for r in outrows),'selected_native_pixels':sum(r['native_selected_pixels'] for r in outrows),'valid_elevation_pixels':sum(r['valid_elevation_pixels'] for r in outrows),'valid_slope_pixels':sum(r['valid_slope_pixels'] for r in outrows),'groups':{g:{'tiles':sum(int(r['recorded_'+g]) for r in outrows),'complete':sum(int(r['recorded_'+g]) for r in complete)} for g in ('known','modern','ADPE','CHPE','GEPE')},'limits':'Native ellipsoidal elevation, coarse projected slope and rock-associated terrain, not actual accessible nesting surface or survey effort.'}
dump('result.json',res);print('V30_RESULT='+json.dumps(res),flush=True)
