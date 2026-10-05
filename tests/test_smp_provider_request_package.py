import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORM = ROOT / "submission" / "SMP_BTO_DATA_REQUEST_FORM_READY_V1.md"
CONTENT = ROOT / "submission" / "SMP_DATA_REQUEST_CONTENT_V1.md"
DRAFT = ROOT / "submission" / "SMP_MACRO_DATA_REQUEST_DRAFT.md"
EVIDENCE = ROOT / "docs" / "SMP_PROVIDER_ACCESS_VERIFICATION_SUPPLEMENT_V1.md"


def section(text: str, heading: str) -> str:
    m = re.search(
        rf"^## {re.escape(heading)}\s*$\n\n([\s\S]*?)(?=\nCharacter count:|\n## |\Z)",
        text,
        flags=re.M,
    )
    if not m:
        raise AssertionError(f"section not found: {heading}")
    return m.group(1).strip()


class SmpProviderRequestPackageTests(unittest.TestCase):
    def test_form_fields_fit_declared_limits(self):
        text = FORM.read_text(encoding="utf-8")

        fields = [
            ("Title of project / question", 200),
            ("Details of research", 1500),
            ("Details of proposed collaboration", 1500),
            ("Details of data required", 1500),
            ("Any other information", 500),
        ]
        for heading, limit in fields:
            body = section(text, heading)
            self.assertLessEqual(len(body), limit, (heading, len(body), limit))

            # If a declared count is present immediately after the section,
            # keep it synchronized with the copy.
            pattern = (
                rf"^## {re.escape(heading)}\s*$\n\n"
                rf"[\s\S]*?\nCharacter count:\s*(\d+)\s*/\s*(\d+)\."
            )
            m = re.search(pattern, text, flags=re.M)
            self.assertIsNotNone(m, heading)
            self.assertEqual(int(m.group(1)), len(body), heading)
            self.assertEqual(int(m.group(2)), limit, heading)

    def test_request_matches_hysteresis_hypothesis_not_old_symmetry_endpoint(self):
        form = FORM.read_text(encoding="utf-8")
        content = CONTENT.read_text(encoding="utf-8")
        draft = DRAFT.read_text(encoding="utf-8")
        joined = "\n".join([form, content, draft])

        required = [
            "same repeated breeding SiteID",
            "recolonization",
            "abandon",
            "explicit zero",
            "missing",
            "Count=0",
            "SiteID",
            "MasterSite",
        ]
        for token in required:
            self.assertIn(token.casefold(), joined.casefold(), token)

        forbidden = [
            "delta_gamma",
            "component-level concentration will remain unopened until both gates pass",
            "ensure adequate representation of both increasing and declining systems",
        ]
        for token in forbidden:
            self.assertNotIn(token.casefold(), joined.casefold(), token)

    def test_provider_questions_preserve_all_hard_stops(self):
        form = FORM.read_text(encoding="utf-8")
        needed = [
            "direct Count=0 is a surveyed nil return",
            "absent SiteID × species × year row means not surveyed/missing rather than zero",
            "estimated/imputed zeroes",
            "renames, merges, splits, retirements, replacements or boundary changes",
        ]
        for text in needed:
            self.assertIn(text, form)

    def test_public_evidence_does_not_unlock_stage_b(self):
        text = EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("zero counts are essential", text)
        self.assertIn("nil return", text)
        self.assertIn("does **not** authorize Stage B", text)
        self.assertIn("provider confirmation", text)

    def test_human_submission_fields_remain_unfilled(self):
        text = FORM.read_text(encoding="utf-8")
        self.assertIn("Human fields still required at submission", text)
        for field in (
            "name",
            "institution",
            "telephone",
            "email",
            "source of funding",
            "supervisor name",
            "deadline for receipt",
        ):
            self.assertIn(field, text)


if __name__ == "__main__":
    unittest.main()
