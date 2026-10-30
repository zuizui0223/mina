"""Delete-one-site/year sensitivity for every exploratory atlas association."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'outputs/correlation_atlas_v1/observation_points.csv'
OUT=ROOT/'outputs/correlation_influence_v1';OUT.mkdir(exist_ok=True)
points=pd.read_csv(SOURCE)
def estimate(d):
 between=d.groupby('cam')[['x','y']].mean().corr().loc['x','y']
 v=d[['x','y']].to_numpy()
 site=pd.get_dummies(d.cam,dtype=float).to_numpy()
 within=v-site@np.linalg.lstsq(site,v,rcond=None)[0]
 both=np.column_stack([site,pd.get_dummies(d.season_start_year,drop_first=True,dtype=float)])
 sy=v-both@np.linalg.lstsq(both,v,rcond=None)[0]
 def corr(v):
  return np.corrcoef(v.T)[0,1] if np.all(np.std(v,axis=0)>1e-10) else np.nan
 return {'between':between,'within':corr(within),'site_year':corr(sy)}
rows=[];base=[]
for (feature,species),d in points.groupby(['feature','species']):
 b=estimate(d)
 for mode,r in b.items():base.append(dict(feature=feature,species=species,mode=mode,r=r))
 for cluster in ['cam','season_start_year']:
  for group in sorted(d[cluster].unique()):
   a=d[d[cluster]!=group].copy()
   # Re-estimate means and all fixed effects after deletion, especially years.
   for mode,r in estimate(a).items():
    rows.append(dict(feature=feature,species=species,mode=mode,deleted_axis=cluster,deleted_group=str(group),n=len(a),sites=a.cam.nunique(),years=a.season_start_year.nunique(),r=r,full_r=b[mode],change=r-b[mode],same_sign=bool(r*b[mode]>0) if np.isfinite(r) else None))
details=pd.DataFrame(rows);summary=[]
for key,g in details.groupby(['feature','species','mode','deleted_axis']):
 finite=g[g.r.notna()]; rec=dict(zip(['feature','species','mode','deleted_axis'],key))
 rec.update(full_r=g.full_r.iloc[0],deletions=len(g),valid=len(finite),minimum=finite.r.min(),maximum=finite.r.max(),same_sign_count=int(finite.same_sign.sum()))
 if len(finite):rec['largest_change_group']=finite.loc[finite.change.abs().idxmax(),'deleted_group'];rec['largest_absolute_change']=finite.change.abs().max()
 summary.append(rec)
s=pd.DataFrame(summary)
assert len(s)==126
atlas=pd.read_csv(ROOT/'outputs/correlation_atlas_v1/correlations.csv')
for r in pd.DataFrame(base).itertuples():
 a=atlas[(atlas.species==r.species)&(atlas.feature==r.feature)].iloc[0]
 assert np.isclose(r.r,a[{'between':'between_r','within':'within_r','site_year':'site_year_r'}[r.mode]],atol=1e-10)
# Independent centering check after every year deletion (must not reuse old deviations).
for (feature,species),d in points.groupby(['feature','species']):
 for year in d.season_start_year.unique():
  a=d[d.season_start_year!=year].copy();v=a[['x','y']]-a.groupby('cam')[['x','y']].transform('mean')
  expected=v.corr().loc['x','y']
  got=details[(details.feature==feature)&(details.species==species)&(details['mode']=='within')&(details.deleted_axis=='season_start_year')&(details.deleted_group==str(year))].r.item()
  assert np.isclose(got,expected,atol=1e-10)
details.to_csv(OUT/'deletion_results.csv',index=False);s.to_csv(OUT/'summary.csv',index=False)
lines=['# 相関は一つの地点・年に左右されるか','','環境7項目×3種の相関一覧を対象に、地点（cam）または年ラベルを一つずつ除き、場所間・地点内・地点＋年の相関を再推定した。削除後の地点平均と固定効果を毎回再計算し、全データで作った偏差を使い回していない。全21関係・3仕様を保持した。','','以下は地点内相関。範囲は削除感度の最小～最大であり、信頼区間・有意性・将来予測区間ではない。符号が保たれても、交絡や複数の影響地点への頑健性を証明しない。','','| 環境 | 種 | 全データ r | 地点を一つ除いた範囲 | 年を一つ除いた範囲 |','|---|---|---:|---|---|']
names={'Adelie':'アデリー','Chinstrap':'ヒゲ','Gentoo':'ジェンツー'}
for (feature,species),g in s[s['mode']=='within'].groupby(['feature','species']):
 a=g[g.deleted_axis=='cam'].iloc[0];b=g[g.deleted_axis=='season_start_year'].iloc[0]
 lines.append(f'| {feature} | {names[species]} | {a.full_r:+.3f} | {a.minimum:+.3f} ～ {a.maximum:+.3f} | {b.minimum:+.3f} ～ {b.maximum:+.3f} |')
lines+=['','## 海氷と定着指数：年調整後も確認','','| 種 | 全データ r（地点＋年） | 地点を一つ除いた範囲 | 年を一つ除いた範囲 |','|---|---:|---|---|']
for species in names:
 g=s[(s.feature=='Near sea ice')&(s.species==species)&(s['mode']=='site_year')];a=g[g.deleted_axis=='cam'].iloc[0];b=g[g.deleted_axis=='season_start_year'].iloc[0]
 lines.append(f'| {names[species]} | {a.full_r:+.3f} | {a.minimum:+.3f} ～ {a.maximum:+.3f} | {b.minimum:+.3f} ～ {b.maximum:+.3f} |')
lines+=['','## 将来シナリオへの位置づけ','','アデリーの近傍海氷と定着指数の正の相関は、地点内・地点＋年の両仕様で、どの地点または年を一つ除いても維持された。地点＋年の削除範囲は全体で +0.212 ～ +0.505。単一地点・単一年だけで生じた関連ではないという支持になる。一方、ヒゲとジェンツーは年の削除で符号が変わり、方向を固定した将来解釈には慎重さが必要。','','安定した符号を将来効果の確定とせず、観測関係を仮定するシナリオの根拠の一つとして扱う。単変量相関と気温・海氷を同時投入した回帰係数は異なる。今回の削除感度は前者の検証であり、将来シナリオの回帰係数が同様に安定していると主張する根拠にはしない。','','地点はカメラ識別子であり独立な島ではない。全地点に共通する年の環境・観測変化は残り得る。削除試行は互いに強く重複するため、符号維持の割合を確率やp値として解釈しない。','','## 再現と検証','','`python research/climate-penguin/work/scenario_support_v1/correlation_influence.py`','','63個の全データ相関が既存一覧と一致すること、各年の削除後の地点内相関がgroupbyで独立に中心化した値と一致することを確認。全削除値と最大変化を生じる地点・年をCSVに保存した。']
(OUT/'REPORT_JA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'full_correlations_checked':63,'summary_rows':len(s),'deletion_estimates':len(details),'nonfinite_estimates':int(details.r.isna().sum()),'year_deletion_centering_independently_checked':True},indent=2)+'\n')
print(s[(s.feature=='Near sea ice')&(s['mode'].isin(['within','site_year']))].to_string(index=False))
