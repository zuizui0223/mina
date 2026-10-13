"""Synthetic CSV schema inputs only; original nest counts remain unread."""
import importlib.util
from pathlib import Path
import pytest
pytest.importorskip("requests")
src=Path(__file__).resolve().parents[1]/"scripts"/"probe_zavodovski_ground2011_header_v19.py"
s=importlib.util.spec_from_file_location("ground_header",src)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

def test_no_coordinate_source_is_hold_even_with_site_id():
    r=m.schema_gate(["SubColony_ID","Nest_Count","Colony_Area","Density"])
    assert r["status"]=="HOLD_NO_COORDINATE_COLUMNS_IN_THIS_CSV"
    assert r["original_biological_rows_parsed"]==0

def test_lat_lon_source_is_only_potential_not_success():
    r=m.schema_gate(["plot","decimal latitude","decimal longitude","nest count"])
    assert r["status"].startswith("POTENTIAL_COORDINATE_HEADER")
    assert r["candidate_georeference_columns"]["latitude_longitude"] is True
    assert r["original_count_values_parsed"]==0

def test_duplicate_names_are_preserved_without_joining():
    q=m.schema_gate(["latitude","LATITUDE"])
    assert q["status"] == "HOLD_AMBIGUOUS_FIRST_CSV_HEADER"
    assert q["spatial_join_eligible"] is False
    assert q["original_columns"] == ["latitude","LATITUDE"]


def test_metadata_preamble_is_skipped_without_reading_the_first_biological_row():
    import io
    raw=io.BytesIO(b"# id: 10.5285/fake\r\n# license: public\r\n\r\nsubcolony,latitude,longitude,nests\r\nA01,-56.3,-27.6,135\r\n")
    line, metadata=m.first_noncomment_header(raw.readline)
    assert line == b"subcolony,latitude,longitude,nests\r\n"
    assert metadata["preamble_line_count"] == 3
    assert raw.readline() == b"A01,-56.3,-27.6,135\r\n"


def test_bounded_preamble_fails_closed():
    import io
    stream=io.BytesIO((b"# source metadata\n"*41)+b"x,y\n100,200\n")
    with pytest.raises(ValueError,match="preamble too long"):
        m.first_noncomment_header(stream.readline)
