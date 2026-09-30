import json
import unittest
from pathlib import Path

try:
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(
        "integrated v0.3 figure-data tests require pandas"
    ) from exc

import importlib.util


def _load_build():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "build_integrated_figure_data_v0_3.py"
    spec = importlib.util.spec_from_file_location(
        "mina_integrated_figure_data_v0_3", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build


build = _load_build()


def test_v03_figure_data_matches_frozen_palmer_state_receipts(tmp_path):
    root = Path(__file__).resolve().parents[1]
    manifest = build(root, tmp_path)

    lag = pd.read_csv(tmp_path / "figure2b_palmer_lag_profile.csv")
    assert list(lag["lag_years"]) == [1, 2, 3, 4, 5]
    beta = dict(zip(lag["lag_years"], lag["beta"]))
    pval = dict(zip(lag["lag_years"], lag["one_sided_p"]))
    assert abs(beta[2] - 0.040890746633273245) < 1e-15
    assert abs(pval[2] - 0.0032699673003269967) < 1e-15
    assert beta[3] > 0
    assert beta[5] < 0
    assert bool(lag.loc[lag.lag_years == 1, "mechanically_coupled"].iloc[0])
    assert bool(lag.loc[lag.lag_years == 2, "primary_bias_resistant"].iloc[0])
    assert not bool(
        lag.loc[lag.lag_years == 2, "fully_preregistered_confirmatory"].iloc[0]
    )

    echo = pd.read_csv(tmp_path / "figure2b_recruitment_echo.csv")
    assert float(echo["observed"].iloc[0]) < 0
    assert abs(float(echo["one_sided_p"].iloc[0]) - 0.987730122698773) < 1e-12

    val = pd.read_csv(tmp_path / "figure2c_palmer_metric_validation.csv")
    by = val.set_index("estimate_id")
    assert abs(
        float(by.loc["REPRO mean creched chicks/nest, lag 1", "beta"])
        - 0.02960239689099827
    ) < 1e-15
    assert abs(
        float(by.loc["REPRO mean creched chicks/nest, lag 1", "one_sided_p"])
        - 0.23194768052319475
    ) < 1e-15
    assert float(by.loc["Common-panel colony-wide state", "beta"]) > 0.10
    assert (
        by.loc["Common-panel colony-wide state", "inference_role"]
        == "posthoc_diagnostic_only"
    )

    assert abs(manifest["figure2"]["lag2_beta"] - 0.040890746633273245) < 1e-15
    assert manifest["figure2"]["repro_primary_supported"] is False
    assert abs(
        manifest["figure2"]["same_panel_state_vs_mean_nest_r"]
        - 0.13161449316495238
    ) < 1e-15


def test_v03_keeps_paper2_nonconfirmatory_and_scale_receipts(tmp_path):
    root = Path(__file__).resolve().parents[1]
    manifest = build(root, tmp_path)

    null = pd.read_csv(tmp_path / "figure3_paper_level_null.csv")
    assert abs(float(null["permutation_p"].iloc[0]) - 0.0947) < 1e-12

    scale = pd.read_csv(tmp_path / "figure4_scale_sensitivity.csv")
    by = dict(zip(scale["variant"], scale["median_gamma_ah"]))
    assert by["2 km richness (primary)"] < 0
    assert by["5 km richness"] > 0

    assert abs(
        manifest["figure4"]["radius_joint_switch_plus_contrast_p"] - 0.081
    ) < 1e-12
    assert abs(manifest["figure4"]["MDE80_abs_gamma_ah"] - 0.49765625) < 1e-12
    assert abs(
        manifest["figure4"]["MDE90_abs_gamma_ah"] - 0.5385714285714286
    ) < 1e-12


def test_v03_manifest_uses_receipts_only(tmp_path):
    root = Path(__file__).resolve().parents[1]
    build(root, tmp_path)
    manifest = json.loads((tmp_path / "figure_data_manifest.json").read_text())
    for path in manifest["provenance"].values():
        assert path.startswith("results/")
        assert (root / path).exists()
