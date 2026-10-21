#!/usr/bin/env python3
"""V30 JNCC original two-census composition vs exact proportional-allocation benchmark."""
from __future__ import annotations
import argparse
from collections import defaultdict,Counter
from decimal import Decimal,InvalidOperation
import hashlib,json,math
from pathlib import Path
from statistics import mean,median
import audit_jncc_two_censuses_source_v28 as v28
import audit_jncc_comparable_site_panels_v29 as v29

SHA=v29.ORIGINAL_SHA
MIN_STRUCT_PANELS=100;MIN_STRUCT_SPECIES=10;MIN_STRUCT_MASTERS=50;MIN_STRUCT_UNITS=3
MIN_NUM_PANELS=40;MIN_NUM_SPECIES=8;MIN_NUM_MASTERS=15;MIN_NUM_UNITS=3
MIN_DECLINE_PANELS=20;MIN_DECLINE_SPECIES=6;MIN_DECLINE_MASTERS=10
MIN_SPECIES_DECLINE_PANELS=3
MAX_ORIGINAL_COUNT=10**9
TV_HIGH=.25

def normalize_name(v):
    return " ".join(str(v or "").casefold().split())

def extract_structural(rows):
    """No original L/O count magnitudes inspected prior to gates."""
    seen=defaultdict(list);exclusions=Counter()
    for sheet,ix,row in rows:
        if ix==4:continue
        record,why=v29.eligible_metadata(sheet,ix,row)
        if why:
            exclusions[why]+=1
            continue
        record["original_site_name"]=str(row.get("E","")).strip()
        key=(record["species"],record["country"],record["master"],record["site_id"])
        seen[key].append((record,row))
    unique={key:x[0] for key,x in seen.items() if len(x)==1}
    dup=len(seen)-len(unique)
    panels=defaultdict(list)
    for rec,source_row in unique.values():
        parent=(rec["species"],rec["country"],rec["master"],rec["unit"])
        panels[parent].append((rec,source_row))
    v29_panels={key:records for key,records in panels.items() if len(records)>=3}
    actual_sites=sum(len(x) for x in v29_panels.values())
    safe={}
    named_parent_drop=0
    ambiguous_parent_panels=0
    for key,records in v29_panels.items():
        same=[(r,s) for r,s in records if normalize_name(r["original_site_name"])==normalize_name(r["master"])]
        if same and len(records)>1:
            ambiguous_parent_panels+=1
            named_parent_drop+=len(same)
            records=[(r,s) for r,s in records if normalize_name(r["original_site_name"])!=normalize_name(r["master"])]
        if len(records)>=3:
            safe[key]=records
    network={(k[1],k[2]) for k in safe}
    spec={k[0] for k in safe}
    units={k[3] for k in safe}
    qa={
       "source_unique_metadata_valid_site_species_records":len(unique),
       "source_duplicate_identity_key_groups":dup,
       "v29_three_component_candidate_parent_panels_before_parent_overlap_guard":len(v29_panels),
       "v29_candidate_parent_component_source_rows":actual_sites,
       "parent_named_component_rows_conservatively_excluded":named_parent_drop,
       "parent_panels_with_ambiguous_parent_named_child":ambiguous_parent_panels,
       "source_panels_remaining_with_ge3_unique_child_site_IDs":len(safe),
       "source_distinct_seabird_species_after_parent_guard":len(spec),
       "source_distinct_country_master_site_networks_after_parent_guard":len(network),
       "source_distinct_count_units_after_parent_guard":len(units),
       "pre_count_structural_gate_pass":(
          len(safe)>=MIN_STRUCT_PANELS and len(spec)>=MIN_STRUCT_SPECIES
          and len(network)>=MIN_STRUCT_MASTERS and len(units)>=MIN_STRUCT_UNITS),
       "original_census_abundance_magnitudes_opened_during_structure":0
    }
    return safe,qa

def exact_count(value):
    """Only called once frozen structural minimum is passed."""
    raw=str(value or "").strip()
    if not raw:return None
    try:
        d=Decimal(raw)
    except InvalidOperation:
        return None
    if not d.is_finite() or d<0 or d>MAX_ORIGINAL_COUNT or d!=d.to_integral_value():
        return None
    return int(d)

def component_effect(counts_old,counts_new,source_y0,source_y1):
    if len(counts_old)<3 or len(counts_old)!=len(counts_new):
        raise ValueError("PANELS_STOP original paired components must match")
    n0=sum(counts_old);n1=sum(counts_new)
    if n0<2 or n1<2:return None
    p0=[n/n0 for n in counts_old]
    p1=[n/n1 for n in counts_new]
    q0=sum(x*x for x in p0)
    q1=sum(x*x for x in p1)
    expected=q0+(1-q0)/n1
    tv=.5*sum(abs(x-y) for x,y in zip(p0,p1))
    y0=float(mean(source_y0)); y1=float(mean(source_y1))
    if y1<=y0:raise ValueError("SOURCE_STOP expected census epoch order")
    return {
       "early_total":n0,"recent_total":n1,"declined":bool(n1<n0),
       "early_simpson":q0,"recent_simpson":q1,
       "late_null_expected_simpson":expected,
       "finite_count_corrected_excess_concentration":q1-expected,
       "effective_components_early":1/q0,
       "effective_components_recent":1/q1,
       "effective_components_ratio_recent_over_early":q0/q1,
       "site_share_total_variation":tv,
       "mean_original_year_difference":y1-y0,
       "annualized_log_total_count_change":(math.log(n1)-math.log(n0))/(y1-y0),
    }

def evaluate(safe):
    """All parent panels are opened, not chosen by observed decline outcomes."""
    outcomes=[]
    reasons=Counter()
    for key,records in sorted(safe.items()):
        c0=[];c1=[];y0=[];y1=[]
        invalid=False
        for info,source in records:
            a=exact_count(source.get("L"))
            b=exact_count(source.get("O"))
            if a is None or b is None:
                reasons["one_or_more_original_adjusted_counts_not_exact_integer"]+=1
                invalid=True
                break
            c0.append(a);c1.append(b);y0.append(info["year_2000"]);y1.append(info["year_recent"])
        if invalid:continue
        effect=component_effect(c0,c1,y0,y1)
        if effect is None:
            reasons["original_parent_one_epoch_total_less_than_two"]+=1
            continue
        outcomes.append({"species":key[0],"country":key[1],"master":key[2],
                         "count_unit":key[3],"source_child_site_count":len(records),
                         **effect})
    allsp={x["species"] for x in outcomes}
    allnet={(x["country"],x["master"]) for x in outcomes}
    allunits={x["count_unit"] for x in outcomes}
    declines=[o for o in outcomes if o["declined"]]
    decline_sp={x["species"] for x in declines}
    decline_net={(x["country"],x["master"]) for x in declines}
    ok=(len(outcomes)>=MIN_NUM_PANELS and len(allsp)>=MIN_NUM_SPECIES
        and len(allnet)>=MIN_NUM_MASTERS and len(allunits)>=MIN_NUM_UNITS
        and len(declines)>=MIN_DECLINE_PANELS and len(decline_sp)>=MIN_DECLINE_SPECIES
        and len(decline_net)>=MIN_DECLINE_MASTERS)
    support={
        "integer_complete_supported_panels":len(outcomes),
        "distinct_species_integer_panels":len(allsp),
        "distinct_country_master_networks_integer_panels":len(allnet),
        "integer_count_units":len(allunits),
        "declining_total_panels":len(declines),
        "declining_species":len(decline_sp),
        "declining_distinct_master_networks":len(decline_net),
        "growing_panels":sum(o["recent_total"]>o["early_total"] for o in outcomes),
        "no_change_total_panels":sum(o["recent_total"]==o["early_total"] for o in outcomes),
        "original_numeric_exclusion_reasons":dict(reasons),
        "frozen_numeric_and_decline_support_gate_pass":bool(ok)
    }
    if not ok:
        return {"status":"STOP_INSUFFICIENT_EXACT_INTEGER_OR_DECLINE_PANEL_SUPPORT",
                "effects_computed":False,"numeric_support":support}
    bysp=defaultdict(list)
    for r in declines:bysp[r["species"]].append(r)
    species_effects=[]
    for sp,rows in sorted(bysp.items()):
        if len(rows)<MIN_SPECIES_DECLINE_PANELS:continue
        d=[r["finite_count_corrected_excess_concentration"] for r in rows]
        species_effects.append({
          "species":sp,"declining_panels":len(rows),
          "mean_excess_concentration":mean(d),
          "median_excess_concentration":median(d),
          "panels_with_positive_excess_concentration":sum(x>0 for x in d),
          "panels_with_negative_excess_concentration":sum(x<0 for x in d),
          "mean_site_share_turnover":mean(r["site_share_total_variation"] for r in rows)
        })
    support["eligible_species_with_at_least_3_decline_panels"]=len(species_effects)
    if len(species_effects)<MIN_DECLINE_SPECIES:
        return {"status":"STOP_FEWER_THAN_SIX_INDEPENDENT_SPECIES_WITH_THREE_DECLINE_PANELS",
                "effects_computed":False,"numeric_support":support}
    e=[r["mean_excess_concentration"] for r in species_effects]
    positive_sp=sum(x>0 for x in e)
    d=[r["finite_count_corrected_excess_concentration"] for r in declines]
    by_country=defaultdict(list)
    for row in declines:by_country[row["country"]].append(row)
    def equal_species(rows):
        group=defaultdict(list)
        for r in rows:group[r["species"]].append(r["finite_count_corrected_excess_concentration"])
        return mean(mean(x) for x in group.values()) if group else None
    leave_country={c:equal_species([r for r in declines if r["country"]!=c])
                   for c in sorted(by_country)}
    summary={
        "source_response":"same-original-Site.ID two-census adjusted count units",
        "num_analysed_species":len(species_effects),
        "num_integer_parent_panels":len(outcomes),
        "num_total_declining_panels":len(declines),
        "num_species_distinct_source_masters":len({(r["country"],r["master"]) for r in declines}),
        "species_equal_mean_finite_count_corrected_simpson_excess":mean(e),
        "median_declining_panel_finite_count_corrected_excess":median(d),
        "fraction_declining_panels_with_positive_excess":sum(x>0 for x in d)/len(d),
        "positive_species_mean_count":positive_sp,
        "fraction_species_mean_positive":positive_sp/len(e),
        "a_priori_directional_descriptive_support":bool(
             mean(e)>0 and positive_sp>=math.ceil(2*len(e)/3)),
        "median_declining_panel_site_share_total_variation":median(
            r["site_share_total_variation"] for r in declines),
        "fraction_declining_panels_with_turnover_ge25pct_but_no_excess_concentration":sum(
            r["site_share_total_variation"]>=TV_HIGH and
            r["finite_count_corrected_excess_concentration"]<=0 for r in declines)/len(declines),
        "country_panel_counts":{k:len(v) for k,v in sorted(by_country.items())},
        "equal_species_mean_excess_leave_one_country_out":leave_country,
        "each_species_summary":species_effects,
        "proportional_benchmark_is_not_measurement_error_or_causal_survival_model":True,
        "original_site_crosswalk_and_physical_island_identity_unverified":True,
        "source_mainland_of_Antarctica_independent_comparison":False,
        "no_biological_p_value":True,
    }
    return {
        "status":"JNCC_COMPARATIVE_SOURCE_TWO_CENSUS_BREEDING_COMPONENT_COMPOSITION",
        "effects_computed":True,
        "numeric_support":support,
        "main_ecological_description":summary,
        "scientific_decision":("EXPLORATORY_CROSS_SEABIRD_CONCENTRATION_BEYOND_PROPORTIONAL_ALLOCATION"
            if summary["a_priori_directional_descriptive_support"] else
            "NO_CROSS_SEABIRD_CONCENTRATION_DIRECTIONAL_GENERALITY")
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args()
    receipt={"status":"HOLD_PUBLISHER_SOURCE","effects_computed":False}
    try:
        raw,sourceinfo=v28.download_original()
        if sourceinfo["original_sha256"]!=SHA:
            raise ValueError("SOURCE_STOP original July2024 JNCC source changed")
        allrows=list(v29.original_rows(raw))
        historic=v29.coverage(allrows)
        if historic["unique_original_two_census_site_species_rows_after_literal_QA"]!=14112:
            raise ValueError("SOURCE_STOP original V29 paired source size differs")
        if historic["qualified_species_country_master_unit_panels_with_ge3_sites"]!=1485:
            raise ValueError("SOURCE_STOP original V29 panel count changed")
        if not historic["frozen_eligibility_gate_pass"]:
            raise ValueError("SOURCE_STOP V29 pre-outcome support lost")
        safe,qa=extract_structural(allrows)
        receipt={
            "status":"JNCC_V30_FROZEN_SITE_PANEL_STRUCTURAL_SUPPORT",
            "source_publisher_SHA256":SHA,
            "source_original_three_sheet_count":4,
            "frozen_contract":"contracts/JNCC_COMPONENT_CONCENTRATION_V30.md",
            "reproduced_original_V29_panels":historic["qualified_species_country_master_unit_panels_with_ge3_sites"],
            "pre_count_structural_support":qa,
            "effects_computed":False,
            "scientific_decision":("STOP_PARENT_OVERLAP_SOURCE_SUPPORT"
                                   if not qa["pre_count_structural_gate_pass"]
                                   else "PENDING_COMPLETE_INTEGER_AND_DECLINE_GATE")
        }
        if qa["pre_count_structural_gate_pass"]:
            r=evaluate(safe)
            receipt["actual_two_census_composition"]=r
            receipt["effects_computed"]=r["effects_computed"]
            receipt["scientific_decision"]=r.get("scientific_decision",r["status"])
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:800]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_PUBLISHER_SOURCE":raise SystemExit(2)

if __name__=="__main__":main()
