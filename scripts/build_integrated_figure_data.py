#!/usr/bin/env python3
"""Build integrated manuscript figure-data tables from frozen receipts only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load(root:Path,path:str)->dict:
    return json.loads((root/path).read_text(encoding="utf-8"))


def build(root:Path,out_dir:Path)->dict:
    out_dir.mkdir(parents=True,exist_ok=True)

    palmer=load(root,"results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json")
    p2=load(root,"results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json")
    scale=load(root,"results/PAPER2_SCALE_TRAIT_SENSITIVITY_RESULT_V1.json")
    mde=load(root,"results/PAPER2_DETECTABLE_EFFECT_RESULT_V1.json")
    radius=load(root,"results/PAPER2_RADIUS_SIGN_SWITCH_NULL_RESULT_V1.json")
    real=load(root,"results/PAPER2_FIRST_REAL_V3_FIT_RESULT_V1.json")

    # Figure 2A/B: Palmer concentration trajectories endpoints + null summaries.
    rows=[]
    name_map={"COR":"Cormorant","HUM":"Humble","LIT":"Litchfield"}
    for code,name in name_map.items():
        obs=palmer["observed"][code]
        cv20=palmer["null_slope_summaries"]["gamma_poisson_cv20"][code]
        rows.append({
            "island_code":code,
            "island":name,
            "first_neff":obs["first_neff"],
            "last_neff":obs["last_neff"],
            "fractional_change":obs["fractional_change"],
            "observed_slope_per_year":obs["slope_per_year"],
            "cv20_null_mean_slope":cv20["mean"],
            "cv20_q025":cv20["q_0_025"],
            "cv20_q975":cv20["q_0_975"],
            "cv20_p":cv20["p"],
        })
    fig2=pd.DataFrame(rows)
    fig2.to_csv(out_dir/"figure2_palmer_concentration.csv",index=False)

    # Figure 3A: species effects.
    rows=[]
    for sp in ("ADPE","CHPE","GEPE"):
        pt=real["primary"][sp]
        inf=p2["species"][sp]
        rows.append({
            "species_id":sp,
            "gamma_a":pt["gamma_a"],
            "gamma_h":pt["gamma_h"],
            "gamma_ah":pt["gamma_ah"],
            "low_area_H_slope":pt["low_area_H_slope"],
            "high_area_H_slope":pt["high_area_H_slope"],
            "crossover_classification":pt["crossover_classification"],
            "raw_p_value":inf["raw_p_value"],
            "holm_p_value":inf["holm_p_value"],
        })
    fig3a=pd.DataFrame(rows)
    fig3a.to_csv(out_dir/"figure3_species_interactions.csv",index=False)

    # Figure 3B: paper-level observed statistic + frozen permutation quantiles.
    fig3b=pd.DataFrame([{
        "observed_median_gamma_ah":p2["primary"]["observed"],
        "permutation_p":p2["primary"]["p_value"],
        "null_q01":p2["primary"]["permutation_distribution"]["q01"],
        "null_q05":p2["primary"]["permutation_distribution"]["q05"],
        "null_median":p2["primary"]["permutation_distribution"]["median"],
        "null_q95":p2["primary"]["permutation_distribution"]["q95"],
        "null_q99":p2["primary"]["permutation_distribution"]["q99"],
    }])
    fig3b.to_csv(out_dir/"figure3_paper_level_null.csv",index=False)

    # Figure 4A: radius/metric sensitivity.
    rows=[
        {
            "variant":"1 km richness",
            "radius_m":1000,
            "metric":"tier2_richness",
            "median_gamma_ah":scale["variants"]["radius_1000m"]["cross_species_median_gamma_ah"],
            "negative_species":scale["variants"]["radius_1000m"]["negative_species"],
        },
        {
            "variant":"2 km richness (primary)",
            "radius_m":2000,
            "metric":"tier2_richness",
            "median_gamma_ah":scale["primary_reference"]["cross_species_median_gamma_ah"],
            "negative_species":3,
        },
        {
            "variant":"5 km richness",
            "radius_m":5000,
            "metric":"tier2_richness",
            "median_gamma_ah":scale["variants"]["radius_5000m"]["cross_species_median_gamma_ah"],
            "negative_species":scale["variants"]["radius_5000m"]["negative_species"],
        },
        {
            "variant":"2 km Shannon",
            "radius_m":2000,
            "metric":"tier2_shannon",
            "median_gamma_ah":scale["variants"]["shannon_2000m"]["cross_species_median_gamma_ah"],
            "negative_species":scale["variants"]["shannon_2000m"]["negative_species"],
        },
    ]
    pd.DataFrame(rows).to_csv(out_dir/"figure4_scale_sensitivity.csv",index=False)

    # Figure 4B: detectable effect curve.
    rows=[]
    for x in mde["effects"]:
        rows.append({
            "truth_gamma_ah":x["truth_gamma_ah"],
            "abs_truth_gamma_ah":abs(x["truth_gamma_ah"]),
            "detection_fraction":x["detection_fraction"],
            "wilson_low":x["wilson95"][0],
            "wilson_high":x["wilson95"][1],
            "median_fitted_gamma_ah":x["median_fitted"],
        })
    pd.DataFrame(rows).to_csv(out_dir/"figure4_detectable_effect.csv",index=False)

    summary={
        "schema_version":1,
        "figure1":{
            "source":"existing frozen Palmer figure-data package",
            "note":"Reuse site map and 1991-2017 trajectory tables; no new data derivation."
        },
        "figure2":{
            "data":"figure2_palmer_concentration.csv",
            "joint_cv20_p":palmer["cv20"]["joint_three_island_p"],
        },
        "figure3":{
            "species_data":"figure3_species_interactions.csv",
            "paper_null_data":"figure3_paper_level_null.csv",
        },
        "figure4":{
            "scale_data":"figure4_scale_sensitivity.csv",
            "detectability_data":"figure4_detectable_effect.csv",
            "radius_joint_switch_plus_contrast_p":radius["decision"]["joint_switch_plus_contrast_probability"],
            "MDE80_abs_gamma_ah":mde["thresholds"]["MDE80_abs_gamma_ah"],
            "MDE90_abs_gamma_ah":mde["thresholds"]["MDE90_abs_gamma_ah"],
        },
        "provenance":{
            "palmer":"results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
            "paper2_primary":"results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json",
            "paper2_real_fit":"results/PAPER2_FIRST_REAL_V3_FIT_RESULT_V1.json",
            "scale":"results/PAPER2_SCALE_TRAIT_SENSITIVITY_RESULT_V1.json",
            "detectability":"results/PAPER2_DETECTABLE_EFFECT_RESULT_V1.json",
            "radius_null":"results/PAPER2_RADIUS_SIGN_SWITCH_NULL_RESULT_V1.json",
        }
    }
    (out_dir/"figure_data_manifest.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    return summary


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    out=build(a.root,a.out_dir)
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
