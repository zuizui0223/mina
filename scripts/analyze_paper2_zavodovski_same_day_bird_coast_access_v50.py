#!/usr/bin/env python3
"""Paper2 V50 Zavodovski 2023: same-day giant-petrel vs penguin coast access.

Exactly one original physical island with SAME original UAV campaign:
5 published BAS GIS POLYGON layers: MACA, CHIN, GIANT PETREL, coast, not-surveyed.
No per-nest movement, true vacancy, actual shore-entry trails, or mammal effects.
All original geometry SHA receipts preserved; only aggregate areas/distances
are printed, not original bird colony positions.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,math,tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs,quote,urlparse,urlunparse

import numpy as np
import requests
import shapefile
from pyproj import CRS
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely import contains_xy,points,distance

PARENT="7220dc6b-2f52-4160-a6c0-e57c50963308"
HOST="ramadda.data.bas.ac.uk"
ALLOWED_REDIRECT_HOSTS={HOST,"194.66.5.50"}
FOLDER="synth:"+PARENT+":L2Ryb25lLWRlcml2ZWRfZGF0YQ=="
SOURCE_DATE="2023-12-14"
LAYERS=(
 "giant_petrel_colony_boundaries_2023",
 "chinstrap_colony_boundaries_2023",
 "macaroni_colony_boundaries_2023",
 "zavodovski_coastline_2023",
 "area_outwith_drone_survey_2023",
)
SIDECARS=(".shp",".shx",".dbf",".prj",".cpg")
MAX_MANIFEST=1_000_000
MAX_SOURCE_FILE=28_000_000
EPSG=32726
SAMPLE_GRID_M=(20,10,40)
PRIMARY_GRID_M=20
MIN_PETREL_PRIMARY_CELLS=20
MIN_PENGUIN_PRIMARY_CELLS=100
EXPECTED_MACARONI_SHAPES=170
EXPECTED_CHINSTRAP_SHAPES=2102
PROJ_BOUNDS=(457000,3753000,471000,3768000)
MAX_SOURCE_GRID_SAMPLE_POINTS=1_000_000
FIXED_ORIGINAL_DOI="10.5285/"+PARENT


def public_get(session,url,maxbytes):
    target=urlparse(url)
    if target.scheme!="https" or target.hostname!=HOST:
        raise ValueError("SOURCE_NOT_CANONICAL_PUBLISHER")
    with session.get(url,timeout=(18,85),stream=True,allow_redirects=True,
                     headers={"User-Agent":"mina-Paper2-original-Zavodovski-coast-v50/1.0"}) as response:
        response.raise_for_status()
        final=urlparse(response.url)
        if final.scheme!="https" or final.hostname not in ALLOWED_REDIRECT_HOSTS:
            raise ValueError("SOURCE_REDIRECT_NOT_ORIGINAL_BAS_PUBLISHER")
        out=bytearray()
        for block in response.iter_content(chunk_size=65536):
            if block:
                out.extend(block)
                if len(out)>maxbytes:
                    raise ValueError("SOURCE_PUBLIC_FILE_EXCEEDS_FROZEN_LIMIT")
    raw=bytes(out)
    if not raw or raw[:160].lstrip().lower().startswith((b"<html",b"<!doctype")):
        raise ValueError("ORIGINAL_SOURCE_RETURNED_HTML_OR_EMPTY")
    return raw


def source_download_url(raw):
    p=urlparse(raw)
    if p.hostname!=HOST or p.scheme not in ("http","https") or p.port not in (None,443):
        raise ValueError("ORIGINAL_MANIFEST_LINK_NOT_BAS")
    if p.path.split("/")[:4]!=["","repository","entry","get"]:
        raise ValueError("ORIGINAL_MANIFEST_FILE_ENDPOINT_CHANGED")
    q=parse_qs(p.query)
    eid=q.get("entryid",[])
    if len(eid)!=1 or not eid[0].startswith("synth:"+PARENT+":"):
        raise ValueError("ORIGINAL_MANIFEST_EXTERNAL_DATASET_ID")
    return urlunparse(("https",HOST,p.path,"",p.query,""))


def original_five_polygon_sources(session,directory):
    uri="https://"+HOST+"/repository/entry/show?entryid="+quote(FOLDER,safe="")+"&output=default.csv"
    raw=public_get(session,uri,MAX_MANIFEST).decode("utf-8-sig")
    rows=list(csv.DictReader(io.StringIO(raw)))
    if not rows or not {"name","url"}.issubset(rows[0]):
        raise ValueError("BAS_DRONE_FOLDER_ORIGINAL_CSV_MANIFEST_CHANGED")
    source={x["name"]:x["url"] for x in rows}
    file_hash={}
    directories={}
    for basename in LAYERS:
        for ext in SIDECARS:
            filename=basename+ext
            if filename not in source:
                raise ValueError("ORIGINAL_2023_GIS_LAYER_MISSING_"+filename)
            url=source_download_url(source[filename])
            if urlparse(url).path.rsplit("/",1)[-1]!=filename:
                raise ValueError("ORIGINAL_GIS_MANIFEST_FILENAME_DOES_NOT_MATCH_URL")
            data=public_get(session,url,MAX_SOURCE_FILE)
            if ext in (".shp",".shx") and data[:4]!=bytes.fromhex("0000270a"):
                raise ValueError("SOURCE_SHAPEFILE_MAGIC_CHANGED")
            if ext==".dbf" and data[:1] not in (b"\x03",b"\x83",b"\x30"):
                raise ValueError("SOURCE_DBF_MAGIC_CHANGED")
            dest=directory/filename
            dest.write_bytes(data)
            file_hash[filename]=hashlib.sha256(data).hexdigest()
        directories[basename]=directory/(basename+".shp")
    return directories,file_hash


def shape_polygon_original(path,name):
    crs=CRS.from_wkt(path.with_suffix(".prj").read_text(encoding="utf-8"))
    if crs.to_epsg()!=EPSG and not crs.equals(CRS.from_epsg(EPSG)):
        raise ValueError("V50_ORIGINAL_SHAPE_NOT_UTM_26S:"+name)
    reader=shapefile.Reader(str(path))
    if reader.shapeType!=shapefile.POLYGON:
        raise ValueError("SOURCE_EXPECTED_POLYGON:"+name)
    original=0;empty=0;polygons=[]
    for shp in reader.iterShapes():
        original+=1
        if shp.shapeType==shapefile.NULL or not getattr(shp,"points",[]):
            if name!="macaroni_colony_boundaries_2023":
                raise ValueError("ORIGINAL_NON_MACA_EMPTY_POLYGON:"+name)
            empty+=1
            continue
        geom=shape(shp.__geo_interface__)
        if geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon","MultiPolygon"):
            raise ValueError("ORIGINAL_NONEMPTY_POLYGON_INVALID:"+name)
        bx=geom.bounds
        if not(PROJ_BOUNDS[0]<=bx[0]<=bx[2]<=PROJ_BOUNDS[2] and
               PROJ_BOUNDS[1]<=bx[1]<=bx[3]<=PROJ_BOUNDS[3]):
            raise ValueError("ORIGINAL_POLYGON_OUTSIDE_SOURCE_ZAVODOVSKI_UTM_BOUNDS:"+name)
        polygons.append(geom)
    if name=="macaroni_colony_boundaries_2023":
        if original!=EXPECTED_MACARONI_SHAPES or empty!=1:
            raise ValueError("ORIGINAL_MACARONI_EMPTY_RECORD_PREV_AUDIT_DRIFT")
    if name=="chinstrap_colony_boundaries_2023" and original!=EXPECTED_CHINSTRAP_SHAPES:
        raise ValueError("ORIGINAL_CHINSTRAP_POLYGON_COUNT_PREV_AUDIT_DRIFT")
    if name in ("zavodovski_coastline_2023","area_outwith_drone_survey_2023"):
        if original!=1 or empty:
            raise ValueError("ORIGINAL_COVERAGE_FRAME_NOT_ONE_VALID_SOURCE_POLYGON")
    if not polygons:
        raise ValueError("ORIGINAL_GIANT_PETREL_FLYING_COLONY_POLYGONS_NOT_FOUND")
    combo=unary_union(polygons)
    if combo.is_empty or not combo.is_valid:
        raise ValueError("ORIGINAL_UNION_GEOMETRY_INVALID_"+name)
    return combo,{
        "published_original_layer_name":name,
        "source_records":original,
        "original_nonempty_source_shapes":len(polygons),
        "literal_empty_source_polygon_shapes":empty,
        "original_species_or_boundary_geometry_repaired":False,
        "native_original_projected_area_m2":float(combo.area),
        "crs":"EPSG:32726",
    }


def sample_grid_distances(coast,survey,petrel,chin,macaroni,grid_m):
    """Area-grid cell midpoint draws: cells are NOT island-level replicates."""
    if grid_m not in SAMPLE_GRID_M:
        raise ValueError("UNFROZEN_GRID_CELLS")
    xmin,ymin,xmax,ymax=coast.bounds
    x=np.arange(math.floor(xmin/grid_m)*grid_m+grid_m/2, xmax, grid_m)
    y=np.arange(math.floor(ymin/grid_m)*grid_m+grid_m/2, ymax, grid_m)
    if len(x)*len(y)>MAX_SOURCE_GRID_SAMPLE_POINTS:
        raise ValueError("FROZEN_AREA_GRID_MILLION_CELL_LIMIT")
    distarr={"PETREL":[],"PENGUIN":[],"CHINSTRAP":[],"MACARONI":[]}
    counts=Counter()
    # Use exact original coastline exterior, not arbitrary one ecological route.
    if coast.geom_type=="Polygon":
        coastline=coast.exterior
    elif coast.geom_type=="MultiPolygon":
        coastline=unary_union([p.exterior for p in coast.geoms])
    else:
        raise ValueError("COASTLINE_NOT_ORIGINAL_POLYGON")
    for batch in range(0,len(y),32):
        xx,yy=np.meshgrid(x,y[batch:batch+32])
        xx=xx.ravel();yy=yy.ravel()
        selected=contains_xy(survey,xx,yy)
        counts["source_survey_grid_cells"]+=int(np.count_nonzero(selected))
        if not np.any(selected):continue
        a=xx[selected];b=yy[selected]
        flying=contains_xy(petrel,a,b)
        chinmask=contains_xy(chin,a,b)
        macmask=contains_xy(macaroni,a,b)
        penguin=chinmask|macmask
        overlap=flying&penguin
        pure_f=flying&~penguin
        pure_p=penguin&~flying
        counts["source_grid_flying_and_penguin_polygon_overlap"]+=int(overlap.sum())
        counts["source_grid_flying_only"]+=int(pure_f.sum())
        counts["source_grid_penguin_only"]+=int(pure_p.sum())
        counts["source_grid_no_colony_polygon"]+=int((~flying&~penguin).sum())
        used=pure_f|pure_p
        if not used.any():continue
        shore=distance(points(a[used],b[used]),coastline)
        d=np.asarray(shore,dtype=float)
        inds_f=pure_f[used]
        inds_p=pure_p[used]
        inds_c=chinmask[used]&~flying[used]
        inds_m=macmask[used]&~flying[used]
        for key,mask in (("PETREL",inds_f),("PENGUIN",inds_p),
                         ("CHINSTRAP",inds_c),("MACARONI",inds_m)):
            if np.any(mask):distarr[key].append(d[mask])
    quant={}
    for key,chunks in distarr.items():
        if chunks:
            arr=np.concatenate(chunks)
            quant[key]={
                "source_occupied_utm_grid_centres":int(len(arr)),
                "coast_distance_m_q05":float(np.quantile(arr,.05)),
                "coast_distance_m_median":float(np.median(arr)),
                "coast_distance_m_q95":float(np.quantile(arr,.95)),
                "original_mapped_area_approx_m2":int(len(arr)*grid_m**2),
            }
        else:
            quant[key]={
                "source_occupied_utm_grid_centres":0,
                "coast_distance_m_q05":None,
                "coast_distance_m_median":None,
                "coast_distance_m_q95":None,
                "original_mapped_area_approx_m2":0,
            }
    return {"grid_m":grid_m,"source_grid_point_support":dict(counts),
            "coastline_distances_by_original_guild":quant,
            "original_country_or_species_independent_island_replicates":1}


def analyze_original(paths):
    sites={}
    source={}
    for name in LAYERS:
        geom,info=shape_polygon_original(paths[name],name)
        sites[name]=geom
        source[name]=info
    coastline=sites["zavodovski_coastline_2023"]
    uncovered=sites["area_outwith_drone_survey_2023"]
    covered=coastline.difference(uncovered)
    if covered.is_empty or not covered.is_valid:
        raise ValueError("SOURCE_COVERED_ISLAND_AREA_IS_INVALID")
    species={
        "PETREL":sites["giant_petrel_colony_boundaries_2023"],
        "CHINSTRAP":sites["chinstrap_colony_boundaries_2023"],
        "MACARONI":sites["macaroni_colony_boundaries_2023"],
    }
    occupied={name:species[name].intersection(covered) for name in species}
    for name,geo in occupied.items():
        if geo.is_empty or not geo.is_valid:
            raise ValueError("SOURCE_PETREL_OR_PENGUIN_ORIGINAL_HABITAT_OUTSIDE_2023_COVERAGE_"+name)
    penguin=occupied["CHINSTRAP"].union(occupied["MACARONI"])
    if not penguin.is_valid:
        raise ValueError("SOURCE_CHINSTRAP_MACARONI_UNION_INVALID")
    overlap=occupied["PETREL"].intersection(penguin)
    survey={
        "coastline_source_area_m2":float(coastline.area),
        "original_unobserved_polygon_area_m2":float(uncovered.area),
        "coastline_intersect_unobserved_area_m2":float(coastline.intersection(uncovered).area),
        "original_source_drone_surveillance_covered_land_m2":float(covered.area),
        "published_giant_petrel_occupied_polygon_area_m2":float(occupied["PETREL"].area),
        "published_chinstrap_occupied_polygon_area_m2":float(occupied["CHINSTRAP"].area),
        "published_macaroni_occupied_polygon_area_m2":float(occupied["MACARONI"].area),
        "published_penguin_pooled_union_polygon_area_m2":float(penguin.area),
        "original_petrel_penguin_polygon_overlap_m2":float(overlap.area),
        "source_newly_observed_single_island":True,
        "same_exact_original_drone_date":"2023-12-14",
        "bird_colonies_are_POLYGON_area_NOT_nest_count_or_persistence":True,
        "unobserved_breeding_areas_recode_as_absent":False,
        "true_island_bird_detection_or_flying_status_interaction_causally_identified":False,
    }
    grids={}
    for step in SAMPLE_GRID_M:
        grids[str(step)]=sample_grid_distances(
            coastline,covered,occupied["PETREL"],occupied["CHINSTRAP"],
            occupied["MACARONI"],step)
    primary=grids[str(PRIMARY_GRID_M)]["coastline_distances_by_original_guild"]
    eligible=(primary["PETREL"]["source_occupied_utm_grid_centres"]>=MIN_PETREL_PRIMARY_CELLS
              and primary["PENGUIN"]["source_occupied_utm_grid_centres"]>=MIN_PENGUIN_PRIMARY_CELLS)
    output={
        "original_site_polygon_inventory":source,
        "original_2023_native_UAV_survey_extent_and_colony_overlap":survey,
        "fixed_original_area_grid_coast_distance_distributions":grids,
        "primary_guild_comparison_source_support_pass":bool(eligible),
        "min_petrel_primary_area_grid_cells":MIN_PETREL_PRIMARY_CELLS,
        "min_penguin_primary_area_grid_cells":MIN_PENGUIN_PRIMARY_CELLS,
        "number_of_independent_real_islands":1,
        "same_2023_UAV_dated_flying_species":["Southern giant petrel"],
        "same_2023_UAV_dated_flightless_species":["Chinstrap penguin","Macaroni penguin"],
        "not_direct_actual_ocean_to_nest_walk_route_or_landscape_barrier":True,
        "no_mammalian_predator_contrast_on_this_one_island":True,
        "surveyed_nonbreeding_land_not_claimed":True,
        "no_animal_coordinates_or_polygon_vertices_committed":True,
    }
    if eligible:
        d=(primary["PETREL"]["coast_distance_m_median"]
            -primary["PENGUIN"]["coast_distance_m_median"])
        output["signed_flying_minus_flightless_occupied_polygon_median_nearest_coast_distance_m"]=d
        output["predeclared_flyer_more_inland_sign_supported_on_single_island"]=bool(d>0)
        output["alternate_grids_same_direction_as_primary"]={
            g:bool(
               entry["coastline_distances_by_original_guild"]["PETREL"]["coast_distance_m_median"]
               -entry["coastline_distances_by_original_guild"]["PENGUIN"]["coast_distance_m_median"]>0
            ) if entry["coastline_distances_by_original_guild"]["PETREL"]["coast_distance_m_median"] is not None
                 and entry["coastline_distances_by_original_guild"]["PENGUIN"]["coast_distance_m_median"] is not None
               else None
            for g,entry in grids.items()}
        output["status"]="V50_ZAVODOVSKI_SAME_DAY_POLYGON_COAST_DISTANCE_EXPLORATORY_COMPUTED"
    else:
        output["status"]="STOP_V50_FLYING_OR_PENGUIN_MAPPED_OCCUPIED_AREA_SUPPORT"
        output["original_animal_colony_distance_direction_computed"]=False
    return output


def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--out",type=Path,required=True)
    a=pa.parse_args()
    report={
        "schema":"MINA_PAPER2_ZAVODOVSKI_ORIGINAL_SAME_DAY_FLYING_V_FLIGHTLESS_V50",
        "status":"V50_ORIGINAL_SOURCE_ACCESS_OR_GEOMETRY_HOLD",
        "source_date":SOURCE_DATE,
        "original_BAS_dataset_DOI":FIXED_ORIGINAL_DOI,
        "contract":"contracts/PAPER2_ZAVODOVSKI_FLIGHT_ACCESS_ORIGINAL_UAV_V50.md",
        "recorded_post_preexisting_penguin_results_exploratory":True,
        "source_full_observation_effort_not_calibrated":True,
        "source_point_predator_GBIF_or_island_SDM_not_used":True,
    }
    try:
        with tempfile.TemporaryDirectory(prefix="bas-zavflight-v50-") as tmp:
            with requests.Session() as session:
                paths,checksums=original_five_polygon_sources(session,Path(tmp))
            report["source_original_GIS_files_SHA256"]=checksums
            report["analysis"]=analyze_original(paths)
            report["status"]=report["analysis"]["status"]
    except Exception as exc:
        report["error"]=type(exc).__name__+": "+str(exc)[:900]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    payload={
        "status":report["status"],
        "inventory":report.get("analysis",{}).get("original_site_polygon_inventory"),
        "survey":report.get("analysis",{}).get("original_2023_native_UAV_survey_extent_and_colony_overlap"),
        "primary_grid":report.get("analysis",{}).get("fixed_original_area_grid_coast_distance_distributions",{}).get("20"),
        "difference":report.get("analysis",{}).get("signed_flying_minus_flightless_occupied_polygon_median_nearest_coast_distance_m"),
        "error":report.get("error")
    }
    print(json.dumps(payload,ensure_ascii=False))
    if report["status"]=="V50_ORIGINAL_SOURCE_ACCESS_OR_GEOMETRY_HOLD":
        raise SystemExit(2)


if __name__=="__main__":
    main()
