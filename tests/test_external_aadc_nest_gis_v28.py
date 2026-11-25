"""Original AADC publisher-only external field-nest GIS registry exact source QA."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from inventory_external_aadc_nest_gis_v28 import exact_registry,SOURCE_IDS


def test_exact_original_source_metadataIDs_not_prefix_or_stripped_similarity():
    original=[
       {"metadata_entry_id":"windmill_flyingbirds_gis160","uuid":"111"},
       {"metadata_entry_id":"Windmill_FlyingBirds_GIS160_v2","uuid":"222"},
       {"metadata_entry_id":"AAS_4518_Cape_Petrel_population_estimates_VestfoldIslands",
        "uuid":"333"},
       {"metadata_entry_id":"bech_nest_locations","uuid":"444"},
       {"metadata_entry_id":"not_a_bird_dataset"},
    ]
    matches=exact_registry(original)
    assert len(matches[SOURCE_IDS[0]])==1
    assert len(matches[SOURCE_IDS[1]])==1
    assert len(matches[SOURCE_IDS[2]])==1
    assert len(matches[SOURCE_IDS[3]])==0
    assert matches[SOURCE_IDS[0]][0]["uuid"]=="111"


def test_invalid_official_registry_is_not_a_plant_nest_count():
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        exact_registry({"source_id":"wild_guess"})

