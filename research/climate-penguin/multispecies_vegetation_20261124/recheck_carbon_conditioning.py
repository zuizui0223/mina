"""Public-source diagnostic: conditional soil associations, not mediation.
Usage: python recheck_carbon_conditioning.py ZENODO_DIRECTORY USAP_ZIP OUTPUT_DIRECTORY
Requires numpy, pandas, openpyxl. Never uses restricted AADC data.
Sources: Iannuzzi et al. 2025 DOI 10.5281/zenodo.17742676;
Ball 2025 DOI 10.15784/602015 (CC BY 4.0).
"""
import hashlib, io, json, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

D,P,O=map(Path,sys.argv[1:]); O.mkdir(parents=True,exist_ok=True)
md5=lambda b:hashlib.md5(b).hexdigest()
for name,h in {'Pygoscelis_metadata.csv':'b58d6e6b476c98afeb9f4e75f8f520fe','Pygoscelis_PP.csv':'fa57915e1d1253a6eeac36e70579ccf9','Methods.txt':'0a2430c1943387e5369159ea950774f2'}.items():
    assert md5((D/name).read_bytes())==h
m=pd.read_csv(D/'Pygoscelis_metadata.csv',sep=';');q=pd.read_csv(D/'Pygoscelis_PP.csv',sep=';')
for a in (m,q):assert a.loc[a.Sample.isna()].isna().all().all()
m=m.dropna(subset=['Sample']);q=q.dropna(subset=['Sample']);assert m.Sample.is_unique and q.Sample.is_unique and set(m.Sample)==set(q.Sample)
a=m.merge(q,on='Sample',validate='1:1').rename(columns={'Site':'site','Penguin species':'species','CH (%)':'water','CO (%)':'carbon','N-NH4 (mg/kg)':'nh4','NO3-N (mg/kg)':'no3'})
a['group']=a.Sample.str.replace(r'\d+$','',regex=True);a['year']=pd.to_datetime(a.Date,format='%d-%m-%Y').dt.year.astype(str)
assert len(a)==87 and a.group.nunique()==29 and a.site.nunique()==23 and a.groupby('group').size().eq(3).all()
with zipfile.ZipFile(P) as z:
    n=[n for n in z.namelist() if n.endswith('FineScaleSurvey_ArchiveData.xlsx')];assert len(n)==1
    raw=z.read(n[0]);assert md5(raw)=='75cc48e8ca21d8b408098a14692e6d3e'
b=pd.read_excel(io.BytesIO(raw)).rename(columns={'Site':'site','Stage':'stage','Cover':'cover','Swc':'water','OrgC':'carbon','Ammon':'nh4','Nitr':'no3','TotalN':'totalN'})
b['stratum']=b.site+'|'+b.stage;b['group']=b.stratum+'|'+b.cover
assert len(b)==132 and not b.duplicated(['group','Rep']).any() and b.groupby('group').size().eq(3).all() and b.group.nunique()==44

# Equal group weights; common complete-case support for both models.
# In between-group models use arithmetic means of natural logs; within-group
# models use weighted demeaning so each group contributes equal total weight.
def fit(d,y,fe,within,conditional):
    names=['water']+(['carbon'] if conditional else [])
    if within:
        sizes=d.groupby('group').size();d=d[d.group.isin(sizes[sizes>=2].index)].copy()
        w=1/d.groupby('group').group.transform('size').to_numpy()
        v=d[names+[y]]-d.groupby('group')[names+[y]].transform('mean')
        X=v[names].to_numpy();Y=v[y].to_numpy()
    else:
        w=np.ones(len(d));Y=d[y].to_numpy()
        X=np.column_stack([d[names].to_numpy(),np.ones(len(d)),pd.get_dummies(d[fe].astype(str),drop_first=True,dtype=float).to_numpy()])
    s=np.sqrt(w);beta,_,rank,_=np.linalg.lstsq(X*s[:,None],Y*s,rcond=None)
    if rank<X.shape[1]:raise ValueError('rank-deficient')
    return float(beta[0]),float(beta[1]) if conditional else None,len(d),d.group.nunique()

def paired(d,y,fe,within):
    x=fit(d,y,fe,within,False);z=fit(d,y,fe,within,True)
    assert x[2:]==z[2:];return x,z

rows=[];site_rows=[]
for name,data,fe in [('colony',a,['species','year']),('succession',b,['stratum','cover'])]:
    for y in ['nh4','no3']+(['totalN'] if name=='succession' else []):
        d=data.copy()
        for k in ['water','carbon',y]:
            v=pd.to_numeric(d[k],errors='coerce');d[k]=np.log(v.where(v>0))
        d=d.dropna(subset=['water','carbon',y]);assert np.isfinite(d[['water','carbon',y]]).all().all()
        for grain in ['between','within']:
            within=grain=='within';g=d.copy()
            if not within:
                agg={k:'first' for k in ['site']+fe};agg.update({k:'mean' for k in ['water','carbon',y]});g=d.groupby('group',as_index=False).agg(agg)
            u,c=paired(g,y,fe,within);del_u=[];del_c=[]
            for site in sorted(g.site.unique()):
                try:
                    uu,cc=paired(g[g.site!=site],y,fe,within);del_u.append(uu[0]);del_c.append(cc[0]);site_rows.append(dict(study=name,outcome=y,grain=grain,omitted_site=site,water_unadjusted=uu[0],water_carbon_adjusted=cc[0],carbon_adjusted=cc[1]))
                except ValueError:site_rows.append(dict(study=name,outcome=y,grain=grain,omitted_site=site,status='rank_deficient'))
            # Independently verify the partial coefficient with residualization on carbon and FE.
            if within:
                v=g[['water','carbon',y]]-g.groupby('group')[['water','carbon',y]].transform('mean');w=1/g.groupby('group').group.transform('size').to_numpy();Z=v[['carbon']].to_numpy();x=v.water.to_numpy();r=v[y].to_numpy()
            else:
                w=np.ones(len(g));Z=np.column_stack([g.carbon,np.ones(len(g)),pd.get_dummies(g[fe].astype(str),drop_first=True,dtype=float)]);x=g.water.to_numpy();r=g[y].to_numpy()
            s=np.sqrt(w);Z=Z*s[:,None];x=x*s;r=r*s;xx=x-Z@np.linalg.lstsq(Z,x,rcond=None)[0];rr=r-Z@np.linalg.lstsq(Z,r,rcond=None)[0];assert np.isclose(xx@rr/(xx@xx),c[0],atol=1e-10)
            rows.append(dict(study=name,outcome=y,grain=grain,n=u[2],groups=u[3],sites=g.site.nunique(),water_unadjusted=u[0],water_carbon_adjusted=c[0],carbon_adjusted=c[1],loo_unadjusted_min=min(del_u),loo_unadjusted_max=max(del_u),loo_adjusted_min=min(del_c),loo_adjusted_max=max(del_c),n_loo=len(del_c)))
pd.DataFrame(rows).to_csv(O/'conditional_associations.csv',index=False);pd.DataFrame(site_rows).to_csv(O/'site_deletion.csv',index=False)
(O/'receipt.json').write_text(json.dumps({'source_zenodo':'10.5281/zenodo.17742676','source_usap':'10.15784/602015','workbook_md5':md5(raw),'comparisons':len(rows),'validation':'all partial water slopes independently reproduced by residualization','interpretation':'descriptive conditional associations, no causal mediation; three succession sites only; no marine N tracer or plant response'},indent=2)+'\n')
print(pd.DataFrame(rows).round(5).to_string(index=False))
