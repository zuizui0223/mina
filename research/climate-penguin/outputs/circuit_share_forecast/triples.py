"""Use one fixed eligible three-site panel per region/species, chosen only by coverage."""
from pathlib import Path
import io,zipfile,itertools
import numpy as np,pandas as pd
from pyproj import Geod
from scipy.spatial import cKDTree
from scipy.ndimage import label
out=Path('outputs/circuit_share_forecast');cache=Path('work/circuit_share')
base=pd.read_csv('work/mina-sync/research/climate-penguin/outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv')
base=base[base.season.between(1992,2021)&base.method.isin(['ground','aerial','vhr','uav'])&base.n_methods.eq(1)&base['count'].ge(0)]
geod=Geod(ellps='WGS84')
grid=np.load(cache/'grid.npz');lon,lat=grid['lon'],grid['lat'];ocean=np.isfinite(np.load(cache/'sic_1991.npy'))
def xyz(x,y):
    a,b=np.radians(x),np.radians(y)
    return np.column_stack((np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)))
with zipfile.ZipFile('work/highice_prey/krillbase.zip') as wrap:
    with zipfile.ZipFile(io.BytesIO(wrap.read(wrap.namelist()[0]))) as z:k=pd.read_csv(z.open('krillbase_data.csv'),encoding='cp1252')
k=k[(k.SEASON<=1990)&k.RECORD_TYPE.eq('haul')&k.NUMBER_OF_KRILL_UNDER_1M2.gt(0)].dropna(subset=['LONGITUDE','LATITUDE'])
dis,idx=cKDTree(xyz(lon[ocean],lat[ocean])).query(xyz(k.LONGITUDE,k.LATITUDE))
prey=np.zeros_like(ocean);prey[tuple(np.argwhere(ocean)[idx[dis*6371<=25]].T)]=True
entries=[];runs=[]
for (region,species),s in base.groupby(['region','species_id']):
    sites={}
    for key,t in s.groupby('site_id'):
        t=t.sort_values('season').set_index('season',drop=False)
        valid=set(t.loc[t.season.shift(-1).sub(t.season).eq(1)&t.method.eq(t.method.shift(-1)),'season'])
        if len(valid)>=3: sites[key]=(t,valid)
    groups=[]
    for keys in itertools.combinations(sites,3):
        yrs=set.intersection(*(sites[a][1] for a in keys))
        if len(yrs)<3:continue
        points=[sites[a][0].iloc[0] for a in keys]
        gaps=[geod.inv(u.longitude,u.latitude,v.longitude,v.latitude)[2]/1000 for u,v in itertools.combinations(points,2)]
        if min(gaps)>=50 and max(gaps)<=300:groups.append((-len(yrs),keys,sorted(yrs),points))
    for _,keys,yrs,points in sorted(groups,key=lambda g:g[:2]):
        ds=np.stack([geod.inv(np.full(lon.shape,float(p.longitude)),np.full(lat.shape,float(p.latitude)),lon.astype(float),lat.astype(float))[2]/1000 for p in points])
        mask=ocean&(np.min(ds,axis=0)<=250); pos=[np.unravel_index(np.argmin(np.where(mask,d,np.inf)),mask.shape) for d in ds]
        connected=label(mask,np.ones((3,3)))[0];mask &= connected==connected[pos[0]]
        if not all(mask[node] and d[node]<=35 for node,d in zip(pos,ds)):continue
        sink=mask&prey&(ds.min(axis=0)>=25)&(ds.max(axis=0)<=200)
        for node in pos:sink[node]=False
        if not sink.any():continue
        group='_'.join((species,*keys));ii,jj=np.where(mask);cut=[ii.min(),ii.max()+1,jj.min(),jj.max()+1];i,j,k1,l=cut
        for n in [1,2]:
            name=f'tri_{group}_{n}';folder=cache/name;folder.mkdir(exist_ok=True);src=np.zeros_like(mask,int);src[pos[0]]=1;src[pos[n]]=2
            np.savez(folder/'spec.npz',mask=mask[i:j,k1:l],s=src[i:j,k1:l],sink=sink[i:j,k1:l],cut=cut)
            for yr in yrs:runs.append(dict(key=name,year=yr))
        for yr in yrs:
            current=np.array([sites[a][0].loc[yr,'count'] for a in keys]);following=np.array([sites[a][0].loc[yr+1,'count'] for a in keys])
            if not min(current.sum(),following.sum())>0:continue
            for n,a in enumerate(keys): entries.append(dict(group=group,region=region,species=species,year=yr,site=a,idx=n,p=current[n]/current.sum(),next_share=following[n]/following.sum(),total=current.sum(),next_total=following.sum(),target_cells=sink.sum()))
        break
pd.DataFrame(runs).to_csv(cache/'tri_runs.csv',index=False);pd.DataFrame(entries).to_csv(out/'three_colony_panel.csv',index=False)
print(pd.DataFrame(entries).groupby(['region','group']).year.nunique())
