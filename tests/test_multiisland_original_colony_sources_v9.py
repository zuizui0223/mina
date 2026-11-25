"""Publisher-only AADC and BAS original archive inventory QA."""
from __future__ import annotations
import io
import csv
import sys
from pathlib import Path
from urllib.parse import quote
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_multiisland_original_colony_sources_v9 import (
    AADC_TARGET,AADC_PREFIX,BAS_ENTRY_ID,BAS_HOST,
    aadc_catalogue,bas_validate_source,bas_folder_target,
    bas_file_row_is_publisher,original_bas_manifest
)


def test_aadc_parent_and_child_not_lookalikes():
    rows=[
      {"metadata_entry_id":"AAS_4088_Adelie_breeding_colony_boundaries",
       "eds_id":123,"uuid":"00000000-0000-0000-0000-000000000001"},
      {"metadata_entry_id":"AAS_4088_Adelie_occupancy_Vestfold_2009",
       "eds_id":124,"uuid":"00000000-0000-0000-0000-000000000002"},
      {"metadata_entry_id":"AAS_4088_Adelie_XYZ_unrelated"},
      {"metadata_entry_id":"AAS_4088_Adelie_occupancy", "eds_id":4},
      {"metadata_entry_id":"AAS_4088_Adelie_breeding_colony_boundaries_fake"},
    ]
    data,receipt=aadc_catalogue(rows)
    assert len(data)==2
    assert receipt["potential_polygon_parent_records"]==1
    assert receipt["source_registry_matching_parent_and_children"]==2
    assert receipt["publisher_breeding_data_rows_opened"]==0


def test_bas_manifest_never_leaves_verified_dataset():
    folder=f"synth:{BAS_ENTRY_ID}:L1phdm9kb3Zza2kvY29vcmRpbmF0ZXM="
    url=f"https://{BAS_HOST}/repository/entry/show?entryid={quote(folder,safe='')}&output=default.csv"
    assert bas_validate_source(url)==folder
    assert bas_folder_target({"url":url})==url
    assert bas_folder_target({"url":"https://malware.example/repository/entry/show?entryid="+folder}) is None
    assert bas_folder_target({"url":"https://"+BAS_HOST+"/repository/entry/show?entryid=OTHER"}) is None
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        bas_validate_source("http://"+BAS_HOST+"/repository/entry/show?entryid="+BAS_ENTRY_ID)


def test_original_csv_nested_directory_and_csv_file_distinction():
    folder=f"synth:{BAS_ENTRY_ID}:L1phdm9kb3Zza2kvY29vcmRpbmF0ZXM="
    rawf=f"https://{BAS_HOST}/repository/entry/get/ZAVO_2020_Macaroni_coordinates.csv?entryid={quote(folder,safe='')}"
    assert bas_file_row_is_publisher({"name":"ZAVO_2020_Macaroni_coordinates.csv","url":rawf})
    assert bas_folder_target({"name":"ZAVO_2020_Macaroni_coordinates.csv","url":rawf}) is None
    assert not bas_file_row_is_publisher({"url":"https://evil.example/file.csv"})


class FakeSession:
    def __init__(self,raw):
        self.raw=raw
    def get(self,*args,**kwargs):
        return FakeResponse(self.raw,args[0])


class FakeResponse:
    def __init__(self,data,url):
        self.body=data;self.url=url;self.headers={"Content-Type":"text/csv"}
        self.status_code=200
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def raise_for_status(self):pass
    def iter_content(self,size):
        yield self.body


def test_original_directory_listing_bounded_csv_header_only():
    root=f"https://{BAS_HOST}/repository/entry/show?entryid={BAS_ENTRY_ID}&output=default.csv"
    csvtext=("name,url,size\\nZAVO_2020_Macaroni_coordinates.csv,"
             f"https://{BAS_HOST}/repository/entry/get/ZAVO_2020_Macaroni_coordinates.csv,10323\\n").replace("\\n","\n")
    rows,metadata=original_bas_manifest(FakeSession(csvtext.encode()),root)
    assert len(rows)==1
    assert rows[0]["name"]=="ZAVO_2020_Macaroni_coordinates.csv"
    assert metadata["original_publisher_file_biological_rows_opened"]==0
    assert metadata["source_bytes"]==len(csvtext.encode())
