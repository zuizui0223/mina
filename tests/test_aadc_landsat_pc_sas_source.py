import unittest
from unittest.mock import Mock,patch
from scripts.audit_aadc_landsat_qa_via_planetary_computer import sign_validated_asset
class TestPCSourceSAS(unittest.TestCase):
  def test_reject_non_pc_asset(self):
    with self.assertRaises(ValueError):
      sign_validated_asset("s3://other/private.tif")
    with self.assertRaises(ValueError):
      sign_validated_asset("https://evil.example.com/file.tif")
  def test_do_not_switch_asset_path(self):
    response=Mock()
    response.status_code=200
    response.json.return_value={"href":"https://example.blob.core.windows.net/x/other.tif?sig=secret"}
    with patch("scripts.audit_aadc_landsat_qa_via_planetary_computer.requests.get",return_value=response):
      with self.assertRaises(ValueError):
        sign_validated_asset("https://example.blob.core.windows.net/x/original.tif")
  def test_stable_original_asset_signing(self):
    response=Mock()
    response.json.return_value={"href":"https://example.blob.core.windows.net/x/original.tif?sig=REDACT"}
    with patch("scripts.audit_aadc_landsat_qa_via_planetary_computer.requests.get",return_value=response):
      signed,host=sign_validated_asset("https://example.blob.core.windows.net/x/original.tif")
      self.assertEqual(host,"example.blob.core.windows.net")
      self.assertNotEqual(signed.split("?")[0], "")
if __name__=="__main__":unittest.main()
