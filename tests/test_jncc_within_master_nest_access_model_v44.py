"""Synthetic tests for fixed V44 within-network matched guild effect gates."""
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "scripts"))
import model_jncc_within_master_nest_access_v44 as m


def panel(sp, master, old=(70,20,10),new=(25,9,3)):
    key=(sp,"Scotland",master,"AON")
    records=[]
    for j,(x,y) in enumerate(zip(old,new)):
        records.append((
            {"year_2000":2000,"year_recent":2018,"site_id":str(j+1)},
            {"L":str(x),"O":str(y)},
        ))
    return key,records


def cohort(num=12):
    rows={};paired={}
    for n in range(num):
        master=f"example{n}"
        a,ra=panel("Herring Gull" if n%2 else "Great Black-backed Gull",
                   master,new=(2,6,2))
        b,rb=panel("Black-legged Kittiwake",
                   master,new=(20,10,5))
        rows[a]=ra
        rows[b]=rb
        paired[("Scotland",master)]=[(a,b)]
    return rows,paired


def test_original_source_exact_integer_count_and_decline_gate():
    key,rows=panel("Herring Gull","A")
    x,reason=m.count_panel(key,rows)
    assert reason=="OK"
    assert x["N0"]==100
    assert x["N1"]==37
    assert x["declined"] is True
    assert x["k"]==3


def test_source_noninteger_record_is_whole_panel_stop():
    key,rows=panel("Herring Gull","A")
    rows[1][1]["L"]="2.5"
    x,reason=m.count_panel(key,rows)
    assert x is None
    assert reason=="NON_EXACT_OR_MISSING_SOURCE_COUNT"


def test_numeric_support_stops_below_ten_without_result_selection():
    rows,paired=cohort(num=4)
    decline,allc,cache,qa=m.build_complete_compared_cohort(rows,paired)
    assert qa["BOTH_GUILD_SOURCE_SPECIES_DECLINING_networks"]==4
    assert qa["fixed_preregistered_both_declining_count_gate_pass"] is False


def test_numeric_support_reports_truly_both_decline_and_not_mixed_total_growth():
    rows,paired=cohort(num=12)
    k=next(k for k in rows if k[0]=="Black-legged Kittiwake")
    rows[k]=panel(k[0],k[2],new=(75,25,25))[1]
    decline,allc,cache,qa=m.build_complete_compared_cohort(rows,paired)
    assert len(allc)==12
    assert len(decline)==11
    assert qa["fixed_preregistered_both_declining_count_gate_pass"]
    assert qa["count_based_exclusion_reasons"]["ONE_OR_BOTH_SOURCE_SPECIES_NOT_DECLINING"]==1


def test_fixed_null_is_zero_mean_in_synthetic_panel():
    key,rows=panel("Herring Gull","A")
    obj,reason=m.count_panel(key,rows)
    original,c0=m.E_from_counts(obj)
    n=m.null_E(obj,np.random.default_rng(20261027))
    assert len(n)==1999
    assert abs(float(np.mean(n)))<.012


def test_paired_E_uses_network_once_even_with_multiple_children():
    rows,paired=cohort(num=12)
    decline,allc,cache,qa=m.build_complete_compared_cohort(rows,paired)
    assert qa["fixed_preregistered_both_declining_count_gate_pass"]
    outcome=m.statistic_for_paired(decline,cache,np.random.default_rng(20261027))
    assert outcome["n_source_Country_Master_paired_networks"]==12
    assert outcome["cliff_species"]==["Black-legged Kittiwake"]
    assert len(outcome["accessible_species"])==2
    assert 0<=outcome["independent_Master_network_signflip_right_tail"]<=1
    assert outcome["finite_count_multinomial_null_1999_replicates"]==1999
    assert outcome["guild_proxy_sole_cliff_species_cannot_support_generality_beyond_kittiwake"]
