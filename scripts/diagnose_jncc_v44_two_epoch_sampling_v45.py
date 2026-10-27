#!/usr/bin/env python3
"""V45 post-hoc detection/count theory sensitivity of the original V44 D.

Original V44 pair cohort is immutable and recomputed from source. This
DIAGNOSTIC models BOTH census epochs as independent multinomial counts under
constant latent site composition, not empirical survey errors. First-epoch
count variability induces negative expected original V44 E even under null.
This workflow does NOT estimate mammalian predation, colony dispersal or
field-verified initial detection probabilities.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path

import numpy as np

import audit_jncc_within_master_nest_access_v44 as src
import model_jncc_within_master_nest_access_v44 as v44

SEED=20261027
N_SIM=3999
EXPECTED_MASTERS=11
EXPECTED_SOURCE_PAIRS=17
ORIGINAL_V44_T=-0.10001721634243599


def unbiased_simpson(n) -> float:
    a=np.asarray(n,dtype=np.int64)
    N=int(a.sum())
    if N<2:raise ValueError("unbiased pairwise Simpson needs N>=2")
    return float(np.dot(a,a-1)/(N*(N-1)))


def old_legacy_E(n0,n1) -> float:
    a=np.asarray(n0,dtype=np.float64)
    b=np.asarray(n1,dtype=np.float64)
    N0=float(a.sum()); N1=float(b.sum())
    if N0<2 or N1<2 or len(a)!=len(b):
        raise ValueError("both original site samples >=2 with equal source roster")
    p0=a/N0; p1=b/N1
    C0=float(p0@p0); C1=float(p1@p1)
    return C1-(C0+(1-C0)/N1)


def both_epoch_unbiased_delta(n0,n1) -> float:
    return unbiased_simpson(n1)-unbiased_simpson(n0)


def expected_legacy_E_two_snapshot(n0,n1,p):
    """Exact under multinomial(N0,p), independent multinomial(N1,p)."""
    q=float(np.dot(p,p))
    N0=sum(n0);N1=sum(n1)
    return -(1-q)*(1-1/N1)/N0


def source_panel_details(cache,keys):
    out={}
    for key in keys:
        panel=cache[key]
        n0=np.array(panel["old"],dtype=int)
        n1=np.array(panel["late"],dtype=int)
        N0=panel["N0"];N1=panel["N1"]
        pool=(n0+n1)/(N0+N1)
        out[key]={
            "p_pool":pool,
            "bias_pool":expected_legacy_E_two_snapshot(n0,n1,pool),
            "E_legacy":old_legacy_E(n0,n1),
            "E_both":both_epoch_unbiased_delta(n0,n1),
            "N0":N0, "N1":N1,"k":len(n0),
            "C0":float(np.dot(n0/N0,n0/N0)),
            "species":key[0],
            "guild":src.TRAITS[key[0]],
        }
    return out


def per_network(rows,score,key):
    return np.asarray([
        float(np.mean([score[k][key] for k in r["high"]])
            -np.mean([score[k][key] for k in r["low"]]))
        for r in rows
    ],dtype=float)


def diagnostic_sim(cache, keys, rng):
    predicted={}
    for key in sorted(keys):
        p=cache[key]
        N0=p["N0"];N1=p["N1"]
        n0=np.asarray(p["old"],dtype=np.int64)
        n1=np.asarray(p["late"],dtype=np.int64)
        q=(n0+n1)/(N0+N1)
        sim0=rng.multinomial(N0,q,size=N_SIM).astype(np.int64)
        sim1=rng.multinomial(N1,q,size=N_SIM).astype(np.int64)
        C0=((sim0/N0)**2).sum(axis=1)
        C1=((sim1/N1)**2).sum(axis=1)
        Eold=C1-(C0+(1-C0)/N1)
        U0=(sim0*(sim0-1)).sum(axis=1)/(N0*(N0-1))
        U1=(sim1*(sim1-1)).sum(axis=1)/(N1*(N1-1))
        predicted[key]={"E_legacy":Eold,"E_both":U1-U0}
    return predicted


def generated_master_statistics(rows,sims):
    out={}
    for term in ("E_legacy","E_both"):
        arr=np.asarray([
            np.mean([sims[k][term] for k in r["high"]],axis=0)
            -np.mean([sims[k][term] for k in r["low"]],axis=0)
            for r in rows
        ])
        out[term]=np.mean(arr,axis=0)
    return out


def descriptive_panel_counts(key_scores):
    out={}
    for guild in ("ACCESSIBLE","CLIFF_PROTECTED"):
        p=[v for v in key_scores.values() if v["guild"]==guild]
        def median(name):return float(np.median([v[name] for v in p]))
        out[guild]={
            "source_distinct_species_panels":len(p),
            "distinct_species":sorted({v["species"] for v in p}),
            "N0_median":median("N0"),
            "N1_median":median("N1"),
            "k_median":median("k"),
            "N1_divided_by_k_median":float(np.median([v["N1"]/v["k"] for v in p])),
            "C0_median":median("C0"),
            "N0_lt10_n":sum(v["N0"]<10 for v in p),
            "N1_lt10_n":sum(v["N1"]<10 for v in p),
            "N1_over_k_lt3_n":sum(v["N1"]/v["k"]<3 for v in p),
        }
    return out


def numeric_support_diagnostics(rows,score):
    filters=[
        ("BOTH_N0_AND_N1_GE20_EVERY_PANEL",
         lambda p:p["N0"]>=20 and p["N1"]>=20),
        ("LATER_N1_OVER_K_GE3_EVERY_PANEL",
         lambda p:p["N1"]/p["k"]>=3),
        ("LATER_N1_OVER_K_GE10_EVERY_PANEL",
         lambda p:p["N1"]/p["k"]>=10),
    ]
    out={}
    for title,fun in filters:
        eligible=[
            r for r in rows
            if all(fun(score[k]) for k in (r["high"]+r["low"]))
        ]
        D=per_network(eligible,score,"E_both") if eligible else np.array([])
        out[title]={
            "eligible_original_Master_networks":len(eligible),
            "D_both_mean":float(D.mean()) if len(D) else None,
            "positive_D_both_n":int((D>0).sum()) if len(D) else 0,
            "subset_is_diagnostic_only_not_new_inference":True,
            "original_source_gate_10_networks_still_met":len(eligible)>=10,
        }
    return out


def calibrated_diagnostics(parents,qualified,sourceqa):
    if not sourceqa["V44_primary_source_only_comparison_gate_pass"]:
        return {
            "status":"STOP_V45_NO_ORIGINAL_V44_SOURCE_GATE"
        }
    both,all_trajectories,cache,numerics=v44.build_complete_compared_cohort(parents,qualified)
    if not numerics["fixed_preregistered_both_declining_count_gate_pass"]:
        return {"status":"STOP_V45_NO_ORIGINAL_V44_COUNT_GATE","support":numerics}
    pairs=sum(len(p) for p in both.values())
    if len(both)!=EXPECTED_MASTERS or pairs!=EXPECTED_SOURCE_PAIRS:
        raise ValueError("V45_V44_FROZEN_11_MASTER_17_PAIR_SOURCE_INVARIANT")
    rows,_=v44.group_data(both,cache)
    keys={key for r in rows for key in (r["high"]+r["low"])}
    score=source_panel_details(cache,keys)
    legacy=per_network(rows,score,"E_legacy")
    raw=float(legacy.mean())
    if not math.isclose(raw,ORIGINAL_V44_T,rel_tol=0,abs_tol=1e-10):
        raise ValueError(f"V44_ORIGINAL_D_DRIFT expected={ORIGINAL_V44_T} got={raw}")
    corrected=per_network(rows,score,"E_both")
    bias=per_network(rows,score,"bias_pool")
    rng=np.random.default_rng(SEED)
    sims=diagnostic_sim(cache,keys,rng)
    null=generated_master_statistics(rows,sims)
    def describe_null(data,obs):
        return {
            "two_independent_epoch_multinomial_null_mean":float(data.mean()),
            "null_q05":float(np.quantile(data,.05)),
            "null_median":float(np.median(data)),
            "null_q95":float(np.quantile(data,.95)),
            "left_tail_fraction":float((1+np.sum(data<=obs))/(len(data)+1)),
            "right_tail_fraction":float((1+np.sum(data>=obs))/(len(data)+1)),
            "only_model_diagnostic_not_field_error_calibrated_p_value":True,
        }
    leaveout=[float(np.mean(np.delete(corrected,i))) for i in range(len(corrected))]
    return {
       "status":"V45_REAL_UNCHANGED_V44_COHORT_TWO_EPOCH_SAMPLING_DIAGNOSTIC_COMPLETED",
       "original_Master_network_count":len(rows),
       "original_strict_pair_links":pairs,
       "unique_original_species_count_panels":len(keys),
       "original_V44_legacy_mean_D_replicated":raw,
       "original_V44_direction_positive_accessible_more_concentrated_predicted":True,
       "V44_original_positive_direction_supported":False,
       "two_epoch_unbiased_pairwise_Simpson_network_equal_mean_D":float(corrected.mean()),
       "both_epoch_delta_positive_networks_n":int((corrected>0).sum()),
       "both_epoch_delta_network_q05_median_q95":[float(v) for v in np.quantile(corrected,[.05,.5,.95])],
       "analytical_two_epoch_sampling_expected_original_D_using_pooled_source_probabilities":float(bias.mean()),
       "original_D_minus_analytic_expected_bias":float(raw-bias.mean()),
       "analytical_formula":"E[E_late|fixed_p, independent_2_epochs]=-(1-Q)*(1-1/N1)/N0",
       "E_both_formula":"sum_i n1_i*(n1_i-1)/(N1*(N1-1)) - sum_i n0_i*(n0_i-1)/(N0*(N0-1))",
       "parametric_null_from_pooled_original_site_counts":{
            "two_epoch_original_E_legacy":describe_null(null["E_legacy"],raw),
            "two_epoch_unbiased_pairwise_E_both":describe_null(null["E_both"],float(corrected.mean())),
       },
       "null_repetitions":N_SIM,"fixed_seed":SEED,
       "separate_species_panels_original_count_support_by_guild":descriptive_panel_counts(score),
       "postresult_fixed_numeric_subcohort_diagnostics":numeric_support_diagnostics(rows,score),
       "leave_one_original_Master_out_E_both_D_min":float(min(leaveout)),
       "leave_one_original_Master_out_E_both_D_max":float(max(leaveout)),
       "leave_one_original_Master_out_E_both_D_negative_n":sum(x<0 for x in leaveout),
       "leave_one_original_Master_out_trials":len(leaveout),
       "original_V44_count_eligibility":numerics,
       "original_V44_source_only_metadata_gate":{
           "strict_primary_same_master_networks_n":sourceqa["strict_primary_same_master_networks_n"],
           "source_original_species_count":sourceqa["exact_original_source_species_n"],
       },
       "ecological_interpretation_ceiling":"Hypothetical independent-count observation model; real JNCC site-census count error and nest-detection mechanisms NOT measured. This sensitivity does not estimate true predation or negate original V44 directional failure.",
       "site_identity_and_traits_unchanged":True,
       "original_JNCC_numeric_eligibility_opened_only_for_17_source_qualified_Master_networks":True,
       "new_concentration_comparison_restricted_to_existing_11_declining_Master_networks":True,
       "no_UK_predator_GBIF_or_Falkland_data":True,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    report={
        "status":"V45_SOURCE_OR_SAMPLING_MODEL_HOLD",
        "date":"2026-10-27",
        "contract":"contracts/JNCC_V45_TWO_EPOCH_COUNT_DIAGNOSTIC_POSTRESULT.md",
        "original_sha256":src.v29.ORIGINAL_SHA,
        "post_V44_exploratory_not_independent_confirmation":True,
    }
    try:
        parents,qualified,sourceqa=src.fetch_and_gate()
        report.update(calibrated_diagnostics(parents,qualified,sourceqa))
    except Exception as e:
        report["status"]="V45_SOURCE_OR_SAMPLING_MODEL_HOLD"
        report["error"]=type(e).__name__+": "+str(e)[:650]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":report["status"],
        "Masters":report.get("original_Master_network_count"),
        "oldD":report.get("original_V44_legacy_mean_D_replicated"),
        "newD":report.get("two_epoch_unbiased_pairwise_Simpson_network_equal_mean_D"),
        "bias":report.get("analytical_two_epoch_sampling_expected_original_D_using_pooled_source_probabilities"),
        "null":report.get("parametric_null_from_pooled_original_site_counts"),
        "guild_counts":report.get("separate_species_panels_original_count_support_by_guild"),
        "fixed_subset_support":report.get("postresult_fixed_numeric_subcohort_diagnostics"),
        "error":report.get("error"),
    },ensure_ascii=False))
    if report["status"]=="V45_SOURCE_OR_SAMPLING_MODEL_HOLD":
        raise SystemExit(2)

if __name__=="__main__":
    main()
