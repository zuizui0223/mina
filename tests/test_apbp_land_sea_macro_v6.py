"""V6 model contract: synthetic site-season panels only, not penguin biology."""
from pathlib import Path
import sys

import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")
pytest.importorskip("pyproj")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import evaluate_apbp_land_sea_macro_v6 as macro


def invented_source_tables():
    records=[]
    for site,sp,class_label,rock,lat,lon in [
        ("A", "Pygoscelis adeliae", macro.ISLAND, 0.6, -64.0, -58.0),
        ("B", "Pygoscelis antarcticus", macro.MAINLAND, 0.8, -65.0, -59.0),
        ("C", "Pygoscelis papua", macro.ISLAND, 0.25, -64.2, -56.0),
    ]:
        for season in (2002,2003,2004):
            original_count={"A":100,"B":30,"C":40}[site] + (season-2002)*({"A":3,"B":-2,"C":1}[site])
            records.append({
                "eligibility":"ELIGIBLE_NEST_RECORD_ONLY",
                "site_id_original":site,
                "scientificName_accepted":sp,
                "event_date":f"{season}-12-10",
                "nest_numeric_candidate":original_count,
                "measurementAccuracy_original":2,
                "original_occurrenceID":f"{site}{season}",
            })
    pop=pd.DataFrame(records)
    med=pd.DataFrame([
        {"original_locationID":site,"rock_2000m_mapped_km2":rock,
         "latitude":lat,"longitude":lon,"land_polygon_id":site}
        for site,sp,kind,rock,lat,lon in [
            ("A","x",macro.ISLAND,0.6,-64.0,-58.0),
            ("B","x",macro.MAINLAND,0.8,-65.0,-59.0),
            ("C","x",macro.ISLAND,0.25,-64.2,-56.0),
        ]
    ])
    hi=pd.DataFrame([
        {"source_locationID":site,"high_class":klass,
         "medium_to_high_class_disagreement":False,
         "high_original_feature_id":int(i),
         "original_APBP_max_uncertainty_m":100}
        for i,(site,klass) in enumerate([
            ("A",macro.ISLAND),("B",macro.MAINLAND),("C",macro.ISLAND)
        ])
    ])
    marine=pd.DataFrame([
        {"original_APBP_locationID":site,"breeding_start_year":year,
         "sic_25_75km_anomaly":(year-2002)*0.02,
         "sic_75_150km_anomaly":(year-2002)*(-0.025)}
        for site in ("A","B","C") for year in (2002,2003,2004)
    ])
    return pop,med,hi,marine


def test_strict_temporal_panel_contains_only_actual_one_year_transitions():
    pop,med,hi,marine=invented_source_tables()
    pairs,support=macro.prepare(pop,med,hi,marine)
    assert len(pairs)==6  # Two consecutive transitions from each of 3 sites
    assert sorted(pairs["season"].unique())==[2003,2004]
    assert support["distinct_source_site_ids"]==3
    y,cols=macro.features(pairs)
    assert np.isfinite(y).all()
    assert len(cols[macro.INTERACTION])==6
    assert all((pairs.nest_numeric_candidate_prev>=0).to_list())


def test_duplicate_original_survey_row_is_excluded_from_both_season_pairs():
    pop,med,hi,marine=invented_source_tables()
    pop=pd.concat([pop,pop.loc[
        (pop.site_id_original=="A") & (pop.event_date=="2003-12-10")
    ]],ignore_index=True)
    pairs,qa=macro.prepare(pop,med,hi,marine)
    # A(2002→2003) and A(2003→2004) both disappear because their
    # common 2003 site/species/season cannot be arbitrarily selected.
    assert len(pairs)==4
    assert qa["ambiguous_duplicate_site_species_season_groups_discarded"]==1
    assert qa["source_rows_in_ambiguous_groups_discarded"]==2


def test_no_year_only_or_november_surveys_in_oct_nov_antecedent_model():
    pop,med,hi,marine=invented_source_tables()
    extra=pop.iloc[0].to_dict()
    extra["event_date"]="2003-11-10"
    extra["original_occurrenceID"]="NOT_ELIGIBLE_NOV"
    pop=pd.concat([pop,pd.DataFrame([extra])],ignore_index=True)
    extra=pop.iloc[0].to_dict()
    extra["event_date"]="2003"
    extra["original_occurrenceID"]="NOT_ELIGIBLE_YEAR_ONLY"
    pop=pd.concat([pop,pd.DataFrame([extra])],ignore_index=True)
    pairs,qa=macro.prepare(pop,med,hi,marine)
    assert len(pairs)==6
    assert qa["dated_dec_jan_feb_rows"]==9


def test_source_sha_mismatch_raises_hard_stop(tmp_path):
    path=tmp_path/"fake.csv"
    path.write_text("secret,numbers\n1,2\n",encoding="utf-8")
    with pytest.raises(ValueError,match="SHA drift"):
        macro.verified_csv(path,"population")


def test_ridge_predict_trains_without_seeing_heldout_responses():
    inputs=np.arange(1,25,dtype=float)
    cols={key:np.zeros(len(inputs)) for key in macro.LAND_SEA}
    cols["year"]=inputs/20
    cols["log_n_prev"]=np.sqrt(inputs)
    actual=inputs/20
    training=np.array([i<18 for i in range(24)],dtype=bool)
    base_pred,coef=macro.ridge_predict(actual,cols,"B0_baseline",training)
    contaminated=actual.copy()
    contaminated[~training]+=1e9
    result,_=macro.ridge_predict(contaminated,cols,"B0_baseline",training)
    np.testing.assert_allclose(base_pred,result,rtol=0,atol=1e-12)
    assert macro.ALPHA==20
    assert "ice_near" not in macro.MODELS["B0_baseline"]


def test_prespecified_model_nesting_and_island_3way_only_in_B2():
    assert set(macro.CONTROL)<set(macro.MARINE)<set(macro.LAND_SEA)
    assert macro.INTERACTION in macro.LAND_SEA
    assert macro.INTERACTION not in macro.MARINE
    assert "ice_near_island_logrock" not in macro.CONTROL


def test_no_one_site_or_one_block_is_an_independent_antarctic_island():
    pop,med,hi,marine=invented_source_tables()
    pairs,qa=macro.prepare(pop,med,hi,marine)
    assert qa["spatial_250km_blocks"]<=3
    assert qa["distinct_source_site_ids"]==3
    # Do not infer independent islands from census row count.
    assert pairs.site_id_original.nunique()<len(pairs)
