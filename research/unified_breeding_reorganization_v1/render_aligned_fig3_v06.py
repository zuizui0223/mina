"""V0.6 replacement Fig. 3 from verified V9/V10 result extracts.
No ecological refit. Primary displayed scenario fixed in V10, not selected here.
Original V10 full coverage CSV SHA256 a3cdebac076593de8d5c93f50e52f7b2d82e4e05683127d366f2c693b0c495b2.
Historical duplicate 25-km SIC rows excluded (same as 100-km).
"""
from pathlib import Path
import argparse,csv,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from PIL import Image
import xml.etree.ElementTree as ET
ROOT=Path(__file__).parent
H=['long_parent23','long_complete17','short_parent15_100','short_complete9_100']
F=['long_parent23_all','long_complete17_all','short_parent15_all','short_complete9_all']
LABELS=['Long 23','Long 17','Short 15','Short 9']
BLUE='#176C80'; ORANGE='#B96A38'; DARK='#253942'; GREY='#9AA8AE'; GREEN='#52794C'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':DARK,'xtick.color':DARK,'ytick.color':DARK,'text.color':DARK,'svg.fonttype':'none','savefig.dpi':300,'svg.hashsalt':'mina-antarctic-v06'})
def read(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def title(ax,t):ax.set_title(t,loc='left',fontweight='bold',fontsize=10,pad=9)
def zero(ax):ax.axhline(0,color=GREY,lw=.8,zorder=0)
def run(out):
    files=['GEOGRAPHIC_HISTORICAL_V10_SUMMARY.csv','GEOGRAPHIC_FUTURE_SSP585_LATE_V10_SUMMARY.csv','ANTARCTIC_V8_FIGURE_EXTRACT.csv','GEOGRAPHIC_COVERAGE_FIG3_V0_6.csv']
    h,f,v,c=[read(n) for n in files]
    h={z['cohort']:z for z in h if z['variable']=='sic_pp'}
    f={z['cohort']:z for z in f if z['variable']=='siconc'}
    v={z['cohort']:z for z in v if z['variable']=='siconc' and z['scenario']=='ssp585' and z['period']=='2081-2100'}
    c={(z['period'],z['era']):z for z in c}
    assert len(c)==4 and len(v)==4
    ht=np.array([float(h[k]['total']) for k in H]);ft=np.array([float(f[k]['total']) for k in F])
    models=np.array([[float(v[k][j]) for j in ('ACCESS_difference','BCC_difference','CESM2_difference')] for k in F])
    assert np.max(abs(models.mean(axis=1)-ft))<2e-9
    for z in [h[k] for k in H]+[f[k] for k in F]:assert abs(float(z['total'])-float(z['between'])-float(z['within']))<2e-9
    for i,t in enumerate(('Long','Short')):
        for era,arr in [('Historical',ht),('Future',ft)]:
            z=c[t,era];assert abs(float(z['parent'])-arr[i*2])<2e-9 and abs(float(z['retained'])-arr[i*2+1])<2e-9
            assert abs(float(z['retained_renormalization'])+float(z['excluded_within'])+float(z['between_subsets'])-float(z['parent_minus_retained']))<2e-9
    fig,axs=plt.subplots(2,2,figsize=(10.5,7.4),layout='constrained')
    ax=axs[0,0];title(ax,'A  Historical and projected change fields')
    x=np.arange(4);zero(ax)
    ax.scatter(x-.18,ht,color=BLUE,s=40,zorder=4,label='Historical contrast')
    for i in range(4):
        xx=x[i]+.18
        ax.vlines(xx,models[i].min(),models[i].max(),color=ORANGE,lw=1.2,alpha=.7)
        for j,m in enumerate(['^','s','v']):ax.scatter(xx+[-.04,0,.04][j],models[i,j],marker=m,s=22,facecolors='white',edgecolors=ORANGE,zorder=3)
        ax.scatter(xx,ft[i],color=ORANGE,s=40,zorder=4)
    ax.set_xticks(x,LABELS);ax.set_ylabel('Recent − early weighted SIC change (pp)')
    ax.legend(handles=[Line2D([0],[0],marker='o',color=BLUE,ls='',label='Historical'),Line2D([0],[0],marker='o',color=ORANGE,ls='',label='Projected, model mean'),Line2D([0],[0],marker='^',markerfacecolor='white',color=ORANGE,ls='',label='Individual GCMs')],frameon=False,fontsize=8,loc='upper left')
    ax=axs[0,1];title(ax,'B  Regional decomposition (all four rosters)')
    rows=[]
    for k,l in zip(H,F):rows.extend([h[k],f[l]])
    xx=np.arange(8);zero(ax)
    for i,(key,col) in enumerate([('between',BLUE),('within',ORANGE)]):
        ax.bar(xx+(-.17 if i==0 else .17),[float(z[key]) for z in rows],width=.32,color=col,label=key.capitalize()+' regions')
    ax.scatter(xx,[float(z['total']) for z in rows],marker='D',s=22,color=DARK,label='Sum',zorder=4)
    ax.set_xticks(xx,[l+'\n'+e for l in LABELS for e in ['Hist.','Proj.']],fontsize=7.2);ax.set_ylabel('Change-field contribution (pp)');ax.legend(frameon=False,fontsize=8,ncol=2)
    ax=axs[1,0];title(ax,'C  Six excluded Victoria Land sites')
    for i,t in enumerate(['Long','Short']):
        z=c[t,'Historical'];shares=100*np.array([float(z['retained_share0']),float(z['retained_share1'])])
        xx=np.array([i*3,i*3+1]);ax.bar(xx,shares,.65,color=GREY);ax.bar(xx,100-shares,.65,bottom=shares,color=ORANGE)
        for x0,y in zip(xx,shares):ax.text(x0,y+(100-y)/2,f'{100-y:.1f}%',color='white',ha='center',va='center',fontsize=9,fontweight='bold')
    ax.set_xticks([0,1,3,4],['Long\nearly','Long\nrecent','Short\nearly','Short\nrecent']);ax.set_ylim(0,110);ax.set_ylabel('Share of recorded site-median sums (%)')
    ax.legend(handles=[Patch(color=GREY,label='Retained'),Patch(color=ORANGE,label='Excluded')],frameon=False,loc='upper center',ncol=2,fontsize=8,bbox_to_anchor=(.5,1.06))
    ax=axs[1,1];title(ax,'D  Why parent and complete rosters differ')
    rows=[c[t,e] for t in ['Long','Short'] for e in ['Historical','Future']];xx=np.arange(4);zero(ax)
    for i,(key,col,lab) in enumerate([('retained_renormalization',BLUE,'Retained re-normalization'),('excluded_within',GREEN,'Excluded within'),('between_subsets',ORANGE,'Between coverage groups')]):
        ax.bar(xx+(i-1)*.22,[float(z[key]) for z in rows],.20,color=col,label=lab)
    ax.scatter(xx,[float(z['parent_minus_retained']) for z in rows],marker='D',color=DARK,s=23,label='Parent − complete',zorder=4)
    ax.set_xticks(xx,['Long\nHist.','Long\nProj.','Short\nHist.','Short\nProj.']);ax.set_ylabel('Contribution (pp)');ax.legend(frameon=False,fontsize=7.5,loc='lower right')
    fig.suptitle('Breeding-allocation effects depend on geographic support and change fields',fontsize=13,fontweight='bold')
    out.mkdir(parents=True,exist_ok=True);stem='A3_aligned_change_fields_geography';qa={'status':'RENDERED_V06_MAIN_FIG3','inputs':{n:sha(ROOT/n) for n in files},'figures':{},'historical':ht.tolist(),'projected':ft.tolist(),'max_model_mean_error':float(np.max(abs(models.mean(axis=1)-ft))),'limits':'Selected SSP5-8.5 2081–2100 relative to model 1995–2014; historical periods differ. Model spread, not CI. Non-independent nested rosters, no ecological benefits or predictions.'}
    for ext in ['png','svg']:
        pp=out/(stem+'.'+ext);fig.savefig(pp,bbox_inches='tight',pad_inches=.17,facecolor='white')
        assert pp.stat().st_size>4000
        d={'sha256':sha(pp),'bytes':pp.stat().st_size}
        if ext=='png':
            with Image.open(pp) as im:im.verify()
            with Image.open(pp) as im:d['pixels']=list(im.size)
        else:ET.parse(pp)
        qa['figures'][pp.name]=d
    plt.close(fig)
    (out/'FIG3_V06_QA.json').write_text(json.dumps(qa,indent=2)+'\n');print('FIG3_QA='+json.dumps(qa,separators=(',',':')))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);run(a.parse_args().out)
