"""Fabricated census/land pixels to enforce V8 null/pairing before effects."""
from pathlib import Path
import importlib.util
import sys
import math

import pytest

pd=pytest.importorskip("pandas")
np=pytest.importorskip("numpy")
rasterio=pytest.importorskip("rasterio")
pytest.importorskip("pyproj")
shapefile=pytest.importorskip("shapefile")
pytest.importorskip("requests")
from rasterio.transform import from_origin
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import evaluate_apbp_icefree_coexistence_v8 as v


def make_event(eid,site,records,lat=-64,lon=-58):
    rows=[]
    for i,(species,n) in enumerate(records):
        rows.append({
            "original_event_core_id":eid,
            "scientificName_accepted":species,
            "eligibility":"ELIGIBLE_NEST_RECORD_ONLY",
            "site_id_original":site,
            "nest_numeric_candidate":n,
            "measurementAccuracy_original":2,
            "decimalLatitude":lat,
            "decimalLongitude":lon,
        })
    return rows


def fake_pair_data():
    a,b,c=v.TAXA
    sample=pd.DataFrame(
        make_event("E1","S1",[(a,80),(b,20)],-64,-58)
        +make_event("E2","S1",[(a,30),(b,70)],-64,-58)
        +make_event("E3","S2",[(a,20),(c,80)],-63,-56)
        +make_event("E4","S3",[(a,20),(b,0),(c,90)],-62,-56)
    )
    geo=pd.DataFrame([
        {"source_locationID":site,
         "high_class":"ISLAND_SEPARATE_LAND_POLYGON_PROXY",
         "original_APBP_max_uncertainty_m":100,
         "high_location_confidence":"HOLD_POSITION_RADIUS_CROSSES_LAND_BOUNDARY",
         "within_site_max_drift_m":0}
        for site in ["S1","S2","S3"]
    ])
    return sample,geo


def test_simultaneous_true_source_event_pair_and_site_aggregation():
    samples,geo=fake_pair_data()
    pairs,qa=v.source_pairs(samples,geo)
    assert qa["original_simultaneous_multispecies_Events"]==4
    assert qa["original_locationIDs_at_multispecies_Events"]==3
    a,b,c=v.TAXA
    selected=pairs[(pairs.site_id=="S1") &
                   (pairs.pair==a+"|"+b)].iloc[0]
    assert abs(selected.response_balance-0.5)<1e-12
    assert selected.source_n_events==2
    assert len(pairs)==5  # S1 AB, S2 AC, S3 AB/AC/BC
    # An unlisted species in E1/E2 was never interpreted as 0.


def test_explicit_original_zero_vs_unobserved_taxon_distinction():
    sample,geo=fake_pair_data()
    a,b,c=v.TAXA
    pairs,_=v.source_pairs(sample,geo)
    assert pairs.loc[
        (pairs.site_id=="S3") & (pairs.pair==a+"|"+b),
        "response_balance"].iloc[0]==0
    assert len(pairs.loc[pairs.site_id=="S1"])==1


def test_one_source_event_with_repeated_taxon_stops_that_whole_event():
    sample,geo=fake_pair_data()
    extra=make_event("E4","S3",[(v.TAXA[0],100)],-62,-56)
    dataset=pd.concat([sample,pd.DataFrame(extra)],ignore_index=True)
    pairs,qa=v.source_pairs(dataset,geo)
    assert qa["n_discarded_ambiguous_multispecies_event_IDs"]==1
    assert len(pairs)==2


def test_pixel_ecology_abiotic_tier_1_with_masked_ice_free_only():
    labels={1:"E1",2:"E2",3:"E3"}
    a=np.zeros((100,100),dtype="int16")
    a[20:70,20:70]=1
    a[30:45,20:45]=2
    a[45:55,30:40]=3
    transform=from_origin(-5000,5000,100,100)
    out=v.pixel_ecology(np.ma.masked_equal(a,0),transform,0,0,labels)
    assert out[5000]["valid_icefree_100m_pixels"]>1000
    assert 0<out[5000]["fraction_mapped_icefree"]<1
    assert out[5000]["tier1_distinct_env_types"]==3
    assert 0<out[5000]["tier1_shannon_diversity_normlog9"]<1
    assert out[2000]["valid_icefree_100m_pixels"]<out[5000]["valid_icefree_100m_pixels"]


def test_vat_lookup_uses_independent_nine_abiotic_categories(tmp_path):
    dbf=tmp_path/"source.dbf"
    out=shapefile.Writer(dbf=str(dbf),shp=None,shx=None)
    out.field("Value","N",size=12)
    out.field("ID_Tier1","C",size=15)
    for i in range(1,181):
        out.record(i,"E"+str((i-1)%9+1))
    out.close()
    typ=v.tier1_lookup(dbf)
    assert len(typ)==180
    assert set(typ.values())=={"E"+str(i) for i in range(1,10)}


def test_raster_sampling_does_not_use_penguin_presence_to_build_abiotic_labels(tmp_path):
    from pyproj import Transformer
    cx,cy=Transformer.from_crs(4326,3031,always_xy=True).transform(-58,-64)
    p=tmp_path/"mock_100m.tif"
    values=np.zeros((130,130),dtype="uint16")
    values[30:100,25:100]=1
    values[45:70,50:80]=2
    transform=from_origin(cx-6500,cy+6500,100,100)
    with rasterio.open(p,"w",driver="GTiff",height=130,width=130,count=1,
                       dtype="uint16",crs="EPSG:3031",transform=transform,nodata=0) as ds:
        ds.write(values,1)
    source,meta=v.extract_habitats(p,{"S":(-64,-58)},{1:"E1",2:"E2"})
    assert meta["raster_original_crs"]=="EPSG:3031"
    assert source["S"][5000]["tier1_distinct_env_types"]==2
    assert source["S"][5000]["valid_icefree_100m_pixels"]>2000
    assert source["S"][5000]["fraction_mapped_icefree"]<1


def test_ridge_is_train_only_never_uses_holdout_balance():
    n=35
    source={name:np.zeros(n) for name in v.PLUS}
    source["latitude"]=np.linspace(-74,-61,n)
    source["tier1_entropy_5km"]=np.linspace(0,0.4,n)
    y=np.linspace(0.1,0.9,n)
    train=np.arange(n)<28
    pred,coeff=v.ridge_predict(y,source,v.PLUS,train)
    edited=y.copy()
    edited[~train]=1e10
    pred2,_=v.ridge_predict(edited,source,v.PLUS,train)
    np.testing.assert_allclose(pred,pred2)
    assert "tier1_entropy_5km" in coeff
    assert v.RIDGE_ALPHA==10


def test_missing_source_sites_are_not_pretended_to_have_zero_habitat():
    sample,geo=fake_pair_data()
    pair,_=v.source_pairs(sample,geo)
    eco={
        "S1":{5000:{"valid_icefree_100m_pixels":200,"fraction_mapped_icefree":.4,
                     "tier1_shannon_diversity_normlog9":.3,"tier1_distinct_env_types":2},
              2000:{"valid_icefree_100m_pixels":40,"fraction_mapped_icefree":.4,
                     "tier1_shannon_diversity_normlog9":.2,"tier1_distinct_env_types":2}},
        "S2":{5000:{"valid_icefree_100m_pixels":0,"fraction_mapped_icefree":0,
                     "tier1_shannon_diversity_normlog9":None,"tier1_distinct_env_types":0},
              2000:{"valid_icefree_100m_pixels":0,"fraction_mapped_icefree":0,
                     "tier1_shannon_diversity_normlog9":None,"tier1_distinct_env_types":0}},
        "S3":{5000:{"valid_icefree_100m_pixels":60,"fraction_mapped_icefree":.1,
                     "tier1_shannon_diversity_normlog9":0.0,"tier1_distinct_env_types":1},
              2000:{"valid_icefree_100m_pixels":20,"fraction_mapped_icefree":.1,
                     "tier1_shannon_diversity_normlog9":0.0,"tier1_distinct_env_types":1}},
    }
    combined=v.attach_habitats(pair,eco)
    assert combined.loc[combined.site_id.eq("S2"),"tier1_entropy_5km"].isna().all()
    assert combined.loc[combined.site_id.eq("S2"),"valid_pixels_5km"].eq(0).all()
