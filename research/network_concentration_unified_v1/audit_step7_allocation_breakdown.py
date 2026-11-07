#!/usr/bin/env python3
"""Step7 late-only composition TV breakdown: source-verified JNCC cohorts, no new tests.

Computes smallest hypothetical late SITE SHARE allocation change needed to reverse
the positive sign against the ORIGINAL fixed-share null offset. Does NOT estimate
real detection error; does not refit the original null or frozen regression models.
"""
from __future__ import annotations
import csv,hashlib,json,math,statistics,subprocess,argparse
from collections import defaultdict
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
DATA=BASE/"data"
OUT=BASE/"outputs"
PLAN=BASE/"contracts/STEP7_ALLOCATION_BREAKDOWN_CONTRACT.md"
SOURCE_GIT_BLOB="e089c4525226c156a1554ce4f480a7611c946ae7"
THRESHOLDS=(.01,.025,.05,.10)

def rows(path):
    with path.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def save(path,items):
    with path.open(encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(items[0]),lineterminator="\n")
        writer.writeheader()
        writer.writerows(items)

def close(a,b,eps=1e-10):
    return abs(float(a)-float(b))<=eps

def h_of(p):
    return sum(x*x for x in p)

def flatten(p,mass):
    """Min-H probability vector within TV mass from p by doubly capped waterfilling."""
    K=len(p)
    target_mass=sum(max(0.,x-1/K) for x in p)
    if mass < -1e-12 or mass > target_mass+1e-10:
        raise ValueError("Requested impossible total variation transfer")
    mass=max(0.,min(mass,target_mass))
    low,high=1/K,max(p)
    for _ in range(60):
        mid=(low+high)/2
        removed=sum(max(0.,x-mid) for x in p)
        if removed > mass:low=mid
        else:high=mid
    cap=(low+high)/2
    low,high=min(p),1/K
    for _ in range(60):
        mid=(low+high)/2
        added=sum(max(0.,mid-x) for x in p)
        if added < mass:low=mid
        else:high=mid
    floor=(low+high)/2
    if floor>cap+1e-10:
        raise ValueError("Optimal floor crossed cap")
    q=[min(cap,max(floor,x)) for x in p]
    if not close(sum(q),1,1e-9):
        raise ValueError("Robin Hood balancing error")
    tv=.5*sum(abs(a-b) for a,b in zip(p,q))
    if not close(tv,mass,1e-9):
        raise ValueError("TV budget not conserved")
    return q

def breakdown(p,threshold):
    """Minimum late-only TV lowering Herfindahl H to a frozen required threshold."""
    K=len(p)
    H=h_of(p)
    if H<=threshold+1e-13:
        return 0.,"already_nonpositive"
    if threshold<1/K-1e-13:
        return None,"unreachable_late_only"
    max_mass=sum(max(0.,x-1/K) for x in p)
    lo,hi=0.,max_mass
    for _ in range(55):
        mid=(lo+hi)/2
        q=flatten(p,mid)
        if h_of(q)>threshold:
            lo=mid
        else:
            hi=mid
    result=hi
    q=flatten(p,result)
    if h_of(q)>threshold+1e-10:
        raise ValueError("Breakdown boundary was not crossed")
    return result,"late_share_reallocation_possible"

def selftest():
    p=[.8,.15,.05]
    assert abs(h_of(p)-.665)<1e-12
    assert close(sum(flatten(p,.1)),1)
    assert close(h_of(flatten(p,sum(max(0.,x-1/3) for x in p))),1/3,1e-10)
    tv,status=breakdown(p,.5)
    assert status=="late_share_reallocation_possible" and 0<tv<.5
    assert h_of(flatten(p,tv))<=.5+1e-10
    assert breakdown(p,.1)[1]=="unreachable_late_only"
    assert breakdown(p,.7)[0]==0
    p2=[1/3,1/3,1/3]
    assert breakdown(p2,1/3)[0]==0
    # Direct grid over 2 coordinates on a 3-part probability simplex to
    # independently check no smaller total variation achieves the threshold.
    qbound,unused=breakdown(p,.5)
    grid=.001
    smaller=1
    for i in range(1001):
        a=i*grid
        for j in range(1001-i):
            b=j*grid
            c=1-a-b
            dist=.5*(abs(a-p[0])+abs(b-p[1])+abs(c-p[2]))
            if a*a+b*b+c*c<=.5+1e-12 and dist<smaller:
                smaller=dist
    assert abs(smaller-qbound)<.0016,(smaller,qbound)
    print(json.dumps({"status":"PASS_WATERFILL_AND_BRUTE_FORCE_3PART_OPTIMUM",
          "synthetic_bound":qbound,"bruteforce_bound":smaller}))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--selftest",action="store_true")
    args=ap.parse_args()
    if args.selftest:
        selftest();return
    if not PLAN.exists():
        raise ValueError("Source-locked breakdown contract missing")
    mainpath=DATA/"network_species.csv"
    actual=subprocess.run(["git","hash-object",str(mainpath)],cwd=ROOT,
            capture_output=True,text=True,check=True).stdout.strip()
    if actual!=SOURCE_GIT_BLOB:
        raise ValueError("Frozen original response file differs")
    dat=rows(mainpath)
    selected=sorted((r for r in dat if r["dataset_id"]=="JNCC" and
          r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"),
          key=lambda r:r["row_id"])
    if len(selected)!=663:
        raise ValueError("Locked source network sample drift")
    chosen={r["row_id"]:r for r in selected}
    grouped=defaultdict(lambda:defaultdict(dict))
    for x in rows(DATA/"unit_endpoints.csv"):
        if x["dataset_id"]!="JNCC" or x["analysis_unit"]!="network_species" or \
           x["row_id"] not in chosen:
            continue
        if x["endpoint"] not in ("early","late"):
            raise ValueError("Unexpected endpoint identifier")
        if x["count_status"] not in ("observed_positive","observed_zero"):
            raise ValueError("Missing / ambiguous count in eligible source site")
        n=float(x["count_value"])
        if not math.isfinite(n) or n<0 or n!=int(n):
            raise ValueError("JNCC adjusted source count is not an exact nonnegative integer")
        site=x["component_id"]
        if site in grouped[x["row_id"]][x["endpoint"]]:
            raise ValueError("Duplicated site/epoch source count")
        grouped[x["row_id"]][x["endpoint"]][site]=n
    outcomes=[]
    for r in selected:
        by=grouped[r["row_id"]]
        a=by["early"];b=by["late"]
        if len(a)!=int(r["K"]) or a.keys()!=b.keys():
            raise ValueError("Original fixed Site.ID roster differs from target cohort")
        N0=sum(a.values());N1=sum(b.values())
        if not close(N0,r["N0"],1e-7) or not close(N1,r["N1"],1e-7):
            raise ValueError("Original count totals changed")
        sites=sorted(a)
        p0=[a[s]/N0 for s in sites]
        p1=[b[s]/N1 for s in sites]
        H0=h_of(p0);H1=h_of(p1)
        dt=float(r["dt_years"])
        raw=(10/dt)*math.log(H1/H0)
        mean_null=float(r["null_mean_decade"])
        Y=float(r["concentration_excess_decade"])
        if not close(raw,float(r["concentration_raw_decade"]),1e-9) or not close(raw-mean_null,Y,1e-9):
            raise ValueError("Original null-centered concentration changed")
        target=H0*math.exp((dt/10)*mean_null)
        if Y>0:
            tv,flag=breakdown(p1,target)
            if tv is not None and not tv>0:
                raise ValueError("Positive source effect erased at zero TV")
        else:
            tv=None;flag="not_positive_primary"
        country=r["network_id"].split("::",2)[1]
        outcomes.append(dict(row_id=r["row_id"],country=country,
            species_id=r["species_id"],count_unit=r["count_unit"],year0=r["year0"],
            year1=r["year1"],K=r["K"],Y_excess_decade=r["concentration_excess_decade"],
            primary_positive=str(Y>0).lower(),late_only_breakdown_TV="" if tv is None else f"{tv:.12g}",
            breakdown_status=flag,
            loss_at_1pct=str(tv is not None and tv<=.01).lower(),
            loss_at_2p5pct=str(tv is not None and tv<=.025).lower(),
            loss_at_5pct=str(tv is not None and tv<=.05).lower(),
            loss_at_10pct=str(tv is not None and tv<=.10).lower()))
    save(DATA/"step7_late_share_breakdown.csv",outcomes)
    positives=[x for x in outcomes if x["primary_positive"]=="true"]
    reachable=[float(x["late_only_breakdown_TV"]) for x in positives if x["late_only_breakdown_TV"]]
    unreachable=[x for x in positives if x["breakdown_status"]=="unreachable_late_only"]
    def summary(group):
        q=[x for x in group if x["primary_positive"]=="true"]
        vals=sorted(float(x["late_only_breakdown_TV"]) for x in q if x["late_only_breakdown_TV"])
        return dict(rows=len(group),positive_rows=len(q),
            reached_n=len(vals),unreachable_n=len(q)-len(vals),
            threshold_n={str(t):sum(v<=t for v in vals) for t in THRESHOLDS},
            positive_fraction=len(q)/len(group) if group else None,
            minimum_TV_median=statistics.median(vals) if vals else None,
            minimum_TV_q25=vals[len(vals)//4] if vals else None,
            minimum_TV_q75=vals[(3*len(vals))//4] if vals else None)
    by_country={c:summary([x for x in outcomes if x["country"]==c]) for c in sorted({x["country"] for x in outcomes})}
    by_unit={u:summary([x for x in outcomes if x["count_unit"]==u]) for u in sorted({x["count_unit"] for x in outcomes})}
    by_species={s:summary([x for x in outcomes if x["species_id"]==s]) for s in sorted({x["species_id"] for x in outcomes})}
    report=dict(status="POST_RESULT_LATE_ONLY_COMPOSITION_TV_FRAGILITY_NOT_ERROR_CALIBRATION",
      fixed_source_git_blob=actual,
      original_source_sha256="9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4",
      contract_sha256=hashlib.sha256(PLAN.read_bytes()).hexdigest(),
      all_JNCC=summary(outcomes),
      by_country=by_country,by_count_unit=by_unit,by_species=by_species,
      source_positive_rows=len(positives),unreachable_late_only=len(unreachable),
      thresholds_fixed_before_calculation=list(THRESHOLDS),
      interpretation="Minimum TV to alter late relative SITE SHARES until positive Y_excess reverses against ORIGINAL unchanged count-null mean",
      source_site_counts_committed=False,
      not_estimated=["actual observer effort","survey-method misclassification",
       "latent breeding polygon identity","new count-null at corrected shares",
       "causal biological movement","posterior measurement-error distribution"],
      prior_step1_4_6_not_refitted=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"STEP7_LATE_SHARE_BREAKDOWN.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    lines=["# Step7 — 元JNCC二時点集中の後期配分TVの崩壊距離（事後解析）","",
        "**観測誤差の推定ではない。** 同じ元Site.ID・前期配分・元の計数帰無平均を固定し、後期配分だけを数学的にどの程度動かせば正方向のY_excessを0にできるか求めた。",
        "",f"- 対象元JNCC行: {len(outcomes)}（うち正方向: {len(positives)}、非正: {len(outcomes)-len(positives)}）",
        f"- 後期のみの配分修正が数学的に不可能: {len(unreachable)}行",
        f"- 数値TV達成可能: {len(reachable)}行",
        "", "## 符号が消えるための最小後期組成TV","",
        "| TV境界（後期配分の合計移動割合） | 元正方向436行中の該当数 | 正方向行中の割合 |",
        "|---|---:|---:|"]
    overall=report["all_JNCC"]
    for t in THRESHOLDS:
        n=overall["threshold_n"][str(t)]
        lines.append(f"| ≤{t:.1%} | {n} / {len(positives)} | {n/len(positives):.1%} |")
    lines.extend(["",f"到達可能行の最小TV中央値: {overall['minimum_TV_median']:.4f}、第1四分位 {overall['minimum_TV_q25']:.4f}、第3四分位 {overall['minimum_TV_q75']:.4f}。","",
        "## 元国別の同じ閾値（抜き出しなし）","",
        "| Country | 元行 | 正 | 1%以内 | 5%以内 | 10%以内 |",
        "|---|---:|---:|---:|---:|---:|"])
    for c,r in by_country.items():
        lines.append(f"| {c} | {r['rows']} | {r['positive_rows']} | {r['threshold_n']['0.01']} | {r['threshold_n']['0.05']} | {r['threshold_n']['0.1']} |")
    lines.extend(["","## 限界と原資料の次の接続","",
      "- 計算結果が小さなTVを示しても「観測誤差がある」と証明しない。水準充填による最も効率的な仮想後期シェア変更を探しただけで、実際にどの方向の誤差が起こったかは不明。",
      "- 前期p0と元の計数帰無平均を固定している。修正後の観測値から帰無を再推定した感度ではなく、両期の独立観測誤差・調査範囲の変更をモデル化していない。",
      "- 未観測・誤ゼロ・ID境界変化に影響される。どのTV閾値も正の真の生態過程を保証しない。",
      "- 原SMPの調査方法、観測精度、調査反復、視認・コロニー境界をSite.IDで対応づけるにはBTO/JNCCの個別調査票・原空間資料が必要。公開二時点Excelにはない。",
      "- 主解析663行、H3/H4固定p値、Step6原稿本文の肯定・不支持結果を**変更しない**。今回の解析は追加の測定脆弱性記述であり新しい生物学的検定ではない。",
      "",
      "再現CSV: data/step7_late_share_breakdown.csv（元動物Site.ID別個数は公開しない）。全分母・すべての計数単位・17種・国のデータを機械可読JSONに記録。"])
    (OUT/"STEP7_LATE_SHARE_BREAKDOWN_JA.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"summary":overall},ensure_ascii=False))

if __name__=="__main__":
    main()
