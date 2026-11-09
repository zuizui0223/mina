"""Summarize physical changes and independently audit reported score calculations."""
import itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
out=Path(__file__).resolve().parent
a=pd.read_csv(out/'native_resistances.csv'); b=pd.read_csv(out/'stress_native.csv');tri=pd.read_csv(out/'tri_native.csv')
b['loss_pp']=b['case'].str.split('minus').str[-1].astype(int)
z=b.merge(a,on=['key','year','beta'],suffixes=('_scenario','_obs'),validate='many_to_one')
for node in ['A','B']:
    z['absolute_access_gain_pct_'+node]=100*(z['R_'+node+'_obs']/z['R_'+node+'_scenario']-1)
z['relative_access_A_vs_B_change_pct']=100*((z.R_B_scenario/z.R_A_scenario)/(z.R_B_obs/z.R_A_obs)-1)
z.to_csv(out/'ice_loss_sensitivity.csv',index=False)
d=pd.read_csv(out/'analysis_panel.csv')
checks=[]
for x in ['penalty','favor']:
    x0=d[x]-d.groupby('key')[x].transform('mean');y0=d.share_change-d.groupby('key').share_change.transform('mean')
    block=d.key.str.split('_',n=1).str[1];cov=(x0*y0).groupby(block).sum()
    null=np.array([np.dot(sign,cov) for sign in itertools.product([-1,1],repeat=len(cov))])
    eligible=d.share_change.abs()>1e-12
    checks.append(dict(model=x,spatial_pairs=len(cov),nonties=eligible.sum(),direction_agreement=((d[x]*d.share_change>0)&eligible).sum(),
                       p_sign_flip_two_sided=np.mean(abs(null)>=abs(cov.sum())-1e-15)))
pd.DataFrame(checks).to_csv(out/'direction_checks.csv',index=False)
s=pd.read_csv(out/'holdout_scores.csv')
h=pd.read_csv(out/'holdout_predictions.csv')
for row in s.itertuples():
    v=h[(h.fold==row.fold)&(h.model==row.model)]
    assert np.allclose(100*abs(v.predicted-v.target).mean(),row.share_MAE_pp)
    assert np.allclose(abs((2*v.predicted**2-2*v.predicted)-(2*v.target**2-2*v.target)).mean(),row.H_MAE)
t=pd.read_csv(out/'three_colony_scores.csv');t0=pd.read_csv(out/'three_colony_holdouts.csv')
assert all(np.isclose(row.H_MAE,abs(g.H_observed-g.H_predicted).mean()) for row in t.itertuples() for g in [t0[(t0.fold==row.fold)&(t0.model==row.model)]])
assert len(d)==48 and len(a)==140 and len(tri)==66 and len(b)==32
err=max(f.max_abs_solver_difference.max() for f in [a,b,tri]);assert err<1e-8
fig,ax=plt.subplots(1,2,figsize=(10,4.4),layout='constrained')
for panel,frame,metric,title in zip(ax,[s,t],['share_MAE_pp','H_MAE'],['A   Two-colony share error (pp)','B   Three-colony concentration error']):
    names=['forward','region','forward_other_region'];ix=np.arange(3)
    for j,(model,label,color) in enumerate([('persistence','Previous share','#686868'),('history_geometry','History + geography','#C77924'),('circuit_penalty','Ice resistance added','#247B90')]):
        v=frame[frame.model==model].set_index('fold').loc[names]
        panel.bar(ix+.25*(j-1),v[metric],width=.24,label=label,color=color)
    panel.set(xticks=ix,xticklabels=['Later year','Other region','Later year,\nother region'],title=title,ylabel='Mean absolute error (lower is better)')
ax[0].legend(frameon=False,fontsize=8);fig.savefig(out/'heldout_errors.png',dpi=170)
(out/'validation.json').write_text(json.dumps(dict(circuitscape_version='6.0.0',julia='1.11.9',native_network_cases=len(a)+len(b)+len(tri),maximum_independent_solver_difference=float(err),dyad_transitions=len(d),fixed_three_site_transitions=int(len(pd.read_csv(out/'three_colony_panel.csv'))/3)),indent=2))
print(checks,err)
