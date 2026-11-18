#!/usr/bin/env python3
"""One post-result provenance sensitivity: 357 site-year pairs vs the 277 subset
that shares a MAPPPD publisher citekey and original census vantage.

No new environmental predictors, ice windows, population outcomes, imputed
species absences, SDM families, ecological p-value searches or future forecasts.
This is a correction of how 'same-year co-census' was described in the paper.
"""
from __future__ import annotations
import argparse,csv,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

PAIRS=("ADPE__GEPE","ADPE__CHPE","CHPE__GEPE")
EXPECTED={"ADPE__GEPE":(100,88),
          "ADPE__CHPE":(89,57),
          "CHPE__GEPE":(168,132)}
SEED=20261110
REPS=2000

def read(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def write(path,rows):
    if not rows:raise ValueError("Empty source sensitivity")
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
def correlation(x,y):
    if len(x)<4:return None
    a=np.asarray(x,dtype=float);b=np.asarray(y,dtype=float)
    if len(a)!=len(b) or min(np.std(a),np.std(b))<1e-12:return None
    return float(np.corrcoef(a,b)[0,1])
def regional_site_r(sites):
    x=np.array([z["mean_SIC"] for z in sites],dtype=float)
    y=np.array([z["mean_log_ratio"] for z in sites],dtype=float)
    group=defaultdict(list)
    for i,z in enumerate(sites):group[z["source_region"]].append(i)
    for ind in group.values():
        x[ind]-=x[ind].mean();y[ind]-=y[ind].mean()
    return correlation(x,y)
def spatial_bootstrap(sites,index):
    blocks=sorted({z["polar_250km_block"] for z in sites})
    if len(blocks)<5:
        return {"status":"UNDERPOWERED_ORIGINAL_BLOCKS","original_blocks":len(blocks),
                "valid":0,"percentile_interval":None}
    rng=np.random.default_rng(SEED+index)
    by=defaultdict(list)
    for z in sites:by[z["polar_250km_block"]].append(z)
    vals=[]
    for i in range(REPS):
        selected=rng.choice(blocks,size=len(blocks),replace=True)
        arr=[z for k in selected for z in by[k]]
        r=regional_site_r(arr)
        if r is not None and np.isfinite(r):vals.append(r)
    if len(vals)<.75*REPS:
        return {"status":"REGIONAL_EVIDENCE_UNDERPOWERED",
                "original_blocks":len(blocks),"valid":len(vals),
                "percentile_interval":None}
    return {"status":"DESCRIPTIVE_BLOCK_SENSITIVITY_ONLY",
            "original_blocks":len(blocks),"valid":len(vals),
            "percentile_interval":[float(np.quantile(vals,.025)),
                                   float(np.quantile(vals,.975))]}
def site_aggregate(rows):
    group=defaultdict(list)
    for z in rows:group[z["site_id"]].append(z)
    out=[]
    for sid,rr in sorted(group.items()):
        regs={z["source_region"] for z in rr}
        blocks={z["polar_250km_block"] for z in rr}
        if len(regs)!=1 or len(blocks)!=1:
            raise ValueError("Original source site regions/blocks disagree")
        out.append({"site_id":sid,"source_region":rr[0]["source_region"],
                    "polar_250km_block":rr[0]["polar_250km_block"],
                    "n_actual_same_citation_siteyears":len(rr),
                    "mean_SIC":float(np.mean([float(z["same_year_AugNov_original_SIC_pct"]) for z in rr])),
                    "mean_log_ratio":float(np.mean([float(z["log1p_first_minus_log1p_second"]) for z in rr]))})
    return out
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-cocensus",type=Path,required=True)
    p.add_argument("--original-publisher-qa",type=Path,required=True)
    p.add_argument("--original-publisher-qa-json",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    original=read(args.original_cocensus)
    checks=read(args.original_publisher_qa)
    receipt=json.loads(args.original_publisher_qa_json.read_text(encoding="utf-8"))
    if receipt["status"]!="PUBLISHER_ORIGINAL_NESTS_FILTER_AND_PAIR_SOURCE_COMPATIBILITY_AUDITED":
        raise ValueError("Unverified original publisher citation audit")
    if len(original)!=357 or len(checks)!=357:
        raise ValueError("Original 357 site-season pair source is not complete")
    q={(z["species_pair"],z["source_site_id"],int(z["breeding_season"])):z for z in checks}
    if len(q)!=357:raise ValueError("Publisher has duplicate species-pair source QA")
    relevant=[]
    missing=[]
    for z in original:
        key=(z["species_pair"],z["site_id"],int(z["census_season"]))
        c=q.get(key)
        if c is None:raise ValueError("Original publisher source QA join failed")
        if c["both_species_match_original_MAPPPD5_published_count_method"]!="True":
            raise ValueError("Missing original publisher count/method match for one of 357")
        strict=(c["strict_shared_publisher_source_and_method"]=="True")
        if strict:
            relevant.append(z)
        else:
            missing.append({"species_pair":z["species_pair"],
                "site_id":z["site_id"],"census_season":z["census_season"],
                "source_region":z["source_region"],
                "same_recorded_method":c["same_recorded_method"],
                "both_original_citekeys_known":c["both_original_source_citekeys_nonempty"],
                "same_original_source_citation":c["same_nonempty_original_publication_citekey"],
                "reason":"PUBLISHER_SOURCE_OR_METHOD_NOT_CERTIFIED"})
    if len(relevant)!=277 or len(missing)!=80:
        raise ValueError("Strict original same-citation+vantage source support changed")
    details={}
    all_site_rows=[]
    for i,pair in enumerate(PAIRS):
        r=[z for z in original if z["species_pair"]==pair]
        strict=[z for z in relevant if z["species_pair"]==pair]
        if (len(r),len(strict))!=EXPECTED[pair]:
            raise ValueError("One fixed original pair source status changed")
        allsites=site_aggregate(r)
        subsets=site_aggregate(strict)
        for z in subsets:all_site_rows.append({"species_pair":pair,**z})
        raw_pool=correlation([float(z["same_year_AugNov_original_SIC_pct"]) for z in strict],
                            [float(z["log1p_first_minus_log1p_second"]) for z in strict])
        desc={
           "n_original_same_site_season_pairs":len(r),
           "n_strict_same_source_vantage_pairs":len(strict),
           "n_excluded_without_proven_same_source_vantage":len(r)-len(strict),
           "n_all_original_colony_sites":len(allsites),
           "n_strict_original_colony_sites":len(subsets),
           "n_strict_regions":len({z["source_region"] for z in subsets}),
           "n_strict_250km_blocks":len({z["polar_250km_block"] for z in subsets}),
           "original_pooled_siteyear_r":correlation(
              [float(z["same_year_AugNov_original_SIC_pct"]) for z in r],
              [float(z["log1p_first_minus_log1p_second"]) for z in r]),
           "strict_pooled_siteyear_r_pseudoreplication_warning":raw_pool,
           "original_site_equal_geographic_r":correlation(
              [z["mean_SIC"] for z in allsites],[z["mean_log_ratio"] for z in allsites]),
           "strict_site_equal_geographic_r":correlation(
              [z["mean_SIC"] for z in subsets],[z["mean_log_ratio"] for z in subsets]),
           "original_region_demeaned_site_equal_r":regional_site_r(allsites),
           "strict_region_demeaned_site_equal_r":regional_site_r(subsets),
           "strict_250km_block_interval":spatial_bootstrap(subsets,i),
           "no_same_field_calendar_day_confirmed":True
        }
        details[pair]=desc
    result={
       "status":"POST_RESULT_STRICT_ORIGINAL_CITATION_AND_VANTAGE_MACRO_SENSITIVITY_COMPLETE",
       "publisher_sha256":receipt["publisher_2026_v5_original"]["publisher_source_sha256"],
       "all_original_known_nest_count_same_site_season_pair_comparisons":len(original),
       "strict_shared_source_vantage_pairs":len(relevant),
       "strict_source_site_equal_geographic_observations":len(all_site_rows),
       "excluded_other_source_or_method_pairs":len(missing),
       "fixed_all_three_species_pairs":details,
       "limits":[
          "Stricter survey-source-vantage matching is a post-hoc measurement-validity correction, NOT an independent replication and not a new confirmatory hypothesis.",
          "No exact field census day or comparable effort is verified even if publisher citekey matches.",
          "Raw co-census correlations pool repeated colony-years and are not site-independent inference.",
          "Source cohort is geographically Antarctic-Peninsula concentrated, not all 595 observed sites.",
          "Static 2017–2023 land cover does not enter this 1991–2020 same-year observed count/sea-ice comparison.",
          "No new model terms, p-value ranking, future breeding forecast or causal competition inference."
       ]}
    write(args.out/"strict_original_same_citation_vantage_277_pair_siteyears.csv",relevant)
    write(args.out/"strict_original_same_citation_vantage_site_means.csv",all_site_rows)
    write(args.out/"original_80_pair_source_provenance_exclusions.csv",missing)
    (args.out/"strict_original_357to277_species_niche_sensitivity.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("ORIGINAL_SAME_SOURCE_277_NICHE_SENSITIVITY="+json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
