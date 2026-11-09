"""Contrast spatially resolved CMIP6 changes against equal-mean uniform shifts."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import spsolve
from scipy.spatial import cKDTree

out=Path('outputs/warming_access_sim')
cache=Path('work/warming_access_sim')
prior=Path('work/circuit_share')
dyads=pd.read_csv('outputs/circuit_share_forecast/dyads.csv').drop_duplicates(['A','B'])
grid=np.load(prior/'grid.npz')
baseline=np.mean([np.load(prior/f'sic_{year}.npy').astype(float) for year in range(1995,2015)],axis=0)
sources=pd.read_csv(out/'model_sources.csv')
records=[]; mappings=[]; jobs=[]

def cartesian(lat,lon):
    lat,lon=np.radians(lat),np.radians(lon)
    return np.column_stack((np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)))

def edges(mask,sources,sinks):
    ids=np.zeros(mask.shape,int)
    free=mask & ~sinks & (sources==0)
    ids[free]=np.arange(4,4+int(free.sum()))
    ids[sinks]=3
    ids[sources==1]=1
    ids[sources==2]=2
    n=int(ids.max()+1)
    locations=np.arange(mask.size).reshape(mask.shape)
    first=[]; second=[]; factors=[]
    for dy,dx in ((0,1),(1,0),(1,1),(1,-1)):
        h,w=mask.shape
        s=(slice(0,h-dy),slice(max(0,-dx),min(w,w-dx)))
        t=(slice(dy,h),slice(max(0,dx),min(w,w+dx)))
        valid=(ids[s]>0)&(ids[t]>0)&(ids[s]!=ids[t])
        first.extend(locations[s][valid]);second.extend(locations[t][valid])
        factors.extend(np.repeat(1/np.hypot(dy,dx),valid.sum()))
    a,b=ids.ravel()[first],ids.ravel()[second]
    keys,inverse=np.unique(np.minimum(a,b)*n+np.maximum(a,b),return_inverse=True)
    return n,*np.divmod(keys,n),inverse,first,second,np.array(factors)

def solve(graph,values,beta):
    n,u,v,inverse,first,second,factors=graph
    conductance=np.exp(-beta*values.ravel()/100)
    weights=np.bincount(inverse,weights=.5*(conductance[first]+conductance[second])*factors)
    adj=coo_matrix((np.r_[weights,weights],(np.r_[u,v],np.r_[v,u])),shape=(n,n)).tocsc()
    keep=np.r_[1,2,np.arange(4,n)]
    lap=diags(np.asarray(adj.sum(axis=1)).ravel())-adj
    volt=spsolve(lap.tocsc()[keep,:][:,keep],np.eye(len(keep),2))
    graph_path=cache/f'graph_{len(jobs):04}.txt'
    np.savetxt(graph_path,np.column_stack((u,v,weights)),fmt=['%d','%d','%.13g'])
    jobs.append((str(graph_path.resolve()),volt[0,0],volt[1,1]))
    return np.array([volt[0,0],volt[1,1]])

def project_scenarios():
    for row in dyads.itertuples():
        spec=np.load(prior/row.key/'spec.npz')
        i,j,k,l=spec['cut']; sl=(slice(i,j),slice(k,l))
        mask=spec['mask']; obs=baseline[sl]; current=obs[mask]
        assert np.isfinite(current).all()
        xyz=cartesian(grid['lat'][sl][mask],grid['lon'][sl][mask])
        graph=edges(mask,spec['s'],spec['sink'])
        refs={beta:solve(graph,obs,beta) for beta in [2,-2,0]}
        for modelset in sources.groupby('model'):
            model,src=modelset
            hist=np.load(cache/f'{model}_historical.npz')
            base=hist['1995']; valid=np.isfinite(base)&np.isfinite(hist['lat'])&np.isfinite(hist['lon'])&(abs(hist['lat'])<=90)
            tree=cKDTree(cartesian(hist['lat'][valid],hist['lon'][valid]))
            chord,index=tree.query(xyz)
            km=2*6371*np.arcsin(chord/2)
            selected=np.flatnonzero(valid)[index]
            maps=dict(pair=row.A+'-'+row.B,model=model,n_native=len(np.unique(selected)),max_snap_km=km.max(),median_snap_km=np.median(km),obs_sic=current.mean(),historical_sic=base.ravel()[selected].mean())
            mappings.append(maps)
            for exp in ['ssp245','ssp585']:
                future=np.load(cache/f'{model}_{exp}.npz')
                assert np.allclose(hist['lat'],future['lat'],equal_nan=True) and np.allclose(hist['lon'],future['lon'],equal_nan=True)
                for period in ['2041','2081']:
                    delta=future[period].ravel()[selected]-base.ravel()[selected]
                    assert np.isfinite(delta).all()
                    raw=current+delta;spatial=np.clip(raw,0,100);mean=spatial.mean()
                    shift=brentq(lambda value:np.clip(current+value,0,100).mean()-mean,-101,101)
                    uniform=np.clip(current+shift,0,100)
                    assert abs(uniform.mean()-mean)<1e-8
                    for mode,field in [('spatial',spatial),('equal_mean',uniform)]:
                        values=obs.copy();values[mask]=field
                        for beta in [2,-2]:
                            res=solve(graph,values,beta)
                            gain=np.log(refs[beta]/res)
                            records.append(dict(pair=maps['pair'],region=row.region,model=model,member=src.iloc[0].member,ssp=exp,period=period,beta=beta,mode=mode,
                                mean_sic_change=mean-current.mean(),clipped_fraction=np.mean((raw<0)|(raw>100)),matched_uniform_shift=shift,
                                access_gain_A_pct=100*np.expm1(gain[0]),access_gain_B_pct=100*np.expm1(gain[1]),common_access_pct=100*np.expm1(gain.mean()),relative_A_to_B_pct=100*np.expm1(gain[0]-gain[1]),absolute_log_contrast=abs(gain[0]-gain[1])))
    pd.DataFrame(jobs,columns=['path','R_A','R_B']).to_csv(cache/'jobs.csv',index=False)
    pd.DataFrame(records).to_csv(out/'scenarios.csv',index=False)
    pd.DataFrame(mappings).to_csv(out/'support.csv',index=False)
    print('scenario rows',len(records),'networks',len(jobs))

if __name__=="__main__":
    project_scenarios()
