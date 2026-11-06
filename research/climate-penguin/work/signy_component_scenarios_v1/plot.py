"""Model-specific conditional mean-climate scenarios; no ensemble averaging."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

OUT=Path(__file__).resolve().parents[2]/'outputs/signy_component_scenarios_v1'


def main():
    climate=pd.read_csv(OUT/'climate_scenarios.csv')
    response=pd.read_csv(OUT/'component_scenarios.csv')
    summary=json.loads((OUT/'summary.json').read_text())
    conditions=[('ssp245','2041-2060'),('ssp245','2081-2100'),
                ('ssp585','2041-2060'),('ssp585','2081-2100')]
    models=[('ACCESS-CM2','#216B99','o',-.19),
            ('BCC-CSM2-MR','#737B83','s',0.),('CESM2','#C65D3B','^',.19)]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
                         'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(12.2,9.2),layout='constrained')
    panels=[(axes[0,0],None,'A  Sea ice at the future mean condition','Sea-ice concentration (%)',(14,75)),
            (axes[0,1],'frequency','B  Stomachs with recorded positive fish mass','Positive-mass stomachs (%)',(35,90)),
            (axes[1,0],'composition','C  Fish fraction within positive-mass stomachs','Conditional fish fraction (%)',(20,67)),
            (axes[1,1],'mean_response','D  Fish fraction across all valid stomachs','Mean fish fraction (%)',(0,58))]
    for ax,key,title,ylabel,limits in panels:
        reference=summary['reference_sic'] if key is None else 100*summary['ols_reference_responses'][key]
        ax.axhline(reference,color='#252525',ls='--',lw=1,zorder=1)
        if key is None:
            ax.axhspan(*summary['observed_diet_sic_range'],color='#A0ADB8',alpha=.15,zorder=0)
        for model,color,marker,offset in models:
            xvalues=[];yvalues=[]
            for i,(scenario,period) in enumerate(conditions):
                source=climate if key is None else response[response.response.eq(key)]
                row=source[source.model.eq(model)&source.scenario.eq(scenario)&source.period.eq(period)].iloc[0]
                x=i+offset
                y=row.delta_adjusted_sic if key is None else 100*row.future_ols
                xvalues.append(x);yvalues.append(y)
                if np.isfinite(y):
                    outside=key is None and not row.within_observed_diet_sic_range
                    ax.scatter(x,y,s=65,color=color,marker='x' if outside else marker,zorder=3)
                    if key is None:
                        ax.annotate(f'{int(row.future_annual_support_count)}/20',(x,y),xytext=(0,-15),
                                    textcoords='offset points',ha='center',fontsize=8,color=color)
                else:
                    ax.text(x,limits[0]+.045*(limits[1]-limits[0]),'NA',ha='center',color=color,fontsize=9)
            for left,right in [(0,1),(2,3)]:
                if np.isfinite(yvalues[left]) and np.isfinite(yvalues[right]):
                    ax.plot(xvalues[left:right+1],yvalues[left:right+1],color=color,lw=1,alpha=.65,zorder=2)
        ax.set(title=title,ylabel=ylabel,ylim=limits,xlim=(-.55,3.55),xticks=range(4),
               xticklabels=['SSP2-4.5\n2041-2060','SSP2-4.5\n2081-2100',
                            'SSP5-8.5\n2041-2060','SSP5-8.5\n2081-2100'])
        ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    handles=[Line2D([0],[0],marker=marker,color=color,lw=1,label=model) for model,color,marker,_ in models]
    handles.append(Line2D([0],[0],color='#252525',ls='--',lw=1,label='Reference condition'))
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.945),ncol=4,frameon=False)
    fig.suptitle('Conditional shifts in gentoo meal composition at Signy',fontsize=17,fontweight='bold')
    fig.get_layout_engine().set(rect=(0,.115,1,.75))
    fig.text(.02,.019,
        'Nine-season local relationships held fixed. Reference: observed 1995-2014 mean SIC; B-D reference values are fitted, not observed period means.\n'
        'A shading: observed diet SIC range (21.90-66.68%). A labels: corrected annual climate values within that range / 20 years.\n'
        'B-D: separate equal-season OLS responses at future mean SIC, not mean future annual diets; NA: mean SIC outside observed range.\n'
        'Model differences are not probability intervals. BCC historical SIC is near zero, limiting its raw decline; no model is removed.\n'
        'Coefficient-only change intervals and fractional-logit sensitivity are in the tables. Sources: BAS gentoo stomach records; OSI SAF; pinned CMIP6 stores.',
        fontsize=8,color='#444444')
    fig.savefig(OUT/'Figure_1_component_scenarios.png',dpi=220,facecolor='white')
    fig.savefig(OUT/'Figure_1_component_scenarios.pdf',facecolor='white')
    plt.close(fig)


if __name__=='__main__':main()
