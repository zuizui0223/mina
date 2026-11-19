#!/usr/bin/env python3
"""Post-result ASI island/continent source support audit, no new effect fitting.

Inputs are unchanged original ASI 827 site-season detection summaries, original
SCAR 196 site coordinates, and the already executed exploratory GLM receipt.
Compute source balance and block influence to bound interpretation. No new p.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

CONT="CONTINENT_LARGEST_LAND_POLYGON_PROXY"
OTHER="NONCONTINENTAL_LAND_POLYGON_PROXY"
SPECIES=("ADPE","CHPE","GEPE")
ORIG_SITES=82
ORIG_BLOCKS=6
ORIG_ROWS=1127
EXPLORATORY_RUN_ID=44513846995
GEO_RUN_ID=44512297362
ASI_RUN_ID=44511340025

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(panel_path:Path,geo_path:Path,model_path:Path)->dict:
    panel=pd.read_csv(panel_path)
    geo=pd.read_csv(geo_path)
    mod=json.loads(model_path.read_text(encoding="utf-8"))
    if len(panel)!=827 or panel.Code.nunique()!=196 or len(geo)!=196 or geo.Code.nunique()!=196:
        raise ValueError("original ASI panel/SCAR source count drift")
    if mod.get("source_site_codes")!=82 or mod.get("source_site_species_seasons")!=1127:
        raise ValueError("source original exploratory model receipt drift")
    groups=geo[geo.geography_group.isin([CONT,OTHER])].copy()
    blocks=groups.groupby(["spatial_block_100km","geography_group"]).Code.nunique().unstack(fill_value=0)
    if CONT not in blocks or OTHER not in blocks:
        raise ValueError("source land groups missing")
    common=sorted(blocks[(blocks[CONT]>0)&(blocks[OTHER]>0)].index.tolist())
    if len(common)!=ORIG_BLOCKS:
        raise ValueError(f"matched original spatial blocks drift: {common}")
    sel=groups[groups.spatial_block_100km.isin(common)].copy()
    if sel.Code.nunique()!=ORIG_SITES:
        raise ValueError("matched original site roster drift")
    long=panel.melt(
        id_vars=["Code","season_start","visit_count"],
        value_vars=list(SPECIES),var_name="species",value_name="state")
    long=long.merge(sel[["Code","geography_group","spatial_block_100km"]],
                    on="Code",how="inner",validate="many_to_one")
    long=long[long.state.ne("INCOMPLETE_OR_MISSING")].copy()
    if len(long)!=ORIG_ROWS:
        raise ValueError("fixed original site×species×season observation count drift")
    long["breeding_observed"]=long.state.eq("BREEDING_OBSERVED")
    block_table=[]
    for block in common:
        g=sel[sel.spatial_block_100km.eq(block)]
        e=long[long.spatial_block_100km.eq(block)]
        def counts(gr):
            q=g[g.geography_group.eq(gr)]
            r=e[e.geography_group.eq(gr)]
            return {
               "source_sites":int(q.Code.nunique()),
               "source_scar_polygon_features":int(q.SCAR_source_land_index.nunique()),
               "source_site_species_seasons":int(len(r)),
               "breeding_confirmed_site_species_seasons":int(r.breeding_observed.sum()),
               "raw_confirmation_fraction":round(float(r.breeding_observed.mean()),6) if len(r) else None,
               "mean_original_visit_count":round(float(r.visit_count.mean()),4) if len(r) else None,
            }
        c=counts(CONT)
        i=counts(OTHER)
        block_table.append({
          "block":block,
          "continental_proxy":c,
          "noncontinental_polygon_proxy":i,
          "site_species_seasons_total":c["source_site_species_seasons"]+i["source_site_species_seasons"],
          "observed_raw_island_minus_continental_confirmation_fraction":
              round(i["raw_confirmation_fraction"]-c["raw_confirmation_fraction"],6),
          "pseudo_independent_land_feature_warning":True,
        })
    signed=[b["observed_raw_island_minus_continental_confirmation_fraction"] for b in block_table]
    loo=mod.get("leave_one_100km_block_out_descriptive",[])
    if len(loo)!=6 or not all("beta_source_polygon" in e for e in loo):
        raise ValueError("observed exploratory model leave-block-out evidence incomplete")
    beta=[float(x["beta_source_polygon"]) for x in loo]
    fragility={
      "max_block_record_fraction":round(max(b["site_species_seasons_total"] for b in block_table)/ORIG_ROWS,6),
      "block_with_max_records":max(block_table,key=lambda x:x["site_species_seasons_total"])["block"],
      "spatial_blocks_with_at_most_2_continental_sites":int(sum(x["continental_proxy"]["source_sites"]<=2 for x in block_table)),
      "blocks_with_higher_raw_noncontinent_breeding_confirmation":sum(x>0 for x in signed),
      "blocks_with_lower_raw_noncontinent_breeding_confirmation":sum(x<0 for x in signed),
      "leave_one_block_out_beta_min":round(min(beta),6),
      "leave_one_block_out_beta_max":round(max(beta),6),
    }
    return {
       "schema_version":1,"study":"Antarctic penguin ASI source-only island proxy fragility QA",
       "status":"POST_RESULT_INFERENCE_CEILING_AUDIT_NO_NEW_ECOLOGICAL_EFFECT",
       "upstream_original_runs":{
          "asi":ASI_RUN_ID,"scar":GEO_RUN_ID,"model_exploratory":EXPLORATORY_RUN_ID},
       "input_sha256":{"ASI_site_year_panel":sha(panel_path),
                       "SCAR_196_site_geography":sha(geo_path),
                       "exploratory_undisturbed_model_receipt":sha(model_path)},
       "original_asi_sample":{"visited_site_codes":196,"site_seasons":827},
       "matched_comparison":{"site_codes":ORIG_SITES,"source_site_species_seasons":ORIG_ROWS,"spatial_blocks":ORIG_BLOCKS},
       "block_source_structure":block_table,
       "source_fragility_diagnostics":fragility,
       "fixed_exploratory_result_unchanged":{
          "conditional_odds_ratio":mod["estimate_odds_ratio"],
          "site_cluster_interval_OR":mod["site_cluster_robust_interval_OR"],
          "site_cluster_p_descriptive":mod["site_cluster_robust_p_descriptive"],
       },
       "decision":"HOLD_ANY_ISLAND_REFUGE_CAUSAL_OR_EQUIVALENCE_INFERENCE",
       "limitations":[
          "This audit is conducted AFTER the exploratory coefficient was observed; no new test, p-value, threshold selection, or predictor search is undertaken.",
          "Source SCAR land feature cannot be treated as verified physical offshore island. Mainland is one largest original polygon only.",
          "One matched spatial block holds over half the analysed response rows; other blocks have very sparse continental controls.",
          "Raw block fractions are descriptive and unadjusted for detection or effort; they are not effects or valid p-values.",
          "Only 6 matched regional blocks; site-cluster confidence intervals are not a reliable proof of geographic generality.",
          "The reported odds ratio includes both island advantage and disadvantage; it cannot demonstrate no island effect.",
          "Antarctic absence of native mammalian land predators is not measured within-source contrast with a predator-exposed system.",
          "Original visit scoring is imperfect-detection, not verified true breeding absence; phylogeny/species and marine niches confounded.",
       ],
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("panel-csv","geography-csv","exploratory-json","out-json"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    result=audit(args.panel_csv,args.geography_csv,args.exploratory_json)
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],
                      "source_fragility_diagnostics":result["source_fragility_diagnostics"],
                      "decision":result["decision"]},sort_keys=True))

if __name__=="__main__":
    main()
