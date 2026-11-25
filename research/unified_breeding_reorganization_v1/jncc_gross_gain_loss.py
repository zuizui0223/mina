"""V3 original JNCC gain-loss accounting, fixed totals and pooled-composition null."""
import argparse, hashlib, json, sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from jncc_all_direction import values, group
GROUPS=('decline','near_stable','increase')
R=999;B=1999
METRICS=('counterflow','material_counterflow')
def measures(a,b):
    a=np.asarray(a,dtype=np.int64);b=np.asarray(b,dtype=np.int64)
    d=b-a;g=np.maximum(d,0).sum(axis=-1);l=np.maximum(-d,0).sum(axis=-1)
    n0=a.sum(axis=-1);n1=b.sum(axis=-1)
    if not np.all(g-l==n1-n0):raise AssertionError('gain-loss identity')
    c=2*np.minimum(g,l)/(n0+n1)
    # Compare exact integer ratio to 5%, rather than use rounded C.
    material=40*np.minimum(g,l)>=n0+n1
    return np.stack([c,material],axis=-1),g,l
def local(a,b):
    m,g,l=measures(a,b);q=values(a,b)
    pos=int((a>0).sum())
    return dict(C=float(m[0]),material=bool(m[1]),mixed=bool(g>0 and l>0),
                any_gain=bool(g>0),any_loss=bool(l>0),positive_to_zero=int(((a>0)&(b==0)).sum()),zero_to_positive=int(((a==0)&(b>0)).sum()),n_baseline_positive=pos,initial_zero=int((a==0).sum()),
                lost_site_fraction=float(((a>0)&(b==0)).sum()/pos),deltaU=float(q[2]),TV=float(q[0]))
def source(path):
    sys.path.insert(0,str(path/'scripts'))
    import audit_jncc_two_censuses_source_v28 as v28
    import audit_jncc_comparable_site_panels_v29 as v29
    import model_jncc_component_concentration_v30 as v30
    raw,meta=v28.download_original()
    assert hashlib.sha256(raw).hexdigest()==v29.ORIGINAL_SHA==meta['original_sha256']=='9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4'
    allrows=list(v29.original_rows(raw));qa=v29.coverage(allrows)
    assert qa['unique_original_two_census_site_species_rows_after_literal_QA']==14112 and qa['qualified_species_country_master_unit_panels_with_ge3_sites']==1485
    parents,struct=v30.extract_structural(allrows);assert len(parents)==1483 and struct['pre_count_structural_gate_pass']
    rows=[];strict_structure=0
    for key,children in sorted(parents.items()):
        strict=len({x['year_2000'] for x,_ in children})==1 and len({x['year_recent'] for x,_ in children})==1
        strict_structure+=strict
        old=[v30.exact_count(x.get('L')) for _,x in children];new=[v30.exact_count(x.get('O')) for _,x in children]
        if None in old or None in new or sum(old)<2 or sum(new)<2:continue
        a=np.asarray(old,dtype=np.int64);b=np.asarray(new,dtype=np.int64)
        assert len(a)>=3 and len(a)==len(b) and np.all(a>=0) and np.all(b>=0)
        rows.append((key,group(int(a.sum()),int(b.sum())),a,b,strict,local(a,b)))
    assert strict_structure==762 and len(rows)==1321 and sum(x[4] for x in rows)==663
    assert sum(x[2].sum()>x[3].sum() for x in rows)==959
    assert sum(x[4] and x[2].sum()>x[3].sum() for x in rows)==479
    return rows,{'original_SHA256':v29.ORIGINAL_SHA,'structural_parent_panels':len(parents),'strict_structural':strict_structure,'full_panels':len(rows),'strict_panels':sum(x[4] for x in rows),'species':len({x[0][0] for x in rows})}
def analyze(rows,species,seed,expected,network_count):
    networks=sorted({tuple(x[0][1:3]) for x in rows});assert len(networks)==network_count
    gcounts={g:sum(x[1]==g for x in rows) for g in GROUPS};assert list(gcounts.values())==expected
    by=defaultdict(list)
    for row in rows:by[row[0][0],row[1]].append(row)
    assert all(len(by[s,g])>=3 for s in species for g in GROUPS)
    def summ(rs):
        n=len(rs);z=[x[5] for x in rs];con=[x for x in z if x['deltaU']>0]
        return {'n':n,'any_local_gain':sum(x['any_gain'] for x in z),'any_local_loss':sum(x['any_loss'] for x in z),'mixed':sum(x['mixed'] for x in z),'material_counterflow':sum(x['material'] for x in z),'median_C':float(np.median([x['C'] for x in z])),'mean_C':float(np.mean([x['C'] for x in z])),'any_positive_to_zero':sum(x['positive_to_zero']>0 for x in z),'any_zero_to_positive':sum(x['zero_to_positive']>0 for x in z),'mean_fraction_baseline_occupied_later_zero':float(np.mean([x['lost_site_fraction'] for x in z])),'positive_deltaU':len(con),'positive_deltaU_mixed':sum(x['mixed'] for x in con),'positive_deltaU_nonmixed':sum(not x['mixed'] for x in con)}
    descriptive={g:summ([x for x in rows if x[1]==g]) for g in GROUPS}
    ni={x:i for i,x in enumerate(networks)};si={s:i for i,s in enumerate(species)};gi={g:i for i,g in enumerate(GROUPS)}
    cnt=np.zeros((len(networks),len(species),3));obs=np.zeros((*cnt.shape,2));null=np.zeros((2,len(species),3,R,2))
    rng=np.random.default_rng(seed)
    for key,g,a,b,strict,z in rows:
        if key[0] not in si:continue
        i,s,l=ni[tuple(key[1:3])],si[key[0]],gi[g];cnt[i,s,l]+=1;obs[i,s,l]+=measures(a,b)[0]
        p=(a+b)/(a.sum()+b.sum())
        for sc in range(2):
            if sc==0:
                x=rng.multinomial(int(a.sum()),p,size=R);y=rng.multinomial(int(b.sum()),p,size=R)
            else:
                px=rng.gamma(25,1/25,size=(R,len(p)))*p;py=rng.gamma(25,1/25,size=(R,len(p)))*p;px/=px.sum(axis=1,keepdims=True);py/=py.sum(axis=1,keepdims=True)
                x=np.array([rng.multinomial(int(a.sum()),q) for q in px]);y=np.array([rng.multinomial(int(b.sum()),q) for q in py])
            null[sc,s,l]+=measures(x,y)[0]
    n=cnt.sum(axis=0);observed=(obs.sum(axis=0)/n[...,None]).mean(axis=0)
    sim=(null/n[None,:,:,None,None]).mean(axis=1)
    w=rng.multinomial(len(networks),np.full(len(networks),1/len(networks)),size=B)
    nc=np.einsum('bn,nsg->bsg',w,cnt);ob=np.einsum('bn,nsgm->bsgm',w,obs);ok=(nc>0).all(axis=(1,2));boot=(ob[ok]/nc[ok,...,None]).mean(axis=1)
    ci=lambda v:np.quantile(v,[.025,.975]).tolist() if len(v)>=.95*B else None
    model={}
    for i,g in enumerate(GROUPS):
        model[g]={}
        for k,m in enumerate(METRICS):
            v=float(observed[i,k]);z={'observed':v,'network_bootstrap95':ci(boot[:,i,k])}
            for sc,label in enumerate(('multinomial','gammaCV20')):
                q=sim[sc,i,:,k];z[label]={'mean':float(q.mean()),'q05_q95':np.quantile(q,[.05,.95]).tolist(),'tail_upper':float((1+(q>=v).sum())/(R+1)),'above_q95':bool(v>np.quantile(q,.95))}
            model[g][m]=z
    return {'n':len(rows),'networks':len(networks),'fixed_common_species':species,'descriptive':descriptive,'common_species_equal_model':model,'bootstrap_valid_draws':int(ok.sum()),'bootstrap_attempts':B,'positive_all_models_and_metrics':{g:all(model[g][m][z]['above_q95'] for m in METRICS for z in ('multinomial','gammaCV20')) for g in GROUPS},'common_species_panel_counts':{s:{g:len(by[s,g]) for g in GROUPS} for s in species}}
def selftest():
    a=np.array([40,30,20,10]);b=np.array([35,55,20,10]);m,g,l=measures(a,b)
    assert g==25 and l==5 and np.isclose(m[0],10/220) and not m[1]
    m,g,l=measures(a,np.array([35,55,20,0]));assert g==25 and l==15 and m[1]
    assert measures(a,a)[0][0]==0
    assert measures(np.array([10,0,0]),np.array([0,10,0]))[0][0]==1
    assert local(np.array([4,2,0]),np.array([0,2,5]))['positive_to_zero']==1
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();selftest()
    root=Path(__file__).parent;full=json.loads((root/'JNCC_ALL_DIRECTION_RESULT_20261125.json').read_text());strict=json.loads((root/'JNCC_EXACT_YEAR_RESULT_20261125.json').read_text())
    rows,qa=source(a.source);assert len(full['common_species'])==10 and len(strict['common_species'])==7
    out={'status':'EXECUTED_GROSS_GAIN_LOSS','source_QA':qa,'full':analyze(rows,full['common_species'],20261125,[912,99,310],604),'exact_year':analyze([x for x in rows if x[4]],strict['common_species'],20261126,[457,47,159],389),'interpretation':'Observed opposing changes in adjusted monitored counts; fixed-composition conditional simulations are not measured survey error. No individual movement, colonization, extirpation, or cause inferred; strict cohort nested in full.'}
    a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
