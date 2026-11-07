"""Same-row salt/MLD conditional correlations; no mediation identification."""
from pathlib import Path
import hashlib,json
import pandas as pd
import numpy as np
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'salinity_mixed_layer_v1';out.mkdir(exist_ok=True)
source=root/'relationship_response_v1/cohort.csv';raw_source=root/'climate_penguin/behavior_ocean_join.csv'
frozen_source=root/'salinity_sensitivity_v1/specifications.csv'
d=pd.read_csv(source);raw=pd.read_csv(raw_source).set_index('source_row_1based');frozen=pd.read_csv(frozen_source)
assert raw.index.is_unique
values=[]
for r in d.itertuples():
    ids=list(map(int,r.source_rows.split('|')));q=raw.loc[ids]
    assert len(q)==r.camera_rows and q.species.eq(r.species).all() and q.cam.eq(r.cam).all() and q.season_start_year.eq(r.year).all()
    assert q.ocean_m9_mixed_layer_depth_m.notna().all() and q.ocean_m9_mixed_layer_depth_m.gt(0).all()
    values.append(q.ocean_m9_mixed_layer_depth_m.mean())
d['mld_m']=values;d['mld10']=d.mld_m/10;d['log_mld']=np.log(d.mld_m)
d.to_csv(out/'cohort.csv',index=False)
def residual(v,z):return v-z@np.linalg.lstsq(z,v,rcond=None)[0]
def calculate(a,mode,form):
    z=pd.get_dummies(a.cam,dtype=float).to_numpy()
    if mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.year,drop_first=True,dtype=float)])
    z=np.column_stack([z,a[['ice10','waterC','airC']].to_numpy()])
    y=a.y.to_numpy();salt=a.salt01.to_numpy();mld=a[form].to_numpy()
    rs=residual(salt,z);rm=residual(mld,z);ry=residual(y,z)
    def cor(x,y):return x@y/np.sqrt((x@x)*(y@y))
    zs=np.column_stack([z,mld]);zm=np.column_stack([z,salt])
    ss=residual(salt,zs);sy=residual(y,zs);mm=residual(mld,zm);my=residual(y,zm)
    beta=ss@sy/(ss@ss);direct=np.linalg.lstsq(np.column_stack([z,mld,salt]),y,rcond=None)[0][-1]
    assert np.isclose(beta,direct,atol=1e-8)
    assert np.linalg.matrix_rank(np.column_stack([z,mld,salt]))==np.linalg.matrix_rank(z)+2
    return dict(salt_r_before=cor(rs,ry),salt_r_after=cor(ss,sy),mld_r_given_salt=cor(mm,my),
        salt_mld_r=cor(rs,rm),salt_residual_fraction=(ss@ss)/(rs@rs),salt_coefficient_per_01=beta,
        df=len(a)-np.linalg.matrix_rank(np.column_stack([z,mld,salt])))
rows=[];deletions=[]
for (scope,sp),a in d.groupby(['scope','species']):
    for mode in ['site','site_year']:
        original=frozen[(frozen.scope==scope)&(frozen.species==sp)&(frozen['mode']==mode)&(frozen.controls=='ice_water_air')].iloc[0]
        for form in ['mld10','log_mld']:
            key=dict(scope=scope,species=sp,mode=mode,form=form)
            result=calculate(a,mode,form);assert np.isclose(result['salt_r_before'],original.partial_r,atol=1e-9)
            rows.append(dict(**key,n=len(a),sites=a.cam.nunique(),years=a.year.nunique(),**result))
            for year in sorted(a.year.unique()):deletions.append(dict(**key,deleted_year=int(year),**calculate(a[a.year!=year],mode,form)))
t=pd.DataFrame(rows);de=pd.DataFrame(deletions)
assert len(t)==24
t.to_csv(out/'comparisons.csv',index=False);de.to_csv(out/'year_deletions.csv',index=False)
v=dict(passed=True,specifications=24,year_deletion_fits=len(de),main_rows=int(d.scope.eq('all_source_labels').sum()),
    missing_mld=0,inputs={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,raw_source,frozen_source]},
    limits=['Same reanalysis, not independent observations of stratification or prey',
            'Conditional correlation change is not a mediated proportion or causal adjustment',
            'No p-values or future MLD projection in this descriptive comparison'])
(out/'validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
print(t[(t.scope=='all_source_labels')&(t.form=='mld10')].to_string(index=False))
