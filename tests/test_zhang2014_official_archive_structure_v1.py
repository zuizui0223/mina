"""Offline HTML fixtures for source-only Zhang 2014 archive link gate."""
import importlib.util
from pathlib import Path

FILE=Path(__file__).resolve().parents[1]/"scripts/probe_zhang2014_official_archive_structure_v1.py"
spec=importlib.util.spec_from_file_location("zhang_archive",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_literal_archive_name_without_real_link_cannot_pass():
    h='<html><body>PanAnta.PenguinColony.rar <form><a href="javascript:__doPostBack(\'ctl\',\'1\')">Download</a></form></body></html>'
    d=m.inspect_page(h)
    assert d["archive_literal_on_page"] is True
    assert d["verified_direct_archive_urls"]==[]
    assert d["status"]=="HOLD_NO_STATIC_VERIFIED_OFFICIAL_ARCHIVE_HREF"
    assert d["no_archive_download_or_biology_executed"]


def test_only_verified_static_official_host_href_can_qualify():
    h='<a href="https://www.geodoi.ac.cn/assets/PanAnta.PenguinColony.rar">Download</a>'
    d=m.inspect_page(h)
    assert d["status"]=="STATIC_OFFICIAL_ARCHIVE_HREF_FOUND"
    assert d["verified_direct_archive_urls"]==[
       "https://www.geodoi.ac.cn/assets/PanAnta.PenguinColony.rar"]
    assert d["no_archive_download_or_biology_executed"]


def test_untrusted_host_cannot_become_download_endpoint():
    h='<a href="https://unknown.example/PanAnta.PenguinColony.rar">Download</a>'
    d=m.inspect_page(h)
    assert d["verified_direct_archive_urls"]==[]
    assert d["status"].startswith("HOLD")
