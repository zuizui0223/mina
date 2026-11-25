"""Original 2026 NZ source location metadata, guarded from false geography."""
import importlib.util,json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("rossloc",ROOT/"scripts/audit_nz_39_colony_location_source_v15.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def sample_record(url="https://datastore.landcareresearch.co.nz/dataset/xyz/resource/colony-locations.xlsx",md5="a"*32):
    return json.dumps({"success":True,"result":{
       "id":m.LOC_ID,"format":"XLSX","url":url,"hash":md5,
       "size":13253,"name":"Adelie Aerial Survey Information"}}).encode()

def test_original_location_resource_explicit_md5_source():
    r=m.resource_metadata(sample_record())
    assert r["md5"]=="a"*32
    assert r["official_url"].startswith("https://datastore.landcareresearch.co.nz/")
    assert r["filename"]=="Adelie Aerial Survey Information"

def test_no_unverified_resource_or_third_party_file():
    z=json.loads(sample_record())
    z["result"]["id"]="5fd490e5-92c4-4f2c-a82e-c66db2320eb1"
    with pytest.raises(ValueError,match="resource ID"):
        m.resource_metadata(json.dumps(z).encode())
    with pytest.raises(ValueError,match="HTTPS"):
        m.resource_metadata(sample_record(url="https://github.com/foo.xlsx"))
    with pytest.raises(ValueError,match="hash"):
        m.resource_metadata(sample_record(md5="not-a-real-checksum"))

def test_only_normalize_literal_site_keys_no_geographical_substitutions():
    assert m.clean_name(" Cape  Royds ")=="cape royds"
    assert m.clean_name("Bird North")=="bird north"
    assert m.clean_name("Cape Bird North")!="bird north"
    assert m.LOC_ID!="5fd490e5-92c4-4f2c-a82e-c66db2320eb1"

def test_v15_initial_scope_blocks_arbitrary_island_independence():
    d=json.loads((ROOT/"contracts/ROSS_NZ_39_COLONY_GEOLOCATION_CROSSWALK_SOURCE_V15.json").read_text())
    assert d["original_location_rows_read"]==0
    assert not d["causal_recruitment_or_pioneer_success_effect_estimated"]
    assert d["locked_Ecology_PR189_unchanged"]

def test_official_location_metadata_without_md5_is_not_claimed_verified():
    r=m.resource_metadata(sample_record(md5=""))
    assert r["md5"] is None
    assert r["md5_status"]=="OFFICIAL_PUBLISHER_MD5_NOT_PROVIDED"
