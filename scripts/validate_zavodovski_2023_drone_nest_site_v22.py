"""2023 independent species-identified UAV nest locations in V18 consensus C→M sites.

Original 2023 drone nest data (14 Dec incubation) vs independent
Jan-2011 redigitized baseline and Jan-2016 satellite polygons.
POST-OUTCOME descriptive site-level observation audit only.
No population settlement rate, individual displacement, or causal inference.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile
from urllib.parse import quote

import requests
import shapefile
from pyproj import CRS
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from shapely.prepared import prep

from reproduce_zavodovski_direct_image_overlap_v10 import (
    audit_dictionary, download_layers, read_geometry,
    secure_request, canonical_file_url, SUFFIXES,
)
from compare_zavodovski_lynch2011_digitizations_v13 import fetch_lynch
from mixed_zavodovski_2011_historical_overlap_v15 import original_three_categories
from validate_zavodovski_2020_uav_nests_v21 import (
    source_baseline_layers, FIXED_T_AREAS, LAND_FOLDER, COAST_BASENAME, HOST
)

DOI = "10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308"
DATE_2023 = "2023-12-14"
GEO_LAYERS = (
    "macaroni_nest_points_2023",
    "chinstrap_nest_points_2023",
    "macaroni_colony_boundaries_2023",
    "chinstrap_colony_boundaries_2023",
    "area_outwith_drone_survey_2023",
    COAST_BASENAME,
)
NEST_SOURCES = ("macaroni_nest_points_2023","chinstrap_nest_points_2023")
POLY_SOURCES = ("macaroni_colony_boundaries_2023",
                "chinstrap_colony_boundaries_2023",
                "area_outwith_drone_survey_2023", COAST_BASENAME)
UTM_E_WINDOW=(458000,470000)
UTM_N_WINDOW=(3755000,3767000)


def retrieve_2023(session, folder):
    manifest_url=("https://"+HOST+"/repository/entry/show?entryid="+
                  quote(LAND_FOLDER,safe="")+"&output=default.csv")
    source_manifest=secure_request(session,manifest_url,limit=250000).decode("utf-8-sig")
    available={r["name"]:r for r in csv.DictReader(io.StringIO(source_manifest))}
    hashes={}
    paths={}
    folder.mkdir(parents=True,exist_ok=True)
    for base in GEO_LAYERS:
        for ext in SUFFIXES:
            name=base+ext
            if name not in available or not available[name].get("url"):
                raise ValueError("SOURCE_STOP unavailable original 2023 drone sidecar "+name)
            url=canonical_file_url(available[name]["url"])
            data=secure_request(session,url,limit=80000000)
            if not data:
                raise ValueError("SOURCE_STOP empty original 2023 file "+name)
            (folder/name).write_bytes(data)
            hashes[name]=hashlib.sha256(data).hexdigest()
        paths[base]=folder/(base+".shp")
    return paths,hashes


def authorized_empty_shape(record):
    """Only an original type-5 polygon with literally no part/point may be ignored."""
    return (record.shapeType == shapefile.POLYGON
            and not record.points
            and not getattr(record,"parts",[]))


def read_2023_maca_polygon_narrowly(path):
    """Skip ONLY the single published 2023 maca empty POLYGON placeholder.

    No coordinate repair, geometry simplification, silent omission or
    species reclassification is permitted for any other original record.
    """
    # Local import avoids source-scanner ↔ V22 circular import during test collection.
    from audit_zavodovski_2023_polygon_empty_source_v22a import inspect_polygon_shape_records
    source_layout=inspect_polygon_shape_records(path)
    if (source_layout["source_shape_type"]!=5
        or source_layout["original_record_count"]!=170
        or source_layout["original_nonnull_zero_vertex_record_count"]!=1
        or source_layout["original_zero_vertex_record_count"]!=1
        or source_layout["original_nonempty_shape_records"]!=169):
        raise ValueError("SOURCE_STOP maca 2023 empty source record contract changed")
    validate_crs(path)
    records=shapefile.Reader(str(path))
    kept=[]
    skipped=0
    for s in records.iterShapes():
        if authorized_empty_shape(s):
            skipped+=1
            continue
        if not s.points or not getattr(s,"parts",[]):
            raise ValueError("GEOMETRY_STOP unexplained nonempty/nonpolygon shape problem")
        geo=shape(s.__geo_interface__)
        if geo.is_empty or not geo.is_valid or geo.geom_type not in ("Polygon","MultiPolygon"):
            raise ValueError("GEOMETRY_STOP invalid NONEMPTY original maca polygon")
        kept.append(geo)
    if skipped!=1 or len(kept)!=169:
        raise ValueError("SOURCE_STOP original maca 2023 record count not reproduced")
    result=unary_union(kept)
    if result.is_empty or not result.is_valid:
        raise ValueError("GEOMETRY_STOP union of original maca source records invalid")
    return result,{"original_shape_records":170,"original_nonempty_polygons":169,
                   "empty_placeholder_skipped_without_repair":1,
                   "source_maca_polygon_geometry_repaired":False}


def validate_crs(path):
    raw=path.with_suffix(".prj").read_text(encoding="utf-8")
    proj=CRS.from_wkt(raw)
    if proj.to_epsg()!=32726 and not proj.equals(CRS.from_epsg(32726)):
        raise ValueError("GEOMETRY_STOP 2023 GIS file not EPSG:32726: "+path.name)


def audited_points(path):
    validate_crs(path)
    r=shapefile.Reader(str(path))
    if r.shapeType not in (shapefile.POINT,shapefile.POINTZ,shapefile.POINTM):
        raise ValueError("GEOMETRY_STOP 2023 nest file is not source Point type")
    pts=[]
    exact=set()
    for s in r.iterShapes():
        if len(s.points)!=1:
            raise ValueError("GEOMETRY_STOP malformed original 2023 nest shape")
        x,y=s.points[0][:2]
        if not all(math.isfinite(z) for z in (x,y)):
            raise ValueError("GEOMETRY_STOP 2023 nest contains nonfinite map coordinate")
        if not (UTM_E_WINDOW[0]<=x<=UTM_E_WINDOW[1] and
                UTM_N_WINDOW[0]<=y<=UTM_N_WINDOW[1]):
            raise ValueError("GEOMETRY_STOP 2023 nest outside preread Zavodovski UTM window")
        pts.append(Point(float(x),float(y)))
        exact.add((float(x),float(y)))
    if not pts:
        raise ValueError("SOURCE_STOP zero original 2023 nest geometries")
    qa={
        "original_source_point_rows":len(pts),
        "distinct_exact_coordinates":len(exact),
        "exact_duplicate_coordinate_rows":len(pts)-len(exact),
        "E_range_m":[round(min(x for x,y in exact),3), round(max(x for x,y in exact),3)],
        "N_range_m":[round(min(y for x,y in exact),3), round(max(y for x,y in exact),3)],
    }
    return pts,qa


def clip_survey(cores, direct, historic, survey_land):
    # P is an explicitly stricter persistent CHPE control:
    # 2011-CHPE under both digitizations, retained as chinstrap in 2016,
    # with no mapped maca from either 2011 interpretation or in 2016.
    hist_c=historic["CHPE"]
    hist_m=historic["MCPE"].union(historic["MIXED"])
    c0,c1=direct[2011,"chinstrap"],direct[2016,"chinstrap"]
    m0,m1=direct[2011,"macaroni"],direct[2016,"macaroni"]
    cloud=unary_union([direct[2011,"cloud"],direct[2016,"cloud"]])
    source_mask=unary_union([c0,c1,m0,m1,*historic.values()]).difference(cloud)
    P=(c0.intersection(hist_c).intersection(c1)
       .difference(unary_union([m0,m1,hist_m]))
       .intersection(source_mask))
    Q=m0.intersection(m1).intersection(source_mask)
    return {
        **{f"T_{metres}m":core.intersection(survey_land) for metres,core in cores.items()},
        "P_consensus_persistent_Chinstrap":P.intersection(survey_land),
        "Q_persistent_Macaroni":Q.intersection(survey_land),
    }


def count_in_regions(points,regions):
    compiled={key:{"prepared":prep(geom),"points":0,"exact":set(),"cells5":set(),"cells10":set()}
              for key,geom in regions.items()}
    for pt in points:
        xy=(pt.x,pt.y)
        for key,z in compiled.items():
            if z["prepared"].contains(pt):
                z["points"]+=1
                z["exact"].add(xy)
                z["cells5"].add((math.floor(pt.x/5),math.floor(pt.y/5)))
                z["cells10"].add((math.floor(pt.x/10),math.floor(pt.y/10)))
    return {
        key:{"nest_point_rows":z["points"],
             "distinct_exact_coordinate_points":len(z["exact"]),
             "occupied_5m_grid_cells":len(z["cells5"]),
             "occupied_10m_grid_cells":len(z["cells10"])}
        for key,z in compiled.items()
    }


def analyze_counts(points,qa_by_species,original_cores,drone_poly,direct,historic):
    land=drone_poly[COAST_BASENAME]
    outside=drone_poly["area_outwith_drone_survey_2023"]
    if land.is_empty or outside.is_empty or not land.is_valid or not outside.is_valid:
        raise ValueError("SURVEY_STOP invalid published land or unsurveyed-area geometry")
    surveyed=land.difference(outside)
    if surveyed.is_empty or not surveyed.is_valid:
        raise ValueError("SURVEY_STOP no valid 2023 surveyed land")
    regions=clip_survey(original_cores,direct,historic,surveyed)
    if any(g is None or not g.is_valid for g in regions.values()):
        raise ValueError("SURVEY_STOP invalid surveyed historical evaluation region")
    summary={
        "status":"V22_2023_DIRECT_UAV_NESTS_AUDITED_EXPLORATORY",
        "year":"2023-12-14",
        "source_doi":DOI,
        "historical_baseline":"Jan 2011 redigitization consensus pure CHPE, Jan 2016 maca gain",
        "original_V18_T_area_m2":{str(k):round(v.area,3) for k,v in original_cores.items()},
        "surveyed_T_area_m2":{str(k):round(regions[f"T_{k}m"].area,3) for k in original_cores},
        "fraction_V18_T_observed_by_2023_survey":{
            str(k):round(regions[f"T_{k}m"].area/v.area,6) if v.area else None
            for k,v in original_cores.items()},
        "evaluation_regions":{k:{"area_m2":round(geom.area,3)} for k,geom in regions.items()},
        "source_point_QA":qa_by_species,
        "same_2023_species_boundary_QA":{},
        "region_point_counts_by_species":{},
        "note":"Semi-automatically classified 2023 nest point observations, NOT individually tracked penguins, 2011 new founders or a causal competition test."
    }
    prep_land=prep(land.buffer(50))
    for species in ("Macaroni","Chinstrap"):
        pts=points[species]
        boundary=drone_poly[f"{species.lower()}_colony_boundaries_2023"]
        prepared=prep(boundary.buffer(5))
        on_species=sum(prepared.covers(pt) for pt in pts)
        on_island=sum(prep_land.covers(pt) for pt in pts)
        species_frac=on_species/len(pts)
        land_frac=on_island/len(pts)
        summary["same_2023_species_boundary_QA"][species]={
            "within_5m_same_species_colony_polygon_rows":on_species,
            "fraction_within_5m_same_species_polygon":round(species_frac,6),
            "within_50m_2023_coastline_land_rows":on_island,
            "fraction_on_or_near_land":round(land_frac,6),
            "required_minimum_fraction":0.9
        }
        if species_frac<0.90 or land_frac<0.90:
            raise ValueError(f"SOURCE_STOP {species} 2023 point vs same-date mapped polygon/land QC below preread 90%")
        summary["region_point_counts_by_species"][species]=count_in_regions(pts,regions)

    for label in regions:
        counts={sp:summary["region_point_counts_by_species"][sp][label]["nest_point_rows"]
                for sp in ("Macaroni","Chinstrap")}
        total=sum(counts.values())
        area=regions[label].area
        summary["evaluation_regions"][label].update({
            "Macaroni_2023_nest_point_rows":counts["Macaroni"],
            "Chinstrap_2023_nest_point_rows":counts["Chinstrap"],
            "Maca_fraction_of_two_species_nest_points":round(counts["Macaroni"]/total,6) if total else None,
            "Maca_record_point_density_per_ha":round(10000*counts["Macaroni"]/area,3) if area else None,
            "Chinstrap_record_point_density_per_ha":round(10000*counts["Chinstrap"]/area,3) if area else None,
            "not_a_2023_breeding_pair_estimate":True,
        })
    summary["2023_mac_nest_points_in_V18_T0"]=summary["evaluation_regions"]["T_0m"]["Macaroni_2023_nest_point_rows"]
    summary["2023_chinstrap_nest_points_in_V18_T0"]=summary["evaluation_regions"]["T_0m"]["Chinstrap_2023_nest_point_rows"]
    summary["2023_mac_nest_points_in_V18_T5"]=summary["evaluation_regions"]["T_5m"]["Macaroni_2023_nest_point_rows"]
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result={"status":"HOLD_SOURCE_OR_GEOMETRY","original_2023_nest_point_rows_opened":0}
    try:
        audit_dictionary("sources/bas_zavodovski_layer_descriptions_v1.csv")
        with tempfile.TemporaryDirectory(prefix="zav22-original-nests-") as tmp:
            with requests.Session() as session:
                base_paths,basehash=download_layers(session,Path(tmp)/"historical")
                orig_path,orig_hash=fetch_lynch(session,Path(tmp))
                drone_paths,drone_hash=retrieve_2023(session,Path(tmp)/"2023")
            hist,_=original_three_categories(orig_path)
            cores,control,direct,other,support=source_baseline_layers(base_paths,hist)
            drone_poly={}
            source_empty_record_audit={}
            for name in POLY_SOURCES:
                if name=="macaroni_colony_boundaries_2023":
                    geom,empty_audit=read_2023_maca_polygon_narrowly(drone_paths[name])
                    source_empty_record_audit[name]=empty_audit
                else:
                    geom,count=read_geometry(drone_paths[name])
                drone_poly[name]=geom
            result["source_empty_record_audit"]=source_empty_record_audit
            nests,qa={},{}
            for name in NEST_SOURCES:
                specie="Macaroni" if name.startswith("macaroni") else "Chinstrap"
                vals,metadata=audited_points(drone_paths[name])
                nests[specie]=vals
                qa[specie]=metadata
            result["original_2023_nest_point_rows_opened"]=sum(len(x) for x in nests.values())
            result.update(analyze_counts(nests,qa,cores,drone_poly,direct,hist))
            result["sha256_authenticated_original_gis"]={**basehash,**orig_hash,**drone_hash}
            result["original_2022_chinstrap_uav_rows_read"]=0
    except Exception as exc:
        result["status"]="HOLD_SOURCE_OR_GEOMETRY"
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:600]
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="sha256_authenticated_original_gis"},ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)

if __name__=="__main__":
    main()
