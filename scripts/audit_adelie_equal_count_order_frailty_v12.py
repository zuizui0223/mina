#!/usr/bin/env python3
"""Exact source-free falsification gate for multi-year Adelie reproductive memory.

Two histories (1,0,1) and (0,1,1) have same length, success count,
last/current observation and focal next prediction. Conditioning on a
lifetime fixed type plus shared additive *calendar-year* shocks is
insensitive to their order. But static type-by-year interactions alone
can make the order predict the next success without any genuine
within-bird carryover. Hence a positive empirical second-order test is
not automatically causal memory. This script reads NO penguin records.
"""
from __future__ import annotations

import argparse
import json
from math import exp, log
from pathlib import Path

HISTORY_A=(1,0,1)
HISTORY_B=(0,1,1)

def logistic(x):
    return 1/(1+exp(-x))

def binary_prob(seq, byyear):
    if len(seq)!=len(byyear) or not seq or any(y not in (0,1) for y in seq):
        raise ValueError("Every historical attempt must have observed binary outcome")
    p=1.0
    for y,q in zip(seq,byyear):
        if not 0<q<1: raise ValueError("Invalid Bernoulli probability")
        p*=q if y else (1-q)
    return p

def posterior_type(seq, hi, lo, weight=.5):
    if not (0<weight<1):
        raise ValueError("Invalid mixture weight")
    l_hi=binary_prob(seq,hi[:len(seq)])*weight
    l_lo=binary_prob(seq,lo[:len(seq)])*(1-weight)
    return l_hi/(l_hi+l_lo)

def next_probability(seq,hi,lo,weight=.5):
    if len(hi)!=len(seq)+1 or len(lo)!=len(seq)+1:
        raise ValueError("Current next year must be specified separately")
    posterior=posterior_type(seq,hi,lo,weight)
    return posterior*hi[-1]+(1-posterior)*lo[-1]

def scenario(hi,lo,label):
    pa=posterior_type(HISTORY_A,hi,lo)
    pb=posterior_type(HISTORY_B,hi,lo)
    na=next_probability(HISTORY_A,hi,lo)
    nb=next_probability(HISTORY_B,hi,lo)
    return {
        "source_free_null_model":label,
        "history_101":list(HISTORY_A),
        "history_011":list(HISTORY_B),
        "number_prior_successes_each":2,
        "last_year_success_each":True,
        "posterior_high_type_given_101":pa,
        "posterior_high_type_given_011":pb,
        "next_success_given_101":na,
        "next_success_given_011":nb,
        "apparent_order_difference":na-nb,
        "real_outcome_to_outcome_causal_memory":0,
    }

def analyze():
    fixed=scenario([.8]*4,[.2]*4,"STATIC_BIRD_QUALITY_IID_BERNOULLI")
    # Type-specific intercept plus same year shock at each occasion.
    yr=[-.6,.5,.2,.25]
    h=[logistic(log(.8/.2)+b) for b in yr]
    l=[logistic(log(.2/.8)+b) for b in yr]
    additive=scenario(h,l,"LIFELONG_QUALITY_INTERCEPT_PLUS_SHARED_CALENDAR_YEAR_LOGIT_EFFECT")
    # Deliberately constructed stable phenotypes with opposite response
    # sensitivities in year 1 and 2, but NO preceding-success dependence.
    interaction=scenario(
        [.75,.45,.65,.75],[.45,.75,.65,.25],
        "FIXED_QUALITY_TYPE_BY_YEAR_INTERACTION_BUT_NO_CAUSAL_REPRODUCTIVE_MEMORY"
    )
    for s in (fixed,additive,interaction):
        if s["real_outcome_to_outcome_causal_memory"]!=0:
            raise ValueError("The mathematical controls must have zero state carry-over")
    assert abs(fixed["apparent_order_difference"])<1e-12
    assert abs(additive["apparent_order_difference"])<1e-12
    assert abs(interaction["apparent_order_difference"]-2/7)<1e-12
    return {
        "status":"EQUAL_HISTORY_COUNTS_REMOVE_SIMPLE_FRAILTY_BUT_NOT_QUALITY_BY_YEAR_INTERACTIONS",
        "interpretation":"Mathematical negative controls, NOT Antarctic penguin field estimates",
        "shared_history_length":3,
        "shared_history_successes":2,
        "shared_last_year_outcome":1,
        "quality_iid":fixed,
        "quality_additive_year":additive,
        "quality_interacting_year":interaction,
        "fixed_iid_order_permutations_exchangeable_given_count":True,
        "additive_logit_year_intercept_quality_order_posterior_invariant_given_count":True,
        "quality_by_year_interaction_induces_order_dependence_without_any_carryover":True,
        "no_confirmation_of_true_biological_memory_or_learning":True,
        "observed_breeding_success_conditional_on_an_attempt_not_survival_or_participation":True,
        "observed_absent_and_not_breeding_states_have_no_defined_binary_success_here":True,
        "individual_penguin_source_data_rows_read":0,
        "new_Crozier_cohort_outcomes_fitted":0,
        "p_values_or_independent_field_effects_computed":False,
        "Ecology_PR189_unmodified":True,
        "locked_USAP_PR142_unmodified":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    r=analyze()
    args.out.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    for name in ("quality_iid","quality_additive_year","quality_interacting_year"):
        z=r[name]
        print("NULL_FRAILTY_SCENARIO",name,
              "NEXT_101",round(z["next_success_given_101"],9),
              "NEXT_011",round(z["next_success_given_011"],9),
              "DIFF",round(z["apparent_order_difference"],9))
    print("ACTUAL_PENGUIN_HISTORY_ROWS_READ",r["individual_penguin_source_data_rows_read"])
    print("CAUSAL_MEMORY_FOUND",False)

if __name__=="__main__":
    main()
