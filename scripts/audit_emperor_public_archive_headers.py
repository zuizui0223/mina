"""Outcome-blind public Zenodo emperor colony workbook archive/schema gate.

Fetch three small public XLSX from pinned Zenodo v3; inspect archive integrity,
sheet names and *header candidates only*. NEVER read cell values in response
rows, calculate colony counts, or infer movement. No pandas/openpyxl needed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, BadZipFile

ROOT = "https://zenodo.org"
RECORD = "17390368"
FILES = {
    "AstridDataUpload.xlsx": "f41f5106df1f3b5bb91bad43ae96e30d",
    "MertzDataUpload.xlsx": "6fee82cd5b9b12d5b10638eb0cbbb49b",
    "SanaeDataUpload.xlsx": "de960629596e5aa86d3a7d68d742a5f4",
}

# A former Zenodo version has a different SANAE filename and checksum.
# This is a SOURCE IDENTIFIER alias only, not an outcome-adaptive data fallback.
# A change in the pinned v3 checksum must stop before reading the workbook.
ALIASES = {"SanaeDataUpload.xlsx": {
    "SanaeDataUpload2.xlsx": "13d916e08387d94ae448e129aa8aa442"
}}
MAX_FILE_SIZE = 200_000  # only public small XLSX workbooks, not 2.4GB image ZIP

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
P = "{http://schemas.openxmlformats.org/package/2006/relationships}"
HEADER_TOKENS = (
    "date", "day", "month", "year", "time", "sensor", "satellite",
    "image", "visible", "shelf", "ice", "guano", "colony", "sea",
    "platform", "landsat", "modis", "sentinel", "cloud", "weather",
    "clear", "observation", "method", "type", "location", "present",
)


def urls_for(name: str):
    return [
        f"{ROOT}/records/{RECORD}/files/{name}?download=1",
        f"{ROOT}/api/records/{RECORD}/files/{name}/content",
    ]


def metadata_for_pinned_record() -> dict:
    """Retrieve version-specific FILE METADATA, never a workbook response row."""
    url = f"{ROOT}/api/records/{RECORD}"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "mina-scientific-archive-audit/2.0",
                          "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=35) as response:
            data = json.loads(response.read(500_000))
        if str(data.get("id")) != RECORD:
            return {"status": "RECORD_ID_MISMATCH", "declared_id": data.get("id")}
        entries = {}
        for item in data.get("files", []):
            key = item.get("key", "")
            if key and isinstance(item.get("size"), int):
                entries[key] = {
                    "size": item["size"],
                    "checksum": item.get("checksum", ""),
                }
        return {
            "status": "MANIFEST_VERIFIED", "doi": data.get("doi"),
            "record_id": str(data.get("id")),
            "file_names_and_hashes": entries
        }
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            json.JSONDecodeError) as exc:
        return {"status": "RECORD_METADATA_BLOCKED",
                "error_type": type(exc).__name__,
                "message": str(exc)[:130]}


def resolve_manifest_name(slot: str, manifest: dict) -> dict:
    entries = manifest.get("file_names_and_hashes", {})
    available = {slot: FILES[slot], **ALIASES.get(slot, {})}
    found = [key for key in available if key in entries]
    if len(found) != 1:
        return {"status": "NAME_MISSING_OR_AMBIGUOUS_IN_PINNED_RECORD",
                "allowed_names": list(available), "matched": found}
    name = found[0]
    rec = entries[name]
    declared_md5 = rec.get("checksum", "").removeprefix("md5:")
    if declared_md5 != available[name]:
        return {"status": "PINNED_CHECKSUM_DISAGREES_WITH_PUBLISHED_MANIFEST",
                "name": name, "expected_md5": available[name],
                "manifest_md5": declared_md5, "no_outcome_data_opened": True}
    if rec.get("size", 0) <= 0 or rec["size"] > MAX_FILE_SIZE:
        return {"status": "UNSAFE_FILE_SIZE", "name": name,
                "published_size_bytes": rec.get("size")}
    return {"status": "SOURCE_IDENTITY_VERIFIED", "name": name,
            "md5": declared_md5, "size_bytes": rec["size"]}


def download_public(name: str, out: Path, expected_md5: str) -> dict:
    statuses = []
    for url in urls_for(name):
        req = urllib.request.Request(
            url, headers={"User-Agent": "mina-scientific-archive-audit/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=35) as inp:
                mime = inp.headers.get("Content-Type", "")
                payload = inp.read(MAX_FILE_SIZE + 1)
                final_url = inp.geturl()
                code = inp.status
            statuses.append({"http_code": code, "response_mime": mime})
            if not payload.startswith(b"PK\x03\x04"):
                statuses[-1]["error"] = "NOT_XLSX_MAGIC"
                continue
            checksum = hashlib.md5(payload).hexdigest()  # frozen public checksum
            if checksum != expected_md5:
                statuses[-1]["error"] = "FROZEN_MD5_MISMATCH"
                statuses[-1]["md5_seen"] = checksum
                continue
            out.write_bytes(payload)
            return {
                "status": "VERIFIED", "size_bytes": len(payload),
                "md5": checksum, "url": final_url, "attempts": statuses
            }
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as err:
            statuses.append({
                "error_type": err.__class__.__name__,
                "message": str(err)[:140],
            })
    return {"status": "DOWNLOAD_OR_MD5_BLOCKED", "attempts": statuses}


def _safe_header_candidate(values: list[str]) -> bool:
    strings = [str(v).strip() for v in values if v and str(v).strip()]
    if len(strings) < 2:
        return False
    signals = sum(any(w in s.lower() for w in HEADER_TOKENS) for s in strings)
    numeric = sum(bool(re.match(r"^\d{4}[-/.]\d\d", s)) for s in strings)
    return signals >= 2 and numeric < max(1, len(strings) // 2)


def _first_row_tokens(zipfile, sheet_path: str) -> list[tuple[str, str]]:
    """Only collect typed references from *row 1*; never decode row 2 onward."""
    with zipfile.open(sheet_path) as stream:
        for event, element in ET.iterparse(stream, events=("end",)):
            if element.tag != M + "row":
                continue
            if element.attrib.get("r") != "1":
                return []
            tokens = []
            for cell in element.findall(M + "c"):
                cell_type = cell.get("t", "")
                if cell_type == "s":
                    value = cell.find(M + "v")
                    if value is not None and value.text:
                        tokens.append(("shared", value.text))
                elif cell_type == "inlineStr":
                    tokens.append(("text", "".join(
                        text.text or "" for text in cell.iter(M + "t")
                    )))
                else:
                    # Numeric or calculated values in row 1 are never headers.
                    tokens.append(("nonheader", ""))
            return tokens
    return []


def _needed_shared_strings(zipfile, indices: set[int]) -> dict[int, str]:
    """Stream the string dictionary, storing only indices referenced in row 1.

    Does not materialize non-header shared-string values or worksheet rows.
    """
    if not indices:
        return {}
    if "xl/sharedStrings.xml" not in zipfile.namelist():
        return {}
    names = {}
    current = -1
    with zipfile.open("xl/sharedStrings.xml") as stream:
        for event, element in ET.iterparse(stream, events=("end",)):
            if element.tag != M + "si":
                continue
            current += 1
            if current in indices:
                names[current] = "".join(
                    text.text or "" for text in element.iter(M + "t")
                )
            element.clear()
            if current >= max(indices):
                break
    return names


def inspect_headers_only(path: Path) -> dict:
    with ZipFile(path) as archive:
        contents = set(archive.namelist())
        if "xl/workbook.xml" not in contents:
            raise ValueError("missing xlsx workbook.xml")
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = workbook.find(M + "sheets")
        if sheets is None:
            raise ValueError("no sheets element")
        relation = "xl/_rels/workbook.xml.rels"
        if relation not in contents:
            return {"sheet_count": len(sheets), "sheets": [
                {"sheet": sheet.get("name"), "status": "NO_WORKBOOK_RELATIONSHIPS"}
                for sheet in sheets
            ]}
        links = {
            rel.get("Id"): rel.get("Target")
            for rel in ET.fromstring(archive.read(relation)).findall(
                P + "Relationship"
            )
        }
        report = []
        for sheet in sheets:
            title = sheet.get("name")
            target = links.get(sheet.get(R + "id", ""), "")
            if target.startswith("/xl/"):
                path = target.lstrip("/")
            elif target.startswith("xl/"):
                path = target
            else:
                path = "xl/" + target.lstrip("/")
            if path not in contents:
                report.append({"sheet": title, "status": "SHEET_TARGET_UNRESOLVED"})
                continue
            tokens = _first_row_tokens(archive, path)
            indices = {int(v) for typ, v in tokens if typ == "shared"}
            strings = _needed_shared_strings(archive, indices)
            values = [
                strings.get(int(value), "") if typ == "shared"
                else value if typ == "text" else ""
                for typ, value in tokens
            ]
            if _safe_header_candidate(values):
                report.append({
                    "sheet": title,
                    "status": "HEADER_CANDIDATE_ROW_1",
                    "headers": [str(value).strip()[:90] for value in values],
                })
            else:
                report.append({
                    "sheet": title,
                    "status": "ROW_1_NOT_VERIFIED_HEADER_STOP",
                    "header_candidates": [],
                })
        return {"sheet_count": len(report), "sheets": report,
                "outcome_rows_decoded": 0}


def run(out_dir: Path, *, no_network=False) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "scope": "pinned_record_manifest_and_row_1_header_only",
        "source": f"{ROOT}/records/{RECORD}",
        "files": {}, "outcome_rows_read": 0, "effect_fitted": False,
        "record_metadata": {"status": "SKIPPED_NO_NETWORK"} if no_network
                           else metadata_for_pinned_record(),
    }
    manifest = report["record_metadata"]
    for logical_name in FILES:
        if no_network:
            report["files"][logical_name] = {"status": "SKIPPED_NO_NETWORK"}
            continue
        if manifest.get("status") != "MANIFEST_VERIFIED":
            report["files"][logical_name] = {
                "status": "RECORD_METADATA_BLOCKED_NO_DOWNLOAD"
            }
            continue
        identity = resolve_manifest_name(logical_name, manifest)
        if identity["status"] != "SOURCE_IDENTITY_VERIFIED":
            report["files"][logical_name] = identity
            continue
        actual_name = identity["name"]
        path = out_dir / actual_name
        try:
            receipt = download_public(actual_name, path, identity["md5"])
            if receipt["status"] == "VERIFIED":
                try:
                    receipt.update(inspect_headers_only(path))
                except (BadZipFile, ValueError, ET.ParseError, KeyError) as exc:
                    receipt["header_status"] = "ERROR"
                    receipt["message"] = str(exc)[:100]
            receipt["resolved_name"] = actual_name
            report["files"][logical_name] = receipt
        finally:
            path.unlink(missing_ok=True)
    report["all_three_verified"] = all(
        x.get("status") == "VERIFIED" and
        x.get("sheet_count", 0) >= 1 and
        x.get("header_status") != "ERROR" and
        all(y.get("status") == "HEADER_CANDIDATE_ROW_1"
            for y in x.get("sheets", []))
        for x in report["files"].values()
    )
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--cache", type=Path, default=Path("/tmp/zenodo_public_schema"))
    p.add_argument("--no-network", action="store_true")
    args=p.parse_args()
    result=run(args.cache, no_network=args.no_network)
    args.out.write_text(json.dumps(result, indent=2)+"\n",encoding="utf8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
