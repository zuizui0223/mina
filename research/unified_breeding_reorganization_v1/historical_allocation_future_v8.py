"""Fixed historical allocation × CMIP6 physical exposure, V8. No animal forecast.
Usage: python historical_allocation_future_v8.py ARTIFACT_DIRECTORY RESULT.json
"""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
PINS={13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',14214704362:'c91e3a1126bdb9af2345fe08bcb201b3c21e802cbd2fcfe21db99faa2163c4d0'}
# Exact V5 parent rosters and site-period medians from pinned matched_support.csv.
LONG='ANNE:171:363.5 ARDL:1134:384 BISC:1665:544.5 BRDM:2561:4343 BRDN:24565:45572 BRDS:9788.5:16764 CHAL:40896:47169 CMID:4138:13185 CRZE:17555:29800 CRZW:105103:251250 CSOU:13219:27292 INEX:21137:34358 LLAN:5522:2354 MAND:14867:24721 NORF:8994:13408 PETE:742:238 PGEO:36103:47058 PHIL:4936:13460 PLEN:0:0 PTHO:9731:3782 ROYD:3411:3058 WHEA:2111.5:1907 WOOD:1501.5:2925'
SHORT='ARDL:409:381 BRDM:3704:4343 BRDN:35077:45572 BRDS:12516:16764 CRZE:24203:29800 CRZW:176342:258031 INEX:30657.5:34358 LLAN:2393:2354 NORF:17913.5:13408 PCHA:11:9 PETE:444.5:238 PGEO:35401:47058 PLEN:0:0 ROYD:2513:3058 WOOD:2728:2925'
EXCLUDED={'BRDM','BRDN','BRDS','CRZE','CRZW','ROYD'}
MODELS={'ACCESS-CM2','BCC-CSM2-MR','CESM2'}
def read(root,i,member):
    b=(root/f'github-actions-artifact-{i}.zip').read_bytes();assert hashlib.sha256(b).hexdigest()==PINS[i]
    with zipfile.ZipFile(io.BytesIO(b)) as z:assert z.testzip() is None;return pd.read_csv(z.open(member))
def calc(q):
    a=q.n0.to_numpy();b=q.n1.to_numpy();x=q.change.to_numpy();p=a/a.sum();r=b/b.sum()
    early=float(p@x);late=float(r@x);d=late-early
    assert abs(d-float((r-p)@x))<1e-10
    return dict(equal=float(x.mean()),early=early,late=late,late_minus_early=d)
def run(root):
    n=read(root,13669533413,'source_observed_2456.csv');atlas=read(root,13669533413,'panantarctic_595_site_inventory.csv');m=read(root,14214704362,'source_root/outputs/cmip6_projection_v1/site_model_changes.csv');g=read(root,14214704362,'source_root/outputs/cmip6_projection_v1/coastal_grid_support.csv')
    assert len(n)==2456 and len(atlas)==595 and len(m)==21420 and len(g)==5355
    assert not m.duplicated(['site_id','source_id','variable_id','experiment_id','period']).any() and m.complete_years.eq(20).all() and set(m.source_id)==MODELS
    assert m.change.notna().all() and set(m.variable_id)=={'siconc','sos','tas'}
    assert set(m.site_id)==set(atlas.site_id)
    m=m.merge(atlas[['site_id','latitude','longitude','source_region']],on='site_id',validate='many_to_one',suffixes=('','_atlas'))
    assert np.allclose(m.latitude,m.latitude_atlas,atol=1e-8,rtol=0) and np.allclose(m.longitude,m.longitude_atlas,atol=1e-8,rtol=0)
    marine=g[g.variable_id.isin(['siconc','sos'])];assert marine.groupby('site_id').size().eq(6).all();near=set(marine.groupby('site_id').distance_km.max().loc[lambda x:x<=50].index)
    out={'status':'EXECUTED_FIXED_ALLOCATION_PHYSICAL_SCENARIOS','source_pins':PINS,'marine50_sites_all595':len(near),'cohorts':[],'limitations':'Same nominal fixed rosters; noncontemporaneous observed site medians, not future population forecasts. Three illustrative GCMs, shared grid cells, no inferred adaptation or polynya/vegetation/diet prediction.'}
    for label,src,periods,expected in [('long',LONG,[(1993,2000),(2011,2020)],[(329851.5,583936),(166868,233149)]),('short',SHORT,[(2004,2010),(2013,2020)],[(344312.5,458299),(89957.5,100731)])]:
        w=pd.DataFrame([s.split(':') for s in src.split()],columns=['site_id','n0','n1']);w[['n0','n1']]=w[['n0','n1']].astype(float)
        for k,(lo,hi) in enumerate(periods):
            z=n[n.species.eq('ADPE')&n.season.between(lo,hi)&n.site_id.isin(w.site_id)];a=z.groupby('site_id').observed_nest_count.agg(['median','size']);assert a['size'].ge(2).all();assert set(a.index)==set(w.site_id);assert np.allclose(w.set_index('site_id')[f'n{k}'].sort_index(),a['median'].sort_index())
        for i,(sub,ww) in enumerate([('parent',w),('complete',w[~w.site_id.isin(EXCLUDED)])]):
            assert tuple(ww[['n0','n1']].sum())==expected[i]
            for support,s in [('all',ww),('marine50',ww[ww.site_id.isin(near)])]:
                q=m.merge(s,on='site_id',validate='many_to_one');assert len(q)==len(s)*36
                row={'name':f'{label}_{sub}{len(ww)}_{support}','sites':len(s),'regions':q.source_region.nunique(),'n0':float(s.n0.sum()),'n1':float(s.n1.sum()),'site_ids':s.site_id.tolist(),'rows':[]}
                if len(s)<3 or row['regions']<2 or row['n0']<=0 or row['n1']<=0:row['status']='STOP_INSUFFICIENT_SUPPORT'
                else:
                    row['status']='DESCRIPTIVE_PHYSICAL_ONLY'
                    for (exp,period,var),v in q.groupby(['experiment_id','period','variable_id']):
                        a=[]
                        for model,gg in v.groupby('source_id'):
                            assert len(gg)==len(s);r=calc(gg);r['model']=model;r['grid_cells']=gg.grid_cell_id.nunique();r['region_omission']={reg:calc(gg[gg.source_region!=reg])['late_minus_early'] for reg in sorted(gg.source_region.unique()) if len(gg[gg.source_region!=reg])>=2 and gg[gg.source_region!=reg].n0.sum()>0 and gg[gg.source_region!=reg].n1.sum()>0};a.append(r)
                        assert len(a)==3
                        mean={k:float(np.mean([x[k] for x in a])) for k in ['equal','early','late','late_minus_early']}
                        d=[x['late_minus_early'] for x in a];r={'scenario':exp,'period':period,'variable':var,'model_mean':mean,'models':a,'all_models_same_sign':bool(min(d)>0 or max(d)<0),'all_region_omissions_same_sign_as_model':all(all(x['late_minus_early']*v>0 for v in x['region_omission'].values()) for x in a)};row['rows'].append(r)
                out['cohorts'].append(row)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.write_text(json.dumps(run(a.root),indent=2,allow_nan=False)+'\n')
