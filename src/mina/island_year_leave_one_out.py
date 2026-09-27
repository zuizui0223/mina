"""Leave-one-island-out robustness for the frozen island-year coherence result."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .lter import ISLANDS
from .island_year_coherence import _run

N_PERMUTATIONS=20_000
SEED=20260927

def analyze(path: str|Path, n_permutations: int=N_PERMUTATIONS, seed: int=SEED):
    results={}
    for idx, omitted in enumerate(ISLANDS):
        kept=tuple(x for x in ISLANDS if x!=omitted)
        results[omitted]=_run(path,kept,n_permutations,seed+idx)
    uniform=all(
        bool(v["supported"])
        and float(v["observed"]["island_year_covariance_contrast"])>0
        and float(v["null"]["two_sided_p"])<=0.05
        for v in results.values()
    )
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-island-year-leave-one-out-v1",
        "omissions":results,
        "decision":{"uniform_leave_one_island_out_robustness":bool(uniform)},
        "interpretation_boundary":{
            "post_positive_robustness":True,
            "all_omissions_reported":True,
            "does_not_test_distance_conditioned_coastline_effect":True
        }
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--census",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--permutations",type=int,default=N_PERMUTATIONS)
    p.add_argument("--seed",type=int,default=SEED)
    a=p.parse_args()
    x=analyze(a.census,a.permutations,a.seed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
