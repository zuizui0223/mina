"""Cluster sign-flip sensitivity for all frozen duration/mean contrasts.

Separate site and year diagnostics do not guarantee calibrated two-way tests.
"""
from pathlib import Path
import hashlib,itertools,json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]/'outputs'
OUT=ROOT/'low_days_mean_inference_v1';OUT.mkdir(exist_ok=True)
source=ROOT/'low_days_mean_separation_v1/paired_features.csv'
reference=ROOT/'low_days_mean_separation_v1/comparisons.csv'
d=pd.read_csv(source);specs=pd.read_csv(reference)
rng=np.random.default_rng(20261030);rows=[];checks=0
for s in specs.itertuples():
    rec=s._asdict();rec.pop('Index')
    if s.status!='estimated':
        rows.append(rec);continue
    a=d[(d.window==s.window)&(d.threshold==s.threshold)&(d.inner_km==s.inner_km)]
    if s.scope!='all_annual':a=a[a.timing_supported]
    if s.scope.endswith('without_victoria'):a=a[a.region!='Victoria Land']
    assert len(a)==s.n
    z=pd.get_dummies(a.site_id,dtype=float).to_numpy()
    if s.mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.end,drop_first=True,dtype=float)])
    z=np.column_stack([z,a.mean_change10])
    u,_,_=np.linalg.svd(z,full_matrices=False);q=u[:,:np.linalg.matrix_rank(z)]
    x=a.duration_change10.to_numpy();y=a.log_growth.to_numpy()
    rx=x-q@(q.T@x);ry=y-q@(q.T@y)
    beta=rx@ry/(rx@rx);r=rx@ry/np.sqrt((rx@rx)*(ry@ry))
    np.testing.assert_allclose([beta,r],[s.beta_per_10days,s.r_after],atol=1e-8)
    h=rx/np.linalg.norm(rx);stat=(h@ry)**2
    design=np.column_stack([z,x])
    assert np.linalg.matrix_rank(design)==q.shape[1]+1
    for name,cluster in [('site',a.site_id),('year',a.end)]:
        labels,inv=np.unique(cluster,return_inverse=True);G=len(labels)
        enumerated=G<=12
        signs=np.array(list(itertools.product([-1.,1.],repeat=G))) if enumerated else rng.choice([-1.,1.],size=(9999,G))
        pseudo=ry[:,None]*signs[:,inv].T;values=(h@pseudo)**2
        exceed=int((values>=stat-1e-10).sum())
        rec[name+'_p']=exceed/len(values) if enumerated else (exceed+1)/(len(values)+1)
        rec[name+'_draws']=len(values);rec[name+'_enumerated']=enumerated
        for i in [0,len(values)//2,len(values)-1]:
            yp=q@(q.T@y)+pseudo[:,i]
            null=yp-z@np.linalg.lstsq(z,yp,rcond=None)[0]
            full=yp-design@np.linalg.lstsq(design,yp,rcond=None)[0]
            np.testing.assert_allclose(null@null-full@full,values[i],atol=1e-7)
            checks+=1
    rec['sensitivity_max_p']=max(rec['site_p'],rec['year_p']);rows.append(rec)
t=pd.DataFrame(rows);assert len(t)==48
p=t.sensitivity_max_p.fillna(1).to_numpy();order=np.argsort(p);m=len(p)
for method,factor in [('bh',1),('by',sum(1/i for i in range(1,m+1)))]:
    adjusted=np.minimum.accumulate((p[order]*m*factor/np.arange(1,m+1))[::-1])[::-1]
    out=np.empty(m);out[order]=np.minimum(1,adjusted);t['fdr_'+method]=out
t.to_csv(OUT/'tests.csv',index=False)
v=dict(passed=True,family_size=48,estimable=int(t.status.eq('estimated').sum()),
       explicit_pseudo_regression_checks=checks,seed=20261030,
       max_p_below_005=int(t.sensitivity_max_p.lt(.05).sum()),
       bh_below_005=int(t.fdr_bh.lt(.05).sum()),by_below_005=int(t.fdr_by.lt(.05).sum()),
       inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,reference]},
       limits=['Separate site/year diagnostics are not a calibrated joint two-way test',
               'Few informative sites, shared measurement errors and fitted nuisance terms limit inference',
               'Exploratory 48-specification family, not all comparisons in the research programme'])
(OUT/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
main=t[(t.scope=='timing_supported')&(t['mode']=='site_year')]
lines=['# 平均海氷濃度調整後の低海氷日数：有意性の感度', '',
    '前回と同じ48条件を保持し、平均濃度・地点（必要な条件では年）を調整した制限付き帰無残差を、地点または年単位で符号付替えした。12群以下では全符号割当、それ以外は9999回。両方のp値と大きい方を保存し、大きい方の48比較にBH/BY補正を適用。推定不能条件は補正時にp=1として家族内に残した。', '',
    f"推定可能{v['estimable']}/48条件。大きい方のp<0.05は{v['max_p_below_005']}件、BH補正後{v['bh_below_005']}件、BY補正後{v['by_below_005']}件。", '',
    '| 期間 | 閾値 | 距離帯 km | 調整後r | 地点p | 年p | 大きい方のp | BH |',
    '|---|---:|---:|---:|---:|---:|---:|---:|']
for r in main.itertuples():
    lines.append(f'| {r.window} | {r.threshold} | {r.inner_km} | {r.r_after:+.3f} | {r.site_p:.4f} | {r.year_p:.4f} | {r.sensitivity_max_p:.4f} | {r.fdr_bh:.4f} |')
lines+=['', '表は計数時期を確認した集合の地点＋年調整。nanは推定不能。相関が強まる条件を選んで検定したものではない。', '',
    'これは地点・年の依存への感度診断であり、両依存を同時に処理した厳密に校正済みの検定ではない。符号割当の全列挙も、残差の対称性や独立性を保証しない。少数の変化地点や地域偏在を解決せず、有意でない結果は無関連の証明ではない。因果的な融氷効果・輸送効果や将来巣数の予測は追加していない。', '',
    f"検証：元の係数・相関を照合し、{checks}個の擬似データについて全変数回帰の残差平方和差と計算統計量を照合。", '',
    '再現：`python research/climate-penguin/work/scenario_support_v1/low_days_mean_inference.py`']
(OUT/'REPORT_JA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(v));print(main[['window','threshold','inner_km','r_after','sensitivity_max_p','fdr_bh']].to_string(index=False))
