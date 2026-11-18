"""Fixed, source-verified Signy proximity summary of Freer et al. (2025) krill GAM rasters.

Published *model predictions*, not raw acoustic krill abundance. Inputs to the
model already include salinity and sea ice; never treat as an independent
verification of either. All 3 species share the same single-island annual field.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,zipfile
from pathlib import Path
import numpy as np
from rasterio.io import MemoryFile

ROOT=Path(__file__).resolve().parents[4]
GPS=ROOT/"research/climate-penguin/outputs/spatial_feasibility/signy_gps_crosswalk.csv"
IMR=ROOT/"research/climate-penguin/inputs/imr_south_orkney_krill_2011_2020_2024_table2.csv"
EXPECTED_MODEL_PAYLOAD_SHA="f4fffbc2b0cbe2dffc5a5728c81f1b46ba9ff99988c6589bb3515d38d2a2fead"
PRODUCTS={"combined":"predict_combined_mean","occurrence":"gam_binom_mean","positive_density":"gam_gaus_mean_exp"}
BANDS=((0,50),(50,100),(100,150))
SPECIES=("Adelie","Chinstrap","Gentoo")
YEARS=tuple(range(2011,2021))

def readcsv(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def anchor():
    gps=readcsv(GPS)
    if len(gps)!=14 or {r["species"] for r in gps}!={"Adelie","Chinstrap"}:
        raise ValueError("BAS Signy native GPS roster drift")
    if any("reference point" not in r["geometry"] for r in gps):
        raise ValueError("BAS reference-point interpretation drift")
    lat=[float(r["latitude"]) for r in gps]
    lon=[float(r["longitude"]) for r in gps]
    return {"lat":(min(lat)+max(lat))/2,"lon":(min(lon)+max(lon))/2,
            "source":"midpoint_of_bbox_of_14_BAS_colony_reference_points_NOT_foraging_site_or_Gentoo_nest"}

def distance_km(lat0,lon0,lats,lons):
    rad=np.deg2rad
    a=np.sin((rad(lats)-rad(lat0))/2)**2+np.cos(rad(lat0))*np.cos(rad(lats))*np.sin((rad(lons)-rad(lon0))/2)**2
    return 2*6371.0088*np.arcsin(np.sqrt(np.clip(a,0,1)))

def extract(zip_path):
    p=Path(zip_path)
    if not zipfile.is_zipfile(p):
        raise ValueError("not official GeoTIFF ZIP")
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    # Regenerated ZIP wrapper hash varies; pin the 30 native original TIFF payloads.
    z=zipfile.ZipFile(p)
    content_sha=hashlib.sha256()
    files=z.namelist()
    ref=anchor()
    common_transform=None
    geo_masks=None
    rows=[]
    for y in YEARS:
        for kind,source_kind in PRODUCTS.items():
            base=f"{y}_{source_kind}.tif"
            matches=[n for n in files if n.endswith("/annual_krill_rasters/"+base)]
            if len(matches)!=1:
                raise ValueError("required original publisher model output unavailable: "+base)
            raw_tiff=z.read(matches[0])
            content_sha.update(base.encode("utf-8")+b"\0")
            content_sha.update(raw_tiff)
            with MemoryFile(raw_tiff) as mem:
                with mem.open() as ds:
                    if str(ds.crs)!="EPSG:4326" or ds.count!=1:
                        raise ValueError("raster CRS/grain incompatible")
                    trans=ds.transform
                    shape=ds.shape
                    data=np.ma.filled(ds.read(1,masked=True),np.nan)
            if common_transform is None:
                common_transform=trans
                grid_shape=shape
                r,c=np.indices(grid_shape)
                lat=trans.f+(r+0.5)*trans.e
                lon=trans.c+(c+0.5)*trans.a
                dd=distance_km(ref["lat"],ref["lon"],lat,lon)
                geo_masks={(lo,hi):(dd>=lo)&(dd<hi) for lo,hi in BANDS}
                area=np.cos(np.deg2rad(lat))
            elif trans!=common_transform or shape!=grid_shape:
                raise ValueError("original model surfaces lack matching native grid")
            valid=np.isfinite(data)
            if np.any(data[valid]<0):
                raise ValueError("negative predicted density or occurrence value")
            if kind=="occurrence" and np.any(data[valid]>1.000001):
                raise ValueError("probability above 1")
            for lo,hi in BANDS:
                region=geo_masks[lo,hi]
                use=region&valid
                n=int(use.sum())
                total=int(region.sum())
                if n<20 or n/max(total,1)<0.20:
                    raise ValueError(f"Too few modelled cells in band {lo}-{hi} km for {y}: {n}/{total}")
                value=float(np.average(data[use],weights=area[use]))
                rows.append({"survey_year":y,"product":kind,"distance_band_km":f"{lo}-{hi}",
                             "predicted_area_weighted_mean":value,
                             "n_valid_model_cells":n,"n_candidate_cells":total,
                             "model_valid_fraction":n/total})
    if content_sha.hexdigest()!=EXPECTED_MODEL_PAYLOAD_SHA:
        raise ValueError("published native raster data changed: "+content_sha.hexdigest())
    if len(rows)!=90:
        raise ValueError("annual × product × band table not complete")
    return rows,ref,{"zip_repack_sha256":digest,"native_selected_raster_bytes_sha256":content_sha.hexdigest()},{"grid_crs":"EPSG:4326","grid_shape":list(grid_shape),"grid_resolution_deg":abs(float(common_transform.a))}

def corr(x,y):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if len(x)<3 or np.std(x)<1e-12 or np.std(y)<1e-12:
        return None
    return float(np.corrcoef(x,y)[0,1])

def analyze(annual,stage_dir):
    outcome={}
    for r in readcsv(Path(stage_dir)/"species_annual_stage_summary.csv"):
        yr=int(r["season_start"])
        if r["species"] in SPECIES and yr in range(2011,2020):
            key=(r["species"],yr)
            if key in outcome:
                raise ValueError("duplicate BAS original annual response")
            outcome[key]=float(r["median_recorded_fledglings_per_pair"])
    if len(outcome)!=27:
        raise ValueError("original 3-species native stage window changed")
    source=readcsv(IMR)
    full={int(r["survey_calendar_year"]):r["survey_coverage"]=="full" for r in source}
    if len(full)!=10:
        raise ValueError("IMR source year count changed")
    features={(r["survey_year"],r["product"],r["distance_band_km"]):r["predicted_area_weighted_mean"] for r in annual}
    if len(features)!=len(annual):
        raise ValueError("duplicate source model feature")
    comparisons={}
    for kind in PRODUCTS:
        comparisons[kind]={}
        for lo,hi in BANDS:
            band=f"{lo}-{hi}"
            comparisons[kind][band]={}
            for label in ("all","complete","complete_minus_2012"):
                years=list(range(2011,2020))
                if label!="all":years=[y for y in years if full[y]]
                if label=="complete_minus_2012":years=[y for y in years if y!=2012]
                xx=[features[y,kind,band] for y in years]
                results={}
                for sp in SPECIES:
                    yy=[outcome[sp,y] for y in years]
                    result=corr(xx,yy)
                    loo=[corr(xx[:i]+xx[i+1:],yy[:i]+yy[i+1:]) for i in range(len(xx))]
                    results[sp]={"r":result,"leave_one_year_out":[min(loo),max(loo)]}
                comparisons[kind][band][label]={"years":years,"n":len(years),"species":results}
    return comparisons

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-zip",required=True,type=Path)
    parser.add_argument("--stage-dir",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    opt=parser.parse_args()
    rows,anchor_data,source_provenance,grid=extract(opt.source_zip)
    relationships=analyze(rows,opt.stage_dir)
    opt.out.mkdir(parents=True,exist_ok=True)
    with (opt.out/"annual_spatial_bands.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]))
        wr.writeheader();wr.writerows(rows)
    receipt={
        "status":"EXPLORATORY_PUBLISHED_GAM_SPATIAL_PREY_PROXY_NOT_INDEPENDENT_OBSERVATION",
        "BAS_DOI":"10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32",
        "publisher_raster_content":source_provenance,
        "anchor":anchor_data,"native_grid":grid,
        "fixed_distance_bands_km":[list(z) for z in BANDS],
        "n_modelled_environmental_years":10,
        "n_breeding_years":9,
        "annual_record_count":len(rows),
        "associations":relationships,
        "limits":[
            "Freer et al 2025 GAM predictions incorporate krill acoustic evidence, salinity and sea ice; no independent climate-effect test is implied.",
            "Original IMR Table 2 region-wide acoustic observations are inputs for the raster model; not independent data replications.",
            "All three species share the same single-island nine-year ocean model; no 27 independent environmental observations.",
            "Signy anchor is derived from BAS original colony reference GPS, not a verified species-specific foraging or landing location.",
            "Source TIFF masks are not independently verified water-only polygon masks.",
            "Distance bands are geographic proximity sensitivities, not measured penguin foraging distances.",
            "2013 and 2015 field acoustic coverage incomplete even though GAM supplies annual predicted maps.",
            "January-February model year t precedes breeding season starting around October t; subsequent rearing conditions may differ.",
            "No stage-specific survival, colonization, vegetation or 2050-2100 nesting projection parameter identified."
        ]}
    (opt.out/"result.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":receipt["status"],"anchor":anchor_data,
                      "grid":grid,"annual_rows":len(rows),
                      "combined":relationships["combined"],
                      "first_modelled_year":[r for r in rows if r["survey_year"]==2011]},ensure_ascii=False))

if __name__=="__main__":main()
