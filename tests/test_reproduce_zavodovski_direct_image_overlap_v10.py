"""Synthetic metadata tests only; no original biological shapefile rows."""
import importlib.util
from pathlib import Path
from urllib.parse import quote
import pytest
pytest.importorskip('requests')

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "scripts" / "reproduce_zavodovski_direct_image_overlap_v10.py"
spec = importlib.util.spec_from_file_location("source_gate", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_original_source_dictionary_frozen():
    rows = m.audit_dictionary(ROOT / "sources" / "bas_zavodovski_layer_descriptions_v1.csv")
    assert len(rows) == 28
    assert {2011, 2016, 2025} == set(m.FOLDERS)
    assert m.DATES[2016] == "09/01/2016"


def test_no_imputed_or_composite_layers_in_primary_roster():
    names = [f for year in m.DATES for f in m.NAMES(year)]
    assert len(names) == 9
    assert len(set(names)) == 9
    assert not any("under_cloud" in f or "2020-22" in f for f in names)


def test_ramadda_file_url_rejects_nonpublisher():
    good = ("http://ramadda.data.bas.ac.uk:443/repository/entry/get/cloud_cover_2011.shp?"
            "entryid=synth%3A7220dc6b-2f52-4160-a6c0-e57c50963308%3Aabc&fileinline=true")
    assert m.canonical_file_url(good).startswith("https://ramadda.data.bas.ac.uk/repository/entry/get/")
    with pytest.raises(ValueError):
        m.canonical_file_url(good.replace("ramadda.data.bas.ac.uk", "example.org"))
    with pytest.raises(ValueError):
        m.canonical_file_url("https://ramadda.data.bas.ac.uk/repository/entry/get/a.shp?entryid=fake")


def test_manifest_schema_and_original_year_closure():
    for year in (2011, 2016, 2025):
        assert all(str(year) in name for name in m.NAMES(year))
        assert all(ext in m.SUFFIXES for ext in (".shp", ".dbf", ".shx", ".prj"))
