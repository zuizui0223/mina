import unittest
from scripts.audit_aadc_planetarycomputer_pixel_qa import check_asset
class TestPCAssets(unittest.TestCase):
    def test_only_publisher_signed_blob(self):
        self.assertTrue(check_asset("https://collection.blob.core.windows.net/data/file.tif?sv=x&sig=valid"))
        self.assertFalse(check_asset("https://collection.blob.core.windows.net/data/file.tif"))
        self.assertFalse(check_asset("http://collection.blob.core.windows.net/data/file.tif?sig=x"))
        self.assertFalse(check_asset("https://fake.example.com/file.tif?sig=x"))
if __name__=="__main__":
    unittest.main()
