from pathlib import Path
import importlib.util

SCRIPT = Path(__file__).resolve().parents[1] / 'research/climate-penguin/work/abandonment/palmer_footprint_source_recovery.py'

def module():
    assert SCRIPT.exists(), 'source recovery implementation missing'
    spec=importlib.util.spec_from_file_location('footprint_recovery',SCRIPT)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj

def test_pdf_magic_not_html_challenge():
    m=module()
    assert m.valid_payload(b'%PDF-1.7\nabc', 'pdf')
    assert not m.valid_payload(b'<html>verify human</html>', 'pdf')

def test_empty_and_oversize_not_source_success():
    m=module()
    assert not m.valid_payload(b'', 'text')
    assert not m.valid_payload(b'x'*(m.MAX_BYTES+1), 'text')

def test_text_rejects_html_authentication_response():
    m=module()
    assert m.valid_payload(b'TORG: Torgersen\n', 'text')
    assert not m.valid_payload(b'<html>Please login</html>', 'text')

def test_manifest_never_calls_maps_polygons():
    m=module()
    assert len(m.SOURCES)==7
    assert len({x[0] for x in m.SOURCES})==7
    assert all(u.startswith('https://') for _,u,_ in m.SOURCES)
    assert all('dryad' not in u for _,u,_ in m.SOURCES)
    assert m.GEOMETRY_STATUS=='not_authenticated_colony_polygons'
