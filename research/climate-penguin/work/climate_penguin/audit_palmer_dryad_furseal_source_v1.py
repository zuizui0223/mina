"""Strict original Dryad fur seal 2020 SOURCE and survey-coverage eligibility.

Downloads public original data files, but does NOT inspect seal occupancy at
islands before a separately frozen, surveyed-area georeference eligibility.
No historical seal inference and no penguin/vegetation effect is estimated.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,os,re,time,zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import quote,urljoin,urlparse

import requests

BASE="https://datadryad.org"
DOI="doi:10.5061/dryad.qv9s4mwp0"
DATASET_API=f"{BASE}/api/v2/datasets/{quote(DOI,safe='')}"
REQUIRED={
 "README.md",
 "drone_survey_dates_times.csv",
 "fur_seal_locations_all_surveys.csv",
 "surveyed_regions_land_mask.zip",
 "exposed_land_mask.zip",
}
MAX_RESOURCE_BYTES=20_000_000

def get_json(session,url):
    r=session.get(url,timeout=(20,60),headers={"Accept":"application/json"})
    r.raise_for_status()
    payload=r.json()
    if not isinstance(payload,(dict,list)):
        raise ValueError("SOURCE_STOP expected JSON object/list")
    return payload

def links(obj):
    raw=obj.get("_links",{}) if isinstance(obj,dict) else {}
    return {str(k):v.get("href") for k,v in raw.items() if isinstance(v,dict) and v.get("href")}

def list_versions(data):
    raw=data.get("_embedded",{}) if isinstance(data,dict) else {}
    if isinstance(data,list):return data
    for k in ("stash:versions","versions"):
        if isinstance(raw.get(k),list):return raw[k]
        if isinstance(data.get(k),list):return data[k]
    return []

def current_version(data):
    for k in ("version","versionId","latestVersion","currentVersion"):
        v=data.get(k)
        if isinstance(v,dict) and v.get("id"):return int(v["id"])
        if isinstance(v,(int,str)) and str(v).isdigit():return int(v)
    for name,href in links(data).items():
        if "version" in name and re.search(r"/versions/\d+",href):
            return int(re.search(r"/versions/(\d+)",href).group(1))
    return None

def list_files(obj):
    if isinstance(obj,list):return obj
    if not isinstance(obj,dict):return []
    for k in ("files","items","results"):
        if isinstance(obj.get(k),list):return obj[k]
    embedded=obj.get("_embedded",{})
    for k in ("stash:files","files"):
        if isinstance(embedded.get(k),list):return embedded[k]
    return []

def normalize_file(f):
    ident=f.get("id",f.get("fileId"))
    filename=f.get("path",f.get("filename",f.get("name")))
    size=f.get("size",f.get("bytes",f.get("fileSize")))
    href=None
    for k in ("downloadUrl","download_url","download"):
        x=f.get(k)
        if isinstance(x,str):href=x
    if not href:
        for k,v in links(f).items():
            if "download" in k.lower() or "file" in k.lower():href=v;break
    if not href and ident is not None:
        href=f"/downloads/file_stream/{int(ident)}"
    return {"id":ident,"name":filename,"bytes":size,"href":href,
            "original_sha256":f.get("digest",f.get("checksum"))}

def source_records(session):
    meta=get_json(session,DATASET_API)
    v=current_version(meta)
    if v is None:
        versions=get_json(session,DATASET_API+"/versions")
        available=list_versions(versions)
        if len(available)==1:
            v=int(available[0]["id"])
        elif available:
            # Latest public version only; use metadata's explicit version if possible.
            v=max(int(x["id"]) for x in available)
    if v is None:
        raise ValueError("SOURCE_STOP Dryad REST dataset did not expose public version ID")
    files=get_json(session,f"{BASE}/api/v2/versions/{v}/files")
    items=list_files(files)
    names=[str(normalize_file(x)["name"]) for x in items]
    expected={n for n in names if n in REQUIRED}
    if len(names)!=len(set(names)):
        raise ValueError("SOURCE_STOP duplicate publicly listed filename")
    if expected!=REQUIRED:
        raise ValueError(f"SOURCE_STOP missing original source files: {sorted(REQUIRED-expected)}")
    return meta,v,[normalize_file(x) for x in items]

def save_resource(session,item,out):
    name=item["name"]
    if name not in REQUIRED:raise ValueError("SOURCE_STOP unexpected file request")
    size=int(item["bytes"])
    if not 0<size<MAX_RESOURCE_BYTES:
        raise ValueError(f"SOURCE_STOP original {name} size outside bound")
    uri=item["href"]
    if not uri:raise ValueError("SOURCE_STOP file lacks original download href")
    url=urljoin(BASE,uri)
    u=urlparse(url)
    if u.scheme!="https" or u.hostname not in (
       "datadryad.org","www.datadryad.org","datadryad-asset-store.s3.amazonaws.com",
       "datadryad.s3.amazonaws.com","s3.amazonaws.com"):
        raise ValueError(f"SOURCE_STOP unexpected original file hostname {u.hostname}")
    with session.get(url,timeout=(25,90),stream=True) as response:
        response.raise_for_status()
        raw=bytearray()
        for block in response.iter_content(chunk_size=65536):
            raw.extend(block)
            if len(raw)>MAX_RESOURCE_BYTES:raise ValueError("SOURCE_STOP oversized file")
    data=bytes(raw)
    if len(data)!=size:
        raise ValueError(f"SOURCE_STOP original {name} downloaded length {len(data)} != {size}")
    if name.endswith(".csv"):
        text=data.decode("utf-8-sig")
        sample=list(csv.reader(io.StringIO(text)))
        if not sample:raise ValueError("SOURCE_STOP empty original CSV")
        fields=sample[0]
        nrows=len(sample)-1
        if len(fields)!=len(set(fields)):
            raise ValueError("SOURCE_STOP duplicate original CSV columns")
    elif name.endswith(".zip"):
        if not data.startswith(b"PK"):raise ValueError("SOURCE_STOP original polygon not a ZIP")
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            if z.testzip() is not None:raise ValueError("SOURCE_STOP ZIP CRC invalid")
            zpaths=[x.filename for x in z.infolist()]
            if not any(x.lower().endswith(".shp") for x in zpaths):
                raise ValueError("SOURCE_STOP source surveyed mask lacks shapefile")
        fields=[];nrows=None
    else:
        fields=[];nrows=None
    (out/name).write_bytes(data)
    return {"name":name,"file_id":item["id"],"source_advertised_bytes":size,
            "original_sha256":hashlib.sha256(data).hexdigest(),
            "rows":nrows,"columns":fields,
            "zip_members":zpaths if name.endswith(".zip") else None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    receipt={"status":"SOURCE_UNVERIFIED","dataset_doi":"10.5061/dryad.qv9s4mwp0",
             "source_api":DATASET_API,"year_scope":"published Jan 2025, field original 2020",
             "target_files":sorted(REQUIRED),"seal_spatial_density_estimated":False,
             "island_absence_estimated":False,"historical_mammal_predator_effect_identified":False}
    try:
        with requests.Session() as session:
            session.headers.update({"User-Agent":"mina-island-mammal-2020-source-audit/1.0"})
            meta,version,files=source_records(session)
            receipt["version_id"]=version
            receipt["api_file_entries"]=len(files)
            receipt["listed_files"]=[{k:x[k] for k in ("name","id","bytes")} for x in files]
            receipt["retrieved"]=[]
            for f in files:
                if f["name"] in REQUIRED:
                    got=save_resource(session,f,args.output)
                    receipt["retrieved"].append(got)
                    print("ORIGINAL_DRYAD_FILE_RECEIPT="+json.dumps(got),flush=True)
            if len(receipt["retrieved"])==len(REQUIRED):
                receipt["status"]="ORIGINAL_PUBLIC_FILES_RETRIEVED_SOURCE_METADATA_ONLY"
            else:raise ValueError("SOURCE_STOP partial public file retrieval")
    except Exception as e:
        receipt["status"]="SOURCE_ACCESS_HOLD"
        receipt["error"]=type(e).__name__+": "+str(e)[:400]
        print(receipt["error"],flush=True)
    finally:
        (args.output/"dryad_original_source_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
        print("PALMER_FURSEAL_DRYAD_SOURCE_RECEIPT="+json.dumps(receipt),flush=True)
    return 0 if receipt["status"].startswith("ORIGINAL_PUBLIC") else 2

if __name__=="__main__":raise SystemExit(main())
