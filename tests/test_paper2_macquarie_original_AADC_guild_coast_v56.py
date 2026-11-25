"""Synthetic V56 AADC original Macquarie GIS metadata source checks only."""
import io,sys,zipfile
from pathlib import Path
import pytest
import shapefile
from pyproj import CRS

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_paper2_macquarie_original_AADC_guild_coast_v56 as m


def fake_zip(include_prj=True):
    sh,shx,dbf=io.BytesIO(),io.BytesIO(),io.BytesIO()
    with shapefile.Writer(shp=sh,shx=shx,dbf=dbf,shapeType=shapefile.POINT) as w:
        w.field("BIRD_SPP","C",size=40)
        w.field("CENSUSYEAR","N",size=4)
        for n in range(3):
            w.point(400000+n,3950000+n)
            w.record("SyntheticSpecies"+str(n),2024)
    buff=io.BytesIO()
    with zipfile.ZipFile(buff,"w") as z:
        for ext,v in ((".shp",sh),(".shx",shx),(".dbf",dbf)):
            z.writestr("macquarie_2024/sample_guild"+ext,v.getvalue())
        if include_prj:
            z.writestr("macquarie_2024/sample_guild.prj",CRS.from_epsg(32757).to_wkt())
    return buff.getvalue()


def test_four_exact_original_AADC_files_are_frozen_and_one_island():
    assert set(m.ORIGINAL)=={
        "Macquarie_2023_24_both_bird_guilds",
        "Macquarie_2000_flying_bird_colony_GIS",
        "Macquarie_historical_penguin_colony_GIS",
        "Macquarie_original_1_to_50k_coast_GIS",
    }
    assert all(x["download_url"].startswith("https://data.aad.gov.au/eds/")
               for x in m.ORIGINAL.values())
    assert m.ORIGINAL["Macquarie_2023_24_both_bird_guilds"]["source_doi"]=="10.26179/98ra-0751"


def test_first_party_aadc_host_does_not_follow_non_aadc_or_non_https():
    assert m.official_source_host("https://data.aad.gov.au/eds/6113/download")
    assert m.official_source_host("https://transfer.data.aad.gov.au/a/b.zip")
    assert m.official_source_host("https://x.antarctica.gov.au/blob")
    assert not m.official_source_host("http://data.aad.gov.au/eds/6113/download")
    assert not m.official_source_host("https://google.com/penguins.shp")
    assert not m.official_source_host("https://maliciousaad.gov.au.fake.com/archive")


def test_native_source_shapefile_original_header_only_from_zip():
    desc=m.source_file_structure(fake_zip())
    assert desc["source_file_format"]=="ZIP_ARCHIVE"
    assert desc["native_shapefile_layers_n"]==1
    assert desc["original_readable_shapefile_header_layers_n"]==1
    layer=desc["native_source_layer_structures_without_raw_rows"][0]
    assert layer["original_source_record_count"]==3
    assert layer["original_shape_type_code"]==shapefile.POINT
    assert layer["original_PRJ_EPSG_if_unambiguous"]==32757
    assert "BIRD_SPP" in layer["original_source_DBF_field_names_only"]
    assert "SyntheticSpecies0" not in str(desc)
    assert layer["original_site_names_and_coordinates_published"] is False


def test_incomplete_native_projection_does_not_impute_CRS():
    desc=m.source_file_structure(fake_zip(include_prj=False))
    layer=desc["native_source_layer_structures_without_raw_rows"][0]
    assert layer["original_PRJ_EPSG_if_unambiguous"] is None


def test_malicious_zip_path_rejected_without_reading_source_data():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("../outside.shp","not real GIS")
    with pytest.raises(ValueError,match="UNSAFE_OR_ENCRYPTED"):
        m.source_file_structure(b.getvalue())


def test_tabular_header_only_has_no_original_bird_observations():
    raw=b"Species,Colony_ID,Census_Year\nEudyptes,SecretSensitiveSite,2023\n"
    q=m.source_file_structure(raw)
    assert q["source_file_format"]=="TABULAR_TEXT_HEADER_ONLY"
    assert q["original_safe_column_count"]==3
    assert "SecretSensitiveSite" not in str(q)


def test_no_html_authentication_forms_accepted_as_animal_data():
    assert m.source_file_structure(b"Plain binary data unknown")["source_file_format"]=="UNRECOGNIZED_NATIVE_SOURCE"
