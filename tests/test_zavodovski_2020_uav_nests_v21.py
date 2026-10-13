"""Source-free fixtures: do not represent penguin field data."""
import sys
from pathlib import Path
import pytest
pytest.importorskip("requests")
pytest.importorskip("shapely")
pytest.importorskip("shapefile")
pytest.importorskip("pyproj")
from shapely.geometry import Point, box
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import validate_zavodovski_2020_uav_nests_v21 as m


def test_actual_source_year_2022_chinstrap_not_read():
    assert len(m.UAV_FILES)==2
    assert all("2020" in z for z in m.UAV_FILES)
    assert not any("2022" in z or "Chinstrap" in z for z in m.UAV_FILES)


def test_lat_lon_4326_to_projected_points_with_duplicate_QA():
    rows=[
        {"nest_number":"1","lat":"-56.30","lon":"-27.58"},
        {"nest_number":"2","lat":"-56.30","lon":"-27.58"},
        {"nest_number":"3","lat":"-56.31","lon":"-27.59"},
    ]
    pts, qa=m.transform_nests(rows)
    assert len(pts)==3
    assert qa["exact_duplicate_coordinate_rows"]==1
    assert qa["unique_exact_latlon_pairs"]==2
    assert all(100000 < p.x < 900000 for p in pts)
    assert all(2500000 < p.y < 5500000 for p in pts)


def test_wrong_year_or_oceanic_coordinate_is_a_hard_stop():
    with pytest.raises(ValueError, match="POINT_STOP"):
        m.transform_nests([{"nest_number":"1","lat":"-57.10","lon":"-27.58"}])


def test_nested_prepared_polygon_count_does_not_pseudoreplicate_repeated_points():
    inside=Point(1,1)
    pts=[inside,inside,Point(2,1),Point(10,10)]
    stat=m.count_locations(pts,box(0,0,3,3))
    assert stat["original_point_rows_with_center_inside"]==3
    assert stat["unique_exact_projected_coordinate_points"]==2
    assert stat["occupied_5m_grid_cells"]==1
    assert stat["no_pseudoreplicate_independence_claim"]


def test_pseudo_2020_macro_positive_and_mixed_source_separated():
    fake={"Macaroni":[Point(1,1),Point(2,1)],"Mixed_source_ambiguous":[Point(1,1),Point(3,3)]}
    qc={"Macaroni":{"rows":2},"Mixed_source_ambiguous":{"rows":2}}
    cores={0:box(0,0,2.5,2.5),1:box(0,0,2,2),2:box(0,0,1.5,1.5),5:box(0,0,.5,.5)}
    main={ (2016,"macaroni"):box(0,0,4,4)}
    res=m.summarize(fake,qc,cores,box(10,10,12,12),main,
                    box(0,0,10,10),box(0,0,10,10))
    assert res["independent_2020_mac_nest_hits_strict_0m"]==2
    assert res["independent_2020_mac_nest_hits_strict_5m"]==0
    assert res["species_nest_points"]["Mixed_source_ambiguous"]["n_original_rows"]==2
    assert res["species_nest_points"]["Macaroni"]["n_original_rows"]==2


def test_georeference_quality_gate_rejects_outside_points():
    data={"Macaroni":[Point(10000,10000),Point(20000,20000)]}
    with pytest.raises(ValueError,match="GEOREFERENCE_STOP"):
        m.summarize(data,{"Macaroni":{}},
                    {0:box(0,0,2,2)},box(0,0,2,2),
                    {(2016,"macaroni"):box(0,0,2,2)},
                    box(0,0,2,2),box(0,0,2,2))
