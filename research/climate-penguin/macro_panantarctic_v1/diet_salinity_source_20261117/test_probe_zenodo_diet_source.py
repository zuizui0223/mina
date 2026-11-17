"""Deterministic source-gate tests; no network."""
from pathlib import Path
import importlib.util,hashlib,unittest
spec=importlib.util.spec_from_file_location("probe",Path(__file__).with_name("probe_zenodo_diet_source.py"))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Tests(unittest.TestCase):
    def test_metadata_only(self):
        record={"id":17409948,"doi":"10.5281/zenodo.17409948","metadata":{"title":"Sample"},
                "files":[{"key":"Data/DI_df.rds","size":1000,"checksum":"md5:abc","links":{"self":"https://zenodo.org/api/files/example"}}]}
        result=mod.normalize(record)
        self.assertEqual(result["file_count"],1)
        self.assertEqual(result["candidate_under50mb"],["Data/DI_df.rds"])
        self.assertTrue(result["ecological_inference"].startswith("NOT RUN"))
    def test_wrong_record_fails(self):
        with self.assertRaises(ValueError):mod.normalize({"id":1,"files":[]})
    def test_large_missing_are_not_download_candidates(self):
        record={"id":17409948,"files":[{"key":"huge.zip","size":100_000_000,"links":{"content":"url"}},
                                           {"key":"no-link.rds","size":100,"links":{}}]}
        self.assertEqual(mod.normalize(record)["candidate_under50mb"],[])
    def test_source_checksum_honored(self):
        source=b"row1,row2\\n"
        good=hashlib.md5(source).hexdigest()
        self.assertEqual(mod.verify_md5_bytes(source,"md5:"+good),"SOURCE_MD5_MATCH")
        with self.assertRaises(ValueError):mod.verify_md5_bytes(source,"md5:"+("f"*32))
if __name__=="__main__":unittest.main()
