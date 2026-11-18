"""Source-matching and mathematical tests; no real response is selected here."""
import importlib.util, math, sys
from pathlib import Path
import pytest
PATH=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/stage_composition_v10.py'
def load():
    sys.path.insert(0,str(PATH.parent))
    spec=importlib.util.spec_from_file_location('stage_comp_v10_test',PATH)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def pair(sp='CHPE',n=100,c=150,site='A',year=2000,cite='study'):
    return dict(site_id=site,species_id=sp,season_start=year,season_end=year+1,
      citekey=cite,vantage='ground',nest_count=n,chick_count=c,
      nest_source_id=f'{site}_{year}_{cite}_{sp}_n',chick_source_id=f'{site}_{year}_{cite}_{sp}_c',
      chronology='nest_interval_precedes_chick_interval',
      nest_date_precision='full_date',chick_date_precision='full_date',
      nest_date_lower=f'{year}-12-01',nest_date_upper=f'{year}-12-01',
      chick_date_lower=f'{year+1}-02-01',chick_date_upper=f'{year+1}-02-01')

def test_nest_dominance_need_not_equal_output_dominance():
    m=load();x=m.stage_metrics(pair(n=100,c=150),pair('GEPE',200,200))
    assert x['nest_dominant_species']=='GEPE' and x['chick_dominant_species']=='GEPE'
    assert x['output_dominant_species']=='CHPE'
    assert x['nest_leader_lower_output'] is True
    assert x['nest_chick_rank_reversal'] is False
    assert math.isclose(x['share_shift_b'],200/350-200/300)

def test_rank_reversal_is_not_just_output_rank_difference():
    x=load().stage_metrics(pair(n=100,c=160),pair('GEPE',200,90))
    assert x['nest_chick_rank_reversal'] is True
    assert x['chick_dominant_species']=='CHPE'
    assert abs(x['log_identity_error'])<1e-12

def test_swapping_taxa_changes_direction_not_rank_mismatch():
    m=load();a,b=pair(),pair('GEPE',200,90)
    x,y=m.stage_metrics(a,b),m.stage_metrics(b,a)
    assert math.isclose(x['share_shift_b'],-y['share_shift_b'])
    assert math.isclose(x['output_difference_b_minus_a'],-y['output_difference_b_minus_a'])
    assert x['nest_chick_rank_reversal']==y['nest_chick_rank_reversal']

def test_observed_zero_chicks_not_pseudocount():
    x=load().stage_metrics(pair(c=0),pair('GEPE',200,30))
    assert x['chick_share_b']==1 and x['log_output_ratio_b_over_a'] is None
    assert x['chick_count_a']==0

def test_both_zero_chicks_give_missing_share_not_zero():
    x=load().stage_metrics(pair(c=0),pair('GEPE',200,0))
    assert x['chick_share_b'] is None and x['share_shift_b'] is None
    assert x['nest_chick_rank_reversal'] is False

def test_ties_are_not_reversals():
    x=load().stage_metrics(pair(n=100,c=200),pair('GEPE',100,200))
    assert x['nest_dominant_species']=='tie'
    assert x['nest_chick_rank_reversal'] is False and x['nest_leader_lower_output'] is False

def test_ratio_over_two_retained_flagged():
    x=load().stage_metrics(pair(n=100,c=220),pair('GEPE',100,130))
    assert x['ratio_above_two_any'] is True
    assert x['recorded_output_a']==2.2

@pytest.mark.parametrize('bad',[None,-1,float('nan'),float('inf')])
def test_bad_count_is_not_zero(bad):
    with pytest.raises((ValueError,TypeError)):
        load().stage_metrics(pair(c=bad),pair('GEPE'))

def test_zero_nest_rejected_not_divided():
    with pytest.raises(ValueError):load().stage_metrics(pair(n=0),pair('GEPE'))

def build(rows):
    return load().build_contrasts(rows,{'A':dict(region='R',site_name='Alpha')},{})[0]

def test_source_mismatch_never_paired():
    assert build([pair(),pair('GEPE',cite='other')])==[]
    b=pair('GEPE');b['vantage']='aerial';assert build([pair(),b])==[]

def test_duplicate_species_source_pair_rejected():
    with pytest.raises(ValueError):build([pair(),pair(),pair('GEPE')])

def test_alternative_sources_preserved_but_not_primary_replicates():
    rows=build([pair(),pair('GEPE'),pair(cite='alt'),pair('GEPE',cite='alt')])
    assert len(rows)==2 and all(r['ambiguous_site_season_pair'] for r in rows)

def test_year_only_not_equal_fully_dated_surveys():
    a,b=pair(),pair('GEPE')
    for r in (a,b):
        r['nest_date_precision']=r['chick_date_precision']='year_only'
        r['chronology']='unresolved'
    row=build([a,b])[0]
    assert not row['both_stages_ordered'] and not row['same_full_dates_across_species']

def test_same_full_dates_and_source_ids_retained():
    a,b=pair(),pair('GEPE');x=build([a,b])[0]
    assert x['both_stages_ordered'] and x['same_full_dates_across_species']
    assert x['nest_source_id_a']==a['nest_source_id']
    assert x['chick_source_id_b']==b['chick_source_id']

def test_same_dates_cohort_requires_ordered_stages():
    a,b=pair(),pair('GEPE');a['chronology']='reported_chicks_before_nests'
    assert not build([a,b])[0]['same_full_dates_across_species']

def test_equal_site_weighting_separates_repeated_years():
    m=load();a=m.stage_metrics(pair(),pair('GEPE',100,50));b=m.stage_metrics(pair(),pair('GEPE',100,300))
    data=[dict(a,site_id='A',region='R',season_start=2000,citekey='s'),
          dict(a,site_id='A',region='R',season_start=2001,citekey='s'),
          dict(b,site_id='B',region='R',season_start=2000,citekey='s')]
    s=m.summary(data)
    assert math.isclose(s['equal_site_mean_share_shift_b'],(a['share_shift_b']+b['share_shift_b'])/2)
    assert not math.isclose(s['row_mean_share_shift_b'],s['equal_site_mean_share_shift_b'])
    assert s['p_value'] is None

def test_inputs_are_not_mutated():
    import copy
    a,b=pair(),pair('GEPE');old=copy.deepcopy([a,b]);build([a,b]);assert [a,b]==old
