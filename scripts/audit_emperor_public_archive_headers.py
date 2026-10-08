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


def download_public(name: str, out: Path) -> dict:
    statuses = []
    for url in urls_for(name):
        req = urllib.request.Request(
            url, headers={"User-Agent": "mina-scientific-archive-audit/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=35) as inp:
                mime = inp.headers.get("Content-Type", "")
                payload = inp.read(1000 * 1000)  # 1 MB cap, known <= 55 KB
                final_url = inp.geturl()
                code = inp.status
            statuses.append({"http_code": code, "response_mime": mime})
            if not payload.startswith(b"PK\x03\x04"):
                statuses[-1]["error"] = "NOT_XLSX_MAGIC"
                continue
            checksum = hashlib.md5(payload).hexdigest()  # frozen public checksum
            if checksum != FILES[name]:
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


def _cell_text(cell, strings: list[str]) -> str:
    typ = cell.attrib.get("t", "")
    if typ == "s":
        v = cell.find(M + "v")
        idx = int(v.text) if v is not None and v.text else -1
        return strings[idx] if 0 <= idx < len(strings) else ""
    if typ == "inlineStr":
        return "".join(t.text or "" for t in cell.iter(M + "t"))
    v = cell.find(M + "v")
    return v.text if v is not None and v.text else ""


def _safe_header_candidate(values: list[str]) -> bool:
    strings = [str(v).strip() for v in values if v and str(v).strip()]
    if len(strings) < 2:
        return False
    signals = sum(any(w in s.lower() for w in HEADER_TOKENS) for s in strings)
    numeric = sum(bool(re.match(r"^\d{4}[-/.]\d\d", s)) for s in strings)
    return signals >= 2 and numeric < max(1, len(strings) // 2)


def inspect_headers_only(path: Path) -> dict:
    with ZipFile(path) as z:
        content_names = set(z.namelist())
        names = sorted(n for n in content_names if n.startswith("xl/worksheets/") and n.endswith(".xml"))
        if "xl/workbook.xml" not in content_names or not names:
            raise ValueError("missing workbook or worksheets")
        doc = ET.fromstring(z.read("xl/workbook.xml"))
        relmap = {}
        relname = "xl/_rels/workbook.xml.rels"
        if relname in content_names:
            roots = ET.fromstring(z.read(relname))
            relmap = {
                x.attrib.get("Id", ""): x.attrib.get("Target", "")
                for x in roots.findall(P + "Relationship")
            }
        strings = []
        if "xl/sharedStrings.xml" in content_names:
            for item in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M + "si"):
                strings.append("".join(t.text or "" for t in item.iter(M + "t")))

        outcome = []
        for sheet in doc.find(M + "sheets"):
            title = sheet.attrib.get("name", "")
            rel = sheet.attrib.get(R + "id", "")
            target = relmap.get(rel, "")
            if target.startswith("/xl/"):
                sheet_path = target.lstrip("/")
            elif target.startswith("xl/"):
                sheet_path = target
            else:
                sheet_path = "xl/" + target.lstrip("/")
            if sheet_path not in content_names:
                outcome.append({"sheet": title, "status": "SHEET_TARGET_UNRESOLVED"})
                continue
            # ET.iterparse reads only the first six XML row records; no response
            # values are printed or materialized into any scientific statistic.
            with z.open(sheet_path) as stream:
                candidates = []
                for ev, row in ET.iterparse(stream, events=("end",)):
                    if row.tag != M + "row":
                        continue
                    y = int(row.attrib.get("r", "0") or 0)
                    if y > 6:
                        break
                    vals = [_cell_text(c, strings) for c in row.findall(M + "c")]
                    if _safe_header_candidate(vals):
                        header = [str(v).strip()[:85] for v in vals if v and str(v).strip()]
                        candidates.append({"row": y, "header": header})
                    row.clear()
            outcome.append({
                "sheet": title,
                "status": "HEADER_CANDIDATE" if candidates else "NO_HEADER_IN_TOP_SIX",
                "header_candidates": candidates,
            })
        return {"sheets": outcome, "sheet_count": len(outcome)}


def run(out_dir: Path, *, no_network=False) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "scope": "outcome_blind_archive_and_header_only",
        "source": "https://zenodo.org/records/17390368",
        "files": {}, "outcome_rows_read": 0, "effect_fitted": False
    }
    for name in FILES:
        xlsx = out_dir / name
        item = {"status": "SKIPPED_NO_NETWORK"} if no_network else download_public(name, xlsx)
        if item.get("status") == "VERIFIED":
            try:
                item.update(inspect_headers_only(xlsx))
            except (BadZipFile, ValueError, ET.ParseError, KeyError) as exc:
                item.update({"header_status": "ERROR", "message": str(exc)[:100]})
            xlsx.unlink(missing_ok=True)  # don't push biological files into repo
        result["files"][name] = item
    result["all_three_verified"] = all(x.get("status")=="VERIFIED" for x in result["files"].values())
    return result


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
