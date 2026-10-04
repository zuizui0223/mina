import unittest, pandas as pd
from scripts.validate_paper3_zenodo_annual_anchor import validate

class AnnualAnchorSemanticTests(unittest.TestCase):
    def test_constancy(self):
        rows=[]
        for c in ("Astrid","Mertz","SANAE"):
          for y in range(2014,2024):
            s=f"{y}-{y+1}"
            rows += [
              {"colony":c,"season":s,"date":f"{y}-09-01","point_lon":1+y/1000,"point_lat":-70},
              {"colony":c,"season":s,"date":f"{y}-10-01","point_lon":1+y/1000,"point_lat":-70},
            ]
        contract={"contract_id":"x","validation":{"required_colonies":["Astrid","Mertz","SANAE"],"required_seasons_per_colony":10,"required_total_colony_seasons":30,"required_constancy_fraction":1.0,"date_parse_required":1.0,"finite_coordinate_required":1.0}}
        r=validate(pd.DataFrame(rows),contract)
        self.assertTrue(r["decision"]["annual_anchor_semantic_gate_passed"])
if __name__=="__main__": unittest.main()
