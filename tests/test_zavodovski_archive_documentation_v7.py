import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/probe_zavodovski_archive_documentation_v7.py"
spec=importlib.util.spec_from_file_location("probe",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def test_only_explicit_csv_documentation_link():
    html='<a href="/repository/entry/get/layer_descriptions.csv">CSV</a><a href="/repository/entry/get/chinstrap_2011.shp">polygon</a>'
    assert m.documentation_links(html)==["https://ramadda.data.bas.ac.uk/repository/entry/get/layer_descriptions.csv"]
def test_external_host_rejected():
    assert m.documentation_links('<a href="https://example.org/layer_descriptions.csv">bad</a>')==[]
def test_no_invented_links():
    assert m.documentation_links('<div>layer_descriptions.csv</div>')==[]
