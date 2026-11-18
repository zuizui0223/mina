"""Rebuild the paired external season contrasts from published panels and tables.
Run from the outer mina workspace after ice_sites.py. Sources and digitization in REPORT.md.
"""
from pathlib import Path
from itertools import permutations, product
from zipfile import ZipFile
import numpy as np
import pandas as pd
from pyproj import Geod
from scipy.stats import t as student_t

out=Path('outputs/cape_diet_replication')
ice=pd.read_csv(out/'historical_ice.csv')
signy=pd.read_csv('outputs/diet_niche_manuscript_v1/Figure_1_data.csv')
# Polito Fig 1 top panels, rendered at 5x in clip (126,284,499,465).
# Marker centres in pixels. y=831 at 0%, y=71 at 100%.
def mass(centres):
    return np.maximum(0,(831-np.array(centres))/7.6)
def share(fish,krill):
    return 100*np.array(fish)/(np.array(fish)+np.array(krill))
def pair(site,years,other,g,c,gn,cn):
    return pd.DataFrame(dict(site=site,start_year=years,other=other,gentoo=g,comparison=c,n_gentoo=gn,n_other=cn))
cape=pair('Cape_Shirreff',range(2006,2011),'Chinstrap',share(mass([679,707,597,643,741]),mass([223,195,313,260,165])),share(mass([831,828,831,824,830]),mass([71,74,78,79,72])),np.nan,np.nan)
sp=pair('Stranger_Point',range(2007,2011),'Adelie',share([.09,.77,1.56,1.49],[99.87,99.20,98.37,98.38]),share([0,.03,0,.11],[99.99,99.92,99.91,99.83]),[25,24,10,24],[30,25,25,25])
data=pd.concat([cape,sp]).merge(ice,on=['site','start_year'],validate='one_to_one')
data['gap']=data.gentoo-data.comparison
data.to_csv(out/'paired_seasons.csv',index=False)
def slope(x,y):
    x=np.array(x);return 10*np.dot(x-x.mean(),y)/np.sum((x-x.mean())**2)
rows=[]
for site,g in data.groupby('site'):
    x=g.sic.to_numpy();y=g.gap.to_numpy();s=slope(x,y);r=np.corrcoef(x,y)[0,1]
    p=np.mean([abs(slope(x,z))>=abs(s)-1e-10 for z in permutations(y)])
    xc=x-x.mean(); resid=y-y.mean()-s*xc/10; lev=1/len(x)+xc**2/(xc@xc)
    se=10*np.sqrt(np.sum((xc*resid/(1-lev))**2))/(xc@xc)
    half=student_t.ppf(.975,len(x)-2)*se
    loo=[slope(np.delete(x,i),np.delete(y,i)) for i in range(len(x))]
    hist=ice[ice.site.eq(site)].sic;q=hist.quantile(.75);ref=hist.mean()
    rows.append(dict(site=site,n=len(y),sic_min=min(x),sic_max=max(x),local_q75=q,n_high=sum(x>=q),hist_ref=ref,gentoo_slope=slope(x,g.gentoo),other_slope=slope(x,g.comparison),gap_slope=s,r=r,p_exact=p,hc3_low=s-half,hc3_high=s+half,loo_min=min(loo),loo_max=max(loo),signy_same_pair_slope=slope(signy.sic_aug_nov,100*(signy.Gentoo-signy[g.other.iloc[0]]))))
res=pd.DataFrame(rows);res.to_csv(out/'slope_checks.csv',index=False)
sc=[]
for row in rows:
 for loss in [5,10,20]:
    a=row['hist_ref'];b=a-loss;ok=row['sic_min']<=b<=a<=row['sic_max']
    sc.append(dict(site=row['site'],baseline_sic=a,loss_pp=loss,target_sic=b,in_domain=ok,change_pp=-row['gap_slope']*loss/10 if ok else np.nan,coef_low=-row['hc3_high']*loss/10 if ok else np.nan,coef_high=-row['hc3_low']*loss/10 if ok else np.nan))
pd.DataFrame(sc).to_csv(out/'scenario.csv',index=False)
z=ZipFile('work/cape_diet_replication/telemetry_s1')
gps=pd.read_csv(z.open('Data/satellite telemetry.csv'),low_memory=False)
gps['date']=pd.to_datetime(gps.Date,format='mixed',errors='coerce')
sub=gps[gps.Site.eq('CS') & gps.Spp.isin(['CHPE','GEPE']) & gps.date.dt.month.isin([1,2]) & gps.date.dt.year.between(2007,2011)].dropna(subset=['Latitude','Longitude'])
sub.groupby([sub.date.dt.year,'Spp','Type']).agg(fixes=('Deployment','size'),deployments=('Deployment','nunique'),days=('date','nunique')).to_csv(out/'telemetry.csv')
k=pd.read_csv(z.open('Data/krill_density.csv')).dropna(subset=['Longitude','Latitude','gm2']); k=k[k.gm2>=0].copy()
k['km']=Geod(ellps='WGS84').inv(k.Longitude,k.Latitude,np.full(len(k),-60.7874),np.full(len(k),-62.4575))[2]/1000
k=k[k.km<100].copy();k['x']=np.floor(k.Longitude*4);k['y']=np.floor(k.Latitude*4)
m=k.groupby(['x','y','Year']).gm2.mean().unstack('Year').dropna()
a=k.groupby('Year').agg(segments=('gm2','size'),segment_mean_gm2=('gm2','mean'));a['common_cells']=len(m);a['balanced_cell_mean_gm2']=m.mean();a['start_year']=a.index-1
a.reset_index().merge(data[data.site.eq('Cape_Shirreff')][['start_year','sic','gap']],on='start_year').to_csv(out/'krill_diet_ice.csv',index=False)
print(res.round(3).to_string(index=False)); print(pd.DataFrame(sc).round(2));print(a.round(2))
