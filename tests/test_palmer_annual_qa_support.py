"""Offline guards for fixed-positions, pre/post annual Landsat QA support."""
import importlib.util
from pathlib import Path

SCRIPT = (Path(__file__).resolve().parents[1] /
          "research/climate-penguin/work/abandonment/palmer_annual_qa_support.py")
s = importlib.util.spec_from_file_location("palmer_annual_qa", SCRIPT)
mod = importlib.util.module_from_spec(s)
s.loader.exec_module(mod)


def test_landsat_qa_bits_and_single_grid_definition():
    assert len(mod.OFFSETS_M) == 5
    assert mod.SITES == ("LITC", "HUMB", "TORG")
    assert mod.LAST_POSITIVE_IMAGE_YEAR + 1 == mod.FIRST_ZERO_IMAGE_YEAR
    assert mod.qa_clear_nonwater_nonsnow(0, "LANDSAT_7")
    assert mod.qa_clear_nonwater_nonsnow(1 << 6, "LANDSAT_7")
    for bit in mod.BAD_LANDSAT_QA_BITS:
        assert not mod.qa_clear_nonwater_nonsnow(1 << bit, "LANDSAT_7")


def test_same_positions_require_three_distinct_years_on_both_sides():
    rows = []
    for site in mod.SITES:
        for year, mask in [(2005, 1), (2006, 1), (2007, 3),
                           (2008, 0), (2009, 1), (2010, 2), (2012, 1)]:
            rows.append({
                "site_id": site, "image_year": year,
                "clear_25_bit_mask": mask, "clear_positions_union": mod.popcount(mask),
                "candidate_scene_count": 1, "failed_qa_reads": 0, "catalog_status": "ok",
            })
    d = mod.temporal_support(rows)
    assert d["LITC"]["pre_summers_with_any_clear_fixed_position"] == 3
    assert d["LITC"]["post_summers_with_any_clear_fixed_position"] == 3
    assert d["LITC"]["same_fixed_positions_with_3_pre_and_3_post_clear_summers"] == 0
    # A repeated position on 3 post years genuinely passes, unlike scene counts.
    for r in rows:
        if r["image_year"] == 2010:
            r["clear_25_bit_mask"] = 1
    d = mod.temporal_support(rows)
    assert d["LITC"]["same_fixed_positions_with_3_pre_and_3_post_clear_summers"] == 1


def test_read_errors_cannot_become_no_scenes():
    rows = [{
        "site_id": site, "image_year": 2008,
        "clear_25_bit_mask": 0, "clear_positions_union": 0,
        "candidate_scene_count": 1, "failed_qa_reads": 1, "catalog_status": "ok",
    } for site in mod.SITES]
    d = mod.temporal_support(rows)
    assert d["LITC"]["post_years_failed_original_qa_read"] == 1
    assert d["LITC"]["post_years_without_catalog_scenes"] == 0


if __name__ == "__main__":
    test_landsat_qa_bits_and_single_grid_definition()
    test_same_positions_require_three_distinct_years_on_both_sides()
    test_read_errors_cannot_become_no_scenes()
    print("PASS three annual QA feasibility guards")
