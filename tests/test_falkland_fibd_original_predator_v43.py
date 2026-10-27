"""V43 original Falklands biodiversity database public-source/absence QA (synthetic)."""
from __future__ import annotations
import io
import json
from pathlib import Path
import sys

import pytest
import xlwt

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_falkland_fibd_original_predator_v43 as v


def invent_xls():
    """Invented non-personal island IDs, field/desktop visit summaries and statuses."""
    book=xlwt.Workbook()
    sh=book.add_sheet("Invasive species")
    for c,name in enumerate(("Island ID","Visit ID","Norway rat","Black rat","House mouse","Survey date")):
        sh.write(0,c,name)
    for i in range(15):
        sh.write(i+1,0,1000+i)
        sh.write(i+1,1,2000+i)
        sh.write(i+1,2,"present" if i<12 else "inferred absent")
        sh.write(i+1,3,"unknown")
        sh.write(i+1,4,"survey unknown")
        sh.write(i+1,5,"2011-09-01")
    second=book.add_sheet("Visits")
    second.write(0,0,"Island ID")
    second.write(0,1,"Visit ID")
    second.write(0,2,"Method")
    for i in range(15):
        second.write(i+1,0,1000+i)
        second.write(i+1,1,2000+i)
        second.write(i+1,2,"desktop" if i%2 else "field")
    handle=io.BytesIO()
    book.save(handle)
    return handle.getvalue()


def test_original_xls_schema_no_raw_identity_rows_in_receipt():
    tables=v.inspect_xls_sheets(invent_xls(),"fibdv8-20140601-invasives")
    assert len(tables)==2
    inv=tables[0]
    assert inv["source_nonempty_sheet_rows"]==16
    assert inv["candidate_header_row_index_0based"]==0
    assert "Norway rat" in inv["literal_rat_header_candidates"]
    assert inv["original_key_cardinality"][0]["distinct_original_key_values"]==15
    assert "2011-09-01" not in json.dumps(tables)
    assert "present" in json.dumps(inv["rat_status_value_distributions_only_if_explicit_header"])
    assert all("0001" not in json.dumps(t) for t in tables)


def test_source_not_arbitrary_license_or_private_dataset(monkeypatch):
    def fake_get(session,url,nbytes):
        return json.dumps({
          "success":True,
          "result":{
            "name":"fibdv8-20140601-invasives",
            "private":True,
            "license_id":"CC-BY-SA-4.0",
            "resources":[],
          },
        }).encode()
    monkeypatch.setattr(v,"bounded_https",fake_get)
    with pytest.raises(ValueError,match="PRIVATE"):
        v.get_official_package(None,"fibdv8-20140601-invasives")


def test_public_resource_host_and_portal_metadata_flags(monkeypatch):
    pkg={
       "success":True,
       "result":{
         "name":"fibdv8-20140601-locations",
         "private":False,
         "license_id":"CC-BY-SA-4.0",
         "saeri_unique_resource_id":"FK-FIG-13",
         "saeri_access_limitations":"open",
         "resources":[{
           "id":"safe_source_id",
           "format":"XLS",
           "name":"fidb_locations_20140601.xls",
           "url":"http://dataportal.saeri.org/dataset/aaa/resource/bbb/download/c.xls",
           "restricted":json.dumps({"allowed_users":"","level":"public"}),
           "size":460000,
           "state":"active",
         }],
       },
    }
    monkeypatch.setattr(v,"bounded_https",lambda *_:json.dumps(pkg).encode())
    resource,metadata=v.get_official_package(None,"fibdv8-20140601-locations")
    assert resource["url"].startswith("http://dataportal.saeri.org")
    assert metadata["license"]=="CC-BY-SA-4.0"
    assert metadata["source_download_restricted_level"]=="public"
    assert metadata["source_dataset_private"] is False
    assert metadata["source_metadata_unique_resource_id"]=="FK-FIG-13"


def test_no_slugs_beyond_frozen_fibd():
    assert len(v.ORIGINAL_DATASETS)==5
    with pytest.raises(ValueError,match="UNREGISTERED_SOURCE_SLUG"):
        v.get_official_package(None,"private-unrelated-fig-surveys")


def test_no_untrusted_hosts_or_insecure_non_publisher_request():
    with pytest.raises(ValueError,match="NON_PUBLISHER_PUBLIC_RESOURCE_HOST"):
        v.bounded_https(None,"https://example.com/secret.xls",100)
    with pytest.raises(ValueError,match="INSECURE_SOURCE_SCHEME"):
        v.bounded_https(None,"ftp://dataportal.saeri.org/secret.xls",100)
