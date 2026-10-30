"""Extract spatially explicit *modelled* South Orkney krill exposure at Signy.

Freer et al. 2025 BAS DOI:10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32.
These are krill hurdle-GAM predictions trained on the SAME IMR acoustic surveys
as the previously imported annual regional biomass estimates. Ice/salinity
entered the GAM; rasters are not independent krill or climate measurements.
Fixed 25/50/100-km geographic buffer sensitivity, NOT observed penguin routes.
Python numpy+rasterio. Needs original BAS source ZIP and original BAS stage CSVs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import zipfile
from pathlib import Path

import numpy as np
from rasterio.io import MemoryFile

ROOT=Path(__file__).resolve().parents[4]
GPS=ROOT/"research/climate-penguin/outputs/spatial_feasibility/signy_gps_crosswalk.csv"
REGIONAL=ROOT/"research/climate-penguin/inputs/imr_south_orkney_krill_2011_2020_2024_table2.csv"
PINS=ROOT/"research/climate-penguin/inputs/freer_krill_combined_raster_sha_v1.json"
RADIUS=(25,50,100)
YEARS=tuple(range(2011,2021))
SPECIES=("Adelie","Chinstrap","Gentoo")
ORIGINAL_DOI="10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32"
COMPONENTS={
 "prob":"gam_binom_mean.tif",
 "density_positive":"gam_gaus_mean_exp.tif",
 "combined":"predict_combined_mean.tif"
}

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def gps_anchor(source=GPS):
    r=read_csv(source)
    if len(r)!=14 or sorted({x["species"] for x in r})!=["Adelie","Chinstrap"]:
        raise ValueError("Signy source colony point roster changed")
    if len({(x["species"],x["colony"]) for x in r})!=14:
        raise ValueError("duplicated original colony reference")
    lat=[float(z["latitude"]) for z in r]
    lon=[float(z["longitude"]) for z in r]
    if any(not(-61<x<-60) for x in lat) or any(not(-46<x<-45) for x in lon):
        raise ValueError("Signy referenced coordinates unexpectedly moved")
    return ((min(lat)+max(lat))/2,(min(lon)+max(lon))/2)

def great_circle(lat,lon,lat0,lon0):
    y=np.deg2rad(lat)
    y0=math.radians(lat0)
    dy=y-y0
    dl=np.deg2rad(lon-lon0)
    h=np.sin(dy/2)**2+np.cos(y)*math.cos(y0)*np.sin(dl/2)**2
    return 2*6371.0088*np.arcsin(np.sqrt(np.clip(h,0,1)))

def raster_fields(source):
    expected=json.loads(PINS.read_text(encoding="utf-8"))
    if len(expected)!=10 or set(expected)!={f"{y}_predict_combined_mean.tif" for y in YEARS}:
        raise ValueError("source pin roster drift")
    if not zipfile.is_zipfile(source):
        raise ValueError("original BAS source archive is not a ZIP")
    found={}
    audit=[]
    with zipfile.ZipFile(source) as z:
        names=z.namelist()
        for year in YEARS:
            fields={}
            for component,suffix in COMPONENTS.items():
                name=f"{year}_{suffix}"
                selected=[x for x in names if Path(x).name==name]
                if len(selected)!=1:
                    raise ValueError(f"source krill raster source ambiguous {name}: {selected}")
                raw=z.read(selected[0])
                digest=hashlib.sha256(raw).hexdigest()
                if component=="combined" and digest!=expected[name]:
                    raise ValueError(f"publisher original modelled mean TIFF changed {name}")
                with MemoryFile(raw) as mf:
                    with mf.open() as ds:
                        if ds.crs is None or ds.crs.to_epsg()!=4326:
                            raise ValueError("non-WGS84 raster; requires explicit reprojection")
                        if ds.count!=1 or ds.width!=241 or ds.height!=121:
                            raise ValueError("source TIFF shape/bands drifted")
                        trans=ds.transform
                        if trans.b!=0 or trans.d!=0:
                            raise ValueError("rotated raster not handled")
                        data=ds.read(1,masked=True)
                        arr=np.asarray(data.filled(np.nan),dtype=float)
                        fields[component]=arr
                        geometry=(ds.width,ds.height,tuple(trans)[:6])
                        if "_geometry" in fields and geometry!=fields["_geometry"]:
                            raise ValueError("different source raster geometry")
                        fields["_geometry"]=geometry
                        audit.append({"year":year,"name":name,"component":component,
                                      "sha256":digest,"valid_cells":int(np.isfinite(arr).sum())})
                        fields["_transform"]=trans
            p=fields["prob"]
            q=fields["density_positive"]
            combined=fields["combined"]
            if not np.array_equal(np.isfinite(p),np.isfinite(q)) or not np.array_equal(np.isfinite(p),np.isfinite(combined)):
                raise ValueError("different model component cell-mask geometry")
            valid=np.isfinite(combined)
            if np.any(p[valid]<0) or np.any(p[valid]>1.000001) or np.any(q[valid]<0) or np.any(combined[valid]<0):
                raise ValueError("invalid modelled krill probability/positive density")
            if np.max(np.abs(combined[valid]-p[valid]*q[valid]))>1e-4:
                raise ValueError("combined raster not product of binomial and positive density")
            found[year]=fields
    return found,audit,hashlib.sha256(Path(source).read_bytes()).hexdigest()

def grid_rows(source):
    lat0,lon0=gps_anchor()
    files,hashes,container_sha=raster_fields(source)
    rows=[]
    source_geom=None
    for year in YEARS:
        field=files[year]
        data=field["combined"]
        tr=field["_transform"]
        if source_geom is None:source_geom=field["_geometry"]
        if field["_geometry"]!=source_geom:
            raise ValueError("different year-specific raster geometry")
        yy,xx=np.meshgrid(np.arange(data.shape[0])+0.5,
                          np.arange(data.shape[1])+0.5,indexing="ij")
        lon=tr.a*xx+tr.b*yy+tr.c
        lat=tr.d*xx+tr.e*yy+tr.f
        km=great_circle(lat,lon,lat0,lon0)
        valid=np.isfinite(data)
        weights=np.cos(np.deg2rad(lat))
        for radius in RADIUS:
            spatial=km<=radius
            area=valid&spatial
            if not np.any(area):
                raise ValueError("no valid raster cells near Signy for model sensitivity "+str(radius))
            q={"survey_calendar_year":year,
               "center_latitude":lat0,"center_longitude":lon0,
               "distance_radius_km":radius,
               "all_pixel_centers_in_radius":int(spatial.sum()),
               "model_valid_grid_cells":int(area.sum()),
               "model_valid_fraction":float(area.sum()/spatial.sum()),
               "area_weighted_predicted_krill_g_m2":float(np.average(data[area],weights=weights[area])),
               "area_weighted_occurrence_probability":float(np.average(field["prob"][area],weights=weights[area])),
               "area_weighted_positive_density_g_m2":float(np.average(field["density_positive"][area],weights=weights[area]))}
            rows.append(q)
    meta={"original_source_doi":ORIGINAL_DOI,
          "download_zip_sha256_this_run":container_sha,
          "original_raster_sha256_verified":True,
          "source_tiff_audit":hashes,
          "raster_native_crs":"EPSG:4326",
          "native_raster_height":source_geom[1],
          "native_raster_width":source_geom[0],
          "native_resolution_degrees":[source_geom[2][0],abs(source_geom[2][4])],
          "published_metadata_says_resolution_degrees":0.04,
          "source_colony_reference_points":14,
          "center_method":"midpoint of latitude and longitude min/max among 14 official colony reference GPS points",
          "signy_reference_center":[lat0,lon0],
          "radii_km":list(RADIUS),
          "model_type":"within-era 2011-2020 fitted hurdle GAM, includes original IMR acoustic data and covariate sea ice, salinity",
          "grid_cell_role":"model-valid raster center, not independently verified marine-only sampling footprint or penguin foraging position"}
    return rows,meta

def simple_corr(x,y):
    if len(x)!=len(y) or len(x)<4:
        raise ValueError("insufficient year support")
    xa=statistics.mean(x);ya=statistics.mean(y)
    cov=sum((v-xa)*(u-ya) for v,u in zip(x,y))
    den=math.sqrt(sum((v-xa)**2 for v in x)*sum((u-ya)**2 for u in y))
    return cov/den if den>1e-12 else None

def ranks(x):
    order=sorted(range(len(x)),key=lambda i:x[i])
    ans=[0.0]*len(x)
    p=0
    while p<len(x):
        q=p+1
        while q<len(x) and x[order[p]]==x[order[q]]:
            q+=1
        for j in range(p,q):
            ans[order[j]]=(p+q+1)/2
        p=q
    return ans

def stage_link(stage_file,original_file):
    values={}
    for row in read_csv(stage_file):
        sp=row["species"];year=int(row["season_start"])
        if sp not in SPECIES or year not in range(2011,2020):
            continue
        val=float(row["median_recorded_fledglings_per_pair"])
        if (sp,year) in values:
            raise ValueError("duplicate stage species-year")
        if int(row["has_reported_fledglings_n"])<1:
            raise ValueError("no documented native fledglings")
        values[(sp,year)]=val
    if len(values)!=27:
        raise ValueError("missing one of 3 species × 9 stage years")
    source={k:0 for k in values}
    for row in read_csv(original_file):
        key=row["species"],int(row["season_start"])
        if key not in values or not row["recorded_fledglings_per_pair"]:
            continue
        if row["nest_before_fledglings"]!="True":
            raise ValueError("native fledgling chronology unresolved")
        from datetime import date
        d=date.fromisoformat(row["fledgling_count_date"])
        if d.year!=key[1]+1 or d.month not in (1,2,3):
            raise ValueError("native fledgling date does not match season")
        source[key]+=1
    if any(n<1 for n in source.values()):
        raise ValueError("source native stage rows missing")
    return values

def associations(krill_rows,stage_values):
    index={(r["distance_radius_km"],r["survey_calendar_year"]):r for r in krill_rows}
    results=[]
    for radius in RADIUS:
        for offset,name in ((0,"preseason_summer_survey_t"),(1,"concurrent_summer_survey_t_plus_1")):
            for scope in ("all","complete_acoustic_coverage","complete_without_2012"):
                years=list(range(2011,2020))
                if scope!="all":
                    years=[y for y in years if y+offset not in (2013,2015)]
                if scope=="complete_without_2012":
                    years=[y for y in years if y!=2012]
                if len(years)<4:raise ValueError("too few sample years")
                x=[index[(radius,y+offset)]["area_weighted_predicted_krill_g_m2"] for y in years]
                for sp in SPECIES:
                    y=[stage_values[sp,z] for z in years]
                    loo=[simple_corr(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(len(years))]
                    results.append({
                        "radius_km":radius,
                        "survey_year_offset":offset,
                        "alignment":name,
                        "cohort":scope,
                        "species":sp,
                        "breeding_years":";".join(map(str,years)),
                        "n_distinct_breeding_years":len(years),
                        "pearson_r":simple_corr(x,y),
                        "spearman_r":simple_corr(ranks(x),ranks(y)),
                        "loo_r_min":min(loo),"loo_r_max":max(loo),
                        "model_predictions_not_observations":True
                    })
    if len(results)!=54:
        raise ValueError("all fixed specifications not retained")
    return results

def region_compare(krill_rows):
    observations={}
    for r in read_csv(REGIONAL):
        if r["source_table"]!="Table_2_overall_stratum":
            raise ValueError("not original whole-stratum series")
        observations[int(r["survey_calendar_year"])]=float(r["density_g_m2"])
    if set(observations)!=set(YEARS):
        raise ValueError("prior same-IMR survey source changed")
    local={(r["distance_radius_km"],r["survey_calendar_year"]):r["area_weighted_predicted_krill_g_m2"] for r in krill_rows}
    results=[]
    for rad in RADIUS:
        x=[local[(rad,y)] for y in YEARS]
        y=[observations[t] for t in YEARS]
        results.append({"radius_km":rad,"n_years":len(YEARS),
                        "pearson_r":simple_corr(x,y),
                        "spearman_r":simple_corr(ranks(x),ranks(y)),
                        "overlaps_original_IMR_acoustic_samples":True})
    return results

def run(source,stage_dir):
    spatial,metadata=grid_rows(source)
    stage=stage_link(Path(stage_dir)/"species_annual_stage_summary.csv",
                     Path(stage_dir)/"source_stage_site_seasons.csv")
    association=associations(spatial,stage)
    acoustic=region_compare(spatial)
    return spatial,association,acoustic,metadata

def check(spatial,comparison,metadata):
    # Source-level numeric receipt determined before writing this v2 script;
    # no p-value or favourable radius/lag model selection is authorized.
    expected={(2011,25):12.230751549146726,
              (2012,25):16.876536534818975,
              (2012,100):24.521396849199192,
              (2019,100):10.201897598856602,
              (2020,25):10.127658570955345}
    for (yr,rad),value in expected.items():
        r=next(r for r in spatial if r["survey_calendar_year"]==yr and r["distance_radius_km"]==rad)
        if not math.isclose(r["area_weighted_predicted_krill_g_m2"],value,rel_tol=1e-7,abs_tol=1e-6):
            raise ValueError(f"independent local numeric receipt changed {yr}/{rad}")
    if len(spatial)!=30 or len(comparison)!=54:
        raise ValueError("the full 10y × 3 radii or 54 combinations not retained")
    if metadata["source_colony_reference_points"]!=14 or not all(math.isclose(v,1/12,abs_tol=1e-10) for v in metadata["native_resolution_degrees"]):
        raise ValueError("source geometry changed")
    for rad,n in ((25,38),(50,175),(100,745)):
        if {x["model_valid_grid_cells"] for x in spatial if x["distance_radius_km"]==rad}!={n}:
            raise ValueError("model-valid pixel support changed")
    return True

def save_csv(path,rows):
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",required=True,type=Path)
    p.add_argument("--stage-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check-receipt",action="store_true")
    args=p.parse_args()
    spatial,associations_csv,regional,metadata=run(args.zip,args.stage_dir)
    if args.check_receipt:
        check(spatial,associations_csv,metadata)
    args.out.mkdir(parents=True,exist_ok=True)
    save_csv(args.out/"year_radii.csv",spatial)
    save_csv(args.out/"stage_correlations.csv",associations_csv)
    save_csv(args.out/"regional_compare.csv",regional)
    (args.out/"source_checks.json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":"EXPLORATORY_SPATIAL_GAM_EXPOSURE_NOT_INDEPENDENT_PREY_OBSERVATION",
      "source_sha":metadata["download_zip_sha256_this_run"],
      "model_tiff_sha_verified":metadata["original_raster_sha256_verified"],
      "native_step_degrees":metadata["native_resolution_degrees"],
      "signy_anchor":metadata["signy_reference_center"],
      "years":[spatial[0]["survey_calendar_year"],spatial[-1]["survey_calendar_year"]],
      "n_cells_by_radius":{r:next(z["model_valid_grid_cells"] for z in spatial if z["distance_radius_km"]==r) for r in RADIUS},
      "primary_preseason_correlations":{rad:{sp:next(z["pearson_r"] for z in associations_csv if z["radius_km"]==rad and z["survey_year_offset"]==0 and z["cohort"]=="all" and z["species"]==sp) for sp in SPECIES} for rad in RADIUS},
      "2012_omitted":{sp:next(z["pearson_r"] for z in associations_csv if z["radius_km"]==25 and z["survey_year_offset"]==0 and z["cohort"]=="complete_without_2012" and z["species"]==sp) for sp in SPECIES},
      "checked":bool(args.check_receipt)
    },ensure_ascii=False))

if __name__=="__main__":
    main()
