import unittest
from scripts.audit_aadc_pc_collection_token_source_recovery import attach_original_container_sas,error_class
class TestCollectionSASReuse(unittest.TestCase):
    def test_exact_azure_container_only(self):
        base="https://landsateuwest.blob.core.windows.net/landsat-c2/level-2/qa.tif"
        x=attach_original_container_sas(base,"se=2026&sig=fake")
        self.assertEqual(x,base+"?se=2026&sig=fake")
        for wrong in (
            "https://evil.example.com/landsat-c2/level-2/qa.tif",
            "https://landsateuwest.blob.core.windows.net/secret/qa.tif",
            "s3://usgs-landsat/collection02/qa.tif",
        ):
            with self.assertRaises(ValueError):
                attach_original_container_sas(wrong,"se=2026&sig=fake")
    def test_auth_error_redacted(self):
        s=error_class(RuntimeError("403 url=https://x?se=a&sig=do-not-emit"))
        self.assertEqual(s,{"type":"RuntimeError","http_code":403})
        self.assertNotIn("sig",str(s))
if __name__=="__main__":
    unittest.main()
