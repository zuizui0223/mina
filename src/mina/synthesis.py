"""Build a drift-resistant ecological synthesis from frozen mina receipts."""
from __future__ import annotations
import argparse, json
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
}

def load(results_dir: str|Path) -> dict[str,dict]:
    root=Path(results_dir)
    return {key:json.loads((root/name).read_text(encoding="utf-8")) for key,name in FILES.items()}

def build(results_dir: str|Path) -> dict[str,object]:
    r=load(results_dir)
    sync=r["synchrony"]; sea=r["seaice"]; time=r["timescale"]
    weather=r["weather"]; colony=r["colony"]; large=r["large"]
    exploratory=r["exploratory"]; network=r["network"]; spatial=r["spatial"]

    if colony["primary"]["decision"]!="supported":
        raise ValueError("colony-network positive endpoint drifted")
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

    endpoint_fractions={
        island:float(row["fraction_remaining"])
        for island,row in sync["endpoints"].items()
    }
    return {
        "schema_version":2,
        "synthesis_id":"mina-palmer-island-ecology-synthesis-v2",
        "core_claim":"A nearly common long-term Adelie decline across neighboring islands coexists with strongly local collapse dynamics; simple climate/weather proxies do not prospectively explain that heterogeneity, while distributed breeding-colony structure carries a small positive signal of next-year local demographic resilience and independent Torgersen mapping shows real, habitat-structured sub-colony attrition.",
        "origin":{
            "pooled_morphology_gain":exploratory["frozen_odsp_context"]["naive_pooled_morphology_gain"],
            "species_layer_gain":exploratory["frozen_odsp_context"]["species_layer_gain"],
            "species_conditioned_morphology_gain":exploratory["frozen_odsp_context"]["species_conditioned_morphology_gain"],
            "structural_cross_year_balanced_accuracy":exploratory["cross_year_transfer"]["structural_morphology"]["mean_balanced_accuracy"],
            "three_island_chance":exploratory["cross_year_transfer"]["structural_morphology"]["chance_reference"],
        },
        "assembly_endpoints":{
            "litchfield_local_extinction":network["abundance_endpoints"]["LITC"]["Adelie"],
            "biscoe_benchmark_adélie":network["abundance_endpoints"]["BISC"]["Adelie"],
            "biscoe_benchmark_gentoo":network["abundance_endpoints"]["BISC"]["Gentoo"],
            "biscoe_functional_reassembly":network["benchmark_functional_reassembly"],
        },
        "five_island_decline":{
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
                "supported":colony["primary"]["decision"]=="supported",
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
            "external_gt50_group_fraction":{
                "gain":large["fixed_sensitivity"]["loyo"]["mse_gain_g0_minus_g1"],
                "beta":large["fixed_sensitivity"]["coefficient"],
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
            "regional":"The five islands share the direction of long-term decline, but the tested sea-ice-duration formulations do not identify its mechanism.",
            "local":"Island-specific vulnerability is substantial, and a distributed colony network predicts slightly better next-year performance beyond abundance and time.",
            "specificity":"The positive topology result is about distribution/evenness rather than simply having more active colonies or more >50-pair breeding groups.",
            "external_triangulation":"Independent Torgersen mapping confirms strong, habitat-structured sub-colony attrition, providing process-level spatial convergence with the internal colony-network signal.",
            "causal_boundary":"The public LTER colony_code values are not yet crosswalked one-to-one to the independent GIS polygons, so identifier-level validation and causal habitat-fragmentation claims remain out of scope.",
        },
    }

def markdown(x: dict[str,object]) -> str:
    d=x["five_island_decline"]; m=x["prospective_mechanism_tests"]; c=x["local_colony_state"]
    endpoints=d["endpoint_fraction_remaining"]; s=c["external_spatial_triangulation"]
    return f"""# Palmer island-ecology synthesis v2

## Central result

{x["core_claim"]}

## Scale separation

Across 27 synchronized census years (1991–2017), PC1 explains **{100*d["pc1_variance_fraction"]:.1f}%** of standardized five-island log-abundance variation, yet median pairwise annual-growth correlation is only **{d["median_annual_growth_correlation"]:.3f}**. The additive decomposition assigns **{100*d["unique_year_fraction"]:.1f}%** of total log-abundance variance uniquely to year, **{100*d["unique_island_fraction"]:.1f}%** uniquely to island, and **{100*d["residual_fraction"]:.1f}%** to residual variation.

By 2017 the fraction of 1991 breeding-pair abundance remaining is: Christine **{100*endpoints["CHR"]:.1f}%**, Cormorant **{100*endpoints["COR"]:.1f}%**, Humble **{100*endpoints["HUM"]:.1f}%**, Litchfield **{100*endpoints["LIT"]:.1f}%**, and Torgersen **{100*endpoints["TOR"]:.1f}%**.

## Prospective mechanism tests

- Annual sea-ice duration: held-out MSE gain **{m["annual_seaice_duration"]["gain"]:+.4f}**, beta **{m["annual_seaice_duration"]["beta"]:+.3f}**; predeclared positive mechanism not supported.
- Five-year sea-ice duration: purged predictive gain **{m["five_year_seaice_duration"]["gain"]:+.4f}**, beta **{m["five_year_seaice_duration"]["beta"]:+.3f}**; timescale rescue not supported.
- October snowfall × snow-prone habitat: LOYO RMSE change full-minus-null **{m["october_snow_x_habitat"]["loyo_rmse_change_full_minus_null"]:+.4f}**, interaction beta **{m["october_snow_x_habitat"]["interaction_beta"]:+.3f}**; directional interaction not supported.

These are failures of specific predeclared formulations, not evidence that marine climate or terrestrial habitat are ecologically irrelevant.

## Local breeding-network state

Effective colony number adds a small positive held-out-year increment (MSE gain **{c["effective_colony_number"]["gain"]:+.4f}**, beta **{c["effective_colony_number"]["beta"]:+.3f}**). Active-colony count does not improve transfer. The externally fixed >50-pair group count improves prediction but has the opposite sign to its historical positive-direction hypothesis.

## External spatial triangulation

Independent mapped Torgersen footprints retain only **{100*s["torgersen_active_footprint_fraction"]:.1f}%** of the historic active sub-colony count by 2022. The extinction fraction is **{100*s["south_extinction_fraction"]:.1f}%** for south-aspect historic footprints versus **{100*s["north_extinction_fraction"]:.1f}%** for north-aspect footprints. This is process-level spatial convergence with colony-network erosion, not an identifier-level validation of the exact LTER `colony_code` metric.

## Ecological interpretation

Palmer penguins create an unusually clean island-ecology contrast because food resources are largely marine while breeding habitat is discrete and terrestrial. Regional processes can impose a common demographic direction without producing identical local dynamics. The internal organization of breeding colonies indexes local vulnerability, and independent Torgersen mapping confirms that real breeding footprints contract non-randomly across physical habitat.

The causal boundary remains explicit: no public one-to-one crosswalk between LTER `colony_code` and the independent GIS polygons has been resolved.
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
