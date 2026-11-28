"""V33 fixed multivariate climate analogue factorial accounting; no causal attribution."""
import csv,io,json,hashlib,pathlib,sys,zipfile,math,itertools
from collections import defaultdict
import numpy as np
from scipy.spatial.distance import cdist
future,analogue,frame,out=map(pathlib.Path,sys.argv[1:5]);out.mkdir(parents=True,exist_ok=True)
models=('ACCESS-CM2','BCC-CSM2-MR','CESM2')
species=('ADPE','CHPE','GEPE')
variables=('siconc','sos','tos')
scenarios=[(s,p) for s in ('ssp245','ssp585') for p in ('2041-2060','2081-2100')]
def rz(p,h):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(p,'hash')
    z=zipfile.ZipFile(p);assert z.testzip() is None;return z
def member(z,n):
    a=[s for s in z.namelist() if pathlib.PurePosixPath(s).name==n];assert len(a)==1,(n,a)
    return z.read(a[0])
def rows(z,n):return list(csv.DictReader(io.StringIO(member(z,n).decode('utf-8-sig'))))
def ix(r,k):
    d={tuple(x[v] for v in k):x for x in r};assert len(d)==len(r);return d
def write(n,rs):
    assert rs
    with (out/n).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rs for k in r)));w.writeheader();w.writerows(rs)
fz=rz(future,'bac958ee1c96168e730a1f5c23c13614da6d3da322d04ee29ee504d857466e94')
az=rz(analogue,'2b3066535396dd9c5b8d813a7a7870873ee0a885cab1ae5ffdbed02617105dd7')
gz=rz(frame,'13bfe5866a27f6fbfad681ed4a44d834f6019c663f94193e1039e96b81c22060')
old=json.loads(member(az,'result.json'));assert old['status']=='EXECUTED_CONDITIONAL_CLIMATE_ANALOGUES'
ff={r['tile']:r for r in rows(gz,'opportunity_tiles.csv') if r['band_km']=='5'}
R=ix(rows(fz,'primary_tile_scenarios.csv'),('tile','model','experiment','period'))
keys=sorted({k[0] for k in R},key=int);n=len(keys);assert n==1401 and len(R)==n*12
saved=ix(rows(az,'primary_tile_analogues.csv'),('species','tile','experiment','period'))
assert len(saved)==n*3*4
X=np.array([[float(R[k,models[0],*scenarios[0]][v+'_observed']) for v in variables] for k in keys])
area=np.array([float(R[k,models[0],*scenarios[0]]['rock_area_m2']) for k in keys]);w=np.array([int(ff[k]['rock_pixels']) for k in keys],float)
assert np.all(area>0) and np.isfinite(X).all()
lab={s:np.array([int(ff[k]['recorded_'+s]) for k in keys],bool) for s in species}
assert {s:int(v.sum()) for s,v in lab.items()}=={'ADPE':31,'CHPE':62,'GEPE':37}
wn=w/w.sum();mu=wn@X;sd=np.sqrt(wn@((X-mu)**2));Z=(X-mu)/sd
corr=(Z*wn[:,None]).T@Z;ev,V=np.linalg.eigh(corr);assert min(ev)>1e-6
white=V@np.diag(1/np.sqrt(ev))@V.T
checks=0;maxerr=0.
def ck(a,b):
    global checks,maxerr
    err=abs(a-b);assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-9),(a,b)
    checks+=1;maxerr=max(maxerr,err)
for a,b in zip(mu,old['standardization']['mean']):ck(float(a),b)
for a,b in zip(sd,old['standardization']['sd']):ck(float(a),b)
for a,b in zip(corr.ravel(),np.array(old['standardization']['correlation']).ravel()):ck(float(a),float(b))
D={};clipped={}
for m in models:
    for s,p in scenarios:
        delta=np.array([[float(R[k,m,s,p][v+'_native_delta']) for v in variables] for k in keys])
        D[m,s,p]=delta
        raw=X+delta;cl=(raw[:,0]<0)|(raw[:,0]>100);clipped[m,s,p]=cl
        raw[:,0]=np.clip(raw[:,0],0,100)
        for i,k in enumerate(keys):
            r=R[k,m,s,p]
            assert bool(int(r['SIC_clipped']))==cl[i]
            ck(float(r['rock_area_m2']),float(area[i]))
            for j,v in enumerate(variables):
                ck(float(r[v+'_observed']),float(X[i,j]))
                ck(float(r[v+'_conditional']),float(raw[i,j]))
def trans(x,metric):
    z=(x-mu)/sd
    return z if metric=='euclidean3' else z@white
def subset_name(k):
    return '+'.join(v for j,v in enumerate(('SIC','SSS','SST')) if k&(1<<j)) or 'none'
def weighted(flag,weight,mask):
    return float(weight[mask]@flag[mask].astype(float)/weight[mask].sum())
perms=list(itertools.permutations(range(3)))
factorial=[];contrib=[];tiles=[];agreement=[]
oldsets=[q for q in old['analogue_scenarios'] if q['metric'] in ('euclidean3','whitened')]
assert len(oldsets)==18
for q in oldsets:
    metric=q['metric'];sp=q['species'];quant=q['quantile'];th=q['threshold']
    ref=trans(X[lab[sp]],metric)
    def classify(a):return cdist(trans(a,metric),ref).min(axis=1)<=th+1e-12
    baseline=classify(X)
    ck(weighted(baseline,area,np.ones(n,bool)),q['baseline']['rock_area_fraction'])
    assert int(baseline.sum())==q['baseline']['tiles']
    for s,p in scenarios:
        panel=next(v for v in q['scenarios'] if (v['experiment'],v['period'])==(s,p))
        no_clip=~np.logical_or.reduce([clipped[m,s,p] for m in models])
        modelphi={}
        modelflag={}
        for m in models:
            d=D[m,s,p]
            flag={}
            for k in range(8):
                a=X+d*np.array([bool(k&(1<<j)) for j in range(3)])
                a[:,0]=np.clip(a[:,0],0,100)
                flag[k]=classify(a)
            assert np.array_equal(flag[0],baseline)
            modelflag[m]=flag[7]
            if metric=='euclidean3' and quant==.9:
                for i,key in enumerate(keys):
                    a=saved[sp,key,s,p]
                    assert bool(int(a['baseline_analogue']))==flag[0][i] and bool(int(a[m]))==flag[7][i]
                    assert bool(int(a['common_unclipped']))==no_clip[i]
                    tiles.append({'species':sp,'tile':key,'model':m,'experiment':s,'period':p,'common_unclipped':int(no_clip[i]),**{'mask_'+str(k):int(flag[k][i]) for k in range(8)}})
            # Tile-level Shapley, averaging six permutations; exact efficiency.
            tilephi=np.zeros((3,n))
            for perm in perms:
                k=0
                for j in perm:
                    k1=k|(1<<j)
                    tilephi[j]+=(flag[k1].astype(float)-flag[k].astype(float))/6
                    k=k1
            assert np.allclose(tilephi.sum(axis=0),flag[7].astype(float)-flag[0].astype(float),atol=1e-12)
            modelphi[m]=tilephi
            for tag,mask in [('full',np.ones(n,bool)),('common_unclipped',no_clip)]:
                expected=panel[tag]
                assert int(mask.sum())==expected['denominator_tiles']
                ck(float(area[mask].sum()/1e6),expected['denominator_rock_area_km2'])
                for wt,weight in [('rock_area',area),('rock_hits',w)]:
                    f={k:weighted(v,weight,mask) for k,v in flag.items()}
                    field='rock_area_fraction' if wt=='rock_area' else 'rock_hit_fraction'
                    ck(f[0],expected['baseline'][field]);ck(f[7],expected['models'][m]['future'][field])
                    base={'metric':metric,'species':sp,'quantile':quant,'threshold':th,'transfer_gate':q['transfer_gate'],'model':m,'experiment':s,'period':p,'support':tag,'weight':wt,'tiles':int(mask.sum()),'denominator_km2':float(area[mask].sum()/1e6)}
                    for k in range(8):
                        gain=weighted(flag[k]&~baseline,weight,mask);loss=weighted(~flag[k]&baseline,weight,mask)
                        ck(f[k]-f[0],gain-loss)
                        factorial.append({**base,'subset_mask':k,'subset':subset_name(k),'analogue_fraction':f[k],'change':f[k]-f[0],'gain':gain,'loss':loss})
                    phi=np.zeros(3)
                    for perm in perms:
                        k=0
                        for j in perm:
                            k1=k|(1<<j);phi[j]+=(f[k1]-f[k])/6;k=k1
                    closed=np.zeros(3)
                    for j in range(3):
                        for k in range(8):
                            if k&(1<<j):continue
                            b=k.bit_count()
                            closed[j]+=math.factorial(b)*math.factorial(2-b)/6*(f[k|(1<<j)]-f[k])
                        ck(float(phi[j]),float(closed[j]))
                        ck(float(phi[j]),weighted(tilephi[j],weight,mask))
                    ck(float(phi.sum()),f[7]-f[0])
                    mob={}
                    for k in range(8):
                        mob[k]=sum((-1)**(k.bit_count()-a.bit_count())*f[a] for a in range(8) if a&k==a)
                    for k in range(8):ck(sum(v for a,v in mob.items() if a&k==a),f[k])
                    for j in range(3):ck(float(phi[j]),sum(mob[k]/k.bit_count() for k in range(1,8) if k&(1<<j)))
                    contrib.append({**base,'baseline':f[0],'future':f[7],'change':f[7]-f[0],**{'phi_'+v:float(phi[j]) for j,v in enumerate(('SIC','SSS','SST'))},**{'mobius_'+str(k):mob[k] for k in range(1,8)},'sum_interactions':sum(mob[k] for k in (3,5,6,7))})
        for tag,mask in [('full',np.ones(n,bool)),('common_unclipped',no_clip)]:
            ph=np.stack([modelphi[m] for m in models]);fs=np.stack([modelflag[m] for m in models])
            row={'metric':metric,'species':sp,'quantile':quant,'experiment':s,'period':p,'support':tag,'tiles':int(mask.sum()),'all_model_loss_fraction':weighted(baseline&~fs.any(axis=0),area,mask),'all_model_gain_fraction':weighted(~baseline&fs.all(axis=0),area,mask)}
            for j,v in enumerate(('SIC','SSS','SST')):
                row['all_negative_'+v]=weighted((ph[:,j,:]<-1e-12).all(axis=0),area,mask)
                row['all_positive_'+v]=weighted((ph[:,j,:]>1e-12).all(axis=0),area,mask)
            agreement.append(row)
assert len(factorial)==18*4*3*2*2*8 and len(contrib)==18*4*3*2*2
write('factorial.csv',factorial);write('contributions.csv',contrib);write('primary_tile_factorial.csv',tiles);write('agreement.csv',agreement)
primary=[r for r in contrib if r['metric']=='euclidean3' and r['quantile']==.9 and r['weight']=='rock_area']
late=[r for r in contrib if r['experiment']=='ssp585' and r['period']=='2081-2100' and r['weight']=='rock_area']
res={'status':'EXECUTED_FIXED_REFERENCE_FACTORIAL','tiles':n,'factorial_rows':len(factorial),'contribution_rows':len(contrib),'QA':{'checks':checks,'max_abs_difference':maxerr},'primary':primary,'late_sensitivity':late,'limits':'Arithmetic hybrid fields, not dynamically consistent models or causal ecological effects; fixed recorded references and land, no P100/snow future or population prediction.'}
(out/'result.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
print('V33_RESULT='+json.dumps({'status':res['status'],'tiles':n,'factorial_rows':len(factorial),'contribution_rows':len(contrib),'QA':res['QA'],'primary_late':[r for r in primary if r['experiment']=='ssp585' and r['period']=='2081-2100'],'gentoo_primary_factorial':[r for r in factorial if r['metric']=='euclidean3' and r['species']=='GEPE' and r['quantile']==.9 and r['experiment']=='ssp585' and r['period']=='2081-2100' and r['weight']=='rock_area'],'gentoo_late_sensitivity':[r for r in late if r['species']=='GEPE']}),flush=True)
