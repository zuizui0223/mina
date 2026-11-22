#!/usr/bin/env python3
"""Leave-one-source-region/block/largest-site influence for source-matched
three-species CMIP6 physical exposure.

No species physiological effect is inferred. A within-common-site mean near
zero is not proof that all site-specific nest weights respond the same way to
warming. These are deterministic deletion diagnostics, NOT confidence intervals.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from derive_species_geographic_exposure_decomposition import MAIN,mean
from source_match_species_shared_site_exposure import (
    PAIRS,read_fixed,direct_cocensuses,pair_sites
)

STAGES=("same_site_original_medians","same_site_sameyear_samemethod_medians")
SCREEN=(False,True)
def weighted_diff(frame):
    if len(frame)<3 or frame.weight_a.sum()<=0 or frame.weight_b.sum()<=0:
        return None
    return float(mean(frame.sic_delta_pp,frame.weight_b)-
                 mean(frame.sic_delta_pp,frame.weight_a))

def range_result(values):
    v=[float(x) for x in values if x is not None and np.isfinite(x)]
    return dict(n_valid=len(v),min=float(min(v)) if v else None,
                max=float(max(v)) if v else None,
                negative=sum(x<0 for x in v),
                positive=sum(x>0 for x in v),
                exact_zero=sum(x==0 for x in v))

def run(counts,species,obs,ice,inventory):
    obs=obs.merge(inventory[["site_id","polar_250km_fixed_grid_block"]],
                  on="site_id",validate="one_to_one")
    annual=direct_cocensuses(counts,species)
    sel=ice[
        ice.experiment_id.eq(MAIN[0]) & ice.period.eq(MAIN[1]) &
        ice.source_id.eq("three_model_equal_mean")
    ][["site_id","sic_delta_pp"]]
    assert len(sel)==595 and sel.site_id.is_unique
    out=[];summary=[]
    for a,b in PAIRS:
        for stage in STAGES:
            baseline=(pair_sites(species,a,b) if stage=="same_site_original_medians"
                      else annual[(a,b)]["sites"].copy())
            z=baseline.merge(obs[["site_id","source_region","polar_250km_fixed_grid_block","all_model_marine50"]],
                             on="site_id",validate="one_to_one").merge(
                             sel,on="site_id",validate="one_to_one")
            for filtered in SCREEN:
                q=(z[z.all_model_marine50] if filtered else z).copy()
                assert q.site_id.is_unique
                base=weighted_diff(q)
                assert base is not None, (a,b,stage,filtered,len(q))
                ref_sums={"species_a_baseline_proxy":float(q.weight_a.sum()),
                          "species_b_baseline_proxy":float(q.weight_b.sum())}
                diag={}
                for grouping,column in (("reporting_region","source_region"),
                                        ("polar_250km_block","polar_250km_fixed_grid_block")):
                    levels=sorted(q[column].unique())
                    removed=[]
                    for key in levels:
                        rem=q.loc[q[column].ne(key)]
                        new=weighted_diff(rem)
                        out.append({
                            "species_a":a,"species_b":b,"matched_support":stage,
                            "marine50":filtered,"removed_type":grouping,
                            "removed_id":str(key),"n_original_sites":len(q),
                            "n_remaining_sites":len(rem),
                            "full_physical_sic_gap_b_minus_a":base,
                            "remaining_gap_b_minus_a":new,
                            "gap_shift_after_deletion":new-base if new is not None else None,
                            **ref_sums
                        })
                        removed.append(new)
                    diag[grouping]=range_result(removed)
                    diag[grouping]["number_deletions"]=len(levels)
                # Single largest combined recorded site. This is an influence
                # sensitivity, not evidence of vital-rate mechanisms.
                largest=q.assign(combined_original_nests_proxy=q.weight_a+q.weight_b)
                largest=largest.sort_values(
                    ["combined_original_nests_proxy","site_id"],ascending=[False,True]).iloc[0]
                rem=q.loc[q.site_id.ne(largest.site_id)]
                deleted=weighted_diff(rem)
                out.append({
                    "species_a":a,"species_b":b,"matched_support":stage,
                    "marine50":filtered,"removed_type":"largest_combined_nest_proxy_site",
                    "removed_id":str(largest.site_id),"n_original_sites":len(q),
                    "n_remaining_sites":len(rem),
                    "full_physical_sic_gap_b_minus_a":base,
                    "remaining_gap_b_minus_a":deleted,
                    "gap_shift_after_deletion":deleted-base if deleted is not None else None,
                    **ref_sums
                })
                summary.append({
                    "species_pair":a+"__"+b,"matched_support":stage,
                    "marine50":filtered,"n_matched_site_ids":len(q),
                    "n_original_source_regions":q.source_region.nunique(),
                    "n_original_polar250_blocks":q.polar_250km_fixed_grid_block.nunique(),
                    "full_gap_b_minus_a_pp":base,
                    "after_largest_combined_nest_site":deleted,
                    "largest_source_site_id":str(largest.site_id),
                    "largest_site_species_a_weight_share":float(largest.weight_a/q.weight_a.sum()),
                    "largest_site_species_b_weight_share":float(largest.weight_b/q.weight_b.sum()),
                    "delete_one_reporting_region":diag["reporting_region"],
                    "delete_one_original_250km_block":diag["polar_250km_block"]
                })
    assert len(summary)==12
    ret={
      "status":"PASS_ORIGINAL_COMMON_SITE_REGIONAL_AND_250KM_INFLUENCE_PHYSICAL_ONLY",
      "scenario":"SSP5-8.5_2081-2100, original 3-model mean SIC delta",
      "source_595_sites":595,"original_counted_sites":271,
      "n_comparisons":len(summary),"source_region_or_block_influence_rows":len(out),
      "no_inferential_p_or_population_confidence_interval":True,
      "no_biological_response_or_future_nests":True,
      "main_results":summary,
      "interpretation":"Conditioned on the observed matched-site source roster; no additional independent population sample."
    }
    return pd.DataFrame(out),ret

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--counts",required=True,type=Path)
    p.add_argument("--inventory",required=True,type=Path)
    p.add_argument("--cmip6-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    counts,species,obs,ice=read_fixed(a.counts,a.inventory,a.cmip6_zip)
    inventory=pd.read_csv(a.inventory)
    table,receipt=run(counts,species,obs,ice,inventory)
    table.to_csv(a.out/"matched_site_species_region_block_influence.csv",index=False)
    receipt["source_sha256"]={
        key:hashlib.sha256(path.read_bytes()).hexdigest()
        for key,path in (("count",a.counts),("inventory",a.inventory),("physical",a.cmip6_zip))
    }
    (a.out/"matched_site_species_influence_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n"
    )
    print("SOURCE_MATCHED_SITE_INFLUENCE="+json.dumps(
        {"status":receipt["status"],"main_results":receipt["main_results"]},ensure_ascii=False),
        flush=True)
if __name__=="__main__":main()
