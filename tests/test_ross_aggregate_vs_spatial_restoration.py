from pathlib import Path
import importlib.util

PATH = Path("scripts/analyze_ross_aggregate_vs_spatial_restoration.py")
spec = importlib.util.spec_from_file_location("ross_restore", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_effective_number_equal_distribution():
    assert mod.effective_number([10,10,10]) == 3.0

def test_anchor_restoration_arithmetic():
    rows = mod.read_counts(Path("external/ross_island_v2_frozen_counts.csv"))
    pre = rows[1999]
    shock = rows[2001]
    rebound = rows[2002]
    assert sum(pre.values()) == 207411
    assert sum(shock.values()) == 94798
    assert sum(rebound.values()) == 203996
    assert sum(rebound.values()) - sum(shock.values()) == 109198
    assert sum(pre.values()) - sum(shock.values()) == 112613

def test_crozier_overshoot_and_royds_bird_lag():
    rows = mod.read_counts(Path("external/ross_island_v2_frozen_counts.csv"))
    pre = mod.aggregate3(rows[1999])
    rebound = mod.aggregate3(rows[2002])
    assert rebound["Crozier"] > pre["Crozier"]
    assert rebound["Bird"] < pre["Bird"]
    assert rebound["Royds"] < pre["Royds"]
