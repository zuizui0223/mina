"""Main-accepted penguin macro positive-claim ledger scope consistency.

Test only scientific claim metadata, denominators and inference guardrails; do not
pretend archived original physical models or third-party guano data are bundled.
"""
import json
from pathlib import Path
def test_antarctic_macro_positive_claims_20261118():
    repo=Path(__file__).resolve().parents[1]
    p=repo/"results/ANTARCTIC_MACRO_POSITIVE_RESULTS_20261118.json"
    x=json.loads(p.read_text(encoding="utf-8"))
    assert x["status"]=="MAIN_ACCEPTED_SOURCE_AUDITED_POSITIVE_CLAIMS_NOT_CAUSAL_INFERENCE"
    assert x["integration_scope"].startswith("claim ledger only")
    a={i["id"]:i for i in x["claims"]}
    assert set(a)=={
      "physical_two_axes","adelie_salinity_optical_isotope",
      "fixed_adelie_colony_nest_reweighting",
      "source_matched_gentoo_adelie_nesting_composition",
      "CMIP6_joint_ice_freshening_physical_exposure"}
    climate=a["physical_two_axes"]
    assert (climate["n_original_sites"],climate["n_original_site_years"],climate["n_original_wet_cells"])==(588,16464,378)
    assert abs(climate["PC1_explained_fraction"]-.603654)<1e-8
    assert abs(climate["PC2_explained_fraction"]-.333773)<1e-8
    isotope=a["adelie_salinity_optical_isotope"]
    assert (isotope["n_original_site_seasons"],isotope["n_sites"],isotope["n_GLORYS_wet_cells"],isotope["n_regions"])==(860,88,82,13)
    assert isotope["beta_delta15N_per_salinity_unit"]>0
    assert isotope["cell_cluster_normal_95ci"][0]>0
    assert isotope["conservative_13region_t_95ci"][0]<0<isotope["conservative_13region_t_95ci"][1]
    assert isotope["conditional_residual_partial_r2"]<.03
    nests=a["fixed_adelie_colony_nest_reweighting"]
    assert nests["n_nested_rosters"]==[19,26,35]
    assert all(z>0 for z in nests["weighted_south_shift_km"])
    pairs=a["source_matched_gentoo_adelie_nesting_composition"]
    assert (pairs["n_strict_matched_colonies"],pairs["n_reporting_regions"],
            pairs["n_positive_gentoo_to_adelie_ratio_slopes"],
            pairs["n_positive_two_species_observed_subtotal_change"])==(6,2,6,5)
    fut=a["CMIP6_joint_ice_freshening_physical_exposure"]
    assert (fut["known_site_ids"],fut["n_selected_models"],
            fut["n_595_sites_all3_sos_decrease"],
            fut["n_595_sites_all3_sos_and_sic_decrease"])==(595,3,464,384)
    assert (fut["n_true_2011_2020_counted_sites"],
            fut["n_counted_sites_all3_sos_decrease"],
            fut["n_counted_sites_all3_both_decrease"])==(271,179,152)
    assert abs(fut["fixed_observed_nest_median_weight_fraction_all3_sos_decrease"]-.935425)<1e-9
    assert abs(fut["fixed_observed_nest_median_weight_fraction_all3_both_decrease"]-.590808)<1e-9
    assert fut["model_raw_spatial_r_delta_sic_vs_delta_sos"]["ACCESS-CM2"]>0
    assert fut["model_raw_spatial_r_delta_sic_vs_delta_sos"]["CESM2"]<0
    assert all(i["inference_boundary"] for i in a.values())
    assert x["rejected_as_unverified_main_claims"]
    doc=(repo/"docs/ANTARCTIC_MACRO_POSITIVE_RESULTS_20261118.md").read_text(encoding="utf-8")
    for anchor in ["60.3654%","33.3773%","+0.8341","2.880%","107.31","88.41","6/6","5/6","464/595","384/595"]:
        assert anchor in doc, anchor
