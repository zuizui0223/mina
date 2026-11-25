"""V55 source-only strict published land and 30m cell-spatial weighting synthetic QA."""
from pathlib import Path
import sys
import numpy as np
import pytest
from shapely import contains_xy
from shapely.geometry import box
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import falsify_paper2_coast_map_proximity_v55 as m


def make_fake_source():
    anchors={
        "Ashen_Hills":(535000.,3592500.),
        "Bellingshausen":(495000.,3414580.),
        "Beach_Point":(482000.,3411000.),
        "Hewison_Point":(482400.,3411100.),
    }
    coast={
        "Saunders":box(534600.,3592100.,535400.,3592900.),
        "Bellingshausen":box(494600.,3414180.,495400.,3414980.),
        "Thule":box(481600.,3410700.,482800.,3411500.),
    }
    rng=np.random.default_rng(20261028)
    original={}
    for name,(x,y) in anchors.items():
        labels=np.tile([0,1],160)
        xy=np.array([x,y])+rng.normal(0,145,(320,2))
        # one synthetic source offshore observation, not a real penguin
        xy[:4,0]+=1000
        orig={
            "xy":xy,
            "label":labels.astype(np.uint8),
            "elev":10+rng.normal(0,2,320)+labels*3,
            "slope":6+rng.normal(0,2,320)+labels*2,
        }
        original[name]=orig
    return original,coast


def test_frozen_original_identifiability_and_design():
    assert m.EXPECTED_V54_GAIN==0.051613243579301644
    assert m.GRID==30.
    assert m.MIN_SOURCE_NESTS_CLASS_SITE==100
    assert m.MIN_CELLS_CLASS_SITE==20
    assert m.MIN_POSITIVE_SOURCE_ISLANDS==2
    assert m.v51.MIN_INSIDE_SOURCE==.95


def test_inverse_30m_occupied_species_cell_weights_have_cell_equal_total():
    xy=np.array([[2.,2.],[3.,3.],[34.,34.],[4.,4.],[5.,5.]],dtype=float)
    y=np.array([0,0,0,1,1],dtype=np.uint8)
    inv,cells=m.source_taxon_cell_inverse(xy,y)
    assert cells=={0:2,1:1}
    assert np.isclose(inv[y==0].sum(),2)
    assert np.isclose(inv[y==1].sum(),1)
    assert np.isclose(inv[0],.5)
    with pytest.raises(ValueError,match="MISSHAPED"):
        m.source_taxon_cell_inverse(np.array([1,2]),np.array([0,1]))


def test_original_land_and_source_GIS_metadata_no_snap_and_cells(monkeypatch):
    original,polygons=make_fake_source()
    import analyze_paper2_penguin_official_coast_map_proximity_v54 as v54
    fake_counts={}
    for site,raw in original.items():
        land=polygons[m.v51.PARENT[site]]
        fake_counts[site]=(len(raw["xy"]),int(contains_xy(land,
             raw["xy"][:,0],raw["xy"][:,1]).sum()))
    monkeypatch.setattr(v54,"SOURCE_SAMPLE_COUNTS",fake_counts)
    measures,atlas=v54.island_coast_map_only(original,polygons)
    strict,counts=m.original_land_and_source_coast(original,polygons,measures)
    assert all(counts[s]["original_Adelie_source_inside_and_DEM_qualified"]>=100
               and counts[s]["original_Chinstrap_source_inside_and_DEM_qualified"]>=100
               for s in strict)
    assert all(np.sum(~strict[s]["keep"])>=4 for s in strict)
    prepared=m.prep_land_only_cell_source(original,strict)
    assert all(min(q["original_taxon_cell_n"].values())>=m.MIN_CELLS_CLASS_SITE
               for q in prepared.values())
    result=m.original_three_island_cell_equal_holdout(prepared)
    assert result["original_heldout_independent_physical_islands"]==3
    assert len(result["original_island_holdout_results"]["Thule"]["original_sites_heldout_together"])==2
    assert np.isfinite(result["original_equal_island_Brier_gain"])
    assert result["individual_penguin_nests_not_independent_source_island_replicates"]


def test_nonland_impossible_95percent_support_is_still_not_rescued():
    orig,coast=make_fake_source()
    assert set(m.v51.PARENT.values())==set(coast)
    # Even when source good fits, V51 strict original 95%-per-site rule
    # is not overridden or promoted by postresult V55.
    assert m.v51.MIN_INSIDE_SOURCE==.95


def test_balanced_cell_scoring_is_not_raw_pseudoreplicate_loss():
    y=np.array([0,0,0,1,1])
    p=np.array([.01,.9,.9,.3,.3])
    inv=np.array([1,.5,.5,1,1])
    with pytest.raises(ValueError,match="SAMPLE_FAILED"):
        m.spatial_cell_guild_balanced_brier(y,p,inv)
