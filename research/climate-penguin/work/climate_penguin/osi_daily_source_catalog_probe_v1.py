"""Bounded source-original OSI-450-a1 v3.1 daily SIC catalog and sample audit.

Historical daily SIC helps determine daily conditions at tagged Chinstrap GPS
locations. This is source discovery ONLY: no modelled prey, penguin dive,
ice navigability, breeding demographic association or forecast.
"""
from __future__ import annotations
import argparse,hashlib,json,re,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path

PUBLISHER="thredds.met.no"
ROOT="https://thredds.met.no/thredds/catalog/osisaf/met.no/reprocessed/ice/conc_450a1_files/catalog.xml"
DOI="10.15770/EUM_SAF_OSI_0023"
TARGETS=("20131215","20140115")
MAX_CATALOG_BYTES=4_000_000
MAX_NETCDF_BYTES=25_000_000
LIMIT_CATALOG=24

def fetch(url,maxsize=MAX_CATALOG_BYTES):
    u=urllib.parse.urlparse(url)
    if u.scheme!="https" or u.hostname!=PUBLISHER:
        raise ValueError("nonpublisher source URL forbidden")
    with urllib.request.urlopen(urllib.request.Request(url,headers={
        "User-Agent":"mina-osi450a1-daily-original-catalog-v1/1.0"}),timeout=45) as f:
        if urllib.parse.urlparse(f.geturl()).hostname!=PUBLISHER:
            raise ValueError("source redirect outside original publisher")
        raw=f.read(maxsize+1)
    if not raw or len(raw)>maxsize:
        raise ValueError("empty or excessive original source size")
    return raw

def catalog(raw,url):
    root=ET.fromstring(raw)
    if root.tag.split("}")[-1]!="catalog":
        raise ValueError("source is not THREDDS XML catalog")
    ref=[]
    datasets=[]
    for node in root.iter():
        name=node.tag.split("}")[-1]
        if name=="catalogRef":
            h=node.attrib.get("{http://www.w3.org/1999/xlink}href","")
            dest=urllib.parse.urljoin(url,h)
            if urllib.parse.urlparse(dest).hostname==PUBLISHER:
                ref.append({"title":node.attrib.get("name",""),"url":dest})
        if name=="dataset" and "urlPath" in node.attrib:
            p=node.attrib["urlPath"]
            if "osisaf/" in p and ("conc_450a1" in p or "ice_conc" in p):
                datasets.append({"name":node.attrib.get("name",""),"url_path":p})
    return ref,datasets

def pick_datasets(items):
    selected={}
    for target in TARGETS:
        hits=[r for r in items if ("ice_conc_sh_ease2-250" in r["url_path"] and
           "cdr-v3p1" in r["url_path"] and target in r["url_path"] and
           r["url_path"].endswith(".nc"))]
        if len(hits)==1:selected[target]=hits[0]
        elif len(hits)>1:raise ValueError("publisher has multiple same-day source files "+target)
    return selected

def run(out):
    queue=[ROOT]
    visited=set()
    records=[]
    datasets=[]
    while queue and len(visited)<LIMIT_CATALOG:
        url=queue.pop(0)
        if url in visited:continue
        visited.add(url)
        item={"url":url}
        try:
            raw=fetch(url)
            refs,files=catalog(raw,url)
            item.update(status="ORIGINAL_CATALOG_READ",sha256=hashlib.sha256(raw).hexdigest(),
                        bytes=len(raw),n_subcatalogs=len(refs),n_datasets=len(files),
                        sample_child_refs=refs[:14],
                        sample_source_files=files[:8])
            datasets.extend(files)
            # Follow only references containing requested source years/months;
            # don't enumerate decades or hundreds of daily files.
            wanted=[]
            for r in refs:
                z=(r["title"]+" "+r["url"]).lower()
                if any(t in z for t in ("daily","day","2013","2014","201312","201401")):
                    wanted.append(r["url"])
            queue=wanted+queue
        except Exception as e:
            item.update(status="SOURCE_ACCESS_HOLD",error=type(e).__name__+": "+str(e)[:350])
        records.append(item)
        found=pick_datasets(datasets)
        if len(found)==len(TARGETS):break
    samples=[]
    found=pick_datasets(datasets)
    for target,row in sorted(found.items()):
        source_url="https://thredds.met.no/thredds/fileServer/"+row["url_path"]
        output={"requested_date":target,"url":source_url}
        try:
            raw=fetch(source_url,MAX_NETCDF_BYTES)
            if not raw.startswith((b"CDF",b"\x89HDF")):
                raise ValueError("publisher daily file not NetCDF")
            path=out/(target+"_source.nc")
            path.write_bytes(raw)
            output.update(status="ORIGINAL_DAILY_NETCDF_BYTES_RETRIEVED",
                          sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),filename=path.name)
            try:
                import xarray as xr
                with xr.open_dataset(path,decode_times=False) as ds:
                    attrs=dict(ds.attrs)
                    output.update(global_attrs=attrs,
                      variables={v:{"dims":list(ds[v].dims),"shape":list(ds[v].shape),
                         "units":ds[v].attrs.get("units"),"dtype":str(ds[v].dtype)}
                         for v in ds.variables})
            except Exception as e:
                output.update(netCDF_open_error=type(e).__name__+":"+str(e)[:250])
        except Exception as e:
            output.update(status="ORIGINAL_DAILY_NETCDF_ACCESS_HOLD",
                          error=type(e).__name__+": "+str(e)[:350])
        samples.append(output)
    status=("SOURCE_DAILY_CATALOG_AND_BOTH_SAMPLES_RETRIEVED" if len(samples)==2 and
         all(r["status"]=="ORIGINAL_DAILY_NETCDF_BYTES_RETRIEVED" and
             r.get("global_attrs",{}).get("doi")==DOI for r in samples)
         else "SOURCE_DAILY_CATALOG_PARTIAL_OR_HOLD")
    result={"status":status,"publisher":PUBLISHER,"target_dates":TARGETS,
            "searched_original_catalogues":len(records),"catalogue_receipts":records,
            "original_source_dataset_examples":datasets[:12],
            "source_daily_samples":samples,
            "no_biological_effect_tested":True,
            "source_daily_not_route_passability":True}
    (out/"daily_source_discovery.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,
        default=str)+"\n",encoding="utf-8")
    print("DAILY_SOURCE_RECEIPT="+json.dumps({
        "status":status,"catalogs":len(records),
        "selected_original_paths":[x.get("url") for x in samples],
        "source_valid":[(x.get("requested_date"),x.get("status"),x.get("bytes")) for x in samples],
        "cat_roots":records[:4]},ensure_ascii=False),flush=True)
    return 0 if status=="SOURCE_DAILY_CATALOG_AND_BOTH_SAMPLES_RETRIEVED" else 2

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    raise SystemExit(run(args.out))
if __name__=="__main__":main()
