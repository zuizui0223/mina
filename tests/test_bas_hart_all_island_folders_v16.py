"""Tests for exact publisher group-ID folders, BAS Hart original file hierarchy."""
from __future__ import annotations
import base64
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import inventory_bas_hart_all_island_folders_v16 as v16


def publisher_id(path):
    return "synth:"+v16.BAS_ENTRY_ID+":"+base64.b64encode(
        path.encode("utf-8")).decode("ascii")


def row(path,typ="group"):
    ident=publisher_id(path)
    name=path.rsplit("/",1)[-1]
    url=(
        f"http://{v16.BAS_HOST}:443/repository/entry/get/{name}"
        f"?entryid={ident}&fileinline=true"
    ) if typ=="file" else ""
    return {"id":ident,"name":name,"type":typ,"url":url,"entry_url":
            f"http://{v16.BAS_HOST}:443/repository/entry/show?entryid={ident}"}


def test_original_id_based_group_lookups_not_only_publisher_url():
    root=v16.BAS_ENTRY_ID
    f=row("/Candlemas_Island")
    assert v16.validate_group_id(root)==root
    assert v16.decode_publisher_relative(f["id"])=="Candlemas_Island"
    assert v16.original_entry_url(f["id"]).startswith("https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=")
    assert v16.canonical_file_row(row("/Candlemas_Island/coordinates/CAND_2020_Adelie_coordinates.csv","file"),
                                  publisher_id("/Candlemas_Island/coordinates")
                                  )["top_level_source_locality_folder"]=="Candlemas_Island"
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        v16.validate_group_id("synth:ANOTHER_UUID:L0V2aWw=")


def test_complete_bounded_manifest_traverses_group_rows(monkeypatch):
    source_rows={
      "":[row("/Zavodovski"),row("/Beach_Point"),
          row("/SSI_count_results.csv","file")],
      "Zavodovski":[row("/Zavodovski/coordinates")],
      "Zavodovski/coordinates":[row("/Zavodovski/coordinates/ZAVO_2020_Macaroni_coordinates.csv","file")],
      "Beach_Point":[row("/Beach_Point/BP_2020_Chinstrap_coordinates.csv","file")]
    }
    def fake_manifest(session,url):
        parsed=__import__("urllib.parse",fromlist=["parse_qs","urlparse"])
        qs=parsed.parse_qs(parsed.urlparse(url).query)
        current=v16.decode_publisher_relative(qs["entryid"][0])
        return source_rows[current],{"source_csv_sha256":"abc","source_bytes":1234}
    monkeypatch.setattr(v16,"original_bas_manifest",fake_manifest)
    r=v16.traverse_publisher_archives(None)
    assert r["publisher_directory_manifest_SHA_receipts"] and len(r["publisher_directory_manifest_SHA_receipts"])==4
    assert r["original_file_types"]=={"csv":3}
    assert r["original_filename_inventory_total"]==3
    assert r["status"]=="HOLD_INCOMPLETE_ORIGINAL_SOURCE_FILE_MANIFEST"
    assert r["original_penguin_nest_coordinate_rows_read"]==0
    assert all(x["source_file_url_https"].startswith("https://") for x in r["original_all_file_metadata_only"])


def test_publisher_file_cannot_escape_original_group():
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        v16.canonical_file_row(
            row("/Ashen_Hills/2020.csv","file"),
            publisher_id("/Candlemas_Island"))
