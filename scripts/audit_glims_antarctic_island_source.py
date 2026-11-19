#!/usr/bin/env python3
"""Read-only GLIMS WFS source-availability gate for selected Antarctic island regions.

Queries are limited, spatial/temporal coverage probes, NOT true habitat-exposure
polygons, penguin absences, or biological models. Date/geometry completeness gates
must precede any glacier-to-penguin join.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

WFS = "https://www.glims.org/geoserver/ows"
# Broad study-area boxes: [west longitude, south latitude, east longitude, north latitude].
# These include non-island terrain and cannot establish physical landmass identity.
PILOT_BBOXES = {
    "south_shetland_king_george_area": (-59.0, -62.35, -57.9, -61.6),
    "south_shetland_livingston_area": (-61.5, -63.1, -59.4, -62.2),
    "palmer_anvers_area": (-65.5, -65.0, -63.3, -64.2),
}
# Never infer a temporal year from the WFS feature creation/publication timestamp.
SOURCE_DATE_FIELDS = (
    "src_date", "source_date", "srcdate", "image_date", "img_date",
    "analysis_date", "anlys_date", "acq_date", "acquisition_date",
    "orig_date", "orig_time", "source_time",
)
GLACIER_KEY_FIELDS = ("glims_id", "glimsid", "glacier_id", "glac_id")
YEAR_RE = re.compile(r"(?<!\d)((?:18|19|20)\d{2})(?!\d)")


def http_get(params: dict[str, str], timeout: int = 35) -> bytes:
    url = WFS + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": "mina-postglacial-source-gate/1.0 (research read-only)",
        "Accept": "application/json, application/xml, text/xml, */*",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read(20_000_001)
        if len(data) > 20_000_000:
            raise RuntimeError("source response >20MB; refusal to autoexpand")
        return data


def feature_types(xml_data: bytes) -> list[str]:
    root = ET.fromstring(xml_data)
    types = []
    for child in root.iter():
        if child.tag.rsplit("}", 1)[-1] == "FeatureType":
            for tag in child:
                if tag.tag.rsplit("}", 1)[-1] == "Name" and tag.text:
                    types.append(tag.text.strip())
                    break
    return types


def select_layer(types: list[str]) -> str | None:
    # Explicit prefer glacier polygon outline; never silently switch to RGI or photo.
    candidates = [x for x in types if "glims" in x.lower()
                  and any(s in x.lower() for s in ("glacier", "outline"))]
    if len(candidates) == 1:
        return candidates[0]
    # If more/none, report rather than cherry-pick another dataset.
    return None


def years_from_properties(props: dict) -> list[int]:
    lowered = {str(k).lower(): v for k, v in props.items()}
    years = []
    for field in SOURCE_DATE_FIELDS:
        v = lowered.get(field)
        if v is None or str(v).strip() == "":
            continue
        # Use source-acquisition fields only, not publication/record-added fields.
        try:
            y = int(str(v)[:4])
            if 1850 <= y <= 2026:
                years.append(y)
                continue
        except (ValueError, TypeError):
            pass
        for m in YEAR_RE.findall(str(v)):
            years.append(int(m))
    return sorted(set(years))


def audit_features(data: dict, limit: int) -> dict:
    feats = data.get("features", [])
    if data.get("type") != "FeatureCollection" or not isinstance(feats, list):
        raise ValueError("response is not GeoJSON FeatureCollection")
    hist = Counter()
    hasdate, hasglac, hasgeom = 0, 0, 0
    date_keys = Counter()
    for feat in feats:
        props = feat.get("properties") or {}
        years = years_from_properties(props)
        if years:
            hasdate += 1
            for y in years: hist[y] += 1
        for k in props:
            if str(k).lower() in SOURCE_DATE_FIELDS:
                date_keys[str(k)] += 1
        if any(props.get(k) not in (None, "") for k in GLACIER_KEY_FIELDS):
            hasglac += 1
        if feat.get("geometry"):
            hasgeom += 1
    return {
        "features_returned": len(feats),
        "limit": limit,
        "limited_page_possible": len(feats) >= limit,
        "features_with_source_date": hasdate,
        "features_with_glacier_key": hasglac,
        "features_with_geometry": hasgeom,
        "source_date_fields_seen": dict(date_keys),
        "years_sample_histogram": dict(sorted(hist.items())),
        "reported_total_features": data.get("totalFeatures") or data.get("numberMatched"),
        "sample_only": True,
    }


def probe(max_features: int = 300) -> dict:
    report = {
        "study": "GLIMS dated glacier outline source-availability; Antarctic island pilot",
        "date_utc": datetime.utcnow().strftime("%Y-%m-%d"),
        "source": WFS,
        "max_features_per_bbox": max_features,
        "source_only": True,
        "penguin_data_opened": False,
        "biological_effect_fitted": False,
        "coverage": {},
    }
    try:
        xml = http_get({"service": "WFS", "version": "1.0.0",
                        "request": "GetCapabilities"})
        types = feature_types(xml)
        report["available_layer_names"] = types
        layer = select_layer(types)
        report["selected_layer"] = layer
        if not layer:
            report["status"] = "HOLD_LAYER_UNRESOLVED"
            return report
        for label, (west, south, east, north) in PILOT_BBOXES.items():
            try:
                raw = http_get({
                    "service": "WFS", "version": "1.0.0", "request": "GetFeature",
                    "typeName": layer, "maxFeatures": str(max_features),
                    "outputFormat": "application/json",
                    "srsName": "EPSG:4326",
                    "bbox": f"{west},{south},{east},{north}",
                })
                report["coverage"][label] = audit_features(json.loads(raw), max_features)
            except (urllib.error.URLError, ValueError, RuntimeError, json.JSONDecodeError) as e:
                report["coverage"][label] = {"status": "HOLD_SOURCE_FETCH", "error": str(e)[:250]}
        report["status"] = "PILOT_SOURCE_FETCH_COMPLETED"
    except (urllib.error.URLError, ET.ParseError, RuntimeError, ValueError) as e:
        report["status"] = "HOLD_WFS_CAPABILITIES"
        report["error"] = str(e)[:250]
    report["interpretation"] = [
        "These are bounded WFS pilot samples, not complete island glacier inventories.",
        "GLIMS outline dates must be paired within geometrically stable glaciers; newest snapshots and RGI are not time series.",
        "Island landmass identity, prior ice at the exact nest patch and visited penguin A/P are all untested.",
        "No GLIMS bounding-box features may be converted directly to new breeding habitat or settlement events.",
    ]
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--max-features", type=int, default=300)
    a = p.parse_args()
    if not 1 <= a.max_features <= 1000:
        raise SystemExit("max-features must be 1..1000")
    r = probe(a.max_features)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(r, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({k: r.get(k) for k in ("status","selected_layer","coverage")}, sort_keys=True))


if __name__ == "__main__":
    main()
