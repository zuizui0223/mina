import unittest

from scripts.crosswalk_published_guano_source_scenes import (
    parse_source_file,
    read_pangaea_table,
    choose_match,
)


class PublishedGuanoSceneCrosswalkTests(unittest.TestCase):
    def test_source_file_parser(self):
        # Character positions follow the PANGAEA description.
        x = parse_source_file("LE70541152001010XXX")
        self.assertEqual(x["wrs_path"], 54)
        self.assertEqual(x["wrs_row"], 115)
        self.assertEqual(x["year"], 2001)
        self.assertEqual(x["doy"], 10)
        self.assertEqual(x["date"], "2001-01-10")

    def test_pangaea_metaheader_parser(self):
        text = """/* DATA DESCRIPTION:\nfoo\n*/\nID\tFile name\td-value\tRow\tColumn\tNorth\tEast\tLatitude\tLongitude\tRot\tB3\tB4\tB5\tB7\n1\tLE70541152001010XXX\t0.4\t2\t3\t0\t0\t-70.0\t150.0\t0\t0.1\t0.2\t0.3\t0.4\n"""
        d = read_pangaea_table(text)
        self.assertEqual(len(d), 1)
        self.assertEqual(d.iloc[0].source_file, "LE70541152001010XXX")
        self.assertAlmostEqual(d.iloc[0].published_d, 0.4)

    def test_choose_match_by_properties(self):
        items = [{
            "id":"LE07_TEST",
            "properties":{"platform":"LANDSAT_7","landsat:wrs_path":54,"landsat:wrs_row":115}
        }]
        item, method = choose_match(items, {"wrs_path":54,"wrs_row":115})
        self.assertEqual(item, "LE07_TEST")
        self.assertEqual(method, "property_path_row")


if __name__ == "__main__":
    unittest.main()
