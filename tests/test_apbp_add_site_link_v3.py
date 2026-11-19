"""Fictional Antarctic GIS only; no real island effect or biological slope."""
import io
import sys
from pathlib import Path
import zipfile

import pytest
pytest.importorskip("requests")
pytest.importorskip("shapely")
pytest.importorskip("shapefile")
pytest.importorskip("pyproj")

from pyproj import CRS
from shapely.geometry import box,Point
from shapely.strtree import STRtree
import shapefile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import link_apbp_to_add_island_rock_v3 as m


def _land():
    return [(0,box(0,0,100,100),{"surface":"land"}),
            (1,box(500,500,520,520),{"surface":"land"})]


def _one(x,y,lat=-62,lon=-60,uncert=30):
    return {"x":x,"y":y,"lat":lat,"lon":lon,"uncertainty_m":uncert,
            "locality":"invented","source_islandGroup":"name is not classification"}


def test_independent_geom_not_name_classifies_island_vs_mainland():
    land=_land()
    rock=[(0,box(1,1,3,3),{}),(1,box(505,505,510,510),{})]
    sites={"name_contains_Island_but_mainland":[_one(2,2)],
           "bare_site_name_but_island":[_one(510,510)]}
    x=m.link_sites(sites,land,rock)
    by={r["original_locationID"]:r for r in x}
    assert by["name_contains_Island_but_mainland"]["provisional_land_type"]=="CONTINENT_LARGEST_POLYGON_PROXY"
    assert by["bare_site_name_but_island"]["provisional_land_type"]=="ISLAND_SEPARATE_LAND_POLYGON_PROXY"
    assert by["bare_site_name_but_island"]["rock_500m_mapped_km2"]>0
    assert all(r["rock_2000m_mapped_km2"]>=r["rock_500m_mapped_km2"] for r in x)


def test_unmapped_micro_island_is_HOLD_not_mainland_zero():
    land=_land()
    rock=[(0,box(1000,1000,1003,1003),{})]
    sites={"micro_islet_missing_from_2026_medium_map":[_one(1000,1000)]}
    x=m.link_sites(sites,land,rock)[0]
    assert x["source_link_status"]=="HOLD_UNMATCHED_MEDIUM_COASTLINE"
    assert x["provisional_land_type"]=="HOLD_UNMATCHED"
    assert x["rock_2000m_mapped_km2"] is None


def test_coordinate_drift_cannot_force_to_one_polygon():
    land=_land()
    rock=[(0,box(2,2,3,3),{})]
    sites={"malformed_multiyear_GPS":[_one(10,10),_one(2000,10)]}
    x=m.link_sites(sites,land,rock)[0]
    assert x["source_link_status"]=="HOLD_COORDINATE_DRIFT_ABOVE_1000M"
    assert x["land_polygon_id"] is None


def test_ambiguous_adjacent_island_polygons_not_arbitrarily_assigned():
    land=[(0,box(0,0,100,100),{}),(1,box(95,95,200,200),{})]
    t=STRtree([z[1] for z in land])
    pos,status=m.unique_match(Point(97,97),land,t)
    assert pos is None
    assert "AMBIGUOUS" in status


def test_overlapping_rock_geometries_are_unioned_not_doublecounted():
    land=box(0,0,5000,5000)
    rocks=[(0,box(100,100,200,200),{}),(1,box(150,150,250,250),{})]
    query=Point(180,180)
    a=m.rock_near_site(query,land,rocks,STRtree([g[1] for g in rocks]))
    assert abs(a[500]-17500)<1e-3
    assert a[2000]>=a[500]


def test_publisher_original_source_zip_requires_crs(tmp_path):
    path=tmp_path/"coast.shp"
    writer=shapefile.Writer(str(path),shapeType=shapefile.POLYGON)
    writer.field("surface","C",size=20)
    writer.poly([[(0,0),(0,100),(100,100),(100,0),(0,0)]])
    writer.record("land")
    writer.close()
    path.with_suffix(".prj").write_text(CRS.from_epsg(3031).to_wkt())
    blob=io.BytesIO()
    with zipfile.ZipFile(blob,"w") as archive:
        for ext in (".shp",".shx",".dbf",".prj"):
            archive.write(path.with_suffix(ext),arcname="folder/coast"+ext)
    decoded=m.unpack_shapefile(blob.getvalue(),tmp_path/"unpacked")
    land,meta=m.mapped_features(decoded,require_surface=True)
    assert len(land)==1
    assert land[0][1].area==10000
    assert meta["retained_valid_features"]==1


def test_original_gis_zip_rejects_directory_traversal(tmp_path):
    blob=io.BytesIO()
    with zipfile.ZipFile(blob,"w") as archive:
        archive.writestr("../attacker",b"bad")
    with pytest.raises(ValueError,match="unsafe"):
        m.unpack_shapefile(blob.getvalue(),tmp_path/"unsafe")


def test_original_island_model_not_fitted():
    s=m.summarize([],{"original_field_names":[]},{"original_field_names":[]},"sha-coast","sha-rock")
    assert s["ecological_effect_models_fitted"]==0
    assert s["n_site_ids"]==0
