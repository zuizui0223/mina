"""Observed stomach components, exact accounting, and recovered mass."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT=Path(__file__).resolve().parents[2]/'outputs/signy_diet_components_v1'


def main():
    data=pd.read_csv(OUT/'gentoo_primary_nine_seasons.csv')
    summary=json.loads((OUT/'summary.json').read_text())
    blue,orange,teal,grey='#246A9B','#CB633D','#268278','#72777D'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
                         'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(12,9.6),layout='constrained')
    for ax,key,col,color,title in [
        (axes[0,0],'frequency','positive_mass_frequency',blue,'A  Frequency of recorded positive fish mass'),
        (axes[0,1],'composition','conditional_fish_fraction',orange,'B  Fish fraction within positive-mass stomachs')]:
        stats=summary['component_associations'][key]
        x=np.linspace(data.sic_aug_nov.min(),data.sic_aug_nov.max(),100)
        ax.scatter(data.sic_aug_nov,100*data[col],color=color,s=55,zorder=3)
        ax.plot(x,100*(stats['intercept']+stats['slope_per_10pp']*x/10),color=color,lw=1.6)
        for row in data.itertuples():
            label=f'{str(row.year)[-2:]}'
            if key=='frequency': label+=f': {row.n_positive_fish_mass}/{row.n_stomachs}'
            dx,dy=(5,5)
            if row.year==2006 and key=='frequency': dx,dy=(-39,-14)
            if row.year==2009 and key=='frequency': dx,dy=(-45,-12)
            if row.year==2009 and key=='composition': dx,dy=(5,-13)
            ax.annotate(label,(row.sic_aug_nov,100*getattr(row,col)),xytext=(dx,dy),
                        textcoords='offset points',fontsize=8)
        ax.set(title=title,xlabel='Antecedent August-November SIC (%)',xlim=(17,74),ylim=(-3,109))
        ax.text(.03,.96,f"r = {stats['pearson_r']:.3f}\nTwo-component max-|r| p = {stats['p_max2']:.4f}",
                transform=ax.transAxes,va='top',fontsize=9,
                bbox={'facecolor':'white','edgecolor':'none','alpha':.9})
    axes[0,0].set_ylabel('Stomachs with fish wet mass > 0 (%)')
    axes[0,1].set_ylabel('Mean fish fraction, conditional on fish mass > 0 (%)')
    ax=axes[1,0]
    accounting=summary['slope_accounting']
    keys=['frequency','composition','covariation']
    values=[100*accounting['component_slopes_per_10pp'][k] for k in keys]
    ax.bar(range(3),values,color=[blue,orange,grey],width=.62)
    for i,value in enumerate(values): ax.text(i,value+.18,f'{value:+.2f}',ha='center',fontsize=11)
    ax.set(title='C  Exact allocation of the mean-response slope',
           xticks=range(3),xticklabels=['Frequency','Conditional\ncomposition','Covariation'],
           ylabel='Allocated slope (diet pp / +10 SIC pp)',ylim=(0,8.6))
    ax.text(.04,.95,f"Total mean-response slope: +{100*accounting['mean_response_slope_per_10pp']:.2f} pp\n"
            'Algebraic accounting; not causal contributions',transform=ax.transAxes,va='top',fontsize=9)
    ax=axes[1,1]
    for col,label,color,marker in [
        ('mean_fish_mass_g','Fish',orange,'o'),
        ('mean_crustacean_mass_g','Crustaceans',teal,'^'),
        ('mean_food_mass_g','Total food',grey,'s')]:
        stats=summary['recovered_mass_descriptives'][col]
        ax.scatter(data.sic_aug_nov,data[col],s=42,color=color,marker=marker,
                   label=f"{label} (r = {stats['pearson_r']:+.2f})",zorder=3)
        x=np.linspace(data.sic_aug_nov.min(),data.sic_aug_nov.max(),100)
        slope=stats['slope_g_per_10pp']/10
        ax.plot(x,data[col].mean()+slope*(x-data.sic_aug_nov.mean()),color=color,lw=1.2,alpha=.8)
    ax.set(title='D  Recovered mass, same stomach cohort',xlabel='Antecedent August-November SIC (%)',
           ylabel='Mean recovered wet mass per stomach (g)',xlim=(17,74),ylim=(-10,700))
    ax.legend(loc='upper left',frameon=False,fontsize=9)
    for ax in axes.flat:
        ax.grid(axis='y',alpha=.18)
        ax.set_axisbelow(True)
    fig.suptitle('Sea ice and the components of gentoo meal composition at Signy',fontsize=16,fontweight='bold')
    fig.get_layout_engine().set(rect=(0,.065,1,.93))
    fig.text(.02,.012,'Nine breeding seasons (2001/02-2009/10), 73 valid stomachs; seasons weighted equally. '
             'Labels are season start years; A also shows positive / valid counts.\n'
             'Frequency denotes recorded positive wet mass, not all fish traces. Recovered grams are not intake rates. '
             'Permutation p assumes exchangeable years.\n'
             'Sources: Dunn et al. (2022), BAS gentoo diet records, doi:10.5285/fb9bd975-e6fe-406c-84be-01e57d612b5e; '
             'OSI SAF sea-ice concentration.',fontsize=8,color='#444444')
    fig.savefig(OUT/'Figure_1_diet_components.png',dpi=220,facecolor='white')
    fig.savefig(OUT/'Figure_1_diet_components.pdf',facecolor='white')
    plt.close(fig)


if __name__=='__main__': main()
