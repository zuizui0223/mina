import importlib.util
from pathlib import Path
import pytest
P=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/seaice_monthly_source_v4.py'
def mod():
    assert P.exists(), 'monthly source reader missing'
    sp=importlib.util.spec_from_file_location('monthly_source',P)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def test_unique_southern_monthly_source_not_daily_or_other_release():
    m=mod(); rows=[{'url_path':'osisaf/x/monthly/ice_conc_sh_ease2-250_cdr-v3p1_199308.nc'}, {'url_path':'osisaf/x/monthly/ice_conc_nh_ease2-250_cdr-v3p1_199308.nc'}]
    assert m.choose_file(rows,1993,8)==rows[0]['url_path']
    with pytest.raises(ValueError):m.choose_file(rows,1993,9)
    with pytest.raises(ValueError):m.choose_file(rows+rows[:1],1993,8)
    with pytest.raises(ValueError):m.choose_file([{'url_path':'osisaf/x/daily/ice_conc_sh_ease2-250_cdr-v3p1_199308011200.nc'}],1993,8)

def test_select_only_needed_catalogs_by_name_not_entire_parent_path():
    m=mod(); root='https://thredds.met.no/thredds/catalog/x/monthly/catalog.xml'
    refs=[{'name':'1978','url':root.replace('catalog.xml','1978/catalog.xml')},{'name':'1993','url':root.replace('catalog.xml','1993/catalog.xml')}]
    assert m.needed_refs(refs,[1993])==[refs[1]['url']]
