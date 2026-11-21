import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import HERE, save

d=pd.read_csv(HERE/'chlorophyll_screen_daily.csv',parse_dates=['date'])
s=pd.read_csv(HERE/'chlorophyll_screen_support.csv');rows=[]
for (site,season),g in d.groupby(['site_id','season']):
    g=g.sort_values('date');run=longest=0
    for ok in g.passes_daily:
        run=0 if ok else run+1;longest=max(longest,run)
    rows.append(dict(site_id=site,season=int(season),retrieved_days=len(g),retrieved_months=g.month.nunique(),mean_retrieved_daily_coverage=g.coverage.mean(),valid_days=int(g.passes_daily.sum()),max_missing_run_within_retrieved_prefix=longest,mean_valid_daily_log10_rms=g.loc[g.passes_daily,'log10_rms'].mean()))
save(pd.DataFrame(rows),'chlorophyll_quality_summary.csv')
q=s.groupby(['source_region','status']).size().unstack(fill_value=0).sort_index()
fig,axes=plt.subplots(1,2,figsize=(14,6),gridspec_kw={'width_ratios':[1.3,1]})
ax=axes[0];y=np.arange(len(q));kept=q['ELIGIBLE'];lost=q['INELIGIBLE_MONTHLY_COVERAGE']
ax.barh(y,kept,color='#2878a0',label='All four months supported');ax.barh(y,lost,left=kept,color='#cccccc',label='Failed monthly coverage')
ax.set_yticks(y,q.index,fontsize=9);ax.invert_yaxis();ax.set_xlabel('Colony-seasons');ax.set_title('Chlorophyll support: 112 of 358 colony-seasons');ax.legend(fontsize=8)
ax=axes[1];r=pd.read_csv(HERE/'chlorophyll_pathway_coefficients.csv').set_index('term')
names=['P0_before_per10pp','P0_after_per10pp','delta_beta_P0_per10pp'];labels=['Before chlorophyll','After chlorophyll','After minus before']
for i,n in enumerate(names):
    v=r.loc[n];ax.errorbar(v.estimate,i,xerr=[[v.estimate-v.lower],[v.upper-v.estimate]],fmt='o',color='#2878a0',capsize=4)
ax.set_yticks(range(3),labels);ax.invert_yaxis();ax.axvline(0,color='grey',linestyle='--');ax.set_xlabel('Optical delta15N proxy per +10 pp polynya (per mil)');ax.set_title('Same 112 observations; region bootstrap intervals\nOnly four regions contribute FE-residual information')
fig.tight_layout();fig.savefig(HERE/'chlorophyll_support_and_adjustment.png',dpi=180)
