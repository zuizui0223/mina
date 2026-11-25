"""Synthetic coordinate-independent terrain source and masked-pixel tests."""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pytest
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from pyproj import Transformer

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_hart_copernicus_dem_terrain_v26 import (
    sample_locality_dem,validate_original_tile_index,EXPECTED_TILE
)


def test_original_tilelist_both_source_geographies_required():
    true_tiles="\n".join(sorted(set(EXPECTED_TILE.values())))+"\n"
    assert validate_original_tile_index(true_tiles)==sorted(set(EXPECTED_TILE.values()))
    with pytest.raises(ValueError,match="SOURCE_TILE_HOLD"):
        validate_original_tile_index(EXPECTED_TILE["Ashen_Hills"])


def test_sample_native_geographic_COG_and_WGS84_metres_slope():
    # Geographic pixels 1/3600°; a known DEM inclined eastward 10m/cell.
    data=np.tile(np.arange(7,dtype=np.float32)*10,(7,1))
    tf=from_origin(-27.,-57.,1/3600,1/3600)
    origlon=-27.+3.5/3600
    origlat=-57.-3.5/3600
    x,y=Transformer.from_crs(4326,32726,always_xy=True).transform(origlon,origlat)
    with MemoryFile() as memory:
        with memory.open(driver="GTiff",height=7,width=7,count=1,
                         dtype="float32",crs="EPSG:4326",transform=tf,
                         nodata=-9999) as src:
            src.write(data,1)
            h,s,q=sample_locality_dem(src,np.asarray([[x,y]]))
            assert h[0]==pytest.approx(30,abs=1e-4)
            assert 0<s[0]<90
            assert q["source_point_cell_outside_original_DEM_tile_or_edge"]==0
            assert q["source_points_with_valid_COG_elevation_and_3x3_slope"]==1
            assert q["terrain_habitat_selection_effect_fitted"] is False


def test_cloud_masked_cell_does_not_get_ocean_zero_rescue():
    data=np.ones((7,7),dtype=np.float32)*50
    data[3,4]=-9999
    tf=from_origin(-27.,-57.,1/3600,1/3600)
    lon=-27.+3.5/3600
    lat=-57.-3.5/3600
    x,y=Transformer.from_crs(4326,32726,always_xy=True).transform(lon,lat)
    with MemoryFile() as memory:
        with memory.open(driver="GTiff",height=7,width=7,count=1,
                         dtype="float32",crs="EPSG:4326",transform=tf,
                         nodata=-9999) as src:
            src.write(data,1)
            h,s,q=sample_locality_dem(src,np.asarray([[x,y]]))
            assert np.isnan(h[0])
            assert np.isnan(s[0])
            assert q["source_points_with_valid_COG_elevation_and_3x3_slope"]==0
            assert q["source_dem_complete_neighborhood_fraction"]==0
