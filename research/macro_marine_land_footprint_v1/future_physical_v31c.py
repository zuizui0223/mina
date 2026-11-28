"""V31c conditional future marine opportunity, not species suitability or population forecast."""
import csv,io,json,math,statistics,pathlib,sys,zipfile,hashlib
from collections import defaultdict,Counter
import numpy as np
ice,hydro,terrain,out=map(pathlib.Path,sys.argv[1:5]);out.mkdir(parents=True,exist_ok=True)
models=('ACCESS-CM2','BCC-CSM2-MR','CESM2');cols=('siconc','sos','tos')
scenarios=[(s,p) for s in ('ssp245','ssp585') for p in ('2041-2060','2081-2100')]
years=list(range(1995,2015));months=(8,9,10,11)
def rz(p,h):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(p,'digest')
    z=zipfile.ZipFile(p);assert z.testzip() is None;return z
def member(z,n):
    a=[x for x in z.namelist() if pathlib.PurePosixPath(x).name==n];assert len(a)==1,(n,a)
    return z.read(a[0])
def rows(z,n):return list(csv.DictReader(io.StringIO(member(z,n).decode('utf-8-sig'))))
def ix(rr,k):
    d={tuple(r[x] for x in k):r for r in rr};assert len(d)==len(rr);return d
iz=rz(ice,'9007f1d426d9fe2914782f7044d46fda8ec2f44c7ba6cac6cb55079e4de52f73')
hz=rz(hydro,'b52f0f5f534690fc26b3dd95b8a9db14d840c462362040c3939ba6d06f8d013f')
tz=rz(terrain,'531b94c8f38b4117d54bb9f3de0f293fdcf3120d1a7f991fb7eb8926e4536511')
it=rows(iz,'marine_tiles_30yr.csv');ht=rows(hz,'hydro_tiles.csv');tt=rows(tz,'terrain_tiles.csv')
I=ix(rows(iz,'monthly_120.csv'),('tile','year','month'));H=ix(rows(hz,'hydro_monthly.csv'),('tile','year','month'))
HT={r['tile']:r for r in ht};T={r['tile']:r for r in tt};assert len(it)==len(HT)==len(T)==1722
checks=0;err=0.
def ck(a,b):
    global checks,err
    e=abs(a-b);assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-9),(a,b);checks+=1;err=max(err,e)
groups=('modern','ADPE','CHPE','GEPE')
obs={}
for r in it:
    k=r['tile'];h=HT[k];t=T[k]
    for v in ('block','rock_pixels','has_plant')+tuple('recorded_'+g for g in groups):assert r[v]==h[v]==t[v],(k,v)
    a=[]
    for y in years:
        for m in months:
            i=I[k,str(y),str(m)]['sic_pp'];u=H[k,str(y),str(m)]
            a.append([float(v) if v!='' else np.nan for v in (i,u['sss'],u['sst_C'])])
    a=np.array(a);assert a.shape==(80,3)
    if np.isfinite(a).all():
        obs[k]={'tile':k,'block':r['block'],'rock_pixels':int(r['rock_pixels']),'rock_area_m2':float(t['rock_union_area_m2']),'terrain_complete':int(t['terrain_complete']),'has_plant':int(r['has_plant']),**{g:int(r['recorded_'+g]) for g in groups},'observed':a.mean(axis=0)}
assert len(obs)==1525
data={};supports={}
for j,model in enumerate(models):
    p=pathlib.Path(sys.argv[5+j*2]);pin=sys.argv[6+j*2];z=rz(p,pin)
    res=json.loads(member(z,'result.json'));assert res['status']=='EXECUTED_NATIVE_CMIP6_MODEL' and res['model']==model and res['source_stores_verified']==9
    maps=rows(z,'mapping.csv');mm={r['tile']:r for r in maps};assert len(mm)==1722 and set(mm)=={r['tile'] for r in it}
    records=rows(z,'tile_model_periods.csv');R=ix(records,('tile','experiment','period'));assert len(R)==1722*5
    meta=json.loads(member(z,'source_metadata.json'));assert len(meta['stores'])==9
    with np.load(io.BytesIO(member(z,'native_monthly.npz'))) as a:
        cells=list(zip(a['grid_y'].tolist(),a['grid_x'].tolist()));assert len(cells)==len(set(cells))
        mp={p:i for i,p in enumerate(cells)}
        for e,period in [('historical','1995-2014')]+scenarios:
            start,end=map(int,period.split('-'))
            vals=[]
            for v in cols:
                name=v+'__'+e;k=meta['keys'][name];ii=[i for i,(y,m) in enumerate(k) if start<=y<=end]
                assert [(k[i][0],k[i][1]) for i in ii]==[(y,m) for y in range(start,end+1) for m in months]
                x=a[name][ii];assert x.shape==(80,len(cells));vals.append(np.where(np.isfinite(x).all(axis=0),x.mean(axis=0),np.nan))
            clim=np.column_stack(vals)
            for t,r in mm.items():
                q=R[t,e,period];cell=(int(r['grid_y']),int(r['grid_x']));i=mp[cell]
                assert (int(q['grid_y']),int(q['grid_x']))==cell
                ck(float(q['distance_km']),float(r['distance_km']))
                vv=clim[i];assert bool(int(q['joint_complete']))==bool(np.isfinite(vv).all())
                for v,n in zip(vv,cols):
                    if np.isfinite(v):ck(float(v),float(q[n]))
                    else:assert q[n]==''
    data[model]=(mm,R)
    supports[model]={'geometry':res['geometry'],'periods':res['periods'],'archive_sha256':pin}
def supported(k,model,dist):
    mm,R=data[model]
    return float(mm[k]['distance_km'])<=dist and all(int(R[k,e,p]['joint_complete']) for e,p in [('historical','1995-2014')]+scenarios)
def wm(v,w):return np.asarray(w/w.sum())@np.asarray(v)
def stat(v,w,a):
    return {'tiles':int(np.sum(v)),'rock_pixel_fraction':float(np.sum(w[v])/np.sum(w)),'mapped_rock_area_fraction':float(np.sum(a[v])/np.sum(a))}
def binids(x):
    # Fixed, absolute climate-space bins, not inferred species envelope.
    return [(min(4,int(math.floor(v[0]/20))),int(math.floor(v[1]/.5)),int(math.floor(v[2]/.5))) for v in x]
def pca(x,w):
    mu=wm(x,w);sd=np.sqrt(wm((x-mu)**2,w));assert (sd>0).all()
    z=(x-mu)/sd;u=w/w.sum();R=(z*u[:,None]).T@z
    eig,V=np.linalg.eigh(R);ii=np.argsort(eig)[::-1];eig=eig[ii];V=V[:,ii]
    for j,i in enumerate((2,1,0)):
        if V[i,j]<0:V[:,j]*=-1
    assert np.allclose((z@V*u[:,None]).T@(z@V),np.diag(eig),atol=1e-10)
    return mu,sd,V,{'explained':(eig/eig.sum()).tolist(),'loadings':V.tolist(),'correlation':R.tolist(),'mean':mu.tolist(),'sd':sd.tolist()}
allrows=[];results=[]
for dist in (50,100,200,1e9):
    keys=[k for k in obs if all(supported(k,m,dist) for m in models)]
    if len(keys)<3:
        results.append({'distance_gate_km':None if dist==1e9 else dist,'status':'LOW_SUPPORT','tiles':len(keys)});continue
    r=[obs[k] for k in keys];w=np.array([x['rock_pixels'] for x in r],float);a=np.array([x['rock_area_m2'] for x in r],float)
    X=np.array([x['observed'] for x in r])
    mu,sd,V,pcs=pca(X,w);basebins=set(binids(X));base_low=X[:,0]<20
    q={'distance_gate_km':None if dist==1e9 else dist,'status':'EXECUTED_COMMON_PHYSICAL_SCENARIOS','tiles':len(keys),'blocks':len({x['block'] for x in r}),'rock_pixels':int(w.sum()),'mapped_rock_area_km2':float(a.sum()/1e6),'terrain_complete_tiles':sum(x['terrain_complete'] for x in r),'modern_groups':{g:sum(x[g] for x in r) for g in groups},'observed_pca':pcs,'baseline_low_sic':stat(base_low,w,a),'baseline_joint_bins':len(basebins),'models':{},'ensemble':[]}
    dd={}
    for model in models:
        mm,R=data[model];B=np.array([[float(R[k,'historical','1995-2014'][v]) for v in cols] for k in keys])
        q['models'][model]={'distinct_native_cells':len({(mm[k]['grid_y'],mm[k]['grid_x']) for k in keys}),'historical_model_mean':wm(B,w).tolist(),'historical_model_minus_observed':wm(B-X,w).tolist(),'scenarios':[]}
        for e,p in scenarios:
            F=np.array([[float(R[k,e,p][v]) for v in cols] for k in keys]);delta=F-B;raw=X+delta;adjusted=raw.copy();adjusted[:,0]=np.clip(adjusted[:,0],0,100)
            clipped=(raw[:,0]<0)|(raw[:,0]>100)
            assert np.isfinite(adjusted).all()
            pc=(adjusted-X)/sd@V
            low=adjusted[:,0]<20
            novel=np.array([v not in basebins for v in binids(adjusted)],bool)
            signs={'sic_decrease':stat(delta[:,0]<0,w,a),'freshening':stat(delta[:,1]<0,w,a),'sst_increase':stat(delta[:,2]>0,w,a),'sic_decrease_and_freshening':stat((delta[:,0]<0)&(delta[:,1]<0),w,a),'all_three_warm_fresh_less_ice':stat((delta[:,0]<0)&(delta[:,1]<0)&(delta[:,2]>0),w,a)}
            rec={'experiment':e,'period':p,'mean_native_delta':wm(delta,w).tolist(),'mean_adjusted_delta':wm(adjusted-X,w).tolist(),'mean_PC_delta':wm(pc,w).tolist(),'SIC_clipped':stat(clipped,w,a),'low_sic':stat(low,w,a),'new_low_sic':stat(low&~base_low,w,a),'lost_low_sic':stat(~low&base_low,w,a),'outside_baseline_joint_bins':stat(novel,w,a),'directions':signs,'observed_modern_groups':{}}
            for g in groups:
                k=np.array([bool(x[g]) for x in r])
                if k.any():rec['observed_modern_groups'][g]={'tiles':int(k.sum()),'mean_native_delta':np.mean(delta[k],axis=0).tolist(),'mean_PC_delta':np.mean(pc[k],axis=0).tolist()}
            q['models'][model]['scenarios'].append(rec)
            dd[model,e,p]=(delta,adjusted,pc,novel,low)
            if dist==100:
                for j,k in enumerate(keys):allrows.append({'tile':k,'model':model,'experiment':e,'period':p,'block':r[j]['block'],'rock_pixels':r[j]['rock_pixels'],'rock_area_m2':r[j]['rock_area_m2'],'distance_km':float(mm[k]['distance_km']),**{v+'_observed':float(X[j,i]) for i,v in enumerate(cols)},**{v+'_native_delta':float(delta[j,i]) for i,v in enumerate(cols)},**{v+'_conditional':float(adjusted[j,i]) for i,v in enumerate(cols)},**{'PC'+str(i+1)+'_delta':float(pc[j,i]) for i in range(3)},'SIC_clipped':int(clipped[j]),'outside_baseline_bins':int(novel[j])})
    for e,p in scenarios:
        d=np.stack([dd[m,e,p][0] for m in models])
        novel=np.stack([dd[m,e,p][3] for m in models])
        low=np.stack([dd[m,e,p][4] for m in models])
        s={'experiment':e,'period':p,'equal_model_mean_native_delta':wm(d.mean(axis=0),w).tolist(),'model_weighted_mean_delta_min':np.min([wm(x,w) for x in d],axis=0).tolist(),'model_weighted_mean_delta_max':np.max([wm(x,w) for x in d],axis=0).tolist(),'all_models_sic_decrease':stat((d[:,:,0]<0).all(axis=0),w,a),'all_models_freshening':stat((d[:,:,1]<0).all(axis=0),w,a),'all_models_sst_increase':stat((d[:,:,2]>0).all(axis=0),w,a),'all_models_less_ice_freshening':stat(((d[:,:,0]<0)&(d[:,:,1]<0)).all(axis=0),w,a),'all_models_new_low_sic':stat(low.all(axis=0)&~base_low,w,a),'all_models_outside_baseline_joint_bins':stat(novel.all(axis=0),w,a),'any_model_outside_baseline_joint_bins':stat(novel.any(axis=0),w,a)}
        q['ensemble'].append(s)
    results.append(q)
if allrows:
    with (out/'primary_tile_scenarios.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(allrows[0]));wr.writeheader();wr.writerows(allrows)
res={'status':'EXECUTED_CMIP6_CONDITIONAL_PHYSICAL_OPPORTUNITY','observed_complete_tiles':len(obs),'model_support':supports,'results':results,'native_mean_QA':{'checks':checks,'max_abs_difference':err},'limits':'Three availability-selected model members, nearest joint coarse wet native cells, observed baseline plus native anomalies, bounded SIC, no local downscaling, no P100 prediction, no future land exposure or actual species forecast; outside joint bins is a discretization-dependent physical analogy diagnostic.'}
(out/'result.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
primary=next(x for x in results if x['distance_gate_km']==100)
print('V31C_RESULT='+json.dumps({'status':res['status'],'observed_complete_tiles':len(obs),'QA':res['native_mean_QA'],'support':[{k:r[k] for k in ('distance_gate_km','status','tiles')} for r in results],'primary':primary}),flush=True)
