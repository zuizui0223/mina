"""Evidence registry for context-specific exploratory manuscript findings.

No refitting, retrospective family shrinking, or independence assumption across
specifications. This is an explicit subset of documented analysis families.
"""
from pathlib import Path
import hashlib,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]/'outputs'
OUT=ROOT/'manuscript_context_v1';OUT.mkdir(exist_ok=True)
definitions=[
 ('settlement_216','climate_penguin/exploratory_significance_results.csv','p','q_bh','q_by'),
 ('settlement_216_wild_sensitivity','climate_penguin/wild_cluster_sensitivity_results.csv','p_wild_max','q_wild_max_bh','q_wild_max_by'),
 ('duration_count_48','low_ice_days_count_v1/associations.csv','p','fdr_bh','fdr_by'),
 ('duration_count_48_sign_sensitivity','low_ice_days_count_v1/associations.csv','sensitivity_max_p','sign_fdr_bh','sign_fdr_by'),
 ('duration_given_mean_48','low_days_mean_inference_v1/tests.csv','sensitivity_max_p','fdr_bh','fdr_by'),
 ('salinity_48_site_year','salinity_cluster_sensitivity_v1/tests.csv','sensitivity_max_p','fdr_bh','fdr_by'),
 ('salinity_48_grid_year','salinity_grid_cluster_v1/tests.csv','sensitivity_max_p','fdr_bh','fdr_by')]
rows=[];inputs={}
for family,path,p,bh,by in definitions:
    a=pd.read_csv(ROOT/path)
    rows.append(dict(family=family,comparisons=len(a),finite_p=int(a[p].notna().sum()),
        raw_below_005=int(a[p].lt(.05).sum()),bh_below_005=int(a[bh].lt(.05).sum()),
        by_below_005=int(a[by].lt(.05).sum()),source=path,p_field=p,bh_field=bh,by_field=by))
    inputs[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
summary=pd.DataFrame(rows);summary.to_csv(OUT/'family_inventory.csv',index=False)
original=pd.read_csv(ROOT/definitions[0][1]);wild=pd.read_csv(ROOT/definitions[1][1])
keys=['cohort','species','predictor','time_mode']
joined=original.merge(wild[keys+['p_wild_site','p_wild_year','q_wild_site_bh','q_wild_year_bh','q_wild_max_bh']],on=keys,validate='one_to_one')
assert len(joined)==216
joined.to_csv(OUT/'settlement_all_comparisons.csv',index=False)
selected=joined[joined.q_by.lt(.05)]
assert len(selected)==3
selected.to_csv(OUT/'settlement_by_candidates.csv',index=False)
counts=pd.read_csv(ROOT/definitions[2][1])
counts[counts.fdr_by.lt(.05)].to_csv(OUT/'count_by_candidates.csv',index=False)
assert counts.fdr_by.lt(.05).sum()==3
lines=['# 種・場所・時期に限定した関連を中心にする論文の結果台帳', '',
    'ユーザーの2026-10-30の方針：共通性・普遍性を採用条件にせず、条件を限定した有意な相関と探索的予測を論文の中心にする。全結果を保持し、有意になった条件だけに検定家族を縮めない。', '',
    '## 登録した比較群', '',
    '下表は本稿の核として確認した比較群。リポジトリ内の全解析を網羅した数ではない。同じ関係の検定法違い・標本違いを含むので、行を合計して独立な発見数にしない。', '',
    '| 比較群 | 比較数 | p<0.05 | BH<0.05 | BY<0.05 |','|---|---:|---:|---:|---:|']
for r in summary.itertuples():lines.append(f'| {r.family} | {r.comparisons} | {r.raw_below_005} | {r.bh_below_005} | {r.by_below_005} |')
lines+=['','## 定着時期のBY補正後候補と検定感度','','| 種 | 環境指標 | 集合／調整 | n | r | 近似p | BY | 地点wild p | 年wild p |','|---|---|---|---:|---:|---:|---:|---:|---:|']
for r in selected.itertuples():
    lines.append(f'| {r.species} | {r.predictor} | {r.cohort}/{r.time_mode} | {r.code_seasons} | {r.adjusted_r:+.3f} | {r.p:.6g} | {r.q_by:.4f} | {r.p_wild_site:.4f} | {r.p_wild_year:.4f} |')
lines+=['','近似検定で有意だった事実を残す。一方、帰無再標本化では多重比較後に維持されず、推論法に依存する探索的関連として扱う。非有意な結果を無関係とは記述しない。','',
    '## 予測との対応','',
    '既存の72試算は気温・平均海氷濃度・塩分・水温の同時回帰である。上の有意候補である低海氷日数・流動・移行日の係数をそのまま未来に適用した予測ではない。したがって「有意だった海氷流動から繁殖時期を予測した」とは書かない。予測は観測関連を将来環境へ接続した別の探索解析として並置する。','',
    '塩分の相関・年成分分解、植生の地域依存の相関は記述的な結果として掲載可能。ただしこの台帳から、塩分や植生で補正後の頑健な有意関連が確認されたとは主張しない。','',
    '再現：`python research/climate-penguin/work/scenario_support_v1/manuscript_candidates.py`。入力ハッシュ、全216比較、候補抽出条件、各比較群の検定列を保存。']
(OUT/'EVIDENCE_JA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(dict(passed=True,registered_family_rows=len(summary),settlement_join_rows=216,settlement_by_candidates=3,count_by_candidates=3,inputs=inputs,scope='Evidence indexing, not new statistical tests or a repository-wide significance count'),indent=2)+'\n')
print(summary.to_string(index=False));print(selected[keys+['code_seasons','adjusted_r','p','q_by']].to_string(index=False))
