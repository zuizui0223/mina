from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "ross_shock", ROOT / "scripts" / "analyze_ross_shock_rebound.py"
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)

def test_ross_shock_rebound_key_results():
    counts = MOD.read_counts(ROOT / "external" / "ross_island_v2_frozen_counts.csv")
    x = MOD.build(counts)

    shock = x["transitions"]["1999_2001_shock"]
    rebound = x["transitions"]["2001_2002_rebound"]
    late = x["transitions"]["1999_2012_pre_shock_to_late"]

    assert shock["all_six_declined"]
    assert shock["N_fraction"] < 0
    assert shock["E3_fraction"] > 0
    assert shock["E6_fraction"] > 0

    assert rebound["all_six_increased"]
    assert rebound["N_fraction"] > 1
    assert rebound["E3_fraction"] < 0
    assert rebound["E6_fraction"] < 0
    assert rebound["six_factors"]["Cape Crozier West"] > 2.4

    assert late["N_fraction"] > 0
    assert late["E3_fraction"] < 0
    assert late["E6_fraction"] < 0

def test_matched_branch_support_is_mechanical_and_has_two_pairs():
    counts = MOD.read_counts(ROOT / "external" / "ross_island_v2_frozen_counts.csv")
    x = MOD.build(counts)
    matched = x["matched_branch"]

    assert matched["eligible_recovery_years"] == [2002, 2004]
    assert [(p["decline_year"], p["recovery_year"]) for p in matched["pairs"]] == [
        (1997, 2002),
        (1985, 2004),
    ]
    assert all(p["E3_fraction_difference"] < 0 for p in matched["pairs"])
    assert all(p["E6_fraction_difference"] < 0 for p in matched["pairs"])
