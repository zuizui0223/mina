"""Source-only original BAS 2025 spatial krill 2011-2020 raster archive gate.

Do not compute penguin associations, select rasters by an outcome, or convert
published model predictions to measured acoustic krill observations at this
stage. Verify downloadable original raster identity, time layers, geographic
resolution, no-data, and source archive digest.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

DOI="10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32"
BAS_ENTRY="4fd0a1bf-da1a-4021-82eb-2fc513910e32"
EXPECTED_YEARS=tuple(range(2011,2021))
def audit(path):
    if not zipfile.is_zipfile(path):
        raise ValueError("publisher source is not a native ZIP; no derived results licensed")
    z=zipfile.ZipFile(path)
    entries=[]
    for info in sorted(z.infolist(),key=lambda x:x.filename):
        if info.is_dir():
            continue
        name=info.filename
        is_tif=name.lower().endswith((".tif",".tiff"))
        year_match=re.search(r"(?<!\d)(201[1-9]|2020)(?!\d)",Path(name).name)
        year=int(year_match.group(1)) if year_match else None
        entries.append({"name":name,"bytes":info.file_size,
                        "compressed_bytes":info.compress_size,
                        "is_raster":is_tif,
                        "year_in_path":year})
    rasters=[x for x in entries if x["is_raster"]]
    annual=[x for x in rasters if x["year_in_path"] in EXPECTED_YEARS]
    decades=[x for x in rasters if x["year_in_path"] not in EXPECTED_YEARS]
    if len(rasters)<10 or not annual:
        raise ValueError("fewer rasters than advertised; check parent source tree")
    present=sorted({e["year_in_path"] for e in annual})
    if present!=list(EXPECTED_YEARS):
        raise ValueError(f"published annual prediction years do not span 2011-2020: {present}; examples={[(v['name'],v['year_in_path']) for v in rasters[:12]]}")
    sample={}
    # Raster schema; source-only no biologically selected positive outcome.
    import rasterio
    from rasterio.io import MemoryFile
    for entry in rasters:
        data=z.read(entry["name"])
        with MemoryFile(data) as mem:
            with mem.open() as ds:
                if ds.count!=1 or ds.crs is None:
                    raise ValueError("bad TIFF raster component count/CRS: "+entry["name"])
                a={
                    "crs":str(ds.crs),"width":ds.width,"height":ds.height,
                    "dtype":str(ds.dtypes[0]),"nodata":ds.nodata,
                    "resolution_x":float(ds.res[0]),"resolution_y":float(ds.res[1]),
                    "bounds":[float(ds.bounds.left),float(ds.bounds.bottom),
                              float(ds.bounds.right),float(ds.bounds.top)]
                }
                sample[entry["name"]]=a
    crss=sorted({x["crs"] for x in sample.values()})
    if len(crss)!=1:
        raise ValueError(f"no common raster CRS across annual products: {crss}")
    return {
        "status":"BAS_ORIGINAL_SPATIAL_KRILL_RASTER_SCHEMA_AUDITED_ONLY",
        "dataset_doi":DOI,"original_entry":BAS_ENTRY,
        "license":"UK Open Government Licence v3; check publisher version",
        "source_zip_sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "original_zip_bytes":Path(path).stat().st_size,
        "file_count":len(entries),"raster_count":len(rasters),
        "annual_raster_count":len(annual),"decade_raster_count":len(decades),
        "complete_source_years":present,
        "CRS_values":crss,
        "file_manifest":entries,
        "raster_geometry":sample,
        "no_predictive_or_biological_outcome_estimated":True,
        "notes":[
            "Raster values are Freer et al 2025 hurdle-model predictions, not new raw acoustic measurements.",
            "This prior model uses sea ice, salinity and other covariates, so future climate correlations are not independent",
            "Acoustic input was collected in South Orkney broader regional transects; suitability to Signy foraging needs geospatial validation",
            "Annual rasters represent January-February survey-time conditions, not October-February complete breeding conditions"
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    args=p.parse_args()
    result=audit(args.source_zip)
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],
        "total_rasters":result["raster_count"],
        "annual":result["annual_raster_count"],
        "decade":result["decade_raster_count"],
        "CRS":result["CRS_values"],
        "raster_names":[x["name"] for x in result["file_manifest"] if x["is_raster"]][:80],
        "digest":result["source_zip_sha256"]},ensure_ascii=False))

if __name__=="__main__":
    main()
