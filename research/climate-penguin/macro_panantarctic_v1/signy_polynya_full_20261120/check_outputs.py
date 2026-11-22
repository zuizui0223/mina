"""Independent consistency checks, including non-identifiable synthetic designs."""
import csv, importlib.util, tempfile
from pathlib import Path
import numpy as np
import pandas as pd

here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('analysis',here/'analyze.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as tmp:
    m.HERE=Path(tmp)
    d=pd.DataFrame({'season':range(2003,2013),'n_valid':30,'krill_fraction':[.9,.8]*5,'sampling_day':range(60,70)})
    e=pd.DataFrame({'site':'Signy','radius_km':100,'season':range(2003,2013),'polynya_fraction':0.})
    assert m.fit(d,e)['verdict']=='NOT_ESTIMABLE_INSUFFICIENT_EXPOSURE_OR_YEARS'
    e['polynya_fraction']=[.1,.2]*5
    assert m.fit(d,e)['verdict']=='NOT_ESTIMABLE_RANK_DEFICIENT'

s=pd.read_csv(here/'stomach_audit.csv').fillna({'exclusion_reason':''})
a=pd.read_csv(here/'signy_annual_diet.csv')
assert len(s)==639 and a.n_raw.sum()==639 and a.n_valid.sum()==638
assert s.loc[s.DATE.eq('2002-01-03'),'season'].eq(2001).all()
assert s.loc[s.DATE.eq('2020-01-18'),'season'].eq(2019).all()
assert not s.duplicated(['DATE','RECORD_ID']).any()
for r in a.itertuples():
    v=s[s.season.eq(r.season)&s.exclusion_reason.eq('')]
    assert len(v)==r.n_valid
    assert abs(sum(v.krill_fraction)/len(v)-r.krill_fraction)<1e-12
if (here/'annual_environment.csv').exists():
    e=pd.read_csv(here/'annual_environment.csv')
    assert not e.duplicated(['site','radius_km','season']).any()
    assert e.loc[~e.passes_coverage,'polynya_fraction'].isna().all()
    assert e.polynya_fraction.dropna().between(0,1).all()
    assert (~e.loc[e.season.isin([2011,2012]),'passes_coverage']).all()
print('PASS: source counts, boundary years, annual means, missing exposure and non-identifiability gates')
