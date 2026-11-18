"""Deliver day-scale exploratory forecasts from frozen observed associations.

All models and both year-adjustment specifications retained, no significance gate.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]/'outputs'
OUT=ROOT/'association_forecast_v1';OUT.mkdir(exist_ok=True)
paths=[ROOT/'four_environment_scenarios_v1'/f for f in ['site_components.csv','coefficients.csv','summary.csv']]
sites,coef,frozen=[pd.read_csv(p) for p in paths]
sites=sites[(sites.scope=='all_source_labels')&(sites['transform']=='bounded')].copy()
coef=coef[coef.scope=='all_source_labels']
assert sites.physical_ice.all()
features=['airC','ice10','salt01','waterC'];rows=[]
for (sp,mode,model,member,scenario,period),a in sites.groupby(['species','mode','source_id','member_id','experiment_id','period']):
    b=coef[(coef.species==sp)&(coef['mode']==mode)].iloc[0]
    parts=a[['delta_'+f for f in features]].to_numpy()*b[features].to_numpy(dtype=float)
    np.testing.assert_allclose(parts.sum(axis=1),a.index_shift,atol=1e-9)
    key=dict(species=sp,mode=mode,source_id=model,member_id=member,experiment_id=scenario,period=period)
    r=dict(**key,sites=len(a),days_shift=float(parts.sum(axis=1).mean()),
           outside_joint_support=int(a.outside_four_variable_hull.sum()))
    r.update({f+'_days':float(parts[:,i].mean()) for i,f in enumerate(features)})
    ref=frozen[(frozen.scope=='all_source_labels')&(frozen['transform']=='bounded')]
    for k,v in key.items():ref=ref[ref[k]==v]
    assert len(ref)==1
    np.testing.assert_allclose(r['days_shift'],ref.mean_index_shift.item(),atol=1e-9)
    r['site_delete_low']=ref.cam_coefficient_delete_min.item()
    r['site_delete_high']=ref.cam_coefficient_delete_max.item()
    r['year_delete_low']=ref.year_coefficient_delete_min.item()
    r['year_delete_high']=ref.year_coefficient_delete_max.item()
    rows.append(r)
t=pd.DataFrame(rows);assert len(t)==72
t.to_csv(OUT/'model_forecasts.csv',index=False)
summary=t.groupby(['species','mode','experiment_id','period']).agg(
    models=('source_id','nunique'),minimum_days=('days_shift','min'),maximum_days=('days_shift','max'),
    min_extrapolated_sites=('outside_joint_support','min'),max_extrapolated_sites=('outside_joint_support','max'),
    sites=('sites','first')).reset_index()
assert len(summary)==24 and summary.models.eq(3).all()
summary.to_csv(OUT/'forecast_ranges.csv',index=False)
names={'Adelie':'アデリー','Chinstrap':'ヒゲ','Gentoo':'ジェンツー'}
lines=['# 観測された関連を使った定着時期の探索的予測', '',
    '既存の相関が将来も続くと仮定し、観測期間の各地点の環境から将来環境への変化を回帰係数に掛けた試算。定着時期の変化を日数で示す。負は早まる方向、正は遅れる方向。個体の帰還日や産卵日、繁殖数の予測ではない。', '',
    '主表示は気温・海氷・塩分・水温の4要因、主観測集合169件、有界海氷変換。塩分との正の相関を理由に係数の符号を固定せず、全係数を同時に用いた。共通年変動を含む地点調整と、除く地点＋年調整を両方提示する。どちらを正解と決めたものでもない。', '',
    '3気候モデル（ACCESS-CM2、BCC-CSM2-MR、CESM2）各1メンバー。2050年前後は2041–2060年、世紀末は2081–2100年の平均条件。基準は各地点で観測のある年に対応するモデル環境で、全地点共通の平年値ではない。', '',
    '## 全シナリオの試算', '',
    '各欄は3気候モデルの最小～最大（日）。信頼区間・予測区間・確率ではない。範囲が0をまたぐ場合は気候モデル間でも方向が異なる。', '',
    '| 種 | 排出シナリオ | 将来期間 | 共通年変動を含む | 共通年変動を除く |',
    '|---|---|---|---:|---:|']
for (sp,scenario,period),a in summary.groupby(['species','experiment_id','period']):
    values=[]
    for mode in ['site','site_year']:
        r=a[a['mode']==mode].iloc[0];values.append(f'{r.minimum_days:+.2f} ～ {r.maximum_days:+.2f}')
    lines.append(f'| {names[sp]} | {scenario} | {period} | {values[0]} | {values[1]} |')
lines+=['', '## 世紀末SSP5-8.5：何が予測値を動かすか', '',
    '地点調整モデルについて全3モデルを列挙。列の和が合計になる（丸め誤差あり）。これは同時回帰の計算成分で、各環境の因果寄与ではない。', '',
    '| 種 | 気候モデル | 気温 | 海氷 | 塩分 | 水温 | 合計（日） | 観測の4変数組合せ範囲外 |',
    '|---|---|---:|---:|---:|---:|---:|---:|']
for r in t[(t['mode']=='site')&(t.experiment_id=='ssp585')&(t.period=='2081-2100')].itertuples():
    lines.append(f'| {names[r.species]} | {r.source_id} | {r.airC_days:+.2f} | {r.ice10_days:+.2f} | {r.salt01_days:+.2f} | {r.waterC_days:+.2f} | {r.days_shift:+.2f} | {r.outside_joint_support}/{r.sites} |')
lines+=['', '## 読み取りと予測の範囲', '',
    '4環境・地点調整の世紀末SSP5-8.5では、アデリーは3モデルとも遅れる方向、ヒゲは3モデルとも早まる方向になる。一方、ヒゲは年調整後に遅れる方向へ変わる。アデリーでも気温・海氷だけの既存2環境モデルは早まる方向だった。したがって4環境モデルの種別予測は検証対象となる仮説であり、採用済みの確定予報ではない。', '',
    'アデリーの水温係数は観測時の条件付き変動幅が小さい状況で推定され、将来変化には大きな外挿がある。大きな水温成分を強い生物学的効果と読まない。海面水温変化を再解析の最上層ポテンシャル水温の代理として使う製品差も残る。', '',
    '地点・年を一つずつ除いた係数感度をmodel_forecasts.csvに保存。これも信頼区間ではない。海氷の日数・流動、植生、混合層、餌環境を含む将来効果は未計算で、効果が0と判定したわけではない。将来環境の極端年や内部変動、全観測誤差も予測幅には含まれない。', '',
    'この試算で具体化した問いは「4環境の観測関係が続けばアデリーは遅れ、ヒゲは早まるという種別の予測が、未使用年・地域でも成り立つか」。新たな独立データで検証する予測であり、既存データだけで仮説が確証されたとは言わない。', '',
    '再現：`python research/climate-penguin/work/scenario_support_v1/association_forecast.py`。全地点の係数×環境差から再計算し、72要約を凍結結果と照合。モデル選別や新しい回帰当てはめは行っていない。']
(OUT/'REPORT_JA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(dict(passed=True,model_forecasts=72,range_rows=24,
    scope='Exploratory association forecast; frozen regressions and future environments, not newly fitted or calibrated',
    inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2)+'\n')
print(summary.to_string(index=False))
