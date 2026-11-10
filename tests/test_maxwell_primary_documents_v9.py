import importlib.util
from pathlib import Path
import pytest
P=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/maxwell_primary_documents_v9.py'
def module():
    spec=importlib.util.spec_from_file_location('maxwell_docs_v9',P)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_magic_not_web_error():
    m=module()
    with pytest.raises(ValueError,match='PDF'):m.validate_bytes(b'<html>error</html>')

def test_verified_size_and_sha():
    m=module();raw=b'%PDF-1.7\n'+b'x'*1000
    out=m.validate_bytes(raw)
    assert out['bytes']==len(raw) and len(out['sha256'])==64

def test_empty_document_does_not_succeed():
    m=module()
    with pytest.raises(ValueError):m.validate_bytes(b'%PDF')

def test_source_urls_and_fixed_selection():
    m=module()
    assert set(m.SOURCES)=={'UBA2025','ASPA171_2024'}
    assert '63_2025_texte.pdf' in m.SOURCES['UBA2025']
    assert m.SOURCES['ASPA171_2024']=='https://documents.ats.aq/recatt/att783_e.pdf'
