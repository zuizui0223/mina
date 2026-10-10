#!/usr/bin/env python3
"""Exact counterexample: second-order memory can be entirely latent quality.

Two never-changing individual quality classes, p=0.8 and p=0.2, each half
the population. Conditional on each person's class, yearly breeding success
is independent Bernoulli, NO within-individual memory or carry-over process.
Observing TWO past successes rather than a success following a failure
changes posterior class mixture and thus next-year predictive probability.
This is a proof of nonidentifiability, NOT an ecological data result.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def posterior_high(prior_history, p_high=0.8, p_low=0.2, fraction_high=0.5):
    if not (0<p_low<p_high<1 and 0<fraction_high<1):
        raise ValueError("Invalid quality-class mixture")
    if not prior_history or any(x not in (0,1) for x in prior_history):
        raise ValueError("History must contain measured binary successes only")
    hi=fraction_high
    lo=1-fraction_high
    for success in prior_history:
        hi*=p_high if success else 1-p_high
        lo*=p_low if success else 1-p_low
    return hi/(hi+lo)

def forecast(posterior, p_high=0.8, p_low=0.2):
    return posterior*p_high+(1-posterior)*p_low

def evaluate():
    sequences={
        "previous_success_current_success":(1,1),
        "previous_failure_current_success":(0,1),
        "previous_success_current_failure":(1,0),
        "previous_failure_current_failure":(0,0),
    }
    results={}
    for label,seq in sequences.items():
        p=posterior_high(seq)
        results[label]={
            "previous_current_sequence":list(seq),
            "posterior_p_high_quality":p,
            "next_success_probability":forecast(p)
        }
    within_current_success_diff=(
        results["previous_success_current_success"]["next_success_probability"]-
        results["previous_failure_current_success"]["next_success_probability"])
    within_current_failure_diff=(
        results["previous_success_current_failure"]["next_success_probability"]-
        results["previous_failure_current_failure"]["next_success_probability"])
    return {
        "status":"LATENT_INDIVIDUAL_QUALITY_GENERATES_SPURIOUS_SECOND_ORDER_PREDICTION",
        "mechanism_assumed":"TWO_FIXED_INDIVIDUAL_QUALITY_CLASSES_NO_TRUE_TEMPORAL_STATE_DEPENDENCE",
        "fraction_high":0.5,
        "high_individual_annual_success_p":0.8,
        "low_individual_annual_success_p":0.2,
        "state_sequences":results,
        "apparent_old_success_bonus_given_current_success":within_current_success_diff,
        "apparent_old_success_bonus_given_current_failure":within_current_failure_diff,
        "individual_specific_state_memory_parameter":0,
        "individual_quality_persists_across_years":True,
        "predictive_information_does_not_imply_causal_history":True,
        "different_and_independent_island_replication_present":False,
        "actual_penguin_individual_records_read":0,
        "observed_wbwa_test_explained_by_this_simulation":False,
        "new_biological_causal_effect_estimated":False,
        "Ecology_PR189_unchanged":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    z=evaluate()
    args.out.write_text(json.dumps(z,indent=2)+"\n",encoding="utf8")
    print("NO_TRUE_MEMORY_MIXTURE_BUT_APPARENT_SECOND_LAG",z["apparent_old_success_bonus_given_current_success"])
    print("OLDER_BREEDING_HISTORY_CAUSAL_IDENTIFICATION",False)

if __name__=="__main__":main()
