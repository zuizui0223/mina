"""V30c same-terrain-cohort conditional P100 residual; descriptive only."""
import csv,io,json,hashlib,pathlib,sys,zipfile,math,statistics
from collections import defaultdict
import numpy as np
t,m,out=map(pathlib.Path,sys.argv[1:4]);out.mkdir(parents=True,exist_ok=True)
def read(p,h,n):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        paths=[v for v in z.namelist() if pathlib.PurePosixPath(v).name==n];assert len(paths)==1
        return list(csv.DictReader(io.StringIO(z.read(paths[0]).decode('utf-8-sig'))))
T={r['tile']:r for r in read(t,sys.argv[4],'terrain_tiles.csv')};assert len(T)==1722
groups=('modern','ADPE','CHPE','GEPE')
cols=('p100','sic','sss','sst','log_area','coast_distance','log_relief','log_slope','elevation')
outrows=[]
for mode in ('shared_aug_oct','winter_vs_aug_nov'):
    raw=read(m,'5f883169cc78726d80f17a9427738a28da87a139233e049fe9201b83795e765f',mode+'_tiles.csv')
    assert len(raw)==1525
    rs=[]
    for r in raw:
        a=T[r['tile']]
        for k in ('block','rock_pixels','has_plant')+tuple('recorded_'+g for g in groups):assert a[k]==r[k]
        if not int(a['terrain_complete']):continue
        v=[float(r[k]) for k in cols[:4]]+[math.log1p(float(a['rock_union_area_m2'])),float(a['median_coastal_distance_km']),math.log1p(float(a['relief_p90_p10_m'])),math.log1p(float(a['median_slope_deg'])),float(a['median_elevation_m_ellipsoid'])]
        rs.append((r,v))
    z=np.asarray([v for r,v in rs]);w=np.asarray([float(r['rock_pixels']) for r,v in rs]);w/=w.sum()
    mu=w@z;sd=np.sqrt(w@((z-mu)**2));assert (sd>0).all()
    x=(z-mu)/sd
    bl=defaultdict(list)
    for i,(r,v) in enumerate(rs):bl[r['block']].append(i)
    for ids in bl.values():x[ids]-=(w[ids]/w[ids].sum())@x[ids]
    def fit(n,keep):
        a=x[keep,1:n];y=x[keep,0];q=w[keep];q=q/q.sum()
        b,_,rank,sing=np.linalg.lstsq(a*np.sqrt(q[:,None]),y*np.sqrt(q),rcond=None)
        if rank!=n-1:return None
        err=y-a@b;ss=float(q@(y*y));se=float(q@(err*err))
        assert np.max(abs((a*q[:,None]).T@err))<1e-10
        return b,{'rank':int(rank),'condition':float(sing.max()/sing.min()),'R2':1-se/ss,'residual_variance':se,'beta':b.tolist()}
    keep=np.ones(len(rs),bool)
    for n,tag in [(4,'marine_only'),(8,'marine_terrain'),(9,'elevation_sensitivity')]:
        f=fit(n,keep)
        if f is None:
            outrows.append({'mode':mode,'model':tag,'status':'RANK_FAIL'});continue
        b,stats=f;err=x[:,0]-x[:,1:n]@b
        for g in groups:
            obs=[i for i,(r,v) in enumerate(rs) if int(r['recorded_'+g])]
            by=defaultdict(list)
            for i in obs:by[rs[i][0]['block']].append(i)
            if not obs:continue
            dif=[float(err[i]) for i in obs];loo=[]
            for k in by:
                mask=np.array([r['block']!=k for r,v in rs])
                refit=fit(n,mask)
                i=[j for j in obs if mask[j]]
                if refit is not None and i:loo.append(float(np.mean(x[i,0]-x[i,1:n]@refit[0])))
            outrows.append({'mode':mode,'model':tag,'group':g,'status':'DESCRIPTIVE_RESIDUAL' if len(obs)>=20 and len(by)>=5 else 'LOW_SUPPORT','joint_tiles':len(rs),'joint_blocks':len(bl),'observed_tiles':len(obs),'observed_blocks':len(by),'mean_residual':statistics.mean(dif),'equal_block_residual':statistics.mean(statistics.mean(float(err[i]) for i in v) for v in by.values()),'positive_blocks':sum(statistics.mean(float(err[i]) for i in v)>0 for v in by.values()),'lobo_refits':len(loo),'lobo_min':min(loo) if loo else None,'lobo_max':max(loo) if loo else None,'fit':stats})
res={'status':'EXECUTED_DESCRIPTIVE_TERRAIN_RESIDUAL','models':outrows,'limits':'Within-block centered WLS, not independent causal effect, selection or true absence; no rescue of failed matching balance.'}
(out/'residual.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
print('V30C_RESULT='+json.dumps(res),flush=True)
