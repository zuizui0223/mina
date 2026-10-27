"""Synthetic V41 UK RSPB named island-group spatial transfer gates."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_jncc_uk_predator_sdm_archipelago_v41 as v
import map_jncc_uk_island_predator_sdm_v40 as b


def records(n=506):
    island={};taxon={}
    for i in range(1,n+1):
        island[i]={
            "low_tide_area_h":11+(i%100),
            "high_tide_area_h":10+(i%100),
            "latitude":49+(i%20)*.31,
            "longitude":-12+(i%28)*.4,
            "human_population":i%5,
            "ferry":"Ferry" if i%13==0 else " ",
            "group":f"Source_Archipelago_{(i-1)//55}",
            "country":"Scotland",
            "coast":"west",
        }
        taxon[i]={tax:"1" if i%3==0 else "0" for tax in b.TAXA}
    return island,taxon


def test_groups_use_original_archipelago_labels_only():
    assert v.original_group({"group":"Orkney_Islands","country":"Scotland","coast":"north"})=="RSPB_GROUP:orkney islands"
    assert v.original_group({"group":"","country":"Scotland","coast":"west"})=="RSPB_REGION_FALLBACK:scotland:west"


def test_true_original_source_group_holdout_all_species_scores():
    island,status=records()
    cohort=b.construct_domain(island,status)
    result=v.group_cv(cohort,"American mink",island)
    assert result["training_source_islands"]==506
    assert result["original_archipelago_fold_support_pass"]
    assert len(result["test_source_counts"])==5
    assert sum(f["original_heldout_islands"] for f in result["test_source_counts"])==506
    assert result["transportability_gate"] in (True,False)
    assert result["source0_is_assumed_or_known_absence_NOT_verified_surveillance_zero"]


def test_undiversified_original_source_groups_STOP_without_favorable_aliases():
    island,status=records()
    for i in island:island[i]["group"]="Same_Admin_Area"
    cohort=b.construct_domain(island,status)
    result=v.group_cv(cohort,"Brown rat",island)
    assert result["status"]=="SOURCE_GROUP_SUPPORT_STOP"


def test_original_status_code_three_excluded_in_group_cv():
    island,status=records()
    for i in (13,53,73):status[i]["Feral cat"]="3"
    cohort=b.construct_domain(island,status)
    result=v.group_cv(cohort,"Feral cat",island)
    assert result["training_source_islands"]==503
    assert result["source_label_positives"]<503
    if result.get("test_source_counts"):
        assert sum(z["original_heldout_islands"] for z in result["test_source_counts"])==503
