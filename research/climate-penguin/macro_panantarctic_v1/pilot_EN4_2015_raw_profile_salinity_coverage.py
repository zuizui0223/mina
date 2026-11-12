#!/usr/bin/env python3
"""Source provenance / true QC pilot for EN4.2.2 2015 Aug–Nov in-situ salinity.

The input is the original UK Met Office Hadley Centre raw monthly profile
observations, NOT EN4 objective analysis and NOT GLORYS reanalysis.
These instruments may themselves have been assimilated in GLORYS.
No raw observations or publisher source ZIP are redistributed.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import os
import re
import shutil
import tempfile
import time
import urllib.request
import zipfile
from collections import Counter, defaultdict, OrderedDict
from pathlib import Path
from statistics import mean

import netCDF4
import numpy as np
from pyproj import Geod
from scipy.spatial import cKDTree

YEAR=2015
MONTHS=(8,9,10,11)
BASE="https://hadleyserver.metoffice.gov.uk/hadobs/en4/data/en4-2-1/EN.4.2.2/"
YEAR_ZIP=f"EN.4.2.2.profiles.g10.{YEAR}.zip"
DIRECT_MONTHLY=tuple(f"EN.4.2.2.f.profiles.g10.{YEAR}{m:02d}.nc.gz" for m in MONTHS)
MAX_BYTES=600_000_000
MAX_AGE=12
MAX_COLONY_DIST_KM=(100.,250.)
QC_SURFACE_M=(10.,20.)
SALINITY_RANGE=(28.,38.)
SOURCE_DIMS=("LATITUDE","LONGITUDE","POSITION_QC","PROFILE_PSAL_QC",
             "PSAL_CORRECTED","PSAL_CORRECTED_QC","DEPH_CORRECTED")


def open_head(url):
    req=urllib.request.Request(url,method="HEAD",headers={"User-Agent":"Antarctic-source-noncommercial-research/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=45) as r:
            size=r.headers.get("Content-Length")
            return {"url":url,"status":int(r.status),"size_bytes":int(size) if size else None,
                    "content_type":r.headers.get("Content-Type"),"final_url":r.geturl()}
    except Exception as e:
        return {"url":url,"status":None,"error":str(e)[:250]}


class HTTPRangeZipReader(io.RawIOBase):
    """Seekable source ZIP using verified HTTP 206 blocks, not whole-year file.

    A central directory at ZIP end identifies original publisher monthly
    members. zipfile validates original per-member CRC on full decompression.
    A downloaded member also receives our own SHA256 source receipt. Do not
    falsely claim a SHA256 of the full 727 MB original archive.
    """
    def __init__(self,url,size,chunk_bytes=4*1024*1024,cache_blocks=6):
        super().__init__()
        self.url=url
        self.file_size=int(size)
        self.chunk_bytes=int(chunk_bytes)
        self.cache_blocks=int(cache_blocks)
        self.location=0
        self.cache=OrderedDict()
        self.http_range_requests=0
        self.bytes_transferred=0
        if self.file_size<=0 or self.chunk_bytes<=0:
            raise ValueError("Original EN4 remote ZIP source size unknown")

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.location

    def seek(self,offset,whence=io.SEEK_SET):
        if whence==io.SEEK_SET:
            new=int(offset)
        elif whence==io.SEEK_CUR:
            new=self.location+int(offset)
        elif whence==io.SEEK_END:
            new=self.file_size+int(offset)
        else:
            raise ValueError("Invalid original EN4 remote ZIP seek")
        if new<0:
            raise ValueError("Negative original EN4 ZIP byte seek")
        self.location=new
        return new

    def _fetch_block(self,index):
        start=index*self.chunk_bytes
        end=min(self.file_size-1,start+self.chunk_bytes-1)
        if end<start:
            return b""
        if self.bytes_transferred+(end-start+1)>MAX_BYTES:
            raise ValueError("Subset source original EN4 month byte-ranges exceed explicit 600MB transfer cap")
        req=urllib.request.Request(
            self.url,
            headers={
                "Range":f"bytes={start}-{end}",
                "User-Agent":"EN4-raw-profile-noncommercial-research-range-source/1.0"
            })
        error=None
        for trial in range(3):
            try:
                with urllib.request.urlopen(req,timeout=120) as response:
                    content_range=response.headers.get("Content-Range","")
                    required=f"bytes {start}-{end}/{self.file_size}"
                    if response.status!=206 or content_range!=required:
                        raise ValueError("Original publisher HTTP partial source not 206 exact byte range: "+
                                         repr((response.status,content_range,required)))
                    data=response.read()
                if len(data)!=end-start+1:
                    raise ValueError("Original EN4 source ranged response returned incomplete bytes")
                self.bytes_transferred+=len(data)
                self.http_range_requests+=1
                return data
            except Exception as exc:
                error=exc
                if trial<2:time.sleep(2**trial)
        raise RuntimeError("Original EN4 ZIP byte-range source unavailable") from error

    def _get_block(self,index):
        if index not in self.cache:
            self.cache[index]=self._fetch_block(index)
            while len(self.cache)>self.cache_blocks:
                self.cache.popitem(last=False)
        self.cache.move_to_end(index)
        return self.cache[index]

    def read(self,size=-1):
        if size is None or size<0:size=self.file_size-self.location
        if size==0 or self.location>=self.file_size:
            return b""
        n=min(size,self.file_size-self.location)
        result=[]
        while n>0:
            k=self.location//self.chunk_bytes
            start_in_block=self.location%self.chunk_bytes
            block=self._get_block(k)
            piece=block[start_in_block:start_in_block+n]
            if not piece:raise IOError("Remote original source ZIP returned empty data before EOF")
            result.append(piece)
            self.location+=len(piece)
            n-=len(piece)
        return b"".join(result)


def fetch(url,destination):
    digest=hashlib.sha256()
    total=0
    req=urllib.request.Request(url,headers={"User-Agent":"Antarctic-source-noncommercial-research/1.0"})
    with urllib.request.urlopen(req,timeout=120) as response, destination.open("wb") as out:
        if response.status!=200:
            raise ValueError(f"EN4 publisher HTTP status not success {response.status}")
        while True:
            chunk=response.read(2**20)
            if not chunk:break
            total+=len(chunk)
            if total>MAX_BYTES:
                raise ValueError("EN4 source response exceeds 600 MB size cap; need a per-month subset")
            digest.update(chunk);out.write(chunk)
    return {"original_url":url,"sha256":digest.hexdigest(),"bytes":total}


def letter(value):
    """Decode EN4 NetCDF 0-D masked char arrays to literal QC 1/4.

    netCDF4 returns a 0-D MaskedArray, whose str() is 'b\'1\''.
    That representation is NOT the QC '1' and previously rejected every
    observed position. Convert via ndarray.item() before source QC filtering.
    """
    if isinstance(value,np.ma.core.MaskedConstant) or np.ma.is_masked(value):
        return ""
    arr=np.asarray(value)
    if arr.size==0:return ""
    value=arr.flat[0]
    if isinstance(value,(np.generic,)):
        value=value.item()
    if isinstance(value,(bytes,np.bytes_)):
        return value.decode("utf-8",errors="ignore").strip("\x00 ")
    return str(value).strip("\x00 ")


def xyz(latitudes,longitudes):
    a=np.deg2rad(np.asarray(latitudes,dtype=float))
    b=np.deg2rad(np.asarray(longitudes,dtype=float))
    return np.stack((np.cos(a)*np.cos(b),np.cos(a)*np.sin(b),np.sin(a)),axis=-1)


def accepted_sites(path):
    import csv
    with path.open(encoding="utf-8",newline="") as src:
        rows=list(csv.DictReader(src))
    if len(rows)!=595 or len({r["site_id"] for r in rows})!=595:
        raise ValueError("Previous source 595 original colony geography no longer matches")
    eligible=[r for r in rows if r["source_wet_2011_september_25km_gate"].lower()=="true"]
    if len(eligible)!=588:
        raise ValueError("Existing source 588 GLORYS-wet colony acceptance changed")
    return eligible


def coordinates_nearest_to_original_colonies(sites,lat,lon):
    # First pick spherical candidate nearest source colonies; final pair
    # distances are WGS84 geodesics, never planar Antarctic distances.
    lat=np.asarray(lat,dtype=float);lon=np.asarray(lon,dtype=float)
    valid=np.where(np.isfinite(lat)&np.isfinite(lon)&(lat<=-55)&(lat>=-90))[0]
    out={}
    if not len(valid):return out
    source_lat=np.asarray([float(r["colony_latitude"]) for r in sites])
    source_lon=np.asarray([float(r["colony_longitude"]) for r in sites])
    tree=cKDTree(xyz(source_lat,source_lon))
    k=min(8,len(sites))
    _,knn=tree.query(xyz(lat[valid],lon[valid]),k=k)
    if k==1:
        knn=np.asarray(knn).reshape(-1,1)
    geod=Geod(ellps="WGS84")
    for i,neighbors in zip(valid,np.atleast_2d(knn)):
        j=np.asarray(neighbors,dtype=int)
        _,_,meters=geod.inv(
            np.full(len(j),float(lon[i])),
            np.full(len(j),float(lat[i])),
            source_lon[j],source_lat[j]
        )
        jj=int(j[np.argmin(meters)])
        dist=float(np.min(meters)/1000.)
        if dist<=250:
            out[int(i)]=(sites[jj],dist)
    return out


def sample_month_nc(raw,year,month,sites):
    with netCDF4.Dataset("en4_original_memory",memory=raw) as ds:
        dims={k:int(len(v)) for k,v in ds.dimensions.items()}
        variables={k:{"shape":list(ds.variables[k].shape),
                     "dimensions":list(ds.variables[k].dimensions)}
                   for k in SOURCE_DIMS if k in ds.variables}
        if len(variables)!=len(SOURCE_DIMS):
            return {
                "source_status":"EN4_PROFILE_SCHEMA_INCOMPLETE",
                "year":year,"month":month,"source_dims":dims,"source_vars":variables,
                "missing":[v for v in SOURCE_DIMS if v not in ds.variables]
            },[]
        latitude=np.asarray(np.ma.filled(ds.variables["LATITUDE"][:],np.nan),dtype=float).reshape(-1)
        longitude=np.asarray(np.ma.filled(ds.variables["LONGITUDE"][:],np.nan),dtype=float).reshape(-1)
        if len(latitude)!=len(longitude):
            raise ValueError("EN4 profile latitude-longitude source identities differ")
        source_nearest=coordinates_nearest_to_original_colonies(sites,latitude,longitude)
        if not source_nearest:
            return {
                "source_status":"EN4_MONTHLY_NO_PROFILES_WITHIN_250KM_ORIGINAL_COLONY",
                "year":year,"month":month,"source_dims":dims,"source_vars":variables,
                "n_global_EN4_profiles":len(latitude),"n_geolocated_near_source":0
            },[]
        qualified=[]
        counts=Counter()
        for pidx,(site,distance_km) in source_nearest.items():
            counts["geolocated_within_250km"]+=1
            position_flag=letter(ds.variables["POSITION_QC"][pidx])
            salinity_profile_flag=letter(ds.variables["PROFILE_PSAL_QC"][pidx])
            counts["position_QC_flag_"+str(position_flag)]+=1
            counts["salinity_profile_QC_flag_"+str(salinity_profile_flag)]+=1
            if position_flag!="1":
                counts["rejected_position_QC"]+=1;continue
            if salinity_profile_flag!="1":
                counts["rejected_profile_salinity_QC"]+=1;continue
            depths=np.asarray(np.ma.filled(ds.variables["DEPH_CORRECTED"][pidx,:],np.nan),dtype=float).reshape(-1)
            salinities=np.asarray(np.ma.filled(ds.variables["PSAL_CORRECTED"][pidx,:],np.nan),dtype=float).reshape(-1)
            qcs=np.asarray(ds.variables["PSAL_CORRECTED_QC"][pidx,:]).reshape(-1)
            if len(depths)!=len(salinities) or len(qcs)!=len(depths):
                raise ValueError("EN4 salinity source profile level mismatched")
            qaccept=np.fromiter((letter(v)=="1" for v in qcs),
                                 count=len(qcs),dtype=bool)
            ok=qaccept&np.isfinite(depths)&np.isfinite(salinities)&\
                (depths>=0)&(salinities>=SALINITY_RANGE[0])&\
                (salinities<=SALINITY_RANGE[1])
            for depthmax in QC_SURFACE_M:
                selected=np.where(ok&(depths<=depthmax))[0]
                if not len(selected):
                    counts[f"no_qualified_{int(depthmax)}m_depth"]+=1
                    continue
                ix=int(selected[np.argmin(depths[selected])])
                countkey=f"accepted_shallowest_{int(depthmax)}m"
                counts[countkey]+=1
                qualified.append({
                    "year":year,"month":month,"region":site["source_region"],
                    "source_250km_block":site["source_250km_block"],
                    "nearest_colony_site_id":site["site_id"],
                    "distance_km":distance_km,
                    "source_depth_gate_m":depthmax,
                    "source_shallowest_qualified_depth_m":float(depths[ix]),
                    # Do not archive individual raw profile salinity or
                    # exact observation position in public research outputs.
                    "source_profile_QC_is_1_at_location_profile_and_level":True,
                })
        return {
            "source_status":"EN4_MONTHLY_RAW_PROFILE_QC_SPATIAL_GATE_COMPUTED",
            "year":year,"month":month,
            "source_dims":dims,"source_vars":variables,
            "n_global_EN4_profiles":len(latitude),
            "source_spatial_geo_250km_match":len(source_nearest),
            "source_EN4_QC_counts":dict(counts),
        },qualified


def run(args):
    sites=accepted_sites(args.geography)
    candidates=[open_head(BASE+fn) for fn in DIRECT_MONTHLY]
    zipmeta=open_head(BASE+YEAR_ZIP)
    print("EN4_ORIGINAL_SOURCE_HEAD="+json.dumps({
        "year":YEAR,"four_direct_months":candidates,"official_year_zip":zipmeta
    },ensure_ascii=False),flush=True)
    mode=("MONTHLY_NC_GZ" if all(c["status"]==200 for c in candidates)
          else "REMOTE_OFFICIAL_ZIP_HTTP_206" if zipmeta["status"]==200
          else "NO_OFFICIAL_EN4_SOURCE_AVAILABLE")
    if mode=="NO_OFFICIAL_EN4_SOURCE_AVAILABLE":
        raise RuntimeError("Neither official EN4 finalized monthly URLs nor the official 2015 ZIP are fetchable")
    args.out.mkdir(parents=True,exist_ok=True)
    source_receipts=[];results=[];qualified=[]
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        if mode=="MONTHLY_NC_GZ":
            for month,fn in zip(MONTHS,DIRECT_MONTHLY):
                destination=root/fn
                receipt=fetch(BASE+fn,destination)
                src=gzip.decompress(destination.read_bytes())
                data,keep=sample_month_nc(src,YEAR,month,sites)
                results.append(data);qualified.extend(keep)
                source_receipts.append({**receipt,"monthly_YYYYMM":f"{YEAR}{month:02d}",
                                        "unzipped_month_netCDF_sha256":hashlib.sha256(src).hexdigest()})
                destination.unlink()
                print("EN4_QC_RAW_MONTH="+json.dumps(data,ensure_ascii=False),flush=True)
        else:
            remote=HTTPRangeZipReader(BASE+YEAR_ZIP,zipmeta["size_bytes"])
            source_receipts.append({
                "official_year_ZIP_url":BASE+YEAR_ZIP,
                "official_year_ZIP_total_bytes":zipmeta["size_bytes"],
                "HTTP_206_byte_range_verified_before_use":True,
                "annual_archive_full_SHA256_NOT_COMPUTED":True,
                "original_members_verified_using_official_ZIP_CRC32_and_monthly_SHA256":True
            })
            with zipfile.ZipFile(remote) as z:
                members=z.namelist()
                for month in MONTHS:
                    pattern=re.compile(fr"\.{YEAR}{month:02d}\.nc$",re.I)
                    chosen=[name for name in members if pattern.search(name)]
                    if len(chosen)!=1:
                        raise ValueError(f"Official EN4 2015 ZIP missing unique source month {month}: "+
                                         repr(members[:24]))
                    filename=chosen[0]
                    member=z.getinfo(filename)
                    # zipfile internally validates original CRC32 on reading.
                    src=z.read(filename)
                    data,keep=sample_month_nc(src,YEAR,month,sites)
                    results.append(data);qualified.extend(keep)
                    source_receipts.append({
                        "year":YEAR,"month":month,
                        "source_zip_member":filename,
                        "original_publisher_zip_member_CRC32":f"{member.CRC:08x}",
                        "original_publisher_zip_member_compressed_bytes":member.compress_size,
                        "original_publisher_zip_member_uncompressed_bytes":member.file_size,
                        "uncompressed_original_month_netCDF_sha256":hashlib.sha256(src).hexdigest(),
                        "uncompressed_original_month_bytes":len(src),
                        "source_CRC32_checked_by_zipfile_on_complete_decompression":True
                    })
                    print("EN4_QC_RAW_MONTH="+json.dumps(data,ensure_ascii=False),flush=True)
            source_receipts.append({
                "total_original_http206_range_requests":remote.http_range_requests,
                "total_original_http206_source_bytes_transferred":remote.bytes_transferred,
                "whole_727MB_publisher_archive_was_not_downloaded":True
            })
    support={}
    coverage={}
    for depth in QC_SURFACE_M:
        depthrows=[r for r in qualified if r["source_depth_gate_m"]==depth]
        for radius in MAX_COLONY_DIST_KM:
            relevant=[r for r in depthrows if r["distance_km"]<=radius]
            group=defaultdict(list)
            for r in relevant:group[r["region"]].append(r)
            key=f"depth_le_{int(depth)}m_dist_le_{int(radius)}km"
            coverage[key]={
                "n_raw_qualified_profile_instances":len(relevant),
                "n_distinct_original_regions_with_any_EN4_shallow_profiles":len(group),
                "n_regions_with_3plus_original_profiles":sum(len(v)>=3 for v in group.values()),
                "n_distinct_original_colony_sites_represented":len({r["nearest_colony_site_id"] for r in relevant}),
                "source_region_profile_counts":{k:len(v) for k,v in sorted(group.items())},
                "original_four_months_profile_counts":dict(sorted(Counter(r["month"] for r in relevant).items())),
                "n_regions_with_all_four_original_months_at_least_one_profile":
                    sum(len({r["month"] for r in v})==4 for v in group.values()),
                "n_original_region_month_cells_with_3plus_profiles":
                    sum(n>=3 for n in Counter((r["region"],r["month"]) for r in relevant).values())
            }
    original_regions=sorted({r["source_region"] for r in sites})
    if len(original_regions)!=18:raise ValueError("Original 18 geography regions changed")
    receipt={
        "source_status":"EN4_REAL_ORIGINAL_QC_2015_PROFILE_COVERAGE_PILOT_COMPLETE",
        "year":YEAR,"months":list(MONTHS),"source_method":mode,
        "source_product":"EN4.2.2 g10 raw quality-controlled in-situ profiles",
        "source_publisher":"UK Met Office Hadley Centre",
        "source_original_breeding_site_count":595,
        "source_marine_eligible_site_count":len(sites),
        "source_original_regions_eligible":original_regions,
        "source_original_2015_product_url":BASE+YEAR_ZIP,
        "source_download_source_sha256_receipts":source_receipts,
        "original_month_source_QC_and_schema":results,
        "source_depth_and_geodesic_coverages":coverage,
        "does_not_redistribute_original_EN4_raw_profiles":True,
        "does_not_verify_independent_of_GLORYS_data_assimilation":True,
        "source_profile_record_is_not_an_independent_climate_year_region":True,
        "no_1993_2020_18region_salinity_synchrony_inferred_from_2015_only":True,
    }
    (args.out/"en4_2015_aug_nov_raw_profile_coverage_and_SHA256.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EN4_RAW_2015_COVERAGE="+json.dumps(coverage,ensure_ascii=False),flush=True)
    print("EN4_RAW_2015_SOURCE_RECEIPT="+json.dumps({
        "product":receipt["source_product"],"method":mode,
        "original_regions":len(original_regions),
        "downloaded_sources":len(source_receipts)},ensure_ascii=False),flush=True)
    return receipt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--geography",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    run(ap.parse_args())


if __name__=="__main__":
    main()
