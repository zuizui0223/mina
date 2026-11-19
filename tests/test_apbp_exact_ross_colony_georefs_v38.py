"""V38 synthetic exact source locality with independent coordinate metadata, no abundance."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_apbp_exact_ross_colony_georefs_v38 as v

def source():
    return {"site_to_named_island_crosswalk":[
      {"original_census_colony":"Cape Bird North",
       "publisher_explicit_island_group":"Ross Island",
       "original_site_coordinate_approx_lat":-77.2,
       "original_site_coordinate_approx_lon":166.4},
      {"original_census_colony":"Beaufort Island",
       "publisher_explicit_island_group":"Beaufort Island",
       "original_site_coordinate_approx_lat":-76.9,
       "original_site_coordinate_approx_lon":167.05}
    ]}

def test_source_locality_exact_only_and_ambiguity_never_promoted():
    tr=v.Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    x,y=tr.transform(166.405,-77.203)
    nearby={"A":[dict(locality="Cape Bird North",x=x,y=y,uncertainty_m=50)],
            "B":[dict(locality="Beaufort Island North",x=x,y=y,uncertainty_m=50)]}
    rows,qa=v.choose_original_APBP_georef(source(),nearby)
    assert rows[0]["status"]=="HOLD_NO_EXACT_SINGLE_APBP_LOCALITY"   # Beaufort
    assert rows[1]["status"]=="APBP_REPORTED_POSITION_PRECISION_CANDIDATE_ONLY_NOT_GPS_PROOF"
    nearby["C"]=nearby["A"]
    rows,qa=v.choose_original_APBP_georef(source(),nearby)
    assert rows[1]["status"]=="HOLD_AMBIGUOUS_APBP_LOCATION_IDS"

def test_one_minute_copied_georeference_does_not_become_new_independent_gps():
    tr=v.Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    x,y=tr.transform(166.4,-77.2)
    src={"A":[dict(locality="Cape Bird North",x=x,y=y,uncertainty_m=10)]}
    rows,_=v.choose_original_APBP_georef(source(),src)
    assert rows[1]["status"]=="HOLD_APBP_COORDINATE_EQUALS_COARSE_NZ_LOCATION"

def test_uncertainty_missing_cannot_be_reinterpreted_as_precision():
    tr=v.Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    x,y=tr.transform(166.402,-77.201)
    src={"A":[dict(locality="Cape Bird North",x=x,y=y,uncertainty_m=None)]}
    rows,_=v.choose_original_APBP_georef(source(),src)
    assert rows[1]["status"]=="HOLD_APBP_UNKNOWN_ORIGINAL_POSITION_UNCERTAINTY"

def test_original_gate_source_constants_unchanged():
    assert v.SOURCE_APBP_SHA=="afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf"
    assert v.MIN_ISLANDS==3 and v.MIN_COOBSERVATION_YEARS==8
    assert len(v.FROZEN_SHARED_YEARS)==13
