"""Synthetic fixtures only; original 2024 SAR data are read by source-pinned CI."""
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).resolve().parents[1]/"scripts/audit_sar2024_six_colony_static_site_georeference_v1.py"
spec=importlib.util.spec_from_file_location("sar2024",PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def synthetic_rows():
    static=[]
    for i,(sar,orig) in enumerate(m.SITES.items()):
        static.append({"site_name":orig,"lat":str(-70-i),"lon":str(10+i)})
    observed=[]
    positive_counts=[9,7,11,10,11,6]
    for i,((sar,_),n) in enumerate(zip(m.SITES.items(),positive_counts)):
        for j in range(n):
            observed.append({"colony":sar,"yyyymmdd":"9/05/2024",
                             "areasum":"500","ycoordmean":str(-70-i),"xcoordmean":str(10+i)})
    for _ in range(10):
        observed.append({"colony":"Atka Bay","yyyymmdd":"11/03/2024",
                         "areasum":"0","ycoordmean":"NA","xcoordmean":"NA"})
    return static,observed


def test_synthetic_six_sites_are_not_interpreted_as_absences():
    a,b=synthetic_rows()
    result=m.calculate(a,b)
    assert result["n_colonies"]==6
    assert result["sar_scene_total"]==64
    assert result["sar_scene_positive_centroid_eligible"]==54
    assert result["zero_area_or_not_detected_sar_rows_EXCLUDED_not_absence"]==10
    assert result["pooled_sar_scene_centroids_outside_threshold"]["3"]==0
    assert result["overall_max_km"]==0
    assert result["never_equate_cross_publication_distance_to_true_ledda_movement"]
    assert not result["new_penguin_causal_or_breeding_success_effect_identified"]


def test_2014_scene_georef_displacement_recovers_independent_distance():
    a,b=synthetic_rows()
    b[0]["ycoordmean"]=str(-70+0.045)  # about 5 km north of original site
    r=m.calculate(a,b)
    assert r["pooled_sar_scene_centroids_outside_threshold"]["3"]==1
    assert r["overall_max_km"]>4
    assert r["ledda_cross_publication_distance_divided_by_largest_2024_sample_distance"]>2


def test_unknown_site_bad_year_and_invalid_coordinates_stop():
    for field,value in [
        ("colony","Unknown"),
        ("yyyymmdd","9/05/2025"),
        ("areasum","-1"),
        ("ycoordmean","-95"),
    ]:
        a,b=synthetic_rows()
        b[0][field]=value
        with pytest.raises(ValueError):
            m.calculate(a,b)


def test_missing_positive_centroids_not_accepted_as_zero_area():
    a,b=synthetic_rows()
    b[0]["xcoordmean"]="NA"
    with pytest.raises(ValueError):
        m.calculate(a,b)


def test_static_site_approximation_not_a_breeding_success_variable():
    a,b=synthetic_rows()
    a[0]["lon"]="1000"
    with pytest.raises(ValueError):
        m.calculate(a,b)
