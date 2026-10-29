"""Paper2 V51 synthetic coast and heldout model tests; no raw original bird rows."""
import io,zipfile
from pathlib import Path
import sys
import numpy as np
import pytest
import shapefile
from shapely.geometry import box

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import analyze_paper2_three_island_penguin_coast_access_v51 as m


def fake_sites():
    # Invented 4 projected localities on three separate fake coastal islands.
    names=list(m.ORIGINAL_LOCALITIES)
    coordinates={
       "Ashen_Hills":(540000.,3590000.),
       "Bellingshausen":(490000.,3410000.),
       "Beach_Point":(475000.,3409000.),
       "Hewison_Point":(476000.,3409000.)
    }
    groups={
       "Saunders":box(539000.,3589000.,541000.,3591000.),
       "Bellingshausen":box(489000.,3409000.,491000.,3411000.),
       "Thule":box(474000.,3408000.,477000.,3410000.)
    }
    rng=np.random.default_rng(1)
    data={}
    for name in names:
        xx,yy=coordinates[name]
        n=320
        xy=rng.normal([xx,yy], [80.,80.],(n,2))
        lab=np.tile([0,1],n//2).astype(np.uint8)
        # invented source species habitat separation
        elev=15+(xy[:,1]-yy)/100.+3*(lab==1)
        slope=10+(xy[:,0]-xx)/100.+2*(lab==1)
        data[name]={
          "xy":xy,"label":lab,"elev":elev,"slope":slope,
          "total_original_rows":n,"original_collision_rows_excluded":0}
    return data,groups


def test_original_source_immutability_and_geographic_signatures():
    assert m.SOURCE_NPZ_SHA=="1566f4fef4ac5370f40f6482e9f76f7b252e32ade8915a190cf0d2fc946883ec"
    assert m.GSHHG_SHA=="8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41"
    assert len(set(m.PARENT.values()))==3
    assert sum(m.SOURCE_NPZ_EXPECTED.values())==122139
    assert m.D_GRID_M==30.
    assert m.SOURCE_NPZ_EXPECTED["Beach_Point"]==7683
    assert m.MIN_INSIDE_SOURCE==.95


def test_source_coast_is_measured_from_one_true_physical_island_not_other_coasts():
    d,g=fake_sites()
    q,report=m.coast_distance_for_locs(d,g)
    assert set(q)==set(m.ORIGINAL_LOCALITIES)
    assert all(r["source_polygon_interior_fraction"]>=.99 for r in report.values())
    assert all(r["max_distance_quantization_error_bound_m"]==30*2**.5/2 for r in report.values())
    assert report["Hewison_Point"]["source_candidate_physical_island"]=="Thule"
    assert report["Beach_Point"]["source_candidate_physical_island"]=="Thule"
    assert report["Ashen_Hills"]["by_original_penguin_taxon"]["ADELIE"]["source_distinct_original_nest_positions_n"]==160


def test_coast_source_gate_rejects_offshore_nests_before_species_effect():
    d,g=fake_sites()
    d["Ashen_Hills"]["xy"][:25,0]+=5000
    with pytest.raises(ValueError,match="OUTSIDE_ISLAND_GATE"):
        m.coast_distance_for_locs(d,g)


def test_source_island_holdout_all_4_localities_nested_in_3_true_islands():
    d,coasts=fake_sites()
    access,_=m.coast_distance_for_locs(d,coasts)
    res=m.source_heldout_predictive_qa(d,access)
    assert res["original_frozen_holdout_groups_n"]==3
    assert res["individual_penguin_nests_independent_island_replicates"] is False
    assert set(res["original_actual_GSHHG_polygon_groups_held_out"])=={"Bellingshausen","Saunders","Thule"}
    assert len(res["heldout_island_Brier"]["Thule"]["source_heldout_original_localities"])==2
    assert all(np.isfinite(v["heldout_island_equal_site_B2"]) for v in res["heldout_island_Brier"].values())


def test_any_corrupted_or_changed_original_npz_must_stop(tmp_path):
    f=tmp_path/"synthetic.npz"
    np.savez(f, Ashen_Hills_xy=np.array([[1.,2.]]))
    with pytest.raises(ValueError,match="SHA_MISMATCH"):
        m.read_original_npz(f)


def test_original_three_island_shape_ids_from_fake_full_L1_source_in_memory():
    # Fake three equal-size source polygons at correct target WGS84 places.
    centers={"Saunders":(-26.42,-57.80),
             "Bellingshausen":(-27.08,-59.40),
             "Thule":(-27.32,-59.45)}
    shp=io.BytesIO();shx=io.BytesIO();dbf=io.BytesIO()
    with shapefile.Writer(shp=shp,shx=shx,dbf=dbf,shapeType=shapefile.POLYGON) as w:
        w.field("id","N",size=11)
        for i,(lon,lat) in enumerate(centers.values(),1):
            ring=[[lon-.003,lat-.003],[lon+.003,lat-.003],
                  [lon+.003,lat+.003],[lon-.003,lat+.003],[lon-.003,lat-.003]]
            w.poly([ring])
            w.record(i)
    buff=io.BytesIO()
    with zipfile.ZipFile(buff,"w") as z:
        for ext,p in ((".shp",shp),(".shx",shx),(".dbf",dbf)):
            z.writestr("GSHHS_shp/f/GSHHS_f_L1"+ext,p.getvalue())
    coast,meta=m.read_original_full_coast_shapes(buff.getvalue(),centers)
    assert len(coast)==3
    assert len(set(meta["original_GSHHG_source_ids_for_three_coast_islands"].values()))==3
    assert all(v>0 for v in meta["original_projected_island_land_area_km2"].values())


def test_train_only_scaler_does_not_use_test_habitat_rows():
    train=np.array([[1.,2.],[2.,3.],[3.,4.],[4.,5.]])
    test=np.array([[10000.,20000.]])
    x,y=m.train_fold_scaled(train,test)
    assert np.allclose(np.median(x,axis=0),[0,0])
    assert np.all(y>100)
    assert m.balanced_brier(np.array([0,1]),np.array([0.5,0.5]))==.25
