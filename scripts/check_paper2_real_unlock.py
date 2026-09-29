#!/usr/bin/env python3
"""Fail-closed unlock guard for Paper 2 real outcomes."""
from __future__ import annotations
import json
from pathlib import Path

CORE_RESULT=Path("results/PAPER2_SPATIAL_ADJUSTED_V3_RESULT_V1.json")
SOURCE_RESULT=Path("results/PAPER2_V3_SOURCE_SENSITIVITY_RESULT_V1.json")

def assert_real_outcome_unlocked(root:Path=Path("."))->dict:
    paths=[root/CORE_RESULT,root/SOURCE_RESULT]
    missing=[str(p) for p in paths if not p.exists()]
    if missing:
        raise RuntimeError(f"Paper 2 outcomes locked; missing pre-outcome receipts: {missing}")
    core=json.loads(paths[0].read_text(encoding="utf-8"))
    source=json.loads(paths[1].read_text(encoding="utf-8"))
    if core.get("decision",{}).get("spatially_adjusted_core_passed") is not True:
        raise RuntimeError("Paper 2 outcomes locked: V3 spatial core did not pass")
    if source.get("decision",{}).get("source_sensitivity_passed") is not True:
        raise RuntimeError("Paper 2 outcomes locked: V3 source sensitivity did not pass")
    if core.get("decision",{}).get("no_real_count_magnitudes_opened") is not True:
        raise RuntimeError("invalid core receipt provenance")
    if source.get("decision",{}).get("no_real_count_magnitudes_opened") is not True:
        raise RuntimeError("invalid source receipt provenance")
    return {"unlocked":True,"core":core["decision"],"source":source["decision"]}

if __name__=="__main__":
    print(json.dumps(assert_real_outcome_unlocked(),indent=2,sort_keys=True))
