import unittest
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from scripts.audit_palmer_reproductive_denominator import (
    fit_beta,
    score_test,
)

class DenominatorAuditTests(unittest.TestCase):
    def test_positive_size_effect_detected_in_count_space(self):
        groups=[]
        for island in ("A","B"):
            pairs=np.array([2.,5.,20.,50.])
            xraw=np.log1p(pairs); x=(xraw-xraw.mean())/xraw.std(ddof=0)
            p=pairs/pairs.sum()
            chicks=np.array([1,4,25,80])
            mu=float((p*x).sum()); var=float((p*(x-mu)**2).sum())
            groups.append({
                "island":island,"study_name":"S","n":4,"chicks":chicks,
                "adult":{"pairs":pairs,"x":x,"p":p,
                         "score":float((chicks*x).sum()-chicks.sum()*mu),
                         "information":float(chicks.sum()*var)},
                "legacy":{"pairs":pairs.copy(),"x":x.copy(),"p":p.copy(),
                          "score":float((chicks*x).sum()-chicks.sum()*mu),
                          "information":float(chicks.sum()*var)},
            })
        fit=fit_beta(groups,"adult")
        self.assertGreater(fit["beta"],0)
        out=score_test(groups,"adult",draws=9999,seed=7)
        self.assertLess(out["one_sided_upper_p"],0.05)

if __name__=="__main__":
    unittest.main()
