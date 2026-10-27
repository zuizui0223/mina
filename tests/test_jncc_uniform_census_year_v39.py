"""Synthetic original 2-epoch year metadata gate and no post-result timing cutoffs."""
from pathlib import Path
import sys
import pytest
import json

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_jncc_uniform_census_year_v39 as audit


def make_rec(y0,y1,source_early="15",source_recent="8"):
    return ({"year_2000":y0,"year_recent":y1},{"L":source_early,"O":source_recent})


def test_parent_both_years_exactly_same_not_within_one_year():
    same=[make_rec(2000,2017),make_rec(2000,2017),make_rec(2000,2017)]
    d=audit.year_metadata(same)
    assert d["both_years_uniform"] is True
    assert d["source_child_count"]==3
    not_same=[make_rec(2000,2017),make_rec(2001,2017),make_rec(2000,2017)]
    d=audit.year_metadata(not_same)
    assert d["uniform_earlier_year"] is False
    assert d["uniform_later_year"] is True
    assert d["both_years_uniform"] is False
    late_diff=[make_rec(2000,2017),make_rec(2000,2018),make_rec(2000,2017)]
    assert audit.year_metadata(late_diff)["both_years_uniform"] is False


def test_numeric_eligible_source_never_rounds_fractional_or_missing_counts():
    key=("Invented species","Scotland","Invented Master","AON")
    rows={
      key:[make_rec(2000,2017,"15","8"),
           make_rec(2000,2017,"10","8"),
           make_rec(2000,2017,"5","3")]
    }
    informative,support,declines=audit.numeric_support(rows)
    assert len(informative)==1
    assert support["integer_valid_original_uniform_year_panels"]==1
    assert support["original_uniform_year_panels_with_lower_recent_total"]==1
    assert support["V39_pre_effect_cohort_information_gate_pass"] is False

    rows[key][1]=make_rec(2000,2017,"10.5","8")
    informative,support,declines=audit.numeric_support(rows)
    assert len(informative)==0
    assert support["numeric_drop_reasons"]["unparseable_count"]==1


def test_all_equal_early_sizes_cannot_define_score_and_are_excluded():
    key=("Invented species","Scotland","Invented Master","AON")
    rows={
      key:[make_rec(2000,2017,"5","1"),
           make_rec(2000,2017,"5","2"),
           make_rec(2000,2017,"5","3")]
    }
    informative,support,declines=audit.numeric_support(rows)
    assert len(declines)==1
    assert len(informative)==0
    assert support["declining_panels_with_nonidentical_original_child_sizes"]==0


def test_same_year_gate_fixed_without_tolerance_tuning():
    assert audit.N_SIM==1999
    assert audit.SEED==20261027
    assert audit.MIN_DECLINING==100
    assert audit.MIN_SPECIES==8
    assert audit.MIN_SOURCE_UNITS==3
    assert audit.MIN_COUNTRY_MASTER==30


def test_actual_output_numeric_types_are_json_serializable_on_invented_panels():
    fabricated=[]
    for sp in range(8):
        for site in range(3):
            fabricated.append(((f"synthetic{sp}","Scotland",f"fake{sp}_{site}","AON"),
                               [13,8,3],[1,7,2]))
    output=audit.same_year_replay(fabricated,fabricated)
    assert output["species"]==8
    assert type(output["species_with_positive_mean_size_score"]) is int
    assert "null_q95" in json.loads(json.dumps(output))
