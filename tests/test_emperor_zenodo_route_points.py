import unittest
from scripts.validate_emperor_zenodo_route_points import colony_from_path, season_from_path

class RoutePointSemanticTests(unittest.TestCase):
    def test_colony(self):
        self.assertEqual(colony_from_path("Upload/Astrid/foo.shp"),"Astrid")
        self.assertEqual(colony_from_path("Mertz/foo.shp"),"Mertz")
        self.assertEqual(colony_from_path("Sanae/foo.shp"),"SANAE")
    def test_season(self):
        self.assertEqual(season_from_path("Astrid14_15distance.shp"),"2014-2015")
        self.assertEqual(season_from_path("Sanae23_24distance.shp"),"2023-2024")

if __name__=="__main__":
    unittest.main()
