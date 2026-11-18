from pathlib import Path
import hashlib,json,zipfile
import pandas as pd,numpy as np
from matplotlib import pyplot as plt
out=Path('outputs/cape_diet_replication')
data=pd.read_csv(out/'paired_seasons.csv');s=pd.read_csv('outputs/diet_niche_manuscript_v1/Figure_1_data.csv')
fig,axes=plt.subplots(1,3,figsize=(11,3.5),sharex=True,layout='constrained')
for ax,(name,x,y,color) in zip(axes,[('Signy: Gentoo - Chinstrap',s.sic_aug_nov,100*(s.Gentoo-s.Chinstrap),'#0072B2')]+[(a+': G - '+g.other.iloc[0],g.sic,g.gap,'#009E73') for a,g in data.groupby('site')]):
 ax.scatter(x,y,color=color);xp=np.array([min(x),max(x)]);ax.plot(xp,np.polyval(np.polyfit(x,y,1),xp),color=color);ax.axhline(0,color='.75',lw=.6);ax.set(xlabel='Aug-Nov sea-ice concentration (%)',title=name.replace('_',' '),xlim=(0,70));ax.tick_params(labelsize=9)
axes[0].set_ylabel('Species gap in fish share (pp)');fig.suptitle('Paired breeding seasons; local fits and separate vertical scales')
fig.savefig(out/'paired_slopes.png',dpi=170);plt.close(fig)
raw=Path('work/cape_diet_replication');sources={'paper.pdf':'https://www.int-res.com/articles/meps_oa/m519p221.pdf','stranger.pdf':'https://sedici.unlp.edu.ar/bitstream/handle/10915/84998/Documento_completo.pdf?sequence=1','adelie.pdf':'https://sedici.unlp.edu.ar/bitstream/handle/10915/133294/Documento_completo.pdf?sequence=1','king.pdf':'https://repository.library.noaa.gov/view/noaa/55536/noaa_55536_DS1.pdf','telemetry_s1':'https://journals.plos.org/plosone/article/file?type=supplementary&id=info:doi/10.1371/journal.pone.0170132.s001'}
(out/'source_receipt.json').write_text(json.dumps({f:{'url':url,'sha256':hashlib.sha256((raw/f).read_bytes()).hexdigest()} for f,url in sources.items()},indent=2),encoding='utf-8')
u=pd.read_csv(zipfile.ZipFile(raw/'telemetry_s1').open('Data/satellite telemetry.csv'),low_memory=False);u['day']=pd.to_datetime(u.Date,format='mixed',errors='coerce')
u=u[u.Site.eq('CS') & u.Spp.isin(['GEPE','CHPE']) & u.day.dt.month.isin([1,2]) & u.day.dt.year.between(2009,2011) & u.Type.eq('PTT')].dropna(subset=['Latitude','Longitude'])
print('paired PTT days',u.groupby('day').Spp.nunique().eq(2).groupby(lambda d:d.year).sum().to_dict())
t=pd.read_csv(out/'cmip6_regional_scenarios.csv');print(t.groupby('site').adjusted_sic.min())
