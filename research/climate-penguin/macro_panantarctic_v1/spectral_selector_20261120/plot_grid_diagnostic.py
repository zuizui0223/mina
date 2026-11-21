from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd

ROOT=Path(__file__).parent
d=pd.read_csv(ROOT/'historical_sr_grid_site_medians.csv').dropna(subset=['red_area_minus_point'])
fig,axes=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
ax=axes[0]
for x in [-30,0,30]:ax.axvline(x,color='#a2a7ab',lw=1)
for y in [-30,0,30]:ax.axhline(y,color='#a2a7ab',lw=1)
ax.scatter([-15,15,-15,15],[-15,-15,15,15],s=35,c='#28638e',label='Native pixel centers')
ax.add_patch(Rectangle((-15,-15),30,30,facecolor='#f2a541',alpha=.25,edgecolor='#a56000',lw=2,label='Assumed centered footprint'))
ax.scatter([0],[0],s=60,c='#be3f45',marker='x',label='Original POINT')
ax.set(xlim=(-36,36),ylim=(-36,36),aspect='equal',xlabel='Easting relative to original POINT (m)',ylabel='Northing relative to original POINT (m)',title='A. Half-grid case: four contributing pixels')
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.16),fontsize=8,frameon=False)
ax=axes[1]
d=d.sort_values('red_area_minus_point')
ax.barh(d.site_id,d.red_area_minus_point,color='#28638e')
ax.set(xlabel='Median absolute red-SR difference',title='B. Area average vs point extraction\n635 paired records; 11 sites')
ax.text(.99,.02,'HASW: no valid paired records\nEach bar is one site, not a significance test',transform=ax.transAxes,ha='right',va='bottom',fontsize=8)
ax.spines[['top','right']].set_visible(False)
fig.savefig(ROOT/'grid_diagnostic.png',dpi=180,bbox_inches='tight')
fig.savefig(ROOT/'grid_diagnostic.svg',bbox_inches='tight')
svg=ROOT/'grid_diagnostic.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
