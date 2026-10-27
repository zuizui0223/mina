#!/usr/bin/env python3
"""V44 FROZEN within original JNCC Master site ground-gull vs cliff-kittiwake E.

First source metadata gate (before biological count magnitudes); then source
count compatibility AND BOTH species decline gate; ONLY THEN E difference.
Do NOT replace failed source-support with all-trajectory or cross-unit data.
No invasive predator source labels or geographical SDM predictors used.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

import audit_jncc_within_master_nest_access_v44 as gate
import model_jncc_component_concentration_v30 as v30

N_SIM = 1999
SEED = 20261027
MIN_NETWORKS=10
MIN_HIGH_SPECIES=2
MIN_LOW_SPECIES=1


def count_panel(parent, source_rows):
    original=[];recent=[]
    for rec,row in source_rows:
        a=v30.exact_count(row.get("L"))
        b=v30.exact_count(row.get("O"))
        if a is None or b is None:
            return None,"NON_EXACT_OR_MISSING_SOURCE_COUNT"
        original.append(a);recent.append(b)
    if sum(original)<2 or sum(recent)<2:
        return None,"SOURCE_TOTAL_LT2"
    return {
        "parent_key":parent, "old":original,"late":recent,
        "N0":sum(original),"N1":sum(recent),
        "k":len(original), "declined":sum(recent)<sum(original),
        "country":parent[1],"species":parent[0],"unit":parent[3],
        "original_source_years0":[rec["year_2000"] for rec,_ in source_rows],
        "original_source_years1":[rec["year_recent"] for rec,_ in source_rows],
    },"OK"


def build_complete_compared_cohort(parent_rows,metadata_pairs):
    cache={}
    fail=Counter()
    eligible_all={}
    eligible_decline={}
    for master,pairs in sorted(metadata_pairs.items()):
        keep_all=[];keep_decline=[]
        for a,b in pairs:
            for k in (a,b):
                if k not in cache:
                    cache[k],why=count_panel(k,parent_rows[k])
                    if why!="OK":fail[why]+=1
            x,y=cache[a],cache[b]
            if x is None or y is None:
                fail["PAIR_MEMBER_NONCOMPARABLE_COUNT"]+=1
                continue
            keep_all.append((a,b))
            if x["declined"] and y["declined"]:
                keep_decline.append((a,b))
            else:
                fail["ONE_OR_BOTH_SOURCE_SPECIES_NOT_DECLINING"]+=1
        if keep_all:eligible_all[master]=keep_all
        if keep_decline:eligible_decline[master]=keep_decline
    def classes(pairs):
        hi=set(a for pool in pairs.values() for a,b in pool)
        lo=set(b for pool in pairs.values() for a,b in pool)
        return hi,lo
    high,low=classes(eligible_decline)
    info={
        "source_original_metadata_master_networks":len(metadata_pairs),
        "source_metadata_matched_candidate_pairs":sum(map(len,metadata_pairs.values())),
        "count_eligible_networks_all_trajectory":len(eligible_all),
        "source_count_eligible_pair_links_all_trajectory":sum(map(len,eligible_all.values())),
        "BOTH_GUILD_SOURCE_SPECIES_DECLINING_networks":len(eligible_decline),
        "BOTH_GUILD_SOURCE_SPECIES_DECLINING_source_pair_links":sum(map(len,eligible_decline.values())),
        "BOTH_DECLINING_distinct_accessible_species":sorted(k[0] for k in high) if len({k[0] for k in high})==len(high) else sorted({k[0] for k in high}),
        "BOTH_DECLINING_distinct_cliff_species":sorted({k[0] for k in low}),
        "BOTH_DECLINING_distinct_country_master_networks":len(eligible_decline),
        "BOTH_DECLINING_countries":dict(Counter(master[0] for master in eligible_decline)),
        "count_based_exclusion_reasons":dict(fail),
        "original_V30_concentration_E_values_opened_before_gate":False,
    }
    # fix possible multiple panels of same species across country/master:
    info["BOTH_DECLINING_distinct_accessible_species"]=sorted({k[0] for k in high})
    eligible=(len(eligible_decline)>=MIN_NETWORKS
              and len({k[0] for k in high})>=MIN_HIGH_SPECIES
              and len({k[0] for k in low})>=MIN_LOW_SPECIES)
    info["fixed_preregistered_both_declining_count_gate_pass"]=bool(eligible)
    return eligible_decline,eligible_all,cache,info


def E_from_counts(obj):
    n0=np.asarray(obj["old"],dtype=np.float64)
    n1=np.asarray(obj["late"],dtype=np.float64)
    p0=n0/obj["N0"]
    p1=n1/obj["N1"]
    c0=float(p0@p0)
    c1=float(p1@p1)
    return c1-(c0+(1-c0)/obj["N1"]),c0


def null_E(obj,rng):
    n0=np.asarray(obj["old"],dtype=np.float64)
    p0=n0/obj["N0"]
    c0=float(p0@p0)
    n1=obj["N1"]
    allocations=rng.multinomial(n1,p0,size=N_SIM)
    c1=((allocations/n1)**2).sum(axis=1)
    return c1-(c0+(1-c0)/n1)


def group_data(cohort,cache):
    """Each Master contributes exactly one guild difference."""
    bymaster={}
    keys=set()
    for master,pairs in sorted(cohort.items()):
        high=sorted({a for a,b in pairs})
        low=sorted({b for a,b in pairs})
        keys.update(high+low)
        bymaster[master]=(high,low)
    scores={}
    for key in sorted(keys):
        original,c0=E_from_counts(cache[key])
        scores[key]={"E":original,"C0":c0,"N0":cache[key]["N0"],
                     "N1":cache[key]["N1"],"k":cache[key]["k"],
                     "sp":key[0],"unit":key[3]}
    result=[]
    for master,(high,low) in sorted(bymaster.items()):
        d=float(np.mean([scores[k]["E"] for k in high])
                -np.mean([scores[k]["E"] for k in low]))
        result.append({"source_master":master,"diff_E":d,
                       "high":high,"low":low})
    return result,scores


def statistic_for_paired(cohort,cache,rng):
    bymaster,scores=group_data(cohort,cache)
    if not bymaster:
        return None
    T=float(np.mean([d["diff_E"] for d in bymaster]))
    per_net=np.array([d["diff_E"] for d in bymaster])
    scores_null={key:null_E(cache[key],rng) for key in sorted(scores)}
    sim=np.array([
      np.mean([scores_null[k] for k in row["high"]],axis=0)-
      np.mean([scores_null[k] for k in row["low"]],axis=0)
      for row in bymaster
    ])
    count_null=np.mean(sim,axis=0)
    flips=rng.choice([-1.,1.],size=(N_SIM,len(bymaster)))
    sign_stat=(flips*per_net[None,:]).mean(axis=1)
    all_high={key for row in bymaster for key in row["high"]}
    all_low={key for row in bymaster for key in row["low"]}
    def leaveout(source_taxon):
        remain=[row for row in bymaster
                if ((source_taxon not in {k[0] for k in row["high"]}
                     and source_taxon not in {k[0] for k in row["low"]}))]
        return {
            "retained_networks":len(remain),
            "mean_D_if_retained":float(np.mean([v["diff_E"] for v in remain])) if remain else None,
            "too_few_networks_to_support_original_primary_gate":len(remain)<MIN_NETWORKS,
        }
    without_scotland=[row for row in bymaster if row["source_master"][0]!="Scotland"]
    desc={
        "n_source_Country_Master_paired_networks":len(bymaster),
        "positive_master_networks_D_gt_0":int(np.sum(per_net>0)),
        "positive_master_network_fraction":float(np.mean(per_net>0)),
        "original_network_equal_mean_accessible_minus_cliff_E":T,
        "network_D_q05":float(np.quantile(per_net,.05)),
        "network_D_q50":float(np.median(per_net)),
        "network_D_q95":float(np.quantile(per_net,.95)),
        "finite_count_multinomial_null_1999_replicates":N_SIM,
        "finite_count_multinomial_null_mean_T":float(np.mean(count_null)),
        "finite_count_multinomial_null_q05_T":float(np.quantile(count_null,.05)),
        "finite_count_multinomial_null_q95_T":float(np.quantile(count_null,.95)),
        "conditional_allocation_right_tail_of_T":float((1+np.sum(count_null>=T))/(N_SIM+1)),
        "independent_Master_network_signflip_right_tail":float((1+np.sum(sign_stat>=T))/(N_SIM+1)),
        "positive_direction_accessible_more_concentrated_than_cliff_supported_descriptively":T>0,
        "accessible_species":sorted({key[0] for key in all_high}),
        "cliff_species":sorted({key[0] for key in all_low}),
        "species_drop_one_at_a_time":{
            taxon:leaveout(taxon) for taxon in sorted({k[0] for k in all_high|all_low})
        },
        "Scotland_excluded":{
            "remaining_networks":len(without_scotland),
            "mean_D":float(np.mean([r["diff_E"] for r in without_scotland])) if without_scotland else None,
            "source_number_unable_to_claim_cross_region_generalization":len(without_scotland)<MIN_NETWORKS,
        },
        "count_unit_distribution_in_original_comparable_panels":dict(Counter(
            scores[k]["unit"] for k in scores)),
        "median_initial_C0_by_guild":{
            "accessible":float(np.median([scores[k]["C0"] for k in all_high])),
            "cliff":float(np.median([scores[k]["C0"] for k in all_low])),
        },
        "median_child_count_by_guild":{
            "accessible":float(np.median([scores[k]["k"] for k in all_high])),
            "cliff":float(np.median([scores[k]["k"] for k in all_low])),
        },
        "median_latest_parent_total_by_guild":{
            "accessible":float(np.median([scores[k]["N1"] for k in all_high])),
            "cliff":float(np.median([scores[k]["N1"] for k in all_low])),
        },
        "different_original_count_shapes_may_create_variance_not_remove_by_source_guild":True,
        "guild_proxy_sole_cliff_species_cannot_support_generality_beyond_kittiwake":len({k[0] for k in all_low})==1,
        "no_site_specific_mammal_exposure_or_causal_predator_effect_measured":True,
        "association_benchmarks_not_Bayesian_true_occupancy_or_survey_error_p_value":True,
    }
    return desc


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    receipt={
        "status":"V44_SOURCE_OR_COUNTERPART_HOLD",
        "frozen_contract":"contracts/JNCC_WITHIN_MASTER_NEST_ACCESS_GUILD_V44_FROZEN.md",
        "original_SHA256":gate.v29.ORIGINAL_SHA,
        "null_reps":N_SIM,"seed":SEED,
        "no_UK_predator_SDM_or_GBIF_data_read":True,
        "no_new_mammal_presence_absence_claim":True,
    }
    try:
        parents,qualified,sourceqa=gate.fetch_and_gate()
        receipt["source_metadata_gate"]=sourceqa
        if not sourceqa["V44_primary_source_only_comparison_gate_pass"]:
            receipt["status"]="STOP_V44_METADATA_ONLY_10_NETWORK_SOURCE_GATE"
            receipt["E_access_cliff_effect_fitted"]=False
        else:
            both,allcomp,cache,numerics=build_complete_compared_cohort(parents,qualified)
            receipt["pre_contrast_numeric_count_eligibility"]=numerics
            if not numerics["fixed_preregistered_both_declining_count_gate_pass"]:
                receipt["status"]="STOP_V44_BOTH_DECLINING_SAME_MASTER_SOURCE_COUNT_GATE"
                receipt["E_access_cliff_effect_fitted"]=False
            else:
                rng=np.random.default_rng(SEED)
                receipt["primary_both_declining_networks"]=statistic_for_paired(both,cache,rng)
                receipt["secondary_all_trajectory_networks_DESCRIPTIVE_ONLY"]=statistic_for_paired(allcomp,cache,rng)
                receipt["status"]="V44_SOURCE_GUILDS_MATCHED_CONCENTRATION_CONTRAST_COMPUTED"
                receipt["E_access_cliff_effect_fitted"]=True
                receipt["possible_compatible_predator_mechanism_NOT_confirmed"]=True
    except Exception as ex:
        receipt["status"]="V44_SOURCE_OR_MODEL_ERROR_HOLD"
        receipt["error"]=type(ex).__name__+": "+str(ex)[:650]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="V44_SOURCE_OR_MODEL_ERROR_HOLD":
        raise SystemExit(2)

if __name__=="__main__":
    main()
