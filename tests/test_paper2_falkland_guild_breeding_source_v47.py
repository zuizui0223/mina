"""Paper2 V47 test exact historical FIG native bird/invader/visit matching with invented records."""
from __future__ import annotations
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_paper2_falkland_guild_breeding_source_v47 as x


def headers():
    locations=["Location Name","Wider Area","DOS", "Category","Latitude","Longitude",
               "Lat/long origin","Area (ha)"]+["Other"]*9
    birds=["Other"]*26
    for i,k in {0:"Location Name",7:"English name",9:"Day",10:"Month",
                11:"Year",13:"Presence",16:"Breeding status",
                21:"Time surveying"}.items():
        birds[i]=k
    visits=["ID","Location Name","Latitude","Longitude","English name",
            "Category","Day","Month","Year","Surveyors","Organisations",
            "Notes on visit","Reference"]
    return tuple(locations),tuple(birds),tuple(visits)


def source_fixture():
    lh,bh,vh=headers()
    places=[lh]
    bird=[bh]
    visit=[vh]
    mammals=[]
    for i in range(4):
        place=f"Fictional Island {i}"
        places.append(tuple([place,"West Falkland","map","island",-51.5,-60.0, "GPS",20.]+[""]*9))
        # 4 source islands, each with a penguin and flying seabird pair in 2009
        for species,status in [("Gentoo penguin","Breeding"),
                               ("Dolphin Gull","Confirmed breeding")]:
            vals=[""]*26
            for col,val in [(0,place),(7,species),(9,12),(10,3),(11,2009),
                            (13,"present"),(16,status),(21,"2h")]:
                vals[col]=val
            bird.append(tuple(vals))
        visit.append((None,place,-51.5,-60.0,None,None,12,3,2009,None,None,
                      "island field survey",None))
        inv=[""]*18
        inv[0]=place;inv[7]="Norway rat";inv[8]="possible"
        mammals.append(tuple(inv))
    return places,bird,visit,mammals


def test_guilds_frozen_and_ambiguous_status_is_not_confirmed():
    assert x.bird_guild("Magellanic penguin")=="PENGUIN_FLIGHTLESS"
    assert x.bird_guild("King Penguin")=="PENGUIN_FLIGHTLESS"
    assert x.bird_guild("Black-browed Albatross")=="SEABIRD_FLYING"
    assert x.bird_guild("Thin-billed prion")=="SEABIRD_FLYING"
    assert x.bird_guild("Cobb's Wren")=="OTHER_OR_AMBIGUOUS"
    assert x.original_breeding_status("Breeding")=="DEFINITE_RECORDED_BREEDING"
    assert x.original_breeding_status("Confirmed breeding")=="DEFINITE_RECORDED_BREEDING"
    for bad in ("possible breeding","probable breeding","breeding?",
                "not breeding","not known","", "present","B"):
        assert x.original_breeding_status(bad)!="DEFINITE_RECORDED_BREEDING"


def test_source_location_visit_and_bird_both_guild_matching_no_absence_assumption():
    places,birds,visits,invs=source_fixture()
    refs,qa=x.locations_source(places)
    v_year,v_day,vqa=x.visits_source(visits,refs)
    counts,matched,days=x.birds_source(birds,refs,v_year,v_day)
    assert counts["classed_flightless_penguin_source_records"]==4
    assert counts["classed_flying_seabird_source_records"]==4
    assert counts["bird_source_same_island_year_BOTH_guilds_DEFINITE_and_visit_same_year"]==4
    assert counts["bird_source_same_island_day_BOTH_guilds_DEFINITE_AND_same_day_original_visit"]==4
    assert counts["G1_predeclared_both_definite_guild_sample_gate_pass"] is False
    assert len(matched)==4
    assert counts["blank_species_no_observed_record_NOT_absent"] is True
    assert all(k[0].startswith("fictional island") for k in matched)


def test_source_rat_records_do_not_infer_independently_surveyed_absence():
    places,birds,visits,invs=source_fixture()
    refs,qa=x.locations_source(places)
    rat=x.invasives_source(invs,refs,{("fictional island 0",2009)})
    assert rat["original_predator_record_rows_per_taxon_not_occupied_islands"]["NORWAY_RAT_LITERAL_SOURCE_RECORD"]==4
    assert rat["same_year_guild_definite_eligible_islands_with_any_Norway_rat_RECORD"]==1
    assert rat["G2_original_matched_mammal_surveyed_positive_and_negative_gate_pass"] is False
    assert rat["source_invasion_rows_are_NOT_surveyed_true_predator_absence"] is True


def test_records_with_different_year_do_not_pair():
    loc,bird,visits,inv=source_fixture()
    records=list(bird)
    vals=list(records[2]);vals[11]=2010;records[2]=tuple(vals)
    refs,_=x.locations_source(loc)
    vy,vd,_=x.visits_source(visits,refs)
    qa,yr,day=x.birds_source(records,refs,vy,vd)
    assert qa["bird_source_same_island_year_BOTH_guilds_DEFINITE"]==3
    assert qa["bird_source_same_island_day_BOTH_guilds_DEFINITE"]==3


def test_free_text_not_emitted_and_no_assumed_zero():
    assert x.safe_status_hist(["Breeding","unknown","maybe", "Name of respondent John Doe"])["uninterpreted_source_code_or_text_rows"]==2
    assert x.norm("  HELLO   Isle ")=="hello isle"
    assert x.source_date((12,3,2009),0,1,2)==(2009,"2009-03-12")
    assert x.source_date((12,3,2020),0,1,2)==(None,None)
    with pytest.raises(ValueError,match="SOURCE_UNAPPROVED_HOST"):
        x.read_url(None,"https://private.example.net/file.xls",1024)
