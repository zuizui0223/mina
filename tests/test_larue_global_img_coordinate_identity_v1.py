"""Synthetic author-source image coordinate identity audit."""
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).resolve().parents[1]/"scripts/audit_larue_global_img_coordinate_identity_v1.py"
spec=importlib.util.spec_from_file_location("global_img_coords",PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def synthetic():
    names=["LEDD","OTHER"]
    sites=[{"site_id":s,"site_name":s,"lat":str(-74 if s=="LEDD" else -70),
            "lon":str(-130 if s=="LEDD" else -10)} for s in names]
    rows=[]
    for i in range(599):
        s="LEDD" if i<10 else "OTHER"
        y=2009+i if i<10 else 2009+i%10
        v=sites[0 if s=="LEDD" else 1]
        rows.append({"site_id":s,"img_year":str(y),
                     "img_lat":v["lat"],"img_long":v["lon"]})
    return rows,sites


def test_static_image_latlon_cannot_establish_real_immobility():
    observations,sites=synthetic()
    z=m.audit(observations,sites)
    assert z["source_observations"]==599
    assert z["source_sites"]==2
    assert z["sites_all_nonzero_valid_image_coordinates_identical_to_static"]==2
    assert z["sites_with_multiple_distinct_valid_image_coord_pairs"]==0
    assert z["original_image_coord_field_classes"]["EXACTLY_SITE_STATIC_COORD"]==599
    assert z["Ledda_summary"]["n_original_images"]==10
    assert z["actual_satellite_scene_georeference_proven_by_these_fields"] is False
    assert z["real_colony_immobility_or_movement_inferred"] is False
    assert z["biological_causal_effect_fitted"] is False


def test_nonstatic_coord_is_not_declared_actual_scene_or_nest():
    obs,sites=synthetic()
    obs[10]["img_lat"]="-70.05"
    z=m.audit(obs,sites)
    assert z["sites_with_multiple_distinct_valid_image_coord_pairs"]==1
    assert z["sites_with_any_nonstatic_nonzero_image_coordinates"]==1
    assert z["actual_bird_or_guano_polygons_proven_by_these_fields"] is False


def test_source_missing_ambiguous_0_class_separate():
    obs,sites=synthetic()
    obs[11]["img_lat"]=""
    obs[12]["img_long"]="0"
    z=m.audit(obs,sites)
    assert z["original_image_coord_field_classes"]["MISSING_OR_INVALID_SOURCE_IMAGE_COORD"]==1
    assert z["original_image_coord_field_classes"]["VALID_RANGE_BUT_ZERO_AMBIGUOUS_IMAGE_COORD"]==1


def test_duplicate_static_site_fails_but_unmatched_source_record_is_preserved():
    a,b=synthetic()
    with pytest.raises(ValueError):
        m.audit(a,b+b[:1])
    a,b=synthetic()
    a[10]["site_id"]="BURT"
    out=m.audit(a,b)
    assert out["source_observations"]==599
    assert out["n_images_unmatched_static_lookup"]==1
    assert out["sites_in_image_source_but_not_static_lookup"]=={"BURT":1}
    assert out["original_image_coord_field_classes"]["SITE_NOT_IN_STATIC_LOOKUP"]==1
    assert not out["actual_bird_or_guano_polygons_proven_by_these_fields"]
