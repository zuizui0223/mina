"""Changes in signed species timing gaps on common geographic-code/year support."""
from pathlib import Path
import hashlib,json,itertools
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]/'outputs';OUT=ROOT/'paired_species_future_v1';OUT.mkdir(exist_ok=True)
paths={
 'cohort':'relationship_response_v1/cohort.csv','coef':'four_environment_scenarios_v1/coefficients.csv',
 'annual':'scenario_support_v1/recent_comparison/overlap_annual_values.csv',
 'water':'surface_temperature_projection_v1/observed_year_alignment.csv',
 'future':'scenario_support_v1/observed_range_audit.csv',
 'water_future':'surface_temperature_projection_v1/matched_site_changes.csv',
 'deletions':'four_environment_scenarios_v1/coefficient_deletions.csv'}
d={k:pd.read_csv(ROOT/v).query("scope == 'all_source_labels'") for k,v in paths.items()}
annual=d['annual'].rename(columns={'scenario_branch':'experiment_id','model':'model_value'})
water=d['water'].assign(variable_id='tos')
columns=['species','cam','year','source_id','member_id','experiment_id','variable_id','model_value','observed']
annual=pd.concat([annual[columns],water[columns]],ignore_index=True)
future=d['future'][['species','cam','source_id','member_id','experiment_id','period','variable_id','future_model_mean']]
future=pd.concat([future,d['water_future'][['species','cam','source_id','member_id','experiment_id','period','future_model_mean']].assign(variable_id='tos')],ignore_index=True)
features={'tas':('airC',1),'siconc':('ice10',10),'sos':('salt01',.1),'tos':('waterC',1)}
def bounded(o,b,f):
    assert 0<=o<=100 and 0<=b<=100 and 0<=f<=100
    if f==b:return o
    return o*f/b if f<b else o+(100-o)*(f-b)/(100-b)
support=[];predictions=[];parts=[]
for first,second in itertools.combinations(['Adelie','Chinstrap','Gentoo'],2):
    c=d['cohort'];pairs=c[c.species==first].merge(c[c.species==second],on=['cam','year'],suffixes=('_a','_b'),validate='one_to_one')
    assert len(pairs)>0
    for cam,g in pairs.groupby('cam'):
        years=sorted(g.year.unique());support.append(dict(first=first,second=second,cam=cam,n_years=len(years),years='|'.join(map(str,years))))
        for species in [first,second]:
            a=annual[(annual.species==species)&(annual.cam==cam)&annual.year.isin(years)]
            for (model,member,scenario,variable),b in a.groupby(['source_id','member_id','experiment_id','variable_id']):
                assert sorted(b.year)==years
                baseline=b.model_value.mean();observed=b.observed.mean()
                targets=future[(future.species==species)&(future.cam==cam)&(future.source_id==model)&(future.member_id==member)&(future.experiment_id==scenario)&(future.variable_id==variable)]
                assert len(targets)==2
                feature,scale=features[variable]
                for target in targets.itertuples():
                    delta=(bounded(observed,baseline,target.future_model_mean)-observed) if variable=='siconc' else target.future_model_mean-baseline
                    for mode in ['site','site_year']:
                        coef=d['coef'][(d['coef'].species==species)&(d['coef']['mode']==mode)][feature].item()
                        parts.append(dict(first=first,second=second,cam=cam,species=species,mode=mode,source_id=model,member_id=member,experiment_id=scenario,period=target.period,feature=feature,baseline_years='|'.join(map(str,years)),observed=observed,model_baseline=baseline,model_future=target.future_model_mean,delta=delta/scale,coefficient=coef,days_component=coef*delta/scale))
parts=pd.DataFrame(parts);keys=['first','second','cam','mode','source_id','member_id','experiment_id','period']
group=parts.groupby(keys+['species']).days_component.agg(['sum','count']).reset_index();assert group['count'].eq(4).all()
for key,a in group.groupby(keys):
    first,second=key[:2];assert len(a)==2
    av=a.loc[a.species==first,'sum'].item();bv=a.loc[a.species==second,'sum'].item()
    predictions.append(dict(zip(keys,key),first_shift_days=av,second_shift_days=bv,gap_change_days=bv-av))
t=pd.DataFrame(predictions)
summary=t.groupby([k for k in keys if k!='cam']).agg(sites=('cam','nunique'),gap_change_days=('gap_change_days','mean'),first_shift_days=('first_shift_days','mean'),second_shift_days=('second_shift_days','mean')).reset_index()
np.testing.assert_allclose(summary.gap_change_days,summary.second_shift_days-summary.first_shift_days,atol=1e-10)
assert len(summary)==72
for i,r in summary.iterrows():
    a=parts
    for k in ['first','second','mode','source_id','member_id','experiment_id','period']:a=a[a[k]==r[k]]
    for cluster in ['cam','year']:
        projected={}
        for sp in [r['first'],r['second']]:
            delta=a[a.species==sp].groupby('feature').delta.mean().reindex(['airC','ice10','salt01','waterC']).to_numpy()
            bs=d['deletions'][(d['deletions'].species==sp)&(d['deletions']['mode']==r['mode'])&(d['deletions'].cluster==cluster)][['airC','ice10','salt01','waterC']].dropna().to_numpy()
            assert len(bs)>0
            projected[sp]=bs@delta
        summary.loc[i,cluster+'_delete_envelope_low']=projected[r['second']].min()-projected[r['first']].max()
        summary.loc[i,cluster+'_delete_envelope_high']=projected[r['second']].max()-projected[r['first']].min()
pd.DataFrame(support).to_csv(OUT/'paired_support.csv',index=False)
parts.to_csv(OUT/'environment_components.csv',index=False)
t.to_csv(OUT/'site_gap_changes.csv',index=False);summary.to_csv(OUT/'scenario_gap_changes.csv',index=False)
ranges=summary.groupby(['first','second','mode','experiment_id','period']).gap_change_days.agg(['min','max']).reset_index();ranges.to_csv(OUT/'ranges.csv',index=False)
lines=['# 温暖化に伴う種間の定着タイミングの相対変化', '',
 '同じ地理コード・同じ観測年で揃った集合を基準に、将来環境との差を作り直した。回帰係数は既存の広域4環境モデルを維持し、少数のペアだけで再推定していない。地点を等重みとし、同じ年を多く持つ地点を重くしない。', '',
 '正の値は後に記した種Bが種Aに対して相対的に遅れる変化、負は相対的に早まる変化。絶対的な種間日付差や繁殖の重複期間は推定せず、「差が広がる」とは一律に言わない。各種の一定の日付原点のずれは差の変化では相殺されるが、年ごとの変換誤差は解決しない。', '',
 '| A → B | 共通地点数 | 共通地点年 |','|---|---:|---:|']
for (a,b),s in pd.DataFrame(support).groupby(['first','second']):lines.append(f'| {a} → {b} | {len(s)} | {s.n_years.sum()} |')
lines+=['','## 世紀末SSP5-8.5：B−Aの変化（日）','','3モデルの範囲であり信頼区間ではない。','','| A → B | 年調整 | 最小 | 最大 |','|---|---|---:|---:|']
for r in ranges[(ranges.experiment_id=='ssp585')&(ranges.period=='2081-2100')].itertuples():lines.append(f'| {r.first} → {r.second} | {r.mode} | {r.min:+.2f} | {r.max:+.2f} |')
lines+=['','共通集合は2～4地理コードと少数で、南極全域の種間関係とは扱わない。地理コードが共通でも同一繁殖区画や同一海洋画素とは限らない。共通観測年への基準合わせは、共通の過去平年値を保証しない。環境外挿・水温製品差・係数不確実性が残り、独立な種間差の有意性検定ではない。','',
 '海氷日数・移行日の別シナリオとは混ぜない。これは気温・月平均海氷濃度・塩分・水温の同時回帰を用いた条件付き相対変化である。','',
 '再現：`python research/climate-penguin/work/scenario_support_v1/paired_species_future.py`']
lines+=['', 'scenario_gap_changes.csvには地点／年を1つずつ除いた係数による感度包絡も保存した。各種の削除係数から得た予測の全組合せの最小・最大であり、共通の削除を同期させた推定でも信頼区間でもない。元係数で方向が揃うことを、この包絡を無視して頑健な予測と呼ばない。']
(OUT/'REPORT_JA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(dict(passed=True,scenario_rows=72,site_rows=len(t),component_rows=len(parts),inputs={v:hashlib.sha256((ROOT/v).read_bytes()).hexdigest() for v in paths.values()}),indent=2)+'\n')
print(ranges[(ranges.experiment_id=='ssp585')&(ranges.period=='2081-2100')].to_string(index=False))
