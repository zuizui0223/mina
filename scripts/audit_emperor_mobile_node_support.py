#!/usr/bin/env python3
"""Outcome-blind support audit for emperor-penguin mobile-node Paper 3."""
from __future__ import annotations

import argparse
import io
import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

import requests


CSW = "https://api.bas.ac.uk/data/metadata/csw/v2/"
UA = "mina-paper3-mobile-node-support/1.0"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        d = dict(attrs)
        if d.get("href"):
            self.links.append(d["href"])


def get_csw_xml(session: requests.Session, record_id: str, iso: bool = True) -> bytes:
    params = {
        "service": "CSW",
        "version": "2.0.2",
        "request": "GetRecordById",
        "elementsetname": "full",
        "id": record_id,
    }
    if iso:
        params["outputSchema"] = "http://www.isotc211.org/2005/gmd"
    r = session.get(CSW, params=params, timeout=60)
    r.raise_for_status()
    return r.content


def extract_urls_from_xml(xml: bytes) -> list[str]:
    root = ET.fromstring(xml)
    urls = []
    for el in root.iter():
        text = (el.text or "").strip()
        if text.startswith("http://") or text.startswith("https://"):
            urls.append(text)
        for value in el.attrib.values():
            value = str(value).strip()
            if value.startswith("http://") or value.startswith("https://"):
                urls.append(value)
    # Some ISO profiles place URLs in free text; regex is a final public-metadata fallback.
    decoded = xml.decode("utf-8", errors="ignore")
    urls.extend(re.findall(r'https?://[^<>"\\s]+', decoded))
    return list(dict.fromkeys(urls))


def datacite_urls(session: requests.Session, doi: str) -> tuple[list[str], str | None]:
    try:
        r = session.get(f"https://api.datacite.org/dois/{doi}", timeout=60)
        r.raise_for_status()
        obj = r.json()
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"
    found = []
    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and (x.startswith("http://") or x.startswith("https://")):
            found.append(x)
    walk(obj)
    return list(dict.fromkeys(found)), None


def download_small(session: requests.Session, url: str, max_bytes: int = 150_000_000):
    r = session.get(url, timeout=120, allow_redirects=True, stream=True)
    r.raise_for_status()
    chunks = []
    total = 0
    for chunk in r.iter_content(1024 * 1024):
        if not chunk:
            continue
        total += len(chunk)
        if total > max_bytes:
            raise ValueError(f"download exceeds {max_bytes} bytes")
        chunks.append(chunk)
    return b"".join(chunks), r.headers.get("content-type", ""), r.url


def candidate_links_from_html(base_url: str, html: bytes) -> list[str]:
    p = LinkParser()
    p.feed(html.decode("utf-8", errors="ignore"))
    links = [urljoin(base_url, x) for x in p.links]
    scored = []
    for u in links:
        low = u.lower()
        score = 0
        if "ramadda.data.bas.ac.uk" in low:
            score += 4
        if "entry/get" in low:
            score += 4
        if any(low.endswith(ext) or ext + "?" in low for ext in (".zip", ".kmz", ".shp", ".tar.gz")):
            score += 5
        if "download" in low:
            score += 2
        if score:
            scored.append((score, u))
    return [u for _, u in sorted(scored, reverse=True)]


def inspect_zip(data: bytes) -> dict:
    if not zipfile.is_zipfile(io.BytesIO(data)):
        return {"is_zip": False, "names": [], "shapefiles": []}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
    shps = [x for x in names if x.lower().endswith(".shp")]
    return {"is_zip": True, "names": names, "shapefiles": shps}


def parse_kmz(data: bytes) -> dict:
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise ValueError("global snapshot is not KMZ/ZIP")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        kmls = [x for x in z.namelist() if x.lower().endswith(".kml")]
        if not kmls:
            raise ValueError("KMZ contains no KML")
        root = ET.fromstring(z.read(kmls[0]))
    placemarks = []
    for pm in root.iter():
        if not pm.tag.endswith("Placemark"):
            continue
        name = None
        coords = []
        for el in pm.iter():
            if el.tag.endswith("name") and name is None:
                name = (el.text or "").strip()
            if el.tag.endswith("coordinates") and el.text:
                for token in el.text.strip().split():
                    parts = token.split(",")
                    if len(parts) >= 2:
                        try:
                            coords.append((float(parts[0]), float(parts[1])))
                        except ValueError:
                            pass
        if coords:
            placemarks.append({"name": name, "coordinates": coords})
    return {
        "placemarks": len(placemarks),
        "names_nonempty": sum(bool(x["name"]) for x in placemarks),
        "coordinate_points": sum(len(x["coordinates"]) for x in placemarks),
    }


def discover_tracking_archive(session: requests.Session, csw_urls: list[str]) -> dict:
    # Prefer BAS/RAMADDA and likely download links, then try HTML expansion.
    candidates = []
    for u in csw_urls:
        low = u.lower()
        if "ramadda" in low or "data.bas.ac.uk" in low or "download" in low:
            candidates.append(u)
    candidates = list(dict.fromkeys(candidates))

    attempts = []
    expanded = []
    for u in candidates[:20]:
        try:
            data, ctype, final = download_small(session, u)
            info = inspect_zip(data)
            attempts.append({
                "url": u, "final_url": final, "content_type": ctype,
                "bytes": len(data), "is_zip": info["is_zip"],
                "n_shapefiles": len(info["shapefiles"]),
            })
            if info["is_zip"] and info["shapefiles"]:
                return {
                    "found": True, "url": final, "bytes": len(data),
                    "shapefiles": info["shapefiles"],
                    "archive_names": info["names"],
                    "attempts": attempts,
                }
            if "html" in ctype.lower() or data.lstrip().startswith(b"<"):
                expanded.extend(candidate_links_from_html(final, data))
        except Exception as exc:
            attempts.append({"url": u, "error": f"{type(exc).__name__}: {exc}"})

    for u in list(dict.fromkeys(expanded))[:30]:
        try:
            data, ctype, final = download_small(session, u)
            info = inspect_zip(data)
            attempts.append({
                "url": u, "final_url": final, "content_type": ctype,
                "bytes": len(data), "is_zip": info["is_zip"],
                "n_shapefiles": len(info["shapefiles"]),
            })
            if info["is_zip"] and info["shapefiles"]:
                return {
                    "found": True, "url": final, "bytes": len(data),
                    "shapefiles": info["shapefiles"],
                    "archive_names": info["names"],
                    "attempts": attempts,
                }
        except Exception as exc:
            attempts.append({"url": u, "error": f"{type(exc).__name__}: {exc}"})
    return {"found": False, "url": None, "shapefiles": [], "archive_names": [], "attempts": attempts}


def audit(contract: dict) -> dict:
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    record_id = contract["primary_tracking_source"]["bas_record_id"]
    csw_payloads = []
    csw_errors = []
    for iso in (True, False):
        try:
            xml = get_csw_xml(session, record_id, iso=iso)
            csw_payloads.append({"schema": "iso19139" if iso else "dublin_core", "bytes": len(xml)})
            if iso:
                xml_iso = xml
            else:
                xml_dc = xml
        except Exception as exc:
            csw_errors.append(f"{'iso' if iso else 'dc'}: {type(exc).__name__}: {exc}")
    csw_urls = []
    for xml in [locals().get("xml_iso", b""), locals().get("xml_dc", b"")]:
        if xml:
            try:
                csw_urls.extend(extract_urls_from_xml(xml))
            except Exception as exc:
                csw_errors.append(f"parse: {type(exc).__name__}: {exc}")
    dc_urls, dc_error = datacite_urls(session, contract["primary_tracking_source"]["doi"])
    explicit_urls = list(contract["primary_tracking_source"].get("ramadda_tree_zip_urls", []))
    landing = contract["primary_tracking_source"].get("landing_url")
    if landing:
        explicit_urls.append(landing)
    all_discovery_urls = list(dict.fromkeys(explicit_urls + csw_urls + dc_urls))
    csw_ok = bool(csw_payloads)
    csw_error = "; ".join(csw_errors) if csw_errors else None

    tracking = discover_tracking_archive(session, all_discovery_urls) if all_discovery_urls else {
        "found": False, "url": None, "shapefiles": [], "archive_names": [], "attempts": []
    }

    kmz_url = contract["global_snapshot_source"]["direct_kmz"]
    try:
        kmz, _, final = download_small(session, kmz_url)
        kmz_info = parse_kmz(kmz)
        kmz_info.update({"available": True, "url": final, "bytes": len(kmz), "error": None})
    except Exception as exc:
        kmz_info = {
            "available": False, "url": kmz_url, "bytes": 0,
            "placemarks": 0, "names_nonempty": 0, "coordinate_points": 0,
            "error": f"{type(exc).__name__}: {exc}",
        }

    snap_min = int(contract["support_requirements"]["global_snapshot"]["minimum_parseable_placemarks"])
    tracking_basic = bool(tracking["found"] and len(tracking["shapefiles"]) >= 1)
    snapshot_pass = bool(kmz_info["available"] and kmz_info["placemarks"] >= snap_min)

    return {
        "schema_version": 1,
        "result_id": "mina-paper3-mobile-node-identity-support-v1",
        "csw": {
            "record_id": record_id,
            "available": csw_ok,
            "error": csw_error,
            "payloads": csw_payloads,
            "urls_found": csw_urls,
        },
        "datacite": {
            "available": dc_error is None,
            "error": dc_error,
            "urls_found": dc_urls,
        },
        "combined_discovery_urls": all_discovery_urls,
        "primary_tracking_archive": tracking,
        "global_2023_snapshot": kmz_info,
        "decision": {
            "tracking_archive_basic_support": tracking_basic,
            "global_snapshot_gate_passed": snapshot_pass,
            "schema_audit_authorized": tracking_basic,
            "movement_outcomes_opened": False,
            "full_support_gate_decided": False,
        },
        "next_action": (
            "If tracking archive is found, inspect shapefile fields/filenames only and freeze a deterministic "
            "date/colony/group parser before calculating any movement displacement."
        ),
        "boundary": [
            "This audit does not calculate movement distance or apparent turnover.",
            "No abundance, breeding success or sea-ice covariate is read.",
            "If the PDC data service is temporarily unavailable, that is recorded as a technical support state rather than a biological failure."
        ]
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()
    c = json.loads(a.contract.read_text(encoding="utf-8"))
    r = audit(c)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(r, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
