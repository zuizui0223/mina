from pathlib import Path
import pandas as pd,numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Patch
from pyproj import Geod
out=Path(__file__).resolve().parent
d=pd.read_csv(out/'primary_cases.csv');a=pd.read_csv(out/'model_agreement.csv')
sites=pd.read_csv('work/mina-sync/research/climate-penguin/outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv').drop_duplicates('site_id').set_index('site_id')
order=d.pair.drop_duplicates().tolist()
columns=[(s,p,m) for s in ['ssp245','ssp585'] for p in [2041,2081] for m in ['ACCESS-CM2','BCC-CSM2-MR','CESM2']]
fig,axes=plt.subplots(1,2,figsize=(13,5),layout='constrained')
for ax,ep,title in zip(axes,['level','gain'],['Higher future access','Larger change from historical access']):
    mat=np.zeros((len(order),len(columns)))
    for iy,pair in enumerate(order):
        g=d.query('pair==@pair').set_index(['ssp','period','model']); A,B=pair.split('-')
        for ix,key in enumerate(columns):
            row=g.loc[key];after=row['moved_'+ep+'_winner'];mat[iy,ix]={A:-1,B:1,'tie':0}[after]
            if row[ep+'_reversed']:ax.text(ix,iy,'×',va='center',ha='center',fontsize=13,color='black')
    ax.imshow(mat,cmap=ListedColormap(['#78afd0','#eeeeee','#edac69']),vmin=-1,vmax=1,aspect='auto')
    ax.set_yticks(range(len(order)),order);ax.set_xticks(range(12),['A','B','C']*4);ax.set_title(title)
    for x in [2.5,5.5,8.5]:ax.axvline(x,lw=1.5,color='white')
    ax.set_xlabel('SSP2-4.5: mid / late       SSP5-8.5: mid / late')
fig.suptitle('Southwest prey shift at regional median distance • × = reversal from fixed prey')
fig.legend(handles=[Patch(color='#78afd0',label='First colony'),Patch(color='#edac69',label='Second colony'),Patch(color='#eeeeee',label='Within 1%')],loc='outside lower center',ncol=3,frameon=False)
fig.savefig(out/'pair_winners.png',dpi=170);plt.close(fig)
used=sites.loc[sorted(set(d.A)|set(d.B))];lons,lats=used.longitude.values,used.latitude.values
geo=Geod(ellps='WGS84')
maxkm=max(geo.inv(x,y,xx,yy)[2]/1000 for x,y in zip(lons,lats) for xx,yy in zip(lons,lats))
print('sites',len(used),'span',maxkm,'native err',pd.read_csv(out/'native_check.csv').max_abs_error.max())
summary=[]
for pair,g in d.groupby('pair'):
    A,B=pair.split('-');summ=dict(pair=pair,A_name=sites.loc[A,'site_name'],B_name=sites.loc[B,'site_name'])
    for ep in ['level','gain']:
        fr=g['fixed_'+ep+'_winner'];to=g['moved_'+ep+'_winner']
        for name,count in [('fixed_A',sum(fr==A)),('fixed_B',sum(fr==B)),('moved_A',sum(to==A)),('moved_B',sum(to==B)),('moved_tie',sum(to=='tie')),('A_to_B',sum((fr==A)&(to==B))),('B_to_A',sum((fr==B)&(to==A)))]:summ[ep+'_'+name]=count
    summary.append(summ)
pd.DataFrame(summary).to_csv(out/'named_winners.csv',index=False)
