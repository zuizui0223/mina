"""Decompose existing conditional scenarios, without refitting or selection."""
from pathlib import Path
import hashlib, json, shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'outputs/conditional_response_v1'
OUT=ROOT/'outputs/scenario_components_v1'; OUT.mkdir(exist_ok=True)
paths=[SRC/f for f in ['site_index_shifts.csv','coefficients.csv','conditional_summary.csv']]
sites,coef,summary=[pd.read_csv(p) for p in paths]
d=sites.merge(coef[['scope','species','mode','air_coefficient','ice10_coefficient']],on=['scope','species','mode'],validate='many_to_one')
d['air_component']=d.delta_air*d.air_coefficient
d['ice_component']=d.delta_ice10*d.ice10_coefficient
valid=d.physical_ice.eq(True)
assert np.allclose((d.air_component+d.ice_component)[valid],d.index_shift[valid],atol=1e-12)
d.loc[~valid,['air_component','ice_component']]=np.nan
keys=['scope','species','mode','transform','source_id','experiment_id','period']
rows=[]
for key,g in d.groupby(keys):
 r=dict(zip(keys,key)); r['n_sites']=len(g)
 complete=bool(g.physical_ice.all()); r['all_sites_physical']=complete
 for col in ['air_component','ice_component','index_shift']:
  r[col]=g[col].mean() if complete else np.nan
 r['components_oppose']=bool(r['air_component']*r['ice_component']<0) if complete else None
 rows.append(r)
s=pd.DataFrame(rows).merge(summary,on=keys,validate='one_to_one')
assert len(s)==288 and len(d)==3936
assert np.allclose(s.index_shift,s.mean_index_shift,equal_nan=True)
assert np.allclose(s.air_component+s.ice_component,s.mean_index_shift,equal_nan=True)
d.to_csv(OUT/'site_components.csv',index=False);s.to_csv(OUT/'summary.csv',index=False)
show=s[(s.scope=='all_source_labels')&(s['mode']=='site')&(s['transform']=='bounded')&(s.period=='2081-2100')&(s.experiment_id=='ssp585')]
fig,axes=plt.subplots(1,3,figsize=(12,4.5),layout='constrained',sharey=True)
for ax,sp in zip(axes,['Adelie','Chinstrap','Gentoo']):
 g=show[show.species==sp].sort_values('source_id');x=np.arange(len(g))
 ax.bar(x-.16,g.air_component,width=.3,color='#d77835',label='Air temperature')
 ax.bar(x+.16,g.ice_component,width=.3,color='#298fa1',label='Sea ice')
 ax.scatter(x,g.mean_index_shift,color='#282828',marker='D',label='Combined',zorder=4)
 ax.axhline(0,color='#666',lw=.7);ax.set_xticks(x,g.source_id,rotation=20,ha='right');ax.set_title(sp)
 ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('Conditional settlement-index change')
axes[0].legend(loc='upper left',fontsize=9)
fig.suptitle('How warming and sea-ice changes combine\nSSP5-8.5, 2081-2100; site effects, bounded ice transformation; point estimates only')
fig.savefig(OUT/'components.png',dpi=160);plt.close(fig)
lines=['# 相関から将来シナリオへ：気温と海氷の成分分解','','既存の2変数回帰を再推定せず、将来の定着指数変化を気温成分（気温係数×気温変化）と海氷成分（海氷係数×海氷濃度変化）へ分解した。相関係数 r を将来変化に直接掛けていない。これは統計的な成分分解であり、独立した因果経路の寄与率ではない。','','## 世紀末・高排出シナリオの例','','主集合、地点固定効果、有界海氷変換、SSP5-8.5、2081–2100年。種内の地点を等重みにした指数変化。数値は日数ではない。','','| 種 | 気候モデル | 気温成分 | 海氷成分 | 合計 | 年再標本化範囲（合計） |','|---|---|---:|---:|---:|---|']
names={'Adelie':'アデリー','Chinstrap':'ヒゲ','Gentoo':'ジェンツー'}
for r in show.itertuples():
 lines.append(f'| {names[r.species]} | {r.source_id} | {r.air_component:+.2f} | {r.ice_component:+.2f} | {r.mean_index_shift:+.2f} | {r.year_resample_low:+.2f} ～ {r.year_resample_high:+.2f} |')
lines+=['','![成分分解](components.png)','','範囲は既存の年単位係数再標本化による合計の感度範囲であり、将来予測全体の区間ではない。成分ごとの区間は今回算出していない。共有する係数の共分散があるため、別々の成分の区間を足し合わせる方法は使わない。','','## 解釈と全仕様の保持','','この地点固定効果の例では、アデリー・ジェンツーは気温成分と海氷成分が同方向、ヒゲは反対方向となる。ただし、年固定効果や付録整合集合では係数が変わるため、確立した種差とは扱わない。ヒゲの海氷の単変量地点内相関はほぼ0なのに、気温を同時投入した係数は負となる。これは条件付きの関連であり、単変量相関の結果と区別する。','','気温と海氷は相互に関連する説明変数なので、成分の大きさはモデル仕様に依存する。場所間相関と地点内相関の不一致に加え、地点＋年固定効果の結果も全件CSVに保持した。共有する年変動を除くと、実際の広域気候信号も失われ得る。どちらか一つを正解として選ばない。','','全3気候モデル・2排出シナリオ・2将来期間・2観測集合・2固定効果仕様・2海氷変換の288要約と3936地点別結果を保持。単純加算で海氷が0–100%を外れる地点があれば、その種の平均を計算しない既存規則を継承した。','','この計算は環境と定着指数の観測関係が将来も続く場合の条件付き変化。到着日・繁殖成功・個体数の予測ではなく、温暖化の因果効果や海氷による移動補助の機構も識別しない。塩分・流動・植生・積雪の将来変化は未投入。気候モデルの内部変動と応答モデルの構造的不確実性は表の範囲に全て含まれない。','','## 再現と検証','','`python research/climate-penguin/work/scenario_support_v1/scenario_components.py`','','有効な全地点で2成分の和が既存の指数変化と一致し、全288要約が既存の種平均・欠測規則と一致することを確認。既存の相関一覧は `../correlation_atlas_v1/REPORT_JA.md`、条件付き計算の方法・外挿範囲は `../conditional_response_v1/REPORT_JA.md`。']
(OUT/'REPORT_JA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'site_rows':len(d),'summary_rows':len(s),'physical_site_rows':int(valid.sum()),'all_component_sums_match':True,'all_summary_missingness_matches':True,'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}},indent=2)+'\n')
print(show[['species','source_id','air_component','ice_component','mean_index_shift']].to_string(index=False))
