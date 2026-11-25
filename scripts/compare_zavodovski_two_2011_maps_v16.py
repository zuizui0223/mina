"""Same-scene 2011 independent digitization sensitivity (V16, exploratory).

Compares revised 2011 single-species polygons with the original Lynch
2011 CHPE / MCPE / MIXED source, keeping MIXED ambiguous and the cloud-free
2011--2016 support fixed for BOTH alternate-baseline estimates.

Outcomes are maps, not the biological founding of penguins.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import requests
from shapely.ops import unary_union

from reproduce_zavodovski_direct_image_overlap_v10 import (
    audit_dictionary, download_layers, read_geometry
)
from compare_zavodovski_lynch2011_digitizations_v13 import fetch_lynch
from mixed_zavodovski_2011_historical_overlap_v15 import original_three_categories
from zavodovski_exchange_v1 import compute_exchange


def safe_ratio(num, denom):
    return round(num / denom, 6) if denom > 0 else None


def agreement(a, b, support):
    first = a.intersection(support)
    second = b.intersection(support)
    inter = first.intersection(second).area
    un = first.union(second).area
    return {
        "jaccard": safe_ratio(inter, un),
        "intersection_m2": round(inter, 3),
        "union_m2": round(un, 3),
        "revised_area_m2": round(first.area, 3),
        "historic_area_m2": round(second.area, 3),
        "fraction_revised_in_historic": safe_ratio(inter, first.area),
        "fraction_historic_in_revised": safe_ratio(inter, second.area),
    }


def audit_maps(direct, historic):
    for cat in ("CHPE", "MCPE", "MIXED"):
        if cat not in historic or historic[cat].is_empty or not historic[cat].is_valid:
            raise ValueError("GEOMETRY_STOP historical polygon category invalid: " + cat)
    for year in (2011, 2016):
        for cat in ("chinstrap", "macaroni", "cloud"):
            if (year, cat) not in direct or not direct[year, cat].is_valid:
                raise ValueError("GEOMETRY_STOP original-date dataset missing/invalid")

    c0 = direct[2011, "chinstrap"]
    m0 = direct[2011, "macaroni"]
    c1 = direct[2016, "chinstrap"]
    m1 = direct[2016, "macaroni"]
    h_c, h_m, h_mix = (historic[k] for k in ("CHPE", "MCPE", "MIXED"))
    clouds = unary_union([direct[2011,"cloud"], direct[2016,"cloud"]])

    # Identical geographical evaluation frame for alternative digitizations.
    support = unary_union([c0, m0, c1, m1, h_c, h_m, h_mix]).difference(clouds)
    if support.is_empty or not support.is_valid:
        raise ValueError("GEOMETRY_STOP no valid joint cloud-free support")
    historic_disputed = h_c.intersection(h_m)
    ambiguous = unary_union([h_mix, historic_disputed])
    support_unambiguous = support.difference(ambiguous)
    if support_unambiguous.is_empty or not support_unambiguous.is_valid:
        raise ValueError("GEOMETRY_STOP no historical unmixed support")

    revised = compute_exchange(c0, c1, m0, m1, support)
    revised_nomix = compute_exchange(c0, c1, m0, m1, support_unambiguous)
    historical_nomix = compute_exchange(h_c, c1, h_m, m1, support_unambiguous)

    gain = m1.intersection(support).difference(m0.intersection(support))
    loss = c0.intersection(support).difference(c1.intersection(support))
    apparent_exchange = gain.intersection(loss)
    historical_m_present_or_mixed = h_m.union(h_mix)
    gaining_outside_old_m = gain.difference(historical_m_present_or_mixed)
    exchange_outside_old_m = apparent_exchange.difference(historical_m_present_or_mixed)

    mapping = {"chinstrap": h_c, "macaroni": h_m}
    return {
        "status": "V16_EXPLORATORY_SAME_SCENE_DIGITIZATION_SENSITIVITY",
        "source_doi": "10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308",
        "image_dates": ["2011-01-08", "2016-01-09"],
        "historical_mixed_not_assigned_to_a_species": True,
        "area_of_all_support_m2": round(support.area, 3),
        "historic_mixed_within_support_m2": round(h_mix.intersection(support).area, 3),
        "historic_pure_code_intersection_m2": round(historic_disputed.intersection(support).area, 3),
        "area_of_unambiguous_support_m2": round(support_unambiguous.area, 3),
        "same_scene_2011_per_species_agreement_excluding_mixed": {
            species: agreement(direct[2011, species], historical, support_unambiguous)
            for species, historical in mapping.items()
        },
        "revised_2011_by_historic_class_within_common_cloud_free_support_m2": {
            species: {cat: round(
                direct[2011, species].intersection(support).intersection(historic[cat]).area, 3)
                for cat in ("CHPE", "MCPE", "MIXED")
            }
            for species in ("chinstrap", "macaroni")
        },
        "same_support_alternative_2011_digitization": {
            "all_support_revised_E_check": revised["exchange_fraction_of_mac_gain"],
            "all_support_revised_F_check": revised["reciprocal_exchange_fraction_of_chin_loss"],
            "nonmixed_support_revised_2011": {
                "E": revised_nomix["exchange_fraction_of_mac_gain"],
                "F": revised_nomix["reciprocal_exchange_fraction_of_chin_loss"],
                "mac_gain_m2": revised_nomix["mac_gained_area_m2"],
                "chin_loss_m2": revised_nomix["chin_lost_area_m2"],
                "apparent_exchange_m2": revised_nomix["mac_gain_on_chin_lost_m2"],
            },
            "nonmixed_support_historic_2011": {
                "E": historical_nomix["exchange_fraction_of_mac_gain"],
                "F": historical_nomix["reciprocal_exchange_fraction_of_chin_loss"],
                "mac_gain_m2": historical_nomix["mac_gained_area_m2"],
                "chin_loss_m2": historical_nomix["chin_lost_area_m2"],
                "apparent_exchange_m2": historical_nomix["mac_gain_on_chin_lost_m2"],
            },
        },
        "apparent_gain_outside_historic_definite_or_possible_macaroni": {
            "gain_total_m2": round(gain.area, 3),
            "gain_outside_historic_MCPE_and_MIXED_m2": round(gaining_outside_old_m.area, 3),
            "fraction_gain_outside_historic_MCPE_and_MIXED": safe_ratio(gaining_outside_old_m.area, gain.area),
            "direct_exchange_total_m2": round(apparent_exchange.area, 3),
            "direct_exchange_outside_historic_MCPE_and_MIXED_m2": round(exchange_outside_old_m.area, 3),
            "fraction_exchange_outside_historic_MCPE_and_MIXED": safe_ratio(exchange_outside_old_m.area, apparent_exchange.area),
        },
        "interpretation": (
            "Independent digitizer comparison of the SAME Jan 2011 scene, "
            "not an independent observation year. Historical MIXED patches indicate "
            "sub-colony co-occurrence somewhere, not every square meter. "
            "No movement, colonization, replacement causality or competition demonstrated."
        )
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()
    result = {"status": "HOLD", "historical_2011_geometry_rows_opened": 0}
    try:
        audit_dictionary("sources/bas_zavodovski_layer_descriptions_v1.csv")
        with tempfile.TemporaryDirectory(prefix="zav16-two-maps-") as tmp:
            with requests.Session() as session:
                paths, download_hashes = download_layers(session, Path(tmp)/"updated")
                historic_path, historic_hashes = fetch_lynch(session, Path(tmp))
            history, counts = original_three_categories(historic_path)
            result["historical_2011_geometry_rows_opened"] = 506
            direct = {}
            for (year, name), path in paths.items():
                if year in (2011, 2016):
                    obj, _ = read_geometry(path, cloud=name.startswith("cloud_cover"))
                    direct[year, name.split("_")[0]] = obj
            result.update(audit_maps(direct, history))
            result["2011_historic_sum_polygon_areas_by_species_m2"] = counts
            result["original_source_sha256"] = {**download_hashes, **historic_hashes}
    except Exception as exc:
        result["status"] = "HOLD_SOURCE_OR_GEOMETRY"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:600]}"
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="original_source_sha256"}))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
