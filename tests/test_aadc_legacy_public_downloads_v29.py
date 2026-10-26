"""Original AADC EDS source probe metadata only; avoid loading actual nest CSV."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from probe_aadc_legacy_public_downloads_v29 import final_host_ok, SOURCE_ITEMS, CAP


def test_no_nonpublisher_source_host_or_url():
    assert final_host_ok("https://data.aad.gov.au/eds/5210/download")
    assert final_host_ok("https://maps.aad.gov.au/survey/attachment.zip")
    assert not final_host_ok("http://data.aad.gov.au/eds/5210/download")
    assert not final_host_ok("https://data.aad.gov.au.evil.example/eds/5210/download")
    assert not final_host_ok("https://s3.amazonaws.com/public/petrel.zip")
    assert list(SOURCE_ITEMS)==[
       "VESTFOLD_CAPE_PETREL_ISLAND_SURVEY",
       "BECHERVAISE_ADELIE_FIELD_NEST_LOCATIONS",
       "WINDMILL_MULTITAXON_FIELD_BIRD_GIS"]
    assert CAP<=128*1024
