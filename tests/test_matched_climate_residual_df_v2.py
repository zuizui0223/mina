"""Regression tests: a source-count gate must not pass a saturated model."""
from pathlib import Path
import importlib.util
import pytest
pytest.importorskip('numpy')
P=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/climate_penguin/fit_MAPPPD5_matched_species_ERA5_v1.py'
spec=importlib.util.spec_from_file_location('target',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def saturated_fixture():
    # Sixteen rows; fifteen nuisance ranks plus climate leaves zero residual df.
    keys=[('A',y) for y in range(2000,2013)]+[('B',2000),('C',2001),('B',2001)]
    rows=[]
    for i,(site,year) in enumerate(keys):
        x=float(i==len(keys)-1)
        rows.append({'site_id':site,'source_region':'R1' if site=='A' else 'R2',
             'grid':site,'end_year':year,'climate':x,
             'relative_growth':2*x+.1*(year-2000)+(0 if site=='A' else 3)})
    return rows

def test_saturated_design_is_not_published_as_supported_coefficient():
    result=m.model(saturated_fixture(),'climate',True)
    assert result['per_1C_climate_coefficient'] is None
    assert result['status']=='SATURATED_NO_RESIDUAL_DF'
    assert result['residual_df']==0
    assert abs(result['algebraic_coefficient_audit_only']-2)<1e-9

def test_balanced_known_effect_remains_correct():
    rows=[]
    for i in range(5):
        for year in range(2005,2014):
            x=.15*(i-2)*(year%3-1)+.05*(year-2005)
            rows.append({'site_id':str(i),'source_region':'A' if i<3 else 'B',
                 'grid':str(i//2),'end_year':year,'climate':x,
                 'relative_growth':3*x+10*i+2*(year-2005)})
    r=m.model(rows,'climate',True)
    assert abs(r['per_1C_climate_coefficient']-3)<1e-9
    assert r['residual_df']==31
