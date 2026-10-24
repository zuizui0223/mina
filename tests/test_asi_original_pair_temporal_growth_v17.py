"""Synthetic original ASI cross-guild pair transitions and causal stop guards."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import fit_asi_original_pair_temporal_growth_v17 as v
import pytest

def r(site="ABCD",sp="ADPE",year=2007,day=12,count="SECRET",region="SH"):
    return dict(Site_ID=site,Region=region,Site_name="mock",
       Latitude="-65",Longitude="-60",Species=sp,Date=f"12/{day}/{year}",
       Season=str(year),Counted_object="N",Accuracy="2",
       Count=count,Notes="",Source="ASI")

def test_two_year_same_date_same_species_pair_structural_not_counts():
    data=[r(sp="ADPE"),r(sp="BESH"),r(sp="ADPE",year=2008,day=14),
          r(sp="BESH",year=2008,day=14)]
    transition,meta=v.original_temporal_pairs(data)
    assert meta["eligible_consecutive_same_site_species_pairs"]==1
    assert transition[0]["site"]=="ABCD"
    assert v.gate(meta) is False
    assert v.measure(transition)["status"]=="HOLD_NUMERIC_NEST_SUPPORT"  # invalid SECRET

def test_no_pair_if_dates_mismatch_and_nest_stage_missing():
    data=[r(sp="ADPE"),r(sp="BESH",day=15),
          r(sp="ADPE",year=2008),r(sp="BESH",year=2008,day=17)]
    trans,_=v.original_temporal_pairs(data)
    assert len(trans)==0

def test_phenological_shift_more_than_21d_stopped_before_biology():
    data=[r(sp="ADPE"),r(sp="BESH"),r(sp="ADPE",year=2008,day=31),
          r(sp="BESH",year=2008,day=31)]
    trans,meta=v.original_temporal_pairs(data)
    assert len(trans)==1  # 19 day difference, not excluded
    data=[r(sp="ADPE"),r(sp="BESH"),r(sp="ADPE",year=2008,day=2),
          r(sp="BESH",year=2008,day=2)]
    assert len(v.original_temporal_pairs(data)[0])==1
    data=[r(sp="ADPE"),r(sp="BESH"),r(sp="ADPE",year=2008,day=31),
          r(sp="BESH",year=2008,day=31)]
    # All examples above are within 21 days; different months are separately validated.
    assert v.phase_day("2008-12-31")-v.phase_day("2008-12-01")==30

def test_real_count_never_used_to_inflate_source_gate():
    data=[r(sp="ADPE",count="1"),r(sp="BESH",count="99999"),
          r(sp="ADPE",year=2008,count="1200000"),r(sp="BESH",year=2008,count="0")]
    trans,meta=v.original_temporal_pairs(data)
    assert meta["eligible_consecutive_same_site_species_pairs"]==1
    assert not v.gate(meta)
    assert v.count_nests("1,234")==1234

def test_all_duplicated_same_day_source_groups_dropped():
    data=[r(sp="ADPE"),r(sp="ADPE",count="10000"),r(sp="BESH"),
          r(sp="ADPE",year=2008),r(sp="BESH",year=2008)]
    trans,_=v.original_temporal_pairs(data)
    assert len(trans)==0

def test_site_weight_correlation_zero_variance_unidentifiable():
    rows=[dict(site="AA",penguin_growth=1,flying_growth=1),
          dict(site="BB",penguin_growth=1,flying_growth=0)]
    assert v.weighted_corr(rows) is None
