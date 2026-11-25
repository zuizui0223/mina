"""Synthetic original-source checks for V50 flying giant petrel vs flightless penguins."""
from pathlib import Path
import sys
import pytest
from shapely.geometry import box

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import analyze_paper2_zavodovski_same_day_bird_coast_access_v50 as m


def sample():
    # These are fabricated local projected polygons, NOT observed ecology.
    coast=box(0,0,1000,1000)
    outside=box(900,0,1000,1000)
    survey=coast.difference(outside)
    petrel=box(350,350,650,650)
    chin=box(15,15,235,235)
    mac=box(0,260,210,480)
    return coast,survey,petrel,chin,mac


def test_frozen_2023_original_source_layers_5_and_no_new_year():
    assert len(m.LAYERS)==5
    assert "giant_petrel_colony_boundaries_2023" in m.LAYERS
    assert "area_outwith_drone_survey_2023" in m.LAYERS
    assert "zavodovski_coastline_2023" in m.LAYERS
    assert m.SOURCE_DATE=="2023-12-14"
    assert m.SAMPLE_GRID_M==(20,10,40)


def test_projected_shoreline_20m_grid_origin_and_difference():
    o=m.sample_grid_distances(*sample(),grid_m=20)
    a=o["coastline_distances_by_original_guild"]
    assert a["PETREL"]["source_occupied_utm_grid_centres"]>m.MIN_PETREL_PRIMARY_CELLS
    assert a["PENGUIN"]["source_occupied_utm_grid_centres"]>m.MIN_PENGUIN_PRIMARY_CELLS
    assert a["PETREL"]["coast_distance_m_median"]>a["PENGUIN"]["coast_distance_m_median"]
    assert o["source_grid_point_support"]["source_grid_no_colony_polygon"]>0
    assert o["original_country_or_species_independent_island_replicates"]==1


def test_original_area_mask_excludes_unsurveyed_2023_without_false_absences():
    coast,survey,petrel,chin,mac=sample()
    q=m.sample_grid_distances(coast,survey,petrel,chin,mac,grid_m=20)
    assert q["source_grid_point_support"]["source_survey_grid_cells"]<2500
    assert q["coastline_distances_by_original_guild"]["PENGUIN"]["coast_distance_m_q05"]>=0
    assert all(x["source_occupied_utm_grid_centres"]==0 or
               x["coast_distance_m_median"] is not None
               for x in q["coastline_distances_by_original_guild"].values())


def test_overlap_species_guild_area_never_dual_allocated():
    coast,survey,petrel,chin,mac=sample()
    petrel=box(100,100,550,550)
    q=m.sample_grid_distances(coast,survey,petrel,chin,mac,20)
    assert q["source_grid_point_support"]["source_grid_flying_and_penguin_polygon_overlap"]>0
    a=q["coastline_distances_by_original_guild"]
    assert a["PETREL"]["source_occupied_utm_grid_centres"]<(
         450*450//400)


def test_fixed_sampling_scale_and_first_party_url_enforcement():
    with pytest.raises(ValueError,match="UNFROZEN"):
        m.sample_grid_distances(*sample(),grid_m=25)
    with pytest.raises(ValueError,match="BAS"):
        m.source_download_url("https://example.com/source.shp")
    with pytest.raises(ValueError,match="CANONICAL"):
        m.public_get(None,"https://other.example.com/file.shp",1000)
