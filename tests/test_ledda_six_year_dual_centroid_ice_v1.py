"""Schema and causal-stop tests on synthetic stand-ins for the source receipts."""
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).resolve().parents[1]/"scripts/synthesize_ledda_six_year_dual_centroid_ice_v1.py"
spec=importlib.util.spec_from_file_location("ledda_sixy",PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def _site(n,last,max_run,periods,trailing):
    return {
        "n_preimage_15day_composites":periods,
        "n_composites_with_any_class4":n,
        "longest_consecutive_composites_any_class4":max_run,
        "trailing_composites_no_class4":trailing,
        "last_fully_preimage":{
            "class4_pixels":last,
            "valid_pixels":28 if last in (0,27) else 30,
            "composite_start_yyyymmdd":"20091001",
            "composite_end_yyyymmdd":"20091015",
        }
    }


def _historical(y,left,right):
    return {
        "year":y,"status":"EXPLORATORY_HISTORIC_INDEPENDENT_PHYSICAL_GRID_READ",
        "source_image":{"image_date":m.BIOLOGICAL_SOURCE[y][2]},
        "preimage_physical_by_site_and_radius":{
            "LaRue_original":{"3":_site(*left)},
            "Fretwell_alternative":{"3":_site(*right)}
        }
    }


def _paired(y,p_last,s_last,p_run,s_run,p_num,s_num,n):
    def x(last,denom):
        return {"original_LaRue_class4_cells":p_last,"original_LaRue_n_cells":28,
                "alternative_Fretwell_class4_cells":s_last,"alternative_Fretwell_n_cells":30,
                "composite_start_yyyymmdd":20140829}
    last=x(p_last,s_last)
    lag={"original_LaRue_class4_cells":0,"original_LaRue_n_cells":28,
         "alternative_Fretwell_class4_cells":30 if y==2014 else 0,
         "alternative_Fretwell_n_cells":30}
    return {
        "year":y,
        "original":{"status":"EXPLORATORY_INDEPENDENT_FASTICE_GRID_EXTRACTED"},
        "alternative":{"status":"ALTERNATIVE_PUBLISHED_CENTROID_ICE_PIXEL_CONTEXT_READ"},
        "trajectory_by_radius":{"3":{
            "n_preimage_composites":n,
            "last_completed_preimage_composite":last,
            "one_extra_15day_ahead_auxiliary_guard_composite":lag,
            "temporal_state_counts":{
                "both_class4_any":2 if y==2011 else 3,
                "only_original_class4_any":0,
                "only_alternative_class4_any":0 if y==2011 else 2,
                "neither_class4_any":7 if y==2011 else 6,
            },
            "original_site":{"number_composites_any_class4":p_num,
                             "longest_consecutive_class4_composites":p_run,
                             "trailing_consecutive_no_class4_composites":4 if y==2011 else 3},
            "alternative_site":{"number_composites_any_class4":s_num,
                             "longest_consecutive_class4_composites":s_run,
                             "trailing_consecutive_no_class4_composites":4 if y==2011 else 0},
        }}
    }


def reports():
    historic={"decision":"EXPLORATORY_PHYSICAL_ANCHOR_SERIES_AVAILABLE_ONLY",
              "all_years_read":True,
              "year_results":[
                _historical(2009,(1,0,1,11,6),(2,0,1,11,4)),
                _historical(2010,(4,27,4,10,0),(5,30,4,10,0)),
                _historical(2012,(2,0,1,10,1),(3,0,2,10,1)),
                _historical(2013,(3,0,1,14,4),(3,0,1,14,4))
            ]}
    pair={"status":"PAIRED_PREIMAGE_PHYSICAL_TRAJECTORIES_EXTRACTED_NOT_BREEDING_HABITABILITY",
          "year_results":[
              _paired(2011,0,0,1,1,2,2,9),
              _paired(2014,0,30,2,2,3,5,11),
          ]}
    return pair,historic


def test_synthetic_complete_six_year_clocks_and_stage_guard():
    p,h=reports()
    out=m.synthesize(p,h)
    assert out["years"]==[2009,2010,2011,2012,2013,2014]
    assert out["status"]=="COMPLETE_DESCRIPTIVE_TWO_CENTROID_SIX_YEAR_ICE_CROSSWALK"
    assert out["physical_source_checks"]["2014_last_both_centers_disagree_on_class4"]
    assert out["physical_source_checks"]["2014_lag_one_additional_interval_still_class4_discordant"]
    assert out["physical_source_checks"]["2014_3km_class4_secondary_dominance_without_complementarity"]
    assert out["physical_source_checks"]["2013_late_november_positive_without_preceding_class4_at_both_centers"]
    assert out["physical_source_checks"]["strict_all_preimage_intervals_class4_at_either_point_for_any_raw_yes_year"] is False
    assert not out["causal_effect_estimated"]
    assert not out["new_breeding_success_data_opened"]
    assert not out["actual_2014_nesting_polygon_identified"]


def test_missing_year_and_bad_physical_histogram_are_fail_closed():
    p,h=reports()
    h["year_results"].pop()
    with pytest.raises(ValueError,match="six"):
        m.synthesize(p,h)
    p,h=reports()
    h["year_results"][0]["preimage_physical_by_site_and_radius"]["LaRue_original"]["3"]["last_fully_preimage"]["class4_pixels"]=35
    with pytest.raises(ValueError,match="Invalid physical"):
        m.synthesize(p,h)


def test_duplicate_year_or_incomplete_source_is_stopped():
    p,h=reports()
    h["year_results"][3]["year"]=2009
    with pytest.raises(ValueError):
        m.synthesize(p,h)
    p,h=reports()
    p["year_results"][0]["original"]["status"]="HOLD"
    with pytest.raises(ValueError):
        m.synthesize(p,h)
