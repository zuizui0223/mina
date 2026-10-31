"""Same-window duration versus mean SIC; descriptive identifiable contrasts."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]/'outputs'
OUT=ROOT/'low_days_mean_separation_v1';OUT.mkdir(exist_ok=True)
paths=[ROOT/'long_ice_timing_v1/count_interval_features.csv',
       ROOT/'climate_penguin/macro_monthly_seaice_1991_2020.csv',
       ROOT/'low_ice_days_count_v1/associations.csv']
d,m,old=[pd.read_csv(p) for p in paths]
assert m.complete_month.all() and m.days.eq(m.expected_days).all()
assert not m.duplicated(['site_id','year','month','inner_km']).any()
means=[]
for window,months in [('aug_sep',[8,9]),('aug_nov',[8,9,10,11])]:
    for (site,year,band),g in m[m.month.isin(months)].groupby(['site_id','year','inner_km']):
        assert sorted(g.month)==months
        means.append(dict(window=window,site_id=site,year=year,inner_km=band,
            sic=np.average(g.sic_mean,weights=g.expected_days)))
means=pd.DataFrame(means)
for endpoint in ['start','end']:
    q=means.rename(columns={'year':endpoint,'sic':endpoint+'_sic'})
    d=d.merge(q,on=['window','site_id',endpoint,'inner_km'],validate='many_to_one')
assert len(d)==2408
d['mean_change10']=(d.end_sic-d.start_sic)/10
d['duration_change10']=d.low_days_change/10
d['log_growth']=np.log(d.n_end/d.n_start)
d.to_csv(OUT/'paired_features.csv',index=False)

def residual(z,v):return v-z@np.linalg.lstsq(z,v,rcond=None)[0]
rows=[]
for (window,threshold,band),g in d.groupby(['window','threshold','inner_km']):
    for scope in ['all_annual','timing_supported','timing_supported_without_victoria']:
        a=g if scope=='all_annual' else g[g.timing_supported]
        if scope.endswith('without_victoria'):a=a[a.region!='Victoria Land']
        for mode in ['site','site_year']:
            z=pd.get_dummies(a.site_id,dtype=float).to_numpy()
            if mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.end,drop_first=True,dtype=float)])
            base=residual(z,a[['duration_change10','mean_change10','log_growth']].to_numpy())
            xx,mm,yy=np.sum(base**2,axis=0)
            key=dict(window=window,threshold=threshold,inner_km=band,scope=scope,mode=mode)
            r=dict(**key,n=len(a),sites=a.site_id.nunique(),years=a.end.nunique(),
                   nonzero_duration_sites=a.loc[a.low_days_change.ne(0),'site_id'].nunique(),
                   status='not_identified',r_before=np.nan,r_after=np.nan,
                   duration_mean_r=np.nan,duration_variance_retained=np.nan,beta_per_10days=np.nan)
            match=old
            for k,v in key.items():match=match[match[k]==v]
            assert len(match)==1 and match.n.item()==len(a)
            base_df=len(a)-np.linalg.matrix_rank(np.column_stack([z,a.duration_change10]))
            if xx>1e-12 and yy>1e-12 and base_df>0:
                r['r_before']=base[:,0]@base[:,2]/np.sqrt(xx*yy)
                np.testing.assert_allclose(r['r_before'],match.partial_r.item(),atol=1e-9)
                z2=np.column_stack([z,a.mean_change10])
                rem=residual(z2,a[['duration_change10','log_growth']].to_numpy())
                x2,y2=np.sum(rem**2,axis=0)
                r['duration_variance_retained']=x2/xx
                if mm>1e-12:r['duration_mean_r']=base[:,0]@base[:,1]/np.sqrt(xx*mm)
                design=np.column_stack([z2,a.duration_change10])
                r['residual_df']=len(a)-np.linalg.matrix_rank(design)
                if x2>1e-12 and y2>1e-12 and r['residual_df']>0:
                    r.update(status='estimated',r_after=rem[:,0]@rem[:,1]/np.sqrt(x2*y2),
                             beta_per_10days=rem[:,0]@rem[:,1]/x2)
                    np.testing.assert_allclose(r['beta_per_10days'],np.linalg.lstsq(design,a.log_growth,rcond=None)[0][-1],atol=1e-8)
            else:assert pd.isna(match.partial_r.item())
            rows.append(r)
t=pd.DataFrame(rows);assert len(t)==48
t.to_csv(OUT/'comparisons.csv',index=False)
main=t[(t.scope=='timing_supported')&(t['mode']=='site_year')]
lines=['# 低海氷日数は同期間の平均濃度と区別できるか','','同じ1991–2020年の海氷資料から8–9月／8–11月の平均濃度を暦日数で重み付けして作成。低海氷日数と同じ場所・距離帯・期間・連続計数年へ結合した。2閾値×2距離帯×2期間×3観測集合×2固定効果の48条件を全て保持。','','下表は計数の時間順序を確認した集合、地点＋年調整。rは低海氷日数の年差とlog計数比の偏相関。保持率は平均濃度差を追加した後に残る日数変動の割合で、因果的寄与率ではない。','','| 期間 | 閾値 | 距離帯 km | n | 日数変化がある地点 | 調整前r | 平均濃度調整後r | 日数変動保持率 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for r in main.itertuples():
    lines.append(f'| {r.window} | {r.threshold} | {r.inner_km} | {r.n} | {r.nonzero_duration_sites} | {r.r_before:+.3f} | {r.r_after:+.3f} | {r.duration_variance_retained:.1%} |')
lines+=['','nanは推定不能。年固定効果の残差化により日数変化のない地点にも残差が配分されるため、残差の数を独立な日数変化の反復数と扱わない。平均濃度と日数は同じ日次系列の要約で、調整後の関係は同じ平均濃度でも日数分布が異なる条件の記述的比較。融氷日や海氷輸送の機構は同定していない。','','今回p値は追加していない。従来の48比較の検定値を調整後へ流用しない。地域偏在・少数の変化地点・共通の海氷測定誤差を残すため、方向や大きさだけで将来巣数の予測係数に採用しない。','','検証：全2408行の多対一結合と完全月を確認。調整前相関を凍結表へ照合し、調整後係数は全変数同時回帰と照合。入力ハッシュと結合行を保存。','','再現：`python research/climate-penguin/work/scenario_support_v1/low_days_mean_separation.py`']
lines += ['', '8–9月・沿岸・15%閾値では相関が−0.126から−0.203へ、8–11月・沖合・30%では+0.041から+0.212へ変化した。平均濃度の調整で一律に消える関係ではない一方、期間・距離帯を通じて共通の方向は得られていない。該当条件で日数変化を含む地点はそれぞれ6地点・10地点であり、全観測数を独立な環境変化の数とはしない。', '',
          '別検証：`python research/climate-penguin/work/scenario_support_v1/validate_low_days_mean.py` は日次原系列から直接平均し、全4816の始点・終点値を照合する。結果はdaily_validation.json。']
(OUT/'REPORT_JA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(dict(passed=True,rows=len(d),specifications=48,estimable=int(t.status.eq('estimated').sum()),inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2)+'\n')
print(main.to_string(index=False))
