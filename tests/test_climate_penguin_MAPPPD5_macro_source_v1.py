"""Mock original records check ancestry and same citation/vantage source gate."""
import pytest
pytest.importorskip("requests")
import importlib.util
from pathlib import Path
S=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/derive_MAPPPD5_original_macro_source_v1.py"
def mod():
 s=importlib.util.spec_from_file_location("source_macro_MAPPPD5",S)
 x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x

def mkobs(id,year,count="100",cite="A",vantage="ground",stage="nests",species="ADPE"):
 return dict(id=str(id),site_id="ABC",site_name="ABC Site",
             species_id=species,season=str(year),count=count,type=stage,
             presence="1",vantage=vantage,citekey=cite,mapppd_version="5.0")
def make():
 sites=[dict(site_id="ABC",site_name="ABC Site",region="South Shetland Islands",
             latitude="-62",longitude="-58",mapppd_version="5.0")]
 for i in range(728):
  sites.append(dict(site_id=f"S{i:03}",site_name=f"Other{i}",region="Victoria Land",
             latitude="-75",longitude="165",mapppd_version="5.0"))
 return sites

def test_numeric_present_and_frozen_sha_source_provenance():
 x=mod()
 assert x.numeric("0") and x.numeric("12.5") and x.numeric("1,234")
 assert not x.numeric("") and not x.numeric("-1") and not x.numeric("bad")
 assert x.PINS["observations_p1"]=="cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075"

def test_no_duplicate_year_source_conflict_or_missing_year_imputation():
 x=mod()
 # 5487 valid observed rows required even when most rows are uninformative.
 obs=[mkobs(1,2001),mkobs(2,2002)]
 obs.extend(mkobs(i+3,2010+i,stage="chicks") for i in range(5485))
 # all IDs unique; nonnumeric years beyond 2026 are skipped.
 pairs,stats=x.strict_pairs(make(),obs)
 assert len(pairs)==1
 assert pairs[0]["start"]==2001 and pairs[0]["end"]==2002
 assert pairs[0]["actual_survey_month_known"] is False
 assert pairs[0]["verified_physical_island"] is False
 # conflicting source citation forbids pair.
 obs[1]["citekey"]="DIFFERENT"
 paired,_=x.strict_pairs(make(),obs)
 assert not paired
 # duplicate exact site×species×year invalidates original record.
 obs[1]["citekey"]="A"
 obs[2]=mkobs(3,2001)  # duplicates original 2001
 paired,_=x.strict_pairs(make(),obs)
 assert not paired
