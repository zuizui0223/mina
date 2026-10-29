"""Synthetic tests for source-matched annual species contrasts, no source downloads."""
import importlib.util
import math
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'research/climate-penguin/work/climate_penguin/mapppd_matched_species_growth_v1.py'

def module():
    assert SCRIPT.exists(), 'Matched species analysis is not implemented'
    spec = importlib.util.spec_from_file_location('matched_growth', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def record(ident, species, season, count, source='field_a', method='ground', site='A'):
    return dict(id=str(ident), site_id=site, species_id=species, season=str(season),
                count=str(count), type='nests', presence='1', citekey=source,
                vantage=method, mapppd_version='5.0', year=str(season), month='11')

def fixture():
    return [record(1,'ADPE',2000,100), record(2,'ADPE',2001,80),
            record(3,'GEPE',2000,50), record(4,'GEPE',2001,60)]

def test_exact_source_pair_and_log_ratio_difference():
    m=module(); annual, audit=m.annual_pairs(fixture(), {'A': {'region':'R1'}})
    pairs, rejected=m.match_species(annual, 'ADPE', 'GEPE')
    assert len(annual)==2 and len(pairs)==1
    assert math.isclose(pairs[0]['delta_log_ratio_b_over_a'], math.log(1.5))
    assert pairs[0]['same_known_calendar_months']
    assert pairs[0]['direction']=='a_down_b_up'

def test_same_source_required_across_species_not_only_within_species():
    m=module(); data=fixture()
    for r in data[2:]: r['citekey']='other_source'
    annual,_=m.annual_pairs(data, {'A': {'region':'R1'}})
    pairs,rejected=m.match_species(annual, 'ADPE', 'GEPE')
    assert len(annual)==2 and not pairs and rejected['different_source']==1

def test_source_duplicate_group_excluded_even_equal_count():
    m=module(); data=fixture(); data.append({**data[0], 'id':'99'})
    annual,a=m.annual_pairs(data, {'A': {'region':'R1'}})
    assert a['duplicate_site_species_seasons']==1
    assert len(annual)==1
    assert not m.match_species(annual, 'ADPE', 'GEPE')[0]

def test_recorded_zero_is_not_positive_growth_or_pseudocount():
    m=module(); data=fixture();data[1]['count']='0'
    annual,a=m.annual_pairs(data, {'A': {'region':'R1'}})
    assert len(annual)==1 and a['nonpositive_pairs_excluded']==1
    assert not m.match_species(annual,'ADPE','GEPE')[0]

def test_same_known_method_and_real_adjacent_seasons_only():
    m=module();data=fixture();data[1]['vantage']='aerial';data[3]['season']='2003'
    annual,a=m.annual_pairs(data, {'A': {'region':'R1'}})
    assert not annual
    assert a['method_changes_or_unknown']==1

def test_no_false_calendar_precision():
    m=module();data=fixture();data[3]['month']=''
    annual,_=m.annual_pairs(data, {'A': {'region':'R1'}})
    pairs,_=m.match_species(annual,'ADPE','GEPE')
    assert len(pairs)==1 and not pairs[0]['same_known_calendar_months']

def test_equal_site_weighting_and_no_independent_year_replication():
    m=module()
    base={'region':'R','direction':'both_up','g_a':.1,'g_b':.2}
    rows=[dict(base,site_id='A',start=y,delta_log_ratio_b_over_a=1.) for y in range(10)]
    rows += [dict(base,site_id='B',start=0,delta_log_ratio_b_over_a=-1.)]
    out=m.summarize(rows)
    assert out['n_intervals']==11 and out['n_sites']==2
    assert out['equal_site_mean_log_ratio_change']==0.
    assert not out['causal_climate_or_competition_effect']
    assert out['site_weighted_fraction_b_outgrows_a']==.5

def test_no_duplicate_ids_or_invalid_numeric_source():
    m=module(); data=fixture();data[1]['id']='1'
    with pytest.raises(ValueError,match='duplicate observation'):
        m.annual_pairs(data,{'A': {'region':'R'}})
    data=fixture();data[0]['count']='nan'
    annual,a=m.annual_pairs(data,{'A': {'region':'R'}})
    assert len(annual)==1
