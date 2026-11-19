import unittest
from scripts.audit_aadc_eight_species_transition_validity import (
    year_detection_group_status, summarize_transitions
)
def datum(occ="A",expert="Y",species="ADP",vantage="G"):
    return {
      "occurrence":occ,"species_code":species,"vantage":vantage,
      "species_expert_validation":expert,
      "site_expert_validation":expert,
      "occurrence_expert_validation":expert
    }
def lookup(grade="4"):
    return {
       ("ADP","A","G","S"):[{"occurrence_cert_cat":grade}],
       ("ADP","P","G","S"):[{"occurrence_cert_cat":"5"}]
    }
class TestAADCSourceEvidenceLevel(unittest.TestCase):
    def test_original_direct_high_absence_and_validated_presence(self):
        a=year_detection_group_status([datum("A")],lookup(),"S")
        p=year_detection_group_status([datum("P")],lookup(),"S")
        self.assertEqual(a[1],"A")
        self.assertEqual(p[1],"P")
    def test_no_NR_or_unvalidated_absence_substitution(self):
        self.assertIsNone(year_detection_group_status(
            [datum("A",expert="N")],lookup(),"S")[1])
        self.assertIsNone(year_detection_group_status(
            [datum("A")],lookup("3"),"S")[1])
        self.assertIsNone(year_detection_group_status(
            [datum("A"),datum("NR")],lookup(),"S")[1])
        self.assertIsNone(year_detection_group_status(
            [datum("P"),datum("NR")],lookup(),"S")[1])
        self.assertIsNone(year_detection_group_status(
            [datum("P"),datum("A")],lookup(),"S")[1])
    def test_annual_pair_is_not_true_colonization(self):
        states={("IS1","ADP",2010):"A",("IS1","ADP",2011):"P",
                ("IS1","ADP",2013):"A"}
        places={"IS1":{"geog_site_feature":"island","sub_group":"SG1"}}
        x=summarize_transitions(states,places)
        self.assertEqual(x["AP_events"],1)
        self.assertEqual(x["A_risk_pairs"],1)
        self.assertEqual(x["AP_distinct_subgroups"],1)
        self.assertFalse(x["AP_event_source_rows"][0]["true_new_settlement_confirmed"])
if __name__=="__main__":
    unittest.main()
