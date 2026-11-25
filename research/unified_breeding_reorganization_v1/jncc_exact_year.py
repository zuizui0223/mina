"""Exact two-epoch synchronous census sensitivity, original V39 source."""
import argparse, json, sys
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from jncc_all_direction import values, group
GROUPS=('decline','near_stable','increase')
def main():
    a=argparse.ArgumentParser();a.add_argument('--source',required=True,type=Path);a.add_argument('--out',required=True,type=Path);args=a.parse_args()
    sys.path.insert(0,str(args.source/'scripts'))
    import audit_jncc_uniform_census_year_v39 as v39
    import model_jncc_component_concentration_v30 as v30
    prior=json.loads((Path(__file__).parent/'JNCC_ALL_DIRECTION_RESULT_20261125.json').read_text())
    prior_common=prior['common_species']; assert len(prior_common)==10
    parents,qa=v39.source_only_year_gate();assert parents is not None and len(parents)==762
    rows=[];counts=defaultdict(int)
    for k,children in sorted(parents.items()):
        old=[v30.exact_count(x.get('L')) for _,x in children];new=[v30.exact_count(x.get('O')) for _,x in children]
        if None in old or None in new or sum(old)<2 or sum(new)<2:continue
        y0={r['year_2000'] for r,_ in children};y1={r['year_recent'] for r,_ in children};assert len(y0)==len(y1)==1
        h=int(next(iter(y1)))-int(next(iter(y0)));assert h>0
        x=np.asarray(old);y=np.asarray(new);g=group(x.sum(),y.sum())
        lead=None if sum(x==x.max())!=1 or sum(y==y.max())!=1 else bool(x.argmax()!=y.argmax())
        rows.append((k,g,x,y,values(x,y),lead,h));counts[k[0],g]+=1
    assert len(rows)==663 and sum(x[2].sum()>x[3].sum() for x in rows)==479
    def summ(rs):
        arr=np.array([x[4] for x in rs]);lead=[x[5] for x in rs if x[5] is not None]
        return {'n':len(rs),'medianTV':float(np.median(arr[:,0])),'medianD2':float(np.median(arr[:,1])),'medianDeltaU':float(np.median(arr[:,2])),'meanDeltaU':float(arr[:,2].mean()),'positiveD2':int((arr[:,1]>0).sum()),'leader_switch':sum(lead),'leader_eligible':len(lead),'duration_min_median_max':[int(min(x[6] for x in rs)),float(np.median([x[6] for x in rs])),int(max(x[6] for x in rs))]}
    summary={g:summ([x for x in rows if x[1]==g]) for g in GROUPS}
    sp=[s for s in prior_common if all(counts[s,g]>=3 for g in GROUPS)]
    result={'status':'DESCRIPTIVE_ONLY_COMMON_SUPPORT','source_qa':qa,'group_summary':summary,'prior_common_species_support':{s:{g:counts[s,g] for g in GROUPS} for s in prior_common},'common_species':sp,'networks':len({tuple(x[0][1:3]) for x in rows})}
    if len(sp)>=6 and min(v['n'] for v in summary.values())>=30:
        networks=sorted({tuple(x[0][1:3]) for x in rows});ni={n:i for i,n in enumerate(networks)};si={s:i for i,s in enumerate(sp)};gi={g:i for i,g in enumerate(GROUPS)}
        rng=np.random.default_rng(20261125);R=999;B=1999
        cnt=np.zeros((len(networks),len(sp),3));obs=np.zeros((*cnt.shape,3));null=np.zeros((2,len(sp),3,R,3))
        for k,g,x,y,v,_,_ in rows:
            if k[0] not in si:continue
            j,s,l=ni[tuple(k[1:3])],si[k[0]],gi[g];cnt[j,s,l]+=1;obs[j,s,l]+=v[:3]
            p=(x+y)/(x.sum()+y.sum())
            for sc in range(2):
                if sc==0:
                    xx=rng.multinomial(int(x.sum()),p,size=R);yy=rng.multinomial(int(y.sum()),p,size=R)
                else:
                    px=rng.gamma(25,1/25,size=(R,len(p)))*p;py=rng.gamma(25,1/25,size=(R,len(p)))*p;px/=px.sum(axis=1,keepdims=True);py/=py.sum(axis=1,keepdims=True)
                    xx=np.array([rng.multinomial(int(x.sum()),z) for z in px]);yy=np.array([rng.multinomial(int(y.sum()),z) for z in py])
                null[sc,s,l]+=values(xx,yy)[:,:3]
        n=cnt.sum(axis=0);mu=(obs.sum(axis=0)/n[...,None]).mean(axis=0)
        sim=(null/n[None,:,:,None,None]).mean(axis=1)
        w=rng.multinomial(len(networks),np.full(len(networks),1/len(networks)),size=B)
        bn=np.einsum('bn,nsg->bsg',w,cnt);bv=np.einsum('bn,nsgm->bsgm',w,obs)
        ok=(bn>0).all(axis=(1,2));boot=(bv[ok]/bn[ok,...,None]).mean(axis=1)
        ci=lambda x:np.quantile(x,[.025,.975]).tolist() if len(x)>=.95*B else None
        result.update(status='EXECUTED_EXACT_YEAR_COMMON_SPECIES',bootstrap_valid_draws=int(ok.sum()),common_species_equal={g:{m:{'observed':float(mu[i,j]),'bootstrap95':ci(boot[:,i,j]),'multinomial_q05_q95':np.quantile(sim[0,i,:,j],[.05,.95]).tolist(),'gammaCV20_q05_q95':np.quantile(sim[1,i,:,j],[.05,.95]).tolist()} for j,m in enumerate(('TV','D2','deltaU'))} for i,g in enumerate(GROUPS)},decline_minus_growth_deltaU={'observed':float(mu[0,2]-mu[2,2]),'bootstrap95':ci(boot[:,0,2]-boot[:,2,2])})
    result['limitations']='Same JNCC source as full analysis; exact within-panel census year does not guarantee comparable survey boundaries/effort. Unequal elapsed intervals; not independent temporal test.'
    args.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
