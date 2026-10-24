"""No original animal values in V40 unit tests."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_mapppd_v5_macro_source_lineage_v40 as m

def site():
    return {"site_id":"TEST","site_name":"Invented Island","region":"Test region",
            "latitude":"-70","longitude":"160","mapppd_version":"5.0"}
def row(n,year,citation="study",vantage="ground",stage="nests",count="42"):
    return {"id":str(n),"site_id":"TEST","site_name":"Invented Island",
            "species_id":"ADPE","season":str(year),"year":str(year),
            "count":count,"type":stage,"presence":"1","vantage":vantage,
            "citekey":citation,"mapppd_version":"5.0"}

def test_same_original_source_and_vantage_only():
    d=[row(1,1996),row(2,1997),row(3,1998),row(4,1999,citation="other")]
    sample,meta,good=m.support(d,{"TEST":site()},require_n=False)
    assert sample["source_original_strict_same_site_species_year_method_nest_transitions"]==2
    assert sample["adjacent_source_stage_candidates_excluded"]["different_or_unknown_original_source"]==1
    assert meta["no_absolute_bird_count_magnitude_exported"]
def test_same_year_duplicate_is_wholly_excluded():
    d=[row(1,1996),row(2,1997),row(3,1997),row(4,1998)]
    sample,meta,good=m.support(d,{"TEST":site()},require_n=False)
    assert sample["duplicate_site_species_season_groups_excluded"]==1
    assert sample["source_original_strict_same_site_species_year_method_nest_transitions"]==0
def test_upstream_NZ_citation_is_not_new_animal_sample():
    good={("TEST","ADPE",1996):row(1,1996,citation=m.NZ_CITE)}
    p=m.overlap(good,{"TEST":site()},{"invented island":{1996}})
    assert p["exact_site_name_species_ADPE_season_nests_citation_numeric_presence_overlaps"]==1
    assert p["upstream_field_census_not_an_independent_replication"]
def test_missing_not_zero_and_literal_source_year():
    assert m.numeric_present("0") and m.numeric_present("42")
    assert not m.numeric_present("") and not m.numeric_present("NA")
    assert not m.numeric_present("-99")
    assert m.valid_year("2001")==2001 and m.valid_year("unknown") is None
    assert m.MIN_PAIRS==50 and m.MIN_SITES==20 and m.MIN_REGIONS==4
