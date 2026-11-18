"""Fixed forward count periods, source identity and no shared baseline denominator."""
from pathlib import Path
import importlib.util
import math
import pytest

FILE=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/stage_followthrough_v11.py'
def mod():
    sp=importlib.util.spec_from_file_location('forward_v11',FILE)
    obj=importlib.util.module_from_spec(sp);sp.loader.exec_module(obj);return obj

def baseline(t=2000):
    return dict(site_id='TEST',site_name='Test',region='A',pair='CHPE|GEPE',
      season_start=t,citekey='annual',vantage='ground',species_a='CHPE',species_b='GEPE',
      nest_count_a=100,nest_count_b=100,chick_count_a=50,chick_count_b=100,
      nest_source_id_a='base-na',nest_source_id_b='base-nb',
      chick_source_id_a='base-ca',chick_source_id_b='base-cb',
      chick_date_lower_a=f'{t+1}-01-10',chick_date_upper_a=f'{t+1}-01-10',
      chick_date_lower_b=f'{t+1}-01-10',chick_date_upper_b=f'{t+1}-01-10',
      both_stages_ordered=True,same_full_dates_across_species=True,
      exact_source_land_fid=10,current_mapped_nonmainland_land=True,
      ambiguous_site_season_pair=False)

def raw(s,sp,n,cite='annual',ident=None):
    return dict(site_id='TEST',species_id=sp,season=str(s),year=str(s),month='',day='',
      count=str(n),citekey=cite,vantage='ground',type='nests',
      id=ident or f'{cite}-{sp}-{s}',presence='1')

def future(cite='annual'):
    return [raw(2002,'CHPE',100,cite),raw(2002,'GEPE',100,cite),
            raw(2005,'CHPE',100,cite),raw(2005,'GEPE',200,cite)]

def get(rows,b=None):
    m=mod();return m.followup(b or baseline(),m.source_index(rows))

def test_same_source_fixed_horizon_and_no_shared_record_ids():
    x=get(future())
    assert x['status']=='accepted' and x['source_link']=='same_citation'
    assert x['future_start']==2002 and x['future_end']==2005
    assert x['no_shared_count_ids'] and x['all_future_counts_after_chicks']
    assert math.isclose(x['future_share_change_per_year'],(2/3-1/2)/3)

def test_baseline_counts_are_not_future_denominator():
    a,b=baseline(),baseline();b['nest_count_b']=500
    x,y=get(future(),a),get(future(),b)
    assert x['future_share_change_per_year']==y['future_share_change_per_year']
    assert x['baseline_share_shift']!=y['baseline_share_shift']

def test_no_missing_year_substitution():
    rows=future();rows[0]['season']='2003'
    assert get(rows)['status']=='no_qualified_future_source'

def test_mixed_future_citation_not_joined():
    rows=future();rows[0]['citekey']='different'
    assert get(rows)['status']=='no_qualified_future_source'

def test_matching_baseline_counts_permit_labelled_bridge():
    rows=future('compiled')+[raw(2000,'CHPE',100,'compiled'),raw(2000,'GEPE',100,'compiled')]
    x=get(rows)
    assert x['status']=='accepted' and x['source_link']=='baseline_count_agreement_bridge'
    assert x['future_citekey']=='compiled'
    assert not x['identical_field_protocol_verified']

def test_disagreeing_source_bridge_is_not_rescued():
    rows=future('compiled')+[raw(2000,'CHPE',99,'compiled'),raw(2000,'GEPE',100,'compiled')]
    x=get(rows)
    assert x['status']=='no_qualified_future_source'
    assert any(a['reason']=='baseline_count_disagreement' for a in x['source_candidate_audit'])

def test_multiple_bridge_sources_are_ambiguous_not_selected_by_values():
    rows=[]
    for c in ['first','second']:
        rows+=future(c)+[raw(2000,'CHPE',100,c),raw(2000,'GEPE',100,c)]
    assert get(rows)['status']=='ambiguous_future_source'

def test_same_citation_preferred_before_bridge():
    rows=future()+future('compiled')+[raw(2000,'CHPE',100,'compiled'),raw(2000,'GEPE',100,'compiled')]
    assert get(rows)['future_citekey']=='annual'

def test_duplicate_even_missing_invalidates_unique_future():
    rows=future()+[raw(2002,'CHPE','','annual',ident='duplicate')]
    assert get(rows)['status']=='no_qualified_future_source'

def test_duplicate_raw_ids_raise():
    m=mod();rows=future()+[dict(future()[0])]
    with pytest.raises(ValueError,match='duplicate observation'):m.source_index(rows)

def test_future_before_recorded_chicks_rejected():
    b=baseline();b['chick_date_upper_b']='2003-01-01'
    assert get(future(),b)['status']=='chronology_unresolved_or_reversed'

def test_unknown_future_year_rejected_not_imputed():
    rows=future();rows[0]['year']=''
    assert get(rows)['status']=='chronology_unresolved_or_reversed'

def test_shared_original_id_rejected():
    rows=future();rows[0]['id']='base-na'
    assert get(rows)['status']=='shared_baseline_future_count_ids'

def test_one_species_zero_retained_no_pseudocount():
    rows=future();rows[-1]['count']='0'
    x=get(rows)
    assert x['status']=='accepted' and x['future_end_count_b']==0
    assert x['future_share_late']==0
    assert x['future_log_ratio_change_per_year'] is None

def test_both_future_zero_composition_undefined_not_zero_effect():
    rows=future();rows[-1]['count']='0';rows[-2]['count']='0'
    x=get(rows)
    assert x['status']=='accepted'
    assert x['future_share_change_per_year'] is None
    assert x['undefined_future_composition']

def test_disjoint_windows_deterministic_and_endpoint_not_reused():
    m=mod();rows=[dict(site_id='X',pair='CHPE|GEPE',season_start=t,
         future_start=t+2,future_end=t+5) for t in range(2000,2010)]
    selected=m.disjoint_windows(list(reversed(rows)))
    assert [r['season_start'] for r in selected]==[2000,2004,2008]

def test_summary_site_weights_not_number_of_repeated_years():
    m=mod();a=get(future());b=dict(a,site_id='OTHER',region='B',
          baseline_share_shift=-.2,future_share_change_per_year=-.1)
    s=m.summarize([a,a,b])
    assert s['n_links']==3 and s['n_sites']==2
    assert math.isclose(s['equal_site_mean_future_share_change_per_year'],(a['future_share_change_per_year']-.1)/2)
    assert not s['multi_region_generality_supported']
    assert s['p_value'] is None and not s['recruitment_identified']

def test_missing_negative_and_nonfinite_count_not_valid():
    for n in ['', '-1', 'nan','inf']:
        rows=future();rows[0]['count']=n
        assert get(rows)['status']=='no_qualified_future_source'

def test_unvarying_stage_direction_not_misrepresented_as_predictive_skill():
    m=mod();a=get(future());b=dict(a,season_start=2001,future_start=2003,future_end=2006,
        future_share_change_per_year=-.05,directional_concordance=False)
    s=m.summarize([a,b])
    assert s['positive_stage_direction_n']==2 and s['positive_future_direction_n']==1
    assert s['stage_direction_uniform_nonzero']
    assert s['constant_positive_direction_concordant_n']==s['concordant']==1

def test_commas_in_valid_original_counts_are_normalized():
    rows=future();rows[0]['count']='1,000'
    x=get(rows)
    assert x['future_start_count_a']==1000
