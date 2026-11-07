"""Build manuscript figures/tables from verified aggregate outputs, no model refits."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COLORS={'Adelie':'#0072B2','Chinstrap':'#D55E00','Gentoo':'#009E73'}

def mdtable(d):
    def fmt(v):
        if pd.isna(v):return 'NA'
        if isinstance(v,(float,np.floating)):return f'{v:.3f}'
        return str(v)
    return '\n'.join(['| '+' | '.join(map(str,d.columns))+' |','| '+' | '.join(['---']*len(d.columns))+' |']+['| '+' | '.join(fmt(v) for v in row)+' |' for row in d.itertuples(index=False,name=None)])

def run(out):
    out.mkdir(parents=True,exist_ok=True);figdir=out/'figures';figdir.mkdir(exist_ok=True)
    root=Path(__file__).resolve().parents[2]/'outputs';n=root/'niche_multiscale_v1';s=root/'diet_niche_scenarios_v1';sources={}
    def read(folder,name):
        p=folder/name;sources[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest();return pd.read_csv(p)
    annual=read(n,'annual_distances.csv');fish=annual.query('variant=="full" and pair=="Gentoo-vs-others" and metric=="fish"').sort_values('year')
    spp=read(n,'prior_signed_fish_gap.csv').merge(fish[['year','sic_aug_nov','distance']],on='year',validate='one_to_one')
    support=read(n,'species_year_support.csv');balanced=read(n,'sample_size_sensitivity.csv');dated=read(n,'date_matching_same_year_comparison.csv')
    associations=read(n,'associations.csv');scenarios=read(s,'conditional_scenarios.csv');sensitivity=read(s,'ice_reduction_sensitivity.csv');exact=read(n,'exact_three_metric_family.csv')
    summary=json.loads((s/'summary.json').read_text());sources[str((s/'summary.json').relative_to(root))]=hashlib.sha256((s/'summary.json').read_bytes()).hexdigest()
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    def save(fig,name):
        fig.savefig(figdir/(name+'.png'),dpi=220);fig.savefig(figdir/(name+'.pdf'));plt.close(fig)
    fig,ax=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
    for sp in COLORS:
        ax[0].scatter(spp.sic_aug_nov,100*spp[sp],label=sp,color=COLORS[sp],marker={'Adelie':'o','Chinstrap':'^','Gentoo':'s'}[sp],s=42,alpha=.85)
    ax[0].set(xlabel='Antecedent Aug–Nov SIC (%)',ylabel='Mean stomach fish share (%)',ylim=(-3,100),title='A  Species-specific diet composition');ax[0].legend(frameon=False)
    ax[1].scatter(fish.sic_aug_nov,fish.distance,color='#454545',s=44)
    for r in fish.itertuples():ax[1].annotate(str(r.year)[2:],(r.sic_aug_nov,r.distance),xytext=(4,4),textcoords='offset points',fontsize=8)
    x=np.array([fish.sic_aug_nov.min(),fish.sic_aug_nov.max()]);b=np.polyfit(fish.sic_aug_nov,fish.distance,1);ax[1].plot(x,np.polyval(b,x),color='#0072B2',lw=1.7)
    ax[1].set(xlabel='Antecedent Aug–Nov SIC (%)',ylabel='Dietary separation D (0–1)',title='B  Matched-species separation: r = 0.784',ylim=(-.03,.95));ax[1].margins(x=.12)
    for a in ax:a.grid(alpha=.15)
    fig.suptitle('Signy, 2001/02–2009/10: 772 stomach samples, 9 environmental years',fontsize=12);save(fig,'Figure_1_observed_diet')
    fig,ax=plt.subplots(1,2,figsize=(11,4.6),layout='constrained')
    rb=balanced.query('metric=="fish"').set_index('method');names=['equal_within_year','equal_all_years','stomach_bootstrap'];labels=['Equal n within each year','Six stomachs / species / year','Within-species-year bootstrap']
    for i,name in enumerate(names):
        z=rb.loc[name];ax[0].errorbar(z.r_median,i,xerr=[[z.r_median-z.r_low],[z.r_high-z.r_median]],fmt='o',color='#0072B2',capsize=4)
    ax[0].axvline(.784042737486591,color='gray',ls='--',label='Full sample');ax[0].set(yticks=range(3),yticklabels=labels,xlim=(.35,1),xlabel='Correlation with SIC',title='A  Stomach-count sensitivity');ax[0].invert_yaxis();ax[0].legend(frameon=False,loc='center left');ax[0].text(.38,2.5,'Intervals: stomach resampling only;\nnine climate years held fixed.',fontsize=8)
    matched=annual.query('variant=="date_matched" and window==7 and metric=="fish" and pair=="Gentoo-Adelie"').dropna(subset=['distance']).sort_values('year')
    same=annual.query('variant=="full" and metric=="fish" and pair=="Gentoo-Adelie"');same=same[same.year.isin(matched.year)].sort_values('year')
    assert len(matched)==len(same)==8 and list(matched.year)==list(same.year)
    for old,new in zip(same.itertuples(),matched.itertuples()):ax[1].plot([old.sic_aug_nov,new.sic_aug_nov],[old.distance,new.distance],color='gray',lw=.9)
    ax[1].scatter(same.sic_aug_nov,same.distance,facecolors='none',edgecolors='#777777',s=55,label='All dates, same 8 years (r = 0.884)')
    ax[1].scatter(matched.sic_aug_nov,matched.distance,color='#009E73',marker='x',s=45,label='Within 7 days (r = 0.880)')
    ax[1].set(xlabel='Antecedent Aug–Nov SIC (%)',ylabel='Gentoo–Adelie fish-share distance',title='B  Matched-date support',ylim=(-.03,1.03));ax[1].legend(frameon=False,fontsize=8,loc='upper left');ax[1].grid(alpha=.15);save(fig,'Figure_2_sampling_sensitivity')
    fig,ax=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    z=sensitivity[sensitivity.in_range];x=np.r_[0,z.reduction_pp];change=np.r_[0,z.conditional_gap_change];low=np.r_[0,z.coefficient_only_ci_low];high=np.r_[0,z.coefficient_only_ci_high]
    ax[0].fill_between(x,low,high,color='#0072B2',alpha=.16,label='95% coefficient-only HC3 interval')
    ax[0].plot(x,change,'o-',color='#0072B2',label='Linear association');ax[0].plot(x,np.r_[0,z.fractional_logit_change],'s--',color='#D55E00',label='Fractional-logit sensitivity')
    ax[0].set(xlabel='SIC reduction from 48.683% (percentage points)',ylabel='Conditional change in D',title='A  Response held fixed',xticks=[0,5,10,20]);ax[0].legend(frameon=False,fontsize=8);ax[0].grid(alpha=.15)
    cats=[('ssp245','2041-2060'),('ssp245','2081-2100'),('ssp585','2041-2060'),('ssp585','2081-2100')]
    colors={'ACCESS-CM2':'#0072B2','BCC-CSM2-MR':'#D55E00','CESM2':'#009E73'}
    ax[1].axvspan(*summary['observed_sic_range'],color='gray',alpha=.12,label='Observed diet–SIC domain')
    ax[1].axvline(summary['reference_sic'],color='gray',ls=':',lw=1)
    for j,(model,col) in enumerate(colors.items()):
        for i,(sc,period) in enumerate(cats):
            r=scenarios.query('model==@model and scenario==@sc and period==@period').iloc[0]
            ax[1].scatter(r.delta_adjusted_sic,i+(j-1)*.16,color=col,marker='o' if r.within_observed_diet_sic_range else 'X',s=50,label=model if i==0 else None)
    ax[1].set(xlabel='Observed reference + model SIC change (%)',yticks=range(4),yticklabels=['SSP2-4.5 mid-century','SSP2-4.5 late-century','SSP5-8.5 mid-century','SSP5-8.5 late-century'],xlim=(15,70),title='B  Climate exposure, not a diet forecast');ax[1].invert_yaxis();ax[1].legend(frameon=False,fontsize=7,loc='lower right');save(fig,'Figure_3_conditional_scenarios')
    # Main tables are regenerated values, never copied hand-typed estimates.
    table1=spp[['year','sic_aug_nov','distance']].copy()
    for sp in COLORS:table1['n_'+sp]=table1.year.map(support.query('species==@sp').set_index('year').n_fish)
    table1=table1[['year','n_Adelie','n_Chinstrap','n_Gentoo','sic_aug_nov','distance']]
    table2=associations.query('variant=="full" and pair=="Gentoo-vs-others" and ice_window=="Aug-Nov"')[['metric','n_years','r','slope_per_10pp','hc3_low','hc3_high','detrended_r','loo_min','loo_max']].merge(exact[['metric','p_exact','p_max3']],on='metric',validate='one_to_one')
    table3=sensitivity.copy();st1=scenarios.copy();st2=read(s,'rolling_origin_scores.csv')
    tables=[('Table_1_observed_support',table1),('Table_2_effects_and_inference',table2),('Table_3_conditional_sensitivity',table3),('Table_S1_model_scenarios',st1),('Table_S2_rolling_diagnostics',st2)]
    parts=[]
    for name,table in tables:
        table.to_csv(out/(name+'.csv'),index=False,lineterminator='\n');parts.append('## '+name+'\n\n'+mdtable(table)+'\n')
    (out/'TABLES.md').write_text('\n'.join(parts),encoding='utf-8',newline='\n')
    # Machine-readable figure data for each panel.
    spp.to_csv(out/'Figure_1_data.csv',index=False,lineterminator='\n');matched.to_csv(out/'Figure_2_matched_data.csv',index=False,lineterminator='\n')
    assert sum(table1.n_Adelie)==349 and sum(table1.n_Chinstrap)==350 and sum(table1.n_Gentoo)==73
    assert len(st1)==12 and st1.within_observed_diet_sic_range.sum()==11
    manifest=dict(inputs=sources,figures=['Figure_1_observed_diet','Figure_2_sampling_sensitivity','Figure_3_conditional_scenarios'],counts=dict(years=len(table1),stomachs=int(table1[['n_Adelie','n_Chinstrap','n_Gentoo']].sum().sum()),scenarios=len(st1)),checks='aggregate joins, 772 stomach denominator, matched 8-year support, 12 scenarios / 11 in domain pass')
    (out/'ASSET_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(manifest['counts']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
