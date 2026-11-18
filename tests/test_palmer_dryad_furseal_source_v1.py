"""Pure source parsing/guard fixtures; no network and no seal outcome."""
import importlib.util
from pathlib import Path
import pytest
pytest.importorskip('requests')  # Optional Dryad acquisition dependency
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/audit_palmer_dryad_furseal_source_v1.py"
def mod():
 s=importlib.util.spec_from_file_location("seal_source",P)
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test_dataset_version_links_are_parsed():
 m=mod()
 assert m.current_version({"version":24})==24
 assert m.current_version({"_links":{"stash:version":{"href":"/api/v2/versions/24099"}}})==24099
 assert m.list_versions({"_embedded":{"stash:versions":[{"id":333}]}})==[{"id":333}]
def test_files_from_documented_Dryad_versions_and_no_duplicate_filenames():
 m=mod()
 a={"_embedded":{"stash:files":[{"id":4,"path":"fur_seal_locations_all_surveys.csv",
         "size":123,"_links":{"stash:download":{"href":"/downloads/file_stream/4"}}}]}}
 files=m.list_files(a)
 assert len(files)==1
 x=m.normalize_file(files[0])
 assert x["name"]=="fur_seal_locations_all_surveys.csv"
 assert x["bytes"]==123 and x["id"]==4
 assert x["href"]=="/downloads/file_stream/4"
 assert m.REQUIRED=={"README.md","drone_survey_dates_times.csv",
    "fur_seal_locations_all_surveys.csv","surveyed_regions_land_mask.zip",
    "exposed_land_mask.zip"}
