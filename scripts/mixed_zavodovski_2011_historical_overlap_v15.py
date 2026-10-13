"""Quantify 2011 historical MIXED labels without assigning them to one species.

The earlier binary-only historical redigitization approach was STOPPED due to
CHPE/MCPE/MIXED labels. This is an exploratory measurement ambiguity test,
not evidence of individual settlement or competition.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile

import requests
import shapefile
from shapely.geometry import shape
from shapely.ops import unary_union
from pyproj import CRS

from compare_zavodovski_lynch2011_digitizations_v13 import fetch_lynch
from reproduce_zavodovski_direct_image_overlap_v10 import (
    audit_dictionary, download_layers, read_geometry,
)
from zavodovski_exchange_v1 import compute_exchange

LABELS = ("CHPE", "MCPE", "MIXED")
COUNTS = {"CHPE": 442, "MCPE": 18, "MIXED": 46}


def original_three_categories(path):
    crs = CRS.from_wkt(path.with_suffix(".prj").read_text(encoding="utf-8"))
    if crs.to_epsg() != 32726 and not crs.equals(CRS.from_epsg(32726)):
        raise ValueError("GEOMETRY_STOP original CRS not EPSG:32726")
    r = shapefile.Reader(str(path))
    fields = [v[0].strip().lower() for v in r.fields[1:]]
    if fields != ["species", "area"]:
        raise ValueError("SOURCE_STOP changed original DBF fields")
    labels = [str(v[0]).strip().upper() for v in r.records()]
    if dict(Counter(labels)) != COUNTS:
        raise ValueError(f"SOURCE_STOP original source category counts differ: {dict(Counter(labels))}")
    geoms = {k: [] for k in LABELS}
    measured = Counter()
    for s, record in zip(r.shapes(), r.records()):
        cat = str(record[0]).strip().upper()
        g = shape(s.__geo_interface__)
        if g.is_empty or not g.is_valid or g.geom_type not in ("Polygon", "MultiPolygon"):
            raise ValueError(f"GEOMETRY_STOP original historic polygon invalid for {cat}")
        geoms[cat].append(g)
        measured[cat] += g.area
    unions = {label: unary_union(parts) for label, parts in geoms.items()}
    if any(not g.is_valid for g in unions.values()):
        raise ValueError("GEOMETRY_STOP invalid original category aggregation")
    return unions, {k: round(measured[k], 3) for k in LABELS}


def mixed_overlay(direct, historical):
    c0, c1 = direct[2011,"chinstrap"], direct[2016,"chinstrap"]
    m0, m1 = direct[2011,"macaroni"], direct[2016,"macaroni"]
    cloud = unary_union([direct[2011,"cloud"], direct[2016,"cloud"]])
    base = unary_union([c0, c1, m0, m1]).difference(cloud)
    if base.is_empty or not base.is_valid:
        raise ValueError("GEOMETRY_STOP empty original-image common support")
    old = compute_exchange(c0,c1,m0,m1,base)
    mac_gain = m1.intersection(base).difference(m0.intersection(base))
    chin_lost = c0.intersection(base).difference(c1.intersection(base))
    exchange = mac_gain.intersection(chin_lost)
    hist = {label: geom.intersection(base) for label, geom in historical.items()}
    overlap_classes = {
        a+"__"+b: round(hist[a].intersection(hist[b]).area,3)
        for i,a in enumerate(LABELS) for b in LABELS[i+1:]
    }
    return {
        "status": "HISTORIC_MIXED_HABITAT_OVERLAY_DESCRIPTIVE_ONLY",
        "years": [2011,2016],
        "direct_original_E": old["exchange_fraction_of_mac_gain"],
        "direct_original_F": old["reciprocal_exchange_fraction_of_chin_loss"],
        "mac_gain_m2": round(mac_gain.area,3),
        "chin_lost_m2": round(chin_lost.area,3),
        "mac_gain_on_chin_lost_m2": round(exchange.area,3),
        "historic_category_area_within_support_m2": {k:round(v.area,3) for k,v in hist.items()},
        "historic_category_pairwise_overlap_m2": overlap_classes,
        "mac_gain_on_historic_mixed_m2": round(mac_gain.intersection(hist["MIXED"]).area,3),
        "mac_gain_on_historic_mixed_fraction": round(mac_gain.intersection(hist["MIXED"]).area/mac_gain.area,6) if mac_gain.area else None,
        "apparent_C_to_M_overlap_on_historic_mixed_m2": round(exchange.intersection(hist["MIXED"]).area,3),
        "apparent_C_to_M_overlap_on_historic_mixed_fraction": round(exchange.intersection(hist["MIXED"]).area/exchange.area,6) if exchange.area else None,
        "mac_gain_on_historic_categories_m2": {label:round(mac_gain.intersection(geom).area,3) for label,geom in hist.items()},
        "note": "Original MIXED is a co-occurring subcolony patch, not a guarantee both species used every sub-location. Mixed cannot be divided into pure-species colonizations."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    receipt={"status":"HOLD","historic_shape_rows_opened":0}
    try:
        audit_dictionary("sources/bas_zavodovski_layer_descriptions_v1.csv")
        with tempfile.TemporaryDirectory(prefix="zav15-") as tmp:
            with requests.Session() as session:
                paths,_=download_layers(session,Path(tmp)/"recent")
                historical_path,historical_hashes=fetch_lynch(session,Path(tmp))
            historic,geom_areas=original_three_categories(historical_path)
            receipt["historic_shape_rows_opened"]=506
            direct={}
            for (year,name),path in paths.items():
                if year in (2011,2016):
                    direct[year,name.split("_")[0]],_=read_geometry(path,cloud=name.startswith("cloud_cover"))
            receipt.update(mixed_overlay(direct,historic))
            receipt["historical_category_geometric_summed_area_m2"]=geom_areas
            receipt["historical_sha256"]=historical_hashes
    except Exception as e:
        receipt["status"]="HOLD_SOURCE_OR_GEOMETRY_GATE"
        receipt["error"]=f"{type(e).__name__}: {str(e)[:350]}"
    Path(args.out).write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if k!="historical_sha256"}))
    if receipt["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
