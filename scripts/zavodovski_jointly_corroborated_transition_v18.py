"""V18: jointly corroborated historic chinstrap-to-macaroni map change.

Exploratory DESCRIPTIVE polygons; both 2011 maps use the SAME satellite scene.
2011 historic MIXED never allocated to a species. The 2011/2016 cloud
masks and source-date gates are reused from V10. No ecological causal claims.
"""
import argparse
import json
import math
from pathlib import Path
import tempfile

import requests
from shapely.ops import unary_union

from reproduce_zavodovski_direct_image_overlap_v10 import (
    audit_dictionary, download_layers, read_geometry,
)
from compare_zavodovski_lynch2011_digitizations_v13 import fetch_lynch
from mixed_zavodovski_2011_historical_overlap_v15 import original_three_categories


EXPECTED_2011_DBFSHA = "3445766f286604431a48f6d3a8d10f91cc91806560a5eccc2307b68e34193053"
SHRINK_METERS = (0, 1, 2, 5)


def ratio(n, d):
    return round(n / d, 6) if d > 0 else None


def checked(geom, label):
    if geom is None or not geom.is_valid:
        raise ValueError(f"GEOMETRY_STOP invalid {label}")
    return geom


def clean_support(direct, historic):
    required = ((2011, "chinstrap"), (2011, "macaroni"), (2011, "cloud"),
                (2016, "chinstrap"), (2016, "macaroni"), (2016, "cloud"))
    for k in required:
        if k not in direct:
            raise ValueError(f"SOURCE_STOP missing original-dated input {k}")
        checked(direct[k], str(k))
    for key in ("CHPE", "MCPE", "MIXED"):
        if key not in historic:
            raise ValueError(f"SOURCE_STOP missing historic label {key}")
        checked(historic[key], key)
    c0, m0 = direct[2011, "chinstrap"], direct[2011, "macaroni"]
    c1, m1 = direct[2016, "chinstrap"], direct[2016, "macaroni"]
    hc, hm, hx = (historic[x] for x in ("CHPE", "MCPE", "MIXED"))
    cloud = checked(unary_union([direct[2011,"cloud"], direct[2016,"cloud"]]), "cloud union")
    support = checked(unary_union([c0, m0, c1, m1, hc, hm, hx]).difference(cloud), "cloud-free support")
    if support.is_empty:
        raise ValueError("GEOMETRY_STOP empty cloud-free support")
    return support, cloud


def evaluate(direct, historic, expected_v10_E=0.669617):
    support, cloud = clean_support(direct, historic)
    c0, m0 = (direct[2011,k].intersection(support) for k in ("chinstrap", "macaroni"))
    c1, m1 = (direct[2016,k].intersection(support) for k in ("chinstrap", "macaroni"))
    hc, hm, hx = (historic[k].intersection(support) for k in ("CHPE", "MCPE", "MIXED"))
    gain = checked(m1.difference(m0), "M gain")
    loss = checked(c0.difference(c1), "C loss")
    x = checked(gain.intersection(loss), "C loss and M gain")
    if gain.is_empty or loss.is_empty or x.is_empty:
        raise ValueError("GEOMETRY_STOP no informative baseline transition")
    if abs(ratio(x.area, gain.area) - expected_v10_E) > 0.003:
        raise ValueError("REPRODUCIBILITY_STOP direct 2011-2016 E unexpectedly differs from V10")

    # Historical categories are spatially exclusive here, despite historic
    # polygon overlap, by assigning mixed first and Mac-only second.
    cats = {
        "A_historic_MIXED": x.intersection(hx),
        "B_historic_MCPE_outside_MIXED": x.intersection(hm.difference(hx)),
        "C_jointly_CHPE_confirmed": x.intersection(hc.difference(unary_union([hm, hx]))),
        "D_not_in_historic_map": x.difference(unary_union([hc, hm, hx])),
    }
    for key, geom in cats.items():
        checked(geom, key)
    total = sum(g.area for g in cats.values())
    tol = max(1e-6, 1e-8 * x.area)
    if abs(total - x.area) > tol:
        raise ValueError(f"PARTITION_STOP {total} != {x.area}")
    for i,(name_i, geom_i) in enumerate(cats.items()):
        for name_j,geom_j in list(cats.items())[i+1:]:
            if geom_i.intersection(geom_j).area > tol:
                raise ValueError(f"PARTITION_STOP categories overlap: {name_i} {name_j}")

    strong = cats["C_jointly_CHPE_confirmed"]
    buffers = []
    for meters in SHRINK_METERS:
        # Erode confirmed old chinstrap and new macaroni occupancy;
        # expand prior macaroni or mixed and later chinstrap exclusions.
        inner = c0.buffer(-meters).intersection(hc.buffer(-meters))
        inner = inner.intersection(m1.buffer(-meters)).intersection(support)
        blocked = unary_union([c1.buffer(meters), m0.buffer(meters),
                               hm.buffer(meters), hx.buffer(meters),
                               cloud.buffer(meters)])
        core = checked(inner.difference(blocked), f"strict interior {meters}")
        if core.difference(strong).area > tol:
            raise ValueError("GEOMETRY_STOP buffered interior not subset of unbuffered concordant map")
        buffers.append({
            "margin_m": meters,
            "corroborated_map_area_m2": round(core.area, 6),
            "fraction_of_fixed_M_gain": ratio(core.area, gain.area),
            "fraction_of_fixed_C_loss_M_gain_overlap": ratio(core.area, x.area),
        })
    if abs(buffers[0]["corroborated_map_area_m2"] - strong.area) > tol:
        raise ValueError("REPRODUCIBILITY_STOP zero-meter core disagrees")

    return {
        "status": "V18_JOINTLY_CORROBORATED_MAP_CHANGE_NOT_CONFIRMED_SETTLEMENT",
        "classification": "POST_OUTCOME_EXPLORATORY_SAME_SCENE_DIGITIZATION_TEST",
        "dates": ["2011-01-08", "2016-01-09"],
        "study": "Zavodovski Island, chinstrap and macaroni mapped breeding polygons",
        "source_doi": "10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308",
        "reference_V10_E": 0.669617,
        "common_cloud_free_support_m2": round(support.area, 6),
        "cloud_excluded_from_union_map_footprint_m2": round(
            unary_union([direct[k] for k in ((2011,"chinstrap"), (2011,"macaroni"),
                                                  (2016,"chinstrap"), (2016,"macaroni"))]).intersection(cloud).area, 6),
        "mapped_M_gain_m2": round(gain.area, 6),
        "mapped_C_loss_m2": round(loss.area, 6),
        "mapped_co_location_X_m2": round(x.area, 6),
        "jointly_corroborated_T_m2": round(strong.area, 6),
        "T_fraction_of_M_gain": ratio(strong.area, gain.area),
        "T_fraction_of_co_location_X": ratio(strong.area, x.area),
        "T_fraction_of_C_loss": ratio(strong.area, loss.area),
        "exclusive_historic_category_partition_of_X": {
            key: {"area_m2": round(geom.area, 6), "fraction_of_X": ratio(geom.area, x.area)}
            for key,geom in cats.items()
        },
        "historical_codes": {"CHPE":442,"MCPE":18,"MIXED":46},
        "geometric_interior_sensitivity": buffers,
        "interpretation_limit": (
            "Concordant SAME-SCENE mapped pure chinstrap baseline; true maca absence, "
            "2016 settlement, within-interval temporal order, bird identities, effective "
            "competition, substrate preference and coastal coverage are NOT observed."
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = {"status":"HOLD_NOT_RUN", "historic_2011_polygon_rows_opened":0}
    try:
        audit_dictionary("sources/bas_zavodovski_layer_descriptions_v1.csv")
        with tempfile.TemporaryDirectory(prefix="zavodovski-v18-") as tmp:
            with requests.Session() as session:
                paths, hashes = download_layers(session, Path(tmp)/"direct")
                historic_path, hashes_old = fetch_lynch(session, Path(tmp))
            dbf_key = "mac_and_chinstrap_colony_boundaries_2011.dbf"
            if hashes_old.get(dbf_key) != EXPECTED_2011_DBFSHA:
                raise ValueError("SOURCE_STOP independent historic 2011 DBF SHA drift")
            historic, _ = original_three_categories(historic_path)
            result["historic_2011_polygon_rows_opened"] = 506
            direct = {}
            for (year,name), path in paths.items():
                if year not in (2011,2016):
                    continue
                geom,_ = read_geometry(path,cloud=name.startswith("cloud_cover"))
                direct[year,name.split("_")[0]] = geom
            result.update(evaluate(direct, historic))
            result["original_source_sha256"] = {**hashes, **hashes_old}
    except Exception as e:
        result["status"] = "HOLD_SOURCE_GEOMETRY_OR_REPRODUCIBILITY"
        result["error"] = f"{type(e).__name__}: {str(e)[:500]}"
    Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    safe={key:value for key,value in result.items() if key!="original_source_sha256"}
    print(json.dumps(safe,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
