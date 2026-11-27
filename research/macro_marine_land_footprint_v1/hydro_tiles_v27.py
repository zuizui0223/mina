"""V27 native GLORYS hydrography on fixed V25 coastal frame; 1993–2018."""
import csv,io,json,hashlib,pathlib,sys,zipfile,math,statistics
from collections import defaultdict,Counter
import fsspec,numpy as np,pandas as pd,xarray as xr
src,oldsrc,icesrc,out=map(pathlib.Path,sys.argv[1:5]);out.mkdir(parents=True,exist_ok=True)
def member(p,h,n):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(p,'digest')
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        paths=[x for x in z.namelist() if pathlib.PurePosixPath(x).name==n];assert len(paths)==1,(p,n,paths)
        return z.read(paths[0])
def read(p,h,n):return list(csv.DictReader(io.StringIO(member(p,h,n).decode('utf-8-sig'))))
H='9ab2ceea44658d66d66f3f2b3805e2b15715e51b7a79aa8cba4198a386a91788'
rows=read(src,H,'wet_tile_mapping.csv');pilot=read(src,H,'native_pilot.csv')
assert len(rows)==1722 and len(pilot)==1722*4 and len({r['tile'] for r in rows})==1722
for r in rows:
    for k in ('eligible','wet_x','wet_y','rock_pixels','plant_rock_pixels','has_plant','recorded_known','recorded_modern','recorded_ADPE','recorded_CHPE','recorded_GEPE'):r[k]=int(r[k])
    for k in ('wet_lat','wet_lon','distance_km','lat','lon'):r[k]=float(r[k])
    assert r['eligible']==(r['distance_km']<=25)
    assert r['rock_pixels']>0
eligible=[r for r in rows if r['eligible']]
points=sorted({(r['wet_y'],r['wet_x']) for r in eligible});lookup={p:i for i,p in enumerate(points)}
assert len(eligible)==1525 and len(points)==1077
store='https://s3.waw3-1.cloudferro.com/mdl-arco-time-025/arco/GLOBAL_MULTIYEAR_PHY_001_030/cmems_mod_glo_phy_my_0.083deg_P1M-m_202311/timeChunked.zarr'
ds=xr.open_zarr(fsspec.get_mapper(store),consolidated=True)
depth=int(np.argmin(abs(ds.elevation.values)));assert abs(float(ds.elevation.values[depth])+0.49402499198913574)<1e-5
lat=np.asarray(ds.latitude.values);lon=np.asarray(ds.longitude.values)
for r in rows:
    assert abs(float(lat[r['wet_y']])-r['wet_lat'])<2e-6 and abs(float(lon[r['wet_x']])-r['wet_lon'])<2e-6
t=pd.DatetimeIndex(ds.time.values);ys=tuple(range(1993,2019));ms=(8,9,10,11)
months=np.flatnonzero((t.year>=1993)&(t.year<=2018)&np.isin(t.month,ms))
keys=[(int(t[j].year),int(t[j].month)) for j in months]
assert keys==[(y,m) for y in ys for m in ms]
monthlookup={v:i for i,v in enumerate(keys)}
sel={'time':xr.DataArray(months,dims='month'),'latitude':xr.DataArray([p[0] for p in points],dims='wet_cell'),'longitude':xr.DataArray([p[1] for p in points],dims='wet_cell'),'elevation':depth}
vv={}
for name in ('so','thetao'):
    data=np.asarray(ds[name].isel(**sel).load().transpose('month','wet_cell').values,dtype=float)
    assert data.shape==(104,1077);vv[name]=data
    print('V27_NATIVE='+json.dumps({'var':name,'finite':int(np.isfinite(data).sum()),'cells':len(points),'months':len(keys)}),flush=True)
valid=np.isfinite(vv['so'])&np.isfinite(vv['thetao'])&(vv['so']>=20)&(vv['so']<=42)&(vv['thetao']>=-4)&(vv['thetao']<=25)
def tile_value(r,j):
    i=lookup.get((r['wet_y'],r['wet_x'])) if r['eligible'] else None
    if i is None or not valid[j,i]:return None,None
    return float(vv['so'][j,i]),float(vv['thetao'][j,i])
pp={(r['tile'],int(r['year']),int(r['month'])):r for r in pilot}
assert len(pp)==len(pilot)
n=0;missingchecks=0;maxpilot=0.
for r in rows:
    for m in ms:
        q=pp[r['tile'],2011,m];a,b=tile_value(r,monthlookup[2011,m])
        if a is None:
            assert q['sss']==q['sst_C']=='';missingchecks+=2
        else:
            for x,k in [(a,'sss'),(b,'sst_C')]:
                diff=abs(x-float(q[k]));assert diff<=1e-5;maxpilot=max(maxpilot,diff);n+=1
assert n==12200 and missingchecks==1576
old=read(oldsrc,'247204637096ae7659f16286b43c75f3801dc9068f619bc3446df5f0438061d9','all_original_eligible_colony_GLORYS12_1993_2020_AugNov_monthly.csv')
nold=0;maxold=0.
for r in old:
    k=(int(r['year']),int(r['month']))
    p=(int(r['source_original_wet_grid_y']),int(r['source_original_wet_grid_x']))
    if k not in monthlookup or p not in lookup or not r['surface_GLORYS_salinity'] or not r['surface_GLORYS_thetao_C']:continue
    j,i=monthlookup[k],lookup[p];assert valid[j,i]
    for name,field in [('so','surface_GLORYS_salinity'),('thetao','surface_GLORYS_thetao_C')]:
        d=abs(float(vv[name][j,i])-float(r[field]));assert d<=1e-5;maxold=max(maxold,d);nold+=1
assert nold>0
ice=read(icesrc,'00d2d66dc941c563afd7e185b7ab8b19733ce7bbae5f36f70044b50f19149459','marine_tiles.csv')
ice={r['tile']:r for r in ice};assert set(ice)=={r['tile'] for r in rows}
fields=('sss','sst_C')
monthly=[];annual=[];x=np.asarray(ys,dtype=float);x-=x.mean()
for r in rows:
    a=np.full((104,2),np.nan)
    for j,(y,m) in enumerate(keys):
        v=tile_value(r,j)
        if v[0] is not None:a[j]=v
        monthly.append({'tile':r['tile'],'year':y,'month':m,'sss':v[0],'sst_C':v[1]})
    yr=a.reshape(26,4,2).mean(axis=1)
    complete=np.isfinite(a).all()
    r['valid_months']=int(np.isfinite(a).all(axis=1).sum());r['complete_104']=int(complete)
    assert complete==np.isfinite(yr).all()
    for j,y in enumerate(ys):
        annual.append({'tile':r['tile'],'year':y,**{k:float(yr[j,i]) if np.isfinite(yr[j,i]) else None for i,k in enumerate(fields)}})
    for i,k in enumerate(fields):
        for stat in ('mean','early','late','delta','trend','sd'):r[k+'_'+stat]=None
        if complete:
            v=yr[:,i];early=float(v[:8].mean());late=float(v[-8:].mean())
            r.update({k+'_mean':float(v.mean()),k+'_early':early,k+'_late':late,k+'_delta':late-early,k+'_trend':float(10*np.dot(x,v-v.mean())/np.dot(x,x)),k+'_sd':float(v.std(ddof=1))})
    z=ice[r['tile']]
    for k in ('rock_pixels','has_plant','block','recorded_known','recorded_modern','recorded_ADPE','recorded_CHPE','recorded_GEPE'):assert str(r[k])==z[k],(k,r['tile'])
    r['sic12']=float(z['sic12']) if z['sic12'] else None
    for k in ('PC1','PC2','PC3'):r[k]=None
assert len(monthly)==1722*104 and len(annual)==1722*26
good=[r for r in rows if r['complete_104']];assert good
joint=[r for r in good if r['sic12'] is not None];assert joint
def wm(rr,k):return math.fsum(r['rock_pixels']*r[k] for r in rr)/sum(r['rock_pixels'] for r in rr)
def statgroups(rr,variables):
    blocks=defaultdict(list)
    for r in rr:blocks[r['block']].append(r)
    out={}
    for g in ('known','modern','ADPE','CHPE','GEPE'):
        obs=[r for r in rr if r['recorded_'+g]]
        if not obs:continue
        d={'tiles':len(obs),'blocks':len({r['block'] for r in obs}),'metrics':{}}
        for k in variables:
            delta=[r[k]-wm(blocks[r['block']],k) for r in obs];z=defaultdict(list)
            for r,v in zip(obs,delta):z[r['block']].append(v)
            bmean={b:statistics.mean(v) for b,v in z.items()}
            lobo=[statistics.mean(v for r,v in zip(obs,delta) if r['block']!=b) for b in bmean] if len(bmean)>1 else []
            a=statistics.mean(r[k] for r in obs)
            d['metrics'][k]={'observed':a,'expected':a-statistics.mean(delta),'difference':statistics.mean(delta),'equal_block_difference':statistics.mean(bmean.values()),'blocks_positive':sum(v>0 for v in bmean.values()),'blocks_negative':sum(v<0 for v in bmean.values()),'lobo_min':min(lobo) if lobo else None,'lobo_max':max(lobo) if lobo else None}
        out[g]=d
    return out
def pca(rr,cols):
    Z=np.array([[r[k] for k in cols] for r in rr],float)
    w=np.array([r['rock_pixels'] for r in rr],float);w/=w.sum()
    mu=w@Z;sd=np.sqrt(w@((Z-mu)**2));assert (sd>0).all()
    z=(Z-mu)/sd;R=(z*w[:,None]).T@z
    eigen,vec=np.linalg.eigh(R);order=np.argsort(eigen)[::-1];eigen=eigen[order];vec=vec[:,order]
    for i,j in enumerate((2,1,0)):
        if vec[j,i]<0:vec[:,i]*=-1
    scores=z@vec
    assert np.allclose((scores*w[:,None]).T@scores,np.diag(eigen),atol=1e-10)
    for r,sc in zip(rr,scores):r.update({f'PC{i+1}':float(v) for i,v in enumerate(sc)})
    return {'columns':cols,'weighted_mean':mu.tolist(),'weighted_sd':sd.tolist(),'weighted_correlation':R.tolist(),'explained':(eigen/eigen.sum()).tolist(),'loading_eigenvectors':vec.tolist(),'groups':statgroups(rr,['PC1','PC2','PC3'])}
def sign(v):return '+' if v>0 else '-' if v<0 else '0'
combo=defaultdict(lambda:{'tiles':0,'rock_pixels':0})
for r in good:
    z=combo[sign(r['sss_delta'])+sign(r['sst_C_delta'])];z['tiles']+=1;z['rock_pixels']+=r['rock_pixels']
assert sum(v['tiles'] for v in combo.values())==len(good)
metrics=[k+'_'+s for k in fields for s in ('mean','early','late','delta','trend','sd')]
z=np.array([[r['sss_mean'],r['sst_C_mean']] for r in good]);w=np.array([r['rock_pixels'] for r in good],float);w/=w.sum()
zc=z-w@z;cov=(zc*w[:,None]).T@zc
res={'status':'EXECUTED_FIXED_HYDROGRAPHY_1993_2018','frame_tiles':len(rows),'eligible_tiles':len(eligible),'complete_tiles':len(good),'unique_complete_wet_cells':len({(r['wet_y'],r['wet_x']) for r in good}),'complete_blocks':len({r['block'] for r in good}),'complete_rock_pixels':sum(r['rock_pixels'] for r in good),'frame_rock_pixels':sum(r['rock_pixels'] for r in rows),'missing_tile_months':sum(104-r['valid_months'] for r in rows),'physical':{k:wm(good,k) for k in metrics},'hydro_weighted_correlation':float(cov[0,1]/math.sqrt(cov[0,0]*cov[1,1])),'change_sign_counts':dict(combo),'groups':statgroups(good,metrics+['has_plant']),'mixed_period_pca':{'tiles':len(joint),'blocks':len({r['block'] for r in joint}),'rock_pixels':sum(r['rock_pixels'] for r in joint),**pca(joint,['sic12','sss_mean','sst_C_mean'])},'QA':{'pilot_numeric_checks':n,'pilot_missing_checks':missingchecks,'max_pilot_difference':maxpilot,'original_old_numeric_checks':nold,'max_old_difference':maxold},'limits':'GLORYS reanalysis native nearest wet cell, not observed diet or foraging; mixed-period PCA SIC 12 scenes vs GLORYS 104 months; no absence, species prediction, or climate causal effect'}
def write(name,rs):
    with (out/name).open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rs[0]));wr.writeheader();wr.writerows(rs)
write('hydro_tiles.csv',rows);write('hydro_monthly.csv',monthly);write('hydro_annual.csv',annual)
(out/'result.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
print('V27_RESULT='+json.dumps(res),flush=True)
