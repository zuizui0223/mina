"""Label endpoint winners with an explicit 1% practical tie margin; keep strict-sign sensitivity."""
from pathlib import Path
import numpy as np
import pandas as pd
out=Path(__file__).resolve().parent
d=pd.read_csv(out/'counterfactuals.csv')
base=np.log(d.base_RB/d.base_RA)
for mode in ['fixed','moved']:
    d[mode+'_level']=np.log(d[mode+'_RB']/d[mode+'_RA'])
    d[mode+'_gain']=d[mode+'_level']-base
def labels(v,margin=1.01):
    return np.select([v>np.log(margin),v< -np.log(margin)],[d.A,d.B],default='tie')
counts=[]
for measure in ['gain','level']:
    for m in ['fixed','moved']:d[m+'_'+measure+'_winner']=labels(d[m+'_'+measure])
    a=d['fixed_'+measure+'_winner'];b=d['moved_'+measure+'_winner']
    d[measure+'_reversed']=(a!=b)&(a!='tie')&(b!='tie')
    d[measure+'_strict_flip']=d['fixed_'+measure]*d['moved_'+measure]<-1e-16
    d[measure+'_tie']=(a=='tie')|(b=='tie')
    for keys,g in d.groupby(['beta','shift','policy']):
        counts.append(dict(beta=keys[0],shift=keys[1],policy=keys[2],endpoint=measure,n=len(g),
                           reversal=g[measure+'_reversed'].sum(),ties=g[measure+'_tie'].sum(),strict_reversal=g[measure+'_strict_flip'].sum()))
pd.DataFrame(counts).to_csv(out/'reversals.csv',index=False)
primary=d.query("beta==2 and shift=='median_SW' and policy=='all'").copy()
old=pd.read_csv('outputs/warming_access_sim/scenarios.csv').query("beta==2 and mode=='spatial'")
join=primary.merge(old,on=['pair','ssp','period','model'],validate='one_to_one')
assert len(join)==84 and np.allclose(100*np.expm1(join.fixed_gain),join.relative_A_to_B_pct,atol=1e-7)
primary.to_csv(out/'primary_cases.csv',index=False)
rows=[]
for (pair,ssp,period),g in primary.groupby(['pair','ssp','period']):
    rec=dict(pair=pair,ssp=ssp,period=period)
    for meas in ['level','gain']:
        for mode in ['fixed','moved']:
            field=mode+'_'+meas+'_winner';wins=g[field].unique()
            rec[field]=wins[0] if len(wins)==1 and wins[0]!='tie' else 'no consensus'
        rec[meas+'_flip_models']=int(g[meas+'_reversed'].sum())
    rows.append(rec)
cons=pd.DataFrame(rows);cons.to_csv(out/'model_agreement.csv',index=False)
s=cons.groupby('pair').agg(moved_level_agreement=('moved_level_winner',lambda t:(t!='no consensus').sum()),moved_gain_agreement=('moved_gain_winner',lambda t:(t!='no consensus').sum()),all_three_level_flip=('level_flip_models',lambda t:(t==3).sum()),all_three_gain_flip=('gain_flip_models',lambda t:(t==3).sum()))
s['level_flip_runs']=primary.groupby('pair').level_reversed.sum()
s['gain_flip_runs']=primary.groupby('pair').gain_reversed.sum()
s.to_csv(out/'pair_results.csv')
print(s.to_string())
print(pd.DataFrame(counts).query("beta==2 and policy=='all'").to_string(index=False))
print(cons.filter(like='winner').apply(lambda col:(col!='no consensus').sum()))
print(pd.read_csv(out/'shift_support.csv').query("treatment=='median_SW'")[['pair','within25_fraction','median_realized_km']].round(2))
