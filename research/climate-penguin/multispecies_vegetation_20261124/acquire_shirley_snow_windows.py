"""Fixed original satellite snow-classification pilot, no vegetation outcomes used.
Three preselected January/February year pairs (2018, 2021, 2023), up to three distinct days
per month chosen by scene cloud metadata, separately Sentinel-2 L2A SCL / Landsat8 QA_PIXEL.
Return native raster windows, not resampled or treated as daily snow persistence.
"""
import csv, datetime, hashlib, json, math, pathlib, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np, rasterio, requests, planetary_computer
from pyproj import Transformer
from rasterio.windows import Window, from_bounds
from rasterio.warp import transform_bounds
OUT=pathlib.Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
BOX=(476400,2648080,477960,2649100)
LL=transform_bounds("EPSG:32749","EPSG:4326",*BOX)
URL="https://planetarycomputer.microsoft.com/api/stac/v1/search"
CONFIG=[("sentinel-2-l2a",("SCL","scl"),None),("landsat-c2-l2",("qa_pixel",),"LC08_")]
def catalogue(cfg,year,month):
    coll,keys,prefix=cfg
    start=datetime.date(year,month,1);end=datetime.date(year,month+1,1)-datetime.timedelta(days=1)
    data={"collections":[coll],"bbox":list(LL),"datetime":f"{start}T00:00:00Z/{end}T23:59:59Z","limit":100}
    url=URL;method="POST";allitems=[];hashes=[];seen=set()
    for _ in range(10):
        r=requests.request(method,url,json=data if method=="POST" else None,timeout=30);r.raise_for_status();page=r.json()
        if not isinstance(page.get("features"),list):raise ValueError("not STAC FeatureCollection")
        hashes.append(hashlib.sha256(r.content).hexdigest());allitems+=page["features"]
        n=[l for l in page.get("links",[]) if l.get("rel")=="next"]
        if not n:break
        if len(n)!=1:raise ValueError("ambiguous pagination")
        from urllib.parse import urljoin,urlsplit
        url=urljoin(url,n[0]["href"]);assert urlsplit(url).hostname=="planetarycomputer.microsoft.com"
        method=n[0].get("method","GET");data=n[0].get("body")
        signature=(url,method,json.dumps(data,sort_keys=True))
        if signature in seen:raise ValueError("pagination loop")
        seen.add(signature)
    else:raise ValueError("page cap")
    candidates=[]
    for item in allitems:
        if prefix and not item["id"].startswith(prefix):continue
        key=next((k for k in keys if k in item.get("assets",{}) and item["assets"][k].get("href")),None)
        if key is None:continue
        dt=item["properties"].get("datetime") or ""
        if not dt:continue
        cloud=item["properties"].get("eo:cloud_cover")
        try:cloud=float(cloud)
        except (ValueError,TypeError):cloud=101.
        candidates.append((cloud,dt[:10],item["id"],item,key))
    chosen=[];days=set()
    for cloud,day,id,item,key in sorted(candidates,key=lambda x:x[:3]):
        if day in days:continue
        chosen.append((coll,year,month,cloud,day,id,item,key));days.add(day)
        if len(chosen)==3:break
    return {"collection":coll,"year":year,"month":month,"catalog_items":len(allitems),"eligible_items":len(candidates),"selected":len(chosen),"page_sha256":hashes,"status":"ok"},chosen
def source_window(entry):
    coll,year,month,cloud,day,id,item,key=entry
    href=item["assets"][key]["href"].split("?")[0]
    receipt={"collection":coll,"year":year,"month":month,"scene_id":id,"day":day,"cloud_metadata":cloud,"asset_key":key,"source_href":href,"item_sha256":hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest(),"status":"error"}
    try:
        signed=planetary_computer.sign(href)
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_MAX_RETRY="1"):
            with rasterio.open(signed) as ds:
                b=transform_bounds("EPSG:32749",ds.crs,*BOX,densify_pts=21)
                f=from_bounds(*b,ds.transform)
                c0=max(0,math.floor(f.col_off));r0=max(0,math.floor(f.row_off));c1=min(ds.width,math.ceil(f.col_off+f.width));r1=min(ds.height,math.ceil(f.row_off+f.height))
                if c1<=c0 or r1<=r0:raise ValueError("empty native window")
                w=Window(c0,r0,c1-c0,r1-r0)
                if w.width*w.height>100000:raise ValueError("window unexpectedly large")
                arr=ds.read(1,window=w,masked=True)
                fn=f"{coll}_{year}_{month}_{id}.npz"
                np.savez_compressed(OUT/fn,values=arr.data,mask=np.ma.getmaskarray(arr),transform=np.array(tuple(ds.window_transform(w))[:6]),crs=np.array(ds.crs.to_wkt()),native_offset=np.array([r0,c0]))
                receipt.update(status="ok",file=fn,sha256=hashlib.sha256((OUT/fn).read_bytes()).hexdigest(),crs=str(ds.crs),resolution=list(ds.res),shape=list(arr.shape),valid_native=int((~np.ma.getmaskarray(arr)).sum()))
    except Exception as e:receipt["error"]=repr(e)[:350].split("?")[0]
    return receipt
def main():
    tasks=[(cfg,y,m) for cfg in CONFIG for y in [2018,2021,2023] for m in [1,2]]
    cats=[];items=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        fs={pool.submit(catalogue,*t):t for t in tasks}
        for f in as_completed(fs):
            cfg,y,m=fs[f]
            try:c,ent=f.result();cats.append(c);items.extend(ent)
            except Exception as e:cats.append({"collection":cfg[0],"year":y,"month":m,"status":"error","error":repr(e)[:350]})
    print("CATALOGUE "+json.dumps(cats),flush=True)
    records=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(source_window,i) for i in items]):
            rr=f.result();records.append(rr);print("SCENE "+json.dumps(rr),flush=True)
    obj={"status":"source_window_inventory_only","bbox_utm49s":BOX,"catalogue":cats,"scenes":records,"n_native_windows":sum(r["status"]=="ok" for r in records),"limit":"Classified snow/ice on selected observation days; cloud masking and coarse mixed pixels do not establish snow duration or thaw dates. Not a vegetation trend."}
    (OUT/"receipt.json").write_text(json.dumps(obj,indent=2)+"\n")
    print("SUMMARY "+json.dumps({"n_selected":len(items),"n_ok":obj["n_native_windows"],"n_catalog_errors":sum(c["status"]!="ok" for c in cats)}))
if __name__=="__main__":main()
