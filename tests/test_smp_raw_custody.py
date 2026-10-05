import json
import tempfile
import unittest
from pathlib import Path

from scripts.record_smp_raw_custody_v1 import RECEIPT_ID, run


class SmpRawCustodyTests(unittest.TestCase):
    def test_receipt_hashes_file_without_emitting_contents(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "provider_export.csv"
            secret = "Species,Count\nKittiwake,987654321\n"
            raw.write_text(secret, encoding="utf-8")

            out = run(
                raw,
                received_at="2026-10-05T20:30:00+09:00",
                provider_filename="SMP_export_original.csv",
                source_channel="BTO secure transfer",
            )

            self.assertEqual(out["receipt_id"], RECEIPT_ID)
            self.assertFalse(out["content_parsed"])
            self.assertFalse(out["content_inspected"])
            self.assertEqual(out["provider_filename"], "SMP_export_original.csv")
            self.assertGreater(out["byte_size"], 0)
            self.assertEqual(len(out["sha256"]), 64)

            blob = json.dumps(out)
            self.assertNotIn("Kittiwake", blob)
            self.assertNotIn("987654321", blob)
            self.assertNotIn("Species", blob)

    def test_received_at_is_explicitly_required(self):
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "x.csv"
            raw.write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError):
                run(raw, received_at="")


if __name__ == "__main__":
    unittest.main()
