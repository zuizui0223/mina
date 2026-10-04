import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "results" / "PAPER2D_FIRST_REAL_DYNAMIC_OUTCOME_RECEIPT_V1.json"


def test_no_species_passes_holm_flag_matches_values():
    x = json.loads(RECEIPT.read_text(encoding="utf-8"))
    holm = [x["primary_p50"][sp]["holm_p"] for sp in ("ADPE", "CHPE", "GEPE")]
    assert x["decision"]["no_species_passes_holm"] is all(p > 0.05 for p in holm)
