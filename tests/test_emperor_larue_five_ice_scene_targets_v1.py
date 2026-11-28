"""Published site centroids + raw author scene dates, not site vacancies."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
R=json.loads((ROOT/"results/EMPEROR_LARUE_FIVE_PRE_SHOCK_ICE_SCENE_TARGETS_V1.json").read_text(encoding="utf8"))


def test_five_scene_checks_exact_dates():
    assert R["candidate_count"]==5
    k=[(x["site"],x["original_previous_scene_date"],x["original_next_scene_date"])
       for x in R["candidates"]]
    assert k==[
       ("AMUN","2010-10-08","2011-09-27"),
       ("LEDD","2009-10-27","2010-10-08"),
       ("LEDD","2012-10-22","2013-11-30"),
       ("MERT","2010-10-02","2011-10-11"),
       ("UMBE","2012-09-27","2013-10-12")
    ]


def test_target_scene_centroid_is_not_platform_access_or_destination():
    assert R["unresolved_extra_four_event_count"]==4
    assert "NOT actual dated ice-platform footprints" in R["coordinate_precision_warning"]
    assert all(not t["original_previous_scene_date"] is None
               for t in R["candidates"])
    assert R["cannot_interpret_five_as_founding_events"] is True
    assert R["no_new_bird_rows_opened"] is True
    assert R["new_causal_test_run"] is False
    assert len(R["required_new_independent_inputs"]) >= 5


def test_unresolved_model_positive_case_includes_absent_raw_image():
    unresolved={(r["site"],r["original_posterior_years"][1]):
                    (r["raw_previous_class"],r["raw_next_class"])
                for r in R["unresolved"]}
    assert unresolved[("AMUN",2013)] == ("no","NA")
    assert unresolved[("LAZA",2012)] == ("yes","yes")
    assert unresolved[("LEDD",2015)] == ("no","no")
    assert unresolved[("RUPE",2017)] == ("no","yes")
