"""Unit QA for AADC × independent Antarctic Ecosystem Inventory source atlas."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_aadc_aei_independent_habitat_v3 import (
    source_circle_values,summarize_habitat,geographic_summary,
    ANIMAL_DERIVED_TERMS,RADIUS_M
)


def mapping():
    return {
        1:{"tier1":"land","tier2":"rocky","tier3":"rock",
           "animal_label_linked":False},
        2:{"tier1":"land","tier2":"snowy","tier3":"algae",
           "animal_label_linked":False},
        3:{"tier1":"land","tier2":"colonies","tier3":"E1B8 Penguin colonies",
           "animal_label_linked":True},
    }


def test_animal_based_raster_class_never_becomes_habitat_predictor():
    m=mapping()
    pixels=np.asarray([1,1,2,3,3],dtype=int)
    v=summarize_habitat(pixels,total=10,mapping=m,pixel_area_m2=10000)
    assert v["all_classified_icefree_pixel_count"]==5
    assert v["all_classified_mapped_icefree_area_projected_ha"]==5
    assert v["independent_nonanimal_mapped_pixel_count"]==3
    assert v["outcome_label_linked_pixels_excluded"]==2
    assert v["nonanimal_tier2_habitat_richness"]==2
    assert 0<v["nonanimal_tier2_habitat_shannon"]<1
    assert v["independently_mapped_habitat_coverage"] is True


def test_all_animal_class_or_unmapped_is_missing_not_ecological_zero():
    m=mapping()
    for values in (np.asarray([3,3],dtype=int),np.asarray([],dtype=int)):
        v=summarize_habitat(values,total=10,mapping=m,pixel_area_m2=10000)
        assert v["nonanimal_tier2_habitat_richness"] is None
        assert v["nonanimal_mapped_icefree_area_projected_ha"] is None
        assert v["independently_mapped_habitat_coverage"] is False


def test_raster_pixel_circle_not_square_and_mask_stays_masked():
    arr=np.ones((7,7),dtype=np.int16)
    arr[3,3]=0
    with MemoryFile() as mem:
        with mem.open(driver="GTiff",height=7,width=7,count=1,
                      dtype="int16",crs="EPSG:3031",
                      transform=from_origin(-350,350,100,100),
                      nodata=0) as ds:
            ds.write(arr,1)
            circle,values=source_circle_values(ds,0,0,radius=250)
            assert 0<circle<49
            assert len(values)==circle-1
            assert np.all(values==1)


def test_unknown_class_stops_instead_of_silent_coercion():
    try:
        summarize_habitat(np.asarray([777]),1,mapping(),10000)
    except ValueError as e:
        assert "SOURCE_STOP" in str(e)
    else:
        raise AssertionError("original unknown raster class must be rejected")


def test_distribution_separates_source_classes_and_map_editions():
    a={"source_geographic_class":"island","original_geographic_site_id_in_2021":True,
       "all_classified_icefree_pixel_count":10,
       "all_classified_mapped_icefree_fraction":.5,
       "independently_mapped_habitat_coverage":True,
       "nonanimal_mapped_icefree_area_projected_ha":8,
       "nonanimal_tier2_habitat_richness":3,
       "nonanimal_tier2_habitat_shannon":0.8}
    b={"source_geographic_class":"continent","original_geographic_site_id_in_2021":False,
       "all_classified_icefree_pixel_count":0,
       "all_classified_mapped_icefree_fraction":0,
       "independently_mapped_habitat_coverage":False,
       "nonanimal_mapped_icefree_area_projected_ha":None,
       "nonanimal_tier2_habitat_richness":None,
       "nonanimal_tier2_habitat_shannon":None}
    result=geographic_summary([a,b])
    assert result["all_2025"]["original_geographic_sites"]==2
    assert result["all_2025"]["sites_with_nonanimal_mapped_habitat_pixels"]==1
    assert result["source_class_island"]["nonanimal_tier2_richness"]["median"]==3
    assert result["source_class_continent"]["nonanimal_tier2_richness"]["median"] is None
    assert result["shared_with_2021_source_ids"]["original_geographic_sites"]==1
    assert result["new_only_in_2025_source_ids"]["original_geographic_sites"]==1
