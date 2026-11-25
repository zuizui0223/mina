"""V10: exact geography decomposition of fixed allocation change-field contrasts.
Usage: python geographic_change_field_v10.py ARTIFACT_DIR FIELD_PSV OUTPUT_DIR
FIELD_PSV is an exact column selection from pinned matched_support.csv; source blob
 da2b63a6d290d5f786badbcd0fbc0931f41ad52a, extracted blob df9dc7b5d5306f3cca24540eba62af5e8727a3a1.
No ecological regression or new primary source acquisition.
"""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
PINS={13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',14214704362:'c91e3a1126bdb9af2345fe08bcb201b3c21e802cbd2fcfe21db99faa2163c4d0'}
SOURCE_BLOB='df9dc7b5d5306f3cca24540eba62af5e8727a3a1'
V8_SHA='4f1e94d55e5f4a3d9b1297596dd736a2e5d1793308d30e0dcd787cbac2278863'
EXCLUDED={'BRDM','BRDN','BRDS','CRZE','CRZW','ROYD'}
MODELS={'ACCESS-CM2','BCC-CSM2-MR','CESM2'}
# Exact prior V9 values, 16 historical exposure rows: A,R,L,total.
V9='''long_parent23|sic_pp|0.37032184138766755|2.251585253278513|-0.6363009220882107|1.6152843311903098
long_complete17|sic_pp|-0.11725603674241462|5.583701391114419|-2.4822733195392344|3.1014280715751994
long_complete17|salinity|0.015661600382846325|0.04865930712401867|-0.010128921794011234|0.038530385330005856
long_complete17|sst_C|0.007489900290949958|-0.030818584221437958|0.004433225433039335|-0.026385358788399094
short_parent15_100|sic_pp|0.06717464149770681|0.22996806017072005|0.30041337934165324|0.5303814395123823
short_parent15_100|polynya_pp|0.13813720447732059|0.05914203535000003|2.5338667427632746|2.593008778113278
short_complete9_100|sic_pp|-0.19482648965005847|0.6866990045022429|-1.6805181705176122|-0.9938191660153706
short_complete9_100|salinity|-0.0010724260494552355|-0.0154623125367148|0.05995787736816983|0.04449556483145756
short_complete9_100|sst_C|-0.005829212242596511|-0.0061009212233104635|0.0020900996482515113|-0.004010821575058721
short_complete9_100|polynya_pp|0.2113201405011326|-0.4306608126975786|1.3039262702677124|0.8732654575701311
short_parent15_25|sic_pp|0.06717464149770681|0.22996806017072005|0.30041337934165324|0.5303814395123823
short_parent15_25|polynya_pp|0.0988200560972079|-1.0918126963485277|2.9864142720871296|1.8946015757386032
short_complete9_25|sic_pp|-0.19482648965005847|0.6866990045022429|-1.6805181705176122|-0.9938191660153706
short_complete9_25|salinity|-0.0010724260494552355|-0.0154623125367148|0.05995787736816983|0.04449556483145756
short_complete9_25|sst_C|-0.005829212242596511|-0.0061009212233104635|0.0020900996482515113|-0.004010821575058721
short_complete9_25|polynya_pp|0.14032334584088188|-1.97289073287493|0.713897315625297|-1.258993417249627'''
def close(a,b): np.testing.assert_allclose(a,b,atol=1e-9,rtol=0)
def read(root,i,member):
    raw=(root/f'github-actions-artifact-{i}.zip').read_bytes();assert hashlib.sha256(raw).hexdigest()==PINS[i]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        return pd.read_csv(z.open(member))
def norm(x):
    a=np.asarray(x,dtype=float);assert (a>=0).all() and a.sum()>0
    return a/a.sum()
def decompose(q,group,ref):
    p=norm(q.n0);r=norm(q.n1);x=q.field.to_numpy()-ref
    z=q.assign(p0=p,p1=r,centered=x,contribution=(r-p)*x)
    a=float((r-p)@x); rows=[]
    for key,g in z.groupby(group,sort=True):
        p0=float(g.p0.sum());p1=float(g.p1.sum());assert p0>0 and p1>0
        f0=float(g.p0@g.centered/p0);f1=float(g.p1@g.centered/p1)
        B=(p1-p0)*(f0+f1)/2;W=(p0+p1)/2*(f1-f0)
        close(B+W,g.contribution.sum())
        rows.append(dict(group=str(key),share0=p0,share1=p1,conditional_change=f1-f0,between=B,within=W,total=B+W))
    B=sum(k['between'] for k in rows);W=sum(k['within'] for k in rows);close(B+W,a)
    close(a,float((r-p)@q.field))
    return dict(total=a,between=B,within=W,groups=rows,sites=z[['site_id','source_region','p0','p1','field','contribution']].to_dict('records'))
def coverage(q,ref):
    q=q.assign(coverage=np.where(q.site_id.isin(EXCLUDED),'excluded','retained'))
    a=decompose(q,'coverage',ref);g={v['group']:v for v in a['groups']};k=g['retained'];o=g['excluded']
    ar=k['conditional_change'];ae=o['conditional_change'];penalty=k['within']-ar
    close(a['total']-ar,penalty+o['within']+a['between'])
    return dict(parent=a['total'],retained=ar,excluded=ae,retained_share0=k['share0'],retained_share1=k['share1'],retained_within=k['within'],excluded_within=o['within'],between_subsets=a['between'],retained_renormalization=penalty,parent_minus_retained=a['total']-ar)
def run(root,fixture):
    raw=fixture.read_bytes();assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==SOURCE_BLOB
    h=pd.read_csv(io.BytesIO(raw),sep='|');assert len(h)==53 and not h.duplicated(['comparison','radius','site_id']).any()
    n=read(root,13669533413,'source_observed_2456.csv');atlas=read(root,13669533413,'panantarctic_595_site_inventory.csv');m=read(root,14214704362,'source_root/outputs/cmip6_projection_v1/site_model_changes.csv')
    assert len(n)==2456 and len(atlas)==595 and len(m)==21420 and m.complete_years.eq(20).all() and set(m.source_id)==MODELS
    assert not m.duplicated(['site_id','source_id','variable_id','experiment_id','period']).any()
    mm=m.merge(atlas[['site_id','source_region','latitude','longitude']],on='site_id',validate='many_to_one',suffixes=('','_atlas'));close(mm.latitude,mm.latitude_atlas);close(mm.longitude,mm.longitude_atlas)
    j=h.merge(atlas[['site_id','source_region']],on='site_id',validate='many_to_one',suffixes=('','_atlas'));assert j.source_region.eq(j.source_region_atlas).all()
    with zipfile.ZipFile(root/'mina_antarctic_bridges_v7_v8.zip') as z:
        assert z.testzip() is None;raw8=z.read('HISTORICAL_ALLOCATION_FUTURE_EXPOSURE_RESULT_V8.json');assert hashlib.sha256(raw8).hexdigest()==V8_SHA;v8=json.loads(raw8)
    prev={(q['name'],r['scenario'],r['period'],r['variable'],v['model']):v['late_minus_early'] for q in v8['cohorts'] if q['name'].endswith('_all') for r in q['rows'] for v in r['models']};assert len(prev)==144
    old={(x[0],x[1]):list(map(float,x[2:])) for x in [s.split('|') for s in V9.splitlines()]};assert len(old)==16
    out={'status':'EXECUTED_FIXED_FIELD_GEOGRAPHIC_ACCOUNTING','pins':PINS,'historical_extract_blob':SOURCE_BLOB,'v8_json_sha256':V8_SHA,'historical':[],'future':[],'coverage':[],'limits':'Exact deterministic decomposition of fixed site-period median count weights, not ecological mechanisms or causal climate adaptation. Model and roster outputs are dependent. Historical vs projected fields have different baseline/interval/source.'}
    for label,comparison,radius,periods,nsite in [('long','long',0,[(1993,2000),(2011,2020)],23),('short','polynya',100,[(2004,2010),(2013,2020)],15),('short','polynya',25,[(2004,2010),(2013,2020)],15)]:
        parent=h[(h.comparison==comparison)&(h.radius==radius)].sort_values('site_id').copy();assert len(parent)==nsite
        complete=parent[~parent.site_id.isin(EXCLUDED)].copy();assert len(complete)==nsite-6
        for k,(lo,hi) in enumerate(periods):
            nn=n[n.species.eq('ADPE')&n.season.between(lo,hi)&n.site_id.isin(parent.site_id)]
            a=nn.groupby('site_id').observed_nest_count.agg(['median','size']);assert a['size'].ge(2).all();assert set(a.index)==set(parent.site_id);close(parent.set_index('site_id')[f'n{k}'],a['median'].reindex(parent.site_id))
        def histname(sub,q):return f'{label}_{sub}{len(q)}'+(f'_{radius}' if radius else '')
        for var in ['sic_pp','salinity','sst_C','polynya_pp']:
            for sub,q0 in [('parent',parent),('complete',complete)]:
                name=histname(sub,q0)
                if (name,var) not in old:continue
                q=q0.assign(field=q0[var+'1']-q0[var+'0']);assert q.field.notna().all()
                p,r=norm(q.n0),norm(q.n1);a=q[var+'0'].to_numpy();b=q[var+'1'].to_numpy()
                ref=float((parent[var+'1']-parent[var+'0']).mean()) if parent[[var+'0',var+'1']].notna().all().all() else float(q.field.mean())
                z=decompose(q,'source_region',ref);R=float((r-p)@((a+b)/2));L=float(((p+r)/2)@(b-a));T=float(r@b-p@a);close([z['total'],R,L,T],old[name,var]);out['historical'].append(dict(cohort=name,variable=var,reference=ref,**z))
                if sub=='parent':out['coverage'].append(dict(era='historical',cohort=name,variable=var,**coverage(q,ref)))
        if radius==25:continue
        # All four scenario-periods, all three models, all three physical variables.
        for (exp,period,var,model),f in mm[mm.site_id.isin(parent.site_id)].groupby(['experiment_id','period','variable_id','source_id']):
            q=parent.merge(f[['site_id','change']],on='site_id',validate='one_to_one').rename(columns={'change':'field'});assert len(q)==len(parent);ref=float(q.field.mean())
            for sub,qq in [('parent',q),('complete',q[~q.site_id.isin(EXCLUDED)])]:
                name=f'{label}_{sub}{len(qq)}_all';z=decompose(qq,'source_region',ref);close(z['total'],prev[name,exp,period,var,model]);out['future'].append(dict(cohort=name,scenario=exp,period=period,variable=var,model=model,reference=ref,**z))
            out['coverage'].append(dict(era='future',cohort=f'{label}_parent{len(q)}_all',scenario=exp,period=period,variable=var,model=model,**coverage(q,ref)))
    assert len(out['historical'])==16 and len(out['future'])==144 and len(out['coverage'])==77
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('fixture',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    z=run(a.root,a.fixture);(a.out/'GEOGRAPHIC_CHANGE_FIELD_ATTRIBUTION_V10.json').write_text(json.dumps(z,indent=2,allow_nan=False)+'\n')
    for key in ['historical','future','coverage']:
        t=pd.DataFrame([{k:v for k,v in r.items() if k not in ['groups','sites']} for r in z[key]]);t.to_csv(a.out/f'{key}_V10.csv',index=False)
    print('Verified 16 historical and 144 future model contrasts, 77 parent/complete coverage decompositions.')
