"""Source-format scan of BAS 2023 drone POLYGON shapefiles only.

Before reattempting V22 authentic bird point opening. Inspect only number
of nonempty/zero-coordinate source records and shapefile shape metadata,
not biological nest points or 2023 ecological occupancy/outcome.
"""
import argparse
import json
import struct
from pathlib import Path
import tempfile

import requests
import shapefile

from validate_zavodovski_2023_drone_nest_site_v22 import retrieve_2023, POLY_SOURCES


def inspect_polygon_shape_records(path):
    """Read SHP/SHX/DBF envelope metadata, NOT mapped vertices or bird rows."""
    raw=path.read_bytes()
    shx=path.with_suffix(".shx").read_bytes()
    dbf=path.with_suffix(".dbf").read_bytes()
    if len(raw)<100 or len(shx)<100 or len(dbf)<32:
        raise ValueError("SOURCE_STOP truncated original shapefile headers")
    for v in (raw,shx):
        if struct.unpack(">I",v[:4])[0]!=9994:
            raise ValueError("SOURCE_STOP invalid canonical shapefile magic")
    declared_shp=struct.unpack(">I",raw[24:28])[0]*2
    declared_shx=struct.unpack(">I",shx[24:28])[0]*2
    if declared_shp!=len(raw) or declared_shx!=len(shx):
        raise ValueError("SOURCE_STOP inconsistent SHP/SHX header length")
    global_type=struct.unpack("<I",raw[32:36])[0]
    index_records=(len(shx)-100)//8
    dbf_records=struct.unpack("<I",dbf[4:8])[0]
    if global_type!=5 or (len(shx)-100)%8:
        raise ValueError("SOURCE_STOP original 2023 polygon header not polygon")
    offset=100
    idx=0
    freq={}
    empty=0
    nonnull_zero=0
    zero_parts=0
    while offset<len(raw):
        if offset+12>len(raw):
            raise ValueError("SOURCE_STOP incomplete shape record")
        record_number, halfwords=struct.unpack(">II",raw[offset:offset+8])
        length=halfwords*2
        if record_number!=idx+1 or length<4 or offset+8+length>len(raw):
            raise ValueError("SOURCE_STOP original shape record offset/length corrupted")
        payload=raw[offset+8:offset+8+length]
        shape_type=struct.unpack("<I",payload[:4])[0]
        freq[str(shape_type)]=freq.get(str(shape_type),0)+1
        if shape_type==0:
            if len(payload)!=4:
                raise ValueError("SOURCE_STOP noncanonical null-shape content")
            empty+=1
        elif shape_type==5:
            if len(payload)<44:
                raise ValueError("SOURCE_STOP original polygon record too short")
            parts,npoints=struct.unpack("<ii",payload[36:44])
            if parts<0 or npoints<0:
                raise ValueError("SOURCE_STOP negative part/vertex count")
            if parts==0:
                zero_parts+=1
            if npoints==0:
                empty+=1
                nonnull_zero+=1
                if parts!=0:
                    raise ValueError("SOURCE_STOP empty coordinate array but positive part count")
            elif parts==0:
                raise ValueError("SOURCE_STOP nonempty coordinate array but no ring parts")
            required=44+4*parts+16*npoints
            if length<required:
                raise ValueError("SOURCE_STOP polygon content shorter than declared coordinate count")
        else:
            raise ValueError("SOURCE_STOP unexpected polygon-record type "+str(shape_type))
        idx+=1
        offset+=8+length
    if idx!=index_records or idx!=dbf_records:
        raise ValueError("SOURCE_STOP SHP SHX DBF record counts disagree")
    return {
        "source_shape_type":global_type,
        "original_record_count":idx,
        "original_shape_type_frequency":freq,
        "original_zero_vertex_record_count":empty,
        "original_nonnull_zero_vertex_record_count":nonnull_zero,
        "original_nonnull_zero_part_record_count":zero_parts,
        "original_nonempty_shape_records":idx-empty,
        "nest_point_rows_opened":0,
        "any_spatial_area_computed":False,
        "scan_method":"Binary SHP record headers: 2023 position coordinates NOT decoded"
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result={"status":"HOLD_SOURCE_AUDIT_ERROR","original_2023_nest_point_rows_opened":0}
    try:
        with tempfile.TemporaryDirectory(prefix="zav22a-") as tmp:
            with requests.Session() as session:
                paths,hashes=retrieve_2023(session,Path(tmp))
            data={key:inspect_polygon_shape_records(paths[key]) for key in POLY_SOURCES}
            result={
                "status":"SOURCE_POLYGON_RECORD_FORMAT_AUDITED_NO_BIRD_NEST_ROWS",
                "published_dataset_doi":"10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308",
                "sources":data,
                "source_file_sha256":{key:val for key,val in hashes.items()
                                      if key.rsplit(".",1)[0] in POLY_SOURCES},
                "original_2023_nest_point_rows_opened":0,
                "no_original_2023_nest_outcome_computed":True,
                "explanation":"This is only a source format check for empty/null geometry records. No shape is modified or omitted here."
            }
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:450]
    Path(a.out).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="source_file_sha256"}))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
