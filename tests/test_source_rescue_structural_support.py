"""No-data-leak regression tests for the source-capacity structural gate."""
import importlib.util
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "source_audit", ROOT / "scripts" / "audit_source_rescue_structural_support.py"
)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def test_published_table():
    v = AUDIT.published_beaufort()
    assert abs(v["main_area_2005_to_2010_change"] - 0.011176034494378762) < 1e-10
    assert abs(v["main_density_change"] - 0.20483981814968932) < 1e-10
    assert abs(
        v["if_eligible_cohort_grew_like_pairs_probability_ratio_must_be_less_than"]
        - 0.8208124215809285
    ) < 1e-10


def test_no_receiver_reoccupation():
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / "ross.csv"
        f.write_text(
            "year," + ",".join(AUDIT.ROSS_COLS) + "\n"
            + "2001,1,2,3,4,5,6\n"
            + "2002,2,3,4,5,6,7\n",
            encoding="utf-8",
        )
        result = AUDIT.audit_frozen_ross(f)
    assert result["colony_years"] == 6
    assert result["positive_colony_years"] == 6
    assert result["colony_zero_to_positive_observed_transitions"] == 0


def test_receiver_reoccupation_not_silent():
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / "ross.csv"
        f.write_text(
            "year," + ",".join(AUDIT.ROSS_COLS) + "\n"
            + "2001,0,2,3,4,5,6\n"
            + "2002,1,2,3,4,5,6\n",
            encoding="utf-8",
        )
        result = AUDIT.audit_frozen_ross(f)
    assert result["colony_zero_to_positive_observed_transitions"] == 1
