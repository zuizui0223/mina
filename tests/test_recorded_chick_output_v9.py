import importlib.util,math
from pathlib import Path
import pytest
P=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/recorded_chick_output_v9.py'
def mod():
 s=importlib.util.spec_from_file_location('chick_output_v9',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def row(i,t,n,source='x',year=2010,month='',day='',sp='CHPE',site='ARDL'):
 return dict(id=str(i),site_id=site,species_id=sp,season='2010',year=str(year),month=str(month),day=str(day),count=str(n),type=t,citekey=source,vantage='ground',presence='1')

def test_ratio_and_zero_are_not_missing():
 m=mod();p,a=m.stage_pairs([row(1,'nests',10),row(2,'chicks',0)])
 assert len(p)==1 and p[0]['recorded_chicks_per_nest']==0
 assert p[0]['fledging_stage_confirmed'] is False

def test_zero_denominator_is_excluded():
 m=mod();p,a=m.stage_pairs([row(1,'nests',0),row(2,'chicks',4)])
 assert not p and a['nonpositive_nests']==1

def test_no_cross_source_match():
 m=mod();p,a=m.stage_pairs([row(1,'nests',10),row(2,'chicks',9,source='other')])
 assert not p

def test_duplicate_stage_never_averaged():
 m=mod();p,a=m.stage_pairs([row(1,'nests',10),row(2,'chicks',9),row(3,'chicks',11)])
 assert not p and a['duplicate_stage_groups']==1

def test_unknown_month_not_invented():
 m=mod();p,a=m.stage_pairs([row(1,'nests',10),row(2,'chicks',11)])
 assert p[0]['chronology']=='unresolved'
 assert p[0]['recorded_chicks_per_nest']==1.1

def test_actual_cross_year_date_support():
 m=mod();p,a=m.stage_pairs([row(1,'nests',10,month=11),row(2,'chicks',11,year=2011,month=2)])
 assert p[0]['chronology']=='nest_interval_precedes_chick_interval'

def test_reversed_dates_remain_flagged_not_reassigned():
 m=mod();p,a=m.stage_pairs([row(1,'nests',10,month=12),row(2,'chicks',9,month=1)])
 assert p[0]['chronology']=='reported_chicks_before_nests'

def test_ratio_greater_than_two_not_clipped():
 m=mod();p,a=m.stage_pairs([row(1,'nests',2),row(2,'chicks',9)])
 assert p[0]['recorded_chicks_per_nest']==4.5 and p[0]['ratio_above_two']

def test_paired_seasons_never_shifted():
 m=mod();r=[]
 for site,n,c in [('ARDL',10,12),('BART',20,30)]:
  for sp in ['CHPE','GEPE']:
   r.extend([row(len(r)+1,'nests',n,source='kpri2020report6',sp=sp,site=site),row(len(r)+2,'chicks',c,source='kpri2020report6',sp=sp,site=site)])
 pairs,_=m.stage_pairs(r);z=m.neighbor_comparison(pairs)
 assert z['n_matched_seasons']==1
 assert math.isclose(z['by_species']['CHPE']['mean_ardley_minus_barton'],-.3)
 assert z['by_species']['CHPE']['across_site_pearson_r'] is None
 assert z['causal_effect_identified'] is False

def test_duplicate_original_id_rejected():
 m=mod()
 with pytest.raises(ValueError,match='duplicate observation'):
  m.stage_pairs([row(1,'nests',10),row(1,'chicks',9)])
