"""Run pinned source V37 input; compare decline, near-stability, growth without selecting on outcomes."""
from pathlib import Path
import argparse, sys, json
from collections import defaultdict
import numpy as np
def values(a,b):
    a=np.asarray(a,dtype=float); b=np.asarray(b,dtype=float)
    N0=a.sum(axis=-1); N1=b.sum(axis=-1)
    p=a/N0[...,None]; q=b/N1[...,None]
    U0=(a*(a-1)).sum(axis=-1)/(N0*(N0-1))
    U1=(b*(b-1)).sum(axis=-1)/(N1*(N1-1))
    h0=(p*p).sum(axis=-1); h1=(q*q).sum(axis=-1)
    return np.stack([.5*np.abs(p-q).sum(axis=-1),U0+U1-2*(p*q).sum(axis=-1),U1-U0,1/h0,1/h1],axis=-1)
def group(n0,n1):
    r=n1/n0
    return 'decline' if r<1/1.1 else 'increase' if r>1.1 else 'near_stable'
def run(records, qa):
    assert len(records)==1321 and len({x[0][0] for x in records})==17
    groups=['decline','near_stable','increase']; species=sorted({x[0][0] for x in records}); networks=sorted({tuple(x[0][1:3]) for x in records})
    assert len(networks)==604
    by=defaultdict(list); rows=[]; rng=np.random.default_rng(20261125)
    for key,old,new in records:
        sp,country,master,unit=key
        n0=sum(old);n1=sum(new)
        assert n0>=2 and n1>=2 and len(old)>=3 and len(old)==len(new)
        a=np.asarray(old,dtype=np.int64);b=np.asarray(new,dtype=np.int64)
        s=group(n0,n1); v=values(a,b)
        unique=(np.sum(a==a.max())==1 and np.sum(b==b.max())==1)
        leader=bool(a.argmax()!=b.argmax()) if unique else None
        row=(sp,tuple(key[1:3]),s,v,leader,a,b)
        rows.append(row);by[sp,s].append(row)
    assert sum(sum(x[5])>sum(x[6]) for x in rows)==959
    def summary(rr):
        arr=np.array([x[3] for x in rr])
        leaders=[x[4] for x in rr if x[4] is not None]
        return dict(n=len(rr),medianTV=float(np.median(arr[:,0])),meanD2=float(arr[:,1].mean()),medianD2=float(np.median(arr[:,1])),medianDeltaU=float(np.median(arr[:,2])),meanDeltaU=float(arr[:,2].mean()),positiveD2=int((arr[:,1]>0).sum()),uniqueLeaders=len(leaders),leaderSwitch=int(sum(leaders)))
    summaries={g:summary([x for x in rows if x[2]==g]) for g in groups}
    species_eligible={g:[sp for sp in species if len(by[sp,g])>=3] for g in groups}
    common=[sp for sp in species if all(len(by[sp,g])>=3 for g in groups)]
    result=dict(source_QA=qa,networks=len(networks),group_summary=summaries,species_eligible=species_eligible,common_species=common,group_equal_species={g:dict(zip(['TV','D2','deltaU','Neff0','Neff1'],np.mean([np.mean([x[3] for x in by[sp,g]],axis=0) for sp in species_eligible[g]],axis=0).tolist())) for g in groups})
    if len(common)<6 or min(x['n'] for x in summaries.values())<30:
        result['status']='DESCRIPTIVE_ONLY_COMMON_SUPPORT';return result
    ns=len(networks);nc=len(common);ng=3;B=1999;R=999
    ni={n:i for i,n in enumerate(networks)};si={s:i for i,s in enumerate(common)};gi={g:i for i,g in enumerate(groups)}
    cnt=np.zeros((ns,nc,ng)); obs=np.zeros((ns,nc,ng,3))
    null=np.zeros((2,nc,ng,R,3));null_count=np.zeros((nc,ng))
    for sp,n,g,v,lead,a,b in rows:
        if sp not in si:continue
        j,k,l=ni[n],si[sp],gi[g]
        cnt[j,k,l]+=1;obs[j,k,l]+=v[:3]
        null_count[k,l]+=1
        p=(a+b)/(a.sum()+b.sum())
        for scenario in range(2):
            if scenario==0:
                x=rng.multinomial(int(a.sum()),p,size=R);y=rng.multinomial(int(b.sum()),p,size=R)
            else:
                xw=rng.gamma(25,1/25,size=(R,len(p)))*p; yw=rng.gamma(25,1/25,size=(R,len(p)))*p
                xw/=xw.sum(axis=1,keepdims=True);yw/=yw.sum(axis=1,keepdims=True)
                x=np.array([rng.multinomial(int(a.sum()),z) for z in xw]);y=np.array([rng.multinomial(int(b.sum()),z) for z in yw])
            null[scenario,k,l]+=values(x,y)[:,:3]
    mean_obs=(obs.sum(axis=0)/cnt.sum(axis=0)[...,None]).mean(axis=0)
    # Network-block bootstrap: same resampled networks for all species and groups.
    weights=rng.multinomial(ns,np.full(ns,1/ns),size=B)
    c=np.einsum('bn,nsg->bsg',weights,cnt)
    v=np.einsum('bn,nsgm->bsgm',weights,obs)
    ok=(c>0).all(axis=(1,2)); bs=(v[ok]/c[ok,...,None]).mean(axis=1)
    def interval(x):
        return np.quantile(x,[.025,.975]).tolist() if len(x)>=.95*B else None
    result['status']='EXECUTED_JNCC_ALL_DIRECTION'; result['bootstrap_valid_draws']=int(ok.sum())
    result['common_species_equal']={g:{'meanTV':float(mean_obs[i,0]),'meanD2':float(mean_obs[i,1]),'meanDeltaU':float(mean_obs[i,2]),'D2_network_bootstrap95':interval(bs[:,i,1]),'deltaU_network_bootstrap95':interval(bs[:,i,2])} for i,g in enumerate(groups)}
    result['decline_minus_growth']={'deltaU':float(mean_obs[0,2]-mean_obs[2,2]),'network_bootstrap95':interval(bs[:,0,2]-bs[:,2,2])}
    result['decline_minus_stable']={'deltaU':float(mean_obs[0,2]-mean_obs[1,2]),'network_bootstrap95':interval(bs[:,0,2]-bs[:,1,2])}
    null_mean=(null/null_count[None,:,:,None,None]).mean(axis=1)
    result['model_sensitivity']={lab:{g:{m:{'mean':float(null_mean[s,i,:,j].mean()),'q05_q95':np.quantile(null_mean[s,i,:,j],[.05,.95]).tolist(),'observed':float(mean_obs[i,j])} for j,m in enumerate(['TV','D2','deltaU'])} for i,g in enumerate(groups)} for s,lab in enumerate(['two_epoch_multinomial','gamma_CV20_then_multinomial'])}
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    sys.path.insert(0,str(a.source/'scripts'))
    import model_jncc_size_share_retention_v37 as original
    assert np.isclose(values([40,30,20,10],[10,20,30,40])[0],.4)
    assert np.isclose(values([40,30,20,10],[10,20,30,40])[2],0)
    assert values([40,30,20,10],[20,15,10,5])[1]<0
    records,qa=original.source_intake()
    result=run(records,qa); a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
