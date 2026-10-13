"""Original 2011 independent redigitization: DBF attribute counts, NO shape rows.

CHPE / MCPE / MIXED are the actually observed DBF labels, not a
backfilled assumption that mixed polygons belong to one species.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import requests
from reproduce_zavodovski_direct_image_overlap_v10 import (
    manifest_rows, secure_request, canonical_file_url
)
from audit_zavodovski_lynch2011_dbf_header_v12 import dbf_header

NAME = "mac_and_chinstrap_colony_boundaries_2011.dbf"
ALLOWED = frozenset(("CHPE", "MCPE", "MIXED"))


def categories_from_dbf(blob):
    header = dbf_header(blob)
    fields = header["fields"]
    if [x["name"].lower() for x in fields] != ["species", "area"]:
        raise ValueError("LABEL_STOP unexpected historic fields")
    n, header_size = header["records"], int.from_bytes(blob[8:10], "little")
    row_size = int.from_bytes(blob[10:12], "little")
    if row_size != 1 + sum(f["width"] for f in fields):
        raise ValueError("LABEL_STOP unexpected record layout")
    if len(blob) < header_size + n * row_size:
        raise ValueError("LABEL_STOP truncated DBF rows")
    labels = []
    area_totals = Counter()
    for i in range(n):
        row = blob[header_size+i*row_size:header_size+(i+1)*row_size]
        if row[0] == 42:
            continue
        if row[0] != 32:
            raise ValueError("LABEL_STOP unknown DBF record deletion flag")
        lab = row[1:1+fields[0]["width"]].decode("ascii").strip().upper()
        if lab not in ALLOWED:
            raise ValueError("LABEL_STOP unexpected species value (cannot recode)")
        labels.append(lab)
        raw_area = row[1+fields[0]["width"]:].decode("ascii").strip()
        try:
            area = float(raw_area)
        except Exception as exc:
            raise ValueError("LABEL_STOP unparseable area attribute") from exc
        if area < 0 or not (-1e30 < area < 1e30):
            raise ValueError("LABEL_STOP implausible historic area attribute")
        area_totals[lab] += area
    if not labels:
        raise ValueError("LABEL_STOP no active records")
    return {
        "category_counts": dict(Counter(labels)),
        "historic_area_attribute_totals_UNVERIFIED_UNITS": {
            label: round(value, 5) for label, value in area_totals.items()
        },
        "active_rows": len(labels),
        "status": "ORIGINAL_CATEGORY_ROWS_AUDITED_NO_GEOMETRY_OPEN",
        "shape_rows_opened": 0,
        "note": "MIXED is not allocated to either species; units/meaning of original area attribute are not independently checked."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()
    result = {"status": "HOLD", "shape_rows_opened": 0}
    try:
        with requests.Session() as session:
            manifest = {r["name"]: r for r in manifest_rows(session, 2011)}
            blob = secure_request(session, canonical_file_url(manifest[NAME]["url"]))
        result = categories_from_dbf(blob)
        result["source_dbf_sha256"] = hashlib.sha256(blob).hexdigest()
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {str(exc)[:250]}"
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    if result["status"] != "ORIGINAL_CATEGORY_ROWS_AUDITED_NO_GEOMETRY_OPEN":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
