import math

import numpy as np

from mina.hierarchy_count_error import _raw_batch, _tail


def test_latent_proportional_subcolonies_have_beta_within_one():
    years=np.asarray([100.0,80.0,60.0,40.0,20.0])
    counts={
        "COR":np.asarray([[
            years*0.25,
            years*0.75,
        ]]).reshape(1,2,5),
        "HUM":np.asarray([[
            years[::-1]*0.40,
            years[::-1]*0.60,
        ]]).reshape(1,2,5),
        "LIT":np.asarray([[
            np.asarray([70.,60.,50.,40.,30.])*0.30,
            np.asarray([70.,60.,50.,40.,30.])*0.70,
        ]]).reshape(1,2,5),
    }
    beta_within,beta_among,contrast=_raw_batch(counts)
    assert math.isclose(float(beta_within[0]),1.0,abs_tol=1e-12)
    assert float(beta_among[0])>=1.0
    assert math.isclose(
        float(contrast[0]),
        math.log(float(beta_within[0])/float(beta_among[0])),
        abs_tol=1e-12,
    )


def test_monte_carlo_tail_uses_plus_one_correction():
    result=_tail(np.asarray([0.1,0.2,0.3]),0.25)
    assert result["exceedances_ge_observed"]==1
    assert math.isclose(
        result["one_sided_probability_ge_observed"],
        0.5,
        abs_tol=1e-12,
    )
