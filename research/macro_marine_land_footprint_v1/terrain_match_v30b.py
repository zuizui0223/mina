"""V30b: fixed terrain-matched observed/background contrasts. Not occupancy or causality."""
import csv,io,hashlib,json,math,pathlib,statistics,sys,zipfile
from collections import defaultdict,Counter
import numpy as np
terrain,marine,out=map(pathlib.Path,sys.argv[1:4]);out.mkdir(parents=True,exist_ok=True)
def rz(p,h):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(p,'digest')
    z=zipfile.ZipFile(p);assert z.testzip() is None;return z
def mem(z,n):
    a=[x for x in z.namelist() if pathlib.PurePosixPath(x).name==n];assert len(a)==1
    return z.read(a[0])
def read(z,n):return list(csv.DictReader(io.StringIO(mem(z,n).decode('utf-8-sig'))))
tz=rz(terrain,sys.argv[4]);mz=rz(marine,'5f883169cc78726d80f17a9427738a28da87a139233e049fe9201b83795e765f')
tres=json.loads(mem(tz,'result.json'));assert tres['status']=='EXECUTED_FIXED_REMA_TERRAIN'
tt=read(tz,'terrain_tiles.csv');T={r['tile']:r for r in tt};assert len(T)==len(tt)==1722
source=json.loads(mem(tz,'source_geometry.json'));assert source['coastal_hit_pixels']==27911
groups=('known','modern','ADPE','CHPE','GEPE')
metrics=('p100','p100_residual_global_z','p100_residual_within_block_z','sic','sss','sst','has_plant','p100_delta','sic_delta')
basecov=('log_rock_area','coast_distance','log_relief','log_slope')
checks=0;maxerr=0.
def ck(a,b):
    global checks,maxerr
    d=abs(a-b);assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-9),(a,b)
    checks+=1;maxerr=max(maxerr,d)
for r in tt:
    n,ne,ns=(int(r[x]) for x in ('native_selected_pixels','valid_elevation_pixels','valid_slope_pixels'))
    assert 0<=ns<=ne<=n
    assert bool(int(r['terrain_complete']))==(ne>=3 and ns>=3 and ne>=.5*n and ns>=.5*n)
    assert 0<=float(r['rock_union_area_m2'])<=int(r['rock_pixels'])*1e6+1e-3
    assert 0<=float(r['median_coastal_distance_km'])<=5
    checks+=3
ck(sum(float(r['rock_union_area_m2']) for r in tt)/1e6,tres['rock_union_area_km2'])
assert sum(int(r['terrain_complete']) for r in tt)==tres['terrain_complete_tiles']
def means(v,w):
    w=np.asarray(w,float);return np.asarray(w/w.sum())@np.asarray(v,float)
def summarize(dif,blocks):
    b=defaultdict(list)
    for d,k in zip(dif,blocks):b[k].append(float(d))
    bm=[statistics.mean(v) for v in b.values()]
    loo=[statistics.mean(float(d) for d,k in zip(dif,blocks) if k!=g) for g in b] if len(b)>1 else []
    return {'difference':float(statistics.mean(dif)),'equal_block_difference':statistics.mean(bm),'positive_blocks':sum(v>1e-12 for v in bm),'negative_blocks':sum(v< -1e-12 for v in bm),'lobo_min':min(loo) if loo else None,'lobo_max':max(loo) if loo else None}
detail=[];results=[]
for mode in ('shared_aug_oct','winter_vs_aug_nov'):
    raw=read(mz,mode+'_tiles.csv');assert len(raw)==1525 and len({r['tile'] for r in raw})==1525
    rr=[]
    for r in raw:
        t=T[r['tile']]
        for k in ('block','rock_pixels','has_plant')+tuple('recorded_'+g for g in groups):assert r[k]==t[k],(k,r['tile'])
        if not int(t['terrain_complete']):continue
        q={**r}
        for k in metrics:q[k]=float(r[k])
        for k in ('rock_pixels',)+tuple('recorded_'+g for g in groups):q[k]=int(r[k])
        q.update(log_rock_area=math.log1p(float(t['rock_union_area_m2'])),coast_distance=float(t['median_coastal_distance_km']),log_relief=math.log1p(float(t['relief_p90_p10_m'])),log_slope=math.log1p(float(t['median_slope_deg'])),elevation=float(t['median_elevation_m_ellipsoid']))
        rr.append(q)
    assert len(rr)>0
    blocks=defaultdict(list)
    for i,r in enumerate(rr):blocks[r['block']].append(i)
    ww=np.array([r['rock_pixels'] for r in rr],float)
    m=np.array([[r[k] for k in metrics] for r in rr],float)
    design={'mode':mode,'joint_tiles':len(rr),'joint_blocks':len(blocks),'joint_rock_pixels':int(ww.sum()),'groups':{g:{'marine_tiles':sum(int(r['recorded_'+g]) for r in raw),'joint_tiles':sum(r['recorded_'+g] for r in rr)} for g in groups},'comparisons':[]}
    for cov,cal,tag in [(basecov,1.,'primary'),(basecov,.5,'strict_caliper'),(basecov,1.5,'wide_caliper'),(basecov+('elevation',),1.,'elevation_sensitivity')]:
        z=np.array([[r[k] for k in cov] for r in rr],float)
        w=ww/ww.sum();mu=w@z;sd=np.sqrt(w@((z-mu)**2));assert (sd>0).all()
        z=(z-mu)/sd
        maps={}
        for i,r in enumerate(rr):
            allc=np.array([j for j in blocks[r['block']] if j!=i],dtype=int)
            good=allc[np.all(np.abs(z[allc]-z[i])<=cal+1e-12,axis=1)]
            assert i not in good and len(good)<=len(allc)
            maps[i]=(allc,good)
        for g in groups[1:]:
            obs=[i for i,r in enumerate(rr) if r['recorded_'+g]]
            matched=[i for i in obs if len(maps[i][1])>=3]
            bb=[rr[i]['block'] for i in matched]
            support={'mode':mode,'design':tag,'species':g,'caliper_sd':cal,'covariates':cov,'joint_observed_tiles':len(obs),'matched_tiles':len(matched),'matched_blocks':len(set(bb)),'unmatched_same_block_lt3':sum(len(maps[i][0])<3 for i in obs),'unmatched_caliper_lt3':sum(len(maps[i][0])>=3 and len(maps[i][1])<3 for i in obs)}
            if not matched:
                support.update(status='NO_MATCHED_SUPPORT');design['comparisons'].append(support);continue
            expect=[];bexpect=[];zd=[];zbd=[];ess=[];allmatches=set()
            for i in matched:
                a,c=maps[i];w1=ww[c]/ww[c].sum();w0=ww[a]/ww[a].sum()
                em=w1@m[c];eb=w0@m[a];expect.append(em);bexpect.append(eb)
                zd.append(z[i]-w1@z[c]);zbd.append(z[i]-w0@z[a])
                ess.append(float(1/(w1@w1)));allmatches.update(c.tolist())
                ck(float(w1.sum()),1.);ck(float(w0.sum()),1.)
                assert np.all(np.abs(z[c]-z[i])<=cal+1e-12)
                detail.append({'mode':mode,'design':tag,'species':g,'focal_tile':rr[i]['tile'],'block':rr[i]['block'],'n_candidates':len(c),'effective_candidates':ess[-1],'matched_tile_ids':';'.join(rr[j]['tile'] for j in c),'weights':';'.join(format(v,'.16g') for v in w1)})
            e=np.asarray(expect);be=np.asarray(bexpect);o=m[matched]
            imbalance=np.mean(zd,axis=0);before=np.mean(zbd,axis=0)
            mx=float(np.max(np.abs(imbalance)))
            support.update(status='DESCRIPTIVE_TERRAIN_MATCH_SUPPORTED' if len(matched)>=20 and len(set(bb))>=5 and mx<=.25 else 'DESCRIPTIVE_ONLY_SUPPORT_OR_BALANCE_FAIL',max_abs_mean_imbalance=mx,mean_imbalance_before=dict(zip(cov,map(float,before))),mean_imbalance_after=dict(zip(cov,map(float,imbalance))),distinct_comparison_tiles=len(allmatches),median_effective_comparison_n=statistics.median(ess),min_effective_comparison_n=min(ess),metrics={})
            for j,k in enumerate(metrics):
                v=o[:,j];d=v-e[:,j];d0=v-be[:,j]
                ck(float(v.mean()-e[:,j].mean()),float(d.mean()))
                support['metrics'][k]={'observed':float(v.mean()),'matched_expected':float(e[:,j].mean()),'baseline_expected':float(be[:,j].mean()),'baseline_difference':float(d0.mean()),**summarize(d,bb)}
            design['comparisons'].append(support)
    results.append(design)
if detail:
    with (out/'matching_weights.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(detail[0]));wr.writeheader();wr.writerows(detail)
res={'status':'EXECUTED_FIXED_TERRAIN_MATCHING','source_terrain':tres,'results':results,'QA':{'checks':checks,'max_abs_discrepancy':maxerr},'limits':'Same-block available geography comparison, not absence or fitted occupancy. Terrain support and balance gates are descriptive, no statistical p-values or independent replication. REMA native slope and mapped rock area are coarse context, not actual travel paths.'}
(out/'result.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
# Compact receipt for logs; retain all values in the archive.
print('V30B_RESULT='+json.dumps(res),flush=True)
