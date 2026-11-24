"""Targeted post-QA diagnostic: original green/SWIR1 bands for two discrepant calendar days.
No new ecological outcomes; same four original STAC item IDs.
"""
import pathlib,json,hashlib,math,sys,requests,numpy as np,rasterio,planetary_computer
from rasterio.windows import from_bounds,Window
from rasterio.warp import transform_bounds
from concurrent.futures import ThreadPoolExecutor,as_completed
OUT=pathlib.Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
BOX=(476400,2648080,477960,2649100)
ITEMS=[
("sentinel-2-l2a","S2A_MSIL2A_20180120T015541_R031_T49DDG_20201014T070811","2018-01-20"),
("sentinel-2-l2a","S2A_MSIL2A_20180127T014541_R131_T49DDG_20201014T090548","2018-01-27"),
("landsat-c2-l2","LC08_L2SR_105106_20180120_02_T2","2018-01-20"),
("landsat-c2-l2","LC08_L2SR_106107_20180127_02_T2","2018-01-27")]
def run(t):
    coll,ident,day=t;rec={"collection":coll,"scene_id":ident,"day":day,"bands":[]}
    try:
        u=f"https://planetarycomputer.microsoft.com/api/stac/v1/collections/{coll}/items/{ident}"
        response=requests.get(u,timeout=25);response.raise_for_status();item=response.json()
        assert item["id"]==ident and item["properties"]["datetime"][:10]==day
        rec["datetime"]=item["properties"]["datetime"]
        rec["item_sha256"]=hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest()
        bands=[("green","B03"),("swir","B11")] if coll.startswith("sentinel") else [("green","green"),("swir","swir16"),("sat","qa_radsat")]
        for name,key in bands:
            asset=item["assets"][key];href=asset["href"].split("?")[0]
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_MAX_RETRY="1"):
                with rasterio.open(planetary_computer.sign(href)) as ds:
                    f=from_bounds(*transform_bounds("EPSG:32749",ds.crs,*BOX),ds.transform)
                    c0=max(0,math.floor(f.col_off));r0=max(0,math.floor(f.row_off));c1=min(ds.width,math.ceil(f.col_off+f.width));r1=min(ds.height,math.ceil(f.row_off+f.height))
                    w=Window(c0,r0,c1-c0,r1-r0);assert 0<w.width*w.height<100000
                    a=ds.read(1,window=w,masked=True);fn=f"{coll}_{day}_{name}.npz"
                    np.savez_compressed(OUT/fn,values=a.data,mask=np.ma.getmaskarray(a),transform=np.array(tuple(ds.window_transform(w))[:6]),crs=np.array(ds.crs.to_wkt()))
                    rec["bands"].append({"name":name,"key":key,"file":fn,"sha256":hashlib.sha256((OUT/fn).read_bytes()).hexdigest(),"asset":href,"raster_bands":asset.get("raster:bands"),"shape":list(a.shape),"crs":str(ds.crs),"resolution":list(ds.res),"scales":list(ds.scales),"offsets":list(ds.offsets)})
        rec["status"]="ok"
    except Exception as e:rec.update(status="error",error=repr(e)[:300].split("?")[0])
    return rec
with ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(run,ITEMS))
(OUT/"receipt.json").write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
