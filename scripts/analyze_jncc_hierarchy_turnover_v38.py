#!/usr/bin/env python3
"""V38 POST-RESULT descriptive: positive concentration E with negative size score S.

Reuses exact JNCC/V30 source-paired components, V37 alpha=.5 score and
fixed-count null; does not rescue H1a, reopen predator H2, or imply bird moves.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

import model_jncc_size_share_retention_v37 as v37

SEED = 20261028
R = 1999
MIN_SPECIES_PANELS = 3
EXPECTED_DECLINING = 959


def leader(n):
    """Unique single largest source child, or None when there is a tie."""
    x=np.asarray(n,dtype=np.int64)
    maxi=int(x.max())
    idx=np.flatnonzero(x==maxi)
    return int(idx[0]) if len(idx)==1 else None


def decomposition(old,late,draws=None):
    """Fixed observable two-census quantities. Never equate changed Site.ID rank with dispersal."""
    n0=np.asarray(old,dtype=np.int64)
    n1=np.asarray(late,dtype=np.int64)
    if int(n1.sum())>=int(n0.sum()):
        raise ValueError("V38_PRIMARY_COHORT_MUST_BE_DECLINING")
    p0=n0/n0.sum()
    p1=n1/n1.sum()
    c0=float(p0@p0)
    c1=float(p1@p1)
    E=c1-(c0+(1-c0)/int(n1.sum()))
    s=v37.baseline_size_score(n0,n1)
    lead0=leader(n0);lead1=leader(n1)
    both_unique=lead0 is not None and lead1 is not None
    return {
        "E_positive":bool(E>0),
        "E":float(E),
        "S_negative":(bool(s["score"]<0) if s is not None else None),
        "S":(float(s["score"]) if s is not None else None),
        "S_informative":s is not None,
        "early_leader_unique":lead0 is not None,
        "both_leaders_unique":both_unique,
        "leader_switch":(bool(lead0!=lead1) if both_unique else None),
        "initial_leader_share_change":(
            float(p1[lead0]-p0[lead0]) if lead0 is not None else None
        ),
        "p0_smoothed":s["pstar"] if s is not None else
          (n0+v37.ALPHA)/(n0.sum()+v37.ALPHA*len(n0)),
        "normalized_size":s["size_standardized"] if s is not None else None,
        "n1":int(n1.sum()),
        "raw_p0":p0,
        "lead0":lead0,
    }


def simulate_events(metrics,rng,replicates=R):
    if replicates!=R:
        raise ValueError("FROZEN_V38_REPLICATES")
    n1=metrics["n1"]
    p=metrics["p0_smoothed"]
    out=rng.multinomial(n1,p,size=replicates)
    scaled=out.astype(np.float64)/n1
    source_c0=float(metrics["raw_p0"]@metrics["raw_p0"])
    E=(scaled**2).sum(axis=1)-(source_c0+(1-source_c0)/n1)
    positive=E>0
    if metrics["S_informative"]:
        size_scores=(scaled-p) @ metrics["normalized_size"]
        jointA=positive & (size_scores<0)
    else:
        jointA=None
    mx=out.max(axis=1)
    unique=(out==mx[:,None]).sum(axis=1)==1
    eligible_B=unique & (metrics["lead0"] is not None)
    sw=(out.argmax(axis=1)!=metrics["lead0"]) & eligible_B
    jointB=positive & sw
    return {"Epos":positive,"A":jointA,"B":jointB,"B_denominator":eligible_B,"switch":sw}


def _summary_event(observed,denominator,nulldraw_numer,nulldraw_denom):
    valid_sp=sorted([sp for sp,den in denominator.items() if den>=MIN_SPECIES_PANELS])
    if not valid_sp:
        return {"status":"STOP_TOO_FEW_UNIQUE_REPLICATE_SPECIES"}
    obs_species={sp:observed[sp]/denominator[sp] for sp in valid_sp}
    null_species=[]
    for sp in valid_sp:
        if isinstance(nulldraw_denom[sp],np.ndarray):
            denarr=nulldraw_denom[sp]
            sim=np.divide(nulldraw_numer[sp],denarr,
                          out=np.full(R,np.nan),where=denarr>0)
        else:
            sim=nulldraw_numer[sp]/nulldraw_denom[sp]
        null_species.append(sim)
    nullmatrix=np.stack(null_species)
    count_valid=np.isfinite(nullmatrix).sum(axis=0)
    equal_null=np.full(R,np.nan)
    ok=count_valid>=min(8,len(valid_sp))
    equal_null[ok]=np.nanmean(nullmatrix[:,ok],axis=0)
    good=equal_null[np.isfinite(equal_null)]
    return {
        "source_species_valid_n":len(valid_sp),
        "observed_numerator_by_species":{sp:int(observed[sp]) for sp in valid_sp},
        "observed_eligible_denominator_by_species":{sp:int(denominator[sp]) for sp in valid_sp},
        "observed_species_equal_fraction":float(np.mean(list(obs_species.values()))),
        "observed_all_valid_panels_count":int(sum(observed[sp] for sp in valid_sp)),
        "observed_all_valid_panels_denominator":int(sum(denominator[sp] for sp in valid_sp)),
        "observed_unweighted_panel_fraction":float(
            sum(observed[sp] for sp in valid_sp)/sum(denominator[sp] for sp in valid_sp)
        ),
        "null_species_equal_mean":float(good.mean()) if len(good) else None,
        "null_species_equal_q05":float(np.quantile(good,.05)) if len(good) else None,
        "null_species_equal_q95":float(np.quantile(good,.95)) if len(good) else None,
        "null_replicate_support_n":int(len(good)),
    }


def simulation_counterexample(seed=20261028, repetitions=5000):
    """Independent snapshots of fixed true shares show baseline score regression to mean."""
    if seed!=SEED or repetitions!=5000:
        raise ValueError("COUNTEREXAMPLE_FROZEN")
    rng=np.random.default_rng(seed)
    fixed_true=np.array([.55,.30,.15])
    score=[]
    for _ in range(repetitions):
        x=rng.multinomial(40,fixed_true)
        y=rng.multinomial(25,fixed_true)
        candidate=v37.baseline_size_score(x,y)
        if candidate is not None:
            score.append(candidate["score"])
    return {
        "simulated_independent_censuses_no_change_in_underlying_site_shares":True,
        "true_shares_only_in_synthetic_counterexample":[.55,.30,.15],
        "baseline_total":40,
        "late_total":25,
        "replicates":repetitions,
        "fixed_seed":seed,
        "simulated_negative_size_score_average":float(np.mean(score)),
        "regression_to_mean_can_generate_negative_scores_without_biological_retention":True,
        "this_is_not_a_fitted_model_of_real_JNCC_counting_error":True,
    }


def analyse(records):
    declined=[(parent,old,new) for parent,old,new in records if sum(new)<sum(old)]
    if len(declined)!=EXPECTED_DECLINING:
        raise ValueError("ORIGINAL_V30_DECLINING_SUPPORT_CHANGED")
    rng=np.random.default_rng(SEED)
    nobs={"A":defaultdict(int),"B":defaultdict(int),"switch":defaultdict(int),
          "Epos":defaultdict(int)}
    den={"A":defaultdict(int),"B":defaultdict(int),"switch":defaultdict(int),
         "Epos":defaultdict(int)}
    sims_num={ev:defaultdict(lambda:np.zeros(R,dtype=np.float64)) for ev in nobs}
    sims_den={ev:defaultdict(lambda:np.zeros(R,dtype=np.float64)) for ev in nobs}
    tie_stats=defaultdict(int)
    lead_deltas=defaultdict(list)
    for parent,old,late in declined:
        sp=parent[0]
        metric=decomposition(old,late)
        null=simulate_events(metric,rng)
        den["Epos"][sp]+=1
        nobs["Epos"][sp]+=int(metric["E_positive"])
        sims_num["Epos"][sp]+=null["Epos"]
        sims_den["Epos"][sp]+=1

        if metric["S_informative"]:
            den["A"][sp]+=1
            nobs["A"][sp]+=int(metric["E_positive"] and metric["S_negative"])
            sims_num["A"][sp]+=null["A"]
            sims_den["A"][sp]+=1
        else:
            tie_stats["S_size_uninformative_count"]+=1

        if metric["early_leader_unique"]:
            lead_deltas[sp].append(metric["initial_leader_share_change"])
            tie_stats["early_single_largest"]=tie_stats["early_single_largest"]+1
        else:
            tie_stats["early_leader_tie"]+=1
        if metric["both_leaders_unique"]:
            for event,yes in (
                ("switch",metric["leader_switch"]),
                ("B",metric["E_positive"] and metric["leader_switch"]),
            ):
                den[event][sp]+=1
                nobs[event][sp]+=int(yes)
        else:
            tie_stats["one_or_both_leaders_tied"]+=1

        sims_den["switch"][sp]+=null["B_denominator"]
        sims_num["switch"][sp]+=null["switch"]
        sims_den["B"][sp]+=null["B_denominator"]
        sims_num["B"][sp]+=null["B"]
    outputs={
        ev:_summary_event(nobs[ev],den[ev],sims_num[ev],sims_den[ev])
        for ev in ("Epos","A","switch","B")
    }
    return {
        "status":"JNCC_V38_POST_V37_DESC_POSITIVE_CONCENTRATION_WITH_HIERARCHY_REVERSAL",
        "declining_original_source_parent_panels":len(declined),
        "outcomes":outputs,
        "missing_lead_or_size_support":dict(tie_stats),
        "original_largest_component_mean_share_delta_species_equal":float(
            np.mean([np.mean(v) for v in lead_deltas.values() if len(v)>=MIN_SPECIES_PANELS])
        ),
        "fixed_no_turnover_independent_measurement_counterexample":simulation_counterexample(),
        "limits":{
            "data_post_outcome_descriptive_not_confirmation":True,
            "source_site_identity_not_historically_validated_polygon":True,
            "original_two_censuses_cannot_measure_dispersal":True,
            "null_is_proportional_allocation_not_observation_error":True,
            "negative_size_score_may_reflect_initial_measurement_regression":True,
            "V36_predator_effect_gating_still_failed":True,
            "no_social_Allee_or_habitat_qualitative_cause_diagnosed":True,
        },
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    result={
      "status":"JNCC_V38_SOURCE_OR_DIAGNOSTIC_HOLD",
      "contract":"contracts/JNCC_CONCENTRATION_HIERARCHY_TURNOVER_V38_DIAGNOSTIC.md",
      "post_result_hypothesis_timing":True,
      "JNCC_original_child_counts_materialized_in_git":False,
      "seed":SEED,"null_replicates":R,
    }
    try:
        rows,qa=v37.source_intake()
        result["source"]=qa
        result["diagnostics"]=analyse(rows)
        result["status"]=result["diagnostics"]["status"]
    except Exception as e:
        result["error"]=type(e).__name__+": "+str(e)[:900]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]!="JNCC_V38_POST_V37_DESC_POSITIVE_CONCENTRATION_WITH_HIERARCHY_REVERSAL":
        raise SystemExit(2)

if __name__=="__main__":main()
