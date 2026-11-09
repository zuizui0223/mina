"""Fix same-species dyads by observation support and source geography, without using change direction."""
from pathlib import Path
import io,zipfile,itertools
import pandas as pd,numpy as np
from pyproj import Geod
from scipy.ndimage import label
from scipy.spatial import cKDTree
out=Path('outputs/circuit_share_forecast');cache=Path('work/circuit_share')
geo=Geod(ellps='WGS84')
def km(x,y,lon,lat):
    lon,lat=np.broadcast_arrays(lon,lat)
    return geo.inv(np.full(lon.shape,float(x)),np.full(lat.shape,float(y)),lon.astype(float),lat.astype(float))[2]/1000
def xyz(lon,lat):
    a,b=np.radians(lon),np.radians(lat)
    return np.column_stack((np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)))
root=Path('work/mina-sync/research/climate-penguin/outputs')
d=pd.read_csv(root/'comparison_audit/mapppd_unambiguous_site_seasons.csv')
d=d[d.season.between(1992,2021)&d.method.isin(['ground','aerial','vhr','uav'])&d.n_methods.eq(1)&d['count'].ge(0)].copy()
with zipfile.ZipFile('work/highice_prey/krillbase.zip') as wrapper:
    with zipfile.ZipFile(io.BytesIO(wrapper.read(wrapper.namelist()[0]))) as z:k=pd.read_csv(z.open('krillbase_data.csv'),encoding='cp1252')
k=k[(k.SEASON<=1990)&k.RECORD_TYPE.eq('haul')&k.NUMBER_OF_KRILL_UNDER_1M2.gt(0)].dropna(subset=['LONGITUDE','LATITUDE'])
grid=np.load(cache/'grid.npz');lon,lat=grid['lon'],grid['lat'];marine=np.isfinite(np.load(cache/'sic_1991.npy'))
pts=np.argwhere(marine); tree=cKDTree(xyz(lon[marine],lat[marine]))
snapdist,ix=tree.query(xyz(k.LONGITUDE,k.LATITUDE))
prey=np.zeros_like(marine);rr,cc=pts[ix[snapdist*6371<=25]].T;prey[rr,cc]=True
tr=[]; specs=[]; nodes=[];fail=[]
for (region,sp),g in d.groupby(['region','species_id']):
    candidates=[]
    for (aa,a),(bb,b) in itertools.combinations(g.groupby('site_id'),2):
        h=a.merge(b,on='season').sort_values('season');h['total']=h.count_x+h.count_y;h['p']=h.count_x/h.total.replace(0,np.nan)
        h['next_share']=h.p.shift(-1);h['next_total']=h.total.shift(-1)
        z=h[(h.season.shift(-1)-h.season==1)&h.method_x.eq(h.method_x.shift(-1))&h.method_y.eq(h.method_y.shift(-1))&h.p.notna()&h.next_share.notna()]
        if len(z)<3:continue
        u,v=a.iloc[0],b.iloc[0];sep=geo.inv(u.longitude,u.latitude,v.longitude,v.latitude)[2]/1000
        if not 50<=sep<=300:continue
        candidates.append((-len(z),aa,bb,u,v,z,sep))
    used=set()
    for neg,aa,bb,u,v,z,sep in sorted(candidates,key=lambda t:t[:3]):
        if aa in used or bb in used:continue
        da=km(u.longitude,u.latitude,lon,lat); db=km(v.longitude,v.latitude,lon,lat)
        mask=marine&(np.minimum(da,db)<=250)
        coords=[np.unravel_index(np.argmin(np.where(mask,ds,np.inf)),ds.shape) for ds in (da,db)]
        ca,cb=coords;com,n=label(mask,np.ones((3,3)));mask &= com==com[ca]
        target=mask&prey&(da<=200)&(db<=200)&(da>=25)&(db>=25)
        target[ca]=False;target[cb]=False
        key=f'{sp}_{aa}_{bb}'
        if (not mask[cb] or da[ca]>35 or db[cb]>35 or ca==cb or not target.any()):
            fail.append((region,key,neg*-1,int(target.sum()),'source-snap/component/target gate'));continue
        used.update([aa,bb]); spec=cache/key;spec.mkdir(exist_ok=True)
        ii,jj=np.where(mask); sl=(slice(ii.min(),ii.max()+1),slice(jj.min(),jj.max()+1))
        source=np.zeros_like(mask,dtype=int);source[ca]=1;source[cb]=2
        np.savez(spec/'spec.npz',mask=mask[sl],s=source[sl],sink=target[sl],cut=[ii.min(),ii.max()+1,jj.min(),jj.max()+1])
        for i,j in zip(*np.where(target)):nodes.append([key,i,j,lon[i,j],lat[i,j]])
        specs.append(dict(key=key,region=region,species=sp,A=aa,B=bb,km=sep,target_cells=target.sum(),grid_cells=mask.sum(),n_transitions=len(z),snap_a=da[ca],snap_b=db[cb]))
        for row in z.itertuples():tr.append(dict(key=key,region=region,species=sp,year=row.season,p=row.p,next_share=row.next_share,total=row.total,next_total=row.next_total))
pd.DataFrame(specs).to_csv(out/'dyads.csv',index=False);pd.DataFrame(tr).to_csv(out/'transitions.csv',index=False)
pd.DataFrame(nodes,columns=['key','row','col','lon','lat']).to_csv(out/'historical_targets.csv',index=False)
pd.DataFrame(fail,columns=['region','key','years','targets','reason']).to_csv(out/'unsupported.csv',index=False)
print(pd.DataFrame(specs)[['key','region','target_cells','n_transitions']].to_string(index=False));print('exclusions',len(fail))
