from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
a=pd.read_csv(p/'signy_annual_diet.csv');m=pd.read_csv(p/'signy_matched.csv');f=pd.read_csv(p/'sensitivity_models.csv')
fig,ax=plt.subplots(1,3,figsize=(14,4))
ax[0].plot(a.season,a.krill_fraction*100,'o-',label='E. superba');ax[0].plot(a.season,a.fish_fraction*100,'s-',label='Fish');ax[0].set(xlabel='Breeding season start year',ylabel='Mean stomach mass fraction (%)',title='All 19 observed seasons');ax[0].legend(fontsize=8)
g=m.dropna(subset=['polynya_fraction']);ax[1].scatter(g.polynya_fraction*100,g.krill_fraction*100)
for r in g.itertuples():
 if r.krill_fraction<.9:ax[1].annotate(str(r.season),(r.polynya_fraction*100,r.krill_fraction*100),fontsize=8)
ax[1].set(xlabel='Winter coastal polynya fraction (%)',ylabel='E. superba mass fraction (%)',title='14 matched seasons (unadjusted points)')
f=f[f.response.eq('krill_fraction')&f.adjusted.eq(True)].sort_values('radius_km',ascending=False)
for i,r in enumerate(f.itertuples()):ax[2].errorbar(r.beta,i,xerr=[[r.beta-r.lower],[r.upper-r.beta]],fmt='o',capsize=4)
ax[2].axvline(0,color='gray',lw=1);ax[2].set(yticks=[0,1],yticklabels=['100 km main','25 km sensitivity'],xlabel='Diet percentage points per +1 pp polynya',title='Adjusted slope and 95% HAC interval',ylim=(-.6,1.6));fig.tight_layout(pad=1.5);fig.savefig(p/'signy_diet_polynya.png',dpi=180);plt.close(fig)
t=pd.read_csv(p.parent/'direct_diet_independent_20261120/primary_table_seasons.csv');e=pd.read_csv(p/'annual_environment.csv');v=t.merge(e[e.radius_km.eq(100)],left_on=['locality','season_start_year'],right_on=['site','season'],how='left',validate='one_to_one');v.to_csv(p/'other_site_table_exposure_support.csv',index=False,lineterminator='\n');print(v.groupby('locality').polynya_fraction.count().to_dict())
l=pd.read_csv(p/'leave_one_season_out.csv');print('LOO',l.beta.min(),l.beta.max(),(l.beta>0).sum(),len(l))
