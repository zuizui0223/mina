import itertools
import json

from mina.mechanism import static_habitat_validation


def test_static_habitat_exact_permutation(tmp_path):
    receipt = {
        "trend_slopes_annual_multiplicative_change": {
            "CHR": -0.12,
            "COR": -0.13,
            "HUM": -0.10,
            "LIT": -0.28,
            "TOR": -0.17,
        }
    }
    out = static_habitat_validation(receipt)
    assert out["pearson_r"] < 0
    assert out["spearman_rho"] < 0
    assert 0 <= out["pearson_exact_permutation_p_two_sided"] <= 1
    assert 0 <= out["spearman_exact_permutation_p_two_sided"] <= 1
    assert out["interpretation_boundary"]["n_islands"] == 5
