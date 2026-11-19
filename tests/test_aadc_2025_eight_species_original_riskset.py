import unittest
from unittest.mock import patch
from scripts.audit_aadc_2025_eight_species_original_riskset import (
    SOURCE_COUNTS, SOURCE_EXPECTED_EVENTS, PUBLICATION_REPORTED_EVENTS,
    season_year,strict_state,audit_source
)

class TestPublisherRiskSet(unittest.TestCase):
    def test_source_count_mismatch_is_explicit(self):
        self.assertEqual(SOURCE_COUNTS["2025_seabird"]+SOURCE_COUNTS["2025_penguin"],
                         SOURCE_EXPECTED_EVENTS)
        self.assertEqual(PUBLICATION_REPORTED_EVENTS-SOURCE_EXPECTED_EVENTS,190)
    def test_na_or_nr_is_not_absence(self):
        self.assertEqual(strict_state({"NR"}),"NR_ONLY")
        self.assertEqual(strict_state({"A","NR"}),"MIXED_A_WITH_NR_OR_INVALID")
        self.assertEqual(strict_state({"A","P"}),"CONFLICT_P_AND_A")
        self.assertEqual(strict_state({"P","NR"}),"P_REPORTED_NO_A")
        self.assertEqual(strict_state({"A"}),"A_REPORTED_ONLY")
    def test_annual_season_parse(self):
        self.assertEqual(season_year(191213),1912)
        self.assertEqual(season_year(195960.0),1959)
        self.assertEqual(season_year(199900),None)  # malformed successor
        self.assertEqual(season_year(199920),None)  # unrelated year suffix
        self.assertEqual(season_year(200001),2000)
        self.assertEqual(season_year("2001-02"),2001)
        self.assertEqual(season_year("2001/02"),2001)
        self.assertEqual(season_year(2013.0),2013)
        self.assertIsNone(season_year("invalid"))
        self.assertIsNone(season_year(""))
    def test_missing_and_conflicting_states_not_transition(self):
        # Test genuine source aggregation logic without loosening annual A/P gate.
        geo=[dict(geog_site_id="SITE1",geog_site_feature="island",
                  sub_group="S",geog_site_area_cat3="1")]
        old=[dict(geog_site_id="SITE1",sub_group="S")]
        base={"sub_group":"S","geog_site_id":"SITE1","species_code":"CP",
              "vantage":"G","site_expert_validation":"Y",
              "occurrence_expert_validation":"Y",
              "species_expert_validation":"Y"}
        fly=[
          dict(base,season="2010-11",occurrence="A"),
          dict(base,season="2010-11",occurrence="NR"),
          dict(base,season="2011-12",occurrence="P"),
          dict(base,season="2013-14",occurrence="A"),
          dict(base,season="2014-15",occurrence="P"),
          dict(base,season="2015-16",occurrence="P"),
          dict(base,season="2016-17",occurrence="A"),
          dict(base,season="2016-17",occurrence="P"),
        ]
        cert=[dict(species_code="CP",occurrence="A",vantage="G",
                   geog_site_area_cat3="1",occurrence_cert_cat="H")]
        with patch("scripts.audit_aadc_2025_eight_species_original_riskset.SOURCE_EXPECTED_EVENTS",len(fly)):
            d=audit_source({
                "2025_seabird":fly,
                "2025_penguin":[],
                "2025_geographic_sites":geo,
                "2025_certainty":cert,
                "2016_icefree_site_atlas":old,
            })
        self.assertEqual(d["status"],"PUBLISHER_EIGHT_SPECIES_SOURCE_SUPPORT_NO_BIOLOGICAL_EFFECT")
        self.assertEqual(d["observed_site_species_A_then_P_pairs"],1)
        self.assertEqual(d["consecutive_strict_state_pairs_by_species"]["CP"].get("A_REPORTED_ONLY__to__P_REPORTED_NO_A",0),1)
        self.assertEqual(d["resolved_annual_site_species_status"]["CONFLICT_P_AND_A"],1)

if __name__=="__main__":
    unittest.main()
