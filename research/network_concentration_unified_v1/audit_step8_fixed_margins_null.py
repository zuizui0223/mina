#!/usr/bin/env python3
"""Post-result JNCC fixed-margins multivariate hypergeometric null sensitivity.

Source-only alternative to original pooled-share independent multinomial count null.
No modification of primary estimates, regression coefficients, original count data.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
DATA=BASE/"data"
OUT=BASE/"outputs"
CONTRACT=BASE/"contracts/STEP8_CONDITIONAL_COUNT_NULL_LOCK.md"
MAIN_BLOB="e089c4525226c156a1554ce4f480a7611c946ae7"
JNCC_ORIGINAL_SHA="9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4"
B=1999
SEED="20261107"

def readcsv(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def savecsv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def sample_raw(x0,x1,dt,rng,b=B):
    """Condition on Site.ID column totals and survey-period row totals."""
    a=np.asarray(x0,dtype=np.int64)
    c=np.asarray(x1,dtype=np.int64)
    m=a+c
    t0=int(a.sum());t1=int(c.sum())
    if len(a)<3 or t0<2 or t1<2 or len(a)!=len(c):
        raise ValueError("Invalid fixed JNCC count matrix")
    if np.any(a<0) or np.any(c<0):
        raise ValueError("Negative source count")
    xs=rng.multivariate_hypergeometric(m,t0,size=b,method="marginals")
    ys=m[None,:]-xs
    if not np.all(xs.sum(axis=1)==t0) or not np.all(ys.sum(axis=1)==t1):
        raise ValueError("Conditional margins did not remain fixed")
    h0=np.sum((xs/t0)**2,axis=1)
    h1=np.sum((ys/t1)**2,axis=1)
    samples=(10./dt)*np.log(h1/h0)
    if not np.all(np.isfinite(samples)):
        raise ValueError("Nonfinite source-margins null statistic")
    return samples

def exact_small(m,t0,dt):
    """Enumerate all allocations of 3 fixed site totals for synthetic QA."""
    from math import comb
    t1=sum(m)-t0
    num=0.;den=0.
    for a in range(m[0]+1):
        for b in range(m[1]+1):
            c=t0-a-b
            if 0<=c<=m[2]:
                x=(a,b,c);y=tuple(z-v for z,v in zip(m,x))
                p=math.prod(comb(z,v) for z,v in zip(m,x))/comb(sum(m),t0)
                h0=sum((v/t0)**2 for v in x)
                h1=sum((v/t1)**2 for v in y)
                num+=p*(10/dt)*math.log(h1/h0)
                den+=p
    if abs(den-1)>1e-12:raise ValueError("Synthetic exact mass did not sum to 1")
    return num

def synthetic():
    mm=np.asarray([3,2,1],dtype=np.int64)
    exact=exact_small(mm,2,17)
    samples=sample_raw([2,0,0],[1,2,1],17,np.random.default_rng(20261107),b=70000)
    error=abs(exact-float(samples.mean()))
    assert error<.015,(exact,float(samples.mean()),error)
    # symmetric original endpoint totals => exact conditional expectation Y_raw=0
    equal=exact_small((3,2,1),3,12)
    assert abs(equal)<1e-12,equal
    print(json.dumps({"status":"PASS_EXACT_ENUMERATION_COMPARISON",
                     "enumerated_conditional_mean":exact,
                     "MC_mean":float(samples.mean()),
                     "abs_difference":error,
                     "symmetric_exact_mean":equal}))

def get_sample_group():
    f=DATA/"network_species.csv"
    blob=subprocess.run(["git","hash-object",str(f)],cwd=ROOT,
          capture_output=True,text=True,check=True).stdout.strip()
    if blob!=MAIN_BLOB:
        raise ValueError("Frozen JNCC main response blob changed")
    entries=readcsv(f)
    group=[r for r in entries if r["dataset_id"]=="JNCC" and
           r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"]
    if len(entries)!=1529 or len(group)!=663:
        raise ValueError("Original Step1 eligibility/row count drift")
    if sum(float(r["concentration_excess_decade"])>0 for r in group)!=436 or \
       sum(float(r["N1"])<float(r["N0"]) for r in group)!=479:
        raise ValueError("Historical primary outcomes changed")
    if sum(float(r["concentration_excess_decade"])>0 and
           float(r["N1"])<float(r["N0"]) for r in group)!=324:
        raise ValueError("Corrected Step1 declines 324/479 changed")
    return sorted(group,key=lambda x:x["row_id"]),blob

def fixed_original(rowlist):
    ids={r["row_id"]:r for r in rowlist}
    original=DATA/"unit_endpoints.csv"
    if not original.exists():
        raise FileNotFoundError("Rebuild original source unit endpoints with the fixed 6-source registry")
    groups=defaultdict(lambda:defaultdict(dict))
    for rec in readcsv(original):
        if rec["analysis_unit"]!="network_species" or rec["dataset_id"]!="JNCC" or rec["row_id"] not in ids:
            continue
        ep=rec["endpoint"]
        if ep not in ("early","late"):
            raise ValueError("Unexpected original epoch")
        if rec["count_status"] not in ("observed_positive","observed_zero"):
            raise ValueError("Eligible source entry had unobserved count")
        v=float(rec["count_value"])
        if v<0 or not math.isfinite(v) or not v.is_integer():
            raise ValueError("Original source count invalid")
        cid=rec["component_id"]
        if cid in groups[rec["row_id"]][ep]:
            raise ValueError("Duplicate original Site.ID in same epoch")
        groups[rec["row_id"]][ep][cid]=int(v)
    if len(groups)!=len(ids):
        raise ValueError("Original source count groups missing")
    return groups

def summarise(rows):
    if not rows:
        return dict(n=0,original_positive=0,conditional_positive=0)
    key=defaultdict(list)
    for r in rows:
        key[r["species_id"]].append(float(r["Y_excess_hypergeom_decade"]))
    means=[float(statistics.mean(q)) for q in key.values()]
    return dict(n=len(rows),original_positive=sum(r["original_sign_positive"]=="true" for r in rows),
        conditional_positive=sum(r["hypergeom_sign_positive"]=="true" for r in rows),
        species_n=len(key),
        species_positive_mean_n=sum(m>0 for m in means),
        species_equal_mean=float(statistics.mean(means)) if means else None,
        conditional_Y_median=float(statistics.median(float(r["Y_excess_hypergeom_decade"]) for r in rows)),
        mean_center_shift=float(statistics.mean(float(r["hypergeom_null_mean_decade"])-
                         float(r["multinomial_null_mean_decade"]) for r in rows)))

def run():
    if not CONTRACT.exists():
        raise ValueError("Need fixed pre-computation contract")
    original=ROOT/"build/step1_inputs/jncc.xlsx"
    if not original.exists() or hashlib.sha256(original.read_bytes()).hexdigest()!=JNCC_ORIGINAL_SHA:
        raise ValueError("Unverified original JNCC publisher XLSX")
    group,blob=get_sample_group()
    counts=fixed_original(group)
    output=[]
    for r in group:
        pp=counts[r["row_id"]]
        if pp["early"].keys()!=pp["late"].keys() or len(pp["early"])!=int(r["K"]):
            raise ValueError("Original frozen component cohort changed")
        ids=sorted(pp["early"])
        a=[pp["early"][k] for k in ids]
        b=[pp["late"][k] for k in ids]
        t0=sum(a);t1=sum(b)
        if abs(t0-float(r["N0"]))>1e-6 or abs(t1-float(r["N1"]))>1e-6:
            raise ValueError("Source margins differ from original Step1 output")
        dt=float(r["dt_years"])
        obs=(10/dt)*math.log(sum((x/t1)**2 for x in b)/
                             sum((x/t0)**2 for x in a))
        if abs(obs-float(r["concentration_raw_decade"]))>1e-10:
            raise ValueError("Raw source Y differs from original Step1")
        seed=int(hashlib.sha256((SEED+"|"+r["row_id"]).encode()).hexdigest()[:8],16)
        simulated=sample_raw(a,b,dt,np.random.default_rng(seed))
        null_mean=float(np.mean(simulated))
        null_sd=float(np.std(simulated,ddof=1))
        q025=float(np.quantile(simulated,.025))
        q975=float(np.quantile(simulated,.975))
        new=obs-null_mean
        old=float(r["concentration_excess_decade"])
        if abs((obs-float(r["null_mean_decade"]))-old)>1e-10:
            raise ValueError("Existing source null mean changed")
        output.append(dict(
           row_id=r["row_id"],dataset_id=r["dataset_id"],network_id=r["network_id"],
           country=r["network_id"].split("::",2)[1],species_id=r["species_id"],count_unit=r["count_unit"],
           year0=r["year0"],year1=r["year1"],K=r["K"],N0=r["N0"],N1=r["N1"],
           original_sign_positive=str(old>0).lower(),
           hypergeom_sign_positive=str(new>0).lower(),
           decline=str(t1<t0).lower(),
           Y_raw_decade=f"{obs:.14g}",
           multinomial_null_mean_decade=r["null_mean_decade"],
           Y_excess_original_decade=r["concentration_excess_decade"],
           hypergeom_null_mean_decade=f"{null_mean:.14g}",
           hypergeom_null_sd_decade=f"{null_sd:.14g}",
           hypergeom_null_q025_decade=f"{q025:.14g}",
           hypergeom_null_q975_decade=f"{q975:.14g}",
           hypergeom_null_mcse_decade=f"{null_sd/math.sqrt(B):.14g}",
           Y_excess_hypergeom_decade=f"{new:.14g}",
           sample_seed=seed))
    savecsv(DATA/"step8_fixed_margins_hypergeom.csv",output)
    original_pos=[r for r in output if r["original_sign_positive"]=="true"]
    newly_positive=[r for r in output if r["hypergeom_sign_positive"]=="true"]
    declines=[r for r in output if r["decline"]=="true"]
    bycountry={c:summarise([r for r in output if r["country"]==c]) for c in sorted({r["country"] for r in output})}
    byunit={u:summarise([r for r in output if r["count_unit"]==u]) for u in sorted({r["count_unit"] for r in output})}
    byspecies={s:summarise([r for r in output if r["species_id"]==s]) for s in sorted({r["species_id"] for r in output})}
    report=dict(
       status="ALTERNATIVE_CONDITIONAL_FIXED_MARGINS_COUNT_NULL_EXPLORATORY",
       source_blob=blob,source_original_sha256=JNCC_ORIGINAL_SHA,
       plan_sha256=hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
       n_draws_per_row=B,PRNG="numpy default_rng PCG64",
       sample_n=len(output),
       existing_positive_n=len(original_pos),
       conditional_positive_n=len(newly_positive),
       conditional_positive_fraction=len(newly_positive)/len(output),
       original_positive_still_positive=sum(r["hypergeom_sign_positive"]=="true" for r in original_pos),
       original_positive_reversed=sum(r["hypergeom_sign_positive"]!="true" for r in original_pos),
       original_nonpositive_to_positive=sum(r["hypergeom_sign_positive"]=="true" and r["original_sign_positive"]!="true" for r in output),
       declined_total=len(declines),
       original_positive_declines=sum(r["original_sign_positive"]=="true" for r in declines),
       conditional_positive_declines=sum(r["hypergeom_sign_positive"]=="true" for r in declines),
       species_positive_means_original=15,
       country=bycountry,count_unit=byunit,species=byspecies,
       overall=summarise(output),
       null_support="both epoch totals and original pooled per-Site.ID counts fixed",
       not_calibrated=["real observer detection errors","varying survey effort",
                        "historical site polygon changes","between-network covariance"],
       hypothesis_p_values_computed=False,
       original_step1_3_4_unmodified=True)
    if report["sample_n"]!=663 or report["existing_positive_n"]!=436 or \
       report["declined_total"]!=479 or report["original_positive_declines"]!=324:
        raise ValueError("Published main denominator drift")
    OUT.mkdir(exist_ok=True)
    (OUT/"STEP8_FIXED_MARGINS_NULL_QA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    c=report
    lines=[
       "# Step 8 — JNCC原計数の固定周辺（超幾何）帰無との照合",
       "",
       "**元のStep1多項帰無からの探索的な条件付き感度。観測誤差推定や追加の事前登録検定ではない。**",
       "",
       "- 両端のネットワーク総数に加え、各元Site.IDの二時点合計を厳密に固定した多変量超幾何帰無を使用。元の多項帰無と違い、二時点の擬似計数は独立ではない。",
       f"- 元JNCC固定主解析663行。元の計数帰無正方向は436/663。新しい条件付き帰無で正方向：**{c['conditional_positive_n']}/663（{c['conditional_positive_fraction']:.1%}）**。",
       f"- 元の436正行のうち正方向維持 **{c['original_positive_still_positive']}**、逆転 **{c['original_positive_reversed']}**。元非正227行から正への変化 **{c['original_nonpositive_to_positive']}**。",
       f"- 減少479行では、元帰無の正324行から、補助帰無の正 **{c['conditional_positive_declines']}行**。",
       f"- 補助帰無では、ネットワーク平均が正の種 **{c['overall']['species_positive_mean_n']}/17種**、種等重み平均 **{c['overall']['species_equal_mean']:+.4f}/10年**。",
       "",
       "## 元Country別（全6カテゴリ）",
       "",
       "| Country | n | 元帰無で正 | 固定周辺帰無で正 | 条件付き種等重み平均 |",
       "|---|---:|---:|---:|---:|"]
    for k,v in bycountry.items():
        lines.append(f"| {k} | {v['n']} | {v['original_positive']} | {v['conditional_positive']} | {v['species_equal_mean']:+.4f} |")
    lines.extend(["","## 原計数単位別（全5種）","",
                  "| Count unit | n | 元帰無で正 | 固定周辺帰無で正 | 条件付き種等重み平均 |",
                  "|---|---:|---:|---:|---:|"])
    for k,v in byunit.items():
        lines.append(f"| {k} | {v['n']} | {v['original_positive']} | {v['conditional_positive']} | {v['species_equal_mean']:+.4f} |")
    lines.extend(["","## 推定対象の境界","",
      "- 二時点の元観測値m_j=n0_j+n1_jを条件として固定するため、潜在的なSiteシェアの変化を引き起こす元配分を条件に取り込んでいる。従来の多項帰無とは異なる補助基準であり、結果を単純な独立検証と呼べない。",
      "- 超幾何帰無も元調査努力、検出誤差、元Site.IDのポリゴン変化を推定しない。国と種が不均衡で、ネットワーク間の空間依存も別問題。",
      "- 元Step1の正436/663、減少324/479、固定H3/H4のHolm pと原稿v0.2は変更しない。新しい帰無を見て新しいカットオフや説明変数を選ばない。",
      "- 元の子Site.ID別原計数はGitへ保存しない。新旧帰無の各row_idの集計値はCSVへ保存、同一入力SHAとコード・乱数seedを保持する。",
    ])
    (OUT/"STEP8_FIXED_MARGINS_NULL_JA.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({k:c[k] for k in (
       "status","sample_n","existing_positive_n","conditional_positive_n",
       "original_positive_still_positive","original_positive_reversed",
       "conditional_positive_declines")},ensure_ascii=False))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    args=p.parse_args()
    if args.selftest:synthetic()
    else:run()

if __name__=="__main__":
    main()
