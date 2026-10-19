"""No original seabird results in tests: invented source P/A geography only."""
import sys
from pathlib import Path

import pytest
np=pytest.importorskip("numpy")
pd=pytest.importorskip("pandas")
pytest.importorskip("sklearn")
pytest.importorskip("pyproj")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import fit_aadc_nesting_guild_island_area_v14 as v


def hypothetical_tables():
    geog=[]
    source=[]
    for block,lon in enumerate((45.,105.)):
        for i in range(7):
            site=f"S{block}{i}"
            typ="island" if i%2==0 else "continent"
            geog.append({
                "geog_site_id":site,
                "sub_group":f"G{block}",
                "geog_site_feature":typ,
                "geog_site_area":1000.*(i+1)**2,
                "geog_site_area_cat3":"S",
                "latitude":-67.2-0.01*i,
                "longitude":lon+0.05*i,
                "distance_station":i+1,
                "distance_inland_coast":0,
            })
            for ix,sp in enumerate(("SGP","SK","AP","CP","SF","SP","WSP")):
                source.append({
                    "geog_site_id":site,"species_code":sp,
                    "season":"200809",
                    "occurrence":"P" if (i+ix)%3==0 else "A",
                    "occurrence_cert_cat":5 if (i+ix)%3==0 else 4,
                    "certainty_lookup":"EXACT_CERTAINTY_RULE",
                    "vantage":"G" if ix%2==0 else "A",
                    "species_expert_validation":"Y",
                    "site_expert_validation":"Y",
                    "occurrence_expert_validation":"Y",
                })
    return pd.DataFrame(source),pd.DataFrame(geog)


def test_primary_survey_P_A_are_preserved_with_unique_site_by_guild():
    survey,geo=hypothetical_tables()
    panel,qa=v.frame_data(survey,geo)
    assert len(panel)==14*7
    assert panel.geog_site_id.nunique()==14
    assert panel.block250km.nunique()==2
    assert qa["raw_eight_flying_species_search_rows"]==98
    assert panel["site_species_weight"].eq(1).all()
    assert panel.y.sum()==survey.occurrence.eq("P").sum()
    assert set(panel.guild)=={"OPEN","LEDGE","CREVICE"}
    assert panel["area"].gt(0).all()


def test_not_reported_is_not_absence_and_inconsistent_class_is_discarded():
    survey,geo=hypothetical_tables()
    nr=survey.iloc[0].copy()
    nr["geog_site_id"]="S01"
    nr["species_code"]="WSP"
    nr["occurrence"]="NR"
    nr["occurrence_cert_cat"]=2
    nr["certainty_lookup"]="EXACT_CERTAINTY_RULE"
    # Replace one original source row with NR without affecting nearby taxa.
    survey.loc[0,"occurrence"]="NR"
    survey.loc[0,"occurrence_cert_cat"]=2
    survey.loc[1,"occurrence_cert_cat"]=3  # false assignment -> source hold
    source=survey.copy()
    panel,qa=v.frame_data(source,geo)
    assert len(panel)==96
    assert qa["original_P_or_direct_A_after_duplicate_drops"]==97
    assert qa["status_or_certainty_mismatch_removed"]==1
    assert qa["source_excluded_nonreporting_not_zero"] is True


def test_same_site_species_season_duplicates_entire_source_group_removed():
    survey,geo=hypothetical_tables()
    duplicate=survey.iloc[0].copy()
    duplicate["occurrence"]="A" if duplicate["occurrence"]=="P" else "P"
    duplicate["occurrence_cert_cat"]=4 if duplicate["occurrence"]=="A" else 5
    survey=pd.concat([survey,pd.DataFrame([duplicate])],ignore_index=True)
    panel,qa=v.frame_data(survey,geo)
    assert len(panel)==97
    assert qa["original_source_status_conflict_groups_dropped"]==1
    assert qa["original_observation_rows_in_duplicate_groups"]==2


def test_year_code_is_author_original_six_digit_not_guessed_from_missing_year():
    survey,geo=hypothetical_tables()
    survey.loc[0,"season"]="2008"
    survey.loc[1,"season"]="200920"
    panel,qa=v.frame_data(survey,geo)
    assert len(panel)==96
    assert qa["original_season_1980_2020_rows"]==96


def test_train_only_logistic_does_not_see_held_out_P_A_values():
    survey,geo=hypothetical_tables()
    sample,qa=v.frame_data(survey,geo)
    y=sample.y.to_numpy(dtype=int)
    features=v.feature_arrays(sample)
    train=np.arange(len(y))<75
    assert set(y[train])=={0,1}
    weights=np.ones(len(y))
    predicted,coeff=v.model_fit(y,features,"B2_nesting_mode_area_island",train,weights)
    modified=y.copy()
    modified[~train]=1-modified[~train]
    predicted2,_=v.model_fit(modified,features,"B2_nesting_mode_area_island",train,weights)
    np.testing.assert_allclose(predicted,predicted2,rtol=0,atol=1e-10)
    assert set(v.PHYSICAL)<set(v.GUILD)
    assert v.TESTED_TRIPLE in coeff
    assert len(predicted)==len(y)
    assert np.min(predicted)>0 and np.max(predicted)<1


def test_distinct_island_sites_vs_repeated_events_are_not_independent_islands():
    survey,geo=hypothetical_tables()
    repeated=survey.copy()
    repeated["season"]="200910"
    df=pd.concat([survey,repeated],ignore_index=True)
    sample,qa=v.frame_data(df,geo)
    assert len(sample)==2*14*7
    assert sample.geog_site_id.nunique()==14
    assert sample.site_species_weight.eq(.5).all()


def test_area_overlap_gate_cannot_be_made_by_dummy_source_columns():
    survey,geo=hypothetical_tables()
    data,qa=v.frame_data(survey,geo)
    supported,report=v.physical_overlap_gate(data)
    assert supported is False
    assert "OPEN" in report
    assert "CONTINENT" not in data.geog_site_feature.values
    assert report["LEDGE"]["site_classes"]["continent"]["distinct_original_geographic_sites"]<8


def test_source_checksum_fails_closed(tmp_path):
    p=tmp_path/"fake.csv"
    p.write_text("site,value\nabc,23\n")
    with pytest.raises(ValueError,match="SHA drift"):
        v.checked_csv(p,v.ORIGINAL_SITE_SHA)
