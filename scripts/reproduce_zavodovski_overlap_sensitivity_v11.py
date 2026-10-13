"""Exploratory positional and patch-core sensitivity for source-backed BAS GIS.

This runs *after* V10 outcome exposure. Its 8-direction offsets are NOT
biological replicates or estimates of actual registration error.
"""
import argparse
import json
import math
from pathlib import Path
import tempfile

import requests
from shapely.affinity import translate
from shapely.ops import unary_union

from reproduce_zavodovski_direct_image_overlap_v10 import (
    DATES, NAMES, audit_dictionary, download_layers, read_geometry,
)


def positional_sensitivity(mac_gain, chin_loss, valid_support, meters):
    if mac_gain.area <= 0:
        return None
    root2 = math.sqrt(2)
    direction_vectors = ((1, 0), (-1, 0), (0, 1), (0, -1),
                         (1 / root2, 1 / root2), (-1 / root2, 1 / root2),
                         (1 / root2, -1 / root2), (-1 / root2, -1 / root2))
    values = sorted(
        mac_gain.intersection(
            translate(chin_loss, xoff=meters * dx, yoff=meters * dy).intersection(valid_support)
        ).area / mac_gain.area for dx, dy in direction_vectors
    )
    return {"m": meters, "min": round(values[0], 6),
            "median": round((values[3] + values[4]) / 2, 6),
            "max": round(values[-1], 6), "n_offsets": 8}


def patch_core_sensitivity(mac_gain, chin_loss, meters):
    a = mac_gain.buffer(-meters)
    b = chin_loss.buffer(-meters)
    if a.is_empty or a.area <= 0:
        return {"m": meters, "core_E": None, "gain_core_m2": 0.0}
    return {"m": meters, "core_E": round(a.intersection(b).area / a.area, 6),
            "gain_core_m2": round(a.area, 3)}


def metrics(geoms):
    out = {"status": "POST_OUTCOME_DIAGNOSTIC_ONLY", "same_year_overlap": {}, "pairs": {}}
    for year in DATES:
        c, m, cloud = (geoms[year, k] for k in ("chinstrap", "macaroni", "cloud"))
        c = c.difference(cloud)
        m = m.difference(cloud)
        out["same_year_overlap"][str(year)] = {
            "C_and_M_m2": round(c.intersection(m).area, 3),
            "M_m2": round(m.area, 3),
            "C_and_M_fraction_of_M": (round(c.intersection(m).area / m.area, 6)
                                      if m.area else None)
        }
    for early, late in ((2011, 2016), (2016, 2025)):
        c0, c1 = geoms[early, "chinstrap"], geoms[late, "chinstrap"]
        m0, m1 = geoms[early, "macaroni"], geoms[late, "macaroni"]
        cloud = unary_union([geoms[early, "cloud"], geoms[late, "cloud"]])
        valid_support = unary_union([c0, c1, m0, m1]).difference(cloud)
        if valid_support.is_empty or not valid_support.is_valid:
            raise ValueError("GEOMETRY_STOP invalid common visible support")
        cs = c0.intersection(valid_support).difference(c1.intersection(valid_support))
        mg = m1.intersection(valid_support).difference(m0.intersection(valid_support))
        if mg.is_empty or mg.area <= 0:
            raise ValueError("GEOMETRY_STOP zero measurable macaroni gain")
        out["pairs"][f"{early}_{late}"] = {
            "baseline_E": round(mg.intersection(cs).area / mg.area, 6),
            "baseline_mac_gain_m2": round(mg.area, 3),
            "baseline_chin_loss_m2": round(cs.area, 3),
            "positional_shifts": [positional_sensitivity(mg, cs, valid_support, d)
                                  for d in (2, 5, 10, 20)],
            "patch_core": [patch_core_sensitivity(mg, cs, d) for d in (1, 2, 5, 10)]
        }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    a = p.parse_args()
    result = {"status": "HOLD_NOT_RUN", "original_biological_polygons_opened": 0}
    try:
        audit_dictionary("sources/bas_zavodovski_layer_descriptions_v1.csv")
        with tempfile.TemporaryDirectory(prefix="zavodovski-v11-") as tmp:
            with requests.Session() as session:
                paths, hashes = download_layers(session, Path(tmp))
            geoms = {}
            for (year, name), path in paths.items():
                geom, _ = read_geometry(path, cloud=name.startswith("cloud_cover"))
                geoms[year, name.split("_")[0]] = geom
            result.update(metrics(geoms))
            result["original_biological_polygons_opened"] = 6
            result["file_sha256"] = hashes
    except Exception as exc:
        result["status"] = "HOLD_SOURCE_OR_GEOMETRY_GATE_FAILED"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
    Path(a.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "file_sha256"}))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
