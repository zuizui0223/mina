import pytest
pytest.importorskip('requests')
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_zavodovski_lynch2011_dbf_header_v12 import dbf_header

def test_synthetic_dbf_header_without_data_rows():
    header = bytearray(97)
    header[0] = 3
    header[4:8] = (7).to_bytes(4, "little")
    header[8:10] = (97).to_bytes(2, "little")
    header[10:12] = (20).to_bytes(2, "little")
    header[32:43] = b"SPECIES" + b"\x00" * 4
    header[43] = ord("C")
    header[48] = 5
    header[64:75] = b"NEST_AREA" + b"\x00" * 2
    header[75] = ord("N")
    header[80] = 9
    header[81] = 3
    header[96] = 13
    x = dbf_header(bytes(header))
    assert x["records"] == 7
    assert [f["name"] for f in x["fields"]] == ["SPECIES", "NEST_AREA"]
