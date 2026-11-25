"""V4 measurement audit: publisher warning exclusion + frozen model replay."""
import argparse, hashlib, json, sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from jncc_gross_gain_loss import source, analyze
from jncc_all_direction import values
GROUPS=('decline','near_stable','increase')
OMIT={'Herring Gull','Lesser Black-backed Gull','Manx Shearwater','European Storm-petrel'}
def composition(rows,species,seed):
    # Same equal species weights and two fixed conditional references as V1/V2.
    R=999;B=1999;rng=np.random.default_rng(seed)
    nets=sorted({tuple(x[0][1:3]) for x in rows});ni={k:i for i,k in enumerate(nets)}
    si={k:i for i,k in enumerate(species)};gi={k:i for i,k in enumerate(GROUPS)}
    cnt=np.zeros((len(nets),len(species),3));obs=np.zeros((*cnt.shape,2));null=np.zeros((2,len(species),3,R,2))
    for key,g,a,b,strict,z in rows:
        if key[0] not in si:continue
        i,s,j=ni[tuple(key[1:3])],si[key[0]],gi[g]
        cnt[i,s,j]+=1;obs[i,s,j]+=values(a,b)[1:3]
        p=(a+b)/(a.sum()+b.sum())
        for sc in range(2):
            if sc==0:
                x=rng.multinomial(int(a.sum()),p,size=R);y=rng.multinomial(int(b.sum()),p,size=R)
            else:
                px=rng.gamma(25,1/25,size=(R,len(p)))*p;py=rng.gamma(25,1/25,size=(R,len(p)))*p
                px/=px.sum(axis=1,keepdims=True);py/=py.sum(axis=1,keepdims=True)
                x=np.array([rng.multinomial(int(a.sum()),q) for q in px]);y=np.array([rng.multinomial(int(b.sum()),q) for q in py])
            null[sc,s,j]+=values(x,y)[:,1:3]
    n=cnt.sum(axis=0);assert np.all(n>=3)
    observed=(obs.sum(axis=0)/n[...,None]).mean(axis=0)
    sim=(null/n[None,:,:,None,None]).mean(axis=1)
    w=rng.multinomial(len(nets),np.full(len(nets),1/len(nets)),size=B)
    nc=np.einsum('bn,nsg->bsg',w,cnt);ob=np.einsum('bn,nsgm->bsgm',w,obs)
    ok=(nc>0).all(axis=(1,2));boot=(ob[ok]/nc[ok,...,None]).mean(axis=1)
    ci=lambda q:np.quantile(q,[.025,.975]).tolist() if len(q)>=.95*B else None
    out={}
    for i,g in enumerate(GROUPS):
        out[g]={}
        for k,name in enumerate(('D2','deltaU')):
            v=float(observed[i,k]);out[g][name]={'observed':v,'bootstrap95':ci(boot[:,i,k])}
            for sc,lab in enumerate(('multinomial','gammaCV20')):
                q=sim[sc,i,:,k];out[g][name][lab]={'mean':float(q.mean()),'q05_q95':np.quantile(q,[.05,.95]).tolist(),'above_q95':bool(v>np.quantile(q,.95))}
    return {'common_species_equal':out,'bootstrap_valid_draws':int(ok.sum()),'bootstrap_attempts':B}
def metadata(path):
    sys.path.insert(0,str(path/'scripts'))
    import audit_jncc_two_censuses_source_v28 as v28
    import audit_jncc_comparable_site_panels_v29 as v29
    import model_jncc_component_concentration_v30 as v30
    raw,src=v28.download_original();assert hashlib.sha256(raw).hexdigest()==v29.ORIGINAL_SHA
    # Use existing publisher XLSX structural parser, no raw count vectors exported.
    doc=v28.inspect_source(raw);records=list(v29.original_rows(raw))
    parents,_=v30.extract_structural(records)
    byid=defaultdict(set);unit=Counter();species=Counter();end_nonempty=Counter()
    for key,children in parents.items():
        for z,row in children:
            byid[(z['species'],z['country'],z['site_id'])].add(z['master'])
            unit[z['unit']]+=1;species[z['species']]+=1
            for c in ['G','H','Q','R']:
                if row.get(c):end_nonempty[c]+=1
    headers={sheet:{k:v for k,v in row.items() if v} for sheet,i,row in records if i==4}
    # Source header/notes only; don't export site labels or actual data rows.
    sheet_metadata=[]
    for s in doc['sheets']:
        d={'name':s['original_name'],'dimension':s['original_declared_dimension']}
        if 'cover' in d['name'].lower() or 'note' in d['name'].lower() or 'readme' in d['name'].lower():
            d['publisher_first_text_rows']=[{'row':z['original_row_number'],'texts':[x['source_text'][:500] for x in z['source_text_cells']]} for z in s['first_12_source_text_rows']]
        sheet_metadata.append(d)
    return {'original_sha256':src['original_sha256'],'worksheets':sheet_metadata,'paired_sheet_headers':headers,'structural_child_rows':sum(unit.values()),'count_unit_child_rows':dict(unit),'additional_column_nonempty':dict(end_nonempty),'species_country_site_ids_with_multiple_master_names':sum(len(z)>1 for z in byid.values()),'unique_species_country_site_ids':len(byid),'historical_boundary_effort_not_verified':True}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    md=metadata(a.source);rows,qa=source(a.source)
    root=Path(__file__).parent;full=json.loads((root/'JNCC_ALL_DIRECTION_RESULT_20261125.json').read_text());strict=json.loads((root/'JNCC_EXACT_YEAR_RESULT_20261125.json').read_text())
    result={'status':'EXECUTED_FIXED_WARNING_EXCLUSION','source_QA':qa,'metadata':md,'official_flagged_taxa':sorted(OMIT),'flagged_taxa_present':sorted({x[0][0] for x in rows}&OMIT),'cohorts':{}}
    for idx,(name,rs,prior) in enumerate([('full',rows,full),('exact_year',[x for x in rows if x[4]],strict)]):
        keep=[x for x in rs if x[0][0] not in OMIT];sp=[x for x in prior['common_species'] if x not in OMIT]
        groups=[sum(x[1]==g for x in keep) for g in GROUPS];nn=len({tuple(x[0][1:3]) for x in keep})
        z={'n_before':len(rs),'n_after':len(keep),'networks':nn,'remaining_species':len({x[0][0] for x in keep}),'removed_panels_by_species':dict(Counter(x[0][0] for x in rs if x[0][0] in OMIT)),'groups':dict(zip(GROUPS,groups)),'fixed_common_species':sp}
        if len(sp)>=6 and min(groups)>=30:
            z['gain_loss']=analyze(keep,sp,20261127+idx,groups,nn);z['composition']=composition(keep,sp,20261129+idx)
            z['primary_all_groups_above_gamma_q95']=all(z['gain_loss']['common_species_equal_model'][g]['counterflow']['gammaCV20']['above_q95'] and z['composition']['common_species_equal'][g]['deltaU']['gammaCV20']['above_q95'] for g in GROUPS)
        else:z['status']='STOP_INSUFFICIENT_FIXED_SUPPORT'
        result['cohorts'][name]=z
    result['limitations']='National comparability warning exclusion only. Not a validation of historical site polygons or calibrated survey effort, and not an independent dataset.'
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    # One compact JSON line ensures whole receipt recoverable from CI logs.
    print('AUDIT_RESULT_JSON='+json.dumps(result,separators=(',',':')))
if __name__=='__main__':main()
