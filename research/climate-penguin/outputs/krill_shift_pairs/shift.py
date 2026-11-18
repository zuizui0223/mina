"""Paired fixed-ice counterfactuals on the original seven ocean networks."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path('outputs/warming_access_sim').resolve()))
import simulate as base
import numpy as np
import pandas as pd
from pyproj import Geod
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import spsolve

out=Path('outputs/krill_shift_pairs')
cache=Path('work/krill_shift_pairs')
cal=pd.read_csv(out/'empirical_shifts.csv')
geo=Geod(ellps='WGS84')

def solve(graph,field,beta):
    n,u,v,inv,a,b,factors=graph
    conductance=np.exp(-beta*field.ravel().astype(float)/100)
    w=np.bincount(inv,weights=(conductance[a]+conductance[b])*.5*factors)
    adj=coo_matrix((np.r_[w,w],(np.r_[u,v],np.r_[v,u])),shape=(n,n)).tocsc()
    keep=np.r_[1,2,np.arange(4,n)]
    lap=diags(adj.sum(axis=1).A1)-adj
    volts=spsolve(lap.tocsc()[keep,:][:,keep],np.eye(len(keep),2))
    return np.array([volts[0,0],volts[1,1]])

def assign(mask,src,sink,lon,lat,km,bearing):
    original=np.flatnonzero(sink); coastal=np.flatnonzero(mask&(src==0))
    x,y=lon.ravel()[original].astype(float),lat.ravel()[original].astype(float)
    dest_x,dest_y,_=geo.fwd(x,y,np.full(len(x),float(bearing)),np.full(len(x),km*1000))
    x1,x2=np.meshgrid(dest_x,lon.ravel()[coastal],indexing='ij')
    y1,y2=np.meshgrid(dest_y,lat.ravel()[coastal],indexing='ij')
    dist=geo.inv(x1,y1,x2,y2)[2]/1000
    ix,jx=linear_sum_assignment(dist); new=coastal[jx]
    snap=dist[ix,jx]
    actual=geo.inv(x[ix],y[ix],lon.ravel()[new],lat.ravel()[new])[2]/1000
    return original[ix],new,snap,actual

rows=[];supports=[];native=[]
for dyad in base.dyads.itertuples():
    pair=dyad.A+'-'+dyad.B
    spec=np.load(base.prior/dyad.key/'spec.npz');i,j,k,l=spec['cut']
    sl=np.s_[i:j,k:l];mask=spec['mask'];src=spec['s'];sink=spec['sink']
    lon,lat=base.grid['lon'][sl],base.grid['lat'][sl];obs=base.baseline[sl].copy()
    xyz=base.cartesian(lat[mask],lon[mask]);g0=base.edges(mask,src,sink)
    shifts=cal[cal.region==dyad.region].km
    treatments=[]
    for level,q,bearing in [('median_SW',.5,225),('q75_SW',.75,225),('median_S',.5,180),('median_NE',.5,45)]:
        km=shifts.quantile(q)
        orig,new,snap,actual=assign(mask,src,sink,lon,lat,km,bearing)
        supports.append(dict(pair=pair,region=dyad.region,treatment=level,km=km,bearing=bearing,n=len(snap),median_realized_km=np.median(actual),target_snap_max_km=max(snap),within25_fraction=np.mean(snap<=25),changed_cells=len(set(new)-set(orig))))
        for policy,ok in [('all',np.ones(len(orig),bool)),('within25',snap<=25)]:
            if not ok.any():continue
            oldmask=np.zeros_like(mask);oldmask.ravel()[orig[ok]]=True
            newmask=np.zeros_like(mask);newmask.ravel()[new[ok]]=True
            oldg=g0 if ok.all() else base.edges(mask,src,oldmask)
            newg=base.edges(mask,src,newmask)
            treatments.append((level,policy,oldg,newg))
    for beta in [2,-2]:
        for level,policy,oldg,newg in treatments:
            ref=solve(oldg,obs,beta)
            for model,mod in base.sources.groupby('model'):
                hist=np.load(base.cache/f'{model}_historical.npz');h=hist['1995'];valid=np.isfinite(h)&np.isfinite(hist['lat'])&np.isfinite(hist['lon'])&(abs(hist['lat'])<=90)
                _,idx=cKDTree(base.cartesian(hist['lat'][valid],hist['lon'][valid])).query(xyz);sel=np.flatnonzero(valid)[idx]
                for ssp in ['ssp245','ssp585']:
                    fut=np.load(base.cache/f'{model}_{ssp}.npz')
                    for per in ['2041','2081']:
                        f=obs.copy();f[mask]=np.clip(obs[mask]+(fut[per].ravel()[sel]-h.ravel()[sel]),0,100)
                        ice=solve(oldg,f,beta);both=solve(newg,f,beta)
                        rows.append(dict(pair=pair,A=dyad.A,B=dyad.B,region=dyad.region,beta=beta,shift=level,policy=policy,model=model,ssp=ssp,period=per,
                          base_RA=ref[0],base_RB=ref[1],fixed_RA=ice[0],fixed_RB=ice[1],moved_RA=both[0],moved_RB=both[1]))
                        if beta==2 and level=='median_SW' and policy=='all':
                            n,u,v,inv,a,b,fac=newg
                            c=np.exp(-beta*f.ravel()/100)
                            weights=np.bincount(inv,weights=(c[a]+c[b])*.5*fac)
                            path=cache/f'graph_{len(native):04}.txt'
                            np.savetxt(path,np.column_stack([u,v,weights]),fmt=['%d','%d','%.13g'])
                            native.append((str(path.resolve()),*both))
pd.DataFrame(rows).to_csv(out/'counterfactuals.csv',index=False)
pd.DataFrame(supports).to_csv(out/'shift_support.csv',index=False)
pd.DataFrame(native,columns=['path','R_A','R_B']).to_csv(cache/'jobs.csv',index=False)
print(len(rows),len(native))
