"""Offline validation of Landsat C2L2 spectral-pilot conversion rules."""
import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/abandonment/palmer_january_spectral_probe.py"
s=importlib.util.spec_from_file_location("pilot",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def test_usgs_scaling_and_invalid_reflectance():
    assert m.surface_reflectance(0) is None
    assert m.surface_reflectance(7272) is None
    assert m.surface_reflectance(43637) is None
    assert abs(m.surface_reflectance(18639)-0.3125725)<1e-9
    assert m.spectral_index(None,0.3) is None
    assert m.spectral_index(0.0,0.3) is None
    assert abs(m.spectral_index(0.2,0.4)-1/3)<1e-12

def test_scene_fixed_before_reflectance_and_grid_positions():
    assert m.PAIR[2007] == "LE07_L2SR_218106_20070105_02_T2"
    assert m.PAIR[2008] == "LE07_L2SR_219105_20080115_02_T2"
    assert m.CLEAR_INDICES["LITC"] == [9,11,15,16,20,22,23]
    assert m.CLEAR_INDICES["TORG"] == [9,12,13]
    assert m.SOURCE_ARTIFACT_SHA256 == "bb386e7ca78d735b7395f5c99a617c7d3462da02258b70792b77156a8f791c62"

if __name__=="__main__":
    test_usgs_scaling_and_invalid_reflectance()
    test_scene_fixed_before_reflectance_and_grid_positions()
    print("PASS preselected QA source, scale and NDVI boundary checks")
