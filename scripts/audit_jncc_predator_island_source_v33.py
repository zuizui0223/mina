#!/usr/bin/env python3
"""V33 original RSPB/Stanbury UK-island predator source intake; no JNCC outcomes.

Read-only public publisher data. All biological JNCC counts and previous
concentration E remain unopened here. No inferred absences from blank cells.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import zipfile

import requests

RSPB_SERVICE = (
    "https://services1.arcgis.com/h1C9f6qsGKmqXsVs/arcgis/rest/"
    "services/Islands_database/FeatureServer/0"
)
SPRINGER_BASE = (
    "https://media.springernature.com/original/springer-static/esm/"
    "art%3A10.1007%2Fs10344-017-1084-7/MediaObjects/"
)
SUPPLEMENTS = {
    "ESM1": SPRINGER_BASE + "10344_2017_1084_MOESM1_ESM.xlsx",
    "ESM5": SPRINGER_BASE + "10344_2017_1084_MOESM5_ESM.xlsx",
}
DOI = "10.1007/s10344-017-1084-7"
RSPB_METADATA = (
    "https://www.arcgis.com/sharing/rest/content/items/"
    "8cf249483ca540c792aee44c3029cb0b/info/metadata/metadata.xml"
)
ALLOWED_HOSTS = {
    "media.springernature.com",
    "static-content.springer.com",
    "link.springer.com",
    "services1.arcgis.com",
}
HEADERS = {"User-Agent": "mina-jncc-v33-primary-source-audit/1.0"}
MAX_SUPP_BYTES = 6_000_000
MAX_XML_BYTES = 45_000_000
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
PREDATOR_HEADER = re.compile(
    r"rat|mink|fox|vulpes|stoat|weasel|ferret|polecat|hedgehog|feral cat|"
    r"mouse|mice|rattus|vison|norvegicus|mustela|felis|predator|"
    r"invasive|badger|rodent",
    re.I,
)


def bounded_get(url: str, max_bytes: int, params: dict | None = None) -> bytes:
    if urlparse(url).scheme != "https" or urlparse(url).hostname not in ALLOWED_HOSTS:
        raise ValueError("SOURCE_HOST_GATE: unapproved source URL")
    with requests.get(
        url, params=params, headers=HEADERS, stream=True, timeout=(15, 65),
    ) as response:
        response.raise_for_status()
        final = urlparse(response.url)
        if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
            raise ValueError("SOURCE_HOST_GATE: unapproved download redirect")
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            total += len(chunk)
            if total > max_bytes:
                raise ValueError("SOURCE_SIZE_GATE: response exceeds bounded limit")
            chunks.append(chunk)
        return b"".join(chunks)


def official_json(path: str, params: dict) -> dict:
    raw = bounded_get(RSPB_SERVICE + path, 3_000_000, params)
    obj = json.loads(raw.decode("utf-8"))
    if "error" in obj:
        raise ValueError("SOURCE_SCHEMA_GATE: ArcGIS returned error " + str(obj["error"])[:200])
    return obj


def to_integral_key(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number < 0 or number != round(number):
        return None
    return int(number)


def fetch_rpsb_islands() -> tuple[set[int], dict[int, dict], dict]:
    service = official_json("", {"f": "json"})
    actual_fields = {f["name"] for f in service.get("fields", [])}
    required = {"FID", "lowid", "mhwsarea_h", "mlwsarea_h", "population", "ferry"}
    if not required.issubset(actual_fields):
        raise ValueError("SOURCE_SCHEMA_GATE missing RSPB fields " + str(required - actual_fields))
    count = official_json(
        "/query", {"where": "1=1", "returnCountOnly": "true", "f": "json"}
    )["count"]
    if count != 9688:
        raise ValueError("SOURCE_FRAME_GATE expected static Stanbury 9688, observed " + str(count))
    per_page = 1000
    ids = set()
    island_meta = {}
    records = []
    coord_count = 0
    missing_key = 0
    for offset in range(0, count, per_page):
        block = official_json(
            "/query",
            {
                "where": "1=1",
                "outFields": "FID,ID,lowid,name,mhwsarea_h,mlwsarea_h,population,ferry,country,coast,group_",
                "outSR": 4326,
                "returnGeometry": "true",
                "orderByFields": "FID ASC",
                "resultOffset": offset,
                "resultRecordCount": min(per_page, count - offset),
                "f": "json",
            },
        )
        features = block.get("features", [])
        if len(features) != min(per_page, count - offset):
            raise ValueError("SOURCE_PAGINATION_GATE unexpected page size")
        for feature in features:
            attr = feature["attributes"]
            key = to_integral_key(attr.get("lowid"))
            if key is None:
                missing_key += 1
            elif key in ids:
                raise ValueError("SOURCE_KEY_GATE duplicated RSPB lowid " + str(key))
            else:
                ids.add(key)
                island_meta[key] = {
                    "high_tide_area_h": attr.get("mhwsarea_h"),
                    "low_tide_area_h": attr.get("mlwsarea_h"),
                    "human_population": attr.get("population"),
                    "ferry": attr.get("ferry"),
                    "country": attr.get("country"),
                    "group": attr.get("group_"),
                    "coast": attr.get("coast"),
                }
            pt = feature.get("geometry") or {}
            if key is not None and key in island_meta:
                island_meta[key]["longitude"] = pt.get("x")
                island_meta[key]["latitude"] = pt.get("y")
            if (
                isinstance(pt.get("x"), (int, float))
                and isinstance(pt.get("y"), (int, float))
                and -180 <= pt["x"] <= 180
                and -90 <= pt["y"] <= 90
            ):
                coord_count += 1
            records.append((
                attr.get("FID"), key, attr.get("mhwsarea_h"),
                attr.get("mlwsarea_h"), attr.get("country"), attr.get("population")
            ))
    stable = json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return ids, island_meta, {
        "area_strata_original_rpsb": {
            label: sum(
                isinstance(meta.get(field), (int, float)) and meta[field] > 10
                for meta in island_meta.values()
            )
            for label, field in (
                ("gt10ha_high_tide", "high_tide_area_h"),
                ("gt10ha_low_tide", "low_tide_area_h"),
            )
        },
        "publisher": "RSPB UK Islands (2014; Stanbury et al. 2017)",
        "source_url": RSPB_SERVICE,
        "metadata_url": RSPB_METADATA,
        "source_original_feature_count": count,
        "source_original_distinct_integer_lowid": len(ids),
        "source_original_missing_lowid": missing_key,
        "original_centroid_coordinates_nonmissing": coord_count,
        "fields": sorted(actual_fields),
        "source_extracted_nonbiological_row_signature_sha256": hashlib.sha256(stable).hexdigest(),
        "point_locations_are_not_island_polygons": True,
        "island_geometry_is_not_original_predator_survey_effort": True,
    }


def col_number(letters: str) -> int:
    value = 0
    for c in letters:
        if not "A" <= c <= "Z":
            raise ValueError("unrecognized Excel coordinate")
        value = value * 26 + ord(c) - 64
    return value - 1


def norm(s: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).strip().lower())


def sheet_rows(
    raw: bytes,
    island_meta: dict[int, dict] | None = None,
    extracted_source_rows: list[dict] | None = None,
) -> tuple[dict, list[dict]]:
    if not raw.startswith(b"PK"):
        raise ValueError("SOURCE_BINARY_GATE not an XLSX ZIP")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        infos = z.infolist()
        if len(infos) > 150 or sum(x.file_size for x in infos) > MAX_XML_BYTES:
            raise ValueError("SOURCE_ZIP_GATE uncompressed workbook too large")
        for item in infos:
            if item.filename.startswith("/") or ".." in item.filename.split("/"):
                raise ValueError("SOURCE_ZIP_GATE unsafe member path")
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join((t.text or "") for t in si.findall(".//x:t", NS))
                      for si in ss.findall("x:si", NS)]
        sheets = sorted(
            [n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)],
            key=lambda s: int(re.search(r"sheet(\d+)", s).group(1))
        )
        if not sheets:
            raise ValueError("SOURCE_XLSX_GATE no worksheets")
        reports = []
        keyed = []
        for name in sheets:
            tree = ET.fromstring(z.read(name))
            rows = []
            for row in tree.findall(".//x:sheetData/x:row", NS):
                cells = {}
                for c in row.findall("x:c", NS):
                    coordinate = c.attrib.get("r", "")
                    match = re.fullmatch(r"([A-Z]+)\d+", coordinate)
                    if not match:
                        continue
                    pos = col_number(match.group(1))
                    inline = c.find("x:is", NS)
                    v = c.find("x:v", NS)
                    if c.attrib.get("t") == "s" and v is not None:
                        idx = int(v.text)
                        val = shared[idx]
                    elif inline is not None:
                        val = "".join(x.text or "" for x in inline.findall(".//x:t", NS))
                    elif v is not None:
                        val = v.text or ""
                    else:
                        continue
                    cells[pos] = val
                if cells:
                    rows.append(cells)
            candidates = []
            for ri, row in enumerate(rows[:30]):
                headers = {col: norm(value) for col, value in row.items()}
                matches = [col for col, hdr in headers.items() if hdr == "lowid"]
                if matches:
                    candidates.append((ri, matches[0]))
            header = candidates[0] if candidates else None
            key_mode = "EXPLICIT_LOWID_HEADER" if header else "NONE"
            # Stanbury ESM5 has a documented but UNLABELED first column; use
            # it only as an independently cross-validated candidate lowid.
            # Never apply this to a short arbitrary or malformed workbook.
            if header is None and len(rows) >= 9002:
                values = [to_integral_key(row.get(0)) for row in rows[2:]]
                candidates_numeric = [v for v in values if v is not None]
                if (
                    len(candidates_numeric) >= 9000
                    and len(candidates_numeric) == len(set(candidates_numeric))
                    and len(candidates_numeric) / max(1, len(values)) >= .99
                ):
                    header = (1, 0)
                    key_mode = "UNLABELED_COL0_CANDIDATE_REQUIRES_FULL_RSPB_LOWID_JOIN"
            report = {
                "sheet_path": name,
                "nonempty_rows": len(rows),
                "first_three_rows_as_source_strings": [
                    {str(k): str(v)[:500] for k, v in list(row.items())[:40]}
                    for row in rows[:3]
                ],
                "exact_lowid_header_row_1indexed": (
                    header[0] + 1 if header and key_mode == "EXPLICIT_LOWID_HEADER" else None
                ),
                "identifier_mode": key_mode,
            }
            if header is not None:
                header_ri, key_col = header
                header_cells = rows[header_ri]
                predator_columns = [
                    (c, str(value))
                    for c, value in header_cells.items()
                    if PREDATOR_HEADER.search(str(value))
                ]
                keys = set()
                codes = {}
                for col, title in predator_columns[:30]:
                    counter = Counter(
                        str(row.get(col, "")).strip()[:64] or "<MISSING>"
                        for row in rows[header_ri + 1:]
                        if to_integral_key(row.get(key_col)) is not None
                    )
                    codes[title[:100]] = dict(counter.most_common(12))
                for row in rows[header_ri + 1:]:
                    value = to_integral_key(row.get(key_col))
                    if value is not None:
                        keys.add(value)
                geo_strata = {}
                if island_meta is not None:
                    for label, area_field in (
                        ("gt10ha_high_tide", "high_tide_area_h"),
                        ("gt10ha_low_tide", "low_tide_area_h"),
                    ):
                        qualifying = {
                            key for key, meta in island_meta.items()
                            if isinstance(meta.get(area_field), (int, float))
                            and meta[area_field] > 10
                        }
                        cohorts = {}
                        for col, title in predator_columns[:30]:
                            values = Counter(
                                str(row.get(col, "")).strip()[:64] or "<MISSING>"
                                for row in rows[header_ri + 1:]
                                if to_integral_key(row.get(key_col)) in qualifying
                            )
                            cohorts[title[:100]] = dict(values.most_common(15))
                        geo_strata[label] = {
                            "RSPB_original_qualifying_island_reference_n": len(qualifying),
                            "predator_literal_source_categories": cohorts,
                        }
                if extracted_source_rows is not None:
                    exact_taxa = {
                        "American mink", "Black rat", "Brown rat",
                        "Feral cat", "European hedgehog", "House mouse",
                        "Stoat", "Red fox", "Weasel",
                    }
                    columns = [(i, title) for i, title in predator_columns
                               if title.strip() in exact_taxa]
                    for original in rows[header_ri + 1:]:
                        original_lowid = to_integral_key(original.get(key_col))
                        if original_lowid is not None:
                            extracted_source_rows.append({
                                "lowid": original_lowid,
                                "status_codes": {
                                    title: str(original.get(i, "")).strip()
                                    for i, title in columns
                                },
                            })
                report.update({
                    "source_original_10ha_stratified_literal_codes": geo_strata,
                    "exact_lowid_distinct_numeric_keys": len(keys),
                    "predator_header_candidates": [x[1][:120] for x in predator_columns],
                    "predator_column_literal_value_histograms": codes,
                    "all_predator_zero_blank_and_unknown_codes_uninterpreted": True,
                })
                keyed.append((name, keys))
            reports.append(report)
    return {"sheets": reports, "shared_strings_n": len(shared)}, keyed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = {
        "status": "SOURCE_AUDIT_IN_PROGRESS",
        "scientific_mode": "FIRST_PARTY_PREDATOR_SOURCE_QA_NO_JNCC_OUTCOMES",
        "doi": DOI,
        "original_source_date_scope": "RSPB UK islands 2014; predator data Stanbury et al. 2017",
        "JNCC_original_count_magnitudes_opened": 0,
        "JNCC_spatial_effects_fitted": False,
    }
    island_ids = set()
    island_meta = {}
    try:
        island_ids, island_meta, receipt["RSPB_islands"] = fetch_rpsb_islands()
    except Exception as exc:
        receipt["RSPB_source_error"] = type(exc).__name__ + ": " + str(exc)[:250]
    supplements = {}
    all_keyed = []
    for label, url in SUPPLEMENTS.items():
        try:
            raw = bounded_get(url, MAX_SUPP_BYTES)
            info, keys_by_sheet = sheet_rows(
                raw, island_meta if label == "ESM5" else None
            )
            supplements[label] = {
                "publisher_url": url,
                "bytes": len(raw),
                "original_sha256": hashlib.sha256(raw).hexdigest(),
                **info,
            }
            for sheet, keys in keys_by_sheet:
                all_keyed.append({
                    "supplement": label,
                    "sheet": sheet,
                    "joinable_lowid_overlap_n": len(island_ids & keys) if island_ids else None,
                    "literal_lowid_distinct_in_sheet": len(keys),
                })
        except Exception as exc:
            supplements[label] = {
                "publisher_url": url,
                "access": "HOLD",
                "error": type(exc).__name__ + ": " + str(exc)[:250],
            }
    receipt["springer_supplements"] = supplements
    receipt["pre_outcome_lowid_key_join_support"] = all_keyed
    success_arcgis = bool(island_ids) and "RSPB_source_error" not in receipt
    success_xlsx = any("original_sha256" in value for value in supplements.values())
    joined = any(
        x["supplement"] == "ESM5"
        and (x.get("joinable_lowid_overlap_n") or 0) >= 9000
        and (x.get("joinable_lowid_overlap_n") or 0) / max(1, x["literal_lowid_distinct_in_sheet"]) >= .95
        for x in all_keyed
    )
    receipt["status"] = (
        "SOURCE_GEOGRAPHY_AND_SUPPLEMENT_LOWID_SCHEMA_PASS"
        if success_arcgis and success_xlsx and joined
        else "SOURCE_PARTIAL_HOLD_NO_PREDATOR_EFFECT"
    )
    receipt["predator_presence_absence_inferred_from_unknown_or_blank"] = False
    receipt["predator_niche_or_seabird_decline_model_fitted"] = False
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
