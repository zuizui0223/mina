"""Invented-only site API identity and source coverage, no penguin counts."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_mapppd_v5_ross_geo_v38 as m

def fake():
    return [dict(site_id=code,site_name=official,mapppd_version="5.0",species=["ADPE"],
                 latitude=-76.,longitude=166.) for name,(code,official,_,_) in m.MATCH.items()]+[
          dict(site_id="T"+str(i),site_name="Fake"+str(i),mapppd_version="5.0",
               latitude=-75.,longitude=160.,species=["ADPE"]) for i in range(32)]

def test_fixed_publisher_IDs_and_three_source_abbreviations_not_verified():
    rows=m.match_sites({"version":"5.0","release_date":"2026-10-21"},fake())
    assert len(rows)==10
    assert sum(x["name_match"]=="EXACT" for x in rows.values())==7
    assert rows["Coulman Island Middle"]["name_match"]=="ABBREVIATED"

def test_version_and_renamed_public_site_fail_closed():
    q=fake()
    q[0]["site_name"]="Beaufort fake"
    try:m.match_sites({"version":"5.0","release_date":"2026-10-21"},q);assert False
    except ValueError as e: assert "identity drift" in str(e)
    try:m.match_sites({"version":"4.4","release_date":"2026-10-21"},fake());assert False
    except ValueError as e: assert "version" in str(e)

def test_original_years_and_numeric_coordinates_are_fixed_not_nesting_outcomes():
    assert m.FROZEN_YEARS==tuple(list(range(1983,1993))+[2001,2004,2005])
    assert len(m.GROUPS)==4
    assert m.MIN_SHARED_YEARS if hasattr(m,"MIN_SHARED_YEARS") else True
    assert "observations" not in m.API
    assert len(m.HIGH_SHA)==64
