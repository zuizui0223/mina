"""Verify manuscript assets against pinned upstream aggregates, not forecast validity."""
from pathlib import Path
import hashlib,json,re
import numpy as np
import pandas as pd

root=Path(__file__).resolve().parents[2]/'outputs'
out=root/'diet_niche_manuscript_v1'
m=json.loads((out/'ASSET_MANIFEST.json').read_text())
for name,sha in m['inputs'].items():
    assert hashlib.sha256((root/Path(name.replace('\\','/'))).read_bytes()).hexdigest()==sha,name
t=pd.read_csv(out/'Table_1_observed_support.csv')
assert len(t)==9 and t[['n_Adelie','n_Chinstrap','n_Gentoo']].sum().tolist()==[349,350,73]
r=np.corrcoef(t.sic_aug_nov,t.distance)[0,1]
e=pd.read_csv(out/'Table_2_effects_and_inference.csv').query('metric=="fish"').iloc[0]
assert np.isclose(r,e.r) and np.isclose(r,.784042737486591)
s=pd.read_csv(out/'Table_3_conditional_sensitivity.csv')
assert np.isclose(s.loc[s.reduction_pp.eq(10),'conditional_gap_change'].iloc[0],-e.slope_per_10pp)
assert s.loc[s.reduction_pp.eq(30),'conditional_gap_change'].isna().all()
c=pd.read_csv(out/'Table_S1_model_scenarios.csv')
assert len(c)==12 and c.within_observed_diet_sic_range.sum()==11
assert len(pd.read_csv(out/'CMIP6_SOURCE_STORES.csv'))==9
links=0
for file in out.glob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
        if '://' in link or link.startswith('#'):continue
        assert (file.parent/link.split('#')[0]).exists(),(file.name,link)
        links+=1
for p in (out/'figures').glob('*.pdf'):assert p.read_bytes().startswith(b'%PDF')
assert len(list((out/'figures').glob('*.pdf')))==3
assert len(list((out/'figures').glob('*.png')))==3
references=json.loads((out/'references.json').read_text(encoding='utf-8'))['references']
assert len(references)==9
assert next(r for r in references if r['id']=='Pickett2018')['doi']=='10.1002/ece3.4445'
result=dict(status='pass',input_hashes=len(m['inputs']),years=9,stomachs=772,model_conditions=12,local_links=links,figures=3,
            references=len(references),scope='Signy asset/source arithmetic and all manuscript local links; external comparison verified in its own output; not biological forecast validation')
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
