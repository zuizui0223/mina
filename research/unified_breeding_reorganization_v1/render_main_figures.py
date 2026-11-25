"""Five main figures from frozen numeric receipts; no new ecological fit."""
import argparse,csv,hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
ROOT=Path(__file__).parent
G=('decline','near_stable','increase');LABEL=('Decline','Near-stable','Increase'); X=np.arange(3)
BLUE='#176A77';ORANGE='#B86B3B';GREY='#8A969C';DARK='#20343D';PALE='#D8E0E2'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':DARK,'text.color':DARK,'xtick.color':DARK,'ytick.color':DARK,'svg.fonttype':'none','figure.dpi':150,'savefig.dpi':300})
def load(s):return json.loads((ROOT/s).read_text())
def hsh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def head(ax,title):ax.set_title(title,loc='left',fontweight='bold',fontsize=10,pad=8)
def save(fig,name,out,receipt):
    record={}
    for ext in ('png','svg'):
        path=out/(name+'.'+ext);fig.savefig(path,bbox_inches='tight',pad_inches=.16,facecolor='white')
        if ext=='png':
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:record['pixels']=list(im.size)
        else:ET.parse(path)
        record[ext+'_sha256']=hsh(path)
        assert path.stat().st_size>4000
    receipt[name]=record
    plt.close(fig)
def fig1(out,r):
    old=np.array([22,15,12,8]);targets=[np.array(z) for z in ([20,5,2,0],[65,18,15,10],[5,54,5,3])]
    f,axs=plt.subplots(1,3,figsize=(10.4,3.5),layout='constrained',sharey=True)
    for i,(ax,new,name) in enumerate(zip(axs,targets,['Differential attrition','Differential amplification','Countervailing changes'])):
        ax.bar(np.arange(4)-.18,old,.34,color=PALE,label='Earlier');ax.bar(np.arange(4)+.18,new,.34,color=BLUE,label='Later')
        p=old/old.sum();q=new/new.sum();d=new-old;g=d.clip(0).sum();l=(-d).clip(0).sum();c=2*min(g,l)/(old.sum()+new.sum());bc=(g+l)/(old.sum()+new.sum())
        assert np.isclose(bc,c+abs(g-l)/(old.sum()+new.sum()))
        head(ax,chr(65+i)+'  '+name);ax.set_xticks(range(4),['1','2','3','4']);ax.set_xlabel('Illustrative component')
        ax.text(.02,.97,f'N: {old.sum()} → {new.sum()}\nΔH = {sum(q*q)-sum(p*p):+.2f}\nC = {c:.2f}',transform=ax.transAxes,va='top',bbox={'facecolor':'white','edgecolor':'none','alpha':.9})
        ax.set_ylim(0,83)
    axs[0].set_ylabel('Illustrative breeding count')
    axs[2].legend(loc='upper right',frameon=False,fontsize=8)
    f.suptitle('Different accounting routes to greater concentration',fontweight='bold',fontsize=13)
    save(f,'Fig1_accounting_framework',out,r)
def fig2(full,strict,out,r):
    f,axs=plt.subplots(2,2,figsize=(8.5,6.0),layout='constrained',sharex=True)
    for row,(d,name) in enumerate([(full,'Full cohort · 10 common taxa'),(strict,'Exact-year cohort · 7 common taxa')]):
        for col,(key,title) in enumerate([('deltaU','Signed concentration change (ΔU)'),('D2','Signed squared share distance (D²)')]):
            ax=axs[row,col];obs=[];q=[]
            for i,g in enumerate(G):
                z=d['common_species_equal'][g]
                if row==0:
                    v=z['meanDeltaU' if key=='deltaU' else 'meanD2'];ci=z.get('deltaU_network_bootstrap95' if key=='deltaU' else 'D2_network_bootstrap95')
                    null=d['model_sensitivity']['gamma_CV20_then_multinomial'][g][key]['q05_q95']
                else:
                    v=z[key]['observed'];ci=z[key]['bootstrap95'];null=z[key]['gammaCV20_q05_q95']
                ax.plot([i-.16,i-.16],null,color=GREY,lw=6,alpha=.6,solid_capstyle='butt')
                if ci:ax.plot([i+.13,i+.13],ci,color=BLUE,lw=1.8)
                ax.scatter(i+.13,v,color=BLUE,s=31,zorder=3)
            ax.axhline(0,color='#A8B1B5',lw=.7);ax.set_xticks(X,LABEL);ax.set_xlim(-.48,2.48)
            head(ax,chr(65+row*2+col)+'  '+title);ax.set_ylabel(name,fontsize=8)
            if row:ax.text(.02,.96,'Bootstrap interval withheld',transform=ax.transAxes,va='top',fontsize=7,color=GREY)
    for col in range(2):
        lo=min(axs[i,col].get_ylim()[0] for i in range(2));hi=max(axs[i,col].get_ylim()[1] for i in range(2))
        for row in range(2):axs[row,col].set_ylim(lo,hi)
    f.legend(handles=[Line2D([0],[0],marker='o',color=BLUE,label='Observed; line = 95% network bootstrap'),Line2D([0],[0],color=GREY,lw=6,label='Gamma CV20 model, 5–95%')],loc='outside lower center',ncol=2,frameon=False,fontsize=8)
    save(f,'Fig2_composition',out,r)
def fig3(gross,out,r):
    f,axs=plt.subplots(2,2,figsize=(8.5,6.2),layout='constrained')
    a,b=gross['full'],gross['exact_year']
    for i,(metric,title) in enumerate([('mixed','Opposing local changes'),('any_positive_to_zero','At least one positive-to-zero record')]):
        ax=axs[0,i];head(ax,chr(65+i)+'  '+title)
        for j,(d,color,label) in enumerate([(a,BLUE,'Full'),(b,ORANGE,'Exact-year')]):
            h=[100*d['descriptive'][g][metric]/d['descriptive'][g]['n'] for g in G]
            bars=ax.bar(X+(-.19 if j==0 else .19),h,.34,color=color,label=label)
            for bar,v in zip(bars,h):ax.text(bar.get_x()+bar.get_width()/2,v+1.5,f'{v:.0f}',ha='center',fontsize=8)
        ax.set_ylim(0,112);ax.set_xticks(X,LABEL);ax.set_ylabel('% of comparisons')
    for col,(metric,title) in enumerate([('counterflow','Replacement component (C)'),('material_counterflow','Comparisons with C ≥ 0.05')]):
        ax=axs[1,col];head(ax,chr(67+col)+'  '+title)
        for j,(d,color) in enumerate([(a,BLUE),(b,ORANGE)]):
            for i,g in enumerate(G):
                z=d['common_species_equal_model'][g][metric];shift=(-.16 if j==0 else .16);v=z['observed']*100;lo,hi=np.array(z['gammaCV20']['q05_q95'])*100
                ax.plot([i+shift-.065,i+shift-.065],[lo,hi],lw=4,color=GREY,alpha=.65)
                ci=z['network_bootstrap95']
                if ci:ax.plot([i+shift+.065]*2,np.array(ci)*100,color=color,lw=1.6)
                ax.scatter(i+shift+.065,v,color=color,s=28,zorder=3)
        ax.set_xticks(X,LABEL);ax.set_ylabel('% (species-equal)');ax.set_xlim(-.5,2.5)
    f.legend(handles=[Patch(facecolor=BLUE,label='Full cohort'),Patch(facecolor=ORANGE,label='Exact-year cohort'),Line2D([0],[0],color=GREY,lw=4,label='Gamma CV20 model, 5–95%')],loc='outside lower center',frameon=False,ncol=3,fontsize=8)
    save(f,'Fig3_local_changes',out,r)
def fig4(lags,local,out,r):
    f,axs=plt.subplots(3,3,figsize=(10.2,8.2),layout='constrained')
    names={'Palmer_COR':'Cormorant','Palmer_HUM':'Humble','Palmer_LIT':'Litchfield','Signy_ADPE':'Signy Adélie','Signy_CHPE':'Signy chinstrap','Ross_ADPE':'Ross Adélie'}
    for i,(k,z) in enumerate(lags['panels'].items()):
        ax=axs.flat[i];head(ax,chr(65+i)+'  '+names[k])
        for mode,color,marker,ls in [('common_start',BLUE,'o','-'),('common_end',ORANGE,'s','--')]:
            y=[z[mode]['lag_medians'][str(h)]['deltaU'] for h in (1,5,10)]
            ax.plot([1,5,10],y,color=color,marker=marker,ls=ls)
        ax.axhline(0,lw=.7,color=GREY);ax.set_xticks([1,5,10]);ax.set_xlabel('Lag (years)');ax.set_ylabel('Median ΔU')
        ax.text(.98,.04,f'n = {z["common_start"]["n"]} / {z["common_end"]["n"]}',ha='right',transform=ax.transAxes,fontsize=8)
    for i,metric in enumerate(['mixed','positive_deltaU','positive_deltaU_nonmixed']):
        ax=axs[2,i];head(ax,chr(71+i)+'  '+['Opposing changes','Positive ΔU','Positive ΔU, nonmixed'][i])
        d=local['descriptive_overlapping_rows_by_lag'];v=[d[str(h)][metric] for h in (1,5,10)]
        bars=ax.bar([1,5,10],v,width=2.3,color=BLUE)
        for bar,val in zip(bars,v):ax.text(bar.get_x()+bar.get_width()/2,val+1,str(val),ha='center',fontsize=8)
        ax.set_ylim(0,77);ax.set_xticks([1,5,10]);ax.set_xlabel('Lag (years)');ax.set_ylabel('Comparisons (of 71)')
    f.legend(handles=[Line2D([0],[0],color=BLUE,marker='o',label='Same start'),Line2D([0],[0],color=ORANGE,marker='s',ls='--',label='Same end')],loc='outside lower center',ncol=2,frameon=False)
    save(f,'Fig4_local_lags',out,r)
def fig5(path,out,r):
    raw=path.read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='eaf47bf87158ef219d75b1be9eb8e50d0703ebaa'
    rows=list(csv.DictReader(raw.decode().splitlines()));assert len(rows)==26
    names=[k for k in rows[0] if k!='year'];by={int(x['year']):np.array([int(x[k]) for k in names]) for x in rows};years=[1999,2001,2002]
    mat=np.array([by[y] for y in years]);tot=mat.sum(axis=1);shares=mat/tot[:,None]
    gain=mat[2]-mat[1];loss=mat[0]-mat[1];assert np.all(gain>0) and np.all(loss>0)
    rec=gain.sum()/loss.sum();assert abs(rec-.969675)<.00001
    def state(a):
        a=a/a.sum(axis=1)[:,None];tv0=.5*abs(a[1]-a[0]).sum();tv1=.5*abs(a[2]-a[0]).sum();return tv0,tv1,1-tv1/tv0
    six=state(mat);three=state(np.stack([mat[:,0],mat[:,1:4].sum(axis=1),mat[:,4:6].sum(axis=1)],axis=1));assert abs(six[1]-.0497)<.0002
    f,axs=plt.subplots(2,2,figsize=(9.5,6.6),layout='constrained')
    ax=axs[0,0];head(ax,'A  Aggregate breeding abundance');ax.plot(years,tot/1000,marker='o',color=BLUE,lw=2);ax.set_xticks(years);ax.set_ylabel('Count (thousands)');ax.text(.05,.08,f'{rec*100:.2f}% of loss regained',transform=ax.transAxes)
    ax=axs[0,1];head(ax,'B  Six-component composition');colors=['#C1CFD6','#8FB7C2','#5498A6','#176A77','#D99E74','#A95235'];bottom=np.zeros(3)
    for i,k in enumerate(names):
        ax.bar(np.arange(3),shares[:,i]*100,bottom=bottom,color=colors[i],label=k.replace('Cape ',''))
        bottom+=shares[:,i]*100
    ax.set_xticks(range(3),years);ax.set_ylabel('Share (%)');ax.legend(fontsize=7,frameon=False,bbox_to_anchor=(1.0,1),loc='upper left')
    ax=axs[1,0];head(ax,'C  Unequal absolute losses and rebound')
    ax.barh(np.arange(6)-.17,loss/1000,.32,color=GREY,label='Loss');ax.barh(np.arange(6)+.17,gain/1000,.32,color=BLUE,label='Rebound')
    ax.set_yticks(np.arange(6),[k.replace('Cape ','') for k in names],fontsize=8);ax.invert_yaxis();ax.set_xlabel('Count change (thousands; magnitude)');ax.legend(frameon=False,fontsize=8)
    ax=axs[1,1];head(ax,'D  Distance from pre-shock composition')
    for i,(z,col,lab) in enumerate([(six,BLUE,'Six components'),(three,ORANGE,'Three colonies')]):
        ax.plot([1999,2001,2002],[0,z[0]*100,z[1]*100],color=col,marker='o',label=lab)
        ax.text(2002.06,z[1]*100,f'{z[2]*100:.1f}% restored',color=col,fontsize=8)
    ax.set_xlim(1998.8,2003.3);ax.set_xticks(years);ax.set_ylabel('TV distance (%)');ax.legend(frameon=False,fontsize=8)
    save(f,'Fig5_ross_rebound',out,r)
    return {'aggregate_restoration':float(rec),'six_component_state':list(map(float,six)),'three_colony_state':list(map(float,three)),'totals':tot.tolist()}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ross',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    files=['JNCC_ALL_DIRECTION_RESULT_20261125.json','JNCC_EXACT_YEAR_RESULT_20261125.json','JNCC_GROSS_GAIN_LOSS_RESULT_20261125.json','MATCHED_LAGS_RESULT_20261125.json','LOCAL_GROSS_GAIN_LOSS_RESULT_20261125.json'];f,s,g,l,o=map(load,files)
    assert f['networks']==604 and s['networks']==389 and g['full']['n']==1321 and g['exact_year']['n']==663
    assert l['common_start_summary']['anchors_total']==71 and l['common_end_summary']['anchors_total']==72
    r={};fig1(a.out,r);fig2(f,s,a.out,r);fig3(g,a.out,r);fig4(l,o,a.out,r);ross=fig5(a.ross,a.out,r)
    assert len(r)==5 and len(list(a.out.glob('*.png')))==5 and len(list(a.out.glob('*.svg')))==5
    z={'status':'FIVE_FIGURES_RENDERED_AND_FILE_VALIDATED','figures':r,'receipt_sha256':{n:hsh(ROOT/n) for n in files},'ross_recomputed':ross,'limitations':'File integrity and receipt arithmetic checks, not visual inspection or new ecological fit.'}
    (a.out/'FIGURE_RENDER_QA.json').write_text(json.dumps(z,indent=2)+'\n');print('FIGURE_RESULT_JSON='+json.dumps(z,separators=(',',':')))
if __name__=='__main__':main()
