"""Outcome-blind source/raster header audit for Freer et al. South Orkney krill fields.

Original NERC UK Polar Data Centre DOI 10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32.
Do not fit reproductive or climate coefficients. Never reinterpret model
predictions as independent observed acoustic krill measurements.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

SOURCE_DOI = "10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32"
EXPECTED = set(range(2011, 2021))


def classify(path):
    base=Path(path).name.lower()
    years=[int(y) for y in re.findall(r"(?<!\d)(20(?:1\d|20))(?!\d)",path)]
    yr=years[0] if len(set(years))==1 and years[0] in EXPECTED else None
    model=("combined" if "combined" in base else
           "binom" if "binom" in base else
           "gaus" if "gaus" in base else None)
    summary=("sd" if re.search(r"(?:^|[_\-.])(?:sd|std|stdev)(?:[_\-.]|$)",base)
             else "mean" if "mean" in base else None)
    return yr,model,summary


def audit_zip(source):
    import rasterio
    from rasterio.io import MemoryFile
    if not zipfile.is_zipfile(source):
        raise ValueError("RAMADDA source returned non-ZIP data; no raster inference allowed")
    tif=[]
    all_members=[]
    with zipfile.ZipFile(source) as z:
        for member in sorted(z.infolist(), key=lambda x:x.filename):
            if member.is_dir():
                continue
            all_members.append({"name":member.filename,"size":member.file_size})
            if not member.filename.lower().endswith((".tif",".tiff")):
                continue
            content=z.read(member.filename)
            with MemoryFile(content) as mf:
                with mf.open() as ds:
                    profile={
                        "path":member.filename,
                        "sha256":hashlib.sha256(content).hexdigest(),
                        "bytes":len(content),
                        "width":ds.width,"height":ds.height,
                        "count":ds.count,
                        "crs":ds.crs.to_string() if ds.crs else None,
                        "transform":list(ds.transform)[:6],
                        "bounds":[ds.bounds.left,ds.bounds.bottom,
                                  ds.bounds.right,ds.bounds.top],
                        "nodata":ds.nodata,
                        "dtypes":list(ds.dtypes),
                        "scales":list(ds.scales),
                        "offsets":list(ds.offsets),
                        "descriptions":list(ds.descriptions),
                    }
                    yr,model,summary=classify(member.filename)
                    profile.update(year=yr,component=model,statistic=summary)
                    tif.append(profile)
    year_files=[z for z in tif if z["year"] in EXPECTED]
    combined_means=[z for z in tif if z["component"]=="combined" and z["statistic"]=="mean" and z["year"] in EXPECTED]
    matches=Counter(z["year"] for z in combined_means)
    metadata={
        "status":"SOURCE_RASTER_HEADERS_OPENED_NO_BIOLOGICAL_OUTCOMES",
        "doi":SOURCE_DOI,
        "source_download":"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=4fd0a1bf-da1a-4021-82eb-2fc513910e32&output=zip.tree",
        "original_zip_sha256":hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        "original_zip_bytes":Path(source).stat().st_size,
        "zip_file_members":len(all_members),
        "tif_count":len(tif),
        "annual_tif_count":len(year_files),
        "combined_mean_counts_by_year":dict(sorted(matches.items())),
        "all_years_have_one_combined_mean":all(matches[y]==1 for y in EXPECTED),
        "raster_profiles":tif,
        "non_tif_members":[z for z in all_members if not z["name"].lower().endswith((".tif",".tiff"))],
        "model_interpretation":"Freer 2025 two-part presence/density GAM predictions conditioned on recorded acoustic data and year-specific environmental covariates; not independent observations.",
        "interpretation_limits":[
            "Salinity and summer ice were candidate input predictors in the published GAM; these rasters cannot independently validate their causal effect on krill.",
            "These source rasters share IMR acoustic data with 2011-2020 regional biomass estimates; they are not an independent second prey survey.",
            "Annual GAM fitting and spatial CV on 2011-2020 survey data is not chronological climate forecast validation.",
            "No nest, vegetation, salinity, fishing, predator or breeding outcome was accessed here."
        ]
    }
    return metadata


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    data=audit_zip(args.zip)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":data["status"],
        "zip_size":data["original_zip_bytes"],
        "tif":data["tif_count"],
        "annual_tif":data["annual_tif_count"],
        "combined_by_year":data["combined_mean_counts_by_year"],
        "profiles":[{k:x[k] for k in
            ("path","width","height","crs","bounds","year","component","statistic","nodata")}
            for x in data["raster_profiles"][:15]]
    },ensure_ascii=False))


if __name__=="__main__":
    main()
