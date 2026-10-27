#!/usr/bin/env python3
"""V39 source-first JNCC exact matched-year census structural sensitivity.

Original K (Seabird 2000 survey year) and N (Seabirds Count survey year) must
be constant among ALL child Site.ID rows within original Master-site×species
same unit. Source structure selected BEFORE opening original L/O magnitudes.
Exploratory POST original V37/V38 effects; no causal island/predator claim.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np

import audit_jncc_two_censuses_source_v28 as v28
import audit_jncc_comparable_site_panels_v29 as v29
import model_jncc_component_concentration_v30 as v30
import model_jncc_size_share_retention_v37 as v37
import analyze_jncc_hierarchy_turnover_v38 as v38

ALPHA=.5
N_SIM=1999
SEED=20261027
MIN_DECLINING=100
MIN_SPECIES=8
MIN_COUNTRY_MASTER=30
MIN_SOURCE_UNITS=3


def year_metadata(rec_group: list) -> dict:
    years0={r["year_2000"] for r,_ in rec_group}
    years1={r["year_recent"] for r,_ in rec_group}
    return {
        "uniform_earlier_year":len(years0)==1,
        "uniform_later_year":len(years1)==1,
        "both_years_uniform":len(years0)==1 and len(years1)==1,
        "num_different_original_earlier_years":len(years0),
        "num_different_original_later_years":len(years1),
        "source_child_count":len(rec_group),
    }


def source_only_year_gate():
    raw, meta=v28.download_original()
    if meta["original_sha256"]!=v29.ORIGINAL_SHA or hashlib.sha256(raw).hexdigest()!=v29.ORIGINAL_SHA:
        raise ValueError("SOURCE_ORIGINAL_PUBLISHER_SHA_MISMATCH")
    rows=list(v29.original_rows(raw))
    source_qa=v29.coverage(rows)
    if not source_qa["frozen_eligibility_gate_pass"] or (
        source_qa["unique_original_two_census_site_species_rows_after_literal_QA"]!=14112
        or source_qa["qualified_species_country_master_unit_panels_with_ge3_sites"]!=1485
    ):
        raise ValueError("V29_SOURCE_SOURCE_COHORT_DRIFT")
    parents,identity=v30.extract_structural(rows)
    if not identity["pre_count_structural_gate_pass"] or len(parents)!=1483:
        raise ValueError("V30_SOURCE_PARENT_GUARD_DRIFT")
    class_counts=Counter()
    bycountry=Counter();byspecies=Counter()
    for parent,group in parents.items():
        stage=year_metadata(group)
        if stage["uniform_earlier_year"]:class_counts["earlier_same_year"]+=1
        if stage["uniform_later_year"]:class_counts["later_same_year"]+=1
        if stage["both_years_uniform"]:
            class_counts["BOTH_YEARS_UNIFORM"]+=1
            bycountry[parent[1]]+=1
            byspecies[parent[0]]+=1
    m={
        "original_parent_guarded_panels":len(parents),
        "all_source_rows_not_birth_death_events":True,
        "original_earlier_year_uniform_parent_n":class_counts["earlier_same_year"],
        "original_later_year_uniform_parent_n":class_counts["later_same_year"],
        "BOTH_original_epoch_years_uniform_parent_n":class_counts["BOTH_YEARS_UNIFORM"],
        "strictly_both_uniform_source_panels_by_species":dict(sorted(byspecies.items())),
        "strictly_both_uniform_source_panels_by_country":dict(sorted(bycountry.items())),
        "unknown_source_coverage_bias_not_eliminated":True,
        "source_year_uniform_does_not_guarantee_colony_polygon_identity":True,
        "original_two_census_counts_opened":0,
    }
    # This is a purely source-metadata gate: the full count stage is opened
    # only if source-only year-aligned panel support is enough.
    if class_counts["BOTH_YEARS_UNIFORM"]<MIN_DECLINING or len(byspecies)<MIN_SPECIES:
        return None,m
    return {k:v for k,v in parents.items() if year_metadata(v)["both_years_uniform"]},m


def numeric_support(panels):
    eligible=[]
    drop=Counter()
    for parent,children in sorted(panels.items()):
        earlier=[];later=[]
        for _r,src in children:
            n0=v30.exact_count(src.get("L"))
            n1=v30.exact_count(src.get("O"))
            if n0 is None or n1 is None:
                earlier=[];later=[];drop["unparseable_count"]+=1
                break
            earlier.append(n0);later.append(n1)
        if not earlier:continue
        if sum(earlier)<2 or sum(later)<2:
            drop["sum_epoch_lt2"]+=1
            continue
        eligible.append((parent,earlier,later))
    declining=[(p,a,b) for p,a,b in eligible if sum(b)<sum(a)]
    informative=[(p,a,b) for p,a,b in declining if len(set(a))>1]
    supporting_species=Counter(p[0] for p,_,_ in informative)
    ctrmasters={(p[1],p[2]) for p,_,_ in informative}
    units={p[3] for p,_,_ in informative}
    support={
        "integer_valid_original_uniform_year_panels":len(eligible),
        "original_uniform_year_panels_with_lower_recent_total":len(declining),
        "declining_panels_with_nonidentical_original_child_sizes":len(informative),
        "species_with_3_or_more_size_informative_declines":sum(n>=3 for n in supporting_species.values()),
        "distinct_country_master_networks":len(ctrmasters),
        "distinct_original_count_units":len(units),
        "numeric_drop_reasons":dict(drop),
    }
    support["V39_pre_effect_cohort_information_gate_pass"]=bool(
       len(informative)>=MIN_DECLINING and
       support["species_with_3_or_more_size_informative_declines"]>=MIN_SPECIES and
       len(ctrmasters)>=MIN_COUNTRY_MASTER and len(units)>=MIN_SOURCE_UNITS
    )
    return informative,support,declining


def same_year_replay(informative,all_declines):
    rng=np.random.default_rng(SEED)
    species_scores=defaultdict(list)
    species_null=defaultdict(lambda:np.zeros(N_SIM,dtype=np.float64))
    country_records=[]
    for parent,old,late in informative:
        g=v37.baseline_size_score(old,late)
        if g is None:
            raise ValueError("SOURCE_SCORE_INFORMATION_CONFLICT")
        s=parent[0]
        species_scores[s].append(float(g["score"]))
        species_null[s]+=v37.exact_null_scores(g,rng)
        country_records.append((s,parent[1],float(g["score"])))
    sp=sorted(s for s,v in species_scores.items() if len(v)>=3)
    if len(sp)<MIN_SPECIES:
        raise ValueError("SOURCE_SP_REPLICATION_GATE_CHANGED")
    t=float(np.mean([np.mean(species_scores[s]) for s in sp]))
    sims=np.mean(np.stack([species_null[s]/len(species_scores[s]) for s in sp]),axis=0)
    leave_country={}
    for country in sorted({c for _,c,_ in country_records}):
        by_sp=defaultdict(list)
        for s,c,val in country_records:
            if country!=c:by_sp[s].append(val)
        selected=[np.mean(vals) for _sp,vals in by_sp.items() if len(vals)>=3]
        leave_country[country]=float(np.mean(selected)) if selected else None

    # Already declared V38 decomposition: no test retuning on alignment.
    counts=Counter()
    bysp=defaultdict(Counter)
    for parent,old,late in all_declines:
        m=v38.decomposition(old,late)
        event={
          "declines":True,
          "Epos":m["E_positive"],
          "score_informative":m["S_informative"],
          "Epos_and_Snegative":bool(m["S_informative"] and m["E_positive"] and m["S_negative"]),
          "unique_both_leaders":m["both_leaders_unique"],
          "switched_unique_leader":bool(m["both_leaders_unique"] and m["leader_switch"]),
          "Epos_and_switched":bool(m["both_leaders_unique"] and m["leader_switch"] and m["E_positive"]),
        }
        for key,yes in event.items():
            counts[key]+=int(yes)
            bysp[parent[0]][key]+=int(yes)
    report={
        "exact_same_epoch_primary_species_equal_size_score":t,
        "original_informative_decline_panels":len(informative),
        "species":len(sp),
        "species_with_positive_mean_size_score":sum(np.mean(species_scores[s])>0 for s in sp),
        "each_source_species_mean_size_score":{s:{"n":len(species_scores[s]),"mean":float(np.mean(species_scores[s]))} for s in sp},
        "null_mean":float(np.mean(sims)),
        "null_q05":float(np.quantile(sims,.05)),
        "null_q95":float(np.quantile(sims,.95)),
        "conditional_null_right_tail_fraction":float((1+np.sum(sims>=t))/(N_SIM+1)),
        "country_leave_out_species_equal_mean_size_score":leave_country,
        "observed_same_epoch_source_concentration_and_leader_events":dict(counts),
        "observed_same_epoch_fraction_Epos_among_declines":counts["Epos"]/counts["declines"],
        "observed_same_epoch_fraction_Epos_and_Snegative_among_size_informative":counts["Epos_and_Snegative"]/counts["score_informative"],
        "observed_same_epoch_fraction_switched_among_unique_leaders":counts["switched_unique_leader"]/counts["unique_both_leaders"] if counts["unique_both_leaders"] else None,
        "observed_same_epoch_fraction_Epos_and_switched_among_unique_leaders":counts["Epos_and_switched"]/counts["unique_both_leaders"] if counts["unique_both_leaders"] else None,
        "frozen_V37_full_sample_T_not_reestimated_or_modified":-0.5388642801626898,
        "this_subgroup_was_source_structurally_defined_post_V37_observed_result":True,
        "no_alternative_subgroup_windows_fitted":True,
    }
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result={
      "status":"V39_ORIGINAL_JNCC_YEAR_ALIGNMENT_SOURCE_HOLD",
      "date":"2026-10-27",
      "source_original_sha256":v29.ORIGINAL_SHA,
      "contract":"contracts/JNCC_MATCHED_EPOCH_COHORT_V39_FROZEN.md",
      "no_island_predator_or_social_Allee_causes_estimated":True,
    }
    try:
        parents,m=source_only_year_gate()
        result["source_only_metadata_year_alignment"]=m
        if parents is None:
            result["status"]="STOP_V39_SOURCE_ONLY_YEAR_ALIGNED_STRUCTURAL_SUPPORT"
            result["year_aligned_animal_response_opened"]=False
        else:
            info,qa,all_declines=numeric_support(parents)
            result["numeric_cohort_gate"]=qa
            if not qa["V39_pre_effect_cohort_information_gate_pass"]:
                result["status"]="STOP_V39_COUNT_COMPATIBLE_SOURCE_SUPPORT"
                result["size_retention_effect_computed"]=False
            else:
                result["V39_fixed_year_aligned_sensitivity"]=same_year_replay(info,all_declines)
                result["status"]="V39_JNCC_STRICT_SAME_YEARS_EPOCH_SENSITIVITY_COMPLETED"
    except Exception as exc:
        result["error"]=type(exc).__name__+": "+str(exc)[:600]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"] not in (
        "STOP_V39_SOURCE_ONLY_YEAR_ALIGNED_STRUCTURAL_SUPPORT",
        "STOP_V39_COUNT_COMPATIBLE_SOURCE_SUPPORT",
        "V39_JNCC_STRICT_SAME_YEARS_EPOCH_SENSITIVITY_COMPLETED",
    ):
        raise SystemExit(2)

if __name__=="__main__":main()
