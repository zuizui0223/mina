"""Only geometric invented island shapes and dummy site points."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from shapely.geometry import Point,box
import audit_jncc_naturalearth_landmass_v31 as g

def test_source_polygon_area_classification():
    assert g.land_type(5)=="SMALL_OFFSHORE_LANDMASS"
    assert g.land_type(1000)=="SMALL_OFFSHORE_LANDMASS"
    assert g.land_type(50000)=="LARGE_LANDMASS"
    assert g.land_type(15000)=="INTERMEDIATE_LANDMASS"
    assert g.land_type(0.001)=="UNRESOLVED_OR_MICRO"

def test_adjoining_same_landmass_fragments_are_unioned_before_area():
    pieces=[box(-5,53,-4,54),box(-4,53,-3,54),box(-7,57,-6.9,57.1)]
    shapes,areas,metadata=g.geometric_components(pieces)
    assert len(shapes)==2
    assert metadata["original_source_fragment_count"]==3
    assert max(areas)>2*min(areas)

def test_point_distance_assign_requires_strict_unique_landmass():
    from shapely.geometry import box
    from shapely.ops import transform
    from pyproj import Transformer
    fn=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True).transform
    a=transform(fn,box(-5,53,-4,54))
    b=transform(fn,box(-7,53,-6,54))
    labeling,c=g.attach_points([a,b],[100,200],
                               {("site",1):(53.5,-4.5),
                                ("site",2):(53.5,-6.5),
                                ("site",3):(55,0)})
    assert labeling[("site",1)]["status"]=="INTERIOR"
    assert labeling[("site",2)]["status"]=="INTERIOR"
    assert labeling[("site",3)]["status"]=="UNRESOLVED"

def test_physical_coast_never_classifies_master_name():
    assert "Site" not in g.URLS["major_land"]
    assert g.SMALL_MAX_KM2==1000
    assert g.LARGE_MIN_KM2==50000
    assert g.MIN_SMALL_PANELS==20
