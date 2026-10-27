#!/usr/bin/env python3
"""V46: two-epoch fixed-composition null for existing V37/V38 JNCC patterns.

This is explicitly POST-OUTCOME. Reproduce original 959/955/846 eligibility,
switch 412, E>0 and switch 284, and initial-size negative score before
simulating BOTH censuses as independent multinomial observations with original
N0,N1, fixed Site.ID roster and pooled p. Do not infer physical colony moves.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path

import numpy as np

import model_jncc_size_share_retention_v37 as v37
import analyze_jncc_hierarchy_turnover_v38 as v38

R=1999
SEED=20261027
SOURCE_DECLINING=959
SOURCE_SIZE_INFORMATIVE=955
SOURCE_EPOS=597
SOURCE_EPOS_SIZE_NEG=321
SOURCE_LEAD_BOTH_UNIQUE=846
SOURCE_LEAD_SWITCH=412
SOURCE_EPOS_AND_SWITCH=284
SOURCE_EQUAL_SIZE_S=-0.538864
MIN_SPECIES_N=3


def _null_from_pooled_multinomial(old,new,rng,replicates=R):
    """Only model randomness; not source-documented field observation effort."""
    n0=np.asarray(old,dtype=np.int64)
    n1=np.asarray(new,dtype=np.int64)
    N0=int(n0.sum());N1=int(n1.sum())
    if len(n0)<3 or len(n0)!=len(n1) or N0<2 or N1<2:
        raise ValueError("V46_FROZEN_ORIGINAL_COUNT_ROSTER")
    if replicates!=R:
        raise ValueError("V46_FROZEN_MC_REPLICATES")
    p_pool=(n0+n1)/(N0+N1)
    first=rng.multinomial(N0,p_pool,size=replicates)
    second=rng.multinomial(N1,p_pool,size=replicates)
    f=first.astype(np.float64); s=second.astype(np.float64)
    c0=((f/N0)**2).sum(axis=1)
    c1=((s/N1)**2).sum(axis=1)
    E=c1-(c0+(1-c0)/N1)
    U0=(first*(first-1)).sum(axis=1)/(N0*(N0-1))
    U1=(second*(second-1)).sum(axis=1)/(N1*(N1-1))
    Unbiased=U1-U0
    max0=first.max(axis=1)
    max1=second.max(axis=1)
    unique0=np.count_nonzero(first==max0[:,None],axis=1)==1
    unique1=np.count_nonzero(second==max1[:,None],axis=1)==1
    both_unique=unique0 & unique1
    lead_flip=both_unique & (first.argmax(axis=1)!=second.argmax(axis=1))

    # V37 score recalculated from each simulated FIRST epoch, not observed n0.
    smoothed=(f+v37.ALPHA)/(N0+v37.ALPHA*len(n0))
    source_size=np.log1p(f)
    mean_size=np.sum(smoothed*source_size,axis=1)
    centered=source_size-mean_size[:,None]
    variance=np.sum(smoothed*centered**2,axis=1)
    z=np.zeros_like(centered)
    informative=variance>1e-14
    z[informative]=centered[informative]/np.sqrt(variance[informative])[:,None]
    score=np.sum((s/N1-smoothed)*z,axis=1)
    score[~informative]=np.nan
    return {
        "eligible_unique":both_unique,
        "switched":lead_flip,
        "joint_E_legacy_positive_and_switched":(E>0)&lead_flip,
        "joint_E_both_positive_and_switched":(Unbiased>0)&lead_flip,
        "E_legacy_positive":E>0,
        "E_both_positive":Unbiased>0,
        "score_S":score,
        "score_S_valid":informative,
    }


def _stats(null,obs,tail="upper"):
    d=null[np.isfinite(null)]
    if len(d)==0:return {"status":"NULL_UNDEFINED"}
    raw=(1+int(np.sum(d>=obs)))/(len(d)+1) if tail=="upper" else (1+int(np.sum(d<=obs)))/(len(d)+1)
    return {
        "observed":float(obs),
        "pooled_two_epoch_multinomial_null_mean":float(np.mean(d)),
        "pooled_two_epoch_null_q05":float(np.quantile(d,.05)),
        "pooled_two_epoch_null_median":float(np.median(d)),
        "pooled_two_epoch_null_q95":float(np.quantile(d,.95)),
        "null_replicates_valid":int(len(d)),
        "tail_direction":tail,
        "conditional_model_tail_fraction_not_field_error_calibrated_p_value":float(raw),
    }


def source_panel_replay_and_null(records):
    observed_declining=[(p,old,new) for p,old,new in records if sum(new)<sum(old)]
    if len(observed_declining)!=SOURCE_DECLINING:
        raise ValueError("V46_ORIGINAL_959_DECLINES_CHANGED")
    obs=Counter()
    observed_S=defaultdict(list)
    observed_switch=defaultdict(lambda:Counter())
    obs_Eboth_and_switch=Counter()
    sim_guild=defaultdict(lambda:{
        k:np.zeros(R,dtype=float) for k in
        ("switch_den","switch_num","joint_legacy_num","joint_both_num",
         "Epos_num","Epos_den","S_sum","S_den")
    })
    sims_all_den=np.zeros(R,dtype=float)
    sims_all_sw=np.zeros(R,dtype=float)
    sims_all_joint_legacy=np.zeros(R,dtype=float)
    sims_all_joint_both=np.zeros(R,dtype=float)
    sims_all_Epos=np.zeros(R,dtype=float)
    sims_all_S_undefined=np.zeros(R,dtype=int)
    rng=np.random.default_rng(SEED)
    for (key,old,new) in observed_declining:
        sp=key[0]
        n0=np.asarray(old,dtype=np.int64)
        n1=np.asarray(new,dtype=np.int64)
        m=v38.decomposition(old,new)
        obs["declining"]+=1
        obs["E_legacy_positive"]+=int(m["E_positive"])
        if m["S_informative"]:
            obs["S_informative"]+=1
            observed_S[sp].append(m["S"])
            obs["E_legacy_positive_and_S_negative"]+=int(
                m["E_positive"] and m["S_negative"]
            )
        if m["both_leaders_unique"]:
            obs["two_unique_leader_panel"]+=1
            obs["leader_switched"]+=int(m["leader_switch"])
            obs["E_legacy_positive_and_switched"]+=int(
                m["leader_switch"] and m["E_positive"]
            )
            old_total=n0.sum();late_total=n1.sum()
            U0=np.dot(n0,n0-1)/(old_total*(old_total-1))
            U1=np.dot(n1,n1-1)/(late_total*(late_total-1))
            obs["E_both_unbiased_positive_and_switched"]+=int(
                m["leader_switch"] and (U1-U0>0)
            )
            observed_switch[sp]["eligible"]+=1
            observed_switch[sp]["switch"]+=int(m["leader_switch"])
            observed_switch[sp]["joint_legacy"]+=int(
                m["leader_switch"] and m["E_positive"]
            )
            observed_switch[sp]["joint_both"]+=int(
                m["leader_switch"] and (U1-U0>0)
            )

        synthetic=_null_from_pooled_multinomial(old,new,rng)
        sims_all_Epos+=synthetic["E_legacy_positive"]
        sim_guild[sp]["Epos_num"]+=synthetic["E_legacy_positive"]
        sim_guild[sp]["Epos_den"]+=1
        if m["S_informative"]:
            val=synthetic["score_S"]
            valid=synthetic["score_S_valid"]
            sim_guild[sp]["S_sum"]+=np.where(valid,val,0.)
            sim_guild[sp]["S_den"]+=valid
            sims_all_S_undefined+=~valid
        if m["both_leaders_unique"]:
            eligible=synthetic["eligible_unique"]
            switched=synthetic["switched"]
            jointL=synthetic["joint_E_legacy_positive_and_switched"]
            jointU=synthetic["joint_E_both_positive_and_switched"]
            sims_all_den+=eligible
            sims_all_sw+=switched
            sims_all_joint_legacy+=jointL
            sims_all_joint_both+=jointU
            sim_guild[sp]["switch_den"]+=eligible
            sim_guild[sp]["switch_num"]+=switched
            sim_guild[sp]["joint_legacy_num"]+=jointL
            sim_guild[sp]["joint_both_num"]+=jointU

    if (obs["declining"]!=SOURCE_DECLINING
        or obs["S_informative"]!=SOURCE_SIZE_INFORMATIVE
        or obs["E_legacy_positive"]!=SOURCE_EPOS
        or obs["E_legacy_positive_and_S_negative"]!=SOURCE_EPOS_SIZE_NEG
        or obs["two_unique_leader_panel"]!=SOURCE_LEAD_BOTH_UNIQUE
        or obs["leader_switched"]!=SOURCE_LEAD_SWITCH
        or obs["E_legacy_positive_and_switched"]!=SOURCE_EPOS_AND_SWITCH):
        raise ValueError("V46_V38_ORIGINAL_EVENTS_DRIFT "+str(dict(obs)))
    source_sp={sp:vals for sp,vals in observed_S.items()
               if len(vals)>=MIN_SPECIES_N}
    S_obs=np.mean([np.mean(vals) for vals in source_sp.values()])
    if not np.isclose(S_obs,SOURCE_EQUAL_SIZE_S,atol=.001,rtol=0):
        raise ValueError(f"V46_V37_EQUAL_SPECIES_S_DRIFT {S_obs}")

    # By species, count only species with >=3 ORIGINAL supported examples.
    original_eligible_sp=sorted([
        sp for sp,c in observed_switch.items() if c["eligible"]>=MIN_SPECIES_N
    ])
    def species_obs(event):
        return float(np.mean([
            observed_switch[sp][event]/observed_switch[sp]["eligible"]
            for sp in original_eligible_sp
        ]))
    def species_null(numerator,denominator):
        vec=[]
        for sp in original_eligible_sp:
            a=sim_guild[sp][numerator]
            b=sim_guild[sp][denominator]
            vec.append(np.divide(a,b,out=np.full(R,np.nan),where=b>0))
        m=np.stack(vec)
        valid=np.isfinite(m).sum(axis=0)
        arr=np.full(R,np.nan)
        allowed=valid>=min(8,len(original_eligible_sp))
        if np.any(allowed):
            arr[allowed]=np.nanmean(m[:,allowed],axis=0)
        return arr
    s_matrix=[]
    for sp in sorted(source_sp):
        a=sim_guild[sp]["S_sum"]
        b=sim_guild[sp]["S_den"]
        s_matrix.append(np.divide(a,b,out=np.full(R,np.nan),where=b>0))
    s_matrix=np.stack(s_matrix)
    s_null=np.nanmean(s_matrix,axis=0)
    s_null[np.isfinite(s_matrix).sum(axis=0)<min(8,len(source_sp))]=np.nan
    observed_source_events={
        "E_legacy_positive_all_declining":f"{SOURCE_EPOS}/{SOURCE_DECLINING}",
        "size_informative_declining":SOURCE_SIZE_INFORMATIVE,
        "E_legacy_positive_AND_S_negative":f"{SOURCE_EPOS_SIZE_NEG}/{SOURCE_SIZE_INFORMATIVE}",
        "both_unique_leaders":SOURCE_LEAD_BOTH_UNIQUE,
        "observed_switch":f"{SOURCE_LEAD_SWITCH}/{SOURCE_LEAD_BOTH_UNIQUE}",
        "observed_joint_Elegacy_positive_AND_switch":f"{SOURCE_EPOS_AND_SWITCH}/{SOURCE_LEAD_BOTH_UNIQUE}",
        "observed_joint_Eboth_positive_AND_switch":
            f"{obs['E_both_unbiased_positive_and_switched']}/{SOURCE_LEAD_BOTH_UNIQUE}",
        "species_equal_source_size_score_S":float(S_obs),
        "species_equal_unique_leader_switch":species_obs("switch"),
        "species_equal_E_legacy_AND_switch":species_obs("joint_legacy"),
        "source_species_size_informative_n":len(source_sp),
        "source_species_unique_leader>=3_n":len(original_eligible_sp),
    }
    den_max=np.max(sims_all_den)
    if den_max>SOURCE_LEAD_BOTH_UNIQUE:
        raise ValueError("V46_MORE_ELIGIBLE_SIM_LEADERS_THAN_ORIGINAL_FIXED_COHORT")
    def rate(num,den):
        return np.divide(num,den,out=np.full(R,np.nan),where=den>0)
    return {
        "status":"V46_ORIGINAL_JNCC_SOURCE_959_PANEL_TWO_EPOCH_NULL_COMPLETED",
        "source_observed_identity_unchanged":observed_source_events,
        "two_epoch_pooled_multinomial_R":R,
        "two_epoch_model_source_fixed_N0_N1_each_panel":True,
        "simulated_unique_leader_eligible_panel_count_quantiles_05_50_95":[
            float(z) for z in np.quantile(sims_all_den,[.05,.5,.95])
        ],
        "simulated_S_early_epoch_equal_component_size_undefined_replicate_number_mean":
            float(np.mean(sims_all_S_undefined)),
        "panels_weighted_original_leader_switch_vs_dual_epoch_null":
            _stats(rate(sims_all_sw,sims_all_den),SOURCE_LEAD_SWITCH/SOURCE_LEAD_BOTH_UNIQUE),
        "species_equal_original_leader_switch_vs_dual_epoch_null":
            _stats(species_null("switch_num","switch_den"),species_obs("switch")),
        "panels_weighted_old_Epositive_and_leader_switch_vs_dual_epoch_null":
            _stats(rate(sims_all_joint_legacy,sims_all_den),
                   SOURCE_EPOS_AND_SWITCH/SOURCE_LEAD_BOTH_UNIQUE),
        "species_equal_old_Epositive_and_leader_switch_vs_dual_epoch_null":
            _stats(species_null("joint_legacy_num","switch_den"),species_obs("joint_legacy")),
        "panels_weighted_two_epoch_unbiased_Epositive_and_switch_vs_null":
            _stats(rate(sims_all_joint_both,sims_all_den),
                   obs["E_both_unbiased_positive_and_switched"]/SOURCE_LEAD_BOTH_UNIQUE),
        "source_species_equal_V37_size_S_vs_dual_epoch_null":
            _stats(s_null,float(S_obs),tail="lower"),
        "panel_weighted_original_legacy_Epositive_vs_dual_epoch_null":
            _stats(sims_all_Epos/SOURCE_DECLINING,SOURCE_EPOS/SOURCE_DECLINING),
        "limits":{
            "fitted_pooled_original_site_probabilities_use_both_observed_snapshots":True,
            "both_epoch_multinomial_sampling_is_not_field_count_error_calibrated":True,
            "same_Site_ID_historical_nesting_boundary_not_independently_verified":True,
            "leader_replacement_does_not_observe_true_bird_dispersal":True,
            "positive_original_predator_pressure_not_identified":True,
            "all_old_V37_and_V38_results_preserved_unchanged":True,
            "null_family_chosen_after_original_effects_known":True,
        },
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result={
        "status":"V46_ORIGINAL_TWO_EPOCH_SOURCE_OR_NULL_HOLD",
        "date":"2026-10-27",
        "contract":"contracts/JNCC_V46_TWO_EPOCH_LEADER_SIZE_STABILITY_POSTRESULT.md",
        "original_source_SHA256":v37.ORIGINAL_SHA,
        "seed":SEED,"replicates":R,
        "post_original_V37_V38_result_diagnostic":True,
        "no_predator_GBIF_Falkland_or_Antarctic_new_outcome_read":True,
    }
    try:
        source,qa=v37.source_intake()
        result["source_quality"]=qa
        result["analysis"]=source_panel_replay_and_null(source)
        result["status"]=result["analysis"]["status"]
    except Exception as e:
        result["error"]=type(e).__name__+": "+str(e)[:750]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    compact={"status":result["status"],"source_N":result.get("source_quality",{}).get("declining_total_panels_before_size_variation"),
             "observed":result.get("analysis",{}).get("source_observed_identity_unchanged"),
             "sizeS":result.get("analysis",{}).get("source_species_equal_V37_size_S_vs_dual_epoch_null"),
             "leader":result.get("analysis",{}).get("panels_weighted_original_leader_switch_vs_dual_epoch_null"),
             "leader_species_equal":result.get("analysis",{}).get("species_equal_original_leader_switch_vs_dual_epoch_null"),
             "joint":result.get("analysis",{}).get("panels_weighted_old_Epositive_and_leader_switch_vs_dual_epoch_null"),
             "joint_unbiased":result.get("analysis",{}).get("panels_weighted_two_epoch_unbiased_Epositive_and_switch_vs_null"),
             "error":result.get("error")}
    print(json.dumps(compact,ensure_ascii=False))
    if result["status"]!="V46_ORIGINAL_JNCC_SOURCE_959_PANEL_TWO_EPOCH_NULL_COMPLETED":
        raise SystemExit(2)

if __name__=="__main__":
    main()
