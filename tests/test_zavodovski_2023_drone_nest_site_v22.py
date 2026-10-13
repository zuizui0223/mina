"""Fabricated GIS shapes only, no authentic penguin nest points."""
import sys
from pathlib import Path
import pytest
pytest.importorskip("requests")
pytest.importorskip("shapely")
pytest.importorskip("shapefile")
pytest.importorskip("pyproj")
import shapefile
from pyproj import CRS
from shapely.geometry import Point, box, GeometryCollection
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import validate_zavodovski_2023_drone_nest_site_v22 as v


def synthetic_baseline():
    c0=box(0,0,4,4)
    c1=box(2,0,4,4)
    m0=box(10,0,12,2)
    m1=box(0,0,2,4).union(m0)
    direct={
        (2011,"chinstrap"):c0, (2016,"chinstrap"):c1,
        (2011,"macaroni"):m0, (2016,"macaroni"):m1,
        (2011,"cloud"):GeometryCollection(),
        (2016,"cloud"):GeometryCollection()
    }
    hist={"CHPE":c0,"MCPE":m0,"MIXED":box(5,5,6,6)}
    cores={0:box(0,0,2,4),1:box(.5,.5,1.5,3.5),2:box(.75,1,1.25,3),5:box(.9,1.5,1.1,2.5)}
    return direct,hist,cores


def test_only_2023_real_drone_species_sources_no_2025_infill():
    assert all("2023" in name for name in v.GEO_LAYERS)
    assert not any("chinstrap_outwith_drone_area_2025" in name for name in v.GEO_LAYERS)
    assert len(v.NEST_SOURCES)==2


def test_clip_survey_excludes_unobserved_sector_and_persistent_control():
    direct,hist,cores=synthetic_baseline()
    survey=box(0,0,15,10).difference(box(0,0,1,4))
    targets=v.clip_survey(cores,direct,hist,survey)
    assert targets["T_0m"].area==4
    assert targets["Q_persistent_Macaroni"].area==4
    assert targets["P_consensus_persistent_Chinstrap"].area==8
    assert not targets["T_0m"].contains(Point(.5,2))


def test_original_drone_source_point_shapefile_and_epsg(tmp_path):
    p=tmp_path/"macaroni_nest_points_2023.shp"
    writer=shapefile.Writer(str(p),shapeType=shapefile.POINT)
    writer.field("ID","N",size=8)
    writer.point(464000,3761000);writer.record(1)
    writer.point(464010,3761010);writer.record(2)
    writer.close()
    p.with_suffix(".prj").write_text(CRS.from_epsg(32726).to_wkt())
    points,quality=v.audited_points(p)
    assert len(points)==2
    assert quality["distinct_exact_coordinates"]==2
    assert quality["original_source_point_rows"]==2


def test_point_out_of_bounding_range_fails(tmp_path):
    p=tmp_path/"chinstrap_nest_points_2023.shp"
    writer=shapefile.Writer(str(p),shapeType=shapefile.POINT)
    writer.field("ID","N",size=8)
    writer.point(400000,3761000);writer.record(1)
    writer.close()
    p.with_suffix(".prj").write_text(CRS.from_epsg(32726).to_wkt())
    with pytest.raises(ValueError,match="Zavodovski UTM window"):
        v.audited_points(p)


def test_species_labels_separate_and_surveyed_region_point_counts():
    direct,hist,cores=synthetic_baseline()
    surveys={
        v.COAST_BASENAME:box(0,0,15,10),
        "area_outwith_drone_survey_2023":box(0,0,1,4),
        "macaroni_colony_boundaries_2023":box(0,0,2,4).union(box(10,0,12,2)),
        "chinstrap_colony_boundaries_2023":box(2,0,4,4),
    }
    pts={
        "Macaroni":[Point(1.5,2),Point(10.5,1)],
        "Chinstrap":[Point(2.5,2),Point(3,3)]
    }
    qa={"Macaroni":{"original_source_point_rows":2},"Chinstrap":{"original_source_point_rows":2}}
    result=v.analyze_counts(pts,qa,cores,surveys,direct,hist)
    assert result["2023_mac_nest_points_in_V18_T0"]==1
    assert result["2023_chinstrap_nest_points_in_V18_T0"]==0
    assert result["evaluation_regions"]["T_0m"]["area_m2"]==4
    assert result["evaluation_regions"]["Q_persistent_Macaroni"]["Macaroni_2023_nest_point_rows"]==1
    assert result["fraction_V18_T_observed_by_2023_survey"]["0"]==0.5


def test_species_location_qc_stops_false_source_registration():
    direct,hist,cores=synthetic_baseline()
    surveys={
        v.COAST_BASENAME:box(0,0,15,10),
        "area_outwith_drone_survey_2023":box(20,20,21,21),
        "macaroni_colony_boundaries_2023":box(0,0,1,1),
        "chinstrap_colony_boundaries_2023":box(2,0,4,4),
    }
    pts={"Macaroni":[Point(10.5,1)],"Chinstrap":[Point(2.5,2)]}
    with pytest.raises(ValueError,match="below preread 90%"):
        v.analyze_counts(pts,{},cores,surveys,direct,hist)
