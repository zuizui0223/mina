"""Offline tests for Palmer source-only STAC audit."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/climate-penguin/work/abandonment/palmer_abandonment_stac_inventory.py"
spec = importlib.util.spec_from_file_location("p0_stac", SCRIPT)
src = importlib.util.module_from_spec(spec)
spec.loader.exec_module(src)


def test_season_calendar_and_bbox():
    q = list(src.queries(2006, 2008, ("landsat", "sentinel")))
    assert [(s, y) for s, y, _ in q] == [("landsat", 2006), ("landsat", 2007), ("landsat", 2008)]
    assert q[1][2]["datetime"].startswith("2007-02-01")
    assert all(src.BBOX[0] < site["longitude"] < src.BBOX[2] and
               src.BBOX[1] < site["latitude"] < src.BBOX[3] for site in src.SITES.values())


def test_unique_scene_and_date_not_a_pixel():
    def fake(_url, _body, *, method):
        assert method == "POST"
        page = {"features": [
            {"id": "X", "collection": "landsat-c2-l2",
             "properties": {"datetime": "2008-02-09T12:00:00Z", "eo:cloud_cover": 12}},
            {"id": "X", "collection": "landsat-c2-l2",
             "properties": {"datetime": "2008-02-09T12:00:00Z", "eo:cloud_cover": 12}},
            {"id": "Y", "collection": "landsat-c2-l2",
             "properties": {"datetime": "2008-02-09T14:00:00Z", "eo:cloud_cover": 50}},
            {"id": "Z", "collection": "landsat-c2-l2",
             "properties": {"datetime": "2008-03-02T12:00:00Z"}},
        ]}
        return page, json.dumps(page).encode()
    row, items, receipt = src.audit_query("landsat", 2008, {}, fetcher=fake)
    assert row["status"] == "ok" and row["scenes"] == 3
    assert row["distinct_dates"] == 2 and row["scene_cloud_under_20"] == 1
    assert row["season_start_year"] == 2007
    assert len(receipt["sha256_pages"]) == 1


def test_missing_is_not_empty_catalog():
    def empty(_url, _body, *, method):
        return {"features": []}, b'{"features":[]}'
    row, _, _ = src.audit_query("landsat", 2008, {}, fetcher=empty)
    assert row["status"] == "ok" and row["scenes"] == 0
    def failure(*_args, **_kwargs):
        raise IOError("offline")
    err, _, _ = src.audit_query("landsat", 2008, {}, fetcher=failure)
    assert err["status"] == "error"
    data = [{**row, "year": 2006}, {**row, "year": 2007, "scenes": 1}, {**err, "year": 2008}]
    support = src.period_support(data, "landsat", 2006, 2008)
    assert support["failed_years"] == 1 and support["years_with_scene"] == 1
    assert not support["supports_3_calendar_years_at_scene_level"]


def test_wrong_month_and_year_are_not_accepted():
    def wrong(_url, _body, *, method):
        page = {"features": [{"id": "x", "collection": "landsat-c2-l2",
                              "properties": {"datetime": "2009-05-01T12:00:00Z"}}]}
        return page, json.dumps(page).encode()
    result, _, _ = src.audit_query("landsat", 2009, {}, fetcher=wrong)
    assert result["status"] == "error" and "month" in result["error"]


def test_pagination_never_exits_provider():
    assert src.next_spec({"links": [{"rel": "next", "href": "?page=2"}]},
                         "https://example.org/x", {}) == ("https://example.org/x?page=2", None, "GET")
    try:
        src.next_spec({"links": [{"rel": "next", "href": "https://evil.example/x"}]},
                      "https://example.org/x", {})
        assert False
    except ValueError:
        pass
