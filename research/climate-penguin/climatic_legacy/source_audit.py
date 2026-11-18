#!/usr/bin/env python3
"""Outcome-blind OSI-450-a1 historical source audit. Does not read penguin counts."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = "https://thredds.met.no/thredds/catalog/osisaf/met.no/reprocessed/ice/conc_450a1_files/monthly/catalog.xml"
SERVER = "https://thredds.met.no/thredds/fileServer/"
SAMPLES = [(1979, 8), (1979, 11), (1986, 8), (1987, 9), (1988, 9),
           (1991, 8), (2001, 9), (2020, 11)]
OUT = Path(__file__).parent / "source_audit_outputs"
OUT.mkdir(exist_ok=True)

def fetch(url: str, limit: int = 35000000) -> bytes:
    if urlparse(url).hostname != "thredds.met.no" or urlparse(url).scheme != "https":
        raise ValueError("unexpected source host")
    last = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent":"mina-climatic-legacy-20261108/1.0"}), timeout=80) as f:
                if urlparse(f.geturl()).hostname != "thredds.met.no":
                    raise ValueError("redirect host changed")
                data = f.read(limit + 1)
            if not 0 < len(data) <= limit:
                raise ValueError("empty/oversized source")
            return data
        except Exception as e:
            last = e
            time.sleep(1 + attempt * 2)
    raise RuntimeError(f"{url}: {type(last).__name__}: {last}")

def parse_xml(raw:bytes, url:str):
    root=ET.fromstring(raw)
    if root.tag.split("}")[-1] != "catalog":
        raise ValueError("not THREDDS XML catalog")
    refs=[];datasets=[]
    for node in root.iter():
        tag=node.tag.split("}")[-1]
        if tag=="catalogRef":
            href=node.attrib.get("{http://www.w3.org/1999/xlink}href","")
            ref=urljoin(url,href)
            if urlparse(ref).hostname=="thredds.met.no":
                refs.append({"name":node.attrib.get("name",node.attrib.get("{http://www.w3.org/1999/xlink}title","")),
                             "url":ref})
        elif tag=="dataset" and node.attrib.get("urlPath"):
            datasets.append(node.attrib["urlPath"])
    return refs,datasets

def describe(path:Path):
    import numpy as np
    import xarray as xr
    with xr.open_dataset(path, decode_times=False) as ds:
        names=list(ds.variables)
        shape={name:{"shape":list(ds[name].shape),
                      "dims":list(ds[name].dims),
                      "units":str(ds[name].attrs.get("units","")),
                      "scale_factor":str(ds[name].encoding.get("scale_factor","")),
                      "fill_value":str(ds[name].encoding.get("_FillValue",""))}
               for name in names}
        val={}
        for key in ["ice_conc","raw_ice_conc_values","status_flag","lat","lon"]:
            if key in ds:
                arr=np.asarray(ds[key].values)
                ff=arr[np.isfinite(arr)]
                val[key]={"finite":int(ff.size),"min":float(ff.min()) if ff.size else None,
                          "max":float(ff.max()) if ff.size else None}
        return {"variables":shape,"global_attrs":{k:str(v) for k,v in ds.attrs.items()
                                                   if k in ("title","product_version","history","source","references","institution")},
                "values":val}

def main():
    rootraw=fetch(ROOT, 4000000)
    refs, datasets=parse_xml(rootraw,ROOT)
    report={"status":"SOURCE_AUDIT_INCOMPLETE",
            "product":"OSI SAF OSI-450-a1 v3.1 DOI 10.15770/EUM_SAF_OSI_0023",
            "catalog":ROOT,"catalog_sha256":hashlib.sha256(rootraw).hexdigest(),
            "top_references":[x["name"] for x in refs][:60],
            "top_datasets_count":len(datasets),"samples":[]}
    print("TOP_CATALOG="+json.dumps({"refs":report["top_references"],
                                     "files":len(datasets)},ensure_ascii=False),flush=True)
    for year in sorted({y for y,m in SAMPLES}):
        matching=[x for x in refs if x["name"].strip()==str(year)]
        if len(matching)!=1:
            print(f"CATALOG_YEAR_MISSING year={year} matches={len(matching)}",flush=True)
            continue
        raw=fetch(matching[0]["url"],4000000)
        _, entries=parse_xml(raw,matching[0]["url"])
        for y,m in [v for v in SAMPLES if v[0]==year]:
            pat=re.compile(r"ice_conc_sh_ease2-250_cdr-v3p1_"+f"{y:04d}{m:02d}"+r"\.nc$")
            hit=[n for n in entries if pat.search(n)]
            item={"year":y,"month":m,"matches":len(hit),"catalog_sha256":hashlib.sha256(raw).hexdigest()}
            if len(hit)==1:
                item["url"]=SERVER+hit[0]
                data=fetch(item["url"])
                if not (data.startswith(b"CDF") or data.startswith(b"\x89HDF")):
                    raise ValueError("not a netCDF file")
                path=OUT/Path(hit[0]).name
                path.write_bytes(data)
                item.update({"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),
                             "schema":describe(path)})
                path.unlink()
            report["samples"].append(item)
            print("SAMPLE_AUDIT="+json.dumps(item,ensure_ascii=False),flush=True)
    report["status"]="SOURCE_SAMPLES_OK" if len(report["samples"])==len(SAMPLES) and all(r["matches"]==1 for r in report["samples"]) else "SOURCE_HOLD"
    (OUT/"source_audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("SOURCE_AUDIT_FINAL="+json.dumps({"status":report["status"],"n":len(report["samples"]),
           "early":len([x for x in report["samples"] if x["year"]<1991]),
           "overlap":len([x for x in report["samples"] if x["year"]>=1991])}),flush=True)
    if report["status"]!="SOURCE_SAMPLES_OK":
        raise SystemExit(2)

if __name__=="__main__":
    main()
