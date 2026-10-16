"""Check Ecology cover-letter claims against frozen scientific receipts.

Publication-only consistency check: no ecology endpoints or author approvals
are computed. Source citations and all-six-sites occupied facts stay separate.
"""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COVER=ROOT/"submission/COVER_LETTER_SPATIAL_RECOVERY_ECOLOGY_V0_6.md"


def test_editorial_claim_numbers_match_frozen_evidence():
    text=COVER.read_text(encoding="utf-8")
    ross=json.loads((ROOT/"results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json").read_text())
    grain=json.loads((ROOT/"results/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.json").read_text())
    f=ross["focal_episode"]
    percent=lambda x:f"{100*x:.2f}%"
    for expected in (
        percent(f["aggregate"]["aggregate_loss_restored_fraction"]),
        percent(grain["six_component"]["inverse_path_fidelity"]),
        percent(grain["three_colony"]["inverse_path_fidelity"]),
        f"{100*grain['six_component']['state_restoration_fraction']:.1f}%",
        f"{100*grain['three_colony']['state_restoration_fraction']:.1f}%",
        f"{100*f['composition_state']['baseline_rebound_TV']:.2f}%",
        f"{100*grain['three_colony']['baseline_rebound_TV']:.2f}%",
    ):
        assert expected in text, expected
    assert "10.8%" in text and "109.8%" in text
    assert "80.6%" in text and "51.8%" in text


def test_all_six_Ross_components_were_observed_positive():
    with (ROOT/"external/ross_island_v2_frozen_counts.csv").open(newline="") as file:
        rows={int(row["year"]):row for row in csv.DictReader(file)}
    assert all(all(int(count)>0 for col,count in rows[y].items() if col!="year")
               for y in (1999,2001,2002))
    letter=COVER.read_text(encoding="utf-8")
    assert "all six focal breeding components remained occupied" in letter
    assert "not a newly observed local extinction or recolonization event" in letter


def test_cover_letter_is_not_a_false_human_submission_confirmation():
    letter=COVER.read_text(encoding="utf-8")
    manifest=(ROOT/"submission/SPATIAL_RECOVERY_ECOLOGY_SUBMISSION_MANIFEST_V1.md").read_text()
    assert "COVER_LETTER_SPATIAL_RECOVERY_ECOLOGY_V0_6.md" in manifest
    assert "COVER_LETTER_SPATIAL_RECOVERY_ECOLOGY_V0_5.md" not in manifest
    assert "post-result" in letter
    assert "not a new resilience-theory claim" in letter
    assert "not under review elsewhere" in letter or "not published, submitted or under review elsewhere" in letter
    assert "[After author confirmation:" in letter
    assert "[Approved corresponding author's full publication name]" in letter
    assert "declining export" not in letter  # Old wording exceeded resighting evidence.
