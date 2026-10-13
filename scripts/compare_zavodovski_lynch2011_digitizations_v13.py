"""2026 BAS direct-2011 versus original Lynch 2011 polygon redigitization.

Post-outcome exploratory source discrepancy audit. Labels fixed by original
public data dictionary BEFORE reading original DBF biological rows.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import requests
import shapefile
from pyproj import CRS
from shapely.geometry import shape
from shapely.ops import unary_union

from reproduce_zavodovski_direct_image_overlap_v10 import (
    SUFFIXES, audit_dictionary, manifest_rows, canonical_file_url,
    secure_request, download_layers, read_geometry,
)
from zavodovski_exchange_v1 import compute_exchange

ORIGINAL = "mac_and_chinstrap_colony_boundaries_2011"
ALLOWED_LABELS = {"CPE": "chinstrap", "MPE": "macaroni"}


def fetch_lynch(session, directory):
    available = {r["name"]: r for r in manifest_rows(session, 2011)}
    hashes = {}
    for suffix in SUFFIXES:
        name = ORIGINAL + suffix
        if name not in available:
            raise ValueError(f"SOURCE_STOP missing original Lynch file {name}")
        content = secure_request(session, canonical_file_url(available[name]["url"]))
        if not content:
            raise ValueError("SOURCE_STOP empty original Lynch file")
        dest = directory / name
        dest.write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    return directory / (ORIGINAL + ".shp"), hashes


def split_lynch_by_species(path):
    proj = CRS.from_wkt(path.with_suffix(".prj").read_text(encoding="utf-8"))
    if proj.to_epsg() != 32726 and not proj.equals(CRS.from_epsg(32726)):
        raise ValueError("SOURCE_STOP original 2011 CRS differs from EPSG:32726")
    reader = shapefile.Reader(str(path))
    fields = [f[0].strip().lower() for f in reader.fields[1:]]
    if fields != ["species", "area"]:
        raise ValueError(f"SOURCE_STOP unexpected original DBF schema {fields}")
    names = [str(rec[0]).strip().upper() for rec in reader.records()]
    unexpected = set(names) - set(ALLOWED_LABELS)
    if unexpected:
        raise ValueError(f"LABEL_STOP non-CPE/MPE species codes: {sorted(unexpected)[:20]}")
    geoms = {"chinstrap": [], "macaroni": []}
    for shp, label in zip(reader.shapes(), names):
        geom = shape(shp.__geo_interface__)
        if geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon", "MultiPolygon"):
            raise ValueError(f"GEOMETRY_STOP invalid Lynch species polygon {label}")
        geoms[ALLOWED_LABELS[label]].append(geom)
    if not all(geoms.values()):
        raise ValueError("SOURCE_STOP zero historical polygons for one species")
    aggregates = {species: unary_union(items) for species, items in geoms.items()}
    if any(not x.is_valid for x in aggregates.values()):
        raise ValueError("GEOMETRY_STOP invalid historical species union")
    return aggregates, {key: len(value) for key, value in geoms.items()}


def jaccard(a, b):
    union = a.union(b)
    return None if union.area == 0 else round(a.intersection(b).area / union.area, 6)


def comparison(direct, historical):
    # The 2011/2016 cloud mask and evaluation frame remain fixed across variants.
    c0, m0 = direct[2011, "chinstrap"], direct[2011, "macaroni"]
    c1, m1 = direct[2016, "chinstrap"], direct[2016, "macaroni"]
    cloud = unary_union([direct[2011, "cloud"], direct[2016, "cloud"]])
    support = unary_union([c0, m0, c1, m1,
                           historical["chinstrap"], historical["macaroni"]]).difference(cloud)
    if support.is_empty or not support.is_valid:
        raise ValueError("GEOMETRY_STOP no shared observed support")
    old = compute_exchange(c0, c1, m0, m1, support)
    alt = compute_exchange(historical["chinstrap"], c1,
                           historical["macaroni"], m1, support)
    jc = jaccard(c0.intersection(support), historical["chinstrap"].intersection(support))
    jm = jaccard(m0.intersection(support), historical["macaroni"].intersection(support))
    return {"status": "EXPLORATORY_SAME_IMAGE_INDEPENDENT_DIGITIZATION",
            "source_identity": "Lynch et al. 2016 independent drawing of same Jan 2011 satellite scene",
            "common_cloud_free_support_m2": round(support.area, 3),
            "Jaccard_2011_chinstrap": jc,
            "Jaccard_2011_macaroni": jm,
            "direct_2011_E": old["exchange_fraction_of_mac_gain"],
            "lynch_2011_E": alt["exchange_fraction_of_mac_gain"],
            "direct_2011_F": old["reciprocal_exchange_fraction_of_chin_loss"],
            "lynch_2011_F": alt["reciprocal_exchange_fraction_of_chin_loss"],
            "direct_2011_gain_m2": old["mac_gained_area_m2"],
            "lynch_2011_gain_m2": alt["mac_gained_area_m2"],
            "note": "No independent dated image, competition, dispersal or recruitment evidence."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = {"status": "HOLD_NO_ORIGINAL_GEOMETRY_OPEN", "historic_2011_rows_opened": 0}
    try:
        audit_dictionary("sources/bas_zavodovski_layer_descriptions_v1.csv")
        with tempfile.TemporaryDirectory(prefix="zavodovski-lynch13-") as tmp:
            with requests.Session() as session:
                direct_paths, hashes = download_layers(session, Path(tmp) / "updated")
                path, historic_hashes = fetch_lynch(session, Path(tmp))
            original, n = split_lynch_by_species(path)
            result["historic_2011_rows_opened"] = sum(n.values())
            updated = {}
            for (year, name), file in direct_paths.items():
                if year in (2011, 2016):
                    geom, _ = read_geometry(file, cloud=name.startswith("cloud_cover"))
                    updated[year, name.split("_")[0]] = geom
            result.update(comparison(updated, original))
            result["historic_species_record_count"] = n
            result["historic_sha256"] = historic_hashes
    except Exception as exc:
        result["status"] = "HOLD_SOURCE_LABEL_OR_GEOMETRY_GATE"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:500]}"
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "historic_sha256"}))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
