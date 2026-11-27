"""V29b: common-calendar physical PCA and residual polynya geography."""
import csv,io,zipfile,hashlib,json,pathlib,sys,math,statistics
from collections import defaultdict,Counter
import numpy as np
ice,hydro,poly,out=map(pathlib.Path,sys.argv[1:5]);out.mkdir(parents=True,exist_ok=True)
def rz(p,h):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(p,'hash')
    z=zipfile.ZipFile(p);assert z.testzip() is None;return z
def member(z,n):
    p=[s for s in z.namelist() if pathlib.PurePosixPath(s).name==n];assert len(p)==1,(n,p)
    return z.read(p[0])
def rows(z,n):return list(csv.DictReader(io.StringIO(member(z,n).decode('utf-8-sig'))))
def ix(r,keys):
    q={tuple(x[k] for k in keys):x for x in r};assert len(q)==len(r);return q
def write(n,r):
    with (out/n).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
iz=rz(ice,'9007f1d426d9fe2914782f7044d46fda8ec2f44c7ba6cac6cb55079e4de52f73')
hz=rz(hydro,'b52f0f5f534690fc26b3dd95b8a9db14d840c462362040c3939ba6d06f8d013f')
pz=rz(poly,sys.argv[5])
receipt=json.loads(member(pz,'result.json'));assert receipt['status']=='EXECUTED_NATIVE_P100' and receipt['old_mismatch_count']==0
it=rows(iz,'marine_tiles_30yr.csv');ht=rows(hz,'hydro_tiles.csv')
im=rows(iz,'monthly_120.csv');hm=rows(hz,'hydro_monthly.csv')
pm=rows(pz,'monthly.csv');pw=rows(pz,'winter.csv')
assert tuple(map(len,(it,ht,im,hm,pm,pw)))==(1722,1722,1722*120,1722*104,2317*65,2317*13)
P=ix([x for x in pm if x['kind']=='tile'],['id','year','month'])
W=ix([x for x in pw if x['kind']=='tile'],['id','year'])
I=ix(im,['tile','year','month']);H=ix(hm,['tile','year','month']);HT={r['tile']:r for r in ht}
Y=tuple(range(2004,2011))+tuple(range(2013,2019));M=(6,7,8,9,10);groups=('known','modern','ADPE','CHPE','GEPE')
qa=0;maxerr=0.
def ck(a,b,tol=1e-10):
    global qa,maxerr
    e=abs(a-b);assert e<=tol,(a,b,e);qa+=1;maxerr=max(maxerr,e)
for r in it:
    h=HT[r['tile']]
    for k in ('block','rock_pixels','plant_rock_pixels','has_plant')+tuple('recorded_'+g for g in groups):assert r[k]==h[k],(r['tile'],k)
    for y in Y:
        vals=[P[r['tile'],str(y),str(m)] for m in M]
        for p in vals:
            ok=int(p['valid_days'])>=.8*int(p['calendar_days'])
            assert (p['p100_fraction']!='')==ok
            if ok:assert 0<=float(p['p100_fraction'])<=1+1e-12
            qa+=1
        old=W[r['tile'],str(y)]
        v=[float(p['p100_fraction']) for p in vals if p['p100_fraction']!='']
        assert int(old['n_valid_months'])==len(v)
        if len(v)==5:
            ck(statistics.mean(v),float(old['p100_winter_fraction']))
            ck(statistics.mean(v[2:]),float(old['p100_aug_oct_fraction']))
        else:assert old['p100_winter_fraction']==old['p100_aug_oct_fraction']==''
cols=('sic','sss','sst','p100')
def mean_month(t,y,m,k):
    if k=='sic':v=I[t,str(y),str(m)]['sic_pp']
    elif k=='sss':v=H[t,str(y),str(m)]['sss']
    elif k=='sst':v=H[t,str(y),str(m)]['sst_C']
    else:v=P[t,str(y),str(m)]['p100_fraction']
    if not v:return None
    a=float(v);assert math.isfinite(a)
    return 100*a if k=='p100' else a
def cohort(mode):
    result=[];missing=Counter()
    for r in it:
        t=r['tile'];v={k:[] for k in cols}
        # Require full 5-month winter even for shared Aug-Oct comparison.
        if any(W[t,str(y)]['p100_winter_fraction']=='' for y in Y):
            missing['incomplete_p100_winter']+=1;continue
        for k in cols:
            months=(8,9,10) if mode=='shared_aug_oct' else ((6,7,8,9,10) if k=='p100' else (8,9,10,11))
            for y in Y:
                a=[mean_month(t,y,m,k) for m in months]
                v[k].append(statistics.mean(a) if all(x is not None for x in a) else None)
        if any(None in v[k] for k in cols):
            missing['incomplete_marine_common']+=1;continue
        q={'tile':t,'block':r['block'],'rock_pixels':int(r['rock_pixels']),'has_plant':int(r['has_plant']),**{f'recorded_{g}':int(r['recorded_'+g]) for g in groups}}
        for k in cols:
            a=v[k]
            e=statistics.mean([x for y,x in zip(Y,a) if 2005<=y<=2010]);l=statistics.mean([x for y,x in zip(Y,a) if 2013<=y<=2018])
            q.update({k:statistics.mean(a),k+'_early':e,k+'_late':l,k+'_delta':l-e})
        result.append(q)
    assert len(result)+sum(missing.values())==1722
    return result,dict(missing)
def wm(rr,k):
    return math.fsum(r['rock_pixels']*r[k] for r in rr)/sum(r['rock_pixels'] for r in rr)
def compare(rr,k,obs):
    blocks=defaultdict(list)
    for r in rr:blocks[r['block']].append(r)
    if not obs:return None
    a=statistics.mean(r[k] for r in obs)
    ds=[r[k]-wm(blocks[r['block']],k) for r in obs]
    b=defaultdict(list)
    for r,d in zip(obs,ds):b[r['block']].append(d)
    bm=[statistics.mean(v) for v in b.values()]
    l=[statistics.mean(d for r,d in zip(obs,ds) if r['block']!=key) for key in b] if len(b)>1 else []
    return {'observed':a,'expected':a-statistics.mean(ds),'difference':statistics.mean(ds),'equal_block_difference':statistics.mean(bm),'positive_blocks':sum(x>1e-12 for x in bm),'negative_blocks':sum(x< -1e-12 for x in bm),'lobo_min':min(l) if l else None,'lobo_max':max(l) if l else None}
def analyze(rr,mode,missing):
    assert len(rr)>=100 and len({r['block'] for r in rr})>=8
    z=np.array([[r[k] for k in cols] for r in rr],float)
    w=np.array([r['rock_pixels'] for r in rr],float);w/=w.sum()
    mu=w@z;sd=np.sqrt(w@((z-mu)**2));assert np.all(sd>0)
    x=(z-mu)/sd;R=(x*w[:,None]).T@x
    assert np.allclose(np.diag(R),1,atol=1e-10)
    pcas={}
    for n in (3,4):
        eig,V=np.linalg.eigh(R[:n,:n]);order=np.argsort(eig)[::-1];eig=eig[order];V=V[:,order]
        for j in range(n):
            i=int(np.argmax(abs(V[:,j])))
            if V[i,j]<0:V[:,j]*=-1
        sc=x[:,:n]@V
        assert np.allclose((sc*w[:,None]).T@sc,np.diag(eig),atol=1e-10)
        pcas[str(n)]={'columns':cols[:n],'explained':(eig/eig.sum()).tolist(),'eigenvalues':eig.tolist(),'eigenvectors':V.tolist()}
        if n==4:
            for r,s in zip(rr,sc):r.update({f'PC{i+1}':float(v) for i,v in enumerate(s)})
    def regress(a,b,ww):
        mat=a*np.sqrt(ww[:,None]);target=b*np.sqrt(ww)
        beta,_,rank,_=np.linalg.lstsq(mat,target,rcond=None)
        assert rank==a.shape[1]
        res=b-a@beta;ss=float(ww@(b*b));sse=float(ww@(res*res))
        assert ss>0 and sse>=0
        return beta,res,{'R2':1-sse/ss,'variance_total':ss,'residual_variance':sse,'beta':beta.tolist(),'rank':int(rank)}
    beta,res,globalfit=regress(x[:,:3],x[:,3],w)
    # Centering within blocks prevents large-scale geographical differences from carrying the entire fit.
    blocks=defaultdict(list)
    for j,r in enumerate(rr):blocks[r['block']].append(j)
    centered=x.copy()
    for a in blocks.values():
        ww=w[a]/w[a].sum();centered[a]-=ww@x[a]
    _,within,withinfit=regress(centered[:,:3],centered[:,3],w)
    for i,r in enumerate(rr):
        r['p100_residual_global_z']=float(res[i]);r['p100_residual_within_block_z']=float(within[i])
    # Check normal equations and variance calculation independently.
    assert np.max(np.abs((x[:,:3]*w[:,None]).T@res))<1e-10
    assert np.max(np.abs((centered[:,:3]*w[:,None]).T@within))<1e-10
    ck(float(w@res**2),globalfit['residual_variance']);ck(float(w@within**2),withinfit['residual_variance'])
    metrics=['sic','sss','sst','p100','p100_residual_global_z','p100_residual_within_block_z','has_plant','p100_delta','sic_delta']
    stats={}
    for g in groups:
        obs=[r for r in rr if r['recorded_'+g]]
        stats[g]={'tiles':len(obs),'blocks':len({r['block'] for r in obs}),'metrics':{k:compare(rr,k,obs) for k in metrics}}
    signs=defaultdict(lambda:{'tiles':0,'rock_pixels':0})
    for r in rr:
        key=''.join('+' if r[k]>0 else '-' if r[k]<0 else '0' for k in ('sic_delta','p100_delta'))
        signs[key]['tiles']+=1;signs[key]['rock_pixels']+=r['rock_pixels']
    write(mode+'_tiles.csv',rr)
    return {'mode':mode,'tiles':len(rr),'blocks':len(blocks),'rock_pixels':sum(r['rock_pixels'] for r in rr),'missing':missing,'columns':cols,'means':mu.tolist(),'sd':sd.tolist(),'correlation':R.tolist(),'PCA':pcas,'global_p100_regression':globalfit,'within_block_p100_regression':withinfit,'groups':stats,'physical':{k:wm(rr,k) for k in list(cols)+[v+'_'+s for v in cols for s in ('early','late','delta')]},'SIC_P100_change_signs':dict(signs)}
results=[]
for mode in ('shared_aug_oct','winter_vs_aug_nov'):
    rr,miss=cohort(mode);results.append(analyze(rr,mode,miss))
res={'status':'EXECUTED_COMMON_POLYNYA_PHYSICAL_GEOGRAPHY','years':Y,'source_extraction':receipt,'analyses':results,'independent_aggregation_QA':{'checks':qa,'max_abs_discrepancy':maxerr},'limits':'Derived native satellite polynya product and different SIC/GLORYS spatial estimators; linear residual not independent driver. Fixed mapped-rock opportunity and modern observed-record labels, no true absences, no causal mechanism or forecasts.'}
(out/'result.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
print('V29B_RESULT='+json.dumps(res),flush=True)
