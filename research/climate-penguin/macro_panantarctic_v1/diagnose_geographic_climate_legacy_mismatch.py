#!/usr/bin/env python3
"""Post-result regional decomposition and within-longitude-sector marine mismatch.

Consumes ONLY the immutable prior 3-decade colony/ice and 60%-front artifacts.
No climate lag/threshold/model selection. Descriptive original-source QA.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

SPECIES=("ADPE","CHPE","GEPE")
PERIODS=("1991-2000","2001-2010","2011-2020")
PAIRS=((0,1),(1,2))
COMPARE={
    "earlier_sic_vs_recent_nests":("delta_ice_pp_earlier","delta_nest_log_recent"),
    "concurrent_sic_vs_recent_nests":("delta_ice_pp_concurrent","delta_nest_log_recent"),
    "future_sic_vs_past_nests_negative_time":("delta_ice_pp_concurrent","delta_nest_log_early")
}
EXPECTED={
    "ADPE": (19,0.4803175300480694,0.2703623581918029,-0.21456774275552992),
    "CHPE": (12,-0.1415247928245524,0.2536608034012301,-0.2023355957595482),
    "GEPE": (12,0.008327843597395657,0.15167160675023483,-0.04874485886824525)
}
KM_LAT=111.195

def load(path):
    with path.open(encoding="utf-8",newline="") as stream:
        return list(csv.DictReader(stream))

def save(path,rows):
    if not rows:
        path.write_text("no_supported_rows\n",encoding="utf-8")
        return
    cols=list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w",encoding="utf-8",newline="") as stream:
        w=csv.DictWriter(stream,fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

def pooled_region_center(rows,x,y):
    groups=defaultdict(list)
    for row in rows:groups[row["source_region"]].append(row)
    vx=vy=num=0.0
    contrib={}
    for region,items in sorted(groups.items()):
        if len(items)<2:continue
        a=[float(r[x]) for r in items];b=[float(r[y]) for r in items]
        da=[v-mean(a) for v in a];db=[v-mean(b) for v in b]
        summ=sum(v*w for v,w in zip(da,db))
        va=sum(v*v for v in da)
        vb=sum(v*v for v in db)
        num+=summ;vx+=va;vy+=vb
        contrib[region]={"n_sites":len(items),"source_250km_blocks":len({q["polar_250km_block"] for q in items}),
            "signed_covariance_numerator":summ,"x_residual_SS":va,"y_residual_SS":vb}
    if vx<=1e-12 or vy<=1e-12 or sum(z["n_sites"] for z in contrib.values())<5:
        corr=None
    else:
        corr=num/math.sqrt(vx*vy)
    return {"r":corr,"numerator":num,"variance_x_sum":vx,"variance_y_sum":vy,
            "n_informative_sites":sum(z["n_sites"] for z in contrib.values()),
            "n_informative_regions":len(contrib),"contributions":contrib}

def raw_region_associations(rows,species,comparison,x,y,grand_numerator):
    grouped=defaultdict(list)
    for row in rows:grouped[row["source_region"]].append(row)
    records=[]
    for reg,group in sorted(grouped.items()):
        n=len(group)
        result={"species":species,"comparison":comparison,"region":reg,
                "n_original_sites":n,"n_spatial_blocks":len({r["polar_250km_block"] for r in group}),
                "no_singleton_as_region_replication":True}
        if n==1:
            result["support"]="ONE_SITE_CANNOT_ESTIMATE_REGION_RELATION"
            records.append(result);continue
        a=[float(r[x]) for r in group];b=[float(r[y]) for r in group]
        da=[v-mean(a) for v in a];db=[v-mean(b) for v in b]
        num=sum(z*w for z,w in zip(da,db))
        ssx=sum(z*z for z in da);ssy=sum(z*z for z in db)
        result["signed_covariance_numerator"]=num
        result["numerator_share_of_pooled"]=num/grand_numerator if abs(grand_numerator)>1e-12 else None
        if ssx>1e-12:
            result["linear_log1p_nest_change_per_positive_10pp_SIC_change"]=10*num/ssx
        if n==2:
            result["support"]="TWO_SITES_PAIR_DIRECTION_ONLY_NO_REGION_CORRELATION"
            result["signed_pair_covariance_direction"]=("positive" if num>1e-12 else "negative" if num<-1e-12 else "indeterminate")
        elif ssx<1e-12 or ssy<1e-12:
            result["support"]="NO_WITHIN_REGION_SOURCE_VARIANCE"
        else:
            result["support"]="REGION_EXPLORATORY_EQUAL_SITE_ASSOCIATION"
            result["within_region_r"]=num/math.sqrt(ssx*ssy)
        records.append(result)
    return records

def assess_lag_geography(rows,species):
    computed={};region_rows=[]
    expected=EXPECTED[species]
    if len(rows)!=expected[0]:
        raise ValueError(f"Frozen {species} triplet site support changed: {len(rows)} != {expected[0]}")
    for idx,(name,(x,y)) in enumerate(COMPARE.items()):
        d=pooled_region_center(rows,x,y)
        if d["r"] is None or abs(d["r"]-expected[idx+1])>1e-10:
            raise ValueError(f"{species} {name} original region-demeaned r mismatch")
        region_rows.extend(raw_region_associations(rows,species,name,x,y,d["numerator"]))
        all_regions=sorted({q["source_region"] for q in rows})
        loo=[]
        for region in all_regions:
            remaining=[q for q in rows if q["source_region"]!=region]
            rec=pooled_region_center(remaining,x,y)
            loo.append({"excluded_region":region,"n_informative_sites":rec["n_informative_sites"],
                        "n_informative_regions":rec["n_informative_regions"],"r":rec["r"]})
        computed[name]={
            "pooled_region_demeaned_r":d["r"],"pooled_region_demeaned_covariance_numerator":d["numerator"],
            "n_informative_sites":d["n_informative_sites"],"n_informative_regions":d["n_informative_regions"],
            "region_covariance_components":d["contributions"],"leave_region_out":loo
        }
    earlier=computed["earlier_sic_vs_recent_nests"]
    loo=[z["r"] for z in earlier["leave_region_out"] if z["r"] is not None]
    stable_sign=bool(loo) and all(z>0 for z in loo) if earlier["pooled_region_demeaned_r"]>0 else bool(loo) and all(z<0 for z in loo)
    strong_regions=sum(1 for z in region_rows if z["comparison"]=="earlier_sic_vs_recent_nests"
                       and z["n_original_sites"]>=3 and z.get("support")=="REGION_EXPLORATORY_EQUAL_SITE_ASSOCIATION")
    blocks=len({q["polar_250km_block"] for q in rows})
    transferable=stable_sign and strong_regions>=3 and blocks>=5
    return {
        "species":species,"n_original_sites_all_three_decades":len(rows),
        "n_original_regions":len({q["source_region"] for q in rows}),
        "n_region_groups_with_3plus_informative_sites":strong_regions,
        "n_spatial_250km_blocks":blocks,
        "earlier_sic_direction_unchanged_across_every_region_omission":stable_sign,
        "geographically_transferable_lag_signature_eligible":bool(transferable),
        "decision":"REGIONALLY_REPLICATED_LAG_CANDIDATE_ONLY_NOT_CAUSAL" if transferable
                   else "GEOGRAPHY_UNSTABLE_OR_UNDERPOWERED_NO_LAG_CLAIM",
        "comparisons":computed
    },region_rows

def sector_mismatch(rows,fronts,species):
    lookup={
        (p["start_period"],p["end_period"],p["climate_month_basis"],int(p["longitude_sector_10deg"])):p
        for p in fronts if p["status"]=="PAIRED_ORIGINAL_MARINE_FRONT"
    }
    results=[];summaries=[]
    for i,j in PAIRS:
        key=(PERIODS[i],PERIODS[j])
        for basis in ("aug_nov","september"):
            bysector=defaultdict(list)
            for r in rows:bysector[int(r["longitude_sector_10deg"])].append(r)
            for sector,group in sorted(bysector.items()):
                lookupkey=(key[0],key[1],basis,sector)
                edge=lookup.get(lookupkey)
                record={"species":species,"period_start":key[0],"period_end":key[1],
                    "basis":basis,"sector":sector,"longitude_west":sector*10-180,
                    "longitude_east":sector*10-170,"n_original_sites":len(group),
                    "n_source_regions":len({r["source_region"] for r in group}),
                    "n_original_250km_blocks":len({r["polar_250km_block"] for r in group}),
                    "direction_agreement_not_a_climate_debt_test":True}
                if edge is None:
                    record["support"]="NO_VALID_ORIGINAL_MARINE_60PCT_FRONT"
                    results.append(record);continue
                physical=float(edge["southward_positive_ice_edge_meridional_km"])
                record["marine_60pct_front_southward_km"]=physical
                n0=[float(r[f"median_original_nest_count_{i}"]) for r in group]
                n1=[float(r[f"median_original_nest_count_{j}"]) for r in group]
                if len(group)<2 or min(sum(n0),sum(n1))<=0:
                    record["support"]="FEWER_THAN_TWO_SITES_OR_ZERO_TOTAL_WEIGHTS"
                    results.append(record);continue
                c0=sum(v*float(r["latitude"]) for r,v in zip(group,n0))/sum(n0)
                c1=sum(v*float(r["latitude"]) for r,v in zip(group,n1))/sum(n1)
                biological=KM_LAT*(c0-c1)
                record["within_sector_nest_weighted_southward_km"]=biological
                record["biophysical_arithmetic_difference_km_not_debt"]=biological-physical
                if abs(physical)<1 or abs(biological)<1:
                    record["direction"]="INDETERMINATE_WITHIN_1KM"
                else:
                    record["direction"]="SAME_SIGN" if physical*biological>0 else "OPPOSITE_SIGN"
                record["support"]="SUPPORTED_TWO_PLUS_OBSERVED_SITES_DESCRIPTIVE_ONLY"
                results.append(record)
            supported=[r for r in results if r["species"]==species
                and r["period_start"]==key[0] and r["period_end"]==key[1]
                and r["basis"]==basis and r["support"]=="SUPPORTED_TWO_PLUS_OBSERVED_SITES_DESCRIPTIVE_ONLY"]
            direct=[r for r in supported if r["direction"] in ("SAME_SIGN","OPPOSITE_SIGN")]
            summaries.append({
                "species":species,"period_start":key[0],"period_end":key[1],"basis":basis,
                "source_sector_count":len(bysector),
                "sectors_with_2plus_census_sites_and_physical_front":len(supported),
                "sectors_with_nontrivial_direction_in_both_axes":len(direct),
                "same_sign":sum(r["direction"]=="SAME_SIGN" for r in direct),
                "opposite_sign":sum(r["direction"]=="OPPOSITE_SIGN" for r in direct),
                "distinct_supported_original_regions":len({r["source_region"] for r in rows
                     if int(r["longitude_sector_10deg"]) in {z["sector"] for z in supported}}),
                "sector_level_macro_replication": "SUPPORTED_DESCRIPTIVE_SECTOR_PATTERN_ONLY"
                   if len(direct)>=5 and len({r["source_region"] for r in rows
                     if int(r["longitude_sector_10deg"]) in {z["sector"] for z in direct}})>=3
                   else "NO_MACRO_SECTOR_REPLICATION",
                "not_an_independent_climate_tracking_or_lag_result":True
            })
    return results,summaries

def exact_sector_nesting_partition(rows, species):
    """Exact symmetric shift decomposition, fixed source sectors and counts."""
    result=[];components=[]
    for early,late in PAIRS:
        all_n0=[float(r[f"median_original_nest_count_{early}"]) for r in rows]
        all_n1=[float(r[f"median_original_nest_count_{late}"]) for r in rows]
        n0=sum(all_n0);n1=sum(all_n1)
        record={"species":species,"period_start":PERIODS[early],
                "period_end":PERIODS[late],"n_original_sites":len(rows),
                "n_original_sectors":len({r["longitude_sector_10deg"] for r in rows})}
        if min(n0,n1)<=0 or len(rows)<2:
            record["status"]="SOURCE_ZERO_COUNTS_OR_TOO_FEW_SITES"
            result.append(record)
            continue
        w0=[v/n0 for v in all_n0];w1=[v/n1 for v in all_n1]
        lat=[float(r["latitude"]) for r in rows]
        total=KM_LAT*(sum(w*ll for w,ll in zip(w0,lat))-
                      sum(w*ll for w,ll in zip(w1,lat)))
        sect=defaultdict(list)
        for idx,site in enumerate(rows):sect[int(site["longitude_sector_10deg"])].append(idx)
        between=within=0.0;ok=True
        for sec,indices in sorted(sect.items()):
            W0=sum(w0[i] for i in indices);W1=sum(w1[i] for i in indices)
            meta={"species":species,"period_start":PERIODS[early],
                  "period_end":PERIODS[late],"longitude_sector_10deg":sec,
                  "n_sites":len(indices),
                  "early_sampled_nest_share":W0,"late_sampled_nest_share":W1}
            if W0<=0 or W1<=0:
                meta["status"]="ZERO_WEIGHT_IN_SOURCE_SECTOR_ONE_PERIOD"
                ok=False;components.append(meta);continue
            c0=sum(w0[i]*lat[i] for i in indices)/W0
            c1=sum(w1[i]*lat[i] for i in indices)/W1
            between_contrib=-KM_LAT*(W1-W0)*(c0+c1)/2
            within_contrib=-KM_LAT*(W1+W0)*(c1-c0)/2
            meta.update({
               "status":"EXACT_SYMMETRIC_SOURCE_SECTOR_PARTITION",
               "sector_early_weighted_latitude_deg":c0,
               "sector_late_weighted_latitude_deg":c1,
               "between_sector_share_contribution_km":between_contrib,
               "within_sector_site_reweighting_contribution_km":within_contrib,
               "sum_sector_contribution_km":between_contrib+within_contrib
            })
            between+=between_contrib;within+=within_contrib
            components.append(meta)
        record["overall_original_roster_latitudinal_nest_reweighting_km"]=total
        if not ok:
            record["status"]="SOME_ORIGINAL_SECTORS_HAVE_ZERO_PERIOD_WEIGHT_PARTITION_UNIDENTIFIED"
        else:
            if not math.isclose(between+within,total,abs_tol=1e-8,rel_tol=1e-11):
                raise AssertionError(f"Exact original sector latitude partition failed {species} {early}->{late}")
            record.update({
              "status":"EXACT_SOURCE_SECTOR_WEIGHTED_LATITUDE_PARTITION",
              "between_sector_share_component_km":between,
              "within_sector_observed_site_component_km":within,
              "exact_identity_absolute_error_km":abs(between+within-total),
              "n_source_sectors_with_positive_two_period_weight":len(sect),
              "dominance_note":"Source nest-weighted latitude is not the true species range or individual dispersal"
            })
        result.append(record)
    return result,components


def run(args):
    source=load(args.roster);fronts=load(args.front)
    bysp=defaultdict(list)
    for r in source:
        bysp[r["species"]].append(r)
    allregion=[];allsector=[];all_sector_summaries=[];summ=[];all_sector_partition=[];all_partition_components=[]
    for species in SPECIES:
        regional,details=assess_lag_geography(bysp[species],species)
        sectors,sector_sum=sector_mismatch(bysp[species],fronts,species)
        partition,partition_parts=exact_sector_nesting_partition(bysp[species],species)
        all_sector_partition+=partition;all_partition_components+=partition_parts
        summ.append(regional);allregion+=details;allsector+=sectors;all_sector_summaries+=sector_sum
    response={
        "status":"ORIGINAL_REGION_AND_SECTOR_MISMATCH_DIAGNOSTIC_COMPLETED",
        "n_previous_original_colony_triplet_rows":len(source),
        "source_roster_id":"prior 42844104869 strict same original three decades",
        "source_front_id":"prior 42791019321 original 60pct 36-sector marine contour",
        "no_new_climate_source_or_lag_thresholds":True,
        "region_lag_replication_verdicts":summ,
        "marine_sector_support":all_sector_summaries,
        "original_sector_nested_latitude_partition":all_sector_partition,
        "inference_limit":[
            "Region-specific correlation in n=2 group is not a valid replicated effect.",
            "A region's covariance contribution is not a biological percentage attribution.",
            "Marine sector direction and colony-composition latitude direction refer to different phenomena.",
            "SIC 60 percent is a physical illustrative contour not a species' preferred ecological isopleth.",
            "No method here identifies true colony range edge, individual movements or a specific response lag.",
            "Same-block and sector observations share ocean climate, not independent climate experiments.",
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    save(args.out/"original_region_climate_legacy_contributions.csv",allregion)
    save(args.out/"original_60pct_sector_matched_colony_direction.csv",allsector)
    save(args.out/"original_60pct_sector_support_summary.csv",all_sector_summaries)
    save(args.out/"original_sector_weighted_latitude_partition.csv",all_sector_partition)
    save(args.out/"original_sector_latitude_partition_components.csv",all_partition_components)
    (args.out/"geographic_replication_and_mismatch_verdict.json").write_text(
        json.dumps(response,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("GEO_REGION_LEGACY="+json.dumps([{
        "species":r["species"],"decision":r["decision"],
        "informative_regions":r["n_region_groups_with_3plus_informative_sites"],
        "early_r":r["comparisons"]["earlier_sic_vs_recent_nests"]["pooled_region_demeaned_r"],
        "concurrent_r":r["comparisons"]["concurrent_sic_vs_recent_nests"]["pooled_region_demeaned_r"],
        "each_region_earlier_r":{reg:p["n_sites"] for reg,p in
            r["comparisons"]["earlier_sic_vs_recent_nests"]["region_covariance_components"].items()},
        "earlier_source_covariance":r["comparisons"]["earlier_sic_vs_recent_nests"]["region_covariance_components"],
        "region_delete":r["comparisons"]["earlier_sic_vs_recent_nests"]["leave_region_out"]
        } for r in summ],ensure_ascii=False),flush=True)
    print("GEO_SECTOR_MISMATCH="+json.dumps(all_sector_summaries,ensure_ascii=False),flush=True)
    print("GEO_SECTOR_MATCHED_DETAILS="+json.dumps(allsector,ensure_ascii=False),flush=True)
    print("GEO_SECTOR_NESTING_PARTITION="+json.dumps(all_sector_partition,ensure_ascii=False),flush=True)
    print("GEO_SECTOR_NESTING_COMPONENTS="+json.dumps(all_partition_components,ensure_ascii=False),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--roster",required=True,type=Path)
    ap.add_argument("--front",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    run(args)
if __name__=="__main__":
    main()
