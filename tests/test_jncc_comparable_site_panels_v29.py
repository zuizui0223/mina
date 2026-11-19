"""Synthetic fixture of two-epoch source data, not author counts."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_jncc_comparable_site_panels_v29 as m

def row(sp="Northern Fulmar",a="2000",b="2018",u="AOS",v="AOS",cnt0="0",cnt1="10",ident="123"):
    return {"A":sp,"B":"Scotland","D":"Skomer Island","F":ident,
            "I":"51.75","J":"-5.30","K":a,"L":cnt0,"M":u,"N":b,"O":cnt1,"P":v}
def test_valid_two_epoch_and_NA_not_zero():
    x,why=m.eligible_metadata(m.MAIN,5,row())
    assert why is None and x["unit"]=="AOS"
    assert "L" not in x and "O" not in x
    assert m.eligible_metadata(m.MAIN,6,row(cnt0="NA"))[1].startswith("NA_missing")
    assert m.numeric_presence("0")
    assert not m.numeric_presence("NA")
def test_unit_and_study_year_are_strict():
    assert m.eligible_metadata(m.MAIN,5,row(u="AON",v="IND"))[1].startswith("unit_incompatible")
    assert m.eligible_metadata(m.MAIN,5,row(a="1994"))[1].startswith("missing_or_out")
    assert m.eligible_metadata(m.MAIN,5,row(b="2012"))[1].startswith("missing_or_out")
def test_puffin_uses_only_comparable_sheet():
    assert m.eligible_metadata(m.MAIN,6,row(sp="Atlantic Puffin"))[0] is None
    item,e=m.eligible_metadata(m.PUFFIN,6,row(sp="Comparable - Atlantic Puffin",u="AOB",v="AOB"))
    assert e is None and item["species"]=="Atlantic Puffin"
def test_duplicate_ID_not_two_site_components():
    header={**m.REQUIRED}
    rows=[(m.MAIN,4,header)]
    for i in range(3):
        rows.append((m.MAIN,i+5,row(ident=str(100+i))))
    rows.append((m.MAIN,8,row(ident="100")))
    # count should remain two unique sites, not 3, after duplicated site ID excluded
    qa=m.coverage(rows)
    assert qa["entire_duplicate_species_master_site_ID_keys_excluded"]==1
    assert qa["qualified_species_country_master_unit_panels_with_ge3_sites"]==0
    assert qa["source_original_animal_magnitudes_accessed"]==0
