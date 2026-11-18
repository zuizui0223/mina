#!/usr/bin/env python3
"""Strict source-only Step3 prefit design audit for mina seabird macro study.

Reads explanatory variables, IDs, count support; deliberately does not access
concentration_excess_decade or overlap_excess_decade. No association fit or p.
"""
from __future__ import annotations
import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data"
OUT=ROOT/"outputs"
PREDICTORS=("W_sst_C_decade","log_abundance_or_pair_decline","log_K","log_extent_km","dt_years")

def rows(path):
    with path.open(encoding="utf8",newline="") as f:
        return list(csv.DictReader(f))

def number(x):
    if x is None or str(x).strip()=="":
        raise ValueError("Prefit source data incomplete")
    z=float(x)
    if not math.isfinite(z):raise ValueError("Nonfinite predictor")
    return z

def inspect_design(records):
    X=np.asarray([r["X"] for r in records],dtype=float)
    if not np.all(np.isfinite(X)):raise ValueError("Nonfinite design")
    raw_sd=X.std(axis=0,ddof=1)
    if np.any(raw_sd<=1e-12):raise ValueError("Some pooled predictor has no variation")
    scaled=(X-X.mean(axis=0))/raw_sd
    design=np.column_stack([np.ones(len(scaled)),scaled])
    rank=int(np.linalg.matrix_rank(design,tol=1e-9))
    singular=np.linalg.svd(design,compute_uv=False)
    correlation=np.corrcoef(scaled,rowvar=False)
    return dict(n_rows=int(len(records)),n_parameters=int(design.shape[1]),
                predictor_names=list(PREDICTORS),rank=rank,
                full_column_rank=rank==design.shape[1],
                standardized_condition_number=float(singular[0]/singular[-1]),
                means={k:float(v) for k,v in zip(PREDICTORS,X.mean(axis=0))},
                standard_deviations={k:float(v) for k,v in zip(PREDICTORS,raw_sd)},
                correlation_matrix=correlation.tolist(),
                max_absolute_predictor_correlation=float(np.max(np.abs(
                    correlation-np.eye(correlation.shape[0])))))

def species_pair_dependence(pair_rows):
    bynetwork=defaultdict(list)
    for r in pair_rows:
        bynetwork[r["network_id"]].append(frozenset((r["species_a"],r["species_b"])))
    networks_with_multi=0
    networks_shared_species=0
    pair_pair_shared=0
    total_pair_pairs=0
    for species_pairs in bynetwork.values():
        if len(species_pairs)>1:networks_with_multi+=1
        shared=False
        for a,b in itertools.combinations(species_pairs,2):
            total_pair_pairs+=1
            if a.intersection(b):
                shared=True
                pair_pair_shared+=1
        if shared:networks_shared_species+=1
    return dict(network_count=len(bynetwork),networks_with_multiple_pairs=networks_with_multi,
                networks_with_shared_species_pairs=networks_shared_species,
                pair_pair_combinations_with_shared_species=pair_pair_shared,
                all_within_network_pair_pair_combinations=total_pair_pairs,
                largest_pair_cluster=max(map(len,bynetwork.values())))

def main():
    main_rows=[r for r in rows(DATA/"network_species.csv") if
               r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"]
    pair_rows=[r for r in rows(DATA/"network_species_pairs.csv") if
               r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"]
    climate=rows(DATA/"network_climate_intake.csv")
    lookup={(r["analysis_unit"],r["row_id"]):r for r in climate}
    if len(lookup)!=len(climate) or len(main_rows)!=675 or len(pair_rows)!=378:
        raise ValueError("Step1 candidate registry or Step2 climate keys changed")
    fm=rows(DATA/"species_traits_intake.csv")
    verified_f={r["species_id"] for r in fm if
                r["verification_status"]=="verified_comparable_breeding_site_fidelity"
                and r["annual_breeding_site_fidelity"]!=""}
    if len(verified_f)!=0:raise ValueError("F changed: separate H2 prerequisite gate required")
    accepted={}
    for unit,records,keycol in (("network_species",main_rows,"row_id"),
                                ("network_species_pairs",pair_rows,"pair_row_id")):
        accepted[unit]=[]
        for r in records:
            c=lookup[(unit,r[keycol])]
            if c["verification_status"]!="verified_same_definition_sst":
                continue
            if c["spatial_status"]!="verified_source_ocean_cell" or c["temporal_status"]!="source_endpoint_months_verified":
                raise ValueError("Invalid SST provenance flag")
            if unit=="network_species":
                d=[number(c["delta_sst_C_per_decade"]),
                   number(r["abundance_log_change_decade"]),
                   math.log(number(r["K"])),math.log(number(r["extent_km"])),
                   number(r["dt_years"])]
            else:
                d=[number(c["delta_sst_C_per_decade"]),
                   number(r["pair_decline_decade"]),
                   math.log(number(r["K_pair"])),math.log(number(r["extent_km"])),
                   number(r["dt_years"])]
            accepted[unit].append(dict(X=d,
                network_id=r["network_id"],dataset_id=r["dataset_id"],
                species_id=r.get("species_id",""),species_a=r.get("species_a",""),
                species_b=r.get("species_b",""),
                pair_row_id=r.get("pair_row_id","")))
    a=accepted["network_species"]
    b=accepted["network_species_pairs"]
    if (len(a),len(b))!=(662,376):raise ValueError("Step2 source-verified cohort changed")
    stat1,stat2=inspect_design(a),inspect_design(b)
    if not stat1["full_column_rank"] or not stat2["full_column_rank"]:
        raise ValueError("Fixed-effect design is rank-deficient; report and stop")
    def summary(items):
        return dict(n_rows=len(items),
                    n_networks=len({r["network_id"] for r in items}),
                    n_species=len({s for r in items for s in (r["species_id"],r["species_a"],r["species_b"]) if s}),
                    source_rows=dict(Counter(r["dataset_id"] for r in items)),
                    source_networks={k:len({r["network_id"] for r in items if r["dataset_id"]==k})
                                     for k in sorted({r["dataset_id"] for r in items})})
    result={
        "status":"PREFIT_DESIGN_ONLY_NO_HYPOTHESIS_FITTING",
        "step1_candidates":{"main":675,"pairs":378},
        "H2":{"ready":False,"verified_species":0,
              "reason":"No comparable exact adult same-site interannual fidelity values"},
        "H3":{"support":summary(a),"fixed_effects":stat1},
        "H4D_H4W":{"support":summary(b),"fixed_effects":stat2,
                    "shared_species_dependence":species_pair_dependence(b)},
        "null_and_inference_not_run":["H3 model coefficient","H4D/H4W model coefficients",
                                     "confidence intervals","p values","Holm correction"],
        "source_hashes":{
            p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (DATA/"network_species.csv",DATA/"network_species_pairs.csv",
             DATA/"network_climate_intake.csv",DATA/"species_traits_intake.csv")},
        "conclusion":"Full fixed-effect rank is necessary, not sufficient for identifiable mixed-model variances; group dependence and convergence remain unfrozen in Step3."
    }
    OUT.mkdir(exist_ok=True)
    (OUT/"STEP3_PREFIT_SOURCE_DESIGN_QA.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    def source_line(unit,k):
        v=result[unit]["support"]
        return f"- {k}: {v['n_rows']}行／{v['n_networks']}ネットワーク／{v['n_species']}種、出典別 {v['source_rows']}、独立ネットワーク出典別 {v['source_networks']}。"
    shared=result["H4D_H4W"]["shared_species_dependence"]
    lines=["# Step3 モデルの説明変数だけの識別可能性チェック（実測、関連係数未適合）","",
           "Step2の検証済みNOAA OISST × Step1の固定人口数・空間支持・年月を使い、"
           "Y（集中）やZ（種間重複）の数値には一切アクセスしていない。",
           "H2の固執率は未検証のため、この解析系では推定不能。","",
           source_line("H3","H3 (SST→過剰集中)"),
           source_line("H4D_H4W","H4D/H4W (SST・平均減少→種間重複)"),"",
           f"- H3固定効果デザイン：6列中ランク {stat1['rank']}、標準化条件数 {stat1['standardized_condition_number']:.2f}、説明変数間最大|r| {stat1['max_absolute_predictor_correlation']:.3f}。",
           f"- H4固定効果デザイン：6列中ランク {stat2['rank']}、標準化条件数 {stat2['standardized_condition_number']:.2f}、説明変数間最大|r| {stat2['max_absolute_predictor_correlation']:.3f}。",
           f"- 種ペアの依存：{shared['networks_with_multiple_pairs']}ネットワークで複数種ペアが観測され、"
           f"{shared['networks_with_shared_species_pairs']}ネットワークでは同じ種が複数ペアに登場。"
           f"単一ネットワークの最大ペア数 {shared['largest_pair_cluster']}。",
           "",
           "**解釈：** これらはデザイン行列の代数的な検査であり、p値、係数、収束、検出力、"
           "生態学的予測支持を示さない。2出典間の大きな不均衡と、同一種・同一ネットワークの共有計数を"
           "考慮できる推定器とネットワーク依存型の不確実性法をStep3で事前固定する必要がある。",
           "モデルの結果を見て固定効果／変数／検定族を入れ替えない。",
           "",
           "証跡：STEP3_PREFIT_SOURCE_DESIGN_QA.json に説明変数行列の平均・SD・相関・ソースSHAを保存。"]
    (OUT/"STEP3_PREFIT_SOURCE_DESIGN_JA.md").write_text("\n".join(lines)+"\n",encoding="utf8")
    print(json.dumps({k:(v if k not in ("H3","H4D_H4W") else
          {"support":v["support"],"rank":v["fixed_effects"]["rank"]})
          for k,v in result.items() if k in ("status","H2","H3","H4D_H4W")},ensure_ascii=False))
if __name__=="__main__":main()
