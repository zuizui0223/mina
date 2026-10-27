"""V43b SOURCE-ONLY invented native island/invader/visit schema tests."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_falkland_fibd_island_visit_join_v43b as m


def fixture_islands(n=40):
    location=[("Location Name","Wider Area","DOS sheet(s)","Category","Latitude","Longitude","Lat/long origin","Area (ha)","Area origin","Within IBA?","Within IPA?","Status","Status date","Max Elevation (m)","Other notes","Owner","Last updated")]
    invasives=[];visits=[("ID","Location Name","Latitude","Longitude","ENGLISH NAME","CATEGORY","Day","Month","Year","Surveyors","Organisations","Notes on visit","Full reference")]
    for i in range(n):
        name=f"Imaginary Island {i:03d}"
        lat=-51.5+(i%4)*.04
        lon=-60.3-(i//4)*.04
        location.append((name,"Fake Area",None,"island",lat,lon,"GPS",10+i,"survey",None,None,"island",None,10,None,None,None))
        invader="Norway rat" if i<24 else "House mouse"
        invasives.append((name,"Fake Area",lat,lon,None,None,None,invader,
                         "present" if i<12 else "absent",None,None,None,None,None,None,None,None,None))
        visits.append((None,name,lat,lon,None,None,10,6,2011,None,None,
                       "desktop imagery assessment" if i%3==0 else "field survey with GPS",
                       None))
    return location,invasives,visits


def test_source_name_normalization_is_exact_without_fuzzy_alias():
    assert m.normalized_name("  NEW  ISLAND  ")=="new island"
    assert m.normalized_name("New-Island")!="new island"
    assert m.normalized_name("Island A")!=m.normalized_name("Island B")


def test_native_original_rat_record_has_no_header_and_taxa_col8():
    loc,inv,vis=fixture_islands()
    qa,column=m.schema_profile_invasives(inv)
    assert qa["native_source_first_row_has_NO_EXPLICIT_HEADERS"]
    assert column==7
    assert qa["source_candidate_taxon_column_1indexed"]==8
    assert qa["known_original_mammal_labels_by_source_row"]=={"Norway rat":24,"House mouse":16}
    assert qa["original_species_status_distributions_by_source_column"][8]["repeated_explicit_status_vocabulary"]["present"]==12


def test_original_island_location_table_and_strict_coordinates_match():
    loc,inv,vis=fixture_islands()
    reference,qa=m.source_location_reference(loc)
    assert len(reference)==40
    assert qa["original_location_rows_excluding_header"]==40
    match=m.identify_exact_invasive_location_links(inv,reference)
    assert match["source_invasive_rows_unique_exact_location_name_in_original_reference"]==40
    assert match["name_matched_rows_with_coordinate_difference_le250m"]==40
    assert match["invasive_lat_col_1indexed"]==3
    assert match["invasive_lon_col_1indexed"]==4
    assert match["unmatched_original_invasive_observation_rows"]==0


def test_duplicate_reference_location_name_not_counted_as_unique_island():
    loc,inv,vis=fixture_islands()
    loc.append(loc[1])
    ref,qa=m.source_location_reference(loc)
    assert len(ref)==39
    assert qa["colliding_names_excluded_from_exact_match"]==1


def test_visits_are_not_field_verified_rat_absences():
    loc,inv,vis=fixture_islands()
    ref,qa=m.source_location_reference(loc)
    out=m.original_visit_summary(vis,ref)
    assert out["original_visits_after_native_header"]==40
    assert out["distinct_original_exactly_matched_islands_with_any_visits"]==40
    assert out["survey_method_note_text_nonexclusive_hints"]["TEXT_HINT_DESKTOP_NOT_VERIFIED_FIELD_VISIT"]>0
    assert out["original_explicit_rat_survey_negative_test_results_detected"] is False
    assert out["island_visit_does_NOT_imply_targeted_mammal_negative"] is True


def test_no_inventory_without_pinned_FIG_official_original_file():
    with pytest.raises(ValueError,match="OUTSIDE_FROZEN_ORIGINAL_SOURCE_SET"):
        m.source_table_public("private-nonfrozen-dataset")


def test_haversine_m_numeric_units_metres():
    assert m.haversine_m(-51.3,-59.4,-51.3,-59.4)==0
    assert m.haversine_m(None,-59.4,-51.3,-59.4) is None
    assert m.haversine_m(-51.3,-59.4,-51.3,-59.397)>100
