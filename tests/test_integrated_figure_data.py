import json
from pathlib import Path

import pandas as pd

from scripts.build_integrated_figure_data import build


def test_integrated_figure_data_matches_frozen_receipts(tmp_path):
    root=Path(__file__).resolve().parents[1]
    manifest=build(root,tmp_path)

    fig2=pd.read_csv(tmp_path/"figure2_palmer_concentration.csv")
    assert set(fig2["island_code"])=={"COR","HUM","LIT"}
    assert abs(float(fig2.loc[fig2.island_code=="COR","cv20_p"].iloc[0])-0.037999620003799965)<1e-15

    fig3=pd.read_csv(tmp_path/"figure3_species_interactions.csv")
    assert len(fig3)==3
    assert (fig3["gamma_ah"]<0).all()
    assert set(fig3.loc[fig3["crossover_classification"],"species_id"])=={"CHPE","GEPE"}

    null=pd.read_csv(tmp_path/"figure3_paper_level_null.csv")
    assert abs(float(null["observed_median_gamma_ah"].iloc[0])+0.31822603579776854)<1e-12
    assert abs(float(null["permutation_p"].iloc[0])-0.0947)<1e-12

    scale=pd.read_csv(tmp_path/"figure4_scale_sensitivity.csv")
    by=dict(zip(scale["variant"],scale["median_gamma_ah"]))
    assert by["2 km richness (primary)"]<0
    assert by["5 km richness"]>0

    mde=pd.read_csv(tmp_path/"figure4_detectable_effect.csv")
    assert len(mde)==9
    assert abs(float(mde.loc[mde["abs_truth_gamma_ah"]==0.5,"detection_fraction"].iloc[0])-0.81)<1e-12

    assert abs(manifest["figure4"]["radius_joint_switch_plus_contrast_p"]-0.081)<1e-12
    assert abs(manifest["figure4"]["MDE80_abs_gamma_ah"]-0.49765625)<1e-12
    assert abs(manifest["figure4"]["MDE90_abs_gamma_ah"]-0.5385714285714286)<1e-12


def test_manifest_uses_frozen_receipts_only(tmp_path):
    root=Path(__file__).resolve().parents[1]
    build(root,tmp_path)
    manifest=json.loads((tmp_path/"figure_data_manifest.json").read_text())
    for path in manifest["provenance"].values():
        assert path.startswith("results/")
        assert (root/path).exists()
