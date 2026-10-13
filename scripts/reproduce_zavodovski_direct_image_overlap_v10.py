"""Source-gated Zavodovski matched-satellite GIS overlay.

Source: Ratcliffe et al. 2026 BAS / UK PDC doi:10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308.
NO replacement polygons, 2020--22 composites, 2023 drone/2025 mixed layers, or
commercial satellite images are loaded. Results are descriptive, not causal.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
from urllib.parse import parse_qs, quote, urlparse, urlunparse

import requests

PARENT = "7220dc6b-2f52-4160-a6c0-e57c50963308"
HOST = "ramadda.data.bas.ac.uk"
FOLDERS = {
    2011: "synth:" + PARENT + ":L3NhdGVsbGl0ZS1kZXJpdmVkX2RhdGEvMjAxMQ==",
    2016: "synth:" + PARENT + ":L3NhdGVsbGl0ZS1kZXJpdmVkX2RhdGEvMjAxNg==",
    2025: "synth:" + PARENT + ":L3NhdGVsbGl0ZS1kZXJpdmVkX2RhdGEvMjAyNQ==",
}
DATES = {2011: "08/01/2011", 2016: "09/01/2016", 2025: "12/01/2025"}
SUFFIXES = (".shp", ".shx", ".dbf", ".prj", ".cpg")
NAMES = lambda year: [
    f"chinstrap_colony_boundaries_{year}",
    f"macaroni_colony_boundaries_{year}",
    f"cloud_cover_{year}",
]


def audit_dictionary(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        original = list(csv.DictReader(handle))
    if len(original) != 28:
        raise ValueError("SOURCE_STOP dictionary row count/version drift")
    for year, date in DATES.items():
        entries = {r["filename"]: r for r in original}
        for base in NAMES(year):
            if base not in entries:
                raise ValueError(f"SOURCE_STOP missing dictionary layer: {base}")
            x = entries[base]
            if x["sub-directory"] != str(year) or x["image_date"] != date:
                raise ValueError(f"SOURCE_STOP original image date mismatch {base}")
            if x["data_type"] not in ("Colony polygons", "Cloud cover polygon"):
                raise ValueError(f"SOURCE_STOP wrong object type {base}")
            if "under_cloud" in base or "2020-22" in base:
                raise ValueError("SOURCE_STOP imputed or composite layer")
    entries = {r["filename"]: r for r in original}
    for species in ("chinstrap", "macaroni"):
        if entries[f"{species}_colony_boundaries_under_cloud_2016"]["image_date"] != "04/02/2020":
            raise ValueError("SOURCE_STOP changed 2016 cloud substitution provenance")
    for species in ("chinstrap", "macaroni"):
        main = entries[f"{species}_colony_boundaries_2020-22"]
        if "2020" not in main["image_date"] or "2022" not in main["image_date"]:
            raise ValueError("SOURCE_STOP unknown composite definition")
    return original


def secure_request(session, url, limit=20_000_000):
    """Restrict live content to source host or its observed public 194.66.5.50 redirect."""
    first = urlparse(url)
    if first.scheme != "https" or first.hostname != HOST:
        raise ValueError("SOURCE_STOP noncanonical source URL")
    with session.get(url, timeout=(20, 60), stream=True, allow_redirects=True,
                     headers={"User-Agent": "mina-zavodovski-science-repro/1.0"}) as response:
        response.raise_for_status()
        final = urlparse(response.url)
        if final.scheme != "https" or final.hostname not in (HOST, "194.66.5.50"):
            raise ValueError("SOURCE_STOP disallowed redirect")
        data = bytearray()
        for chunk in response.iter_content(chunk_size=32768):
            data.extend(chunk)
            if len(data) > limit:
                raise ValueError("SOURCE_STOP file exceeds fixed byte limit")
        if b"<html" in bytes(data[:200]).lower():
            raise ValueError("SOURCE_STOP HTML rather than original file")
        return bytes(data)


def manifest_rows(session, year):
    entryid = FOLDERS[year]
    url = ("https://" + HOST + "/repository/entry/show?entryid=" +
           quote(entryid, safe="") + "&output=default.csv")
    raw = secure_request(session, url, limit=1000000).decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(raw)))
    if not rows or "url" not in rows[0] or "name" not in rows[0]:
        raise ValueError("SOURCE_STOP manifest CSV schema")
    return rows


def canonical_file_url(published):
    """Promote RAMADDA's legacy http://HOST:443 file links to HTTPS on same host."""
    x = urlparse(published)
    if x.hostname != HOST or x.path.split("/")[:4] != ["", "repository", "entry", "get"]:
        raise ValueError("SOURCE_STOP manifest contains non-BAS file")
    if x.scheme not in ("https", "http") or (x.port not in (None, 443)):
        raise ValueError("SOURCE_STOP invalid manifest link scheme or port")
    q = parse_qs(x.query)
    if len(q.get("entryid", [])) != 1 or not q["entryid"][0].startswith("synth:" + PARENT + ":"):
        raise ValueError("SOURCE_STOP missing exact source ID")
    return urlunparse(("https", HOST, x.path, "", x.query, ""))


def download_layers(session, output_dir):
    names = {}
    hashes = {}
    for year in DATES:
        rows = manifest_rows(session, year)
        available = {r["name"]: r for r in rows}
        for base in NAMES(year):
            for suffix in SUFFIXES:
                filename = base + suffix
                item = available.get(filename)
                if item is None:
                    raise ValueError(f"SOURCE_STOP missing published GIS sidecar {filename}")
                url = canonical_file_url(item["url"])
                if urlparse(url).path.rsplit("/", 1)[-1] != filename:
                    raise ValueError("SOURCE_STOP downloaded filename disagreement")
                blob = secure_request(session, url)
                if len(blob) == 0:
                    raise ValueError(f"SOURCE_STOP empty {filename}")
                if suffix in (".shp", ".shx") and blob[:4] != bytes.fromhex("0000270a"):
                    raise ValueError(f"SOURCE_STOP bad shapefile signature {filename}")
                if suffix == ".dbf" and blob[:1] not in (b"\x03", b"\x83", b"\x30"):
                    raise ValueError(f"SOURCE_STOP bad DBF signature {filename}")
                if suffix == ".prj" and b"PROJCS" not in blob.upper() and b"PROJCRS" not in blob.upper():
                    raise ValueError(f"SOURCE_STOP bad projection sidecar {filename}")
                dest = output_dir / str(year) / filename
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(blob)
                hashes[str(year) + "/" + filename] = hashlib.sha256(blob).hexdigest()
            names[year, base] = output_dir / str(year) / (base + ".shp")
    return names, hashes


def read_geometry(path, cloud=False):
    import shapefile
    from pyproj import CRS
    from shapely.geometry import GeometryCollection, shape
    from shapely.ops import unary_union

    crs_text = path.with_suffix(".prj").read_text(encoding="utf-8")
    crs = CRS.from_wkt(crs_text)
    if not crs.equals(CRS.from_epsg(32726)) and crs.to_epsg() != 32726:
        raise ValueError(f"GEOMETRY_STOP CRS not EPSG:32726: {path.name}")
    reader = shapefile.Reader(str(path))
    features = []
    for feature in reader.shapes():
        geom = shape(feature.__geo_interface__)
        if geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon", "MultiPolygon"):
            raise ValueError(f"GEOMETRY_STOP invalid polygon: {path.name}")
        features.append(geom)
    if not features:
        if cloud:
            return GeometryCollection(), 0
        raise ValueError(f"GEOMETRY_STOP no colony polygons: {path.name}")
    merged = unary_union(features)
    if not merged.is_valid:
        raise ValueError(f"GEOMETRY_STOP invalid union: {path.name}")
    bounds = merged.bounds
    if bounds[0] < 100000 or bounds[2] > 900000 or bounds[1] < 2500000 or bounds[3] > 5500000:
        raise ValueError(f"GEOMETRY_STOP implausible UTM26S bounds: {path.name}")
    return merged, len(features)


def analyze(paths):
    from shapely.ops import unary_union
    from zavodovski_exchange_v1 import compute_exchange

    geoms = {}
    n = {}
    for (year, name), path in paths.items():
        geo, count = read_geometry(path, cloud=name.startswith("cloud_cover"))
        geoms[year, name.split("_")[0]] = geo
        n[f"{year}/{name}"] = count

    out = {}
    for old, new in [(2011, 2016), (2016, 2025)]:
        # Prospective complete-common-cloud exclusion; no under-cloud substitutions.
        labels = ("chinstrap", "macaroni")
        inputs = [geoms[year, species] for year in (old, new) for species in labels]
        all_occupied = unary_union(inputs)
        cloud_union = unary_union([geoms[old, "cloud"], geoms[new, "cloud"]])
        valid_support = all_occupied.difference(cloud_union)
        if valid_support.is_empty or not valid_support.is_valid:
            raise ValueError("GEOMETRY_STOP no common clear-sky support")
        if max(valid_support.bounds[2]-valid_support.bounds[0],
               valid_support.bounds[3]-valid_support.bounds[1]) > 20000:
            raise ValueError("GEOMETRY_STOP impossible mapped colony-span")
        summary = compute_exchange(inputs[0], inputs[2], inputs[1], inputs[3], valid_support)
        summary["comparison"] = [old, new]
        summary["common_visible_support_m2"] = round(valid_support.area, 6)
        summary["excluded_cloud_in_occupied_envelope_m2"] = round(all_occupied.intersection(cloud_union).area, 6)
        summary["interpretation"] = "APPARENT_POLYGON_OVERLAY_ONLY_NO_CAUSAL_INFERENCE"
        out[f"{old}_{new}"] = summary
    return {"status": "DESCRIPTIVE_GIS_OVERLAY_SOURCE_AND_GEOMETRY_GATED",
            "source_doi": "10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308",
            "note": "Underlying survey-footprint uncertainty and image registration persist. No competition or legacy effect identified.",
            "feature_counts": n, "comparisons": out}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dictionary", default="sources/bas_zavodovski_layer_descriptions_v1.csv")
    parser.add_argument("--out", required=True)
    parser.add_argument("--source-only", action="store_true",
                        help="Download and integrity-check only, without loading polygon geometry")
    args = parser.parse_args()
    result = {"status": "HOLD_NOT_RUN", "source_doi":
              "10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308",
              "original_biological_polygons_opened": 0}
    try:
        audit_dictionary(args.dictionary)
        result["dictionary_rows"] = 28
        with tempfile.TemporaryDirectory(prefix="bas-zavodovski-") as tmp:
            with requests.Session() as session:
                paths, hashes = download_layers(session, Path(tmp))
            result["downloaded_original_shapefile_components"] = len(hashes)
            result["source_sha256"] = hashes
            result["status"] = "SOURCE_FILES_VERIFIED_NO_GEOMETRY_YET"
            if not args.source_only:
                analysis = analyze(paths)
                result.update(analysis)
                result["original_biological_polygons_opened"] = 6
    except Exception as exc:
        result["status"] = "HOLD_SOURCE_OR_GEOMETRY_GATE_FAILED"
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)[:300]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    safe = {k: v for k, v in result.items() if k != "source_sha256"}
    print(json.dumps(safe, ensure_ascii=False))
    if result["status"] == "HOLD_SOURCE_OR_GEOMETRY_GATE_FAILED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
