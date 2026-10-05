import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.freeze_smp_spatial_recovery_stageb_v1 import (
    git_blob_sha,
    sha256_file,
    validate_zero_semantics,
)
from scripts.guarded_run_smp_spatial_recovery_stagec_v1 import require_hash


class SmpOperationalFreezeTests(unittest.TestCase):
    def test_git_blob_sha_matches_git_object_format(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.txt"
            p.write_bytes(b"abc\n")
            data = b"abc\n"
            expected = hashlib.sha1(
                b"blob " + str(len(data)).encode() + b"\0" + data
            ).hexdigest()
            self.assertEqual(git_blob_sha(p), expected)

    def test_zero_semantics_requires_all_confirmations(self):
        good = {
            "row_with_direct_count_zero_is_surveyed_nil": True,
            "absent_site_year_row_is_not_zero": True,
            "estimated_or_imputed_zero_excluded_from_primary": True,
            "confirmation_source": "provider email",
            "compatible_start_year": 2000,
            "compatible_end_year": 2020,
            "compatible_record_family_or_era": "Whole Colony Counts",
        }
        validate_zero_semantics(good)
        bad = dict(good)
        bad["absent_site_year_row_is_not_zero"] = False
        with self.assertRaises(ValueError):
            validate_zero_semantics(bad)

    def test_guard_hash_rejects_mutated_stagec_input(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = root / "stageb.json"
            p.write_text('{"x":1}\n', encoding="utf-8")
            receipt = {
                "input_hashes": {
                    "stageb_support": {"sha256": sha256_file(p)}
                }
            }
            require_hash(receipt, "stageb_support", p)
            p.write_text('{"x":2}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                require_hash(receipt, "stageb_support", p)


if __name__ == "__main__":
    unittest.main()
