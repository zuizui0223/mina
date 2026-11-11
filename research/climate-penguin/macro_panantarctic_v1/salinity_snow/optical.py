"""Sentinel-2 public COG seasonal sample. Each site has a fixed 20-m UTM grid."""
import json,hashlib,sys,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np,pandas as pd,requests,rasterio,geopandas as gp
from pyproj import Transformer
from shapely.geometry import Point
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.windows import from_bounds
from rasterio.warp import reproject,Resampling,transform_bounds
from acquire import R,S
F=R/"optical"
F.mkdir(exist_ok=True)
ocean=pd.read_csv(R.parent/"outputs/panantarctic_595_site_inventory.csv").set_index("site_id")
matches=pd.read_csv(R/"expanded_marine_matches.csv")
sites=sorted(set(pd.read_csv(next(S.glob("observed_2species*.csv"))).site_id) | set(matches.query("scope=='site' and annual and cal==5").high_site))
def grid(site):
    c=ocean.loc[site];crs=f"EPSG:{32701+int((c.longitude+180)//6)}"
    x,y=Transformer.from_crs(4326,crs,always_xy=True).transform(c.longitude,c.latitude)
    return crs,from_origin(round(x/20)*20-500,round(y/20)*20+500,20,20),x,y
def mask_sites(source):
    g=gp.read_file(source)
    for site in sites:
        crs,t,x,y=grid(site); circle=Point(x,y).buffer(500)
        gg=g[g.Vegetation.isin(["Vegetation","Lichen"])].to_crs(crs)
        hits=gg.geometry.iloc[gg.sindex.query(circle,predicate="intersects")].intersection(circle)
        mask=rasterize([(a,1) for a in hits if a.area],out_shape=(50,50),transform=t,dtype="uint8") if len(hits) else np.zeros((50,50),"uint8")
        np.save(F/(site+"_mask.npy"),mask)
def catalog(job):
    site,summer,m=job; c=ocean.loc[site]; yr=summer-(m>=10);lo=pd.Timestamp(yr,m,1);hi=lo+pd.offsets.MonthEnd()
    collection="sentinel-2-c1-l2a" if yr>=2024 else "sentinel-2-l2a"
    path=F/f"{site}_{summer}_{m:02}_{collection}_series.json"
    if path.exists():return json.loads(path.read_text())
    url="https://earth-search.aws.element84.com/v1/search"
    params={"collections":collection,"bbox":f"{c.longitude-.0001},{c.latitude-.0001},{c.longitude+.0001},{c.latitude+.0001}","datetime":f"{lo:%Y-%m-%d}T00:00:00Z/{hi:%Y-%m-%d}T23:59:59Z","limit":100}
    items=[]
    while url:
        res=requests.get(url,params=params,timeout=45);res.raise_for_status();d=res.json();items += [f for f in d["features"] if f["assets"]["scl"]["href"].startswith("https://") and f["assets"]["scl"]["href"].endswith(".tif")]
        url=next((k["href"] for k in d["links"] if k["rel"]=="next"),None);params=None
    rows=[]
    for date in sorted({f["properties"]["datetime"][:10] for f in items}):
        fs=[f for f in items if f["properties"]["datetime"][:10]==date]
        if not fs:continue
        f=min(fs,key=lambda v:(v["properties"].get("eo:cloud_cover",101),v["id"]))
        assets={k:f["assets"][k] for k in (["scl","red","nir"] if m in (1,2,3) else ["scl"])}
        rows.append(dict(site=site,summer=summer,date=f["properties"]["datetime"][:10],id=f["id"],collection=collection,offset_applied=False if collection=="sentinel-2-c1-l2a" else f["properties"].get("earthsearch:boa_offset_applied"),assets=assets))
    path.write_text(json.dumps(rows));return rows
def read(r):
    dst=F/f"{r['site']}_{r['id']}.npz"
    if dst.exists():return
    crs,t,x,y=grid(r["site"]); arr={}
    for k,a in r["assets"].items():
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",GDAL_HTTP_TIMEOUT=25,GDAL_HTTP_MAX_RETRY=2):
            with rasterio.open(a["href"]) as s:
                bounds=transform_bounds(crs,s.crs,t.c-50,t.f-1050,t.c+1050,t.f+50)
                w=from_bounds(*bounds,s.transform).round_offsets().round_lengths()
                raw=s.read(1,window=w,boundless=True,fill_value=0)
                target=np.zeros((50,50),dtype=np.float32)
                reproject(raw,target,src_transform=s.window_transform(w),src_crs=s.crs,dst_transform=t,dst_crs=crs,src_nodata=0,dst_nodata=0,resampling=Resampling.nearest if k=="scl" else Resampling.average)
        if k!="scl":
            band=a["raster:bands"][0];off=band.get("offset",0)
            assert not off or r["offset_applied"] is not None
            target=np.where(target>0,target*band["scale"]+(0 if r["offset_applied"] else off),np.nan)
        arr[k]=target.astype("uint8" if k=="scl" else "float32")
    np.savez_compressed(dst,**arr)
def retry(fn,job):
    for i in range(3):
        try:return fn(job)
        except Exception as e:err=repr(e);time.sleep(1+i)
    raise RuntimeError((str(job)[:100],err))
if __name__=="__main__":
    mask_sites(sys.argv[1])
    with ThreadPoolExecutor(max_workers=10) as ex:
        batches=list(ex.map(lambda j:retry(catalog,j),[(s,y,m) for s in sites for y in range(2018,2026) for m in (10,11,12,1,2,3) if np.load(F/(s+"_mask.npy")).any()]))
        items=[r for b in batches for r in b]
        print("selected",len(items),flush=True)
        list(ex.map(lambda r:retry(read,r),items))
