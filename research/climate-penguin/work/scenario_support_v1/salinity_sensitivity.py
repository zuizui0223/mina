"""Fixed-cohort salinity specification sensitivity; descriptive, no selection."""
from pathlib import Path
import hashlib,json
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[2];src=ROOT/'outputs/relationship_response_v1/cohort.csv'
OUT=ROOT/'outputs/salinity_sensitivity_v1';OUT.mkdir(exist_ok=True)
d=pd.read_csv(src)
specs={'none':[],'ice':['ice10'],'ice_water':['ice10','waterC'],'ice_water_air':['ice10','waterC','airC']}
def fit(a,mode,controls):
 z=pd.get_dummies(a.cam,dtype=float).to_numpy()
 if mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.year,drop_first=True,dtype=float)])
 base=a.salt01.to_numpy()-z@np.linalg.lstsq(z,a.salt01,rcond=None)[0]
 if controls:z=np.column_stack([z,a[controls].to_numpy()])
 v=a[['salt01','y']].to_numpy();r=v-z@np.linalg.lstsq(z,v,rcond=None)[0]
 xx=r[:,0]@r[:,0];yy=r[:,1]@r[:,1]
 beta=r[:,0]@r[:,1]/xx
 direct=np.linalg.lstsq(np.column_stack([z,a.salt01]),a.y,rcond=None)[0][-1]
 assert np.isclose(beta,direct,atol=1e-9)
 return dict(partial_r=(r[:,0]@r[:,1])/np.sqrt(xx*yy),coefficient_per_01=beta,salt_residual_fraction=xx/(base@base),residual_df=len(a)-np.linalg.matrix_rank(np.column_stack([z,a.salt01])))
rows=[];deletions=[]
for (scope,sp),a in d.groupby(['scope','species']):
 assert not a[['salt01','ice10','waterC','airC','y']].isna().any().any()
 for mode in ['site','site_year']:
  for name,controls in specs.items():
   key=dict(scope=scope,species=sp,mode=mode,controls=name)
   r=fit(a,mode,controls);r.update(key,n=len(a),sites=a.cam.nunique(),years=a.year.nunique());rows.append(r)
   for year in a.year.unique():
    q=fit(a[a.year!=year],mode,controls);q.update(key,deleted_year=int(year));deletions.append(q)
t=pd.DataFrame(rows);j=pd.DataFrame(deletions)
assert len(t)==48
summary=j.groupby(['scope','species','mode','controls']).partial_r.agg(year_delete_min='min',year_delete_max='max').reset_index()
t=t.merge(summary,validate='one_to_one');t.to_csv(OUT/'specifications.csv',index=False);j.to_csv(OUT/'year_deletions.csv',index=False)
lines=['# 塩分と定着指数：同じ観測で調整条件を比較','','同一169観測（アデリー41、ヒゲ41、ジェンツー87種×地点×季）を使い、塩分と定着指数の関連を、無追加調整・海氷調整・海氷＋水温調整・海氷＋水温＋気温調整で比較した。全変数の完全ケースを使うのはこの調整条件の比較に限る。変数ごとの全利用可能観測による相関一覧を置き換えない。付録整合集合147観測も別に全仕様を保持した。','','塩分は海洋再解析の表層値で、係数は元製品の塩分0.1単位あたりの定着指数変化。偏相関は、塩分と定着指数の両方から指定変数と固定効果を除いた残差の相関。調整変数は因果的な交絡因子と確定したものではなく、因果効果の推定ではない。','','| 種 | 固定効果 | 追加調整 | 偏相関 r | 係数 / 塩分0.1 | 塩分変動の残存割合 | 年を一つ除いた r の範囲 |','|---|---|---|---:|---:|---:|---|']
names={'Adelie':'アデリー','Chinstrap':'ヒゲ','Gentoo':'ジェンツー'}
for r in t[t.scope=='all_source_labels'].itertuples():
 lines.append(f'| {names[r.species]} | {r.mode} | {r.controls} | {r.partial_r:+.3f} | {r.coefficient_per_01:+.3f} | {r.salt_residual_fraction:.3f} | {r.year_delete_min:+.3f} ～ {r.year_delete_max:+.3f} |')
lines+=['','site は地点、site_year は地点＋年固定効果。none は追加環境調整なし、ice は海氷、water は水温、air は気温。塩分変動の残存割合は、同じ固定効果のみで残る塩分偏差平方和に対する割合であり、因果的な寄与率ではない。低い場合、海氷・水温等と塩分を個別に分離する情報が少ない。','','削除範囲は信頼区間や有意判定ではない。調整による符号反転は、独立した塩分効果の発見を意味しない。年固定効果は共通気候信号も除去し得るため、どちらの仕様も保持する。現在の観測関係を塩分の将来予測へ適用するには、モデル仕様に対する方向の安定性と将来塩分データの対応が別途必要。','','## 今回の読み取り','','アデリーは地点調整 r=+0.480、海氷・水温・気温も調整して +0.482。観測した3環境変数を線形に調整するだけでは正の相関は消えない。ただし地点＋年＋3環境では +0.213、年削除範囲 −0.028～+0.370 で、共通年変動との切り分けは不確実。ヒゲは地点調整 +0.564 から3環境調整 +0.354、地点＋年＋3環境では +0.007 とほぼ0。ジェンツーは地点＋年＋3環境で −0.159。いずれも探索的関連であり、有意性・因果性・機構の確認とは区別する。','','変数ごとの利用可能観測による先の相関一覧と数値が異なるのは、調整比較のため観測集合を固定したため。ジェンツーでは塩分のみ利用可能な95観測から87観測へ変わるだけでも、無追加調整の地点内相関は +0.076 から −0.014 に変わる。調整効果と観測選択効果を混同しない。','','## 再現と検証','','`python research/climate-penguin/work/scenario_support_v1/salinity_sensitivity.py`','','48仕様と各年削除の全回帰で、残差化から得た塩分係数を全ダミー・説明変数を同時投入した最小二乗係数と照合した。入力のハッシュ・元観測集合を保存。探索的比較なので、有意な条件だけの選別は行わない。']
(OUT/'REPORT_JA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'specifications':len(t),'year_deletion_fits':len(j),'direct_coefficient_checks':len(t)+len(j),'all_checks_passed':True},indent=2)+'\n')
print(t[(t.scope=='all_source_labels')&(t.controls.isin(['none','ice_water_air']))][['species','mode','controls','partial_r','salt_residual_fraction','year_delete_min','year_delete_max']].to_string(index=False))
