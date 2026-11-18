"""Create conductance networks on fixed 25-km ocean grids and validate by grounded Laplacian."""
from pathlib import Path
import numpy as np,pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
out=Path('outputs/circuit_share_forecast');cache=Path('work/circuit_share')
import sys
stress = "--stress" in sys.argv
triple = "--triple" in sys.argv
cases=[]; missing=[]
tr=pd.read_csv(cache/'tri_runs.csv' if triple else out/'transitions.csv')
for key,g in tr.groupby('key'):
    folder=cache/key; spec=np.load(folder/'spec.npz')
    mask=spec['mask'];target=spec['sink']; src=spec['s']; i,j,k,l=spec['cut']
    # Encode two source cells and the equipotential historical feeding-ground proxies as nodes 1,2,3.
    ids=np.zeros(mask.shape,int); free=mask & ~target & (src==0)
    ids[free]=np.arange(4,4+free.sum());ids[target]=3;ids[src==1]=1;ids[src==2]=2
    a=[];b=[];mult=[];origin=[];end=[]
    loc=np.arange(ids.size).reshape(ids.shape)
    for di,dj in [(0,1),(1,0),(1,1),(1,-1)]:
        si=slice(0,mask.shape[0]-di); ti=slice(di,mask.shape[0])
        sj=slice(max(0,-dj),min(mask.shape[1],mask.shape[1]-dj));tj=slice(max(0,dj),min(mask.shape[1],mask.shape[1]+dj))
        u=ids[si,sj];v=ids[ti,tj];valid=(u>0)&(v>0)&(u!=v)
        a.extend(u[valid]);b.extend(v[valid]);origin.extend(loc[si,sj][valid]);end.extend(loc[ti,tj][valid]);mult.extend(np.repeat(1/np.hypot(di,dj),valid.sum()))
    a=np.array(a);b=np.array(b);m=ids.max()+1
    pairs=np.minimum(a,b)*m+np.maximum(a,b);unique,inv=np.unique(pairs,return_inverse=True);u,v=np.divmod(unique,m)
    (folder/'nodes.txt').write_bytes(b'1\n2\n3\n')
    seasons = [(g.year.max(), reduction) for reduction in (10,20)] if stress else [(y,0) for y in sorted({0}|set(g.year)|set(g.year-1))]
    for year,reduction in seasons:
        if year==0:ice=np.zeros(mask.shape)
        else:ice=np.load(cache/f'sic_{year}.npy')[i:j,k:l]
        if np.any(~np.isfinite(ice[mask])):
            missing.append((key,year,int(np.sum(~np.isfinite(ice[mask])))));continue
        if reduction: ice=np.maximum(ice-reduction,0)
        for beta in ([0] if year==0 else [2,-2]):
            # As in the prior native raster configuration, average cell conductances.
            cond=np.exp(-beta*ice.ravel().astype(float)/100)
            weight=np.bincount(inv,weights=(cond[origin]+cond[end])*.5*np.array(mult))
            case=f'{key}_{year}_{beta}' + (f'_minus{reduction}' if stress else '');path=folder/(case+'.txt')
            np.savetxt(path,np.column_stack([u,v,weight]),fmt=['%d','%d','%.12g'])
            adj=coo_matrix((np.r_[weight,weight],(np.r_[u,v],np.r_[v,u])),shape=(m,m)).tocsc()
            from scipy.sparse import diags
            L=diags(np.asarray(adj.sum(axis=1)).ravel())-adj
            keep=np.r_[1,2,np.arange(4,m)].astype(int)
            rhs=np.eye(len(keep),2); volts=spsolve(L.tocsc()[keep,:][:,keep],rhs)
            cases.append(dict(case=case,key=key,year=year,beta=beta,path=str(path.resolve()),nodes=str((folder/'nodes.txt').resolve()),scipy_a=volts[0,0],scipy_b=volts[1,1]))
pd.DataFrame(cases).to_csv(cache/('stress_jobs.csv' if stress else 'tri_jobs.csv' if triple else 'jobs.csv'),index=False)
if not stress and not triple: pd.DataFrame(missing,columns=['key','year','missing_cells']).to_csv(out/'missing_ice.csv',index=False)
print('networks',len(cases),'missing years',len(missing))
