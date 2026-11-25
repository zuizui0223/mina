"""Synthetic original Site ID land polygon support and coastline-near HOLD."""
from __future__ import annotations

import sys
from pathlib import Path
import pytest
from pyproj import Transformer
from shapely.geometry import box

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_asi_source_landmass_v34 import (
    original_site_coordinates,source_geography_to_land
)


def row(sid,latitude,longitude,region="CW"):
    return {
        "Site_ID":sid,"Latitude":str(latitude),
        "Longitude":str(longitude),"Region":region,
        "Site_name":sid,"Count":"100","Species":"ADPE",
    }


def test_source_same_site_year_coordinate_drift_is_hold_not_census_change():
    data=[
        row("AAAA",-72.,70.),
        row("AAAA",-72.,70.),
        row("BBBB",-72.,70.001),
        row("BBBB",-72.,70.100),
    ]
    q=original_site_coordinates(data)
    assert q["AAAA"]["source_coordinate_status"]=="EXACT_ONE_ORIGINAL_SITE_LATLON_AND_REGION"
    assert q["BBBB"]["source_coordinate_status"]=="HOLD_UNSTABLE_SOURCE_SITE_COORDINATE_OR_REGION"


def test_original_sites_two_source_ids_same_landmass_are_not_two_islands():
    transformer=Transformer.from_crs(4326,3031,always_xy=True)
    lat,lon=-70.,60.
    x,y=transformer.transform(lon,lat)
    observations=[
        row("C001",lat,lon),
        row("C002",lat,lon+.001),
        row("C003",lat,lon+.04),
    ]
    sites=original_site_coordinates(observations)
    # First two inside same original land polygon; third is outside/hold.
    aa=transformer.transform(lon+.001,lat)
    bb=transformer.transform(lon+.04,lat)
    source_land=[
        (10,box(min(x,aa[0])-100,min(y,aa[1])-100,
                max(x,aa[0])+100,max(y,aa[1])+100),{}),
        (20,box(x+10000,y+10000,x+20000,y+20000),{})
    ]
    out,stats=source_geography_to_land(sites,source_land)
    lookup={r["original_Site_ID"]:r for r in out}
    assert lookup["C001"]["source_exact_original_SCAR_land_FID"]==10
    assert lookup["C002"]["source_exact_original_SCAR_land_FID"]==10
    assert lookup["C003"]["source_exact_original_SCAR_land_FID"] is None
    assert stats["original_distinct_mapped_parent_land_FIDs"]==1
    assert stats["original_parent_land_polygons_with_two_or_more_original_Site_IDs"]==1
    assert stats["source_reported_site_centroid_is_verified_colony_nest_GPS"] is False
    assert stats["ecological_breeding_growth_or_island_effect_fitted"] is False
