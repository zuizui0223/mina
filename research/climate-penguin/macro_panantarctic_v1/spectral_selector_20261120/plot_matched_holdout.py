import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).parent
train=json.loads((ROOT/'matched_training_verdict.json').read_text())
test=json.loads((ROOT/'matched_holdout_verdict.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(10,4.7),layout='constrained')
labels=['Training OOF\nthreshold selection','2008-2012 fixed\nregion bootstrap','Same heldout data\nshared-scene blocks']
for ax,name,key,target in zip(axes,['Original-positive recovery','Sampled candidate-background rejection'],
    ['positive_recovery','candidate_background_rejection'],[.8,.95]):
    tr=train['diagnostic_positive_recovery' if key=='positive_recovery' else 'diagnostic_background_rejection']
    ax.scatter([0],[tr],color='#777777',s=50,zorder=3)
    for i,field in [(1,'rates'),(2,'shared_scene_block_rates')]:
        r=test[field][key];value=r['estimate']
        ax.errorbar([i],[value],yerr=np.array([[value-r['lower95']],[r['upper95']-value]]),fmt='o',capsize=4,color='#28638e')
    ax.axhline(target,linestyle='--',color='#b64542',lw=1.3,label=f'Fixed target {target:.0%}')
    ax.set(xticks=[0,1,2],xticklabels=labels,ylim=(0,1.03),title=name,ylabel='Site-weighted proportion')
    ax.tick_params(axis='x',labelsize=8);ax.spines[['right','top']].set_visible(False)
    ax.legend(loc='lower left',frameon=False,fontsize=9)
fig.suptitle('Historical method validation: fixed threshold; no L8 or isotope outcome',fontsize=11)
fig.savefig(ROOT/'matched_holdout.png',dpi=180,bbox_inches='tight')
fig.savefig(ROOT/'matched_holdout.svg',bbox_inches='tight')
svg=ROOT/'matched_holdout.svg';svg.write_text('\n'.join(s.rstrip() for s in svg.read_text().splitlines())+'\n',encoding='utf-8',newline='\n')
