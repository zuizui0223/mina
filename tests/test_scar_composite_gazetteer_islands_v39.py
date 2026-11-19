"""Invented official feature HTML and immutable source-years only."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_scar_composite_gazetteer_islands_v39 as m

def source(name="Ross Island",kind="Island",id=130958):
    return (f"<html><h2>{name}</h2><p>United States Gazetteer Id {id}</p>"
            f"<p>Feature type: {kind} (5)</p>"
            f"<p>This is part of the SCAR Composite Gazetteer of Antarctica.</p></html>").encode()

def test_only_exact_official_island_type_and_name_and_gaz_id():
    x=m.validate_island_feature(source(),"Ross Island",130958)
    assert x["original_exact_feature_type"]=="Island (5)"
    assert not x["original_nest_colony_GPS_or_animal_count_evidence"]
    for data,named,id in [(source(kind="Cape"),"Ross Island",130958),
                          (source(name="James Ross Island"),"Ross Island",130958),
                          (source(),"Ross Island",99999)]:
        try:m.validate_island_feature(data,named,id);assert False
        except ValueError:pass

def test_original_island_aggregate_NOT_independent_colonies_or_new_effect():
    assert len(m.SOURCES)==4
    assert m.SOURCES["Ross Island"]!=m.SOURCES["Coulman Island"]
    assert len(m.ORIGINAL_YEAR_ROSTER)==13
    assert m.ORIGINAL_YEAR_ROSTER[0]==1983
    assert "count" not in m.ORIGIN
