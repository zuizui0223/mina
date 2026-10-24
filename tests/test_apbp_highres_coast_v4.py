"""Synthetic coastline/uncertainty contrasts, never artificial biological outcomes."""
import io
import sys
from pathlib import Path
import zipfile
import pytest
pytest.importorskip("requests")
pytest.importorskip("shapely")
pytest.importorskip("shapefile")
pytest.importorskip("pyproj")
from shapely.geometry import Point,box
from pyproj import CRS
import shapefile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import validate_apbp_highres_coast_v4 as v


def at(x,y,unc=25):
    return {"x":x,"y":y,"uncertainty_m":unc,"locality":"fictional","source_islandGroup":"fictional"}


def test_finer_land_map_recovers_islet_not_medium_and_cannot_count_it_as_mainland():
    medium=[(0,box(0,0,100,100),{"surface":"land"})]
    high=[*medium,(1,box(2000,2000,2030,2030),{"surface":"land"})]
    sites={"fakeTinyIsland":[at(2015,2015)]}
    result=v.compare_site_maps(sites,medium,high)[0]
    assert result["medium_class"]=="HOLD_UNMATCHED"
    assert result["high_class"]=="ISLAND_SEPARATE_LAND_POLYGON_PROXY"
    assert result["formerly_unmatched_and_rescued"] is True
    assert result["high_location_confidence"]=="HOLD_POSITION_RADIUS_CROSSES_LAND_BOUNDARY"


def test_island_georeference_buffer_stable_only_when_whole_uncertainty_disk_in_polygon():
    land=box(0,0,1000,1000)
    assert v.location_quality(Point(500,500),land,"EXACT_ONE_LAND_POLYGON",100).startswith("ISLAND_OR_CONTINENT_ASSIGNMENT_STABLE")
    assert v.location_quality(Point(5,500),land,"EXACT_ONE_LAND_POLYGON",100)=="HOLD_POSITION_RADIUS_CROSSES_LAND_BOUNDARY"
    assert v.location_quality(Point(500,500),land,"EXACT_ONE_LAND_POLYGON",None)=="HOLD_PRECISION_MISSING"
    assert v.location_quality(Point(500,500),land,"NEAR_LAND_WITHIN_250M_ONLY",100)=="HOLD_NOT_EXACT_LAND_POINT"


def test_one_site_with_repeated_gps_more_than_1km_not_assigned():
    land=[(0,box(0,0,10000,10000),{"surface":"land"})]
    values=v.compare_site_maps({"notsame":[at(100,100),at(3000,100)]},land,land)[0]
    assert values["high_status"]=="HOLD_SOURCE_COORDINATE_DRIFT"
    assert values["high_original_feature_id"] is None


def test_cross_version_classification_disagreement_is_reported():
    medium=[(0,box(0,0,2000,2000),{"surface":"land"})]
    high=[(0,box(-100,-100,100,100),{"surface":"land"}),
          (1,box(300,300,2000,2000),{"surface":"land"})]
    values=v.compare_site_maps({"site":[at(500,500,50)]},medium,high)[0]
    assert values["medium_class"]=="CONTINENT_LARGEST_POLYGON_PROXY"
    assert values["high_class"]=="CONTINENT_LARGEST_POLYGON_PROXY"
    assert values["medium_to_high_class_disagreement"] is False


def test_publisher_highres_zip_extract_shp_and_reject_non_3031_crs(tmp_path):
    def zip_original(crs):
        base=tmp_path/"source"
        base.mkdir(exist_ok=True)
        file=base/"land.shp"
        writer=shapefile.Writer(str(file),shapeType=shapefile.POLYGON)
        writer.field("surface","C",size=25)
        writer.poly([[(0,0),(0,100),(100,100),(100,0),(0,0)]])
        writer.record("land")
        writer.poly([[(200,200),(200,300),(300,300),(300,200),(200,200)]])
        writer.record("ice shelf")
        writer.close()
        file.with_suffix(".prj").write_text(CRS.from_epsg(crs).to_wkt())
        b=io.BytesIO()
        with zipfile.ZipFile(b,"w",zipfile.ZIP_DEFLATED) as z:
            for suf in (".shp",".shx",".dbf",".prj"):
                z.write(file.with_suffix(suf),arcname="folder/land"+suf)
        return b.getvalue()
    sample={"A":[at(50,50)]}
    land,meta=v.original_highres_shapes(zip_original(3031),tmp_path/"good",sample)
    assert len(land)==1
    assert land[0][1].area==10000
    assert meta["original_surface_counts"]["ice shelf"]==1
    with pytest.raises(ValueError,match="EPSG:3031"):
        v.original_highres_shapes(zip_original(4326),tmp_path/"wrong",sample)


def test_original_highres_rejects_path_traversal(tmp_path):
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("meta.txt",b"fake")
        z.writestr("../evil.txt",b"malicious")
    with pytest.raises(ValueError,match="unsafe"):
        v.original_highres_shapes(b.getvalue(),tmp_path/"target",{})


def test_study_recovery_summary_contains_no_fitted_effect():
    mid=[(0,box(0,0,100,100),{"surface":"land"})]
    rows=v.compare_site_maps({"A":[at(50,50,10)]},mid,mid)
    report=v.summarise(rows,"fake-medium","fake-high",{}, {})
    assert report["no_ecological_effects_fitted"] is True
    assert report["n_formerly_unmatched_rescued"] == 0
    assert report["n_source_locationIDs"] == 1
    assert report["high_polygon_match_precision"]["ISLAND_OR_CONTINENT_ASSIGNMENT_STABLE_UNDER_REPORTED_POSITION_RADIUS"]==1
