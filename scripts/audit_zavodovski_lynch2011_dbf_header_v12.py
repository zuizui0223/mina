"""DBF HEADER ONLY: assess coding of prior 2011 Lynch same-scene redigitization.

Does not inspect DBF biological row values or SHP geometry.
"""
import argparse
import hashlib
import json
from pathlib import Path
import requests
from reproduce_zavodovski_direct_image_overlap_v10 import (
    canonical_file_url, manifest_rows, secure_request
)
BASENAME = "mac_and_chinstrap_colony_boundaries_2011"


def dbf_header(blob):
    if len(blob) < 33 or blob[0] not in (3, 0x83, 0x30):
        raise ValueError("Invalid original dBASE header")
    rows = int.from_bytes(blob[4:8], "little")
    length = int.from_bytes(blob[8:10], "little")
    if length < 33 or length > len(blob) or (length - 33) % 32 != 0:
        raise ValueError("DBF descriptor length mismatch")
    if blob[length - 1] != 13:
        raise ValueError("Missing DBF header terminator")
    fields = []
    for i in range(32, length - 1, 32):
        block = blob[i:i+32]
        fields.append({"name": block[:11].split(b"\x00", 1)[0].decode("ascii").strip(),
                       "type": chr(block[11]), "width": block[16],
                       "decimal_places": block[17]})
    if not fields:
        raise ValueError("No DBF fields")
    return {"records": rows, "fields": fields}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()
    result = {"status": "HOLD_SCHEMA", "original_gis_shape_rows_opened": 0,
              "original_dbf_data_rows_opened": 0}
    try:
        with requests.Session() as session:
            rows = manifest_rows(session, 2011)
            name = BASENAME + ".dbf"
            item = next((r for r in rows if r["name"] == name), None)
            if item is None:
                raise ValueError("Historic 2011 DBF missing from authentic directory")
            blob = secure_request(session, canonical_file_url(item["url"]))
        result.update(dbf_header(blob))
        result["source_sha256"] = hashlib.sha256(blob).hexdigest()
        result["status"] = "HEADER_VERIFIED_NO_DATA_ROWS"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {str(exc)[:220]}"
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    if result["status"] != "HEADER_VERIFIED_NO_DATA_ROWS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
