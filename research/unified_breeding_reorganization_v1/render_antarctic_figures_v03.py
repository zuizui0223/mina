"""Six Antarctic integrated manuscript figures; pinned result receipts, no ecological refit."""
import argparse, hashlib, json, csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from PIL import Image
import xml.etree.ElementTree as ET
ROOT=Path(__file__).parent
BLUE='#176C80'; ORANGE='#B96A38'; GREEN='#52794C'; GREY='#8D9BA2'; DARK='#253942'; PALE='#C9D5D9'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':DARK,'text.color':DARK,'xtick.color':DARK,'ytick.color':DARK,'axes.titlecolor':DARK,'svg.fonttype':'none','savefig.dpi':300})
H=['long_parent23','long_complete17','short_parent15_100','short_complete9_100']
HL=['Long 23','Long 17','Short 15','Short 9']
def head(ax,t): ax.set_title(t,loc='left',fontweight='bold',fontsize=10,pad=8)
def zero(ax,axis='y'): (ax.axhline if axis=='y' else ax.axvline)(0,color=GREY,lw=.8,zorder=0)
def dotrange(ax,v,lo,hi,y,color,marker='o'):
    ax.hlines(y,lo,hi,color=color,lw=1.5)
    ax.scatter(v,y,color=color,marker=marker,s=31,zorder=3)
def labels(ax,bars,fmt='{:.2f}'):
    for b in bars:
        v=b.get_height()
        ax.annotate(fmt.format(v),(b.get_x()+b.get_width()/2,v),xytext=(0,4 if v>=0 else -5),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=8)
def save(f,name,out,qa):
    rec={}
    for ext in ['png','svg']:
        p=out/(name+'.'+ext);f.savefig(p,bbox_inches='tight',pad_inches=.16,facecolor='white')
        if ext=='png':
            with Image.open(p) as im: im.verify()
            with Image.open(p) as im: rec['pixels']=list(im.size)
        else: ET.parse(p)
        assert p.stat().st_size>4000
        rec[ext+'_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    qa[name]=rec;plt.close(f)
def title(f,t): f.suptitle(t,fontweight='bold',fontsize=12)
def fig1(d,out,qa):
    a=d['physical'];f,ax=plt.subplots(1,3,figsize=(10.8,3.8),layout='constrained')
    head(ax[0],'A  Physical variation (588 sites)')
    pc=a['pca_variance'];labels(ax[0],ax[0].bar(['Temperature–ice','Salinity axis','Remaining'],[*pc,100-sum(pc)],color=[BLUE,ORANGE,PALE]),'{:.1f}%')
    ax[0].set_ylim(0,74);ax[0].set_ylabel('Standardized variance (%)');ax[0].tick_params(axis='x',labelrotation=18)
    head(ax[1],'B  Winter polynya (595 sites)')
    labels(ax[1],ax[1].bar(['2004–10','2013–20'],[a['early'],a['late']],color=[GREY,BLUE]),'{:.2f}%')
    ax[1].set_ylim(0,4.8);ax[1].set_ylabel('Mean coastal-polynya fraction (%)')
    ax[1].text(.5,.96,'100 km; 15 complete winters',ha='center',va='top',transform=ax[1].transAxes,fontsize=8)
    head(ax[2],'C  Change depends on weighting')
    labels(ax[2],ax[2].bar(['595 sites','18 regions','43 blocks'],[a['site_delta'],a['region_delta'],a['block_delta']],color=[BLUE,ORANGE,GREY]),'{:+.2f}')
    zero(ax[2]);ax[2].set_ylim(-.23,.85);ax[2].set_ylabel('Period difference (percentage points)')
    ax[2].text(.5,.95,'408/595 sites increased',ha='center',va='top',transform=ax[2].transAxes,fontsize=8)
    title(f,'Near-colony physical conditions vary across variables and geographic weights');save(f,'A1_physical_context',out,qa)
def fig2(d,out,qa):
    hist={z['name']:z for z in d['historical']};f,axs=plt.subplots(2,2,figsize=(9.2,6.7),layout='constrained')
    ax=axs[0,0];head(ax,'A  Effective breeding-site number')
    for i,k in enumerate(H):
        z=hist[k]['composition'];ax.plot([0,1],[z['Neff0'],z['Neff1']],marker='o',color=[BLUE,ORANGE,BLUE,ORANGE][i],ls='-' if i<2 else '--',label=HL[i])
    ax.set_xticks([0,1],['Earlier','Recent']);ax.set_ylabel('Inverse Simpson effective number');ax.legend(frameon=False,ncol=2,fontsize=8);ax.set_ylim(2,8)
    def decomp(ax,ks,lab,var,yl):
        for i,key in enumerate(['local','redistribution']):
            ax.bar(np.arange(len(ks))+(-.18 if i==0 else .18),[hist[k]['exposure'][var][key] for k in ks],.33,color=[GREY,BLUE][i],label=['Location term','Reweighting term'][i])
        ax.scatter(np.arange(len(ks)),[hist[k]['exposure'][var]['total'] for k in ks],marker='D',facecolors='white',edgecolors=DARK,s=30,zorder=5,label='Total')
        zero(ax);ax.set_xticks(range(len(ks)),lab);ax.set_ylabel(yl)
    ax=axs[0,1];head(ax,'B  Sea-ice exposure decomposition');decomp(ax,H,HL,'sic_pp','Change (pp)');ax.legend(frameon=False,fontsize=8)
    ax=axs[1,0];head(ax,'C  Salinity: complete rosters');decomp(ax,[H[1],H[3]],[HL[1],HL[3]],'salinity','Change (practical salinity)')
    ax=axs[1,1];head(ax,'D  Polynya: dependence on radius');decomp(ax,['short_parent15_100','short_complete9_100','short_parent15_25','short_complete9_25'],['15 / 100 km','9 / 100 km','15 / 25 km','9 / 25 km'],'polynya_pp','Change (pp)');ax.tick_params(axis='x',labelrotation=15)
    for z in d['historical']:
        for v in z['exposure'].values():assert abs(v['local']+v['redistribution']-v['total'])<1e-10
    title(f,'Historical allocation changes exposure independently of concentration');save(f,'A2_historical_allocation',out,qa)
def fig3(d,rows,out,qa):
    f,axs=plt.subplots(2,2,figsize=(10,6.8),layout='constrained',sharex=True)
    pairs=[('ssp245','2041-2060'),('ssp245','2081-2100'),('ssp585','2041-2060'),('ssp585','2081-2100')]
    idx={(q['cohort'],q['scenario'],q['period'],q['variable']):q for q in rows};assert len(idx)==32
    for i,var in enumerate(['siconc','sos']):
        for j,(names,t) in enumerate([(['long_parent23_all','long_complete17_all'],'Long-period allocation'),(['short_parent15_all','short_complete9_all'],'Short-period allocation')]):
            ax=axs[i,j];head(ax,chr(65+i*2+j)+'  '+t)
            for k,name in enumerate(names):
                col=[BLUE,ORANGE][k]
                for x,(ex,period) in enumerate(pairs):
                    z=idx[name,ex,period,var];md=np.array([float(z[k]) for k in ['ACCESS_difference','BCC_difference','CESM2_difference']]);m=float(z['late_weights'])-float(z['early_weights']);assert abs(md.mean()-m)<3e-9
                    xx=x+(-.17 if k==0 else .17);ax.vlines(xx,md.min(),md.max(),color=col,lw=1.4,alpha=.65)
                    for l,marker in enumerate(['^','s','v']):ax.scatter(xx+[-.045,0,.045][l],md[l],marker=marker,facecolors='white',edgecolors=col,s=24,zorder=3)
                    ax.scatter(xx,m,color=col,s=34,zorder=4)
            zero(ax);ax.set_xlim(-.5,3.5);ax.set_xticks(range(4),['2-4.5\nMid','2-4.5\nLate','5-8.5\nMid','5-8.5\nLate'])
            ax.set_ylabel('Recent − early weight effect\n'+('Sea ice (pp)' if i==0 else 'Salinity (model units)'))
    for i in range(2):
        lo=min(axs[i,j].get_ylim()[0] for j in range(2));hi=max(axs[i,j].get_ylim()[1] for j in range(2))
        for j in range(2):axs[i,j].set_ylim(lo,hi)
    f.legend(handles=[Patch(facecolor=BLUE,label='Parent roster (23 / 15)'),Patch(facecolor=ORANGE,label='Complete roster (17 / 9)'),Line2D([0],[0],marker='o',color=DARK,ls='',label='Three-model mean'),Line2D([0],[0],marker='^',markerfacecolor='white',color=DARK,ls='',label='ACCESS-CM2'),Line2D([0],[0],marker='s',markerfacecolor='white',color=DARK,ls='',label='BCC-CSM2-MR'),Line2D([0],[0],marker='v',markerfacecolor='white',color=DARK,ls='',label='CESM2')],loc='outside lower center',ncol=3,frameon=False,fontsize=8)
    title(f,'Historical reweighting does not guarantee reduced future physical exposure');save(f,'A3_future_fixed_allocation',out,qa)
def fig4(d,out,qa):
    f,axs=plt.subplots(2,2,figsize=(10,7.1),layout='constrained')
    ax=axs[0,0];head(ax,'A  Optical isotope proxy (425 informative records)')
    for i,z in enumerate(d['optical']):dotrange(ax,z['beta'],z['lower'],z['upper'],i,BLUE if z['model']=='M_P' else ORANGE)
    ax.set_yticks(range(4),['P / PLSR','P / R1000','P + S / PLSR','P + S / R1000']);ax.invert_yaxis();zero(ax,'x');ax.set_xlabel('δ¹⁵N proxy change (‰ per 10 pp polynya)');ax.text(.98,.04,'CV3 95% intervals; same optical source',transform=ax.transAxes,ha='right',fontsize=7.5)
    ax=axs[0,1];head(ax,'B  Adélie reproductive-stage associations')
    for i,z in enumerate(d['productivity']):
        dotrange(ax,z['time'],*z['time_range'],i-.12,GREY,'s');dotrange(ax,z['adjusted'],*z['adjusted_range'],i+.12,BLUE)
    ax.set_yticks(range(4),['Admiralty Bay (14)','Palmer (15)','Signy (13)','Pointe Géologie (15)']);ax.invert_yaxis();zero(ax,'x');ax.set_xlabel('Offspring / nesting female per 1 pp P100');ax.legend(handles=[Line2D([0],[0],marker='s',color=GREY,label='Time-adjusted'),Line2D([0],[0],marker='o',color=BLUE,label='Hydro-adjusted')],frameon=False,fontsize=7.5)
    ax=axs[1,0];head(ax,'C  Optical–nest overlap by season')
    z=d['optical_support']['annual'];x=np.arange(len(z));ax.bar(x,[q['optical_rows'] for q in z],color=PALE,label='Optical');ax.bar(x,[q['matched_rows'] for q in z],color=BLUE,label='Matched nests');ax.set_xticks(x,[q['season'] for q in z],rotation=25);ax.set_ylabel('Site-seasons');ax.legend(frameon=False,fontsize=8)
    ax=axs[1,1];head(ax,'D  No multi-site temporal bridge')
    z=d['optical_support']['windows'];x=np.arange(len(z));ax.bar(x,[q['sites'] for q in z],color=BLUE);ax.axhline(3,color=GREY,ls='--',lw=1,label='Minimum site support (3)');ax.set_xticks(x,[str(q['start'])[-2:]+'–'+str(q['end'])[-2:] for q in z],rotation=25);ax.set_ylim(0,3.7);ax.set_ylabel('Same-method matched sites');ax.legend(frameon=False,fontsize=8);ax.text(.5,.69,'Also require ≥2 regions; all windows fail',transform=ax.transAxes,ha='center',fontsize=8)
    title(f,'Marine biological associations differ among outcomes and locations');save(f,'A4_biological_response',out,qa)
def fig5(d,out,qa):
    f,axs=plt.subplots(2,2,figsize=(9.3,6.8),layout='constrained');keys=['fur','elephant','weddell','Adelie','Chinstrap','Gentoo'];names=['Fur seal','Elephant seal','Weddell seal','Adélie','Chinstrap','Gentoo']
    ax=axs[0,0];head(ax,'A  Signy: matched-summer count changes')
    for i,k in enumerate(keys):
        z=d['signy'][k];v=100*(z['count_ratio']-1);a,b=100*(np.array(z['loo_ranges']['count_ratio'])-1);dotrange(ax,v,a,b,i,BLUE if i<3 else ORANGE)
    ax.set_yticks(range(6),names);ax.invert_yaxis();zero(ax,'x');ax.set_xlabel('Change in mean monitored count (%)')
    ax=axs[0,1];head(ax,'B  Signy: signed concentration changes')
    for i,k in enumerate(keys):
        z=d['signy'][k]
        if 'delta_H' in z:dotrange(ax,z['delta_H'],*z['loo_ranges']['delta_H'],i,BLUE if i<3 else ORANGE)
        else:ax.text(0,i,'Not available',va='center',fontsize=8,color=GREY)
    ax.set_yticks(range(6),names);ax.invert_yaxis();zero(ax,'x');ax.set_xlabel('Change in Simpson H')
    ax=axs[1,0];head(ax,'C  Ross: different recovery summaries')
    a=d['ross'];v=100*np.array([a['aggregate_restoration'],a['six_state_restoration'],a['three_state_restoration']]);labels(ax,ax.bar(['Aggregate\nloss regained','Six-component\nconfiguration','Three-colony\nconfiguration'],v,color=[BLUE,ORANGE,ORANGE]),'{:.1f}%');ax.set_ylim(0,114);ax.set_ylabel('Recovery measure (%)')
    ax=axs[1,1];head(ax,'D  Bird Island: a growth contrast')
    a=d['bird'];v=[100*(a['last_total']/a['first_total']-1),100*(a['last_neff']/a['first_neff']-1)];labels(ax,ax.bar(['Breeding pairs','Effective number'],v,color=[BLUE,ORANGE]),'{:+.1f}%');ax.set_ylim(0,61);ax.set_ylabel('2003–2024 endpoint change (%)');ax.text(.5,.96,'Effective-number trend is not robust\nto one-season deletion',ha='center',va='top',transform=ax.transAxes,fontsize=8)
    title(f,'Numerical trajectories do not determine spatial configuration');save(f,'A5_vertebrate_allocation',out,qa)
def fig6(d,out,qa):
    f,axs=plt.subplots(2,2,figsize=(9.8,7),layout='constrained')
    ax=axs[0,0];head(ax,'A  Palmer: observed vs available cover')
    z=d['palmer'];x=[q['reference'] for q in z];y=[q['observed'] for q in z];ax.plot([0,43],[0,43],ls='--',color=GREY,lw=1);ax.scatter(x,y,color=GREEN,s=30);ax.set_xlim(-1,44);ax.set_ylim(-1,44)
    for a,b,k in zip(x,y,z):
        if k['site'] in ['Humb','KCove','Torg','ShortW','BonPt','AmslE']:ax.annotate(k['site'],(a,b),xytext=(3,4),textcoords='offset points',fontsize=7)
    ax.set_xlabel('Terrain-matched mapped overlap (%)');ax.set_ylabel('Observed detection overlap (%)')
    ax=axs[0,1];head(ax,'B  Palmer: detected-use strata (20 m)')
    for i,q in enumerate(d['palmer_tiles']):ax.plot([0,1,2],[q['undetected'],q['low'],q['high']],marker=['o','s','^'][i],color=[DARK,GREEN,ORANGE][i],label=q['class'])
    ax.set_xticks([0,1,2],['No detection','Low use','High use']);ax.set_ylabel('Mapped cover (%)');ax.legend(frameon=False,fontsize=8)
    ax=axs[1,0];head(ax,'C  Shirley: historical colony status')
    z=d['shirley'];labels(ax,ax.bar(['Extant','Relic minus\nextant','Maximum minus\nextant'],[q['cover'] for q in z],color=[GREY,GREEN,GREY]),'{:.2f}%');ax.set_ylim(0,4.3);ax.set_ylabel('Later mapped vegetation overlap (%)');ax.text(.5,.95,'Relic positives form one 50-m cluster',ha='center',va='top',transform=ax.transAxes,fontsize=8)
    ax=axs[1,1];head(ax,'D  Broad-scale vegetation association')
    z=d['vegetation']
    for i,q in enumerate(z):dotrange(ax,q['slope'],*q['range'],i,GREEN)
    ax.set_yticks(range(3),[q['species']+' ('+str(q['sites'])+' sites)' for q in z]);ax.invert_yaxis();zero(ax,'x');ax.set_xlabel('Regional slope: log nest-count trend\nper log mapped area');ax.text(.98,.04,'Block-resampling ranges; no causal effects',ha='right',transform=ax.transAxes,fontsize=7.5)
    title(f,'Animal use and mapped vegetation co-occur, but plant change is unmeasured');save(f,'A6_terrestrial_overlap',out,qa)
def main():
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args();out=args.out;out.mkdir(parents=True,exist_ok=True)
    ip=ROOT/'ANTARCTIC_MAIN_FIGURE_INPUTS_V0_3.json';fp=ROOT/'ANTARCTIC_V8_FIGURE_EXTRACT.csv';d=json.loads(ip.read_text());rows=list(csv.DictReader(fp.open()))
    assert len(d['palmer'])==10 and sum(x['n'] for x in d['palmer'])==3684
    assert len(d['optical'])==4 and d['optical_support']['matched']==46
    assert all(q['status']=='STOP_INSUFFICIENT_SUPPORT' for q in d['optical_support']['windows'])
    qa={};fig1(d,out,qa);fig2(d,out,qa);fig3(d,rows,out,qa);fig4(d,out,qa);fig5(d,out,qa);fig6(d,out,qa)
    assert len(qa)==6 and len(list(out.glob('*.png')))==6 and len(list(out.glob('*.svg')))==6
    receipt={'status':'SIX_ANTARCTIC_FIGURES_RENDERED_VALIDATED','figures':qa,'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ip,fp)},'limitations':'File integrity and receipt arithmetic, not a new ecological fit. V8 extract rounded to 9 decimals; full V8 JSON SHA256 4f1e94d55e5f4a3d9b1297596dd736a2e5d1793308d30e0dcd787cbac2278863.'}
    (out/'ANTARCTIC_FIGURE_QA.json').write_text(json.dumps(receipt,indent=2)+'\n');print('FIGURE_QA='+json.dumps(receipt,separators=(',',':')))
if __name__=='__main__':main()
