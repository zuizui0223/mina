import importlib.util
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/seaice_catalog_probe_v4.py'
def mod():
    assert SCRIPT.exists(), 'catalog parser not implemented'
    sp=importlib.util.spec_from_file_location('seaice_probe',SCRIPT)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def test_catalog_resolves_source_refs_and_preserves_data_urlpath():
    m=mod()
    xml=b'<catalog xmlns="http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0" xmlns:xlink="http://www.w3.org/1999/xlink"><catalogRef xlink:href="monthly/catalog.xml" name="monthly v3p1"/><dataset name="original.nc" urlPath="osisaf/example.nc"/></catalog>'
    d=m.parse_catalog(xml,'https://thredds.met.no/thredds/catalog/osisaf/catalog.xml')
    assert d['refs'][0]['url']=='https://thredds.met.no/thredds/catalog/osisaf/monthly/catalog.xml'
    assert d['datasets'][0]['url_path']=='osisaf/example.nc'

def test_external_refs_and_html_fail_without_false_source_success():
    m=mod()
    try:
        m.parse_catalog(b'<html>login</html>','https://thredds.met.no/thredds/catalog/test.xml')
        assert False
    except ValueError:pass
    xml=b'<catalog xmlns:xlink="http://www.w3.org/1999/xlink"><catalogRef xlink:href="https://elsewhere.invalid/source"/></catalog>'
    assert m.parse_catalog(xml,'https://thredds.met.no/thredds/catalog/test.xml')['refs']==[]
