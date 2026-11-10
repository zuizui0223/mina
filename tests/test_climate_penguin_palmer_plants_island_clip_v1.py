"""Check island-exclusive map footprint clipping and don't equate zeros with absence."""
import importlib.util
from pathlib import Path
import pytest

pytest.importorskip("shapely")
from shapely.geometry import box
HERE=Path(__file__).resolve().parents[1]
SCRIPT=HERE/"research/climate-penguin/work/climate_penguin/audit_palmer_plants_original_land_clip_v1.py"

def load():
    sp=importlib.util.spec_from_file_location("plant_island_union",SCRIPT)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def test_source_clip_union_independent_real_islands():
    m=load()
    island={"A":box(0,0,10,10),"B":box(11,0,21,10)}
    src=[(0,"Vegetation",box(8,2,14,5)),(1,"Vegetation",box(9,2,12,5)),
         (2,"Lichen",box(0,0,2,3)),(3,"Snow Algae",box(12,0,13,2))]
    rows={r["site_id"]:r for r in m.geom_class_clips(island,src)}
    assert len(rows)==2
    assert rows["A"]["Vegetation_source_features_intersecting_island"]==2
    assert rows["B"]["Vegetation_source_features_intersecting_island"]==2
    assert rows["A"]["Vegetation_mapped_union_m2"]==6
    assert rows["B"]["Vegetation_mapped_union_m2"]==9
    assert rows["A"]["Lichen_mapped_union_m2"]==6
    assert rows["B"]["Lichen_mapped_union_m2"]==0
    assert rows["B"]["Snow_Algae_mapped_union_m2"]==2
    assert rows["A"]["zero_map_does_not_prove_true_vegetation_absence"]
    assert rows["B"]["zero_map_does_not_prove_true_vegetation_absence"]

def test_invalid_geometry_and_source_expectations():
    m=load()
    assert m.VEG_ZIP_SHA=="7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236"
    assert m.EXPECTED_FEATURES==87391
    assert m.FIGSHARE_ID==24745956
    assert m.EXPECTED_CLASSES=={"Vegetation","Lichen","Snow Algae"}
