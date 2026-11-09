from pathlib import Path
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
out=Path(__file__).resolve().parent
s=pd.read_csv(out/'scenarios.csv')
o=pd.read_csv(out/'observed_support.csv')
checks=pd.read_csv(out/'native_check.csv')
keys=['pair','model','ssp','period','beta']
p=s.pivot(index=keys,columns='mode',values='absolute_log_contrast').reset_index()
for name in ['spatial','equal_mean']:p[name]=100*np.expm1(p[name])
p=p.merge(s[s['mode'].eq('spatial')][keys+['clipped_fraction','relative_A_to_B_pct']],on=keys,validate='one_to_one')
h=o.pivot(index=['pair','year','beta'],columns='mode',values='absolute_log_contrast').reset_index()
for name in ['observed_pattern','matched_mean']:h[name]=100*np.expm1(h[name])
rows=[]
for beta in [2,-2]:
    future=p[p.beta==beta]
    history=h[h.beta==beta]
    for label,frame,a,b in [('all future',future,'spatial','equal_mean'),('future <=10% clipped',future[future.clipped_fraction<=.1],'spatial','equal_mean'),('observed 2015-20',history,'observed_pattern','matched_mean')]:
        rows.append(dict(beta=beta,subset=label,n=len(frame),median_pattern_asymmetry_pct=frame[a].median(),median_control_pct=frame[b].median(),greater=int((frame[a]>frame[b]+1e-6).sum()),tie=int(np.isclose(frame[a],frame[b],atol=1e-6,rtol=0).sum())))
summary=pd.DataFrame(rows);summary.to_csv(out/'summary.csv',index=False)
a=p[p.beta==2].copy();a['direction']=np.where(a.relative_A_to_B_pct>1e-6,1,np.where(a.relative_A_to_B_pct < -1e-6,-1,0))
agreement=a.groupby(['pair','ssp','period']).direction.agg(lambda z:abs(z.sum())==3)
print(summary.round(3).to_string(index=False));print('sign agreement',agreement.sum(),len(agreement))
assert len(s)==336 and len(o)==168 and len(checks)==357 and checks.max_abs_error.max()<1e-7
print('native max',checks.max_abs_error.max())
fig,axes=plt.subplots(1,2,figsize=(10.3,4.1),layout='constrained')
for ax,frame,x,y,title in [(axes[0],h[h.beta==2],'matched_mean','observed_pattern','Satellite ice, 2015–2020'),(axes[1],a,'equal_mean','spatial','CMIP6 ice-change patterns')]:
    for name,g in frame.groupby('model') if 'model' in frame else [('Observed seasons',frame)]:
        ax.scatter(g[x],g[y],s=22,alpha=.65,label=name)
    lim=max(frame[x].max(),frame[y].max())*1.04
    ax.plot([0,lim],[0,lim],ls=':',color='.4');ax.set(xlim=(-1,lim),ylim=(-1,lim),aspect='equal',title=title,xlabel='Equal-mean control: asymmetry (%)',ylabel='Spatial ice pattern: asymmetry (%)');ax.legend(fontsize=8,frameon=False)
fig.savefig(out/'access_contrast.png',dpi=190)
