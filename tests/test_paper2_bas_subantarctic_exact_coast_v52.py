"""V52 source-first new official BAS 50-60S coastline ZIP tests (invented polygons)."""
import io
from pathlib import Path
import sys
import zipfile

import numpy as np
import pytest
import shapefile
from pyproj import CRS,Transformer
from shapely.geometry import box

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_paper2_bas_subantarctic_exact_coast_v52 as a


def fake_BAS_archive(include_thule=True):
    centers={
      "Saunders":(535000.,3592500.),
      "Bellingshausen":(495250.,3414580.),
      "Thule":(482000.,3411000.),
    }
    medians=dict(centers)
    trans=Transformer.from_crs(32726,3031,always_xy=True)
    files={ext:io.BytesIO() for ext in (".shp",".shx",".dbf")}
    with shapefile.Writer(shp=files[".shp"],shx=files[".shx"],dbf=files[".dbf"],
                          shapeType=shapefile.POLYGON) as writer:
        writer.field("ID","N",size=11)
        for i,(island,(x,y)) in enumerate(centers.items(),1):
            if island=="Thule" and not include_thule:continue
            # UTM-specified test square transformed into original EPSG3031.
            ring=[(x-800,y-800),(x-800,y+800),(x+800,y+800),
                  (x+800,y-800),(x-800,y-800)]
            outline=[list(trans.transform(xx,yy)) for xx,yy in ring]
            writer.poly([outline])
            writer.record(i)
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w") as arc:
        for ext,buf in files.items():
            arc.writestr("sub_antarctic_coastline_high_res_polygon_v1.0"+ext,buf.getvalue())
        arc.writestr("sub_antarctic_coastline_high_res_polygon_v1.0.prj",
                     CRS.from_epsg(3031).to_wkt())
    return out.getvalue(),medians


def fake_original_nest_rows():
    centers={
      "Ashen_Hills":(535000.,3592500.),
      "Bellingshausen":(495250.,3414580.),
      "Beach_Point":(482000.,3411000.),
      "Hewison_Point":(482000.,3411000.),
    }
    result={}
    for name,p in centers.items():
        # Irrelevant invented labels, geographic support only.
        xy=np.array([[p[0]+(i%7)*30-100,p[1]+(i//7)*30-100]
                     for i in range(110)],dtype=float)
        result[name]={"xy":xy}
    return result


def test_exact_original_public_publisher_url_and_doi():
    assert a.official_source_url_verified(a.URL)
    assert a.DOI=="10.5285/c1d83502-8799-4e3c-bdca-21db6a4405d4"
    with pytest.raises(ValueError,match="ORIGINAL_BAS_URL"):
        a.official_source_url_verified("http://ramadda.data.bas.ac.uk/other")
    with pytest.raises(ValueError,match="ENTRY_ID"):
        a.official_source_url_verified(
          "https://ramadda.data.bas.ac.uk/repository/entry/get/"
          "sub_antarctic_coastline_high_res_polygon_v1.0.zip?entryid=other")


def test_original_BAS_EPSG3031_exact_three_coasts_and_source_sha():
    data,medians=fake_BAS_archive()
    coast,meta=a.original_native_land_geometry(data,medians)
    assert len(coast)==3
    assert meta["original_source_native_crs_EPSG"]==3031
    assert meta["all_three_candidates_unique_containing_polygons"]
    assert meta["distinct_physical_publisher_polygon_ids"]==3
    assert len(meta["original_source_zip_SHA256"])==64
    source=a.source_sample_without_species_outcomes(fake_original_nest_rows(),coast)
    assert all(v["fraction_source_nests_inside"]==1 for v in source.values())
    assert a.science_gates(meta,source)["source_only_Paper2_Geography_gate_pass"]


def test_missing_real_physical_island_not_nearest_snapped():
    data,medians=fake_BAS_archive(include_thule=False)
    polygons,meta=a.original_native_land_geometry(data,medians)
    report=a.source_sample_without_species_outcomes(fake_original_nest_rows(),polygons)
    assert meta["original_three_island_strict_polygon_counts"]["Thule"]==0
    assert report["Beach_Point"]["original_STRICT_island_land_polygon_matched"] is False
    assert report["Hewison_Point"]["fraction_source_nests_inside"] is None
    assert not a.science_gates(meta,report)["source_only_Paper2_Geography_gate_pass"]


def test_source_nest_offshore_fraction_fails_before_any_effect():
    data,medians=fake_BAS_archive()
    polys,meta=a.original_native_land_geometry(data,medians)
    nests=fake_original_nest_rows()
    nests["Ashen_Hills"]["xy"][:20,0]+=10000
    out=a.source_sample_without_species_outcomes(nests,polys)
    assert out["Ashen_Hills"]["fraction_source_nests_inside"]<.95
    assert not a.science_gates(meta,out)["source_only_Paper2_Geography_gate_pass"]
