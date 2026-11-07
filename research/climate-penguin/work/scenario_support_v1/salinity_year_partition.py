"""Orthogonal covariance accounting on frozen cohorts; not causal attribution."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/salinity_year_partition_v1'
OUT.mkdir(exist_ok=True)
source = ROOT / 'outputs/relationship_response_v1/cohort.csv'
reference = ROOT / 'outputs/salinity_sensitivity_v1/specifications.csv'
data = pd.read_csv(source)
frozen = pd.read_csv(reference)
controls = {'none': [], 'ice': ['ice10'], 'ice_water': ['ice10', 'waterC'],
            'ice_water_air': ['ice10', 'waterC', 'airC']}

def residual(z, v):
    return v - z @ np.linalg.lstsq(z, v, rcond=None)[0]

rows, observations = [], []
for (scope, species), a in data.groupby(['scope', 'species']):
    a = a.reset_index(drop=True)
    v = a[['salt01', 'y']].to_numpy()
    year = pd.get_dummies(a.year, drop_first=True, dtype=float).to_numpy()
    for label, columns in controls.items():
        z = np.column_stack([pd.get_dummies(a.cam, dtype=float), a[columns]])
        base = residual(z, v)
        # Residualize the year design too: raw annual means are not equivalent
        # in this unbalanced panel with site and environmental adjustment.
        year_design = residual(z, year)
        common = year_design @ np.linalg.lstsq(year_design, base, rcond=None)[0]
        remaining = base - common
        direct = residual(np.column_stack([z, year]), v)
        np.testing.assert_allclose(remaining, direct, atol=1e-8)
        np.testing.assert_allclose(common.T @ remaining, np.zeros((2, 2)), atol=1e-7)
        gram = base.T @ base
        cg, rg = common.T @ common, remaining.T @ remaining
        np.testing.assert_allclose(gram, cg + rg, atol=1e-7)
        scale = np.sqrt(gram[0, 0] * gram[1, 1])
        r_base = gram[0, 1] / scale
        r_remaining = rg[0, 1] / np.sqrt(rg[0, 0] * rg[1, 1])
        match = frozen[(frozen.scope == scope) & (frozen.species == species)
                       & (frozen.controls == label)]
        for mode, value in [('site', r_base), ('site_year', r_remaining)]:
            np.testing.assert_allclose(value, match.loc[match['mode'] == mode, 'partial_r'].item(), atol=1e-9)
        key = dict(scope=scope, species=species, controls=label)
        rows.append(dict(**key, n=len(a), sites=a.cam.nunique(), years=a.year.nunique(),
            r_site=r_base, r_site_year=r_remaining,
            salt_ss_common_year=cg[0, 0] / gram[0, 0],
            response_ss_common_year=cg[1, 1] / gram[1, 1],
            common_year_covariance_scaled=cg[0, 1] / scale,
            remaining_covariance_scaled=rg[0, 1] / scale))
        for i, observation in a.iterrows():
            observations.append(dict(**key, cam=observation.cam, year=observation.year,
                salt_base=base[i, 0], response_base=base[i, 1],
                salt_common=common[i, 0], response_common=common[i, 1],
                salt_remaining=remaining[i, 0], response_remaining=remaining[i, 1]))

result = pd.DataFrame(rows)
assert len(result) == 24
result.to_csv(OUT / 'partition.csv', index=False)
pd.DataFrame(observations).to_csv(OUT / 'observation_components.csv', index=False)
main = result[(result.scope == 'all_source_labels') & (result.controls == 'ice_water_air')]
lines = ['# 塩分と定着時期：共通年変動と残る共変動', '',
    '同一の主169観測と付録147観測を保持し、既存の24条件を分解した。地点と指定環境変数を除いた塩分・定着時期について、年ダミーが表現する成分を直交射影で求めた。不均衡な地点年パネルなので、単純な年平均の相関ではない。', '',
    '以下は海氷・水温・気温を調整した主集合。変動割合は、これらと地点差を除いた後の偏差平方和に対する割合。', '',
    '| 種 | 観測数 | 年成分に重なる塩分変動 | 年成分に重なる定着時期変動 | 元の相関 | 年成分の共変動 | 残る共変動 | 年調整後の相関 |',
    '|---|---:|---:|---:|---:|---:|---:|---:|']
for r in main.itertuples():
    lines.append(f'| {r.species} | {r.n} | {r.salt_ss_common_year:.1%} | {r.response_ss_common_year:.1%} | {r.r_site:+.3f} | {r.common_year_covariance_scaled:+.3f} | {r.remaining_covariance_scaled:+.3f} | {r.r_site_year:+.3f} |')
lines += ['', '年成分と残る共変動は、どちらも元の残差標準偏差の積で規格化した値で、足すと元の相関になる。一方、年調整後の相関は残る変動だけで規格化するため、残る共変動と数値が異なる。', '',
    '共通年成分は温暖化や塩分の因果効果ではない。未測定の環境、観測条件、時間傾向も含み得る。年効果を除いて相関が弱まることは、広域気候との関連がないという証拠にもならない。年調整の有無は異なる問いとして併記する。', '',
    '探索的な記述分解であり、有意性検定や新しい将来予測を追加していない。年成分は年ごとの自由な効果なので、観測していない未来の年へ外挿できない。既存の多重比較結果をこの分解の有意性に流用しない。', '',
    '検証：24条件で共変動行列の加法性と直交性を確認。逐次射影と全変数同時回帰の残差を照合。地点調整・地点＋年調整の48相関を凍結表と照合した。観測ごとの成分を保存。', '',
    '再現：`python research/climate-penguin/work/scenario_support_v1/salinity_year_partition.py`', '',
    '主集合では、アデリーの元の相関+0.482は共通年成分+0.409と残る共変動+0.073に分かれた。ヒゲは+0.354のうち年成分+0.352、残る共変動+0.002。ジェンツーは負の共変動が年成分−0.069と残る成分−0.070の双方にあった。これは相関が現れる時間・空間成分の違いであり、種間の因果効果差の検定ではない。']
(OUT / 'REPORT_JA.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
(OUT / 'validation.json').write_text(json.dumps(dict(passed=True, specifications=24,
    frozen_correlation_matches=48, inputs={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, reference]},
    claim='Descriptive orthogonal accounting, not climate attribution or mediation'), indent=2) + '\n')
print(main.to_string(index=False))
