from run import HERE
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d=pd.read_csv(HERE/'coefficients.csv');o=pd.read_csv(HERE/'region_omissions.csv')
fig,axes=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1,1.5]})
labels={'P0':'Preceding winter','P1':'Following winter','P0_minus_P1':'Preceding minus following'}
q=d[d.model.eq('Mjoint')].reset_index(drop=True)
ax=axes[0]
for i,r in q.iterrows():
    ax.errorbar(r.beta_per_10pp,i,xerr=[[r.beta_per_10pp-r.lower],[r.upper-r.beta_per_10pp]],fmt='o',color='#206b8a',capsize=4)
ax.set_yticks(range(len(q)),[labels[t] for t in q.term]);ax.invert_yaxis();ax.axvline(0,color='grey',linestyle='--');ax.set_title('Joint model: 358 colony-seasons\n95% region-cluster t intervals')
ax.set_xlabel('Optical delta15N proxy change per +10 pp (per mil)')
ax=axes[1];q=o[o.term.eq('P0_minus_P1')].sort_values('beta_per_10pp')
ax.plot(q.beta_per_10pp,range(len(q)),'o',color='#d18e00');ax.set_yticks(range(len(q)),q.omitted_region,fontsize=8);ax.axvline(0,color='grey',linestyle='--');ax.set_title('Leave one region out\nPreceding-minus-following point estimates')
ax.set_xlabel('Coefficient contrast per +10 pp (per mil)')
fig.tight_layout();fig.savefig(HERE/'temporal_contrast.png',dpi=180)
