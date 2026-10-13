"""Source-format scan of BAS 2023 drone POLYGON shapefiles only.

Before reattempting V22 authentic bird point opening. Inspect only number
of nonempty/zero-coordinate source records and shapefile shape metadata,
not biological nest points or 2023 ecological occupancy/outcome.
"""
import argparse
import json
from pathlib import Path
import tempfile

import requests
import shapefile

from validate_zavodovski_2023_drone_nest_site_v22 import retrieve_2023, POLY_SOURCES


def inspect_polygon_shape_records(path):
    reader=shapefile.Reader(str(path))
    counts={}
    empties=0
    zero_parts=0
    vertexless_nonnull=0
    for record in reader.iterShapes():
        shape_id=int(record.shapeType)
        counts[str(shape_id)]=counts.get(str(shape_id),0)+1
        verts=record.points
        if not verts:
            empties+=1
            if shape_id != shapefile.NULL:
                vertexless_nonnull += 1
        if shape_id != shapefile.NULL and not getattr(record,"parts",[]):
            zero_parts += 1
    if reader.numRecords != sum(counts.values()):
        raise ValueError("SOURCE_STOP shape count differs from DBF header count")
    return {
        "source_shape_type":int(reader.shapeType),
        "original_record_count":reader.numRecords,
        "original_shape_type_frequency":counts,
        "original_zero_vertex_record_count":empties,
        "original_nonnull_zero_vertex_record_count":vertexless_nonnull,
        "original_nonnull_zero_part_record_count":zero_parts,
        "original_nonempty_shape_records":reader.numRecords-empties,
        "nest_point_rows_opened":0,
        "any_spatial_area_computed":False
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
