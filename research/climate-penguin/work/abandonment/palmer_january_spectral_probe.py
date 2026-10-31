#!/usr/bin/env python3
"""Exploratory two-date *spectral* probe after independent, QA-only scene choice.

The QA-only original source check selected January 5, 2007 versus January 15,
2008 before examining red/NIR data. These are fixed point-neighborhood samples
near MAPPPD island coordinates, NOT historically georeferenced nesting plots.
NDVI difference must NOT be interpreted as plant greening or a penguin effect.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("palmer_jan_qa", HERE / "palmer_january_common_qa.py")
january = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(january)

SOURCE_RUN = "https://github.com/zuizui0223/mina/actions/runs/40860491682"
SOURCE_ARTIFACT_SHA256 = "bb386e7ca78d735b7395f5c99a617c7d3462da02258b70792b77156a8f791c62"
PAIR = {
    2007: "LE07_L2SR_218106_20070105_02_T2",
    2008: "LE07_L2SR_219105_20080115_02_T2",
}
# Frozen from the QA-only source receipt, not selected after seeing reflectance.
CLEAR_INDICES = {
    "LITC": [9, 11, 15, 16, 20, 22, 23],
    "TORG": [9, 12, 13],
}
FIELDS = [
    "site_id", "grid_position", "offset_x_m", "offset_y_m",
    "before_scene", "after_scene", "before_date", "after_date",
    "before_red_dn", "before_nir_dn", "after_red_dn", "after_nir_dn",
    "before_red_sr", "before_nir_sr", "after_red_sr", "after_nir_sr",
    "ndvi_2007", "ndvi_2008", "delta_ndvi", "radsat_before", "radsat_after",
    "eligible", "reason",
]


def surface_reflectance(dn: int | None) -> float | None:
    # USGS Landsat Collection 2 Level 2, reflectance, not TOA.
    if dn is None or not (7273 <= int(dn) <= 43636):
        return None
    return float(dn) * 0.0000275 - 0.2


def spectral_index(red: float | None, nir: float | None) -> float | None:
    if red is None or nir is None or red <= 0 or nir <= 0 or red + nir < 0.01:
        return None
    return (nir - red) / (nir + red)


def fixed_points(loc, ds):
    from pyproj import Transformer
    polar = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    native = Transformer.from_crs("EPSG:3031", ds.crs, always_xy=True)
    x,y = polar.transform(loc["longitude"], loc["latitude"])
    return [native.transform(x+dx,y+dy) for dx,dy in january.OFFSETS_M]


def sample_band(ds, loc) -> list[int | None]:
    points = fixed_points(loc, ds)
    out = []
    for a in ds.sample(points, masked=True):
        mask = getattr(a, "mask", False)
        if bool(mask.any()) if hasattr(mask, "any") else bool(mask):
            out.append(None)
        else:
            out.append(int(a[0]))
    assert len(out) == 25
    return out


def load_scene(year: int, source_item: dict, site: str) -> dict:
    import planetary_computer
    import rasterio
    feat = source_item
    asset = feat.get("assets") or {}
    for key in ("qa_pixel", "red", "nir08", "qa_radsat"):
        if key not in asset or not asset[key].get("href"):
            raise ValueError(f"missing Landsat C2 asset {key} in {feat['id']}")
    loc = january.qa.mod.SITES[site]
    def open_key(stack, key):
        return stack.enter_context(rasterio.open(planetary_computer.sign(asset[key]["href"])))
    with contextlib.ExitStack() as stack:
        qa = open_key(stack, "qa_pixel")
        red = open_key(stack, "red")
        nir = open_key(stack, "nir08")
        sat = open_key(stack, "qa_radsat")
        # Reproduce original QA-only selection without reading any NDVI to select.
        clear = [p["i"] for p in january.sample_grid(qa, loc) if p["clear"]]
        data = {
            "clear_indices": clear,
            "red": sample_band(red, loc),
            "nir": sample_band(nir, loc),
            "radsat": sample_band(sat, loc),
            "red_native_crs": str(red.crs),
            "nir_native_crs": str(nir.crs),
            "pixel_resolution_red": tuple(map(float, red.res)),
            "pixel_resolution_nir": tuple(map(float, nir.res)),
            "scene_id": feat["id"],
            "scene_date": feat["properties"]["datetime"][:10],
        }
    return data


def run(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    original = {
        yr: next((f for f in january.qa.fetch_all(yr, month=1) if f.get("id") == ref), None)
        for yr, ref in PAIR.items()
    }
    if any(x is None for x in original.values()):
        raise RuntimeError("QA-frozen selected original Landsat scene missing in live STAC")
    import rasterio
    datasets = {}
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      GDAL_HTTP_MAX_RETRY="2", GDAL_HTTP_RETRY_DELAY="1"):
        for site in CLEAR_INDICES:
            for yr in PAIR:
                datasets[(site, yr)] = load_scene(yr, original[yr], site)
    # Exact expected common QA positions fixed from the independent earlier run.
    for site, ids in CLEAR_INDICES.items():
        b = datasets[(site, 2007)]
        a = datasets[(site, 2008)]
        observed = sorted(set(b["clear_indices"]) & set(a["clear_indices"]))
        if observed != ids:
            raise RuntimeError(f"{site}: source QA common-point set changed: {observed} != {ids}")
    rows, summary = [], {}
    for site, indices in CLEAR_INDICES.items():
        b, a = datasets[(site, 2007)], datasets[(site, 2008)]
        vals = []
        for i in indices:
            br, bn, ar, an = b["red"][i], b["nir"][i], a["red"][i], a["nir"][i]
            r0,n0,r1,n1 = map(surface_reflectance, (br,bn,ar,an))
            s0,s1=b["radsat"][i],a["radsat"][i]
            # No saturation in red (band 3) or NIR (band 4) for Landsat 7.
            saturation = (s0 is None or s1 is None or
                          bool(int(s0) & ((1<<2)|(1<<3))) or
                          bool(int(s1) & ((1<<2)|(1<<3))))
            nd0,nd1=spectral_index(r0,n0),spectral_index(r1,n1)
            ok=nd0 is not None and nd1 is not None and not saturation
            diff=nd1-nd0 if ok else None
            if ok:
                vals.append(diff)
            x,y=january.OFFSETS_M[i]
            rows.append({
                "site_id":site,"grid_position":i,"offset_x_m":x,"offset_y_m":y,
                "before_scene":PAIR[2007],"after_scene":PAIR[2008],
                "before_date":b["scene_date"],"after_date":a["scene_date"],
                "before_red_dn":br,"before_nir_dn":bn,"after_red_dn":ar,"after_nir_dn":an,
                "before_red_sr":r0,"before_nir_sr":n0,"after_red_sr":r1,"after_nir_sr":n1,
                "ndvi_2007":nd0,"ndvi_2008":nd1,"delta_ndvi":diff,
                "radsat_before":s0,"radsat_after":s1,"eligible":ok,
                "reason":"" if ok else ("radsat" if saturation else "reflectance_out_of_valid_range"),
            })
        summary[site] = {
            "original_qa_common_ground_locations":len(indices),
            "radiometrically_valid_paired_ground_locations":len(vals),
            "median_delta_ndvi_exploratory":statistics.median(vals) if vals else None,
            "min_delta_ndvi":min(vals) if vals else None,
            "max_delta_ndvi":max(vals) if vals else None,
            "not_a_vegetation_effect":True,
        }
    with (out/"original_paired_spectra.csv").open("w",newline="",encoding="utf-8") as fh:
        wr=csv.DictWriter(fh,fieldnames=FIELDS)
        wr.writeheader();wr.writerows(rows)
    checks = {
        "schema_version":1,
        "status":"observational_spectral_pilot_not_vegetation_inference",
        "preselected_QA_source_run":SOURCE_RUN,
        "preselected_QA_source_artifact_sha256":SOURCE_ARTIFACT_SHA256,
        "surface_reflectance_rule":"USGS Landsat C2 L2: DN*0.0000275-0.2; valid DN 7273..43636",
        "measurement_scale":"7+3 fixed geographic point probes, not independent biological replicates",
        "original_scene_ids":PAIR,
        "same_sensor":"Landsat 7 ETM+",
        "source_dataset_samples":{
            f"{site}:{year}":datasets[(site,year)]["scene_date"]
            for site in CLEAR_INDICES for year in PAIR
        },
        "site_results":summary,
        "important_limitations":[
            "QA-only scene choice was post-hoc after February-March 2008 had zero support.",
            "One 2007/08 pair cannot estimate a temporal trend, event-study, or any climate effect.",
            "The 25-point site neighborhood is not a verified historical breeding footprint.",
            "Different ground-referenced positions can sample differently aligned native 30m pixels.",
            "Spectral NDVI is not validated Antarctic moss or terrestrial plant cover.",
            "No independently georeferenced never-occupied terrain or nutrient data are present.",
            "Radsat and physical SR range are filters; no atmospheric residual/BRDF correction validation.",
        ],
    }
    (out/"checks.json").write_text(json.dumps(checks,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)
    return 0


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,default=Path("palmer_jan_reflectance_pilot"))
    args=p.parse_args()
    return run(args.out)


if __name__ == "__main__":
    raise SystemExit(main())
