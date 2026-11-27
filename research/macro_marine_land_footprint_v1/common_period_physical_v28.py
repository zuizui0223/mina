"""V28: exact same-period physical opportunity geography, not a habitat model."""
import csv,io,json,hashlib,pathlib,sys,zipfile,math,statistics
from collections import defaultdict
import numpy as np
ice,hydro,out=map(pathlib.Path,sys.argv[1:4]);out.mkdir(parents=True,exist_ok=True)
def readzip(p,h):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h
    z=zipfile.ZipFile(p);assert z.testzip() is None;return z
def member(z,name):
    paths=[x for x in z.namelist() if pathlib.PurePosixPath(x).name==name];assert len(paths)==1,(name,paths)
    return z.read(paths[0])
def rows(z,name):return list(csv.DictReader(io.StringIO(member(z,name).decode('utf-8-sig'))))
iz=readzip(ice,'9007f1d426d9fe2914782f7044d46fda8ec2f44c7ba6cac6cb55079e4de52f73')
hz=readzip(hydro,'b52f0f5f534690fc26b3dd95b8a9db14d840c462362040c3939ba6d06f8d013f')
it=rows(iz,'marine_tiles_30yr.csv');ht=rows(hz,'hydro_tiles.csv')
im=rows(iz,'monthly_120.csv');ia=rows(iz,'annual_30.csv')
hm=rows(hz,'hydro_monthly.csv')
assert tuple(map(len,(it,ht,im,ia,hm)))==(1722,1722,1722*120,1722*30,1722*104)
def ix(rs,keys):
    d={tuple(r[k] for k in keys):r for r in rs};assert len(d)==len(rs);return d
I=ix(im,['tile','year','month']);A=ix(ia,['tile','year']);H=ix(hm,['tile','year','month'])
HT={r['tile']:r for r in ht};assert len(HT)==1722 and set(HT)=={r['tile'] for r in it}
old=json.loads(member(iz,'result.json'))
checks=0;maxerr=0.
def ck(a,b):
    global checks,maxerr
    assert math.isclose(a,b,abs_tol=1e-9,rel_tol=1e-10),(a,b)
    checks+=1;maxerr=max(maxerr,abs(a-b))
def wm(rr,key):
    return math.fsum(int(r['rock_pixels'])*float(r[key]) for r in rr)/sum(int(r['rock_pixels']) for r in rr)
def bin20(v):return min(4,int(v//20))
ms=(8,9,10,11);ys=list(range(1993,2019));years=list(range(1991,2021))
groups=('known','modern','ADPE','CHPE','GEPE')
common=[];complete=[]
for r in it:
    t=r['tile'];h=HT[t]
    for key in ('block','rock_pixels','plant_rock_pixels','has_plant')+tuple('recorded_'+g for g in groups):
        assert r[key]==h[key],(t,key,r[key],h[key])
    series=[]
    for y in years:
        vv=[I[t,str(y),str(m)]['sic_pp'] for m in ms]
        v=A[t,str(y)]['sic_pp']
        if all(x!='' for x in vv):
            mean=math.fsum(map(float,vv))/4;ck(mean,float(v));series.append(mean)
        else:assert v=='';series.append(None)
    good=all(x is not None for x in series);assert good==bool(int(r['complete_120']))
    if good:
        complete.append(r)
        a=statistics.mean(series[:10]);b=statistics.mean(series[-10:])
        for k,v in [('sic30',statistics.mean(series)),('early_sic',a),('late_sic',b),('delta_sic',b-a),('annual_sd',statistics.stdev(series)),('trend_pp_decade',10*statistics.linear_regression(years,series).slope)]:
            ck(v,float(r[k]))
    v=[]
    for y in ys:
        for m in ms:
            a=I[t,str(y),str(m)]['sic_pp'];h1=H[t,str(y),str(m)]
            v.append([float(q) if q!='' else np.nan for q in (a,h1['sss'],h1['sst_C'])])
    v=np.asarray(v)
    if not np.isfinite(v).all():continue
    annual=v.reshape(26,4,3).mean(axis=1)
    e=annual[:8].mean(axis=0);l=annual[-8:].mean(axis=0);mu=annual.mean(axis=0)
    outrow={'tile':t,'block':r['block'],'rock_pixels':int(r['rock_pixels']),'has_plant':int(r['has_plant']),**{f'recorded_{g}':int(r['recorded_'+g]) for g in groups}}
    for j,k in enumerate(('sic','sss','sst')):
        outrow.update({k+'_mean':float(mu[j]),k+'_early':float(e[j]),k+'_late':float(l[j]),k+'_delta':float(l[j]-e[j])})
    common.append(outrow)
assert len(complete)==old['complete_tiles']==1719 and len(common)>0
trans=np.zeros((5,5),dtype=int)
for r in complete:trans[bin20(float(r['early_sic'])),bin20(float(r['late_sic']))]+=int(r['rock_pixels'])
assert trans.tolist()==old['transition_rock_pixels']
for k in ('sic30','early_sic','late_sic','delta_sic','trend_pp_decade','annual_sd'):ck(wm(complete,k),old['physical'][k])
blocks=defaultdict(list)
for r in complete:blocks[r['block']].append(r)
for g,d in old['groups'].items():
    v=[r for r in complete if int(r['recorded_'+g])];assert len(v)==d['complete_tiles']
    for k,z in d['metrics'].items():
        ck(statistics.mean(float(r[k]) for r in v),z['observed'])
        ck(statistics.mean(wm(blocks[r['block']],k) for r in v),z['expected'])
cols=('sic','sss','sst')
w=np.array([r['rock_pixels'] for r in common],float);w/=w.sum()
z=np.array([[r[k+'_mean'] for k in cols] for r in common])
mu=w@z;sd=np.sqrt(w@((z-mu)**2));assert (sd>0).all()
std=(z-mu)/sd;R=(std*w[:,None]).T@std
eig,V=np.linalg.eigh(R);order=np.argsort(eig)[::-1];eig=eig[order];V=V[:,order]
for j,i in enumerate((2,1,0)):
    if V[i,j]<0:V[:,j]*=-1
scores=std@V
assert np.allclose((scores*w[:,None]).T@scores,np.diag(eig),atol=1e-10)
early=(np.array([[r[k+'_early'] for k in cols] for r in common])-mu)/sd@V
late=(np.array([[r[k+'_late'] for k in cols] for r in common])-mu)/sd@V
for i,r in enumerate(common):
    for j in range(3):
        k='PC'+str(j+1);r.update({k:float(scores[i,j]),k+'_early':float(early[i,j]),k+'_late':float(late[i,j]),k+'_delta':float(late[i,j]-early[i,j])})
blocks=defaultdict(list)
for r in common:blocks[r['block']].append(r)
def compare(obs,k):
    a=statistics.mean(r[k] for r in obs)
    differences=[r[k]-wm(blocks[r['block']],k) for r in obs];b=defaultdict(list)
    for r,d in zip(obs,differences):b[r['block']].append(d)
    means=[statistics.mean(v) for v in b.values()]
    leave=[statistics.mean(d for r,d in zip(obs,differences) if r['block']!=k1) for k1 in b] if len(b)>1 else []
    return {'observed':a,'expected':a-statistics.mean(differences),'difference':statistics.mean(differences),'equal_block_difference':statistics.mean(means),'blocks_positive':sum(v>0 for v in means),'blocks_negative':sum(v<0 for v in means),'lobo_min':min(leave) if leave else None,'lobo_max':max(leave) if leave else None}
stats={}
for g in groups:
    obs=[r for r in common if r['recorded_'+g]]
    stats[g]={'tiles':len(obs),'blocks':len({r['block'] for r in obs}),'metrics':{k:compare(obs,k) for k in ('PC1','PC2','PC1_delta','PC2_delta','sic_mean','sss_mean','sst_mean','has_plant')}}
combo=defaultdict(lambda:{'tiles':0,'rock_pixels':0})
for r in common:
    k=''.join('+' if r[j]>0 else '-' if r[j]<0 else '0' for j in ('PC1_delta','PC2_delta'))
    a=combo[k];a['tiles']+=1;a['rock_pixels']+=r['rock_pixels']
res={'status':'EXECUTED_COMMON_PERIOD_1993_2018_PHYSICAL_OPPORTUNITY','tiles':len(common),'blocks':len(blocks),'rock_pixels':sum(r['rock_pixels'] for r in common),'columns':cols,'mean':mu.tolist(),'sd':sd.tolist(),'correlation':R.tolist(),'explained':(eig/eig.sum()).tolist(),'eigenvectors':V.tolist(),'physical':{k:wm(common,k) for k in [v+'_'+s for v in cols for s in ('early','late','delta')]+['PC1_delta','PC2_delta']},'axis_change_counts':dict(combo),'groups':stats,'sic_independent_arithmetic_QA':{'checks':checks,'max_abs_discrepancy':maxerr},'limits':'Fixed static land, same calendar months, different ocean spatial estimators (100km SIC vs nearest GLORYS wet cell), no measured plant change, no suitability, no inference of ecological absence, no forecast.'}
with (out/'common_tiles.csv').open('w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(common[0]));wr.writeheader();wr.writerows(common)
(out/'result.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
print('V28_RESULT='+json.dumps(res),flush=True)
