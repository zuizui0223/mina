"""Positive-only 2020 UAV maca nest verification of 2011→2016 mapped change.

Original dated 2011/2016 BAS colony boundaries + independent 2019/20
UAV nest points. No 2022 Chinstrap coordinate file or any inferred absence.
Results are exploratory and not a causal island-biogeography estimate.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile
from urllib.parse import quote, urlparse

import requests
from pyproj import Transformer
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely.prepared import prep

from reproduce_zavodovski_direct_image_overlap_v10 import (
    audit_dictionary, download_layers, read_geometry, canonical_file_url,
    secure_request, SUFFIXES,
)
from compare_zavodovski_lynch2011_digitizations_v13 import fetch_lynch
from mixed_zavodovski_2011_historical_overlap_v15 import original_three_categories
from audit_zavodovski_2020_uav_nest_headers_v20 import (
    FILES as UAV_FILES, publisher_url, HOST
)

DOI = "10.5285/28222725-c53d-40f4-9350-49c368899f0b"
LAND_FOLDER = "synth:7220dc6b-2f52-4160-a6c0-e57c50963308:L2Ryb25lLWRlcml2ZWRfZGF0YQ=="
COAST_BASENAME = "zavodovski_coastline_2023"
FIXED_T_AREAS = {
    0: 9938.357203,
    1: 7003.755299,
    2: 4753.570626,
    5: 1216.517023,
}
MAX_BYTES = {
    "ZAVO_2020_Macaroni_coordinates.csv": 2000000,
    "ZAVO_2020_Mixed_species_coordinates.csv": 3000000,
}


def authenticated_source_csv(session, filename):
    if filename not in UAV_FILES:
        raise ValueError("SOURCE_STOP unauthorized source name: " + filename)
    url = publisher_url(session, filename)
    with session.get(url, timeout=(20, 70), stream=True, allow_redirects=True) as response:
        response.raise_for_status()
        final = urlparse(response.url)
        if final.scheme != "https" or final.hostname not in (HOST, "194.66.5.50"):
            raise ValueError("SOURCE_STOP off-publisher file redirect")
        chunks = bytearray()
        for piece in response.iter_content(chunk_size=16384):
            chunks.extend(piece)
            if len(chunks) > MAX_BYTES[filename]:
                raise ValueError("SOURCE_STOP original UAV CSV exceeds source byte limit")
    raw = bytes(chunks)
    if raw[:100].lstrip().lower().startswith(b"<html"):
        raise ValueError("SOURCE_STOP publisher served HTML")
    csvtext = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(csvtext)))
    if not rows or list(rows[0]) != ["nest_number", "lat", "lon"]:
        raise ValueError("SOURCE_STOP changed original 2020 nest-point schema")
    return rows, hashlib.sha256(raw).hexdigest(), len(raw)


def transform_nests(rows):
    to_utm = Transformer.from_crs(4326, 32726, always_xy=True)
    points = []
    raw_values = []
    for i, row in enumerate(rows):
        if None in row or any(row.get(k) is None or row[k].strip() == "" for k in ("nest_number", "lat", "lon")):
            raise ValueError("POINT_STOP missing source coordinate or source nest label")
        try:
            lat, lon = float(row["lat"]), float(row["lon"])
        except (TypeError, ValueError) as exc:
            raise ValueError("POINT_STOP nonnumeric latitude or longitude") from exc
        if not -56.34 <= lat <= -56.26 or not -27.66 <= lon <= -27.50:
            raise ValueError(f"POINT_STOP coordinate outside fixed Zavodovski bounding envelope on row {i}")
        xy = to_utm.transform(lon, lat)
        if not all(math.isfinite(v) for v in xy):
            raise ValueError("POINT_STOP invalid WGS84→UTM projection")
        points.append(Point(*xy))
        raw_values.append((lat,lon))
    if not points:
        raise ValueError("POINT_STOP no original nest coordinates")
    return points, {
        "rows": len(points),
        "unique_exact_latlon_pairs": len(set(raw_values)),
        "exact_duplicate_coordinate_rows": len(points)-len(set(raw_values)),
        "latitude_range": [min(x[0] for x in raw_values), max(x[0] for x in raw_values)],
        "longitude_range": [min(x[1] for x in raw_values), max(x[1] for x in raw_values)],
        "UTM_E_range": [round(min(p.x for p in points),2),round(max(p.x for p in points),2)],
        "UTM_N_range": [round(min(p.y for p in points),2),round(max(p.y for p in points),2)],
    }


def fetch_coastline(session, directory):
    folder=("https://"+HOST+"/repository/entry/show?entryid="+
            quote(LAND_FOLDER,safe="")+"&output=default.csv")
    manifest = secure_request(session, folder, limit=250000).decode("utf-8-sig")
    available={r["name"]:r for r in csv.DictReader(io.StringIO(manifest))}
    hashes={}
    directory.mkdir(parents=True,exist_ok=True)
    for ext in SUFFIXES:
        name=COAST_BASENAME+ext
        if name not in available:
            raise ValueError(f"SOURCE_STOP missing independent coastline sidecar {name}")
        link=canonical_file_url(available[name]["url"])
        blob=secure_request(session,link,limit=12000000)
        if not blob:
            raise ValueError("SOURCE_STOP empty coastline component")
        (directory/name).write_bytes(blob)
        hashes[name]=hashlib.sha256(blob).hexdigest()
    coast_path=directory/(COAST_BASENAME+".shp")
    land,count=read_geometry(coast_path)
    return land, count, hashes


def source_baseline_layers(paths, historic):
    direct={}
    for (year,name),path in paths.items():
        if year in (2011,2016,2025):
            geo,_=read_geometry(path,cloud=name.startswith("cloud_cover"))
            direct[year,name.split("_")[0]]=geo
    c0,m0=(direct[2011,k] for k in ("chinstrap","macaroni"))
    c1,m1=(direct[2016,k] for k in ("chinstrap","macaroni"))
    h_c,h_m,h_mix=(historic[x] for x in ("CHPE","MCPE","MIXED"))
    cloud=unary_union([direct[2011,"cloud"],direct[2016,"cloud"]])
    support=unary_union([c0,m0,c1,m1,h_c,h_m,h_mix]).difference(cloud)
    if support.is_empty or not support.is_valid:
        raise ValueError("BASELINE_STOP invalid original masked support")

    cores={}
    for margin,source_area in FIXED_T_AREAS.items():
        core=(c0.buffer(-margin).intersection(h_c.buffer(-margin))
              .intersection(m1.buffer(-margin)).intersection(support))
        blocked=unary_union([
            c1.buffer(margin),m0.buffer(margin),h_m.buffer(margin),
            h_mix.buffer(margin),cloud.buffer(margin)])
        core=core.difference(blocked)
        if core.is_empty or not core.is_valid or abs(core.area-source_area)>0.10:
            raise ValueError(f"BASELINE_STOP {margin}m core deviates from pinned V18 area")
        cores[margin]=core

    # Positive-control habitat is jointly occupied by M in BOTH revised maps;
    # this is NOT necessarily continuously breeding every day.
    historical_m=direct[2011,"macaroni"]
    positive_control=(historical_m.intersection(direct[2016,"macaroni"])
                      .intersection(support))
    all_mapped=unary_union([g for (year,sp),g in direct.items()
                            if sp in ("chinstrap","macaroni")])
    return cores, positive_control, direct, all_mapped, support


def count_locations(points, target):
    prepared = prep(target)
    selected=[p for p in points if prepared.contains(p)]
    return {
        "original_point_rows_with_center_inside":len(selected),
        "unique_exact_projected_coordinate_points":len({(p.x,p.y) for p in selected}),
        "occupied_5m_grid_cells":len({(math.floor(p.x/5),math.floor(p.y/5)) for p in selected}),
        "occupied_10m_grid_cells":len({(math.floor(p.x/10),math.floor(p.y/10)) for p in selected}),
        "no_pseudoreplicate_independence_claim":True
    }


def summarize(points_by_class, qc_by_class, cores, control, direct, all_mapped, land):
    result={"status":"2020_NEST_LOCATION_POSITIVE_ONLY_EXTERNAL_VALIDATION",
            "2020_source_doi":DOI,
            "map_source_doi":"10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308",
            "V18_cores_m2":{str(k):round(v.area,3) for k,v in cores.items()},
            "source_file_QC":qc_by_class,
            "species_nest_points":{},
            "coordinate_plausibility":{},
            "scientific_condition":"Only positive source nest-coordinate corroboration; no surveyed-zero, settlement propensity or causal mechanism."}
    prepared_land = prep(land.buffer(150))
    prepared_colonies = prep(all_mapped.buffer(100))
    for cat,pts in points_by_class.items():
        in_island=[p for p in pts if prepared_land.covers(p)]
        if cat=="Macaroni" and len(in_island)/len(pts)<0.90:
            raise ValueError("GEOREFERENCE_STOP less than 90% original maca points on/near 2023 coastline")
        near_mapped=sum(prepared_colonies.covers(p) for p in pts)
        result["coordinate_plausibility"][cat]={
            "point_rows_within_150m_of_2023_coastline_land":len(in_island),
            "fraction_within_150m_of_2023_land":round(len(in_island)/len(pts),6),
            "point_rows_within_100m_of_any_2011_2016_2025_mapped_penguin_boundary":near_mapped,
            "fraction_within_100m_of_mapped_colonies":round(near_mapped/len(pts),6),
            "note":"2023 coastline is an independent approximate location check, not contemporary 2020 habitat or survey mask."
        }
        result["species_nest_points"][cat]={
            "n_original_rows":len(pts),
            "within_V18_consensus_historic_CHPE_2011_to_M_2016_core":{
                str(m):count_locations(pts,g) for m,g in cores.items()},
            "positive_control_original_M_2011_and_2016":count_locations(pts,control),
            "original_2016_maca_mapped_polygons":count_locations(pts,direct[2016,"macaroni"]),
        }
    result["independent_2020_mac_nest_hits_strict_0m"] = result["species_nest_points"]["Macaroni"]["within_V18_consensus_historic_CHPE_2011_to_M_2016_core"]["0"]["original_point_rows_with_center_inside"]
    result["independent_2020_mac_nest_hits_strict_5m"] = result["species_nest_points"]["Macaroni"]["within_V18_consensus_historic_CHPE_2011_to_M_2016_core"]["5"]["original_point_rows_with_center_inside"]
    result["interpretation"]=(
        "An independently observed 2020 MAC nest point inside V18 consensus historic 2011 CHPE site "
        "corroborates later dated maca nest-site use, but not original 2011 maca absence or immigration. "
        "No geographic 2020 coverage mask is established and source 2022 chinstrap coordinates were never accessed.")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    result={"status":"HOLD_NO_ORIGINAL_UAV_ROWS","nest_coordinate_rows_opened":0}
    try:
        audit_dictionary("sources/bas_zavodovski_layer_descriptions_v1.csv")
        with tempfile.TemporaryDirectory(prefix="zavodovski-2020-uav21-") as td:
            with requests.Session() as sess:
                direct_paths,h_direct=download_layers(sess,Path(td)/"baseline")
                original_2011,h_original=fetch_lynch(sess,Path(td))
                coastline,coast_shapes,h_coast=fetch_coastline(sess,Path(td)/"coastline")
                uav_download=[authenticated_source_csv(sess,name) for name in UAV_FILES]
            historic,_=original_three_categories(original_2011)
            cores,control,direct,allmapped,support=source_baseline_layers(direct_paths,historic)
            label_pairs=(("Macaroni",uav_download[0]),("Mixed_source_ambiguous",uav_download[1]))
            points_by_class,qa={},{}
            src_hashes={}
            for label,(rows,sha,bytes_len) in label_pairs:
                points,detail=transform_nests(rows)
                qa[label]={**detail,"source_csv_bytes":bytes_len,
                           "source_file_label":UAV_FILES[0 if label=="Macaroni" else 1]}
                points_by_class[label]=points
                src_hashes[UAV_FILES[0 if label=="Macaroni" else 1]]=sha
            result["nest_coordinate_rows_opened"]=sum(len(x) for x in points_by_class.values())
            result.update(summarize(points_by_class,qa,cores,control,direct,allmapped,coastline))
            result["sha256_original_sources"]={**h_direct,**h_original,**h_coast,**src_hashes}
            result["coastline_shape_count"]=coast_shapes
            result["original_Maca_2020_rows_read"]=len(points_by_class["Macaroni"])
            result["original_MIXED_2020_rows_read"]=len(points_by_class["Mixed_source_ambiguous"])
            result["original_2022_Chinstrap_rows_read"]=0
    except Exception as exc:
        result["status"]="HOLD_SOURCE_COORDINATE_OR_GEOMETRY"
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:450]
    Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    short={k:v for k,v in result.items() if k!="sha256_original_sources"}
    print(json.dumps(short,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
