from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run(out):
    d=pd.read_csv(out/'annual_distances.csv');d=d[(d.variant=='full')&(d.pair=='Gentoo-vs-others')]
    fig,axes=plt.subplots(1,3,figsize=(13,4.6),layout='constrained')
    labels=[('fish','Fish / crustacean composition','Absolute fish-share gap'),('size_assumed_common_scale','Carapace: scale assumption only','Wasserstein distance (source numeric units)'),('stage_labels','Recorded maturity labels','Total variation distance')]
    for ax,(m,title,ylabel) in zip(axes,labels):
        g=d[d.metric==m].sort_values('year');x=g.sic_aug_nov.to_numpy();y=g.distance.to_numpy()
        ax.scatter(x,y,c=g.year,cmap='viridis',s=46)
        for r in g.itertuples():ax.annotate(str(r.year)[2:],(r.sic_aug_nov,r.distance),xytext=(4,4),textcoords='offset points',fontsize=8)
        xx=np.array([x.min(),x.max()]);ax.plot(xx,np.polyval(np.polyfit(x,y,1),xx),color='gray',lw=1)
        ax.set_title(title+'\nr = %.3f'%np.corrcoef(x,y)[0,1],fontsize=11);ax.set_xlabel('Prior Aug–Nov sea-ice concentration (%)');ax.set_ylabel(ylabel);ax.grid(alpha=.15);ax.margins(x=.12,y=.12)
        if m.startswith('size'):ax.set_facecolor('#fff8e9')
    fig.suptitle('Signy, 2001–2009: Gentoo distance from the other two species\nEach stomach has equal weight; nine years, one island. Numbers label season start years.',fontsize=12)
    fig.savefig(out/'multiscale_distances.png',dpi=180)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
