"""V32: geographically held-out analogue distance diagnostic and conditional climate areas."""
import csv,io,json,math,statistics,hashlib,pathlib,sys,zipfile
from collections import defaultdict
import numpy as np
from scipy.spatial.distance import cdist
future,frame,terrain,out=map(pathlib.Path,sys.argv[1:5]);out.mkdir(parents=True,exist_ok=True)
models=('ACCESS-CM2','BCC-CSM2-MR','CESM2')
groups=('ADPE','CHPE','GEPE')
variables=('siconc','sos','tos')
scenarios=[(s,p) for s in ('ssp245','ssp585') for p in ('2041-2060','2081-2100')]
def zread(p,h):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(p,'digest')
    z=zipfile.ZipFile(p);assert z.testzip() is None;return z
def member(z,n):
    a=[s for s in z.namelist() if pathlib.PurePosixPath(s).name==n];assert len(a)==1,(n,a)
    return z.read(a[0])
def rows(z,n):return list(csv.DictReader(io.StringIO(member(z,n).decode('utf-8-sig'))))
def index(rr,k):
    d={tuple(r[x] for x in k):r for r in rr};assert len(d)==len(rr);return d
def write(n,rr):
    if not rr:return
    with (out/n).open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rr for k in r)));wr.writeheader();wr.writerows(rr)
fz=zread(future,'bac958ee1c96168e730a1f5c23c13614da6d3da322d04ee29ee504d857466e94')
gz=zread(frame,'13bfe5866a27f6fbfad681ed4a44d834f6019c663f94193e1039e96b81c22060')
tz=zread(terrain,'531b94c8f38b4117d54bb9f3de0f293fdcf3120d1a7f991fb7eb8926e4536511')
fr={r['tile']:r for r in rows(gz,'opportunity_tiles.csv') if r['band_km']=='5'}
tr={r['tile']:r for r in rows(tz,'terrain_tiles.csv')}
rr=rows(fz,'primary_tile_scenarios.csv');R=index(rr,('tile','model','experiment','period'))
keys=sorted({r['tile'] for r in rr},key=int);n=len(keys)
assert n==1401 and len(rr)==n*12 and len(fr)==len(tr)==1722
native=[]
for j,(model,pin) in enumerate(zip(models,('1c7d282e4d77930679b1bd444f624fc7aa513f1f2b70c857e6e8254defb79bd5','57d1b908cb18a0e8f6cd4a3fab116220915e28daacf707bb7639629c87c7cca3','f514be11e1ad3d175631a994a326981e6ddd11d75c5ff661212f10c082b2ee87'))):
    z=zread(pathlib.Path(sys.argv[5+j]),pin)
    mp={r['tile']:r for r in rows(z,'mapping.csv')};assert len(mp)==1722
    q=[(int(mp[k]['grid_y']),int(mp[k]['grid_x'])) for k in keys]
    assert all(float(mp[k]['distance_km'])<=100 for k in keys)
    native.append(q)
base=[];w=[];area=[];block=[];label={g:[] for g in groups};checks=0;maxerr=0.
def ck(a,b,tol=1e-8):
    global checks,maxerr
    d=abs(a-b);assert math.isclose(a,b,rel_tol=1e-10,abs_tol=tol),(a,b)
    checks+=1;maxerr=max(maxerr,d)
F={};clip={}
for j,k in enumerate(keys):
    t=fr[k];u=tr[k];r=R[k,models[0],*scenarios[0]]
    assert t['block']==u['block']==r['block'] and t['rock_pixels']==u['rock_pixels']
    base.append([float(r[v+'_observed']) for v in variables]);w.append(int(t['rock_pixels']));area.append(float(r['rock_area_m2']));block.append(t['block'])
    ck(area[-1],float(u['rock_union_area_m2']))
    for g in groups:label[g].append(int(t['recorded_'+g]))
    for m in models:
        for s,p in scenarios:
            q=R[k,m,s,p]
            assert q['block']==block[-1] and int(q['rock_pixels'])==w[-1]
            ck(float(q['rock_area_m2']),area[-1])
            obs=np.array([float(q[v+'_observed']) for v in variables])
            for a,b in zip(obs,base[-1]):ck(a,b)
            raw=obs+np.array([float(q[v+'_native_delta']) for v in variables])
            cl=raw[0]<0 or raw[0]>100
            assert cl==bool(int(q['SIC_clipped']))
            raw[0]=np.clip(raw[0],0,100)
            val=[float(q[v+'_conditional']) for v in variables]
            for a,b in zip(raw,val):ck(a,b)
            F.setdefault((m,s,p),[]).append(val);clip.setdefault((m,s,p),[]).append(cl)
X=np.array(base);w=np.array(w,float);area=np.array(area,float);block=np.array(block);label={g:np.array(v,bool) for g,v in label.items()}
assert np.isfinite(X).all() and np.all(area>0) and len(set(block))==56
assert {g:int(v.sum()) for g,v in label.items()}=={'ADPE':31,'CHPE':62,'GEPE':37}
assert [len(set(q)) for q in native]==[183,143,156]
F={k:np.array(v) for k,v in F.items()};clip={k:np.array(v,bool) for k,v in clip.items()}
wn=w/w.sum();mu=wn@X;sd=np.sqrt(wn@((X-mu)**2));assert (sd>0).all()
Z=(X-mu)/sd;corr=(Z*wn[:,None]).T@Z;ev,V=np.linalg.eigh(corr);assert min(ev)>1e-6
white=V@np.diag(1/np.sqrt(ev))@V.T
def transform(x,metric):
    z=(x-mu)/sd
    if metric=='sic_only':return z[:,:1]
    if metric=='whitened':return z@white
    return z
blocks=sorted(set(block));bi={b:np.array(b.split(':'),int) for b in blocks}
def dist(a,b):return cdist(a,b).min(axis=1)
folds=[];scores=[];summary=[];scen=[];tileout=[]
def quantile(v,bb,q):
    c={b:sum(k==b for k in bb) for b in set(bb)}
    order=np.argsort(v,kind='stable');weights=np.array([1/(len(c)*c[b]) for b in bb])
    return float(np.asarray(v)[order][min(len(order)-1,np.searchsorted(np.cumsum(weights[order]),q,side='left'))])
def stat(flag,mask):
    return {'tiles':int(np.sum(flag&mask)),'rock_area_fraction':float(area[flag&mask].sum()/area[mask].sum()) if mask.any() else None,'rock_hit_fraction':float(w[flag&mask].sum()/w[mask].sum()) if mask.any() else None}
for metric in ('euclidean3','sic_only','whitened'):
    z=transform(X,metric)
    for group in groups:
        y=label[group];ref=z[y]
        for mode in ('native_exclusion','adjacent_exclusion'):
            ss=[];rankblocks={}
            for b in sorted(set(block[y])):
                hold=np.flatnonzero(block==b);test=np.flatnonzero(y&(block==b))
                allowed=block!=b
                if mode=='adjacent_exclusion':
                    allowed&=np.array([np.max(np.abs(bi[k]-bi[b]))>1 for k in block])
                for q in native:
                    forbidden={q[i] for i in hold}
                    allowed&=np.array([v not in forbidden for v in q])
                train=np.flatnonzero(y&allowed);nb=len(set(block[train]))
                rec={'metric':metric,'species':group,'mode':mode,'held_block':b,'held_recorded':len(test),'candidate_tiles':len(hold),'train_records':len(train),'train_blocks':nb,'train_tile_ids':';'.join(keys[i] for i in train)}
                if len(train)<10 or nb<3 or len(hold)<4:
                    folds.append({**rec,'status':'LOW_SUPPORT'});continue
                d=dist(z[hold],z[train]);pos={i:j for j,i in enumerate(hold)};ranks=[]
                for i in test:
                    j=pos[i];bg=hold!=i;delta=d[bg]-d[j];wg=w[hold[bg]]
                    rank=float(wg@((delta>1e-12)+.5*(abs(delta)<=1e-12))/wg.sum())
                    assert 0<=rank<=1
                    a={'metric':metric,'species':group,'mode':mode,'block':b,'tile':keys[i],'distance':float(d[j]),'rank':rank}
                    ss.append(a);scores.append(a);ranks.append(rank)
                rankblocks[b]=statistics.mean(ranks)
                folds.append({**rec,'status':'EVALUATED','mean_rank':rankblocks[b]})
            nb=len(rankblocks);nr=len(ss)
            er=statistics.mean(rankblocks.values()) if nb else None
            lo=[statistics.mean(v for k,v in rankblocks.items() if k!=b) for b in rankblocks] if nb>1 else []
            support=nr>=20 and nb>=5
            gate=support and er>.5 and min(lo)>.5
            su={'metric':metric,'species':group,'mode':mode,'all_reference_records':int(y.sum()),'reference_blocks':len(set(block[y])),'evaluated_records':nr,'evaluated_blocks':nb,'equal_block_rank':er,'equal_record_rank':statistics.mean(a['rank'] for a in ss) if ss else None,'rank_lobo_min':min(lo) if lo else None,'rank_lobo_max':max(lo) if lo else None,'calibration_support':bool(support),'descriptive_transfer_gate':bool(gate)}
            summary.append(su)
            if mode!='native_exclusion' or not support:continue
            ds=[a['distance'] for a in ss];bb=[a['block'] for a in ss]
            db=dist(z,ref)
            for q in (.8,.9,.95):
                thresh=quantile(ds,bb,q);baseflag=db<=thresh+1e-12
                assert np.all(baseflag[y])
                rec={'metric':metric,'species':group,'quantile':q,'threshold':thresh,'transfer_gate':bool(gate),'baseline':stat(baseflag,np.ones(n,bool)),'scenarios':[]}
                for s,p in scenarios:
                    fs={m:dist(transform(F[m,s,p],metric),ref)<=thresh+1e-12 for m in models}
                    goodclip=~np.logical_or.reduce([clip[m,s,p] for m in models])
                    def panel(mask):
                        return {'denominator_tiles':int(mask.sum()),'denominator_rock_area_km2':float(area[mask].sum()/1e6),'baseline':stat(baseflag,mask),'models':{m:{'future':stat(fs[m],mask),'gain':stat(fs[m]&~baseflag,mask),'loss':stat(~fs[m]&baseflag,mask),'persistent':stat(fs[m]&baseflag,mask)} for m in models},'all_model_gain':stat(np.logical_and.reduce(list(fs.values()))&~baseflag,mask),'all_model_loss':stat(~np.logical_or.reduce(list(fs.values()))&baseflag,mask)}
                    pa=panel(np.ones(n,bool));pc=panel(goodclip)
                    for m in models:
                        b0=pa['baseline']['rock_area_fraction'];f0=pa['models'][m]['future']['rock_area_fraction'];v=pa['models'][m]
                        ck(f0-b0,v['gain']['rock_area_fraction']-v['loss']['rock_area_fraction'])
                    rec['scenarios'].append({'experiment':s,'period':p,'full':pa,'common_unclipped':pc})
                    if metric=='euclidean3' and q==.9:
                        for i,k in enumerate(keys):
                            tileout.append({'species':group,'tile':k,'experiment':s,'period':p,'threshold':thresh,'baseline_analogue':int(baseflag[i]),**{m:int(fs[m][i]) for m in models},'common_unclipped':int(goodclip[i])})
                scen.append(rec)
write('transfer_folds.csv',folds);write('transfer_scores.csv',scores);write('primary_tile_analogues.csv',tileout)
res={'status':'EXECUTED_CONDITIONAL_CLIMATE_ANALOGUES','tiles':n,'blocks':len(blocks),'area_km2':float(area.sum()/1e6),'reference_counts':{g:int(y.sum()) for g,y in label.items()},'standardization':{'mean':mu.tolist(),'sd':sd.tolist(),'correlation':corr.tolist()},'transfer':summary,'analogue_scenarios':scen,'QA':{'checks':checks,'max_abs_difference':maxerr},'limits':'Species-associated observed climate analogue, not occupancy or suitability; modern record labels with historical climate; all same-block availability not true absences; fixed land, no P100, model and clipping limitations. Threshold calibrated on held-out distances, not independently validated classification.'}
(out/'result.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
# Compact log receipt; full scenario tables retained in artifact.
primary=[]
for r in scen:
    if r['metric']=='euclidean3' and r['quantile']==.9:
        primary.append({**{k:r[k] for k in ('metric','species','quantile','threshold','transfer_gate','baseline')},'scenarios':r['scenarios']})
print('V32_RESULT='+json.dumps({'status':res['status'],'tiles':n,'blocks':len(blocks),'area_km2':res['area_km2'],'reference_counts':res['reference_counts'],'transfer':summary,'primary':primary,'scenario_records':len(scen),'QA':res['QA']}),flush=True)
