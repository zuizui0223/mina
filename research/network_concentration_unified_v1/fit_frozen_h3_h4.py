#!/usr/bin/env python3
"""Fixed-before-fit exploratory analysis of H3/H4D/H4W, with H2 kept missing."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import qr
from scipy.stats import t as student_t

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
DATA = BASE / "data"
OUT = BASE / "outputs"
PLAN = BASE / "contracts" / "ANALYSIS_PLAN_FROZEN.md"
B = 9999
INPUT_BLOBS = {
    "network_species.csv": "e089c4525226c156a1554ce4f480a7611c946ae7",
    "network_species_pairs.csv": "fe4751b9f12e7ffa6f92ed43c233f6a77b109065",
    "network_climate_intake.csv": "d8a642977202daf563fa8c0622caffe60b657a27",
    "species_traits_intake.csv": "95662a64e6a62e1965bdea20f7b05a702838499a",
    "step2_join_readiness.csv": "f42bbd8720a16d6fff6f1e7d6d3dae1f16eded80",
}

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def preflight():
    if not PLAN.exists():
        raise ValueError("Frozen analysis contract missing")
    hashes={}
    for f, expected in INPUT_BLOBS.items():
        path=DATA/f
        sha=subprocess.run(["git","hash-object",str(path)],cwd=ROOT,
                           check=True,capture_output=True,text=True).stdout.strip()
        if sha!=expected:
            raise ValueError(f"Source file differs from pre-fit lock: {f} {sha}")
        hashes[f]={"git_blob":sha,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    main=read_csv(DATA/"network_species.csv")
    pairs=read_csv(DATA/"network_species_pairs.csv")
    climate=read_csv(DATA/"network_climate_intake.csv")
    traits=read_csv(DATA/"species_traits_intake.csv")
    ready=read_csv(DATA/"step2_join_readiness.csv")
    if (len(main),len(pairs),len(climate),len(traits),len(ready))!=(1529,732,1053,20,1053):
        raise ValueError("Frozen row-count signature changed")
    if any(t["annual_breeding_site_fidelity"] for t in traits):
        raise ValueError("Site fidelity unexpectedly changed: never silently open H2")
    if (sum(r["H3_ready"]=="true" for r in ready),
        sum(r["H4D_ready"]=="true" for r in ready),
        sum(r["H4W_ready"]=="true" for r in ready))!=(662,376,376):
        raise ValueError("Locked complete-case mask changed")
    climate_map={(r["analysis_unit"],r["row_id"]):r for r in climate}
    if len(climate_map)!=len(climate):
        raise ValueError("Duplicated SST join key")
    selected=[]
    for kind,allrows,kcol in (("network_species",main,"row_id"),
                              ("network_species_pairs",pairs,"pair_row_id")):
        target=[]
        for r in allrows:
            c=climate_map.get((kind,r[kcol]))
            if r["analysis_role"]!="macro_primary" or r["null_status"]!="computed" or not c:
                continue
            if c["verification_status"]!="verified_same_definition_sst":
                continue
            if c["temporal_status"]!="source_endpoint_months_verified" or \
               c["spatial_status"]!="verified_source_ocean_cell":
                raise ValueError("Unsupported SST status")
            if (c["year0"],c["year1"],c["network_id"]) != \
               (r["year0"],r["year1"],r["network_id"]):
                raise ValueError("SST joins different endpoint")
            if not math.isfinite(float(c["delta_sst_C_per_decade"])):
                raise ValueError("Nonfinite SST")
            target.append(r)
        selected.append(sorted(target,key=lambda r:r[kcol]))
    a,z=selected
    if (len(a),len(z))!=(662,376) or \
       (len({r["network_id"] for r in a}),len({r["network_id"] for r in z}))!=(387,90) or \
       len({r["species_id"] for r in a})!=20 or \
       len({sp for r in z for sp in (r["species_a"],r["species_b"])})!=18:
        raise ValueError("Frozen sample size or network/species support changed")
    return a,z,climate_map,hashes

def select_nuisance(values,labels):
    X=np.column_stack(values).astype(float)
    _,R,piv=qr(X,mode="economic",pivoting=True)
    diagonal=np.abs(np.diag(R))
    keep=sorted(int(j) for j in piv[:int(np.sum(diagonal>diagonal[0]*1e-10))])
    if 0 not in keep:
        raise ValueError("Intercept aliased from nuisance model")
    return X[:,keep],[labels[j] for j in keep],[labels[j] for j in range(len(labels)) if j not in keep]

def design(rows,kind,climate):
    n=len(rows)
    K=np.array([float(r["K"] if kind=="H3" else r["K_pair"]) for r in rows])
    E=np.array([float(r["extent_km"]) for r in rows])
    DT=np.array([float(r["dt_years"]) for r in rows])
    if np.any(K<3) or np.any(E<=0) or np.any(DT<=0):
        raise ValueError("Nonpositive original spatial or time supports")
    unit="network_species" if kind=="H3" else "network_species_pairs"
    col="row_id" if kind=="H3" else "pair_row_id"
    W=np.array([float(climate[unit,r[col]]["delta_sst_C_per_decade"]) for r in rows])
    values=[np.ones(n),np.log(K),np.log(E),DT]
    names=["intercept","logK","log_extent","dt_years"]
    if kind=="H3":
        Y=np.array([float(r["concentration_excess_decade"]) for r in rows])
        G=np.array([float(r["abundance_log_change_decade"]) for r in rows])
        values.append(G);names.append("G")
        species=sorted({r["species_id"] for r in rows})
        for s in species:
            values.append(np.array([float(r["species_id"]==s) for r in rows]))
            names.append("species_"+s)
        base,keep,drop=select_nuisance(values,names)
        X=np.column_stack([W,base])
        targets={"H3":0}
    else:
        Y=np.array([float(r["overlap_excess_decade"]) for r in rows])
        D=np.array([float(r["pair_decline_decade"]) for r in rows])
        species=sorted({s for r in rows for s in (r["species_a"],r["species_b"])})
        for s in species:
            values.append(np.array([float(int(r["species_a"]==s)+int(r["species_b"]==s)) for r in rows]))
            names.append("shared_species_"+s)
        base,keep,drop=select_nuisance(values,names)
        X=np.column_stack([D,W,base])
        targets={"H4D":0,"H4W":1}
    sv=np.linalg.svd(X,compute_uv=False)
    if sv[-1]/sv[0]<1e-10 or sv[0]/sv[-1]>1e8:
        raise ValueError("Full model is numerically singular")
    if not np.isfinite(X).all() or not np.isfinite(Y).all():
        raise ValueError("Nonfinite regression values")
    return dict(X=X,Y=Y,network=[r["network_id"] for r in rows],
                dataset=[r["dataset_id"] for r in rows],
                species_n=len(species),target=targets,aliased=drop,
                design_condition=float(sv[0]/sv[-1]))

def cluster_stats(X,y,idx,networks):
    n,p=X.shape
    levels=sorted(set(networks))
    m=len(levels)
    if n<=p+5 or m<=p or m<20:
        raise ValueError("Not enough independent network blocks")
    groups={name:i for i,name in enumerate(levels)}
    gi=np.array([groups[v] for v in networks],dtype=int)
    L=np.linalg.pinv(X,rcond=1e-12)
    if np.linalg.norm(X@(L@X)-X)>1e-6*(np.linalg.norm(X)+1):
        raise ValueError("Unstable OLS projection")
    b=L@y
    resid=y-X@b
    S=np.zeros((m,n))
    S[gi,np.arange(n)]=L[idx,:]
    cr1=(m/(m-1))*((n-1)/(n-p))
    se=math.sqrt(cr1*float(np.sum((S@resid)**2)))
    if se<=1e-11:
        raise ValueError("Cluster variance indistinguishable from zero")
    q=float(b[idx]);t=q/se
    critical=float(student_t.ppf(0.975,m-1))
    return dict(coef=q,se=se,t=t,ci_low=q-critical*se,ci_high=q+critical*se,
                n=n,m=m,p=p,L=L,S=S,group_index=gi,cr1=cr1)

def wild_bootstrap(X,y,idx,networks,seed,b=B):
    st=cluster_stats(X,y,idx,networks)
    m=st["m"];n=st["n"];S=st["S"];L=st["L"];gi=st["group_index"]
    reduced=np.delete(X,idx,axis=1)
    e=y-reduced@np.linalg.lstsq(reduced,y,rcond=1e-12)[0]
    # A single Rademacher sign is shared by every row of the same network.
    D=np.zeros((n,m));D[np.arange(n),gi]=e
    R=S@(D-X@(L@D))
    q=S@e
    rng=np.random.default_rng(seed)
    exceed=0;remaining=b
    while remaining:
        count=min(remaining,250)
        signs=(2*rng.integers(0,2,size=(m,count),dtype=np.int8)-1).astype(float)
        numerator=q@signs
        denom=np.sqrt(st["cr1"]*np.sum((R@signs)**2,axis=0))
        if np.any(denom<=1e-13):
            raise ValueError("Bootstrap zero-variance replicate")
        exceed+=int(np.sum(np.abs(numerator/denom)+1e-12>=abs(st["t"])))
        remaining-=count
    return {k:st[k] for k in ("coef","se","t","ci_low","ci_high","n","m","p")} | {
        "p_raw":(1+exceed)/(b+1),"bootstrap_n":b,
        "bootstrap_extreme":exceed,"seed":seed}

def holm(p):
    family=["H2","H3","H4D","H4W"]
    values=[1 if p.get(s) is None else float(p[s]) for s in family]
    ix=sorted(range(4),key=lambda j:(values[j],j))
    result={k:None for k in family}
    max_adj=0
    for rank,i in enumerate(ix):
        max_adj=max(max_adj,min(1,(4-rank)*values[i]))
        if p.get(family[i]) is not None:
            result[family[i]]=max_adj
    return result

def without_scotland(rows,kind,climate,target):
    subset=[r for r in rows if not r["network_id"].startswith("JNCC::Scotland::")]
    try:
        d=design(subset,kind,climate)
        t=cluster_stats(d["X"],d["Y"],d["target"][target],d["network"])
        return {k:t[k] for k in ("coef","se","ci_low","ci_high","n","m")} | {
            "status":"descriptive_sensitivity_no_pvalue"}
    except (ValueError,np.linalg.LinAlgError) as e:
        return {"status":"not_estimable","reason":str(e)}

def selftest():
    assert holm({"H2":None,"H3":.01,"H4D":.03,"H4W":.04})=={
        "H2":None,"H3":.04,"H4D":.09,"H4W":.09}
    rng=np.random.default_rng(841)
    m=48;n=m*3
    net=[f"test_{i//3}" for i in range(n)]
    W=rng.normal(size=n)
    G=rng.normal(size=n)
    block=rng.normal(0,1,m)
    Y=1.5*W+.4*G+np.array([block[i//3] for i in range(n)])+rng.normal(0,.3,n)
    X=np.column_stack([W,np.ones(n),G])
    res=wild_bootstrap(X,Y,0,net,seed=841,b=199)
    assert 1.0<res["coef"]<2.0
    assert 0<res["p_raw"]<=1 and res["m"]==m
    print("PASS: synthetic network-unit wild bootstrap, source rank checks, four Holm slots")

def fit():
    main,pairs,climate,hashes=preflight()
    a=design(main,"H3",climate)
    b=design(pairs,"H4",climate)
    tests={}
    for name,design_info,rows,kind,seed in (
        ("H3",a,main,"H3",20261108),
        ("H4D",b,pairs,"H4",20261109),
        ("H4W",b,pairs,"H4",20261110),
    ):
        val=wild_bootstrap(design_info["X"],design_info["Y"],
                           design_info["target"][name],design_info["network"],seed=seed)
        val["source_rows"]=dict(Counter(design_info["dataset"]))
        val["species_n"]=design_info["species_n"]
        val["aliased_species_columns"]=design_info["aliased"]
        val["design_condition_number"]=design_info["design_condition"]
        val["scotland_exclusion"]=without_scotland(rows,kind,climate,name)
        val["predicted_direction"]="positive"
        tests[name]=val
        print(json.dumps({"hypothesis":name,"coef":val["coef"],"raw_p":val["p_raw"],
               "network_blocks":val["m"],"rows":val["n"]}),flush=True)
    adjusted=holm({"H2":None,**{k:v["p_raw"] for k,v in tests.items()}})
    for k,v in tests.items():
        v["holm_4"]=adjusted[k]
        v["prediction_supported"]=v["coef"]>0 and v["holm_4"]<.05
        v["significant_opposite"]=v["coef"]<0 and v["holm_4"]<.05
    result={
        "analysis_status":"POST_PRIOR_RESULTS_EXPLORATORY_FIXED_BEFORE_H3_H4_FITS",
        "H2":{"status":"NOT_ESTIMABLE","fidelity_species_n":0,
              "p_observed":None,"p_holm_4":None,"internal_holm_placeholder":1},
        "hypothesis_family":["H2","H3","H4D","H4W"],
        "inference":"species fixed effects; CR1 + network-block restricted wild Rademacher bootstrap",
        "B":B,
        "software":{"numpy":np.__version__,"scipy":scipy.__version__},
        "pre_fit_plan_sha256":hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        "frozen_inputs":hashes,
        "results":tests,
        "limitations":[
            "Not externally preregistered; earlier concentration outcomes were viewed.",
            "Model is a documented prefit revision to the earlier LMM draft.",
            "Observed-species conditional inference, not a random species-population generalization.",
            "Shared source counts stay together within network; between-network spatial and phylogenetic dependence may remain.",
            "JNCC, especially Scotland, dominates; Antarctic network replication is sparse.",
            "SST is an observed environmental covariate, not an identified causal warming effect."
        ]
    }
    OUT.mkdir(exist_ok=True)
    (OUT/"STEP4_FIXED_ASSOCIATIONS.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=[
        "# Step 4: 観測SSTと繁殖集中・種間重なりの固定関連解析",
        "",
        "**過去の集中結果を閲覧した後の探索的関連検定であり、外部事前登録・独立確認ではありません。**",
        "",
        "- H2：比較可能な繁殖地固執率は0/20種で未推定。元の4仮説Holm枠を保持。",
        "- H3：662行、387ネットワーク、20種。H4：376種ペア行、90ネットワーク、18種。",
        "- 種固定効果、同一ネットワーク内の共有計数を保持したCR1／帰無制約wild bootstrap 9,999回。",
        "",
        "| 仮説 | 係数 | ネットワークCR1 95%CI | 両側p | Holm 4枠p | 判定 |",
        "|---|---:|---|---:|---:|---|",
    ]
    for name,v in tests.items():
        state=("正の予測支持" if v["prediction_supported"] else
               "補正有意の逆方向" if v["significant_opposite"] else "支持未確認")
        lines.append(f"| {name} | {v['coef']:+.5f} | [{v['ci_low']:+.5f}, {v['ci_high']:+.5f}] | {v['p_raw']:.5f} | {v['holm_4']:.5f} | {state} |")
    lines+=["","## スコットランド除外（主検定ではない事前指定感度）"]
    for name,v in tests.items():
        z=v["scotland_exclusion"]
        if z["status"]=="not_estimable":
            lines.append(f"- {name}: 推定不能（{z['reason']}）")
        else:
            lines.append(f"- {name}: {z['n']}行、{z['m']}ネットワーク、係数 {z['coef']:+.5f}、95%CR1区間 [{z['ci_low']:+.5f}, {z['ci_high']:+.5f}]。")
    lines+=["","## 解釈と制限",
        "- H3はWの1℃/10年当たり集中Y_excess、H4DはDの1 log-unit/10年当たり重なりZ、H4WはWの1℃/10年当たり重なりZの係数。",
        "- 元のLMM草案とは別の推定仕様。帰無制約付き9,999回のネットワークブロックRademacherと4枠Holmを係数計算前に固定。",
        "- 県・国・南極区域の気候変化の共分散、種間の系統依存、地点境界変更と調査誤差は完全には解消しない。",
        "- 南極の主解析6行、ペア3行だけでは両半球の普遍性を主張しない。観測相関は温暖化の因果や将来個体数予測ではない。",
        "",
        "再現用出典とソフトウェア版・各係数の数値はSTEP4_FIXED_ASSOCIATIONS.jsonに記録。"]
    (OUT/"STEP4_MODEL_READOUT_JA.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",required=True,choices=("selftest","preflight","fit"))
    args=parser.parse_args()
    if args.mode=="selftest":selftest()
    elif args.mode=="preflight":
        a,b,_,sha=preflight()
        print(json.dumps({"status":"SOURCE_LOCK_PASS","main":len(a),"pair":len(b),"blob_sha":sha}))
    else:fit()

if __name__=="__main__":
    main()
