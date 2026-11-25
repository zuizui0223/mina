import pytest
pytest.importorskip('requests')
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_zavodovski_lynch2011_categories_v14 import categories_from_dbf

def fake_dbf(labels):
    width_species=50; width_area=19
    h=bytearray(97)
    h[0]=3
    h[4:8]=len(labels).to_bytes(4,"little")
    h[8:10]=(97).to_bytes(2,"little")
    h[10:12]=(1+width_species+width_area).to_bytes(2,"little")
    h[32:43]=b"species"+b"\x00"*4
    h[43]=ord("C");h[48]=width_species
    h[64:75]=b"area"+b"\x00"*7
    h[75]=ord("N");h[80]=width_area;h[81]=11;h[96]=13
    for label in labels:
        h.extend(b" "+label.encode().ljust(50)+b"1.0".rjust(19))
    return bytes(h)

def test_coded_mixed_is_not_reallocated():
    o=categories_from_dbf(fake_dbf(["CHPE","MCPE","MIXED","MIXED"]))
    assert o["category_counts"]=={"CHPE":1,"MCPE":1,"MIXED":2}
    assert o["shape_rows_opened"]==0
