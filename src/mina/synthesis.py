"""Build a drift-resistant ecological synthesis from frozen mina receipts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FILES={
    "exploratory":"EXPLORATORY_RESULT_V1.json",
    "network":"PALMER_NETWORK_STAGE2_RESULT_V1.json",
    "synchrony":"PALMER_LTER_FIVE_ISLAND_SYNCHRONY_RESULT_V1.json",
    "seaice":"PALMER_SEAICE_HABITAT_MECHANISM_RESULT_V1.json",
    "timescale":"PALMER_SEAICE_TIMESCALE_SEPARATION_RESULT_V1.json",
    "weather":"PALMER_WEATHER_X_HABITAT_MECHANISM_RESULT_V2.json",
    "colony":"PALMER_COLONY_NETWORK_EROSION_RESULT_V1.json",
    "large":"PALMER_LARGE_BREEDING_GROUP_THRESHOLD_RESULT_V1.json",
    "spatial":"PALMER_EXTERNAL_SPATIAL_TRIANGULATION_RESULT_V1.json",
    "neff_perm":"PALMER_NEFF_YEAR_BLOCK_PERMUTATION_RESULT_V1.json",
    "neff_coupling":"PALMER_NEFF_MECHANICAL_COUPLING_RESULT_V1.json",
    "neff_circular":"PALMER_NEFF_CIRCULAR_SHIFT_RESULT_V1.json",
    "neff_circular_coupling":"PALMER_NEFF_CIRCULAR_COUPLING_RESULT_V1.json",
}


def load(results_dir: str|Path) -> dict[str,dict]:
    root=Path(results_dir)
    return {
        key:json.loads((root/name).read_text(encoding="utf-8"))
        for key,name in FILES.items()
    }


def build(results_dir: str|Path) -> dict[str,object]:
    r=load(results_dir)
    sync=r["synchrony"]; sea=r["seaice"]; time=r["timescale"]
    weather=r["weather"]; colony=r["colony"]; large=r["large"]
    exploratory=r["exploratory"]; network=r["network"]; spatial=r["spatial"]
    perm=r["neff_perm"]; coupling=r["neff_coupling"]
    circular=r["neff_circular"]; circular_coupling=r["neff_circular_coupling"]

    if sea["primary_result"]["decision"]["regional_support"] is not False:
        raise ValueError("annual sea-ice decision drifted")
    if time["decision"]["timescale_separation_supported"] is not False:
        raise ValueError("sea-ice timescale decision drifted")
    if weather["decision"]!="not_supported":
        raise ValueError("snowfall x habitat decision drifted")
    if large["primary"]["decision"]!="not_supported":
        raise ValueError("external >50-pair directional decision drifted")
    if spatial["decision"]["phenomenon_level_spatial_convergence"] is not True:
        raise ValueError("external spatial convergence endpoint drifted")
    if spatial["decision"]["identifier_level_validation"] is not False:
        raise ValueError("colony-code crosswalk boundary drifted")
    if perm["decision"]["primary_positive_predictive_pillar_survives"] is not False:
        raise ValueError("N_eff permutation decision drifted")
    if coupling["decision"]["observed_beta_unusual_under_all_coupled_nulls"] is not True:
        raise ValueError("legacy N_eff coupling diagnostic drifted")
    if circular["decision"]["association_retained_against_both_structured_nulls"] is not True:
        raise ValueError("N_eff circular-shift decision drifted")
    if circular_coupling["decision"]["observed_beta_unusual_under_all_coupled_circular_nulls"] is not True:
        raise ValueError("N_eff circular-coupling decision drifted")

    endpoint_fractions={
        island:float(row["fraction_remaining"])
        for island,row in sync["endpoints"].items()
    }
    return {
        "schema_version":4,
        "synthesis_id":"mina-palmer-island-ecology-synthesis-v4",
        "core_claim":"Neighboring Adelie breeding islands share a strong long-term regional decline but diverge in annual dynamics and local ecological endpoints. Simple sea-ice-duration and snowfall formulations do not explain that divergence. Within-island effective colony number has a positive conditional association with next-year growth that survives serial-structure-preserving circular-shift and fixed shared-count-error nulls, but its small held-out predictive gain remains compatible with permutation noise; independent Torgersen mapping confirms real habitat-structured sub-colony attrition.",
        "origin":{
            "status":"historical motivation only; not part of the core manuscript argument",
            "pooled_morphology_gain":exploratory["frozen_odsp_context"]["naive_pooled_morphology_gain"],
            "species_layer_gain":exploratory["frozen_odsp_context"]["species_layer_gain"],
            "species_conditioned_morphology_gain":exploratory["frozen_odsp_context"]["species_conditioned_morphology_gain"],
        },
        "assembly_endpoints":{
            "litchfield_local_extinction":network["abundance_endpoints"]["LITC"]["Adelie"],
            "biscoe_benchmark_adélie":network["abundance_endpoints"]["BISC"]["Adelie"],
            "biscoe_benchmark_gentoo":network["abundance_endpoints"]["BISC"]["Gentoo"],
            "biscoe_functional_reassembly":network["benchmark_functional_reassembly"],
        },
        "five_island_decline":{
            "role":"descriptive synchrony context, not novelty by itself",
            "n_years":sync["synchronized_panel"]["n_years"],
            "pc1_variance_fraction":sync["common_long_term_component"]["pc1_variance_fraction"],
            "median_annual_growth_correlation":sync["annual_growth_synchrony"]["median_pairwise_correlation"],
            "unique_year_fraction":sync["additive_decomposition"]["unique_year_fraction"],
            "unique_island_fraction":sync["additive_decomposition"]["unique_island_fraction"],
            "residual_fraction":sync["additive_decomposition"]["residual_fraction"],
            "endpoint_fraction_remaining":endpoint_fractions,
        },
        "prospective_mechanism_tests":{
            "annual_seaice_duration":{
                "gain":sea["primary_result"]["predictive_gain_M0_minus_M1"],
                "beta":sea["primary_result"]["regional_beta_M1"],
                "supported":sea["primary_result"]["decision"]["regional_support"],
            },
            "five_year_seaice_duration":{
                "gain":time["primary_K5"]["purged_validation"]["gain_T0_minus_T1"],
                "beta":time["primary_K5"]["full_fit"]["seaice_beta_T1"],
                "supported":time["decision"]["timescale_separation_supported"],
            },
            "october_snow_x_habitat":{
                "loyo_rmse_change_full_minus_null":weather["leave_one_year_out"]["rmse_change_full_minus_null"],
                "interaction_beta":weather["model"]["full"]["interaction_coefficient"],
                "supported":weather["decision"]=="supported",
            },
        },
        "local_colony_state":{
            "effective_colony_number":{
                "gain":colony["primary"]["loyo"]["mse_gain_c0_minus_c1"],
                "beta":colony["primary"]["full_data_coefficient"],
                "original_directional_decision":colony["primary"]["decision"],
                "predictive_gain_permutation_p":perm["gain_null"]["one_sided_permutation_p"],
                "predictive_gain_null_percentile":perm["gain_null"]["observed_percentile"],
                "predictive_supported_after_uncertainty":False,
                "legacy_beta_block_permutation_p":perm["coefficient_null"]["one_sided_permutation_p"],
                "circular_shift":{
                    "independent_island_p":circular["primary_independent_island_circular_shift"]["coefficient_null"]["one_sided_p"],
                    "joint_persistent_islands_exact_p":circular["joint_persistent_island_shift_sensitivity"]["coefficient_null"]["exact_one_sided_p"],
                    "retained_against_both":circular["decision"]["association_retained_against_both_structured_nulls"],
                },
                "circular_coupling":{
                    "poisson_p_ge_observed":circular_coupling["error_models"]["poisson"]["coupled_beta"]["one_sided_probability_ge_observed"],
                    "gamma_poisson_cv10_p_ge_observed":circular_coupling["error_models"]["gamma_poisson_cv10"]["coupled_beta"]["one_sided_probability_ge_observed"],
                    "gamma_poisson_cv20_p_ge_observed":circular_coupling["error_models"]["gamma_poisson_cv20"]["coupled_beta"]["one_sided_probability_ge_observed"],
                    "max_median_bias_fraction_of_observed":max(
                        abs(float(circular_coupling["error_models"][name]["paired_coupling_bias"]["median_fraction_of_observed_beta"]))
                        for name in ("poisson","gamma_poisson_cv10","gamma_poisson_cv20")
                    ),
                },
                "association_retained":True,
            },
            "active_colony_count":{
                "gain":colony["sensitivities"]["active_colony_count"]["mse_gain_c0_minus_c1"],
                "beta":colony["sensitivities"]["active_colony_count"]["coefficient"],
            },
            "external_gt50_group_count":{
                "gain":large["primary"]["loyo"]["mse_gain_g0_minus_g1"],
                "beta":large["primary"]["coefficient"],
                "directional_supported":large["primary"]["decision"]=="supported",
            },
            "external_spatial_triangulation":{
                "phenomenon_level_convergence":spatial["decision"]["phenomenon_level_spatial_convergence"],
                "identifier_level_validation":spatial["decision"]["identifier_level_validation"],
                "torgersen_active_footprint_fraction":spatial["external_torgersen_spatial"]["active_footprint_fraction"],
                "south_extinction_fraction":spatial["external_torgersen_spatial"]["south_extinction_fraction"],
                "north_extinction_fraction":spatial["external_torgersen_spatial"]["north_extinction_fraction"],
            },
        },
        "terminal_interpretation":{
            "synchrony":"The common long-term trend versus moderate annual synchrony is consistent with established timescale-dependent synchrony theory and is descriptive context rather than a stand-alone novelty claim.",
            "regional":"The tested sea-ice-duration formulations do not identify the mechanism of the common regional decline.",
            "local":"Local endpoints differ among breeding patches, including persistence, vacancy/extinction and species replacement.",
            "colony_state":"Effective colony number retains a positive conditional coefficient that survives independent island-wise circular shifts (p<1e-5) and an exact cross-island-covariance-preserving shift sensitivity (p=0.0024), but its +0.00103 held-out MSE gain is not unusual under year-block permutation (p=0.262); it is an association, not robust out-of-year prediction.",
            "measurement_error":"With latent topology also circularly shifted, fixed Poisson and 10%/20% Gamma-Poisson coupled simulations still rarely generate an observed-scale coefficient (p=0.00030, 0.00150, 0.00780); simple shared census error under these stylized models is not sufficient to explain the association.",
            "external_triangulation":"Independent Torgersen mapping confirms strong, habitat-structured sub-colony attrition at the phenomenon level.",
            "causal_boundary":"No public one-to-one colony_code/GIS polygon crosswalk is resolved; causal habitat-fragmentation claims remain out of scope.",
        },
        "journal_position":{
            "jae_submission_ready":False,
            "recommended_first_shot":"Ecosphere",
            "fallback":"Ecology and Evolution",
        },
    }


def markdown(x: dict[str,object]) -> str:
    d=x["five_island_decline"]; m=x["prospective_mechanism_tests"]
    c=x["local_colony_state"]; n=c["effective_colony_number"]
    endpoints=d["endpoint_fraction_remaining"]; s=c["external_spatial_triangulation"]
    return f"""# Palmer island-ecology synthesis v4

## Central result

{x["core_claim"]}

## Synchrony context

Across 27 synchronized census years, PC1 explains **{100*d["pc1_variance_fraction"]:.1f}%** of standardized five-island log-abundance variation, while median pairwise annual-growth correlation is **{d["median_annual_growth_correlation"]:.3f}**. This timescale contrast is treated as expected synchrony structure, not as the manuscript's novelty by itself.

By 2017 the fraction of 1991 breeding-pair abundance remaining is Christine **{100*endpoints["CHR"]:.1f}%**, Cormorant **{100*endpoints["COR"]:.1f}%**, Humble **{100*endpoints["HUM"]:.1f}%**, Litchfield **{100*endpoints["LIT"]:.1f}%**, and Torgersen **{100*endpoints["TOR"]:.1f}%**.

## Bounded mechanism tests

Annual and five-year sea-ice-duration formulations and October snowfall × snow-prone habitat do not satisfy their frozen directional/predictive rules. These failures apply to the tested formulations only.

## Colony organization after uncertainty diagnostics

The conditional N_eff coefficient is **{n["beta"]:+.4f}**. The original held-out MSE gain is **{n["gain"]:+.6f}**, but the year-block predictive-gain p-value is **{n["predictive_gain_permutation_p"]:.3f}**; robust predictive support is therefore withdrawn. The coefficient survives independent island-wise circular shifts (p=**{n["circular_shift"]["independent_island_p"]:.3g}**) and the exact joint-shift sensitivity (p=**{n["circular_shift"]["joint_persistent_islands_exact_p"]:.4f}**). Under circular-shift count-error coupling nulls, the largest coupled p-value across the three fixed error models is **{max(n["circular_coupling"]["poisson_p_ge_observed"],n["circular_coupling"]["gamma_poisson_cv10_p_ge_observed"],n["circular_coupling"]["gamma_poisson_cv20_p_ge_observed"]):.4f}**.

## External spatial triangulation

Independent Torgersen mapping retains only **{100*s["torgersen_active_footprint_fraction"]:.1f}%** of historic active sub-colony footprints by 2022. This is phenomenon-level spatial convergence, not colony-ID-level validation.

## Ecological interpretation

The ecological contribution is the divergence of local fates within an externally subsidized breeding-island system: a shared regional decline can terminate in persistence, vacancy/extinction, or species replacement, while internal colony organization remains associated with local demographic state without demonstrating robust out-of-year prediction or causal habitat fragmentation.
"""


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--results",type=Path,default=Path("results"))
    p.add_argument("--out-json",type=Path,required=True)
    p.add_argument("--out-md",type=Path,required=True)
    a=p.parse_args()
    x=build(a.results)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_md.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    a.out_md.write_text(markdown(x),encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
